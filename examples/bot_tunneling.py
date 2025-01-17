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
        sleep(.5)
        for msg in bot:
            if msg.chat == TARGET:
                try:
                    chat, message = msg.message.split(":")
                    bot.open_chat(chat)
                    bot.send_message(message)
                except ChatNotFoundException as e:
                    bot.open_chat(TARGET)
                    bot.send_message(str(e))
                except (ValueError, AttributeError):
                    pass
            elif msg.sender != MY_NAME:
                # Tunel das conversas para a conversa designada
                bot.open_chat(TARGET)
                bot.send_message('({}) {} -> {}'.format(msg.chat, msg.sender, msg.message.replace(':', ';')))


if __name__=='__main__':
    # Inicializa bot
    bot = ZapAPI("C:/Thales/Curiosidades/ZapBot/drivers/chromedriver.exe", debug_level=logging.ERROR)
    zapbot(bot)
