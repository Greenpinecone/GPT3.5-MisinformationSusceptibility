from typing import List, Optional


class CreateProjectDTO:
    def __init__(self, project_name: str, description: str, models: Optional[List[int]], datasets: Optional[List[int]]):
        self.project_name = project_name
        self.description = description
        self.models = models
        self.datasets = datasets


class CreateDatasetDTO:
    def __init__(self, dataset_name: str, augmented: bool, category: str, projects: List[int], initial_dataset: Optional[int], test_dataset: Optional[int], datapoints: List[int]):
        self.dataset_name = dataset_name
        self.augmented = augmented
        self.category = category
        self.projects = projects
        self.initial_dataset = initial_dataset
        self.test_dataset = test_dataset
        self.datapoints = datapoints


class CreateDataPointDTO:
    def __init__(self, dataset_id: int, coherence_score: Optional[int], relevance_score: Optional[int], semantic_similarity_score: Optional[float], augmentation_type: Optional[str], messages: str, initial_datapoint_id: Optional[int]):
        self.dataset_id = dataset_id
        self.coherence_score = coherence_score
        self.relevance_score = relevance_score
        self.semantic_similarity_score = semantic_similarity_score
        self.augmentation_type = augmentation_type
        self.messages = messages
        self.initial_datapoint_id = initial_datapoint_id


class CreateModelDTO:
    def __init__(self, model_name: str, parent_model_id: Optional[int], version: int, project_id: int, evaluations: Optional[List[int]], datasets: List[int], training_run: Optional[int]):
        self.model_name = model_name
        self.parent_model_id = parent_model_id
        self.version = version
        self.project_id = project_id
        self.evaluations = evaluations
        self.datasets = datasets
        self.training_run = training_run


class CreateModelEvaluationDTO:
    def __init__(self, model_id: int, datapoint_id: int, evaluation_type: str, helpful_score: int, honest_score: int, harmless_score: int):
        self.model_id = model_id
        self.datapoint_id = datapoint_id
        self.evaluation_type = evaluation_type
        self.helpful_score = helpful_score
        self.honest_score = honest_score
        self.harmless_score = harmless_score


class CreateTrainingRunDTO:
    def __init__(self, model_id: int, epochs: int, learning_rate_multiplier: float, batch_size: int):
        self.model_id = model_id
        self.epochs = epochs
        self.learning_rate_multiplier = learning_rate_multiplier
        self.batch_size = batch_size
