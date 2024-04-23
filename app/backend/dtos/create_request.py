from typing import Optional, Dict, TypedDict
from dataclasses import dataclass
from ..database.schema import DatasetCategory, AugmentationType, EvaluationType
from ..custom_types.typedicts import MessagesContainer


@dataclass
class CreateProjectDTO:
    project_name: str
    description: Optional[str] = None
    model_ids: Optional[list[int]] = None
    dataset_ids: Optional[list[int]] = None


@dataclass
class CreateDatasetDTO:
    dataset_name: str
    augmented: bool
    category: DatasetCategory
    project_ids: Optional[list[int]] = None
    initial_dataset_id: Optional[int] = None
    test_dataset_id: Optional[int] = None
    datapoint_ids: Optional[list[int]] = None


@dataclass
class CreateDataPointDTO:
    dataset_id: int
    messages: MessagesContainer
    category: str
    coherence_score: Optional[int] = None
    relevance_score: Optional[int] = None
    semantic_similarity_score: Optional[float] = None
    augmentation_type: Optional[AugmentationType] = None
    initial_datapoint_id: Optional[int] = None


@dataclass
class CreateModelDTO:
    model_name: str
    version: int
    project_id: int
    dataset_ids: list[int]
    parent_model_id: Optional[int] = None
    training_run_id: Optional[int] = None


@dataclass
class CreateModelEvaluationDTO:
    model_id: int
    datapoint_id: int
    evaluation_type: EvaluationType
    helpful_score: int
    honest_score: int
    harmless_score: int


@dataclass
class CreateTrainingRunDTO:
    model_id: int
    epochs: int
    learning_rate_multiplier: float
    batch_size: int
