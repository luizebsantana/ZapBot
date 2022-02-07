
import os, re
import logging
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException,\
                                       StaleElementReferenceException
from .ChatTypes import ChatMessage, ChatNotification, ChatTextMessage

# from PIL import Image
# from io import BytesIO

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

# ---------- XPATHS ------------
SEARCH_BAR = '//div[@data-tab="3" and @role="textbox"]'
CHAT_LIST_CONTAINER = '//div[@id="pane-side"]'
SEARCH_CANCEL_BUTTON = '//button[@aria-label="Lista de conversas"]/../span/button'
SEARCH_RESULTS = './/div[@aria-label="Resultados da pesquisa."]/div/div/div'
SEARCH_RESULTS_NAME = './/div[@aria-colindex="2"]/div[1]'

ARCHIVED_OPEN_BUTTON = '//div[@id="pane-side"]/button[@aria-label="Arquivadas "]'
ARCHIVED_BACK_BUTTON = '//header//button[@aria-label="Voltar"]'
ARCHIVED_MENU_HEADER = '//h1[contains(text(),"Arquivada")]'

NAO_LIDAS = '//*[@role="row"]//div[@aria-colindex="2" and ..//*[contains(@aria-label, "não lida")]]/..'
NAO_LIDAS_TITLE = './div[1]/div[1]/span'
NAO_LIDAS_TIME = './div[1]/div[2]'
NAO_LIDAS_PREVIEW = './div[2]//span'

MENSAGE_BOX = '//div[@title="Mensagem"]'
SEND_BUTTON = '//button/span[@data-icon="send"]'

CHAT_CONTAINER = '//div[@id="main"]//div[contains(@aria-label, "Lista de mensagens.")]/..'
CHAT_NAME = '//div[@id="main"]/header/div[2]/div[1]'
CHAT = '//div[@id="main"]//div[contains(@aria-label, "Lista de mensagens.")]/div'


