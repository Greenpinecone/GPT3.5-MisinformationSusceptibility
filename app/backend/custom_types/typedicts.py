from typing import TypedDict


# TODO: Update the intermediate data storing typedicts for uploaded fine tuning data to adhere to multiple different data types and formats based on the AI model data structure chosen for uploading. Also adapt this for all of its occurences.
class Message(TypedDict):
    role: str
    content: str


class MessagesContainer(TypedDict):
    messages: list[Message]
