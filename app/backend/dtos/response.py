"""
This module contains data transfer objects (DTOs) used for responses from the service layer.
These DTOs define the structure and types of data returned by the service layer to the clients.
"""


from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from app.backend.custom_types.typedicts import AugmentationConfiguration
from app.backend.database.schema import DatasetCategory, EvaluationType, AugmentationType, FineTuningCompany
from app.backend.dtos.create_request import MessagesContainer


@dataclass
class ProjectDTO:
    """
    Data transfer object for returning project details.

    Attributes:
        id (int): The unique identifier of the project.
        project_name (str): The name of the project.
        description (str | None): The description of the project (optional).
        created_at (datetime): The creation date of the project.
        model_ids (list[int]): List of model IDs associated with the project.
        dataset_ids (list[int]): List of dataset IDs associated with the project.
    """

    id: int
    project_name: str
    description: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
    model_ids: list[int] = field(default_factory=list)
    dataset_ids: list[int] = field(default_factory=list)


@dataclass
class SimpleProjectDTO:
    """
    Data transfer object for returning simplified project details.

    Attributes:
        id (int): The unique identifier of the project.
        project_name (str): The name of the project.
        description (str | None): The description of the project (optional).
        created_at (datetime): The creation date of the project.
    """

    id: int
    project_name: str
    description: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())


@dataclass
class DatasetDTO:
    """
    Data transfer object for returning dataset details.

    Attributes:
        id (int): The unique identifier of the dataset.
        dataset_name (str): The name of the dataset.
        augmented (bool): Indicates if the dataset is augmented.
        category (DatasetCategory): The category of the dataset.
        fine_tuning_model (str): The fine-tuning model the dataset is formatted for.
        fine_tuning_company (FineTuningCompany): The company associated with the fine-tuning.
        fine_tuning_formatting (str): The formatting of the underlying fine-tuning data.
        is_global (bool): Indicates if the dataset is global (default is False).
        test_dataset_id (int | None): The ID of the test dataset (optional).
        created_at (datetime): The creation date of the dataset.
        initial_dataset_ids (list[int]): List of initial dataset IDs associated with the dataset.
        model_ids (list[int]): List of model IDs associated with the dataset.
        project_ids (list[int]): List of project IDs associated with the dataset.
        datapoint_ids (list[int]): List of datapoint IDs associated with the dataset.
    """

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
    """
    Data transfer object for returning datapoint details.

    Attributes:
        id (int): The unique identifier of the datapoint.
        messages (MessagesContainer): The messages contained in the datapoint.
        dataset_id (int): The ID of the dataset the datapoint belongs to.
        related_datapoints (list[DataPointDTO]): List of related datapoints.
        augmentation_type (AugmentationType | None): The type of augmentation applied to the datapoint (optional).
        created_at (datetime): The creation date of the datapoint.
        initial_datapoint_id (int | None): The ID of the initial datapoint from which this datapoint was augmented (optional).
        evaluation_type (EvaluationType | None): The evaluation type of the datapoint (optional).
    """

    id: int
    messages: MessagesContainer
    dataset_id: int
    related_datapoints: list['DataPointDTO']
    augmentation_type: AugmentationType | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
    initial_datapoint_id: int | None = None
    evaluation_type: EvaluationType | None = None


@dataclass
class SimpleDataPointDTO:
    """
    Data transfer object for returning simplified datapoint details.

    Attributes:
        id (int): The unique identifier of the datapoint.
        messages (MessagesContainer): The messages contained in the datapoint.
        augmentation_type (AugmentationType | None): The type of augmentation applied to the datapoint (optional).
        created_at (datetime): The creation date of the datapoint.
    """

    id: int
    messages: MessagesContainer
    augmentation_type: AugmentationType | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())


@dataclass
class DataPointWithInitialDataPointDTO:
    """
    Data transfer object for returning datapoint details along with the initial datapoint.

    Attributes:
        id (int): The unique identifier of the datapoint.
        messages (MessagesContainer): The messages contained in the datapoint.
        dataset_id (int): The ID of the dataset the datapoint belongs to.
        augmentation_type (AugmentationType): The type of augmentation applied to the datapoint.
        initial_datapoint (DataPointWithInitialDataPointDTO): The initial datapoint from which this datapoint was augmented.
        created_at (datetime): The creation date of the datapoint.
    """

    id: int
    messages: MessagesContainer
    dataset_id: int
    augmentation_type: AugmentationType
    initial_datapoint: 'DataPointWithInitialDataPointDTO'
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())


