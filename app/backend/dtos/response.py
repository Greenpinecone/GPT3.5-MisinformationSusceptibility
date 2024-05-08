from typing import Optional, Dict
from datetime import datetime
from dataclasses import dataclass, field
from ..database.schema import DatasetCategory, EvaluationType, AugmentationType
from ..dtos.create_request import MessagesContainer
from ..custom_types.dataclasses import LinkedData

# Only for conversion from database entities not for requests


@dataclass
class ProjectDTO:
    id: int
    project_name: str
    description: str | None = None
    created_at: datetime = datetime.now(
    ).astimezone()
    model_ids: list[int] = field(default_factory=list)
    dataset_ids: list[int] = field(default_factory=list)


@dataclass
class DatasetDTO:
    id: int
    dataset_name: str
    augmented: bool
    category: DatasetCategory
    created_at: datetime = datetime.now(
    ).astimezone()
    initial_dataset_id: int | None = None
    test_dataset_id: int | None = None
    project_ids: list[int] = field(default_factory=list)
    datapoint_ids: list[int] = field(default_factory=list)


@dataclass
class DataPointDTO:
    id: int
    messages: MessagesContainer
    category: str
    dataset_ids: list[int] = field(default_factory=list)
    linked_datapoint_ids_per_dataset_id: LinkedData = field(
        default_factory=LinkedData)
    created_at: datetime = datetime.now(
    ).astimezone()
    augmentation_type: AugmentationType | None = None
    coherence_score: int | None = None
    relevance_score: int | None = None
    semantic_similarity_score: float | None = None
    initial_datapoint_id: int | None = None


@dataclass
class SimpleDataPointDTO:
    id: int
    messages: MessagesContainer
    category: str
    created_at: datetime = datetime.now(
    ).astimezone()
    augmentation_type: AugmentationType | None = None
    coherence_score: int | None = None
    relevance_score: int | None = None
    semantic_similarity_score: float | None = None
    initial_datapoint_id: int | None = None


@dataclass
class ModelDTO:
    id: int
    model_name: str
    version: int
    project_id: int
    uuid: str
    created_at: datetime = datetime.now(
    ).astimezone()
    dataset_ids: list[int] = field(default_factory=list)
    parent_model_id: int | None = None
    training_run_id: int | None = None


@dataclass
class ModelEvaluationDTO:
    id: int
    model_id: int
    datapoint_id: int
    evaluation_type: EvaluationType
    helpful_score: int
    honest_score: int
    harmless_score: int
    created_at: datetime = datetime.now(
    ).astimezone()


@dataclass
class TrainingRunDTO:
    id: int
    model_id: int
    epochs: int
    learning_rate_multiplier: float
    batch_size: int
    created_at: datetime = datetime.now(
    ).astimezone()
