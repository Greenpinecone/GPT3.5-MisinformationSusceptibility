"""
This module centralizes configuration settings for the application, including
any constants and global settings required across different modules that are not sensitive information.
"""


SBERT_MODELS = [
    {
        "Model Name": "all-mpnet-base-v2",
        "Performance Sentence Embeddings": 69.57,
        "Performance Semantic Search": 57.02,
        "Avg. Performance": 63.30,
        "Speed": 2800,
        "Model Size": "420 MB"
    },
    {
        "Model Name": "multi-qa-mpnet-base-dot-v1",
        "Performance Sentence Embeddings": 66.76,
        "Performance Semantic Search": 57.60,
        "Avg. Performance": 62.18,
        "Speed": 2800,
        "Model Size": "420 MB"
    },
    {
        "Model Name": "all-distilroberta-v1",
        "Performance Sentence Embeddings": 68.73,
        "Performance Semantic Search": 50.94,
        "Avg. Performance": 59.84,
        "Speed": 4000,
        "Model Size": "290 MB"
    },
    {
        "Model Name": "all-MiniLM-L12-v2",
        "Performance Sentence Embeddings": 68.70,
        "Performance Semantic Search": 50.82,
        "Avg. Performance": 59.76,
        "Speed": 7500,
        "Model Size": "120 MB"
    },
    {
        "Model Name": "multi-qa-distilbert-cos-v1",
        "Performance Sentence Embeddings": 65.98,
        "Performance Semantic Search": 52.83,
        "Avg. Performance": 59.41,
        "Speed": 4000,
        "Model Size": "250 MB"
    },
    {
        "Model Name": "all-MiniLM-L6-v2",
        "Performance Sentence Embeddings": 68.06,
        "Performance Semantic Search": 49.54,
        "Avg. Performance": 58.80,
        "Speed": 14200,
        "Model Size": "80 MB"
    },
    {
        "Model Name": "multi-qa-MiniLM-L6-cos-v1",
        "Performance Sentence Embeddings": 64.33,
        "Performance Semantic Search": 51.83,
        "Avg. Performance": 58.08,
        "Speed": 14200,
        "Model Size": "80 MB"
    },
    {
        "Model Name": "paraphrase-multilingual-mpnet-base-v2",
        "Performance Sentence Embeddings": 65.83,
        "Performance Semantic Search": 41.68,
        "Avg. Performance": 53.75,
        "Speed": 2500,
        "Model Size": "970 MB"
    },
    {
        "Model Name": "paraphrase-albert-small-v2",
        "Performance Sentence Embeddings": 64.46,
        "Performance Semantic Search": 40.04,
        "Avg. Performance": 52.25,
        "Speed": 5000,
        "Model Size": "43 MB"
    },
    {
        "Model Name": "paraphrase-multilingual-MiniLM-L12-v2",
        "Performance Sentence Embeddings": 64.25,
        "Performance Semantic Search": 39.19,
        "Avg. Performance": 51.72,
        "Speed": 7500,
        "Model Size": "420 MB"
    },
    {
        "Model Name": "paraphrase-MiniLM-L3-v2",
        "Performance Sentence Embeddings": 62.29,
        "Performance Semantic Search": 39.19,
        "Avg. Performance": 50.74,
        "Speed": 19000,
        "Model Size": "61 MB"
    },
    {
        "Model Name": "distiluse-base-multilingual-cased-v1",
        "Performance Sentence Embeddings": 61.30,
        "Performance Semantic Search": 29.87,
        "Avg. Performance": 45.59,
        "Speed": 4000,
        "Model Size": "480 MB"
    },
    {
        "Model Name": "distiluse-base-multilingual-cased-v2",
        "Performance Sentence Embeddings": 60.18,
        "Performance Semantic Search": 27.35,
        "Avg. Performance": 43.77,
        "Speed": 4000,
        "Model Size": "480 MB"
    }
]

# All entries should be unique
DATA_AUGMENTATION_METHODS = {
    "google_translate": "google_translate",
    "EDA_Easy_Data_Augmentation": "EDA_Easy_Data_Augmentation"
}

DTO_LIST_FORMATTING_PRESETS = {
    "DATASETDTO_SIMPLE": [
        ("", "dataset_name"), ("Augmented", "augmented"), ("Global", "is_global")],
    "MODELDTO_SIMPLE": [("", "model_name"), ("Version", "version"), ("Checkpoint Model", "is_checkpoint_model"), ("Checkpoint Step", "checkpoint_step"), ("Global", "is_global")],
    "TRAINING_RUN_DTO_SIMPLE": [("", "model_name"), ("Version", "model_version")],
    "SBERT_MODELS": [("Name", "Model Name"),  ("Avg. Perf.", "Avg. Performance"), ("Size", "Model Size"), ("Speed", "Speed"), ("Perf. Emb.", "Performance Sentence Embeddings"), ("Perf. Sear.", "Performance Semantic Search")]
}

GLOBAL_SESSION_STATE_KEYS = {
    'GLOBAL_STATES_KEY': 'global_states',
    'SERVICE_KEY': 'service',
    'GLOBAL_TOASTS_KEY': 'global_toasts',
    'CURRENT_PROJECT_DATA_KEY': 'current_project_data'
}

# Unified page configuration
PAGE_CONFIG = {
    'home': {
        'path': 'main.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_DATA_KEY'], ['current_project', 'id']],
        }
    },
    'create_project': {
        'path': 'pages/1_create_project.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_DATA_KEY'], ['current_project', 'id']]
        }
    },
    'update_project': {
        'path': 'pages/2_update_project.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_DATA_KEY'], ['current_project', 'id']]
        }
    },
    'fine_tune_model': {
        'path': 'pages/3_fine_tune_model.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_DATA_KEY'], ['current_project', 'id']]
        }
    },
    'create_model': {
        'path': 'pages/4_create_model.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_DATA_KEY'], ['current_project', 'id']]
        }
    },
    'create_dataset': {
        'path': 'pages/5_create_dataset.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_DATA_KEY'], ['current_project', 'id']]
        }
    },
    'match_datapoint': {
        'path': 'pages/6_match_datapoint.py',
        'query_params': {
            'projectId': [GLOBAL_SESSION_STATE_KEYS['CURRENT_PROJECT_DATA_KEY'], ['current_project', 'id']]
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
