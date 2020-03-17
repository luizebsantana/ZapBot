import os
from PIL import Image
from io import BytesIO
from time import sleep
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

driver_running = False
strdiasemana = [
    'segunda-feira',
    'terça-feira',
    'quarta-feira',
    'quinta-feira',
    'sexta-feira',
    'sábado',
    'domingo',
]

class ZapBot:
    
    def __init__(self, driver_path=None, driver=None, reload=False, profile_path=os.path.join(os.getcwd(), "profile", "wpp")):
        self.driver_options = webdriver.ChromeOptions()
        self.driver_options.add_argument(r"user-data-dir={}".format(profile_path))
        self.driver_path = driver_path
        self.url = "https://web.whatsapp.com/"
        self.driver = None
        self.wait_time = 2
        
        if driver:
            self.driver = driver
            if reload:
                self.driver.get(self.url)
        else:
            self.init_driver()
        
        #Espera a pagina carregar
        pagina_carregada = False
        tentativas = 0
        self.driver.implicitly_wait(0.5)
        print('Carregando pagina.', end='')
        while tentativas < 40:
            
            #verifica se a caixa de pesquisa existe
            try:
                WebDriverWait(self.driver, 0.5).until(
                  expected_conditions.element_to_be_clickable(
                    (By.XPATH,'//div[@class="_3u328 copyable-text selectable-text"]')
                  )
                )
                print('\nPagina Carregada')
                pagina_carregada = True
                break
            except:
                pass
            
            #verifica se a conexão com celular existe
            try:
                el = self.driver.find_element_by_xpath('//div[contains(text(), "Tentando novamente em")]')
                print('\nCelular desconectado '+el.text, end='')
                sleep(1)
            except:
                pass
            print('.', end='')
            tentativas += 1
        
        self.driver.implicitly_wait(self.wait_time)
        if not pagina_carregada:
            #fecha driver caso a pagina não possa ser carregada
            print("\nImpossivel carregar a pagina, verifique conexao com a internet.")
            self.close_driver()
    
    def reload(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(self.wait_time)

    def get_mensages(self, start_index, end_index):
        """ Captura a ultima mensagem da conversa """
        count = 0
        try:
            posts = self.driver.find_elements_by_xpath("//div[@class='_1ays2']/div")
            count = len(posts)
            while count < end_index:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", posts[0]); sleep(0.5)
                posts = self.driver.find_elements_by_xpath("//div[@class='_1ays2']/div")
                if count != len(posts):
                    count = len(posts)
                else:
                    break
            parsed = []
            for i in range(end_index-start_index):
                parsed.append(self.parse_mensage(posts[len(posts)-1-start_index-i]))
            return parsed
        except Exception as e:
            print(e)
            
    def parse_mensage(self, element):
        self.driver.implicitly_wait(0)
        mensage=dict()
        status = element.get_attribute('class')
        last = not '_4jEk2' in status
        if 'message-out' in status:
            status = element.find_element_by_xpath(".//span[@data-icon]").get_attribute('data-icon')
        else:
            status = 'message-in'
        mensage['type']      = ['other']
        mensage['user']      = None
        mensage['status']    = status
        mensage['last']      = last
        mensage['content']   = ''
        mensage['timestamp'] = None
        try:
            data = element.find_element_by_xpath(".//div[@data-pre-plain-text]").get_attribute('data-pre-plain-text')
            content = element.find_element_by_xpath('.//div[contains(@class,"_12pGw")]/span').text
        except:
            return mensage
        try:
            time, date = data.split(' ')[:2]
            user = ' '.join(data.split(' ')[2:])
            (h, m), (D, M, A) = time[1:-1].split(':'), date[:-1].split('/')
            mensage['type'] = ['text']
            mensage['user'] = user[:-1]
            mensage['content'] = content
            mensage['timestamp'] = datetime(int(A), int(M), int(D), int(h), int(m))
            try:
                link = element.find_element_by_xpath('.//img').get_attribute('src')
                mensage['type'].append('img')
            except: pass
        except Exception as e:
            raise e
        #   try:
        #      link = element.find_element_by_xpath('.//audio').get_attribute('src')
        #      length = element.find_element_by_xpath('.//div[@class="_1lxsr"]').text
        #      h, m = element.find_element_by_xpath(".//span[@class='_3fnHB']").text.split(':')
        #      mensage['type'] = ['audio']
        #      mensage['content'] = link
        #      mensage['user'] = puser
        #      mensage['length'] = length
        #      mensage['timestamp'] = datetime(ptime.year, ptime.month, ptime.day, int(h), int(m))
        #      bot.driver.implicitly_wait(10)
        #      return mensage
        #   except Exception as e:
        #      print(e)
        return mensage
        

    def enviar(self, msg):
        """ Envia uma mensagem para a conversa aberta """
        try:
            msg = msg.replace('\n','\\n')
            caixa_de_mensagem = self.driver.find_element_by_xpath('//footer//div[contains(@class,"_3u328")]')
            self.driver.execute_script('arguments[0].innerHTML="'+msg+' ";', caixa_de_mensagem); sleep(0.2)
            caixa_de_mensagem.send_keys(Keys.BACKSPACE)
            botao_enviar = self.driver.find_element_by_xpath('//button[@class="_3M-N-"]')
            botao_enviar.click()
        except Exception as e:
            print("Erro ao enviar msg", e)

    def abrir_conversa(self, contato):
        
        def tstamp(c):
            timestr=None
            try:
                self.driver.implicitly_wait(0)
                timestr = c.find_element_by_xpath('.//div[@class="_0LqQ"]').text
            except:
                self.driver.implicitly_wait(self.wait_time)
                return datetime(1900, 1, 1)
            self.driver.implicitly_wait(self.wait_time)
            if ':' in timestr:
                h, m = timestr.split(':')
                now = datetime.now()
                return datetime(now.year, now.month, now.day, int(h), int(m))
            elif '/' in timestr:
                d, m, a = timestr.split('/')
                return datetime(int(a), int(m), int(d))
            elif timestr.lower() in ZapBot.strdiasemana:
                now = datetime.now()
                target_day = ZapBot.strdiasemana.index(timestr.lower())
                delta_day = target_day - now.isoweekday()
                if delta_day >= 0: delta_day -= 7 # go back 7 days
                return now + timedelta(days=delta_day)
            else:
                now = datetime.now()
                return now+timedelta(days=-1)
        
        """ Abre a conversa com um contato especifico """
        try:
            # Seleciona a caixa de pesquisa de conversa
            caixa_de_pesquisa = self.driver.find_element_by_xpath('//div[@class="_3u328 copyable-text selectable-text"]')
            self.driver.execute_script('arguments[0].innerHTML="'+contato+' ";', caixa_de_pesquisa)
            sleep(0.5)
            # Digita o nome ou numero do contato
            caixa_de_pesquisa.send_keys(Keys.BACKSPACE)
            sleep(1)
            # Seleciona o contato            
            contatos = self.driver.find_elements_by_xpath("//div[@class='KgevS' and .//span[@title='{}']]".format(contato))
            contatos.sort(reverse=True, key=lambda e: tstamp(e))
            contatos[0].click()
        except Exception as e:
            raise e
    
    
    def init_driver(self):
        global driver_running
        if not driver_running:
            self.driver = webdriver.Chrome(self.driver_path, options=self.driver_options)
            driver_running = True
            self.driver.get(self.url)
            self.driver.implicitly_wait(self.wait_time)
            print('Driver Inicializado.')
        else:
            print('O drive ja esta sendo executado.')
    
    def close_driver(self):
        global driver_running
        if driver_running:
            self.driver.close()
            driver_running = False
            print('Driver fechado.')
        else:
            print('O driver esta inativo.')