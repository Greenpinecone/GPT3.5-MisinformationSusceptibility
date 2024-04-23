from typing import Optional, Dict
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
    model_ids: Optional[list[int]] = None
    dataset_ids: Optional[list[int]] = None


@dataclass
class DatasetDTO:
    id: int
    dataset_name: str
    augmented: bool
    category: DatasetCategory
    created_at: datetime
    initial_dataset_id: Optional[int] = None
    test_dataset_id: Optional[int] = None
    project_ids: Optional[list[int]] = None
    datapoint_ids: Optional[list[int]] = None


@dataclass
class DataPointDTO:
    id: int
    dataset_id: int
    augmentation_type: AugmentationType
    messages: MessagesContainer
    created_at: datetime
    category: str
    coherence_score: Optional[int] = None
    relevance_score: Optional[int] = None
    semantic_similarity_score: Optional[float] = None
    initial_datapoint_id: Optional[int] = None


@dataclass
class ModelDTO:
    id: int
    model_name: str
    version: int
    created_at: datetime
    project_id: int
    dataset_ids: list[int]
    parent_model_id: Optional[int] = None
    training_run_id: Optional[int] = None


@dataclass
class ModelEvaluationDTO:
    id: int
    model_id: int
    datapoint_id: int
    evaluation_type: EvaluationType
    helpful_score: int
    honest_score: int
    harmless_score: int
    created_at: datetime


@dataclass
class TrainingRunDTO:
    id: int
    model_id: int
    epochs: int
    learning_rate_multiplier: float
    batch_size: int
    created_at: datetime
