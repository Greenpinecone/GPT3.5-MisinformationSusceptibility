"""
Defines the IServiceManager interface for managing service-related operations.
This interface sets the ground functionality for various service managers,
ensuring a standardized approach to handling service logic and interactions.

Classes:
    IServiceManager: Interface for managing service operations.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session
from app.backend.custom_types.typedicts import AugmentationConfiguration, MessagesContainer
from app.backend.dtos.create_request import CreateDataPointDTO, CreateDataPointEvaluationDTO, CreateDatasetDTO, CreateModelDTO, CreateProjectDTO, CreateTrainingRunDTO
from app.backend.dtos.get_request import GetDataPointEvaluationsDTO, GetDatasetsDTO, GetModelEvalautionsDTO, GetModelsDTO, GetProjectsDTO, GetTrainingRunsDTO
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO, UpdateDataPointDTO, UpdateDataPointEvaluationDTO, UpdateModelDTO, UpdateModelEvaluationDTO, UpdateProjectDTO, UpdateTrainingRunDTO
from app.backend.dtos.response import ComplexDatasetDTO, ComplexModelDTO, ComplexModelEvaluationDTO, CurrentProjectDataDTO, DataPointDTO, DataPointEvaluationDTO, DatasetDTO, ModelDTO, ModelEvaluationDTO, ModelWithOriginalProjectDTO, ProjectDTO, SimpleProjectDTO, SimpleTrainingRunDTO, TrainingRunDTO


class IServiceManager(ABC):
    """
    Interface for managing service operations. Ensures a standardized approach
    to handling service logic and interactions.
    """

    @abstractmethod
    def filter_projects(self, projects_data: GetProjectsDTO, existing_session: Session | None = None) -> list[ProjectDTO]:
        """
        Filters projects based on the provided filtering criteria.

        Args:
            projects_data (GetProjectsDTO): Data transfer object containing filtering criteria for projects.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ProjectDTO]: A list of data transfer objects representing the filtered projects.
        """
        pass

    @abstractmethod
    def filter_models(self, model_data: GetModelsDTO, existing_session: Session | None = None) -> list[ModelDTO]:
        """
        Filters models based on the provided filtering criteria.

        Args:
            model_data (GetModelsDTO): Data transfer object containing filtering criteria for models.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ModelDTO]: A list of data transfer objects representing the filtered models.
        """
        pass

    @abstractmethod
    def filter_datasets(self, dataset_data: GetDatasetsDTO, existing_session: Session | None = None) -> list[DatasetDTO]:
        """
        Filters datasets based on the provided filtering criteria.

        Args:
            dataset_data (GetDatasetsDTO): Data transfer object containing filtering criteria for datasets.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[DatasetDTO]: A list of data transfer objects representing the filtered datasets.
        """
        pass

    @abstractmethod
    def create_projects(self, projects_data: list[CreateProjectDTO], existing_session: Session | None = None) -> list[ProjectDTO]:
        """
        Creates new projects based on the provided data.

        Args:
            projects_data (list[CreateProjectDTO]): list of data transfer objects containing project creation data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ProjectDTO]: A list of data transfer objects representing the created projects.
        """
        pass

    @abstractmethod
    def udpate_projects(self, projects_data: list[UpdateProjectDTO], existing_session: Session | None = None) -> list[ProjectDTO]:
        """
        Updates existing projects based on the provided data.

        Args:
            projects_data (list[UpdateProjectDTO]): list of data transfer objects containing project update data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ProjectDTO]: A list of data transfer objects representing the updated projects.
        """
        pass

    @abstractmethod
    def create_dataset_with_datapoints(self, trainings_dataset_dto: CreateDatasetDTO, trainings_datapoint_dtos: list[CreateDataPointDTO], test_dataset_dto: CreateDatasetDTO, test_datapoint_dtos: list[CreateDataPointDTO], existing_session: Session | None = None) -> ComplexDatasetDTO:
        """
        Creates a training and test dataset with their respective datapoints.

        Args:
            trainings_dataset_dto (CreateDatasetDTO): Data transfer object containing training dataset creation data.
            trainings_datapoint_dtos (list[CreateDataPointDTO]): list of data transfer objects containing training datapoint creation data.
            test_dataset_dto (CreateDatasetDTO): Data transfer object containing test dataset creation data.
            test_datapoint_dtos (list[CreateDataPointDTO]): list of data transfer objects containing test datapoint creation data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            ComplexDatasetDTO: A data transfer object representing the complex dataset.
        """
        pass

    @abstractmethod
    def get_dataset_by_id(self, id: int, existing_session: Session | None = None) -> list[DatasetDTO]:
        """
        Retrieves a dataset by its ID.

        Args:
            id (int): ID of the dataset.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[DatasetDTO]: A list containing the dataset data transfer object.
        """
        pass

    @abstractmethod
    def create_models(self, create_model_dto: list[CreateModelDTO], existing_session: Session | None = None) -> list[ModelDTO]:
        """
        Creates new models based on the provided data.

        Args:
            create_model_dto (list[CreateModelDTO]): list of data transfer objects containing model creation data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ModelDTO]: A list of data transfer objects representing the created models.
        """
        pass

    @abstractmethod
    def update_models(self, update_model_dtos: list[UpdateModelDTO], existing_session: Session | None = None) -> list[ModelDTO]:
        """
        Updates existing models based on the provided data.

        Args:
            update_model_dtos (list[UpdateModelDTO]): list of data transfer objects containing model update data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ModelDTO]: A list of data transfer objects representing the updated models.
        """
        pass

    @abstractmethod
    def delete_models(self, model_ids: list[int], existing_session: Session | None = None) -> None:
        """
        Deletes models based on the provided IDs.

        Args:
            model_ids (list[int]): list of model IDs to delete.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.
        """
        pass

    @abstractmethod
    def update_datapoints(self, update_datapoint_dtos: list[UpdateDataPointDTO], existing_session: Session | None = None) -> list[DataPointDTO]:
        """
        Updates existing datapoints based on the provided data.

        Args:
            update_datapoint_dtos (list[UpdateDataPointDTO]): list of data transfer objects containing datapoint update data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[DataPointDTO]: A list of data transfer objects representing the updated datapoints.
        """
        pass

    @abstractmethod
    def filter_simple_training_runs(self, training_run_data: GetTrainingRunsDTO, existing_session: Session | None = None) -> list[SimpleTrainingRunDTO]:
        """
        Filters simple training runs based on the provided filtering criteria.

        Args:
            training_run_data (GetTrainingRunsDTO): Data transfer object containing filtering criteria for training runs.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[SimpleTrainingRunDTO]: A list of data transfer objects representing the filtered training runs.
        """
        pass

    @abstractmethod
    def get_or_create_current_project_data(self, existing_session: Session | None = None) -> list[CurrentProjectDataDTO]:
        """
        Retrieves or creates the current project data.

        Args:
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[CurrentProjectDataDTO]: A list containing the current project data transfer object.
        """
        pass

    @abstractmethod
    def update_current_project_data(self, current_project_data: UpdateCurrentProjectDataDTO, existing_session: Session | None = None) -> list[CurrentProjectDataDTO]:
        """
        Updates the current project data based on the provided data.

        Args:
            current_project_data (UpdateCurrentProjectDataDTO): Data transfer object containing current project data update.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[CurrentProjectDataDTO]: A list of data transfer objects representing the updated current project data.
        """
        pass

    @abstractmethod
    def create_training_run_dtos(self, training_run_dtos: list[CreateTrainingRunDTO], existing_session: Session | None = None) -> list[TrainingRunDTO]:
        """
        Creates new training runs based on the provided data.

        Args:
            training_run_dtos (list[CreateTrainingRunDTO]): list of data transfer objects containing training run creation data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[TrainingRunDTO]: A list of data transfer objects representing the created training runs.
        """
        pass

    @abstractmethod
    def update_training_run_dtos(self, training_run_dtos: list[UpdateTrainingRunDTO], existing_session: Session | None = None) -> list[TrainingRunDTO]:
        """
        Updates existing training runs based on the provided data.

        Args:
            training_run_dtos (list[UpdateTrainingRunDTO]): list of data transfer objects containing training run update data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[TrainingRunDTO]: A list of data transfer objects representing the updated training runs.
        """
        pass

    @abstractmethod
    def create_datapoint_evaluations(self, create_datapoint_evaluations: list[CreateDataPointEvaluationDTO], existing_session: Session | None = None) -> list[DataPointEvaluationDTO]:
        """
        Creates new datapoint evaluations based on the provided data.

        Args:
            create_datapoint_evaluations (list[CreateDataPointEvaluationDTO]): list of data transfer objects containing datapoint evaluation creation data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[DataPointEvaluationDTO]: A list of data transfer objects representing the created datapoint evaluations.
        """
        pass

    @abstractmethod
    def update_datapoint_evaluations(self, update_datapoint_evaluations: list[UpdateDataPointEvaluationDTO], existing_session: Session | None = None) -> list[DataPointEvaluationDTO]:
        """
        Updates existing datapoint evaluations based on the provided data.

        Args:
            update_datapoint_evaluations (list[UpdateDataPointEvaluationDTO]): list of data transfer objects containing datapoint evaluation update data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[DataPointEvaluationDTO]: A list of data transfer objects representing the updated datapoint evaluations.
        """
        pass

    @abstractmethod
    def get_datapoint_evaluations(self, get_datapoint_evaluation: GetDataPointEvaluationsDTO, existing_session: Session | None = None) -> list[DataPointEvaluationDTO]:
        """
        Retrieves datapoint evaluations based on the provided criteria.

        Args:
            get_datapoint_evaluation (GetDataPointEvaluationsDTO): Data transfer object containing criteria for retrieving datapoint evaluations.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[DataPointEvaluationDTO]: A list of data transfer objects representing the retrieved datapoint evaluations.
        """
        pass

    @abstractmethod
    def create_fine_tuning_run(self, model_id: int, fine_tuning_model: str, existing_session: Session | None = None) -> ModelDTO:
        """
        Creates a fine-tuning run for a given model.

        Args:
            model_id (int): ID of the model to fine-tune.
            fine_tuning_model (str): The fine-tuning model identifier.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            ModelDTO: A data transfer object representing the fine-tuned model.
        """
        pass

    @abstractmethod
    def get_current_fine_tuning_status(self, fine_tuning_job_id: str) -> tuple[float | None, str, dict]:
        """
        Retrieves the current status of a fine-tuning job.

        Args:
            fine_tuning_job_id (str): ID of the fine-tuning job.

        Returns:
            tuple[Optional[float], str, dict]: A tuple containing the current training progress, status, and additional details.
        """
        pass

    @abstractmethod
    def cancel_fine_tuning_run(self, fine_tuning_job_id: str) -> None:
        """
        Cancels a fine-tuning run based on the provided job ID.

        Args:
            fine_tuning_job_id (str): ID of the fine-tuning job to cancel.
        """
        pass

    @abstractmethod
    def save_checkpoint_models(self, current_fine_tuning_model: ModelDTO, current_project_id: int, updated_training_run_dto: TrainingRunDTO, existing_session: Session | None = None) -> list[ModelDTO]:
        """
        Saves checkpoint models during a fine-tuning run.

        Args:
            current_fine_tuning_model (ModelDTO): Data transfer object representing the current fine-tuning model.
            current_project_id (int): ID of the current project.
            updated_training_run_dto (TrainingRunDTO): Data transfer object containing updated training run data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ModelDTO]: A list of data transfer objects representing the saved checkpoint models.
        """
        pass

    @abstractmethod
    def get_datasets_datapoints_count(self, dataset_ids: list[int], existing_session: Session | None = None) -> int:
        """
        Retrieves the count of datapoints in the specified datasets.

        Args:
            dataset_ids (list[int]): list of dataset IDs.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            int: The count of datapoints in the specified datasets.
        """
        pass

    @abstractmethod
    def get_training_run_by_id(self, training_run_id: int, existing_session: Session | None = None) -> list[TrainingRunDTO]:
        """
        Retrieves a training run by its ID.

        Args:
            training_run_id (int): ID of the training run.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[TrainingRunDTO]: A list containing the training run data transfer object.
        """
        pass

    @abstractmethod
    def get_total_augmentation_amount(self, datapoint_count: int, percentage: float) -> int:
        """
        Calculates the total amount of augmentation needed based on the provided datapoint count and percentage.

        Args:
            datapoint_count (int): The total count of datapoints.
            percentage (float): The percentage of augmentation required.

        Returns:
            int: The total amount of augmentation needed.
        """
        pass

    @abstractmethod
    def generate_augmented_data(self, model_id: int, augmentation_configurations: list[AugmentationConfiguration], current_project_id: int, semantic_similarity_model: dict | None = None, existing_session: Session | None = None) -> list[int]:
        """
        Generates augmented data for a given model based on the provided configurations.

        Args:
            model_id (int): ID of the model.
            augmentation_configurations (list[AugmentationConfiguration]): list of augmentation configurations.
            current_project_id (int): ID of the current project.
            semantic_similarity_model (Optional[dict], optional): Semantic similarity model configuration, if any. Defaults to None.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[int]: A list of IDs representing the generated augmented data.
        """
        pass

    @abstractmethod
    def calculate_datapoint_evaluation_scores(self, filter_data: GetDataPointEvaluationsDTO, existing_session: Session | None = None) -> tuple[tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], int]:
        """
        Calculates evaluation scores for datapoints based on the provided criteria.

        Args:
            filter_data (GetDataPointEvaluationsDTO): Data transfer object containing criteria for retrieving datapoint evaluations.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            tuple[tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], int]: A tuple containing evaluation scores and their respective counts and percentages.
        """
        pass

    @abstractmethod
    def calculate_model_evaluation_scores(self, filter_data: GetModelEvalautionsDTO, existing_session: Session | None = None) -> tuple[tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], list[dict[str, Any]], int]:
        """
        Calculates evaluation scores for models based on the provided criteria.

        Args:
            filter_data (GetModelEvalautionsDTO): Data transfer object containing criteria for retrieving model evaluations.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            tuple[tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], list[dict[str, Any]], int]: A tuple containing evaluation scores, their respective counts and percentages, and additional evaluation types.
        """
        pass

    @abstractmethod
    def generate_model_evaluation(self, model_id: int, test_datapoint_id: int, semantic_similarity_model: dict | None = None, existing_session: Session | None = None) -> list[int]:
        """
        Generates a model evaluation for a given model and test datapoint.

        Args:
            model_id (int): ID of the model.
            test_datapoint_id (int): ID of the test datapoint.
            semantic_similarity_model (Optional[dict], optional): Semantic similarity model configuration, if any. Defaults to None.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[int]: A list of IDs representing the generated model evaluation.
        """
        pass

    @abstractmethod
    def generate_model_chat(self, chat: MessagesContainer, model_id: str) -> str:
        """
        Generates a chat response based on the provided chat and model ID.

        Args:
            chat (MessagesContainer): Container holding the chat messages.
            model_id (str): ID of the model to generate the chat response.

        Returns:
            str: The generated chat response.
        """
        pass

    @abstractmethod
    def get_or_create_model_evaluation_by_id(self, model_id: int, test_datapoint_id: int, semantic_similarity_model: dict | None = None, existing_session: Session | None = None) -> list[ComplexModelEvaluationDTO]:
        """
        Retrieves or creates a model evaluation by its ID.

        Args:
            model_id (int): ID of the model.
            test_datapoint_id (int): ID of the test datapoint.
            semantic_similarity_model (Optional[dict], optional): Semantic similarity model configuration, if any. Defaults to None.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ComplexModelEvaluationDTO]: A list containing the complex model evaluation data transfer object.
        """
        pass

    @abstractmethod
    def get_all_test_datapoints(self, model_id: int, only_ids: bool, existing_session: Session | None = None) -> list[DataPointDTO | int]:
        """
        Retrieves all test datapoints for a given model.

        Args:
            model_id (int): ID of the model.
            only_ids (bool): If True, only the IDs of the datapoints are returned. If False, full datapoint DTOs are returned.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[Union[DataPointDTO, int]]: A list of datapoint IDs or data transfer objects representing the test datapoints.
        """
        pass

    @abstractmethod
    def get_all_training_datapoints(self, model_id: int, existing_session: Session | None = None) -> list[DataPointDTO]:
        """
        Retrieves all training datapoints for a given model.

        Args:
            model_id (int): ID of the model.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[DataPointDTO]: A list of data transfer objects representing the training datapoints.
        """
        pass

    @abstractmethod
    def delete_datasets(self, dataset_ids: list[int], existing_session: Session | None = None) -> None:
        """
        Deletes datasets based on the provided IDs.

        Args:
            dataset_ids (list[int]): list of dataset IDs to delete.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.
        """
        pass

    @abstractmethod
    def delete_model_evaluations_by_model_id(self, model_id: int, existing_session: Session | None = None) -> None:
        """
        Deletes model evaluations for a given model ID.

        Args:
            model_id (int): ID of the model.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.
        """
        pass

    @abstractmethod
    def update_model_evaluations(self, update_models_evalautions_data: list[UpdateModelEvaluationDTO], existing_session: Session | None = None) -> list[ModelEvaluationDTO]:
        """
        Updates existing model evaluations based on the provided data.

        Args:
            update_models_evalautions_data (list[UpdateModelEvaluationDTO]): list of data transfer objects containing model evaluation update data.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ModelEvaluationDTO]: A list of data transfer objects representing the updated model evaluations.
        """
        pass

    @abstractmethod
    def filter_models_with_original_project(self, model_data: GetModelsDTO, existing_session: Session | None = None) -> list[ModelWithOriginalProjectDTO]:
        """
        Filters models along with their original projects based on the provided filtering criteria.

        Args:
            model_data (GetModelsDTO): Data transfer object containing filtering criteria for models.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ModelWithOriginalProjectDTO]: A list of data transfer objects representing the filtered models along with their original projects.
        """
        pass

    @abstractmethod
    def filter_simple_projects(self, projects_data: GetProjectsDTO, existing_session: Session | None = None) -> list[SimpleProjectDTO]:
        """
        Filters simple project data based on the provided filtering criteria.

        Args:
            projects_data (GetProjectsDTO): Data transfer object containing filtering criteria for projects.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[SimpleProjectDTO]: A list of data transfer objects representing the filtered simple projects.
        """
        pass

    @abstractmethod
    def remove_model_global_status(self, model_id: int, existing_session: Session | None = None) -> None:
        """
        Removes the global status of a model based on the provided ID.

        Args:
            model_id (int): ID of the model.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.
        """
        pass

    @abstractmethod
    def delete_openai_checkpoint_models(self, original_fine_tuning_job_id: str) -> None:
        """
        Deletes checkpoint models for a given original fine-tuning job ID.

        Args:
            original_fine_tuning_job_id (str): ID of the original fine-tuning job.
        """
        pass

    @abstractmethod
    def get_fine_tuning_job_metrics(self, fine_tuning_job_id: str, step: int | None = None) -> dict[str, Any]:
        """
        Retrieves metrics for a given fine-tuning job.

        Args:
            fine_tuning_job_id (str): ID of the fine-tuning job.
            step (Optional[int], optional): Step number for which metrics are to be retrieved. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the metrics for the fine-tuning job.
        """
        pass

    @abstractmethod
    def get_model_by_id(self, model_id: int, existing_session: Session | None = None) -> list[ComplexModelDTO]:
        """
        Retrieves a model by its ID.

        Args:
            model_id (int): ID of the model.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[ComplexModelDTO]: A list containing the complex model data transfer object.
        """
        pass

    @abstractmethod
    def get_model_hierarchy_ids(self, model_id: int, existing_session: Session | None = None) -> list[int]:
        """
        Retrieves the hierarchy IDs of a model.

        Args:
            model_id (int): ID of the model.
            existing_session (Optional[Session], optional): An existing database session, if any. Defaults to None.

        Returns:
            list[int]: A list of hierarchy IDs for the model.
        """
        pass

    @abstractmethod
    def retrieve_training_data(self, file_id: str, as_jsonl: bool = True) -> bytes:
        """
        Retrieves training data for a given file ID.

        Args:
            file_id (str): ID of the file containing the training data.
            as_jsonl (bool, optional): Whether to retrieve the data as JSONL. Defaults to True.

        Returns:
            bytes: The retrieved training data.
        """
        pass

    @abstractmethod
    def check_model_availability(self, fine_tuning_model: str) -> bool:
        """
        Checks the availability of a fine-tuning model.

        Args:
            fine_tuning_model (str): The fine-tuning model identifier.

        Returns:
            bool: True if the model is available, False otherwise.
        """
        pass

    @abstractmethod
    def fetch_new_events(self, fine_tuning_job_id: str, limit: int = 20, last_event_id: str | None = None) -> tuple[list[object], str]:
        """
        Fetches new events for a fine-tuning job.

        Args:
            fine_tuning_job_id (str): ID of the fine-tuning job.
            limit (int, optional): The maximum number of events to fetch. Defaults to 20.
            last_event_id (Optional[str], optional): ID of the last event fetched. Defaults to None.

        Returns:
            tuple[list[object], str]: A tuple containing the list of new events and the ID of the last fetched event.
        """
        pass
