from typing import List, Optional, Dict, TypedDict


class Message(TypedDict):
    role: str
    content: str


class MessagesContainer(TypedDict):
    messages: List[Message]
