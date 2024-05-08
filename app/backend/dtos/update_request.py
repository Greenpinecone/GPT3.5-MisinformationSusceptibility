from typing import Optional, Dict
from datetime import datetime
from dataclasses import dataclass, field
from ..database.schema import DatasetCategory, EvaluationType, AugmentationType
from ..dtos.create_request import MessagesContainer
from ..custom_types.dataclasses import LinkedData


@dataclass
class UpdateProjectDTO:
    id: int
    project_name: str
    description: str | None = None
    model_ids: list[int] = field(default_factory=list)
    dataset_ids: list[int] = field(default_factory=list)


@dataclass
class UpdateDatasetDTO:
    id: int
    dataset_name: str
    augmented: bool
    category: DatasetCategory
    initial_dataset_id: int | None = None
    test_dataset_id: int | None = None
    project_ids: list[int] = field(default_factory=list)
    datapoint_ids: list[int] = field(default_factory=list)


# A LinkedData list is passed with this update request. For each object in this Linked Data, the dataset id is taken as context and the datapoint ids are added / deleted based on the provided list of related datapoint ids. This means if ids are left out, compared to the current related ids, they are removed from teh relation, if some are added they are added to the relation. If all relations to other datapoints within a dataset context are removed, the relation to the dataset is removed as well. If an object does not occur / has no dataset_id for context inside the list, the relations of this dataset context stay uneffected.
@dataclass
class UpdateDataPointDTO:
    id: int
    messages: MessagesContainer | None = None
    category: str | None = None
    linked_datapoint_ids_per_dataset_id: LinkedData = field(
        default_factory=LinkedData)
    augmentation_type: AugmentationType | None = None
    coherence_score: int | None = None
    relevance_score: int | None = None
    semantic_similarity_score: float | None = None
    initial_datapoint_id: int | None = None


@dataclass
class UpdateModelDTO:
    id: int
    model_name: str
    version: int
    project_id: int
    dataset_ids: list[int] = field(default_factory=list)
    parent_model_id: int | None = None
    training_run_id: int | None = None


@dataclass
class UpdateModelEvaluationDTO:
    id: int
    model_id: int
    datapoint_id: int
    evaluation_type: EvaluationType
    helpful_score: int
    honest_score: int
    harmless_score: int


@dataclass
class UpdateTrainingRunDTO:
    id: int
    model_id: int
    epochs: int
    learning_rate_multiplier: float
    batch_size: int
