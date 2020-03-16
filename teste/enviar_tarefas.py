import os, sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep

log_file = 'log.txt'

"tranformar selenium em html tree"

def str_datetime(dt):
	strdia = strdiasemana[dt.weekday()]
	return "{}, {:02d}/{:02d}/{:4d} - {:02d}:{:02d}:{:02d}".format(
		strdia[0].upper()+strdia[1:],dt.day, dt.month,
		dt.year, dt.hour, dt.minute, dt.second)

def printf(string):
	print(string)
	with open(log_file, 'a') as file:
		file.write(string+'\n')

class ZapBot:

	def __init__(self, webdriver):
		self.url = "https://web.whatsapp.com/"
		self.driver = webdriver
		# Abre o whatsappweb
		self.driver.get(self.url)
		printf('Carrengando pagina: '+self.url+'.')
		# Aguarda alguns segundos para validação manual do QrCode
		self.driver.implicitly_wait(15)


	def ultima_msg(self):
		""" Captura a ultima mensagem da conversa """
		try:
			post = self.driver.find_elements(By.XPATH('//div[contains(@class,"message-in")]'))
			# O texto da ultima mensagem
			texto = post[-1].find_element_by_css_selector("span.selectable-text").text
			return texto
		except Exception as e:
			print(e)

	def envia_msg(self, msg):
		""" Envia uma mensagem para a conversa aberta """
		try:
			msg = msg.replace('\n','\\n')
			script='document.getElementsByClassName("_3u328 copyable-text selectable-text")[1].innerHTML="'+msg+' "'
			self.driver.execute_script(script)
			sleep(1)
			caixa_de_mensagem = self.driver.find_element_by_xpath('//footer//div[contains(@class,"_3u328")]')
			caixa_de_mensagem.send_keys(Keys.BACKSPACE)
			botao_enviar = self.driver.find_element_by_xpath('//button[@class="_3M-N-"]')
			botao_enviar.click()
		except Exception as e:
			print("Erro ao enviar msg", e)

	def abre_conversa(self, contato):
		""" Abre a conversa com um contato especifico """
		try:
			# Seleciona a caixa de pesquisa de conversa
			caixa_de_pesquisa = self.driver.find_element_by_xpath(
				'//div[@class="_3u328 copyable-text selectable-text"]')
			script='document.getElementsByClassName("_3u328 copyable-text selectable-text")[0].innerHTML="'+contato+' "'
			self.driver.execute_script(script)
			sleep(1)
			# Digita o nome ou numero do contato
			caixa_de_pesquisa.send_keys(Keys.BACKSPACE)
			sleep(1)
			# Seleciona o contato
			contato = self.driver.find_element_by_xpath("//div[@class='KgevS']//span[@title = '{}']".format(contato))
			contato.click()

		except Exception as e:
			raise e

def get_driver():
	dir_path = os.getcwd()
	profile = os.path.join(dir_path, "profile", "wpp")
	options = webdriver.ChromeOptions()
	options.add_argument(r"user-data-dir={}".format(profile))
	chromedriver = "./drivers/chromedriver.exe"
	print('Inicializando driver.')
	return webdriver.Chrome(chromedriver, options=options)

def get_meta(post):
	temp_ = post.xpath('./div')[0]
	data = temp_[0]
	content = temp_[-1]
	time, date, user = post.xpath('.//@data-pre-plain-text')[0].split()
	(h, m), (D, M, Y) = time[1:-1].split(':'), date[1:-1].split('/')
	mensagem = {'username' : user[:-1],
				'content'  : content.text_content(),
				'timestamp': datetime.datetime(int(Y),int(M),int(D),int(h),int(m))}
	return mensagem


strdiasemana = [
	'segunda-feira',
	'terça-feira',
	'quarta-feira',
	'quinta-feira',
	'sexta-feira',
	'sábado',
	'domingo',
]

"""
class Tarefa:

	def __init__(self, nome: str, responsavel: str, funcao: 'function', frequencia, inicio, final, **kwargs):
		self.nome: str = nome
		self.responsavel: str = responsavel
		self.rrule = rrule(frequencia, inicio, until=final, **kwargs)
		self.agendado: list = [dt for dt in self.rrule]
		self.execucoes: list = []
		self.funcao = funcao

	def proxima(self):
		for dt in self.agendado:
			if dt > datetime.now():
				return dt

	def executar(self, dt, now):
		self.funcao(dt, now)
		self.execucoes.append(now)

	def executar_pendentes(self):
		now = datetime.now()
		i = 0
		while i < len(self.agendado):
			dt = self.agendado[i]
			if dt < now:
				try:
					self.executar(dt, now)
					self.agendado.remove(dt)
					i -= 1
				except Exception as e:
					print("Erro ao executar tarefa: "+str(self))
					print(e)
			i += 1
"""

msg = {
	"segunda-feira":
"""*TAREFAS SEGUNDA-FEIRA*

❌Borel -> Sala
❌Gigolô -> Banheiro
❌Dentinho -> Escada
❌Bixos -> Café
❌Bixos -> Lixo
""",
	"terça-feira":
"""*TAREFAS TERÇA-FEIRA*

❌Peta -> Cozinha
❌Enxurrada -> Area Frente
❌Leôncio -> Banheiro baixo
❌Bixos -> Café
""",
	"quarta-feira":
"""*TAREFAS QUARTA-FEIRA*

❌Borel -> Sala
❌Bixos -> Lixo
❌Baby Shark -> Microondas
❌Funko -> Máquina de lavar
❌Funko -> Pano e capa colchão
""",
	"quinta-feira":
"""*TAREFAS QUARTA-FEIRA*

❌Baby Shark -> Cozinha
❌Sussurro/Zé Boni -> Garagem
❌Dinho -> Banheiro cima
❌Grilo -> Banheiro baixo
❌Bixos -> Café
""",
	"sexta-feira":
"""*TAREFAS SEXTA-FEIRA*

❌Bixos -> Café
❌Bixos -> Lixo
""",
	"sábado":
"""*TAREFAS SABADO*

❌Bixos -> Banho Xica
""",
	"domingo": None
}


if __name__ == "__main__":

	today = datetime.now()
	if len(sys.argv) > 1:
		today += relativedelta(days=int(sys.argv[1]))
	printf('['+str_datetime(today)+']')
	printf('Iniciando script...')
	strdia = strdiasemana[today.weekday()]
	if msg[strdia]:

		try:
			driver = get_driver()
		except:
			print("Erro ao inicializar o driver")
			exit()

		try:
			bot = ZapBot(driver)
			tentativas = 0
			mensagem_enviada = False

			while not mensagem_enviada:
				tentativas += 1
				try:
					contato = "CARRANCA MORADORES"
					printf("Abrindo conversa '"+contato+"'.")
					bot.abre_conversa(contato)

					printf('Enviando mensagem...')
					print('\n'+msg[strdia])
					bot.envia_msg(msg[strdia])

					mensagem_enviada = True
					printf('Mensagem enviada com sucesso.')
					driver.get_screenshot_as_file('./temp.png')

				except Exception as e:
					printf(str(e)+'\nErro ao enviar a mensagem de '+strdia+'.')
					if tentativas < 3:
						printf('Tentando novamente...')
						sleep(2)
					else:
						mensagem_enviada = True
						printf('Mensagesm não enviada.')
		finally:
			try:
				driver.close()
				printf('Driver finalizado.')
			except Exception as e:
				print(e)
				
	else:
		printf('Não há mensagens para '+strdia+'.')
		sleep(2)

	printf('Fim de execução.\n')
	sys.exit(0)
