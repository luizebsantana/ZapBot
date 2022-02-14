import os, sys
import logging
from time import sleep
sys.path.append(os.getcwd())
from zapapi import ZapAPI

# Replicando mensagens
# Não escutar por notificações que contenham...
MY_NAME = 'Thales Fernandes'
IGNORE_FROM = (MY_NAME, 'Analytics', 'Carran', 'Estrutura', '2', 'Padri', 'Se vi', 'BROTH', 'Rol', 'Botelho')

if __name__=='__main__':
    # Inicializa bot
    api = ZapAPI("C:/Thales/Curiosidades/ZapBot/drivers/chromedriver.exe", debug_level=logging.DEBUG)
    while True:
        # Aguarda um tempo minimo para realizar o loop
        sleep(.5)
        # Verifica se ah alguma notificação e abre a conversa
        for msg in api:
            #  Pulando notificações indesejadas.
            skip = False
            for name in IGNORE_FROM:
                if name in msg.sender:
                    skip = True
            if skip:
                continue
            # Abrindo chat da notificação
            api.open_chat(msg.sender)
            api.send_message(msg.message)