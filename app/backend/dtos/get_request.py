from dataclasses import dataclass, field
from datetime import datetime
from ..database.schema import DatasetCategory, AugmentationType


@dataclass
class GetProjectsDTO:
    project_name: str | None = None
    created_at: datetime | None = None


@dataclass
class GetModelsDTO:
    model_name: str | None = None
    created_at: datetime | None = None
    version: int | None = None
    project_id: int | None = None
    is_global: bool | None = None
    fine_tuning_model: str | None = None


@dataclass
class GetDatasetsDTO:
    dataset_name: str | None = None
    augmented: bool | None = None
    category: DatasetCategory | None = None
    initial_dataset_id: int | None = None
    project_id: int | None = None
    is_global: bool | None = None


@dataclass
class GetModelsByProjectIdDTO:
    project_id: int
    name: str | None = None
    version: int | None = None
    fine_tuning_model: str | None = None


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
    coherence_score: int | None = None
    relevance_score: int | None = None
    semantic_similarity: float | None = None
    augmentation_type: AugmentationType | None = None
    category: str | None = None
