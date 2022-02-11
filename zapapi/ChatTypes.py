from datetime import datetime
from dataclasses import dataclass
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .xpaths import LIST_ITEM_NAME, LIST_ITEM_TIME, LIST_ITEM_NAO_LIDA

class ChatListItem:

    name: str
    time: str
    lida: bool
    element: WebElement

    def __init__(self, element: WebElement, name: str=None) -> None:
        self.element = element
        self.name = name
        self.time = None
        self.lida = None

    def __getattribute__(self, _attrib: str) -> any:
        if _attrib == 'name' and super().__getattribute__('name') is None:
            self.name = self.element.find_element(By.XPATH, LIST_ITEM_NAME).text
        elif _attrib == 'time' and super().__getattribute__('time') is None:
            self.time = self.element.find_element(By.XPATH, LIST_ITEM_TIME).text
        elif _attrib == 'lida' and super().__getattribute__('lida') is None:
            try:
                self.element.find_element(By.XPATH, LIST_ITEM_NAO_LIDA)
                self.lida = False
            except NoSuchElementException:
                self.lida = True
        return super().__getattribute__(_attrib)
    
    def __str__(self) -> str:
        return f'ChatListItem({self.name}, {self.time}, {"lida" if self.lida else "nao lida"})'

    def __repr__(self) -> str:
        return str(self)
    


@dataclass(frozen=True)
class ChatMessage:
    chat: str
    message: str


@dataclass(frozen=True)
class ChatTextMessage(ChatMessage):
    sender: str
    datetime: datetime