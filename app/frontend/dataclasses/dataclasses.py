from dataclasses import dataclass


@dataclass
class ToastMessage:
    message: str = ""
    icon: str = ""
