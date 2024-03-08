"""
Provides a service class for interacting with OpenAI's API, specifically for
fine-tuning the GPT-3.5-Turbo model. It handles API requests and responses,
streamlining the model's fine-tuning process.

Classes:
    OpenAIService: Manages the API interactions with OpenAI, including fine-tuning and data retrieval.
"""


class OpenAIService:
    """
    Service class for interacting with OpenAI's API. Manages the process of
    fine-tuning GPT-3.5-Turbo, including request preparation and response handling.

    Attributes:
        api_key (str): API access key for openAI's API.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
