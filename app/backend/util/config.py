"""
This module centralizes configuration settings for the application, including
any constants and global settings required across different modules that are not sensitive information.
"""

from dotenv import load_dotenv, find_dotenv
import os
from types import SimpleNamespace

load_dotenv(find_dotenv())

# Unified page configuration
PAGE_CONFIG = {
    'home': {
        'path': 'main.py',
        'query_params': {
            'projectId': ['current_project', 'id'],
            'userId': ['current_user', 'id']
        }
    },
    'create_project': {
        'path': 'pages/1_create_project.py',
        'query_params': {
            'itemId': ['selected_item', 'id']
        }
    },
    'update_project': {
        'path': 'pages/2_update_project.py',
        'query_params': {
            'itemId': ['selected_item', 'id']
        }
    },
    'fine_tune_model': {
        'path': 'pages/3_fine_tune_model.py',
        'query_params': {
            'itemId': ['selected_item', 'id']
        }
    },
    'create_model': {
        'path': 'pages/4_create_model.py',
        'query_params': {
            'itemId': ['selected_item', 'id']
        }
    },
    'create_dataset': {
        'path': 'pages/5_create_dataset.py',
        'query_params': {
            'itemId': ['selected_item', 'id']
        }
    },
}


class Config:
    pages = PAGE_CONFIG
    upload_format_formattings = SimpleNamespace(
        openai={
            "jsonl": '''{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "Oh, just some guy named William Shakespeare. Ever heard of him?"}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "Around 384,400 kilometers. Give or take a few, like that really matters."}]}''',
            "example": "Nothing to see here"
        },
        google={"example": "Nothing to see here"}
    )
