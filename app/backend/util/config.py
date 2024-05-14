"""
This module centralizes configuration settings for the application, including
any constants and global settings required across different modules that are not sensitive information.
"""

from dotenv import load_dotenv, find_dotenv
import os
from types import SimpleNamespace
from ..service.validators.classes.request_dto_validators import MessageKeys, UploadFormats, FineTuningCompanies

load_dotenv(find_dotenv())

# TODO: Make config dynamic (adapt to Enums etc.) and maybe reconsider SimpleNamespace usage.


class Config:

    def __init__(self, openai_api_key: str = None, google_translate_api_key: str = None,
                 current_augmentation_amount: int = 100, current_augmentation_run: int = 1,
                 pages: SimpleNamespace = None, global_states: list = None, upload_formats: SimpleNamespace = None, roles: list[str] = None, upload_format_formattings: SimpleNamespace = None, fine_tuning_companies: list[str] = None):
        # Use environment variables as fallback if no API keys are provided
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key must not be None!")

        self.google_translate_api_key = google_translate_api_key or os.getenv(
            'GOOGLE_TRANSLATE_API_KEY')
        if not self.google_translate_api_key:
            raise ValueError("Google Translate API key must not be None!")

        # Use default values for other parameters if none are provided
        self.current_augmentation_amount = current_augmentation_amount
        self.current_augmentation_run = current_augmentation_run

        # Initialize pages with a default SimpleNamespace if none is provided
        self.pages = pages or SimpleNamespace(
            home="main.py", create_project="pages/1_create_project.py", update_project="pages/2_update_project.py", fine_tune_model="pages/3_fine_tune_model.py", create_model="pages/4_create_model.py", create_dataset="pages/5_create_dataset.py")

        # Initialize global states list if none is provided
        self.global_states = global_states or ["service", "config"]
        self.roles = roles or SimpleNamespace(
            openai=MessageKeys.opanai.value, google=MessageKeys.google.value)
        self.upload_format_formattings = upload_format_formattings or SimpleNamespace(openai="""{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "Oh, just some guy named William Shakespeare. Ever heard of him?"}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "Around 384,400 kilometers. Give or take a few, like that really matters."}]}""", google="")
        self.upload_formats = upload_formats or SimpleNamespace(
            openai=UploadFormats.openai.value, google=UploadFormats.google.value)
        self.fine_tuning_companies = fine_tuning_companies or SimpleNamespace(
            companies=FineTuningCompanies.companies.value)
