"""
This module centralizes configuration settings for the application, including
any constants and global settings required across different modules that are not sensitive information.
"""

DTO_LIST_FORMATTING_PRESETS = {
    "DATASETDTO_SIMPLE": [
        ("", "dataset_name"), ("Augmented", "augmented"), ("Global", "is_global")],
    "MODELDTO_SIMPLE": [("", "model_name"), ("Version", "version"), ("Model", "fine_tuning_model"), ("Checkpoint Model", "is_checkpoint_model"), ("Checkpoint Step", "checkpoint_step"), ("Global", "is_global")]
}


GLOBAL_SESSION_STATE_KEYS = {
    'GLOBAL_STATES_KEY': 'global_states',
    'SERVICE_KEY': 'service',
    'CURRENT_PROJECT_KEY': 'current_project',
    'GLOBAL_TOASTS_KEY': 'global_toasts'
}

# Unified page configuration
PAGE_CONFIG = {
    'home': {
        'path': 'main.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_KEY'], 'id'],
        }
    },
    'create_project': {
        'path': 'pages/1_create_project.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_KEY'], 'id']
        }
    },
    'update_project': {
        'path': 'pages/2_update_project.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_KEY'], 'id']
        }
    },
    'fine_tune_model': {
        'path': 'pages/3_fine_tune_model.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_KEY'], 'id']
        }
    },
    'create_model': {
        'path': 'pages/4_create_model.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_KEY'], 'id']
        }
    },
    'create_dataset': {
        'path': 'pages/5_create_dataset.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_KEY'], 'id']
        }
    },
}

UPLOAD_FORMAT_FORMATTINGS = {
    "openai": {
        "jsonl": '''{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "Oh, just some guy named William Shakespeare. Ever heard of him?"}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "Around 384,400 kilometers. Give or take a few, like that really matters."}]}''',
        "example": "Nothing to see here"
    },
    "google": {
        "example": "Nothing to see here"
    }
}


class Config:
    pass
