from random import randint
from ChatTypes import ChatTextMessage


def random(*variations: list[any]) -> any:
    return variations[randint(0, len(variations)-1)]

def greeting(msg: ChatTextMessage) -> str:
    if msg.datetime.hour > 18:
        return 'Boa noite'
    if msg.datetime.hour > 12:
        return 'Boa tarde'
    if msg.datetime.hout > 5:
        return 'Bom dia'
    return 'Boa noite'
