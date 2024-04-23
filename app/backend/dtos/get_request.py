from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from ..database.schema import DatasetCategory, AugmentationType


@dataclass
class GetProjectsDTO:
    project_name: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class GetModelsByProjectIdDTO:
    project_id: int
    name: Optional[str] = None
    version: Optional[int] = None


@dataclass
class GetDatasetsByModelIdDTO:
    model_id: int
    created_at: Optional[datetime] = None
    dataset_name: Optional[str] = None
    augmented: Optional[bool] = None
    category: Optional[DatasetCategory] = None


@dataclass
class GetDatapointsByDatasetIdDTO:
    dataset_id: int
    coherence_score: Optional[int] = None
    relevance_score: Optional[int] = None
    semantic_similarity: Optional[float] = None
    augmentation_type: Optional[AugmentationType] = None
    category: Optional[str] = None
