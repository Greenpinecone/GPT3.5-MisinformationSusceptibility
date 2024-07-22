"""
Defines the IDataManager interface for managing data-related operations.
This interface establishes the required functionality for various data managers,
ensuring a consistent approach to handling data interactions and persistence.

Classes:
    IDataManager: Interface for managing data operations.
"""

from abc import ABC, abstractmethod
from typing import Generator
from sqlalchemy.orm import Session
from app.backend.database.schema import CurrentProjectData, DataPointEvaluation, Project, DataPoint, Dataset, Model, TrainingRun, ModelEvaluation
from app.backend.dtos.create_request import CreateDataPointDTO, CreateDataPointEvaluationDTO, CreateDatasetDTO, CreateModelDTO, CreateModelEvaluationDTO, CreateProjectDTO, CreateTrainingRunDTO
from app.backend.dtos.get_request import GetDataPointEvaluationsDTO, GetDatapointsByDatasetIdDTO, GetDatasetsByModelIdDTO, GetDatasetsDTO, GetModelEvalautionsDTO, GetModelsByProjectIdDTO, GetModelsDTO, GetProjectsDTO, GetTrainingRunsDTO
from app.backend.dtos.response import DataPointDTO, ProjectDTO
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO, UpdateDataPointDTO, UpdateDataPointEvaluationDTO, UpdateDatasetDTO, UpdateModelDTO, UpdateModelEvaluationDTO, UpdateProjectDTO, UpdateTrainingRunDTO