@dataclass
class DataPointEvaluationDTO:
    """
    Data transfer object for returning datapoint evaluation details.

    Attributes:
        id (int): The unique identifier of the datapoint evaluation.
        datapoint_id (int): The ID of the evaluated datapoint.
        model_id (int): The ID of the model used for evaluation.
        semantic_similarity_score (float): The semantic similarity score of the evaluation.
        coherence_score (int | None): The coherence score of the evaluation (optional).
        relevance_score (int | None): The relevance score of the evaluation (optional).
        created_at (datetime): The creation date of the evaluation.
    """

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
    """
    Data transfer object for returning complex dataset details.

    Attributes:
        id (int): The unique identifier of the dataset.
        dataset_name (str): The name of the dataset.
        augmented (bool): Indicates if the dataset is augmented.
        category (DatasetCategory): The category of the dataset.
        fine_tuning_model (str): The fine-tuning model the dataset is formatted for.
        fine_tuning_company (FineTuningCompany): The company associated with the fine-tuning.
        fine_tuning_formatting (str): The formatting of the underlying fine-tuning data.
        is_global (bool): Indicates if the dataset is global (default is False).
        test_dataset (list[Optional[ComplexDatasetDTO]] | None): The test dataset associated with the dataset (optional).
        created_at (datetime): The creation date of the dataset.
        initial_datasets (list[ComplexDatasetDTO]): List of initial datasets associated with the dataset.
        model_ids (list[int]): List of model IDs associated with the dataset.
        project_ids (list[int]): List of project IDs associated with the dataset.
        datapoints (list[DataPointDTO]): List of datapoints contained in the dataset.
    """

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
    """
    Data transfer object for returning model details.

    Attributes:
        id (int): The unique identifier of the model.
        model_name (str): The name of the model.
        version (str): The version of the model.
        project_ids (list[int]): List of project IDs associated with the model.
        training_dataset_ids (list[int]): List of training dataset IDs associated with the model.
        uuid (str): A unique identifier for the model.
        augmentation_configurations (list[AugmentationConfiguration]): List of augmentation configurations for the model.
        semantic_similarity_model (str | None): The semantic similarity model used for evaluation (optional).
        fine_tuning_checkpoint_job_id (str | None): The ID of the fine-tuning checkpoint job (optional).
        fine_tuned_model_id (str | None): The ID of the fine-tuned model (optional).
        is_global (bool): Indicates if the model is global (default is False).
        fine_tuning_job_id (str | None): The ID of the fine-tuning job (optional).
        created_at (datetime): The creation date of the model.
        parent_model_id (int | None): The ID of the parent model (optional).
        training_run_id (int | None): The ID of the training run (optional).
        is_checkpoint_model (bool | None): Indicates if the model is a checkpoint model (optional).
        checkpoint_step (int | None): The checkpoint step at which the model was created (optional).
    """

    id: int
    model_name: str
    version: str
    project_ids: list[int]
    training_dataset_ids: list[int]
    uuid: str
    augmentation_configurations: list[AugmentationConfiguration] = field(
        default_factory=list)
    semantic_similarity_model: str | None = None
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
class ModelWithOriginalProjectDTO:
    """
    Data transfer object for returning model details with the original project.

    Attributes:
        id (int): The unique identifier of the model.
        model_name (str): The name of the model.
        version (str): The version of the model.
        original_project (ProjectDTO): The original project associated with the model.
        is_global (bool): Indicates if the model is global (default is False).
        created_at (datetime): The creation date of the model.
        is_checkpoint_model (bool | None): Indicates if the model is a checkpoint model (optional).
        checkpoint_step (int | None): The checkpoint step at which the model was created (optional).
    """

    id: int
    model_name: str
    version: str
    original_project: ProjectDTO
    is_global: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
    is_checkpoint_model: bool | None = None
    checkpoint_step: int | None = None


@dataclass
class ComplexDataPointEvaluationDTO:
    """
    Data transfer object for returning complex datapoint evaluation details.

    Attributes:
        id (int): The unique identifier of the datapoint evaluation.
        datapoint (DataPointWithInitialDataPointDTO): The evaluated datapoint with initial datapoint details.
        model_id (int): The ID of the model used for evaluation.
        coherence_score (int): The coherence score of the evaluation.
        relevance_score (int): The relevance score of the evaluation.
        semantic_similarity_score (float): The semantic similarity score of the evaluation.
        created_at (datetime): The creation date of the evaluation.
    """

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
    """
    Data transfer object for returning model evaluation details.

    Attributes:
        id (int): The unique identifier of the model evaluation.
        model_id (int): The ID of the model being evaluated.
        datapoint_id (int): The ID of the evaluated datapoint.
        messages (MessagesContainer): The messages contained in the evaluation.
        semantic_similarity_score (float | None): The semantic similarity score of the evaluation (optional).
        evaluation_type (EvaluationType | None): The evaluation type (optional).
        helpful_score (int | None): The helpful score of the evaluation (optional).
        honest_score (int | None): The honest score of the evaluation (optional).
        harmless_score (int | None): The harmless score of the evaluation (optional).
        created_at (datetime): The creation date of the evaluation.
    """

    id: int
    model_id: int
    datapoint_id: int
    messages: MessagesContainer
    semantic_similarity_score: float | None = None
    evaluation_type: EvaluationType | None = None
    helpful_score: int | None = None
    honest_score: int | None = None
    harmless_score: int | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())


