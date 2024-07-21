from dataclasses import dataclass
from datetime import datetime
from app.backend.database.schema import DatasetCategory, AugmentationType


@dataclass
class GetProjectsDTO:
    project_name: str | None = None
    created_at: datetime | None = None


@dataclass
class GetModelsDTO:
    model_name: str | None = None
    created_at: datetime | None = None
    version: str | None = None
    project_id: int | None = None
    is_global: bool | None = None
    exlude_project_id: int | None = None
    is_checkpoint_model: bool | None = None
    only_original_models: bool | None = None
    fine_tuning_job_id: str | None = None


@dataclass
class GetDatasetsDTO:
    dataset_name: str | None = None
    augmented: bool | None = None
    category: DatasetCategory | None = None
    initial_dataset_ids: list[int] | None = None
    project_id: int | None = None
    is_global: bool | None = None
    exlude_project_id: int | None = None


@dataclass
class GetModelsByProjectIdDTO:
    project_id: int
    name: str | None = None
    version: str | None = None


@dataclass
class GetDatasetsByModelIdDTO:
    model_id: int
    created_at: datetime | None = None
    dataset_name: str | None = None
    augmented: bool | None = None
    category: DatasetCategory | None = None


@dataclass
class GetDatapointsByDatasetIdDTO:
    dataset_id: int
    augmentation_type: AugmentationType | None = None


@dataclass
class GetTrainingRunsDTO:
    model_id: int | None = None
    seed: int | None = None
    epochs: int | None = None
    learning_rate_multiplier: float | None = None
    batch_size: int | None = None
    fine_tuning_model: str | None = None
    project_id: int | None = None


@dataclass
class GetDataPointEvaluationsDTO:
    model_id: int
    datapoint_id: int | None = None
    coherence_score: int | None = None
    relevance_score: int | None = None
    semantic_similarity_score: float | None = None


@dataclass
class GetModelEvalautionsDTO:
    model_id: int
    datapoint_id: int | None = None
    evaluation_type: int | None = None
    helpful_score: int | None = None
    honest_score: int | None = None
    harmless_score: int | None = None
    semantic_similarity_score: float | None = None
