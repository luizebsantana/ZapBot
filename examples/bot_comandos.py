import os, sys
import logging
from time import sleep
from datetime import datetime
sys.path.append(os.getcwd())
print(os.getcwd())
from zapapi.ZapAPI import ZapAPI
from zapapi.ChatTypes import ChatTextMessage 
from zapapi.Exceptions import ChatNotFoundException
from zapbot.StateMachine import StateMachine
import io
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

yaml = yaml.load(io.FileIO('./examples/fsm.yaml'), Loader)
bot: StateMachine = StateMachine(**yaml)

# Replicando mensagens
TARGET= 'Eu'
MY_NAME = 'Thales Fernandes'
        
def zapbot(api: ZapAPI):
    while True:
        sleep(.5)
        for msg in api:
            if msg.chat == TARGET:
                try:
                    chat, message = msg.message.split(":")
                    if chat.startswith('BOT'):
                        now = datetime.now()
                        a = bot.send(message=msg.message, sender=msg.sender, h=now.hour, m=now.min, s=now.second, D=now.day, M=now.month, A=now.year)
                        print("a", a.message)
                        api.open_chat(TARGET)
                        api.send_message('\n'.join(a.message))
                except ChatNotFoundException as e:
                    api.open_chat(TARGET)
                    api.send_message(str(e))
                except (ValueError, AttributeError):
                    pass
            elif msg.sender != MY_NAME:
                # Tunel das conversas para a conversa designada
                api.open_chat(TARGET)
                api.send_message('({}) {} -> {}'.format(msg.chat, msg.sender, msg.message.replace(':', ';')))

if __name__=='__main__':
    # Inicializa bot
    api = ZapAPI("C:/Thales/Curiosidades/ZapBot/drivers/chromedriver.exe", debug_level=logging.ERROR)
    zapbot(api)
