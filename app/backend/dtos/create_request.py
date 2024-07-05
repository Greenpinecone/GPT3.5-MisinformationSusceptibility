from dataclasses import dataclass, field
from app.backend.database.schema import DatasetCategory, AugmentationType, EvaluationType, FineTuningCompany
from ..custom_types.typedicts import AugmentationConfiguration, MessagesContainer


@dataclass
class CreateProjectDTO:
    project_name: str
    description: str | None = None
    model_ids: list[int] | None = None
    dataset_ids: list[int] | None = None


@dataclass
class CreateDatasetDTO:
    dataset_name: str
    category: DatasetCategory
    augmented: bool
    fine_tuning_company: FineTuningCompany
    # The fine tuning model this data is formatted for
    fine_tuning_model: str
    # The formatting of the underlying fine tuning data based on the company you want to fine tune with. Neeed for conversionbetween fien tuning schematas if the same dataset uploaded for openai is used for google. TODO: Implement typedicts and mappers at some point if needed.
    fine_tuning_formatting: str
    project_ids: list[int] | None = None
    initial_dataset_ids: list[int] | None = None
    test_dataset_id: int | None = None
    datapoint_ids: list[int] | None = None
    is_global: bool = False


@dataclass
class CreateDataPointDTO:
    messages: MessagesContainer
    dataset_id: int | None = None
    related_datapoint_ids: list[int] | None = None
    augmentation_type: AugmentationType | None = None
    initial_datapoint_id: int | None = None


@dataclass
class CreateModelDTO:
    model_name: str
    project_ids: list[int]
    training_dataset_ids: list[int]
    augmentation_configurations: list[AugmentationConfiguration] | None = None
    semantic_similarity_model: str | None = None
    fine_tuning_job_id: str | None = None
    fine_tuning_checkpoint_job_id: str | None = None
    fine_tuned_model_id: str | None = None
    parent_model_id: int | None = None
    training_run_id: int | None = None
    is_global: bool = False
    is_checkpoint_model: bool = False
    checkpoint_step: int | None = None


@dataclass
class CreateModelEvaluationDTO:
    model_id: int
    datapoint_id: int
    messages: MessagesContainer
    semantic_similarity_score: float | None = None
    evaluation_type: EvaluationType | None = None
    helpful_score: int | None = None
    honest_score: int | None = None
    harmless_score: int | None = None


@dataclass
class CreateTrainingRunDTO:
    model_id: int
    fine_tuning_model: str
    epochs: int | None = None
    learning_rate_multiplier: float | None = None
    batch_size: int | None = None
    seed: int | None = None


@dataclass
class CreateDataPointEvaluationDTO:
    datapoint_id: int
    model_id: int
    semantic_similarity_score: float
    coherence_score: int | None = None
    relevance_score: int | None = None
