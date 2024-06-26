"""
This module centralizes configuration settings for the application, including
any constants and global settings required across different modules that are not sensitive information.
"""


SBERT_MODELS = [
    # Models for semantic similarity: https://sbert.net/docs/sentence_transformer/pretrained_models.html#original-models

    # Only models that can be used with cosine similarity for a result value between -1 - 1
    {
        "model_name": "paraphrase-multilingual-mpnet-base-v2",
        "performance_sentence_embeddings": 65.83,
        "performance_semantic_search": 41.68,
        "avg_performance": 53.75,
        "speed": 2500,
        "model_size": "970 MB",
        "similarity_fn_names": ["cosine"],
        "description": "A multilingual model designed for paraphrase identification. It supports 50+ languages and is effective for semantic similarity tasks across multiple languages.",
        "base_model": "Teacher: paraphrase-mpnet-base-v2; Student: xlm-roberta-base",
        "max_sequence_length": 128,
        "dimensions": 768,
        "normalized_embeddings": False,
        "pooling": "Mean Pooling",
        "training_data": "Multi-lingual model of paraphrase-mpnet-base-v2, extended to 50+ languages.",
        "model_card": "https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    },
    {
        "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
        "performance_sentence_embeddings": 64.25,
        "performance_semantic_search": 39.19,
        "avg_performance": 51.72,
        "speed": 7500,
        "model_size": "420 MB",
        "similarity_fn_names": ["cosine"],
        "description": "A compact multilingual model for paraphrase detection. It supports 50+ languages and provides a balance between performance and speed for semantic similarity.",
        "base_model": "Teacher: paraphrase-MiniLM-L12-v2; Student: microsoft/Multilingual-MiniLM-L12-H384",
        "max_sequence_length": 128,
        "dimensions": 384,
        "normalized_embeddings": False,
        "pooling": "Mean Pooling",
        "training_data": "Multi-lingual model of paraphrase-multilingual-MiniLM-L12-v2, extended to 50+ languages.",
        "model_card": "https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    },
    {
        "model_name": "distiluse-base-multilingual-cased-v1",
        "performance_sentence_embeddings": 61.30,
        "performance_semantic_search": 29.87,
        "avg_performance": 45.59,
        "speed": 4000,
        "model_size": "480 MB",
        "similarity_fn_names": ["cosine"],
        "description": "A multilingual model based on distilled Universal Sentence Encoder. It supports 15 languages and is suitable for general semantic similarity tasks.",
        "base_model": "Teacher: mUSE; Student: distilbert-base-multilingual",
        "max_sequence_length": 128,
        "dimensions": 512,
        "normalized_embeddings": False,
        "pooling": "Mean Pooling",
        "training_data": "Multi-Lingual model of Universal Sentence Encoder for 15 languages: Arabic, Chinese, Dutch, English, French, German, Italian, Korean, Polish, Portuguese, Russian, Spanish, Turkish.",
        "model_card": "https://huggingface.co/sentence-transformers/distiluse-base-multilingual-cased-v1"
    },
    {
        "model_name": "distiluse-base-multilingual-cased-v2",
        "performance_sentence_embeddings": 60.18,
        "performance_semantic_search": 27.35,
        "avg_performance": 43.77,
        "speed": 4000,
        "model_size": "480 MB",
        "similarity_fn_names": ["cosine"],
        "description": "An improved version of the v1 model with support for 50+ languages. It is effective for multilingual semantic similarity.",
        "base_model": "Teacher: mUSE; Student: distilbert-base-multilingual",
        "max_sequence_length": 128,
        "dimensions": 512,
        "normalized_embeddings": False,
        "pooling": "Mean Pooling",
        "training_data": "Multi-Lingual model of Universal Sentence Encoder for 50 languages.",
        "model_card": "https://huggingface.co/sentence-transformers/distiluse-base-multilingual-cased-v2"
    },
    # Semantic Search Models
    {
        "model_name": "multi-qa-distilbert-cos-v1",
        "performance_sentence_embeddings": 65.98,
        "performance_semantic_search": 52.83,
        "avg_performance": 59.41,
        "speed": 4000,
        "model_size": "250 MB",
        "similarity_fn_names": ["dot", "cosine", "euclidean"],
        "description": "A distilled BERT model for question-answering tasks optimized for cosine similarity. It provides a good balance between speed and performance.",
        "base_model": "distilbert-base",
        "max_sequence_length": 512,
        "dimensions": 768,
        "normalized_embeddings": True,
        "pooling": "Mean Pooling",
        "training_data": "215M (question, answer) pairs from diverse sources.",
        "model_card": "https://huggingface.co/sentence-transformers/multi-qa-distilbert-cos-v1"
    },
    {
        "model_name": "multi-qa-MiniLM-L6-cos-v1",
        "performance_sentence_embeddings": 64.33,
        "performance_semantic_search": 51.83,
        "avg_performance": 58.08,
        "speed": 14200,
        "model_size": "80 MB",
        "similarity_fn_names": ["dot", "cosine", "euclidean"],
        "description": "A lightweight model optimized for semantic search using cosine similarity. It offers high speed and reasonable performance for large-scale search tasks.",
        "base_model": "nreimers/MiniLM-L6-H384-uncased",
        "max_sequence_length": 512,
        "dimensions": 384,
        "normalized_embeddings": True,
        "pooling": "Mean Pooling",
        "training_data": "215M (question, answer) pairs from diverse sources.",
        "model_card": "https://huggingface.co/sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
    },
    # All purpose models
    {
        "model_name": "all-mpnet-base-v2",
        "performance_sentence_embeddings": 69.57,
        "performance_semantic_search": 57.02,
        "avg_performance": 63.30,
        "speed": 2800,
        "model_size": "420 MB",
        "similarity_fn_names": ["dot", "cosine", "euclidean"],
        "description": "A general-purpose model trained on a large dataset for various NLP tasks. It performs well for both sentence embeddings and semantic search.",
        "base_model": "microsoft/mpnet-base",
        "max_sequence_length": 384,
        "dimensions": 768,
        "normalized_embeddings": True,
        "pooling": "Mean Pooling",
        "training_data": "1B+ training pairs. For details, see model card.",
        "model_card": "https://huggingface.co/sentence-transformers/all-mpnet-base-v2"
    },
    {
        "model_name": "all-distilroberta-v1",
        "performance_sentence_embeddings": 68.73,
        "performance_semantic_search": 50.94,
        "avg_performance": 59.84,
        "speed": 4000,
        "model_size": "290 MB",
        "similarity_fn_names": ["dot", "cosine", "euclidean"],
        "description": "A distilled version of RoBERTa optimized for speed and performance in semantic similarity and search tasks.",
        "base_model": "distilroberta-base",
        "max_sequence_length": 512,
        "dimensions": 768,
        "normalized_embeddings": True,
        "pooling": "Mean Pooling",
        "training_data": "1B+ training pairs. For details, see model card.",
        "model_card": "https://huggingface.co/sentence-transformers/all-distilroberta-v1"
    },
    {
        "model_name": "all-MiniLM-L12-v2",
        "performance_sentence_embeddings": 68.70,
        "performance_semantic_search": 50.82,
        "avg_performance": 59.76,
        "speed": 7500,
        "model_size": "120 MB",
        "similarity_fn_names": ["dot", "cosine", "euclidean"],
        "description": "A highly efficient model offering a good trade-off between speed and performance for various NLP tasks.",
        "base_model": "microsoft/MiniLM-L12-H384-uncased",
        "max_sequence_length": 256,
        "dimensions": 384,
        "normalized_embeddings": True,
        "pooling": "Mean Pooling",
        "training_data": "1B+ training pairs. For details, see model card.",
        "model_card": "https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2"
    },
    {
        "model_name": "all-MiniLM-L6-v2",
        "performance_sentence_embeddings": 68.06,
        "performance_semantic_search": 49.54,
        "avg_performance": 58.80,
        "speed": 14200,
        "model_size": "80 MB",
        "similarity_fn_names": ["dot", "cosine", "euclidean"],
        "description": "An even more compact version optimized for speed, suitable for large-scale processing with good performance.",
        "base_model": "nreimers/MiniLM-L6-H384-uncased",
        "max_sequence_length": 256,
        "dimensions": 384,
        "normalized_embeddings": True,
        "pooling": "Mean Pooling",
        "training_data": "1B+ training pairs. For details, see model card.",
        "model_card": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"
    },
    {
        "model_name": "paraphrase-albert-small-v2",
        "performance_sentence_embeddings": 64.46,
        "performance_semantic_search": 40.04,
        "avg_performance": 52.25,
        "speed": 5000,
        "model_size": "43 MB",
        "similarity_fn_names": ["cosine"],
        "description": "A small and efficient model for paraphrase detection and semantic similarity tasks.",
        "base_model": "nreimers/albert-small-v2",
        "max_sequence_length": 256,
        "dimensions": 768,
        "normalized_embeddings": False,
        "pooling": "Mean Pooling",
        "training_data": "AllNLI, sentence-compression, SimpleWiki, altlex, msmarco-triplets, quora_duplicates, coco_captions,flickr30k_captions, yahoo_answers_title_question, S2ORC_citation_pairs, stackexchange_duplicate questions, wiki-atomic-edits",
        "model_card": "https://huggingface.co/sentence-transformers/paraphrase-albert-small-v2"
    },
    {
        "model_name": "paraphrase-MiniLM-L3-v2",
        "performance_sentence_embeddings": 62.29,
        "performance_semantic_search": 39.19,
        "avg_performance": 50.74,
        "speed": 19000,
        "model_size": "61 MB",
        "similarity_fn_names": ["cosine"],
        "description": "A very lightweight model for paraphrase detection, offering extremely high speed with reasonable performance.",
        "base_model": "nreimers/MiniLM-L3-H384-uncased",
        "max_sequence_length": 128,
        "dimensions": 384,
        "normalized_embeddings": False,
        "pooling": "Mean Pooling",
        "training_data": "AllNLI, sentence-compression, SimpleWiki, altlex, msmarco-triplets, quora_duplicates, coco_captions,flickr30k_captions, yahoo_answers title question, S2ORC_citation_pairs, stackexchange_duplicate questions, wiki-atomic-edits",
        "model_card": "https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L3-v2"
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
    "SBERT_MODELS": [("Name", "model_name"),  ("Avg. Perf.", "avg_performance"), ("Size", "model_size"), ("Speed", "speed"), ("Perf. Emb.", "performance_sentence_embeddings"), ("Perf. Sear.", "performance_semantic_search")]
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
