"""
This module includes the GoogleTranslateService class, designed to handle back-translations 
using the Google Translate API. This service is crucial for the data augmentation aspect of 
the thesis, particularly for implementing back-translation as a method to introduce 
linguistic diversity while preserving the semantic content of the data.

Classes:
    GoogleTranslateService: Handles interactions with the Google Translate API.
"""


class GoogleTranslateService:
    """
    Service class for performing back-translations using the Google Translate API.
    Contributes to data augmentation by adding linguistic diversity to the datasets.

    Attributes:
        api_key (str): API access key for Google's API.
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
