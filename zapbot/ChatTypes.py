from datetime import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class ChatNotification:
    name: str
    timestring: str
    preview: str


@dataclass(frozen=True)
class ChatMessage:
    message: str


@dataclass(frozen=True)
class ChatTextMessage(ChatMessage):
    sender: str
    datetime: datetime