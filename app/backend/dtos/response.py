from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import dataclass
from ..database.schema import DatasetCategory, EvaluationType, AugmentationType
from ..dtos.create_request import MessagesContainer


@dataclass
class ProjectDTO:
    id: int
    project_name: str
    description: str
    created_at: datetime
    models: Optional[List[int]]
    datasets: Optional[List[int]]


@dataclass
class DatasetDTO:
    id: int
    dataset_name: str
    augmented: bool
    category: DatasetCategory
    created_at: datetime
    projects: List[int]
    initial_dataset: Optional[int]
    test_dataset: Optional[int]
    datapoints: List[int]


@dataclass
class DataPointDTO:
    id: int
    dataset_id: int
    coherence_score: Optional[int]
    relevance_score: Optional[int]
    semantic_similarity_score: Optional[float]
    augmentation_type: AugmentationType
    messages: MessagesContainer
    initial_datapoint_id: Optional[int]
    created_at: datetime
    category: str


@dataclass
class ModelDTO:
    id: int
    model_name: str
    parent_model_id: Optional[int]
    version: int
    created_at: datetime
    project_id: int
    datasets: List[int]
    training_run: Optional[int]


@dataclass
class ModelEvaluationDTO:
    id: int
    model_id: int
    datapoint_id: int
    evaluation_type: EvaluationType
    helpful_score: int
    honest_score: int
    harmless_score: int
    datapoint: int
    created_at: datetime


@dataclass
class TrainingRunDTO:
    id: int
    model_id: int
    epochs: int
    learning_rate_multiplier: float
    batch_size: int
    created_at: datetime
