from typing import List, Optional
from datetime import datetime


class ProjectDTO:
    def __init__(self, id: int, project_name: str, description: str, created_at: datetime, models: Optional[List[int]], datasets: Optional[List[int]]):
        self.id = id
        self.project_name = project_name
        self.description = description
        self.created_at = created_at
        self.models = models
        self.datasets = datasets


class DatasetDTO:
    def __init__(self, id: int, dataset_name: str, augmented: bool, category: str, created_at: datetime, projects: List[int], initial_dataset: Optional[int], test_dataset: Optional[int], datapoints: List[int]):
        self.id = id
        self.dataset_name = dataset_name
        self.augmented = augmented
        self.category = category
        self.created_at = created_at
        self.projects = projects
        self.initial_dataset = initial_dataset
        self.test_dataset = test_dataset
        self.datapoints = datapoints


class DataPointDTO:
    def __init__(self, id: int, dataset_id: int, coherence_score: Optional[int], relevance_score: Optional[int], semantic_similarity_score: Optional[float], augmentation_type: str, messages: str, initial_datapoint_id: Optional[int], created_at: datetime):
        self.id = id
        self.dataset_id = dataset_id
        self.coherence_score = coherence_score
        self.relevance_score = relevance_score
        self.semantic_similarity_score = semantic_similarity_score
        self.augmentation_type = augmentation_type
        self.messages = messages
        self.initial_datapoint_id = initial_datapoint_id
        self.created_at = created_at


class ModelDTO:
    def __init__(self, id: int, model_name: str, parent_model_id: Optional[int], version: int, created_at: datetime, project_id: int, evaluations: Optional[List[int]], datasets: List[int], training_run: Optional[int]):
        self.id = id
        self.model_name = model_name
        self.parent_model_id = parent_model_id
        self.version = version
        self.created_at = created_at
        self.project_id = project_id
        self.evaluations = evaluations
        self.datasets = datasets
        self.training_run = training_run


class ModelEvaluationDTO:
    def __init__(self, id: int, model_id: int, datapoint_id: int, evaluation_type: str, helpful_score: int, honest_score: int, harmless_score: int, datapoint: DataPointDTO, created_at: datetime):
        self.id = id
        self.model_id = model_id
        self.datapoint_id = datapoint_id
        self.evaluation_type = evaluation_type
        self.helpful_score = helpful_score
        self.honest_score = honest_score
        self.harmless_score = harmless_score
        self.datapoint = datapoint
        self.created_at = created_at


class TrainingRunDTO:
    def __init__(self, id: int, model_id: int, epochs: int, learning_rate_multiplier: float, batch_size: int, created_at: datetime):
        self.id = id
        self.model_id = model_id
        self.epochs = epochs
        self.learning_rate_multiplier = learning_rate_multiplier
        self.batch_size = batch_size
        self.created_at = created_at
