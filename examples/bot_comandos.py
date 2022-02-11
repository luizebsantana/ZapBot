import os, io, sys
import logging
from time import sleep
from datetime import datetime
sys.path.append(os.getcwd())
print(os.getcwd())
from zapapi.ZapAPI import ZapAPI
from zapapi.ChatTypes import ChatTextMessage 
from zapapi.Exceptions import ChatNotFoundException
from zapbot.StateMachine import StateMachine

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

yaml_dict = yaml.load(io.FileIO('./examples/fsm.yaml'), Loader)

# Replicando mensagens
TARGET= ('Eu', 'Teste') 
MY_NAME = 'Thales Fernandes'
        
def zapbot(api: ZapAPI):

    stateMachines = {}

    while True:
        sleep(.5)
        for msg in api:
            if msg.chat in TARGET:
                if msg.sender not in stateMachines:
                    stateMachines[msg.sender] = StateMachine(**yaml_dict)
                bot = stateMachines[msg.sender]
                try:
                    if not msg.message.lower().startswith('bot'):
                        print(msg.message)
                        now = datetime.now()
                        response = bot.send(message=msg.message, sender=msg.sender, h=now.hour, m=now.minute, s=now.second, D=now.day, M=now.month, A=now.year)
                        api.open_chat(msg.chat)
                        for res in response:
                            api.send_message('bot:\n'+'\n'.join(res))
                except ChatNotFoundException as e:
                    api.open_chat('Eu')
                    api.send_message(str(e))
                except (ValueError, AttributeError):
                    pass

if __name__=='__main__':
    # Inicializa bot
    api = ZapAPI("C:/Thales/Curiosidades/ZapBot/drivers/chromedriver.exe", debug_level=logging.ERROR)
    zapbot(api)
