from typing import Optional, Dict, TypedDict
from dataclasses import dataclass, field
from ..database.schema import DatasetCategory, AugmentationType, EvaluationType
from ..custom_types.typedicts import MessagesContainer


@dataclass
class CreateProjectDTO:
    project_name: str
    description: str | None = None
    model_ids: list[int] = field(default_factory=list)
    dataset_ids: list[int] = field(default_factory=list)


@dataclass
class CreateDatasetDTO:
    dataset_name: str
    augmented: bool
    category: DatasetCategory
    project_ids: list[int] = field(default_factory=list)
    initial_dataset_id: int | None = None
    test_dataset_id: int | None = None
    datapoint_ids: list[int] = field(default_factory=list)


@dataclass
class CreateDataPointDTO:
    dataset_id: int
    messages: MessagesContainer
    category: str
    coherence_score: int | None = None
    relevance_score: int | None = None
    semantic_similarity_score: float | None = None
    augmentation_type: AugmentationType | None = None
    initial_datapoint_id: int | None = None


@dataclass
class CreateModelDTO:
    model_name: str
    version: int
    project_id: int
    dataset_ids: list[int] = field(default_factory=list)
    parent_model_id: int | None = None
    training_run_id: int | None = None


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
