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

api = ZapAPI("C:/Thales/Curiosidades/ZapBot/drivers/chromedriver.exe", debug_level=logging.ERROR)

print(api.get_chat_list())