"""
This module contains data transfer objects (DTOs) used for get requests.
These DTOs define the structure and types of data required for retrieving various entities in the application.
"""


from dataclasses import dataclass
from datetime import datetime
from app.backend.database.schema import DatasetCategory, AugmentationType


@dataclass
class GetProjectsDTO:
    """
    Data transfer object for retrieving project details.

    Attributes:
        project_name (str | None): The name of the project (optional).
        created_at (datetime | None): The creation date of the project (optional).
    """

    project_name: str | None = None
    created_at: datetime | None = None


@dataclass
class GetModelsDTO:
    """
    Data transfer object for retrieving model details.

    Attributes:
        model_name (str | None): The name of the model (optional).
        created_at (datetime | None): The creation date of the model (optional).
        version (str | None): The version of the model (optional).
        project_id (int | None): The ID of the associated project (optional).
        is_global (bool | None): Indicates if the model is global (optional).
        exlude_project_id (int | None): The ID of the project to exclude (optional).
        is_checkpoint_model (bool | None): Indicates if the model is a checkpoint model (optional).
        only_original_models (bool | None): Indicates if only original models should be retrieved (optional).
        fine_tuning_job_id (str | None): The ID of the fine-tuning job (optional).
    """

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
    """
    Data transfer object for retrieving dataset details.

    Attributes:
        dataset_name (str | None): The name of the dataset (optional).
        augmented (bool | None): Indicates if the dataset is augmented (optional).
        category (DatasetCategory | None): The category of the dataset (optional).
        initial_dataset_ids (list[int] | None): List of initial dataset IDs (optional).
        project_id (int | None): The ID of the associated project (optional).
        is_global (bool | None): Indicates if the dataset is global (optional).
        exlude_project_id (int | None): The ID of the project to exclude (optional).
    """

    dataset_name: str | None = None
    augmented: bool | None = None
    category: DatasetCategory | None = None
    initial_dataset_ids: list[int] | None = None
    project_id: int | None = None
    is_global: bool | None = None
    exlude_project_id: int | None = None


@dataclass
class GetModelsByProjectIdDTO:
    """
    Data transfer object for retrieving models by project ID.

    Attributes:
        project_id (int): The ID of the project.
        name (str | None): The name of the model (optional).
        version (str | None): The version of the model (optional).
    """

    project_id: int
    name: str | None = None
    version: str | None = None


@dataclass
class GetDatasetsByModelIdDTO:
    """
    Data transfer object for retrieving datasets by model ID.

    Attributes:
        model_id (int): The ID of the model.
        created_at (datetime | None): The creation date of the dataset (optional).
        dataset_name (str | None): The name of the dataset (optional).
        augmented (bool | None): Indicates if the dataset is augmented (optional).
        category (DatasetCategory | None): The category of the dataset (optional).
    """

    model_id: int
    created_at: datetime | None = None
    dataset_name: str | None = None
    augmented: bool | None = None
    category: DatasetCategory | None = None


@dataclass
class GetDatapointsByDatasetIdDTO:
    """
    Data transfer object for retrieving datapoints by dataset ID.

    Attributes:
        dataset_id (int): The ID of the dataset.
        augmentation_type (AugmentationType | None): The type of augmentation applied to the datapoint (optional).
    """

    dataset_id: int
    augmentation_type: AugmentationType | None = None


@dataclass
class GetTrainingRunsDTO:
    """
    Data transfer object for retrieving training run details.

    Attributes:
        model_id (int | None): The ID of the model being trained (optional).
        seed (int | None): The seed for random number generation (optional).
        epochs (int | None): The number of epochs for training (optional).
        learning_rate_multiplier (float | None): The learning rate multiplier (optional).
        batch_size (int | None): The batch size for training (optional).
        fine_tuning_model (str | None): The fine-tuning model used for the training run (optional).
        project_id (int | None): The ID of the associated project (optional).
    """

    model_id: int | None = None
    seed: int | None = None
    epochs: int | None = None
    learning_rate_multiplier: float | None = None
    batch_size: int | None = None
    fine_tuning_model: str | None = None
    project_id: int | None = None


@dataclass
class GetDataPointEvaluationsDTO:
    """
    Data transfer object for retrieving datapoint evaluations.

    Attributes:
        model_id (int): The ID of the model used for evaluation.
        datapoint_id (int | None): The ID of the datapoint being evaluated (optional).
        coherence_score (int | None): The coherence score (optional).
        relevance_score (int | None): The relevance score (optional).
        semantic_similarity_score (float | None): The semantic similarity score (optional).
    """

    model_id: int
    datapoint_id: int | None = None
    coherence_score: int | None = None
    relevance_score: int | None = None
    semantic_similarity_score: float | None = None


@dataclass
class GetModelEvalautionsDTO:
    """
    Data transfer object for retrieving model evaluations.

    Attributes:
        model_id (int): The ID of the model being evaluated.
        datapoint_id (int | None): The ID of the datapoint being evaluated (optional).
        evaluation_type (int | None): The evaluation type (optional).
        helpful_score (int | None): The helpful score (optional).
        honest_score (int | None): The honest score (optional).
        harmless_score (int | None): The harmless score (optional).
        semantic_similarity_score (float | None): The semantic similarity score (optional).
    """

    model_id: int
    datapoint_id: int | None = None
    evaluation_type: int | None = None
    helpful_score: int | None = None
    honest_score: int | None = None
    harmless_score: int | None = None
    semantic_similarity_score: float | None = None