class IDataManager(ABC):
    """
    Interface for managing data operations. Ensures a consistent approach to
    handling data interactions and persistence.
    """

    @abstractmethod
    def __init__(self, dest_directory: str = 'database', db_filename: str = 'streamlit_app.db'):
        """Initialize the database connection and session.

        This method sets up the connection to the SQLite database, enables foreign key support,
        and initializes the session factory and scoped session for thread-local sessions.

        Args:
            dest_directory (str): The directory where the database file is located. Defaults to 'database'.
            db_filename (str): The name of the database file. Defaults to 'streamlit_app.db'.

        Raises:
            Exception: If foreign key support is not enabled.
        """
        pass

    @abstractmethod
    def check_sqlite_version(self):
        """Check and log the SQLite version.

        This method executes a SQL query to retrieve and log the SQLite version currently in use.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def check_foreign_keys_enabled(self) -> bool:
        """Check if foreign key support is enabled in the SQLite database.

        This method executes a SQL query to check if foreign key support is enabled in the SQLite database.

        Returns:
            bool: True if foreign key support is enabled, False otherwise.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_session(self, session: Session = None) -> Generator[Session, None, None]:
        """Context manager to provide a database session.

        This method provides a context manager for managing SQLAlchemy sessions. If an existing session
        is provided, it will be used; otherwise, a new session will be created. The session is committed
        if the operations are successful, otherwise it is rolled back.

        Args:
            session (Session, optional): An existing SQLAlchemy session. Defaults to None.

        Yields:
            Session: A SQLAlchemy session object.

        Raises:
            Exception: If there is an error during session commit or rollback.
        """
        pass

    @abstractmethod
    def get_or_create_current_project_data(self, session: Session) -> list[CurrentProjectData]:
        """Retrieve or create the current project data.

        This method retrieves the current project data from the database. If no such data exists,
        it creates a new entry.

        Args:
            session (Session): The SQLAlchemy session to use for the query.

        Returns:
            list[CurrentProjectData]: A list containing the current project data object.

        Raises:
            Exception: If more than one current project data entry is found.
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def update_current_project_data(self, session: Session, current_project_data: UpdateCurrentProjectDataDTO) -> list[CurrentProjectData]:
        """Update the current project data.

        This method updates the current project data based on the provided DTO.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            current_project_data (UpdateCurrentProjectDataDTO): The data transfer object containing the updated project data.

        Returns:
            list[CurrentProjectData]: A list containing the updated current project data object.

        Raises:
            ValueError: If the current project data ID is not found.
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def _get_unoriginal_project_models(self, session: Session, project_id: int) -> list[Model]:
        """Retrieve models not originally associated with the given project.

        This method retrieves all models that are not originally associated with the specified project.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            project_id (int): The ID of the project.

        Returns:
            list[Model]: A list of models not originally associated with the project.
        """
        pass

    @abstractmethod
    def _update_project_model_associations(self, session: Session, project: Project, project_dto: ProjectDTO):
        """Update project model associations.

        This method updates the associations between a project and its models based on the provided DTO.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            project (Project): The project entity to update.
            project_dto (ProjectDTO): The data transfer object containing the updated project data.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def _update_project_datasets(self, session: Session, project_dto: ProjectDTO):
        """Update project dataset associations.

        This method updates the associations between a project and its datasets based on the provided DTO.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            project_dto (ProjectDTO): The data transfer object containing the updated project data.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def update_projects(self, session: Session, projects_data: list[UpdateProjectDTO]) -> list[Project]:
        """Update multiple projects.

        This method updates multiple projects based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            projects_data (list[UpdateProjectDTO]): A list of data transfer objects containing the updated project data.

        Returns:
            list[Project]: A list of updated project entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def create_projects(self, session: Session, projects_data: list[CreateProjectDTO]) -> list[Project]:
        """Create new projects.

        This method creates new projects based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            projects_data (list[CreateProjectDTO]): A list of data transfer objects containing the new project data.

        Returns:
            list[Project]: A list of newly created project entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def update_datasets(self, session: Session, datasets_data: list[UpdateDatasetDTO]) -> list[Dataset]:
        """Update multiple datasets.

        This method updates multiple datasets based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            datasets_data (list[UpdateDatasetDTO]): A list of data transfer objects containing the updated dataset data.

        Returns:
            list[Dataset]: A list of updated dataset entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def _update_training_datasets(self, session: Session, dataset_dto: CreateDatasetDTO, dataset: Dataset):
        """Update training datasets.

        This method updates the relationships between a dataset and its training datasets based on the provided DTO.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            dataset_dto (CreateDatasetDTO): The data transfer object containing the new dataset data.
            dataset (Dataset): The dataset entity to update.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def create_datasets(self, session: Session, datasets_data: list[CreateDatasetDTO]) -> list[Dataset]:
        """Create new datasets.

        This method creates new datasets based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            datasets_data (list[CreateDatasetDTO]): A list of data transfer objects containing the new dataset data.

        Returns:
            list[Dataset]: A list of newly created dataset entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def update_datapoints(self, session: Session, datapoints_data: list[UpdateDataPointDTO]) -> list[DataPointDTO]:
        """Update multiple datapoints.

        This method updates multiple datapoints based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            datapoints_data (list[UpdateDataPointDTO]): A list of data transfer objects containing the updated datapoint data.

        Returns:
            list[DataPointDTO]: A list of updated datapoint entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def create_datapoints(self, session: Session, datapoints_data: list[CreateDataPointDTO]) -> list[DataPoint]:
        """Create new datapoints.

        This method creates new datapoints based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            datapoints_data (list[CreateDataPointDTO]): A list of data transfer objects containing the new datapoint data.

        Returns:
            list[DataPoint]: A list of newly created datapoint entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def create_models(self, session: Session, models_data: list[CreateModelDTO]) -> list[Model]:
        """Create new models.

        This method creates new models based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            models_data (list[CreateModelDTO]): A list of data transfer objects containing the new model data.

        Returns:
            list[Model]: A list of newly created model entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def check_if_model_name_exists_in_specific_project(self, session: Session, model_name: str, project_id: int) -> bool:
        """Check if a model name exists in a specific project.

        This method checks if a model with the given name exists in the specified project.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_name (str): The name of the model to check.
            project_id (int): The ID of the project to check in.

        Returns:
            bool: True if the model name exists in the project, False otherwise.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def check_if_dataset_name_exists_in_specific_project(self, session: Session, dataset_name: str, project_id: int) -> bool:
        """Check if a dataset name exists in a specific project.

        This method checks if a dataset with the given name exists in the specified project.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            dataset_name (str): The name of the dataset to check.
            project_id (int): The ID of the project to check in.

        Returns:
            bool: True if the dataset name exists in the project, False otherwise.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def delete_models(self, session: Session, model_ids: list[int]) -> None:
        """Delete models.

        This method deletes models with the specified IDs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_ids (list[int]): A list of IDs of the models to delete.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def delete_datasets(self, session: Session, dataset_ids: list[int]) -> None:
        """Delete datasets.

        This method deletes datasets with the specified IDs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            dataset_ids (list[int]): A list of IDs of the datasets to delete.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def _get_current_project_ids(self, session: Session, model_id: int):
        """Get current project IDs associated with a model.

        This method retrieves the IDs of projects currently associated with the specified model.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_id (int): The ID of the model.

        Returns:
            list[int]: A list of project IDs currently associated with the model.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def _determine_project_changes(self, current_project_ids: set[int], new_project_ids: set[int]):
        """Determine project changes.

        This method determines which projects need to be added or removed based on the current and new project IDs.

        Args:
            current_project_ids (set[int]): The set of current project IDs.
            new_project_ids (set[int]): The set of new project IDs.

        Returns:
            tuple: A tuple containing two sets: projects to add and projects to remove.
        """
        pass

    @abstractmethod
    def _update_project_associations(self, session: Session, model_id: int, new_project_ids: list[int]):
        """Update project associations for a model.

        This method updates the associations between a model and its projects based on the new project IDs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_id (int): The ID of the model.
            new_project_ids (list[int]): A list of new project IDs to associate with the model.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def update_models(self, session: Session, models_data: list[UpdateModelDTO]) -> list[Model]:
        """Update multiple models.

        This method updates multiple models based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            models_data (list[UpdateModelDTO]): A list of data transfer objects containing the updated model data.

        Returns:
            list[Model]: A list of updated model entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def create_model_evaluations(self, session: Session, evaluations_data: list[CreateModelEvaluationDTO]) -> list[ModelEvaluation]:
        """Create new model evaluations.

        This method creates new model evaluations based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            evaluations_data (list[CreateModelEvaluationDTO]): A list of data transfer objects containing the new model evaluation data.

        Returns:
            list[ModelEvaluation]: A list of newly created model evaluation entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def update_model_evaluations(self, session: Session, evaluations_data: list[UpdateModelEvaluationDTO]) -> list[ModelEvaluation]:
        """Update multiple model evaluations.

        This method updates multiple model evaluations based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            evaluations_data (list[UpdateModelEvaluationDTO]): A list of data transfer objects containing the updated model evaluation data.

        Returns:
            list[ModelEvaluation]: A list of updated model evaluation entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def create_training_runs(self, session: Session, runs_data: list[CreateTrainingRunDTO]) -> list[TrainingRun]:
        """Create new training runs.

        This method creates new training runs based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            runs_data (list[CreateTrainingRunDTO]): A list of data transfer objects containing the new training run data.

        Returns:
            list[TrainingRun]: A list of newly created training run entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_all_projects(self, session: Session, project_data: GetProjectsDTO) -> list[Project]:
        """Retrieve all projects.

        This method retrieves all projects based on the provided filter data.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            project_data (GetProjectsDTO): The data transfer object containing the filter data.

        Returns:
            list[Project]: A list of project entities that match the filter criteria.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_all_models(self, session: Session, model_data: GetModelsDTO) -> list[Model]:
        """Retrieve all models.

        This method retrieves all models based on the provided filter data.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_data (GetModelsDTO): The data transfer object containing the filter data.

        Returns:
            list[Model]: A list of model entities that match the filter criteria.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_all_models_with_original_project(self, session: Session, model_data: GetModelsDTO) -> list[tuple[Model, Project]]:
        """Retrieve all models with their original project.

        This method retrieves all models along with their original project based on the provided filter data.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_data (GetModelsDTO): The data transfer object containing the filter data.

        Returns:
            list[tuple[Model, Project]]: A list of tuples, each containing a model and its original project.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def remove_model_global_status(self, session: Session, model_id: int) -> Model:
        """Remove the global status of a model.

        This method removes the global status of the specified model and updates its associations.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_id (int): The ID of the model.

        Returns:
            Model: The updated model entity.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_original_project(self, session: Session, model_id: int) -> int:
        """Get the original project ID of a model.

        This method retrieves the original project ID associated with the specified model.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_id (int): The ID of the model.

        Returns:
            int: The ID of the original project.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def _get_current_project_associations(self, session: Session, model_id: int) -> list[Project]:
        """Get current project associations of a model.

        This method retrieves the current project associations of the specified model.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_id (int): The ID of the model.

        Returns:
            list[Project]: A list of projects currently associated with the model.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def _remove_non_original_associations(self, session: Session, model_id: int, original_project_id: int):
        """Remove non-original project associations.

        This method removes associations between a model and projects that are not its original project.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_id (int): The ID of the model.
            original_project_id (int): The ID of the original project.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def create_datapoint_evaluations(self, session: Session, evaluations_data: list[CreateDataPointEvaluationDTO]) -> list[DataPointEvaluation]:
        """Create new datapoint evaluations.

        This method creates new datapoint evaluations based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            evaluations_data (list[CreateDataPointEvaluationDTO]): A list of data transfer objects containing the new datapoint evaluation data.

        Returns:
            list[DataPointEvaluation]: A list of newly created datapoint evaluation entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def delete_model_evaluations(self, session: Session, model_eval_ids: list[int]) -> None:
        """Delete model evaluations.

        This method deletes model evaluations with the specified IDs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_eval_ids (list[int]): A list of IDs of the model evaluations to delete.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def update_datapoint_evaluations(self, session: Session, evaluations_data: list[UpdateDataPointEvaluationDTO]) -> list[DataPointEvaluation]:
        """Update multiple datapoint evaluations.

        This method updates multiple datapoint evaluations based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            evaluations_data (list[UpdateDataPointEvaluationDTO]): A list of data transfer objects containing the updated datapoint evaluation data.

        Returns:
            list[DataPointEvaluation]: A list of updated datapoint evaluation entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_all_datapoint_evaluations(self, session: Session, filter_data: GetDataPointEvaluationsDTO) -> list[DataPointEvaluation]:
        """Retrieve all datapoint evaluations.

        This method retrieves all datapoint evaluations based on the provided filter data.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            filter_data (GetDataPointEvaluationsDTO): The data transfer object containing the filter data.

        Returns:
            list[DataPointEvaluation]: A list of datapoint evaluation entities that match the filter criteria.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_all_model_evaluations(self, session: Session, filter_data: GetModelEvalautionsDTO) -> list[ModelEvaluation]:
        """Retrieve all model evaluations.

        This method retrieves all model evaluations based on the provided filter data.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            filter_data (GetModelEvalautionsDTO): The data transfer object containing the filter data.

        Returns:
            list[ModelEvaluation]: A list of model evaluation entities that match the filter criteria.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_all_datasets(self, session: Session, dataset_data: GetDatasetsDTO) -> list[Dataset]:
        """Retrieve all datasets.

        This method retrieves all datasets based on the provided filter data.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            dataset_data (GetDatasetsDTO): The data transfer object containing the filter data.

        Returns:
            list[Dataset]: A list of dataset entities that match the filter criteria.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_all_training_runs(self, session: Session, training_run_data: GetTrainingRunsDTO) -> list[TrainingRun]:
        """Retrieve all training runs.

        This method retrieves all training runs based on the provided filter data.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            training_run_data (GetTrainingRunsDTO): The data transfer object containing the filter data.

        Returns:
            list[TrainingRun]: A list of training run entities that match the filter criteria.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def update_training_runs(self, session: Session, update_training_run_dtos: list[UpdateTrainingRunDTO]) -> list[TrainingRun]:
        """Update multiple training runs.

        This method updates multiple training runs based on the provided list of DTOs.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            update_training_run_dtos (list[UpdateTrainingRunDTO]): A list of data transfer objects containing the updated training run data.

        Returns:
            list[TrainingRun]: A list of updated training run entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_models_by_project_id(self, session: Session, model_project_data: GetModelsByProjectIdDTO) -> list[Model]:
        """Retrieve models by project ID.

        This method retrieves all models associated with the specified project based on the provided filter data.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_project_data (GetModelsByProjectIdDTO): The data transfer object containing the filter data.

        Returns:
            list[Model]: A list of model entities associated with the project.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_datasets_by_model_id(self, session: Session, dataset_model_data: GetDatasetsByModelIdDTO) -> list[Dataset]:
        """Retrieve datasets by model ID.

        This method retrieves all datasets associated with the specified model based on the provided filter data.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            dataset_model_data (GetDatasetsByModelIdDTO): The data transfer object containing the filter data.

        Returns:
            list[Dataset]: A list of dataset entities associated with the model.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_datapoints_by_dataset_id(self, session: Session, dataset_datapoints_data: GetDatapointsByDatasetIdDTO) -> list[DataPointDTO]:
        """Retrieve datapoints by dataset ID.

        This method retrieves all datapoints associated with the specified dataset based on the provided filter data.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            dataset_datapoints_data (GetDatapointsByDatasetIdDTO): The data transfer object containing the filter data.

        Returns:
            list[DataPointDTO]: A list of datapoint entities associated with the dataset.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_model_hierarchy_ids(self, session: Session, model_id: int) -> list[int]:
        """Retrieve model hierarchy IDs.

        This method retrieves the hierarchy of model IDs, starting from the specified model and moving up the parent chain.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_id (int): The ID of the model.

        Returns:
            list[int]: A list of model IDs representing the hierarchy.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_model_evaluations_by_model_id(self, session: Session, model_id: int) -> list[ModelEvaluation]:
        """Retrieve model evaluations by model ID.

        This method retrieves all evaluations associated with the specified model.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_id (int): The ID of the model.

        Returns:
            list[ModelEvaluation]: A list of model evaluation entities.

        Raises:
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_training_run_by_model_id(self, session: Session, model_id: int) -> list[TrainingRun]:
        """Retrieve training run by model ID.

        This method retrieves the training run associated with the specified model.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_id (int): The ID of the model.

        Returns:
            list[TrainingRun]: A list containing the training run entity.

        Raises:
            MultipleResultsFound: If more than one training run is found for the model.
            NoResultFound: If no training run is found for the model.
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_model_by_id(self, session: Session, model_id: int) -> list[Model]:
        """Retrieve model by ID.

        This method retrieves the model with the specified ID.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_id (int): The ID of the model.

        Returns:
            list[Model]: A list containing the model entity.

        Raises:
            MultipleResultsFound: If more than one model is found with the specified ID.
            NoResultFound: If no model is found with the specified ID.
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_dataset_by_id(self, session: Session, dataset_id: int) -> list[Dataset]:
        """Retrieve dataset by ID.

        This method retrieves the dataset with the specified ID.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            dataset_id (int): The ID of the dataset.

        Returns:
            list[Dataset]: A list containing the dataset entity.

        Raises:
            MultipleResultsFound: If more than one dataset is found with the specified ID.
            NoResultFound: If no dataset is found with the specified ID.
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_project_by_id(self, session: Session, project_id: int) -> list[Project]:
        """Retrieve project by ID.

        This method retrieves the project with the specified ID.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            project_id (int): The ID of the project.

        Returns:
            list[Project]: A list containing the project entity.

        Raises:
            MultipleResultsFound: If more than one project is found with the specified ID.
            NoResultFound: If no project is found with the specified ID.
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_training_run_by_id(self, session: Session, training_run_id: int) -> list[TrainingRun]:
        """Retrieve training run by ID.

        This method retrieves the training run with the specified ID.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            training_run_id (int): The ID of the training run.

        Returns:
            list[TrainingRun]: A list containing the training run entity.

        Raises:
            MultipleResultsFound: If more than one training run is found with the specified ID.
            NoResultFound: If no training run is found with the specified ID.
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_datapoint_by_id(self, session: Session, datapoint_id: int) -> list[DataPoint]:
        """Retrieve datapoint by ID.

        This method retrieves the datapoint with the specified ID.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            datapoint_id (int): The ID of the datapoint.

        Returns:
            list[DataPoint]: A list containing the datapoint entity.

        Raises:
            MultipleResultsFound: If more than one datapoint is found with the specified ID.
            NoResultFound: If no datapoint is found with the specified ID.
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_model_evaluation_by_id(self, session: Session, model_evaluation_id: int) -> list[ModelEvaluation]:
        """Retrieve model evaluation by ID.

        This method retrieves the model evaluation with the specified ID.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            model_evaluation_id (int): The ID of the model evaluation.

        Returns:
            list[ModelEvaluation]: A list containing the model evaluation entity.

        Raises:
            MultipleResultsFound: If more than one model evaluation is found with the specified ID.
            NoResultFound: If no model evaluation is found with the specified ID.
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass

    @abstractmethod
    def get_datapoint_evaluation_by_id(self, session: Session, datapoint_evaluation_id: int) -> list[DataPointEvaluation]:
        """Retrieve datapoint evaluation by ID.

        This method retrieves the datapoint evaluation with the specified ID.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            datapoint_evaluation_id (int): The ID of the datapoint evaluation.

        Returns:
            list[DataPointEvaluation]: A list containing the datapoint evaluation entity.

        Raises:
            MultipleResultsFound: If more than one datapoint evaluation is found with the specified ID.
            NoResultFound: If no datapoint evaluation is found with the specified ID.
            SQLAlchemyError: If there is an error executing the SQL query.
        """
        pass
