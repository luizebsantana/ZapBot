import os, sys
from time import sleep
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
from lxml import html
from parse_input import get_input
from ZapBot import ZapBot, strdiasemana

LOG_PATH    = './log.txt'
DRIVER_PATH = './drivers/chromedriver.exe'

"tranformar selenium em html tree"

def str_datetime(dt):
	strdia = strdiasemana[dt.weekday()]
	return "{}, {:02d}/{:02d}/{:4d} - {:02d}:{:02d}:{:02d}".format(
		strdia[0].upper()+strdia[1:],dt.day, dt.month,
		dt.year, dt.hour, dt.minute, dt.second)

def printf(string):
	print(string)
	with open(LOG_PATH, 'a') as file:
		file.write(string+'\n')

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

	contato = "-"

	today = datetime.now()
	today += relativedelta(days=get_input('--offset', '-ofs', 0, int))
	contato = get_input('--contato', '-c', 'Eu', str)

	printf('['+str_datetime(today)+']')
	printf('Iniciando script...')
	strdia = strdiasemana[today.weekday()]

	if msg[strdia]:
		try:
			bot = ZapBot(DRIVER_PATH)
			printf('Carrengando pagina: '+bot.url+'.')
			tentativas = 0
			mensagem_enviada = False

			while not mensagem_enviada:
				tentativas += 1
				try:
					printf("Abrindo conversa '"+contato+"'.")
					bot.abrir_conversa(contato)

					printf('Enviando mensagem...')
					print('\n'+msg[strdia])
					bot.enviar(msg[strdia])

					mensagem_enviada = True
					printf('Mensagem enviada com sucesso.')
					bot.driver.get_screenshot_as_file('./temp.png')

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
				bot.close_driver()
				printf('Driver finalizado.')
			except Exception as e:
				print(e)
				
	else:
		printf('Não há mensagens para '+strdia+'.')
		sleep(2)

	printf('Fim de execução.\n')
	sys.exit(0)
