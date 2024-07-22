"""
This module contains data transfer objects (DTOs) used for create requests. 
These DTOs define the structure and types of data required for creating various entities in the application.
"""


from dataclasses import dataclass
from app.backend.database.schema import DatasetCategory, AugmentationType, EvaluationType, FineTuningCompany
from app.backend.custom_types.typedicts import AugmentationConfiguration, MessagesContainer


@dataclass
class CreateProjectDTO:
    """
    Data transfer object for creating a new project.

    Attributes:
        project_name (str): The name of the project.
        description (str | None): A brief description of the project (optional).
        model_ids (list[int] | None): List of model IDs associated with the project (optional).
        dataset_ids (list[int] | None): List of dataset IDs associated with the project (optional).
    """

    project_name: str
    description: str | None = None
    model_ids: list[int] | None = None
    dataset_ids: list[int] | None = None


@dataclass
class CreateDatasetDTO:
    """
    Data transfer object for creating a new dataset.

    Attributes:
        dataset_name (str): The name of the dataset.
        category (DatasetCategory): The category of the dataset (training or test).
        augmented (bool): Indicates if the dataset is augmented.
        fine_tuning_company (FineTuningCompany): The company for which the dataset is formatted.
        fine_tuning_model (str): The fine-tuning model this data is formatted for.
        fine_tuning_formatting (str): The formatting of the underlying fine-tuning data based on the company.
        project_ids (list[int] | None): List of project IDs associated with the dataset (optional).
        initial_dataset_ids (list[int] | None): List of initial dataset IDs (optional).
        test_dataset_id (int | None): ID of the test dataset associated with this dataset (optional).
        datapoint_ids (list[int] | None): List of datapoint IDs associated with the dataset (optional).
        is_global (bool): Indicates if the dataset is global.
    """

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
    """
    Data transfer object for creating a new datapoint.

    Attributes:
        messages (MessagesContainer): Container holding message data.
        dataset_id (int | None): ID of the dataset to which this datapoint belongs (optional).
        related_datapoint_ids (list[int] | None): List of related datapoint IDs (optional).
        augmentation_type (AugmentationType | None): The type of augmentation applied to the datapoint (optional).
        initial_datapoint_id (int | None): ID of the initial datapoint from which this one is augmented (optional).
    """

    messages: MessagesContainer
    dataset_id: int | None = None
    related_datapoint_ids: list[int] | None = None
    augmentation_type: AugmentationType | None = None
    initial_datapoint_id: int | None = None


@dataclass
class CreateModelDTO:
    """
    Data transfer object for creating a new model.

    Attributes:
        model_name (str): The name of the model.
        project_ids (list[int]): List of project IDs associated with the model.
        training_dataset_ids (list[int]): List of training dataset IDs associated with the model.
        augmentation_configurations (list[AugmentationConfiguration] | None): List of augmentation configurations (optional).
        semantic_similarity_model (str | None): The semantic similarity model used (optional).
        fine_tuning_job_id (str | None): ID of the fine-tuning job (optional).
        fine_tuning_checkpoint_job_id (str | None): ID of the fine-tuning checkpoint job (optional).
        fine_tuned_model_id (str | None): ID of the fine-tuned model (optional).
        parent_model_id (int | None): ID of the parent model (optional).
        training_run_id (int | None): ID of the training run (optional).
        is_global (bool): Indicates if the model is global.
        is_checkpoint_model (bool): Indicates if the model is a checkpoint model.
        checkpoint_step (int | None): The checkpoint step number (optional).
    """

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
    """
    Data transfer object for creating a new model evaluation.

    Attributes:
        model_id (int): ID of the model being evaluated.
        datapoint_id (int): ID of the datapoint being evaluated.
        messages (MessagesContainer): Container holding message data.
        semantic_similarity_score (float | None): The semantic similarity score (optional).
        evaluation_type (EvaluationType | None): The evaluation type (optional).
        helpful_score (int | None): The helpful score (optional).
        honest_score (int | None): The honest score (optional).
        harmless_score (int | None): The harmless score (optional).
    """

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
    """
    Data transfer object for creating a new training run.

    Attributes:
        model_id (int): ID of the model being trained.
        fine_tuning_model (str): The fine-tuning model used for the training run.
        epochs (int | None): The number of epochs for training (optional).
        learning_rate_multiplier (float | None): The learning rate multiplier (optional).
        batch_size (int | None): The batch size for training (optional).
        seed (int | None): The seed for random number generation (optional).
    """

    model_id: int
    fine_tuning_model: str
    epochs: int | None = None
    learning_rate_multiplier: float | None = None
    batch_size: int | None = None
    seed: int | None = None


@dataclass
class CreateDataPointEvaluationDTO:
    """
    Data transfer object for creating a new datapoint evaluation.

    Attributes:
        datapoint_id (int): ID of the datapoint being evaluated.
        model_id (int): ID of the model used for evaluation.
        semantic_similarity_score (float): The semantic similarity score between the initial and augmented datapoint.
        coherence_score (int | None): The coherence score (optional).
        relevance_score (int | None): The relevance score (optional).
    """

    datapoint_id: int
    model_id: int
    semantic_similarity_score: float
    coherence_score: int | None = None
    relevance_score: int | None = None