class ZapAPI:

    def __init__(self, driver_path:str, debug_level=logging.DEBUG, profile_path:str = PROFILE_PATH):
        
        logger.setLevel(debug_level)

        self.url = "https://web.whatsapp.com/"
        self.wait_time = 2

        service = Service(driver_path)
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument(r"user-data-dir={}".format(profile_path))
        self.driver = webdriver.Chrome(service=service, options=driver_options)
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
                WebDriverWait(self.driver, 2).until(
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
        self.__init_chats()


    def get_notifications(self, archived: bool = False) -> list[ChatNotification]:
        """ Retorna as notificações não lidas.

            Parameters:
                archived (bool): Caso verdadeiro também retorna as notificações de chats
                arquivados.

            Returns: 
                str: Notificaçoes não lidas
        """
        try:
            self.driver.find_element(By.XPATH, SEARCH_CANCEL_BUTTON).click()
        except:
            pass
        if archived:
            self.__open_archived()   
        else:
            self.__close_archived()
        messages: list[ChatNotification] = []
        for e in self.driver.find_elements(By.XPATH, NAO_LIDAS):
            name = e.find_element(By.XPATH, NAO_LIDAS_TITLE).get_attribute('title')
            dt_string = e.find_element(By.XPATH, NAO_LIDAS_TIME).text
            try:
                preview = e.find_element(By.XPATH, NAO_LIDAS_PREVIEW).get_attribute('title')
                preview = preview.replace('\n','\\n')
            except StaleElementReferenceException:
                preview = None
            messages.append(ChatNotification(name, dt_string, preview))
        return messages

    def open_chat(self, search: str=None, exact_match: bool=False) -> str:
        """ Abre um chat para leitura ou envio de mensages, se o parametro de
            busca nao for fornecido retorna o chat aberto atualmente.

            Parameters:
                search (str): nome para busca nas conversas contatos e grupos

                exact_match (bool): Se verdadeiro o titulo da conversa ou do contato
                precisa ser exatamente igual ao valor passado em search caso contrario
                o chat nao é aberto e None é retornado

            Returns:
                str: O nome do contato encotrado e aberto, caso nenhum seja
                encontrado None é retornado
        """

        if search is None:
            try:
                return self.driver.find_element(By.XPATH, CHAT_NAME).text
            except:
                return None

        # Verifica se já corresponde ao chat aberto
        try:
            open_chat = self.driver.find_element(By.XPATH, CHAT_NAME).text
            if search == open_chat:
                logger.info("Chat '{}' já está aberto.".format(open_chat))
                return open_chat
        except:
            pass

        # Fecha a aba de mensagens arquivadas caso aberta
        self.__close_archived()

        # Encontra a caixa de pesquisa e digita o nome da pessoa
        search_box = self.driver.find_element(By.XPATH, SEARCH_BAR)
        self.driver.execute_script('arguments[0].innerHTML="";', search_box)
        search_box.send_keys(search)

        try:
            container = self.driver.find_element(By.XPATH, CHAT_LIST_CONTAINER)
        except NoSuchElementException:
            self.driver.find_element(By.XPATH, SEARCH_CANCEL_BUTTON).click()
            container = self.driver.find_element(By.XPATH, CHAT_LIST_CONTAINER)
        
        # Retorna a barra de rolagem para o inicio
        self.driver.execute_script('arguments[0].scroll(0,0)', container)
        
        # Espera a execucao do javascript
        sleep(0.2)

        # Tenta abrir a mensagem
        tries = 0
        while tries < 5:
            try:
                # Espera pelo termino do loading
                WebDriverWait(self.driver, 2).until(
                    expected_conditions.element_to_be_clickable((By.XPATH, SEARCH_CANCEL_BUTTON))
                )
                # Ordena resultados pelo ordem da posicao y na tela
                res = sorted(container.find_elements(By.XPATH, SEARCH_RESULTS),  key=lambda x: x.location['y'])

                # Clica no resultado e espera o chat ser aberto
                result_name = res[0].find_element(By.XPATH, SEARCH_RESULTS_NAME).text
                if not exact_match or (exact_match and result_name == search):
                    try:
                        open_chat = self.driver.find_element(By.XPATH, CHAT_NAME).text
                        if result_name != open_chat:
                            logger.info("Chat aberto '{}' difere de '{}' tentando novamente...".format(open_chat, result_name))
                            res[0].click()
                            sleep(0.1)
                        else:
                            logger.info("Chat '{}' aberto com sucesso.".format(open_chat, result_name))
                            return open_chat
                    except NoSuchElementException:
                        res[0].click()
                tries += 1
            except (IndexError, StaleElementReferenceException, NoSuchElementException) as e:
                logger.error(e)
                tries += 1
        logger.error("Nao foi possivel abrir a conversa {}.".format(search))
        return None

    def send_message(self, mensagem: str) -> None:
        """ Envia uma mensagem para o chat aberto

            Parameters:
                mensagem (str): Mensagem a ser enviada ao chat aberto

            Returns:
                None
        """
        # pre-process mensage
        mensagem_lines = mensagem.split('\n')
        caixa_de_mensagem = self.driver.find_element(By.XPATH, MENSAGE_BOX)
        self.driver.execute_script('arguments[0].innerHTML="";', caixa_de_mensagem)
        for i, line in enumerate(mensagem_lines):
            caixa_de_mensagem.send_keys(line)
            if i < len(mensagem_lines)-1:
                caixa_de_mensagem.send_keys(Keys.SHIFT+Keys.ENTER)
        botao_enviar = self.driver.find_element(By.XPATH, SEND_BUTTON)
        botao_enviar.click()

    def get_messages(self, only_new_messages: bool=True, max_number: int=-1) -> list[ChatMessage]:
        """ Retorna mensages do chat aberto.

            Parameters:
                only_new_messages (bool): Verdadeiro retorna somente as mensagens novas,
                Falso retorna as ultimas mensagens (quantidade indefinida aprox.: [8 a 30] )

            Returns:
                list[ChatMessage]: Lista de mensagens
        """
        res = self.driver.find_elements(By.XPATH, CHAT)
        messages: list[ChatMessage] = []
        try:
            open_chat: str = self.driver.find_element(By.XPATH, CHAT_NAME).text
        except NoSuchElementException:
            logger.error("Nenhuma conversa aberta.")
            return None

        # Retorna a barra de rolagem para o final
        container = self.driver.find_element(By.XPATH, CHAT_CONTAINER)
        self.driver.execute_script('arguments[0].scroll(0,1000000)', container)

        if open_chat not in self.__contact_last_message:
            self.__contact_last_message[open_chat] = None
        while len(res) > 0:
            e = res.pop()
            if self.__contact_last_message[open_chat] is None:
                try:
                    element = e.find_element(By.XPATH, './/span[@aria-live]')
                    try:
                        if element.text.index("NÃO LIDA"):
                            break
                    except ValueError:
                        messages.append(ChatMessage(element.text))
                except:
                    pass
            try:
                metadata_element = e.find_element(By.XPATH, './/div[@data-pre-plain-text]')
                data = metadata_element.find_element(By.XPATH, './div/span')
                metadata_raw = metadata_element.get_attribute('data-pre-plain-text')
                sender = re.search('(?<=\] ).+:', metadata_raw).group(0)[:-1]
                dt = datetime.strptime(re.search("\[.*?\]", metadata_raw).group(0), '[%H:%M, %d/%m/%Y]')
                content = data.text.replace('\\n','\n')
                message = ChatTextMessage(sender=sender, datetime=dt, message=content)
                if message == self.__contact_last_message[open_chat] or (max_number > -1 and len(messages) >= max_number):
                    break
                else:
                    messages.insert(0, message)
            except StaleElementReferenceException as e:
                logger.error(e)
            except NoSuchElementException:
                pass
        if len(messages) > 0:
            self.__contact_last_message[open_chat] = messages[-1]
        return messages

    def __init_chats(self):
        search_box = self.driver.find_element(By.XPATH, SEARCH_BAR)
        self.driver.execute_script('arguments[0].innerHTML="";', search_box)
        search_box.send_keys(' ')
        try:
            container = self.driver.find_element(By.XPATH, CHAT_LIST_CONTAINER)
        except NoSuchElementException:
            self.driver.find_element(By.XPATH, SEARCH_CANCEL_BUTTON).click()
            container = self.driver.find_element(By.XPATH, CHAT_LIST_CONTAINER)
        # Retorna a barra de rolagem para o inicio
        self.driver.execute_script('arguments[0].scroll(0,0)', container)
        # Espera a execucao do javascript
        # Espera pelo termino do loading
        WebDriverWait(self.driver, 2).until(
            expected_conditions.element_to_be_clickable((By.XPATH, SEARCH_CANCEL_BUTTON))
        )
        # Ordena resultados pelo ordem da posicao y na tela
        res = sorted(container.find_elements(By.XPATH, SEARCH_RESULTS),  key=lambda x: x.location['y'])
        chat_names = [r.find_element(By.XPATH, SEARCH_RESULTS_NAME).text for r in res]
        for chat_name in chat_names:
            self.open_chat(chat_name, True)
            msg = self.get_messages(max_number=1)
            if msg is not None and len(msg) > 0:
                logger.info("initializing chats: "+chat_name+"   "+msg[0].message)
        return None

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

