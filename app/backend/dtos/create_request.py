from typing import List, Optional, Dict, TypedDict
from dataclasses import dataclass
from ..database.schema import DatasetCategory, AugmentationType, EvaluationType
from ..custom_types.typedicts import MessagesContainer


@dataclass
class CreateProjectDTO:
    project_name: str
    description: Optional[str] = None
    model_ids: Optional[List[int]] = None
    dataset_ids: Optional[List[int]] = None


@dataclass
class CreateDatasetDTO:
    dataset_name: str
    augmented: bool
    category: DatasetCategory
    project_ids: List[int]
    initial_dataset_id: Optional[int]
    test_dataset_id: Optional[int]
    datapoint_ids: List[int]


@dataclass
class CreateDataPointDTO:
    dataset_id: int
    coherence_score: Optional[int]
    relevance_score: Optional[int]
    semantic_similarity_score: Optional[float]
    augmentation_type: Optional[AugmentationType]
    messages: MessagesContainer
    initial_datapoint_id: Optional[int]
    category: str


@dataclass
class CreateModelDTO:
    model_name: str
    parent_model_id: Optional[int]
    version: int
    project_id: int
    dataset_ids: List[int]
    training_run_id: Optional[int]


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
