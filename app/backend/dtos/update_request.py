"""
This module defines Data Transfer Objects (DTOs) for update requests.
These DTOs are used to encapsulate data for updating various entities in the system.
"""


from dataclasses import dataclass, field
from app.backend.custom_types.typedicts import AugmentationConfiguration
from app.backend.database.schema import EvaluationType


SENTINEL = object()


@dataclass
class UpdateProjectDTO:
    """
    DTO for updating a project.

    Attributes:
        id (int): The unique identifier of the project.
        project_name (str | None): The name of the project (optional).
        description (str | None): The description of the project (optional).
        model_ids (list[int] | None): List of model IDs associated with the project (optional).
        dataset_ids (list[int] | None): List of dataset IDs associated with the project (optional).
    """

    id: int
    project_name: str | None = None
    description: str | None = None
    model_ids: list[int] | None = None
    dataset_ids: list[int] | None = None


@dataclass
class UpdateDatasetDTO:
    """
    DTO for updating a dataset.

    Attributes:
        id (int): The unique identifier of the dataset.
        dataset_name (str | None): The name of the dataset (optional).
        project_ids (list[int] | None): List of project IDs associated with the dataset (optional).
        is_global (bool | None): Indicates if the dataset is global (optional).
    """

    id: int
    dataset_name: str | None = None
    project_ids: list[int] | None = None
    is_global: bool | None = None


@dataclass
class UpdateDataPointDTO:
    """
    DTO for updating a datapoint.

    Attributes:
        id (int): The unique identifier of the datapoint.
        related_datapoint_ids (list[int] | None): List of related datapoint IDs (optional).
        evaluation_type (EvaluationType | None): The evaluation type (optional).
    """

    id: int
    related_datapoint_ids: list[int] | None = None
    evaluation_type: EvaluationType | None = None


@dataclass
class UpdateModelDTO:
    """
    DTO for updating a model.

    Attributes:
        id (int): The unique identifier of the model.
        model_name (str | None): The name of the model (optional).
        project_ids (list[int] | None): List of project IDs associated with the model (optional).
        is_global (bool | None): Indicates if the model is global (optional).
        training_dataset_ids (list[int] | None): List of training dataset IDs (optional).
        semantic_similarity_model (str | None): The semantic similarity model used for evaluation (optional).
        fine_tuning_job_id (str | None): The ID of the fine-tuning job (optional).
        fine_tuning_checkpoint_job_id (str | None): The ID of the fine-tuning checkpoint job (optional).
        fine_tuned_model_id (str | None): The ID of the fine-tuned model (optional).
        augmentation_configurations (list[AugmentationConfiguration] | None): List of augmentation configurations (optional).
    """

    id: int
    model_name: str | None = None
    # Removes / adds Models from / to projects
    project_ids: list[int] | None = None
    is_global: bool | None = None
    training_dataset_ids: list[int] | None = None
    semantic_similarity_model: str | None = None
    # Can only be updated if no values has been set already
    fine_tuning_job_id: str | None = None
    fine_tuning_checkpoint_job_id: str | None = None
    fine_tuned_model_id: str | None = None
    augmentation_configurations: list[AugmentationConfiguration] | None = None


@dataclass
class UpdateModelEvaluationDTO:
    """
    DTO for updating a model evaluation.

    Attributes:
        id (int): The unique identifier of the model evaluation.
        evaluation_type (EvaluationType | None): The evaluation type (optional).
        helpful_score (int | None): The helpful score (optional).
        honest_score (int | None): The honest score (optional).
        harmless_score (int | None): The harmless score (optional).
        semantic_similarity_score (float | None): The semantic similarity score (optional).
    """

    id: int
    evaluation_type: EvaluationType | None = None
    helpful_score: int | None = None
    honest_score: int | None = None
    harmless_score: int | None = None
    semantic_similarity_score: float | None = None


@dataclass
class UpdateTrainingRunDTO:
    """
    DTO for updating a training run.

    Attributes:
        id (int): The unique identifier of the training run.
        epochs (int | None): The number of epochs for training (optional).
        learning_rate_multiplier (float | None): The learning rate multiplier (optional).
        batch_size (int | None): The batch size (optional).
        seed (int | None): The seed used for random number generation during training (optional).
    """

    id: int
    epochs: int | None = None
    learning_rate_multiplier: float | None = None
    batch_size: int | None = None
    seed: int | None = None


@dataclass
class UpdateDataPointEvaluationDTO:
    """
    DTO for updating a datapoint evaluation.

    Attributes:
        id (int): The unique identifier of the datapoint evaluation.
        coherence_score (int | None): The coherence score (optional).
        relevance_score (int | None): The relevance score (optional).
        semantic_similarity_score (float | None): The semantic similarity score (optional).
    """

    id: int
    coherence_score: int | None = None
    relevance_score: int | None = None
    semantic_similarity_score: float | None = None


# Uses SENTINAL default values to differentiate for partial updates if a field is set to None
@dataclass
class UpdateCurrentProjectDataDTO:
    """
    DTO for updating current project data. Uses SENTINEL default values to differentiate for partial updates if a field is set to None.

    Attributes:
        id (int): The unique identifier of the current project data.
        semantic_similarity_model (dict | None): The semantic similarity model configuration (optional).
        current_augmented_datapoint_evaluation_ids (list[int] | None): List of IDs of the current augmented datapoint evaluations (optional).
        selected_statistic_models (list[int] | None): List of selected statistic model IDs (optional).
        current_augmentation_configurations (list[AugmentationConfiguration] | None): List of current augmentation configurations (optional).
        unfinished_progress (bool | None): Indicates if there is unfinished progress in the current project (optional).
        current_page (str | None): The current page in the project workflow (optional).
        save_checkpoint_models (bool | None): Indicates if checkpoint models should be saved (optional).
        fine_tuning_step_counter (int | None): The current fine-tuning step counter (optional).
        current_project_id (int | None): The ID of the current project (optional).
        current_fine_tuning_model_id (int | None): The ID of the current fine-tuning model (optional).
        selected_model_for_fine_tuning_id (int | None): The ID of the selected model for fine-tuning (optional).
        currently_modified_dataset_id (int | None): The ID of the currently modified dataset (optional).
        generated_checkpoint_model_ids (list[int] | None): List of generated checkpoint model IDs (optional).
    """

    id: int
    semantic_similarity_model: dict | None = field(
        default_factory=lambda: SENTINEL)
    current_augmented_datapoint_evaluation_ids: list[int] | None = field(
        default_factory=lambda: SENTINEL)
    selected_statistic_models: list[int] | None = field(
        default_factory=lambda: SENTINEL)
    current_augmentation_configurations: list[AugmentationConfiguration] | None = field(
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
    generated_checkpoint_model_ids: list[int] | None = field(
        default_factory=lambda: SENTINEL)
