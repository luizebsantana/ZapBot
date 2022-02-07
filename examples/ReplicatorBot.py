import os, sys
import logging
from time import sleep
sys.path.append(os.getcwd())
from zapbot import ZapAPI

# Replicando mensagens

# Não escutar por notificações que contenham...
IGNORE_FROM = ('Analytics', 'Carran', 'Estrutura', '2', 'Padri', 'Se vi', 'BROTH', 'Rol', 'Botelho')

bot = ZapAPI("C:/Thales/Curiosidades/ZapBot/drivers/chromedriver.exe", debug_level=logging.DEBUG)

try:
    # Abri alguma conversa
    bot.open_chat(' ')

    while True:

        # Verifica se ah alguma notificação e abre a conversa
        for notification in bot.get_notifications():
            #  Pulando notificações indesejadas.
            skip = False
            for name in IGNORE_FROM:
                if name in notification.name:
                    skip = True
            if skip:
                continue
            bot.open_chat(notification.name)

        # Replicando as novas mensagens
        for msg in bot.get_messages(True):
            # Previnindo o reenvio da mensagem que estamos enviado
            if 'BOT' not in msg.message:
                bot.send_message("BOT: "+msg.message)
        
        # Aguarda um tempo minimo para a proxima checagem
        sleep(.5)

except Exception as e:
    print(e)
    bot.driver.close()
    exit(1)