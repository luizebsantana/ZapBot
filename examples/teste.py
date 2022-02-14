import os, io, sys
import logging
from time import sleep
from datetime import datetime
sys.path.append(os.getcwd())
print(os.getcwd())
from zapapi import ZapAPI
from zapapi.ChatTypes import ChatTextMessage 
from zapapi.Exceptions import ChatNotFoundException
from fsm import FSM
from fsm import util

fsm = FSM.loadYAML('./examples/fsm.yaml')
fsm.execute()
