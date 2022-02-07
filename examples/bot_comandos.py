import os, sys
import logging
from time import sleep

sys.path.append(os.getcwd())
from zapbot import ZapAPI
from zapbot.ChatTypes import ChatTextMessage 
from zapbot.Exceptions import ChatNotFoundException

# Replicando mensagens
TARGET= 'Eu'
MY_NAME = 'Thales Fernandes'
        
def zapbot(bot: ZapAPI):

    while True:
        for msg in bot:
            if msg.chat == TARGET and msg.message[0] == '-':
                sender = TARGET if msg.sender == MY_NAME else msg.sender
                bot.open_chat(sender)
                bot.send_message("Ola {}! tudo bem?".format(msg.sender.split(' ')[0]))


if __name__=='__main__':
    # Inicializa bot
    bot = ZapAPI("C:/Thales/Curiosidades/ZapBot/drivers/chromedriver.exe", debug_level=logging.ERROR)
    zapbot(bot)
