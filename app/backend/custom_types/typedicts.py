"""
This module defines custom type dictionaries for various configurations and data structures.

Classes:
    Message: Defines the structure for a single message.
    MessagesContainer: Contains a list of messages.
    EDAParams: Defines parameters for EDA (Easy Data Augmentation) methods.
    GoogleBTParams: Defines parameters for Google Back-Translation methods.
    AugmentationConfiguration: Defines the configuration for data augmentation.
"""


from typing import TypedDict
# TODO: Update the intermediate data storing typedicts for uploaded fine tuning data to adhere to multiple different data types and formats based on the AI model data structure chosen for uploading. Also adapt this for all of its occurences.


class Message(TypedDict):
    """
    Defines the structure for a single message.

    Attributes:
        role (str): The role of the person or entity sending the message.
        content (str): The content of the message.
    """
    role: str
    content: str


class MessagesContainer(TypedDict):
    """
    Contains a list of messages.

    Attributes:
        messages (list[Message]): A list of messages.
    """
    messages: list[Message]


class EDAParams(TypedDict):
    """
    Defines parameters for EDA (Easy Data Augmentation) methods.

    Attributes:
        alpha_sr (float): Alpha parameter for synonym replacement.
        alpha_ri (float): Alpha parameter for random insertion.
        alpha_rs (float): Alpha parameter for random swap.
        alpha_rd (float): Alpha parameter for random deletion.
    """
    alpha_sr: float
    alpha_ri: float
    alpha_rs: float
    alpha_rd: float


class GoogleBTParams(TypedDict):
    """
    Defines parameters for Google Back-Translation methods.

    Attributes:
        translate_languages (list[dict]): A list of dictionaries specifying translation languages.
    """
    translate_languages: list[dict]


class AugmentationConfiguration(TypedDict):
    """
    Defines the configuration for data augmentation.

    Attributes:
        selected_method (str | None): The selected augmentation method.
        prev_method (str | None): The previously used augmentation method.
        augmentation_percentage (float | None): The percentage of data to augment.
        augmentation_config (EDAParams | GoogleBTParams | None): The configuration parameters for the selected augmentation method.
    """
    selected_method: str | None = None
    prev_method: str | None = None
    augmentation_percentage: float | None = None
    augmentation_config: EDAParams | GoogleBTParams | None = None
