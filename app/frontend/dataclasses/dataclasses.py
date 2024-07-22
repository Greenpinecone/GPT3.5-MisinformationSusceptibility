"""
A module containing custom data classes.
"""

from dataclasses import dataclass


@dataclass
class ToastMessage:
    """
    A class to represent a toast message with an icon.

    Attributes:
        message (str): The message to be displayed in the toast.
        icon (str): The icon to be displayed with the toast message.
    """

    message: str = ""
    icon: str = ""
