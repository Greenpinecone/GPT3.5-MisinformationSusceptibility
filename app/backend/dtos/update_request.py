from typing import Optional, Dict
from datetime import datetime
from dataclasses import dataclass, field
from ..database.schema import DatasetCategory, EvaluationType, AugmentationType


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


class UpdateDataPointDTO:
    id: int
    related_datapoint_ids: list[int] | None = None
    coherence_score: int | None = None
    relevance_score: int | None = None
    semantic_similarity_score: float | None = None


@dataclass
class UpdateModelDTO:
    id: int
    model_name: str | None = None
    # Removes / adds Models from / to projects
    project_ids: list[int] | None = None
    is_global: bool | None = None
    # Can only be updated if no values has been set already
    underlying_fine_tuned_model: str | None = None
    full_fine_tuned_model_id: str | None = None


@dataclass
class UpdateModelEvaluationDTO:
    id: int
    evaluation_type: EvaluationType | None = None
    helpful_score: int | None = None
    honest_score: int | None = None
    harmless_score: int | None = None
