from dataclasses import dataclass, field
from app.backend.custom_types.typedicts import AugmentationConfiguration, EDAParams, GoogleBTParams
from app.backend.dtos.response import ComplexDatasetDTO, ModelDTO, ProjectDTO, TrainingRunDTO
from app.backend.database.schema import EvaluationType


SENTINEL = object()


@dataclass
class UpdateProjectDTO:
    id: int
    project_name: str | None = None
    description: str | None = None
    model_ids: list[int] | None = None
    dataset_ids: list[int] | None = None


@dataclass
class UpdateDatasetDTO:
    id: int
    dataset_name: str | None = None
    project_ids: list[int] | None = None
    is_global: bool | None = None


@dataclass
class UpdateDataPointDTO:
    id: int
    related_datapoint_ids: list[int] | None = None


@dataclass
class UpdateModelDTO:
    id: int
    model_name: str | None = None
    # Removes / adds Models from / to projects
    project_ids: list[int] | None = None
    is_global: bool | None = None
    training_dataset_ids: list[int] | None = None
    # Can only be updated if no values has been set already
    fine_tuning_job_id: str | None = None
    fine_tuning_checkpoint_job_id: str | None = None
    fine_tuned_model_id: str | None = None


@dataclass
class UpdateModelEvaluationDTO:
    id: int
    evaluation_type: EvaluationType | None = None
    helpful_score: int | None = None
    honest_score: int | None = None
    harmless_score: int | None = None


@dataclass
class UpdateTrainingRunDTO:
    id: int
    epochs: int | None = None
    learning_rate_multiplier: float | None = None
    batch_size: int | None = None
    seed: int | None = None


class UpdateDataPointEvaluationDTO:
    id: int
    coherence_score: int | None = None
    relevance_score: int | None = None
    semantic_similarity_score: float | None = None


# Uses SENTINAL default values to differentiate for partial updates if a field is set to None
@dataclass
class UpdateCurrentProjectDataDTO:
    id: int
    semantic_similarity_model: dict | None = field(
        default_factory=lambda: SENTINEL)
    augmentation_configurations: list[AugmentationConfiguration] | None = field(
        default_factory=lambda: SENTINEL)
    unfinished_progress: bool | None = field(default_factory=lambda: SENTINEL)
    current_page: str | None = field(default_factory=lambda: SENTINEL)
    save_checkpoint_models: bool | None = field(
        default_factory=lambda: SENTINEL)
    fine_tuning_step_counter: int | None = field(
        default_factory=lambda: SENTINEL)
    current_project_id: int | None = field(
        default_factory=lambda: SENTINEL)
    current_fine_tuning_model_id: int | None = field(
        default_factory=lambda: SENTINEL)
    selected_model_for_fine_tuning_id: int | None = field(
        default_factory=lambda: SENTINEL)
    currently_modified_dataset_id: int | None = field(
        default_factory=lambda: SENTINEL)