@dataclass
class TrainingRunDTO:
    """
    Data transfer object for returning training run details.

    Attributes:
        id (int): The unique identifier of the training run.
        model_id (int): The ID of the model being trained.
        seed (int): The seed used for random number generation during training.
        epochs (int): The number of epochs for training.
        learning_rate_multiplier (float): The learning rate multiplier used during training.
        batch_size (int): The batch size used during training.
        fine_tuning_model (str): The fine-tuning model used for training.
        created_at (datetime): The creation date of the training run.
    """

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
    """
    Data transfer object for returning complex model details.

    Attributes:
        id (int): The unique identifier of the model.
        model_name (str): The name of the model.
        version (str): The version of the model.
        project_ids (list[int]): List of project IDs associated with the model.
        training_dataset_ids (list[int]): List of training dataset IDs associated with the model.
        uuid (str): A unique identifier for the model.
        augmentation_configurations (list[AugmentationConfiguration]): List of augmentation configurations for the model.
        semantic_similarity_model (str | None): The semantic similarity model used for evaluation (optional).
        fine_tuning_checkpoint_job_id (str | None): The ID of the fine-tuning checkpoint job (optional).
        fine_tuned_model_id (str | None): The ID of the fine-tuned model (optional).
        is_global (bool): Indicates if the model is global (default is False).
        fine_tuning_job_id (str | None): The ID of the fine-tuning job (optional).
        created_at (datetime): The creation date of the model.
        is_checkpoint_model (bool | None): Indicates if the model is a checkpoint model (optional).
        checkpoint_step (int | None): The checkpoint step at which the model was created (optional).
        parent_model (Optional[ComplexModelDTO]): The parent model of the current model (optional).
        training_run (TrainingRunDTO | None): The training run details associated with the model (optional).
    """

    id: int
    model_name: str
    version: str
    project_ids: list[int]
    training_dataset_ids: list[int]
    uuid: str
    augmentation_configurations: list[AugmentationConfiguration] = field(
        default_factory=list)
    semantic_similarity_model: str | None = None
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
    """
    Data transfer object for returning simplified training run details.

    Attributes:
        id (int): The unique identifier of the training run.
        model_name (str): The name of the model being trained.
        model_version (str): The version of the model being trained.
        fine_tuning_model (str): The fine-tuning model used for training.
        seed (int): The seed used for random number generation during training.
    """

    id: int
    model_name: str
    model_version: str
    fine_tuning_model: str
    seed: int


@dataclass
class CurrentProjectDataDTO:
    """
    Data transfer object for returning current project data details.

    Attributes:
        id (int): The unique identifier of the current project data.
        created_at (datetime): The creation date of the current project data.
        current_augmented_datapoint_evaluation_ids (list[int]): List of IDs of the current augmented datapoint evaluations.
        current_augmentation_configurations (list[AugmentationConfiguration]): List of current augmentation configurations.
        generated_checkpoint_model_ids (list[int]): List of generated checkpoint model IDs.
        selected_statistic_models (list[int]): List of selected statistic model IDs.
        unfinished_progress (bool): Indicates if there is unfinished progress in the current project.
        current_page (str): The current page in the project workflow.
        save_checkpoint_models (bool): Indicates if checkpoint models should be saved.
        fine_tuning_step_counter (int): The current fine-tuning step counter.
        semantic_similarity_model (dict | None): The semantic similarity model configuration (optional).
        current_project (ProjectDTO | None): The current project details (optional).
        current_fine_tuning_model (ModelDTO | None): The current fine-tuning model details (optional).
        selected_model_for_fine_tuning (ComplexModelDTO | None): The selected model for fine-tuning (optional).
        currently_modified_dataset (ComplexDatasetDTO | None): The currently modified dataset details (optional).
    """

    id: int
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
    current_augmented_datapoint_evaluation_ids: list[int] = field(
        default_factory=list)
    current_augmentation_configurations: list[AugmentationConfiguration] = field(
        default_factory=list)
    generated_checkpoint_model_ids: list[int] = field(
        default_factory=list)
    selected_statistic_models: list[int] = field(
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


@dataclass
class ComplexModelEvaluationDTO:
    """
    Data transfer object for returning complex model evaluation details.

    Attributes:
        id (int): The unique identifier of the model evaluation.
        model_id (int): The ID of the model being evaluated.
        datapoint (DataPointDTO): The evaluated datapoint details.
        messages (MessagesContainer): The messages contained in the evaluation.
        semantic_similarity_score (float | None): The semantic similarity score of the evaluation (optional).
        evaluation_type (EvaluationType | None): The evaluation type (optional).
        helpful_score (int | None): The helpful score of the evaluation (optional).
        honest_score (int | None): The honest score of the evaluation (optional).
        harmless_score (int | None): The harmless score of the evaluation (optional).
        created_at (datetime): The creation date of the evaluation.
    """

    id: int
    model_id: int
    datapoint: DataPointDTO
    messages: MessagesContainer
    semantic_similarity_score: float | None = None
    evaluation_type: EvaluationType | None = None
    helpful_score: int | None = None
    honest_score: int | None = None
    harmless_score: int | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now().astimezone())
