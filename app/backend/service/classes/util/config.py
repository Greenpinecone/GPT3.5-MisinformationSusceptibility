"""
This module centralizes configuration settings for the application, including
any constants and global settings required across different modules that are not sensitive information.
"""

from typing import Optional
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())


class Config:
    """
    Centralizes configuration settings for the application.

    This class is responsible for holding configuration settings that are used
    across the application. These settings include API keys, parameters for data
    processing, and other configuration variables that might be needed by various
    components of the application.

    Attributes:
        openai_api_key (Optional[str]): The API key for OpenAI services. This key
            is read from the environment variable 'OPENAI_API_KEY'. If the environment
            variable is not set, this attribute will be None.
        current_augmentation_amount (int): The default number of augmentations to
            perform on the dataset. This value is used if no specific amount is
            provided during data augmentation processes.
        current_augmentation_run (int): An identifier for the current run of data
            augmentation. This can be used to track different augmentation experiments
            or runs over time.

     Raises:
        ValueError: If the 'OPENAI_API_KEY' environment variable is not set, indicating
                    that the OpenAI API key is missing.
    """

    def __init__(self):
        self.openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("Openai API key must not be None!")
        self.current_augmentation_amount: int = 100
        self.current_augmentation_run: int = 1
