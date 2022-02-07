import os, sys
import logging
from time import sleep
sys.path.append(os.getcwd())
from zapbot import ZapAPI

# Replicando mensagens
# Não escutar por notificações que contenham...
IGNORE_FROM = ('Analytics', 'Carran', 'Estrutura', '2', 'Padri', 'Se vi', 'BROTH', 'Rol', 'Botelho')

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

        # Se as mensagens forem nulas continua
        if messages is None:
            continue

        # Caso contrario realiza o reenvio das mensages
        for msg in messages:
            # Previnindo o reenvio da mensagem que estamos enviado
            if 'BOT' not in msg.message:
                bot.send_message("BOT: "+msg.message)
        
        

if __name__=='__main__':
    # Inicializa bot
    bot = ZapAPI("C:/Thales/Curiosidades/ZapBot/drivers/chromedriver.exe", debug_level=logging.DEBUG)
    try:
        zapbot(bot)
    except Exception as e:
        print(e)
        bot.driver.close()
        exit(1)