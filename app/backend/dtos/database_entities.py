from typing import List, Optional
from database.schema import DatasetCategory, AugmentationType, EvaluationType


class ProjectDTO:
    def __init__(self, project_name: str):
        self.project_name = project_name


class DatasetDTO:
    def __init__(self, dataset_name: str, augmented: bool, category: DatasetCategory, projects: List[int], initial_dataset: Optional[int], test_dataset: Optional[int]):
        self.dataset_name = dataset_name
        self.augmented = augmented
        self.category = category
        self.projects = projects
        self.initial_dataset = initial_dataset
        self.test_dataset = test_dataset


class DataPointDTO:
    def __init__(self, dataset_id: int, coherence_score: Optional[int], relevance_score: Optional[int], semantic_similarity_score: Optional[float], augmentation_type: Optional[AugmentationType], messages: str, datapoint_category: str, initial_datapoint_id: Optional[int]):
        self.dataset_id = dataset_id
        self.coherence_score = coherence_score
        self.relevance_score = relevance_score
        self.semantic_similarity_score = semantic_similarity_score
        self.augmentation_type = augmentation_type
        self.messages = messages
        self.datapoint_category = datapoint_category
        self.initial_datapoint_id = initial_datapoint_id


class ModelDTO:
    def __init__(self, model_name: str, parent_model_id: Optional[int], version: int, project_id: int):
        self.model_name = model_name
        self.parent_model_id = parent_model_id
        self.version = version
        self.project_id = project_id


class ModelEvaluationDTO:
    def __init__(self, model_id: int, datapoint_id: int, evaluation_type: EvaluationType, helpful_score: int, honest_score: int, harmless_score: int):
        self.model_id = model_id
        self.datapoint_id = datapoint_id
        self.evaluation_type = evaluation_type
        self.helpful_score = helpful_score
        self.honest_score = honest_score
        self.harmless_score = harmless_score


class TrainingRunDTO:
    def __init__(self, model_id: int, epochs: int, learning_rate_multiplier: float, batch_size: int):
        self.model_id = model_id
        self.epochs = epochs
        self.learning_rate_multiplier = learning_rate_multiplier
        self.batch_size = batch_size
