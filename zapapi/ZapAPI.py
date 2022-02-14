import os, re
import logging
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException,\
                                       StaleElementReferenceException,\
                                       WebDriverException,\
                                       TimeoutException, InvalidArgumentException
from .ChatTypes import ChatMessage, ChatListItem, ChatTextMessage
from .Exceptions import ChatNotFoundException, NoOpenChatException
from .xpaths import SEARCH_BAR, LIST, LIST_CONTAINER, LIST_ITEM_NAO_LIDA,\
SEARCH_CANCEL_BUTTON, CHAT, CHAT_NAME, MENSAGE_BOX, SEND_BUTTON,\
ARCHIVED_OPEN_BUTTON, CHAT_CONTAINER, ARCHIVED_MENU_HEADER,\
ARCHIVED_BACK_BUTTON


import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

strdiasemana = [
    'segunda-feira',
    'terça-feira',
    'quarta-feira',
    'quinta-feira',
    'sexta-feira',
    'sábado',
    'domingo',
]

PROFILE_PATH = os.path.join(os.getcwd(),'userdata', 'profile', 'wpp')


class ZapAPI:

    def __init__(self,
        driver_path:str,
        debug_level=logging.DEBUG,
        driver_options: webdriver.ChromeOptions=None,
        profile_path:str = PROFILE_PATH,
        chat_work_list: list[str]=None
        ):
        
        logger.setLevel(debug_level)

        self.chat_work_list = chat_work_list
        self.url = "https://web.whatsapp.com/"
        self.wait_time = 2

        service = Service(driver_path)
        if driver_options is None:
            driver_options = webdriver.ChromeOptions()
            driver_options.add_argument(r"user-data-dir={}".format(profile_path))
        try:
            self.driver = webdriver.Chrome(service=service, options=driver_options)
        except InvalidArgumentException:
            raise Exception("Provavelmente uma janela do navegador já está utilizando a pasta de usuarios.")
        self.driver.get(self.url)
        self.driver.implicitly_wait(0)
        logger.info('Driver Inicializado.')
    
        # Espera a pagina carregar
        pagina_carregada = False
        tentativas = 0
        logger.info('Carregando pagina.')

        # Verifica se a caixa de pesquisa existe e caso exista
        while tentativas < 10:
            try:
                WebDriverWait(self.driver, 10).until(
                  expected_conditions.element_to_be_clickable(
                    (By.XPATH, SEARCH_BAR)
                  )
                )
                logger.info('Pagina Carregada')
                pagina_carregada = True
                break
            except:
                pass
            logger.debug('tentativa {}'.format(tentativas))
            tentativas += 1
            
        # Fecha driver caso a pagina não for carregada
        if not pagina_carregada:
            logger.critical("\nImpossivel carregar a pagina, verifique conexao com a internet.")
            self.driver.close()

        self.__contact_last_message: dict = {}
        self.queue: list[ChatMessage] = []


    def __iter__(self):
        return self

    def __next__(self) -> ChatMessage:
        if len(self.queue) == 0:
            self.__lookup_new_messages()
        if len(self.queue) > 0:
            return self.queue.pop(0)
        else:
            raise StopIteration

    def get_chat_list(self, only_not_readed=False) -> list[ChatListItem]:
        # Fecha a aba de mensagens arquivadas caso aberta
        self.__close_archived()
        # Retorna a barra de rolagem para o inicio
        container = self.driver.find_element(By.XPATH, LIST_CONTAINER)
        self.driver.execute_script('arguments[0].scroll(0,0)', container)
        # Espera a execucao do javascript
        sleep(0.2)
        # Ordena resultados pelo ordem da posicao y na tela e retorna a lista de busca ou de conversas
        res = container.find_elements(By.XPATH, LIST if not only_not_readed else LIST+f'[{LIST_ITEM_NAO_LIDA}]')
        return [ChatListItem(el) for el in sorted(res, key=lambda x: x.location['y'])]

    def open_chat(self, target: str=None, exact_match: bool=True) -> str:
        """ Abre um chat para leitura ou envio de mensages, se o parametro de
            busca nao for fornecido retorna o chat aberto atualmente.

            Parameters:
                target (str): nome para busca nas conversas contatos e grupos

                exact_match (bool): Se verdadeiro o titulo da conversa ou do contato
                precisa ser exatamente igual ao valor passado em target caso contrario
                o chat nao é aberto e None é retornado

            Returns:
                str: O nome do contato encotrado e aberto, caso nenhum seja
                encontrado None é retornado
        """

        if target is None:
            try:
                return self.driver.find_element(By.XPATH, CHAT_NAME).text
            except NoSuchElementException:
                raise NoOpenChatException from None

        # Verifica se já corresponde ao chat aberto
        try:
            open_chat = self.driver.find_element(By.XPATH, CHAT_NAME).text
            if target == open_chat:
                logger.info("Chat '{}' já está aberto.".format(open_chat))
                return open_chat
        except:
            pass

        # Verifica se a conversa requisitada já esta na lista atual 
        res = self.get_chat_list()
        for r in res:
            chat_name = r.name
            if chat_name == target:
                return self.__open_chat_list_item(r)

        # Encontra a caixa de pesquisa e digita o nome da pessoa
        search_box = self.driver.find_element(By.XPATH, SEARCH_BAR)
        self.driver.execute_script('arguments[0].innerHTML="";', search_box)
        try:
            search_box.send_keys(target)
        except WebDriverException as e:
            logger.error(e)

        # Espera pelo termino do loading
        try:
            WebDriverWait(self.driver, 10).until(
                expected_conditions.element_to_be_clickable((By.XPATH, SEARCH_CANCEL_BUTTON))
            )
        except TimeoutException as e:
            logger.error(e)
            raise ChatNotFoundException(target, message="Nao foi possivel carregar os resultados.") from None

        # Retorna lista de conversas
        res = self.get_chat_list()
        try:
            if not exact_match or (exact_match and res[0].name == target):
                return self.__open_chat_list_item(res[0])
        finally:
            self.driver.find_element(By.XPATH, SEARCH_CANCEL_BUTTON).click()
        raise ChatNotFoundException(target)

    def send_message(self, mensagem: str) -> None:
        """ Envia uma mensagem para o chat aberto

            Parameters:
                mensagem (str): Mensagem a ser enviada ao chat aberto

            Returns:
                None
        """
        try: 
            caixa_de_mensagem = self.driver.find_element(By.XPATH, MENSAGE_BOX)
        except NoSuchElementException:
            raise NoOpenChatException from None
        # pre-process mensage
        mensagem_lines = mensagem.split('\n')
        self.driver.execute_script('arguments[0].innerHTML="";', caixa_de_mensagem)
        for i, line in enumerate(mensagem_lines):
            try:
                caixa_de_mensagem.send_keys(line)
            except WebDriverException as e:
                logger.error(e)
            if i < len(mensagem_lines)-1:
                caixa_de_mensagem.send_keys(Keys.SHIFT+Keys.ENTER)
        try:
            botao_enviar = self.driver.find_element(By.XPATH, SEND_BUTTON)
            botao_enviar.click()
        except NoSuchElementException as e:
            logger.error(e)

    def get_messages(self, only_new_messages: bool=True, max_number: int=-1) -> list[ChatMessage]:
        """ Retorna mensages do chat aberto.

            Parameters:
                max_number (int): O número maximo de mensagens a ser retornado.

            Returns:
                list[ChatMessage]: Lista de mensagens, None se não há novas mensagens
        """
        new_message = True
        res = self.driver.find_elements(By.XPATH, CHAT)
        messages: list[ChatMessage] = []
        try:
            open_chat: str = self.driver.find_element(By.XPATH, CHAT_NAME).text
        except NoSuchElementException:
            raise NoOpenChatException from None

        # Retorna a barra de rolagem para o final
        container = self.driver.find_element(By.XPATH, CHAT_CONTAINER)
        self.driver.execute_script('arguments[0].scroll(0,1000000)', container)

        if open_chat not in self.__contact_last_message:
            self.__contact_last_message[open_chat] = None
        while len(res) > 0:
            if max_number > -1 and len(messages) >= max_number:
                 break
            e = res.pop()
            if self.__contact_last_message[open_chat] is None:
                try:
                    element = e.find_element(By.XPATH, './/span[@aria-live]')
                    try:
                        if element.text.index("NÃO LIDA") and only_new_messages:
                            break
                    except ValueError:
                        messages.insert(0, ChatMessage(chat=open_chat, message=element.text))
                except:
                    pass
            try:
                try:
                    read_more_button: WebElement = e.find_element(By.XPATH, './/span[@role="button"]')
                    read_more_button.click()
                    logger.info("Read more...")
                    sleep(.2)
                except NoSuchElementException:
                    pass
                metadata_element = e.find_element(By.XPATH, './/div[@data-pre-plain-text]')
                data = metadata_element.find_element(By.XPATH, './div/span')
                metadata_raw = metadata_element.get_attribute('data-pre-plain-text')
                sender = re.search('(?<=\] ).+:', metadata_raw).group(0)[:-1]
                dt = datetime.strptime(re.search("\[.*?\]", metadata_raw).group(0), '[%H:%M, %d/%m/%Y]')
                content = data.text.replace('\\n','\n')
                message = ChatTextMessage(new=new_message, chat=open_chat, sender=sender, datetime=dt, message=content)
                if new_message and message == self.__contact_last_message[open_chat]:
                    new_message = False
                    message = ChatTextMessage(new=new_message, chat=open_chat, sender=sender, datetime=dt, message=content)
                    if only_new_messages:
                        break
                messages.insert(0, message)
            except StaleElementReferenceException as e:
                logger.error(e)
            except NoSuchElementException as e:
                logger.info(e)
        if len(messages) > 0:
            if self.__contact_last_message[open_chat] is None:
                self.__contact_last_message[open_chat] = messages[-1]
                return None if only_new_messages else messages
            self.__contact_last_message[open_chat] = messages[-1]
            return messages
        return None if only_new_messages else []

    def __lookup_new_messages(self) -> int:
        messages_fount: int = 0
        if self.chat_work_list:
            for work in self.chat_work_list:
                self.open_chat(work)
                messages = self.get_messages()
                if messages is not None and len(messages) > 0:
                    messages_fount += len(messages)
                    self.queue.extend(messages)
            return messages_fount

        for res in self.get_chat_list():
            self.__open_chat_list_item(res)
            messages = self.get_messages()
            if messages is not None and len(messages) > 0:
                messages_fount += len(messages)
                self.queue.extend(messages)
            else:
                break
        for res in self.get_chat_list(True):
            self.__open_chat_list_item(res)
            messages = self.get_messages()
            if messages is not None and len(messages) > 0:
                messages_fount += len(messages)
                self.queue.extend(messages)
        return messages_fount

    def __open_chat_list_item(self, list_item: ChatListItem) -> None:
        # Tenta abrir a mensagem
        tries = 0
        # Clica no resultado e espera o chat ser aberto
        while tries < 5:
            try:
                try:
                    open_chat = self.driver.find_element(By.XPATH, CHAT_NAME).text
                    if list_item.name != open_chat:
                        logger.info("Chat aberto '{}' difere de '{}' tentando novamente...".format(open_chat, list_item.name))
                        list_item.element.click()
                        sleep(0.1)
                    else:
                        logger.info("Chat '{}' aberto com sucesso.".format(open_chat, list_item.name))
                        return open_chat
                except NoSuchElementException:
                    list_item.element.click()
                tries += 1
            except (IndexError, StaleElementReferenceException, NoSuchElementException) as e:
                logger.error(e)
                tries += 1
        logger.error("Nao foi possivel abrir a conversa {}.".format(list_item.name))
        raise ChatNotFoundException(list_item.name)

    def __open_archived(self) -> bool:
        tries = 0
        while tries < 4 :
            try:
                self.driver.find_element(By.XPATH, ARCHIVED_MENU_HEADER)
                logger.debug('Aba arquivados aberta')
                return True
            except NoSuchElementException:
                tries += 1
                self.driver.find_element(By.XPATH, ARCHIVED_OPEN_BUTTON).click()
                sleep(.1)
        logger.error('Nao foi possivel abrir a aba arquivados')
        return False

    def __close_archived(self) -> bool:
        tries = 0
        while tries < 4 :
            try:
                self.driver.find_element(By.XPATH, ARCHIVED_MENU_HEADER)
                try:
                    self.driver.find_element(By.XPATH, ARCHIVED_BACK_BUTTON).click()
                except:
                    pass
                tries += 1
                sleep(.1)
            except NoSuchElementException:
                if tries > 0:
                    logger.debug('Aba arquivados fechada')
                return True
        logger.error('Nao foi possivel fechar a aba arquivados')
        return False

