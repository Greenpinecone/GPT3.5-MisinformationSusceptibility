from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from app.backend.custom_types.typedicts import AugmentationConfiguration, EDAParams, GoogleBTParams
from app.backend.database.schema import DatasetCategory, EvaluationType, AugmentationType, FineTuningCompany
from ..dtos.create_request import MessagesContainer


# Only for conversion from database entities not for requests
@dataclass
class ProjectDTO:
    id: int
    project_name: str
    description: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
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
    test_dataset_id: int | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
    initial_dataset_ids: list[int] = field(default_factory=list)
    model_ids: list[int] = field(default_factory=list)
    project_ids: list[int] = field(default_factory=list)
    datapoint_ids: list[int] = field(default_factory=list)


@dataclass
class DataPointDTO:
    id: int
    messages: MessagesContainer
    dataset_id: int
    related_datapoints: list['DataPointDTO']
    augmentation_type: AugmentationType | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
    initial_datapoint_id: int | None = None


@dataclass
class DataPointWithInitialDataPointDTO:
    id: int
    messages: MessagesContainer
    dataset_id: int
    augmentation_type: AugmentationType
    initial_datapoint: 'DataPointWithInitialDataPointDTO'
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())


@dataclass
class DataPointEvaluationDTO:
    id: int
    datapoint_id: int
    model_id: int
    semantic_similarity_score: float
    coherence_score: int | None = None
    relevance_score: int | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())


@dataclass
class ComplexDatasetDTO:
    id: int
    dataset_name: str
    augmented: bool
    category: DatasetCategory
    fine_tuning_model: str
    fine_tuning_company: FineTuningCompany
    # The formatting of the underlying fine tuning data based on the company you want to fine tune with.
    fine_tuning_formatting: str
    is_global: bool = False
    test_dataset: list[Optional['ComplexDatasetDTO']] | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
    initial_datasets: list['ComplexDatasetDTO'] = field(default_factory=list)
    model_ids: list[int] = field(default_factory=list)
    project_ids: list[int] = field(default_factory=list)
    datapoints: list[DataPointDTO] = field(default_factory=list)


@dataclass
class ModelDTO:
    id: int
    model_name: str
    version: str
    project_ids: list[int]
    training_dataset_ids: list[int]
    uuid: str
    fine_tuning_checkpoint_job_id: str | None = None
    fine_tuned_model_id: str | None = None
    is_global: bool = False
    fine_tuning_job_id: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
    parent_model_id: int | None = None
    training_run_id: int | None = None
    is_checkpoint_model: bool | None = None
    checkpoint_step: int | None = None


@dataclass
class ComplexDataPointEvaluationDTO:
    id: int
    datapoint: DataPointWithInitialDataPointDTO
    model_id: int
    coherence_score: int
    relevance_score: int
    semantic_similarity_score: float
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())


@dataclass
class ModelEvaluationDTO:
    id: int
    model_id: int
    datapoint_id: int
    evaluation_type: EvaluationType
    helpful_score: int
    honest_score: int
    harmless_score: int
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())


@dataclass
class TrainingRunDTO:
    id: int
    model_id: int
    seed: int
    epochs: int
    learning_rate_multiplier: float
    batch_size: int
    fine_tuning_model: str
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())


@dataclass
class ComplexModelDTO:
    id: int
    model_name: str
    version: str
    project_ids: list[int]
    training_dataset_ids: list[int]
    uuid: str
    fine_tuning_checkpoint_job_id: str | None = None
    fine_tuned_model_id: str | None = None
    is_global: bool = False
    fine_tuning_job_id: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
    is_checkpoint_model: bool | None = None
    checkpoint_step: int | None = None
    parent_model: Optional['ComplexModelDTO'] = None
    training_run: TrainingRunDTO | None = None


@dataclass
class SimpleTrainingRunDTO:
    id: int
    model_name: str
    model_version: str
    fine_tuning_model: str
    seed: int


@dataclass
class CurrentProjectDataDTO:
    id: int
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
    augmentation_configurations: list[AugmentationConfiguration] = field(
        default_factory=list)
    unfinished_progress: bool = False
    current_page: str = ""
    save_checkpoint_models: bool = False
    fine_tuning_step_counter: int = 0
    semantic_similarity_model: dict | None = None
    current_project: ProjectDTO | None = None
    current_fine_tuning_model: ModelDTO | None = None
    selected_model_for_fine_tuning: ComplexModelDTO | None = None
    currently_modified_dataset: ComplexDatasetDTO | None = None
