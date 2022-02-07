import os, sys
import logging
from time import sleep
sys.path.append(os.getcwd())
from zapbot import ZapAPI

# Replicando mensagens
# Não escutar por notificações que contenham...
IGNORE_FROM = ('Eu',)
TARGET= 'Eu'

def zapbot(bot):
    while True:
        # Aguarda um tempo minimo para realizar o loop
        sleep(.5)

        # Verifica se ah alguma notificação e abre a conversa
        for notification in bot.get_notifications():
            #  Pulando notificações indesejadas.
            skip = False
            for name in IGNORE_FROM:
                if name in notification.name:
                    skip = True
            if skip:
                continue

            # Abrindo chat da notificação
            bot.open_chat(notification.name)

        # Replicando as novas mensagens
        messages = bot.get_messages(True)

        # Caso contrario realiza o reenvio das mensages
        # Abrindo chat alvo
        if messages is None:
            continue

        for msg in messages:
            # Previnindo o reenvio da mensagem que estamos enviado
            if msg.chat != TARGET and bot.open_chat(TARGET): 
                print('({}) {}: {}'.format(msg.chat, msg.sender, msg.message))
                # bot.send_message('({}) {}: {}'.format(msg.chat, msg.sender, msg.message))
        
        

if __name__=='__main__':
    # Inicializa bot
    bot = ZapAPI("C:/Thales/Curiosidades/ZapBot/drivers/chromedriver.exe", debug_level=logging.DEBUG)
    try:
        zapbot(bot)
    except Exception as e:
        print(e)
        bot.driver.close()
        exit(1)