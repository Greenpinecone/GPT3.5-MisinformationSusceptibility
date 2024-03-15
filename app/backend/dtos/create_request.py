from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class CreateProjectDTO:
    project_name: str
    description: str
    models: Optional[List[int]]
    datasets: Optional[List[int]]


@dataclass
class CreateDatasetDTO:
    dataset_name: str
    augmented: bool
    category: str
    projects: List[int]
    initial_dataset: Optional[int]
    test_dataset: Optional[int]
    datapoints: List[int]


@dataclass
class CreateDataPointDTO:
    dataset_id: int
    coherence_score: Optional[int]
    relevance_score: Optional[int]
    semantic_similarity_score: Optional[float]
    augmentation_type: Optional[str]
    messages: List[Dict[str, str]]
    initial_datapoint_id: Optional[int]
    category: str


@dataclass
class CreateModelDTO:
    model_name: str
    parent_model_id: Optional[int]
    version: int
    project_id: int
    evaluations: Optional[List[int]]
    datasets: List[int]
    training_run: Optional[int]


@dataclass
class CreateModelEvaluationDTO:
    model_id: int
    datapoint_id: int
    evaluation_type: str
    helpful_score: int
    honest_score: int
    harmless_score: int


@dataclass
class CreateTrainingRunDTO:
    model_id: int
    epochs: int
    learning_rate_multiplier: float
    batch_size: int
