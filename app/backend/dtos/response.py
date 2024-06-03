from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass, field
from ..database.schema import DatasetCategory, EvaluationType, AugmentationType, FineTuningCompany, FineTuningModelVersions
from ..dtos.create_request import MessagesContainer


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
    fine_tuning_model: str
    fine_tuning_company: FineTuningCompany
    # The formatting of the underlying fine tuning data based on the company you want to fine tune with.
    fine_tuning_formatting: str
    is_global: bool = False
    created_at: datetime = datetime.now(
    ).astimezone()
    initial_dataset_id: int | None = None
    test_dataset_id: int | None = None
    model_id: int | None = None
    project_ids: list[int] = field(default_factory=list)
    datapoint_ids: list[int] = field(default_factory=list)


@dataclass
class DataPointDTO:
    id: int
    messages: MessagesContainer
    dataset_id: int
    related_datapoints: list['DataPointDTO']
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
    project_ids: list[int]
    training_dataset_id: int
    is_global: bool = False
    fine_tuning_model: str | None = None
    full_fine_tuned_model_id: str | None = None
    created_at: datetime = datetime.now(
    ).astimezone()
    parent_model_id: int | None = None
    training_run_id: int | None = None
    is_checkpoint_model: bool | None = None
    checkpoint_step: int | None = None


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
