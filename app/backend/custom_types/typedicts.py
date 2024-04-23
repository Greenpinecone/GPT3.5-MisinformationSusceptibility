from typing import Optional, Dict, TypedDict


class Message(TypedDict):
    role: str
    content: str


class MessagesContainer(TypedDict):
    messages: list[Message]
