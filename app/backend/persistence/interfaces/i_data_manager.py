"""Provides a common interface for DAO implementations.
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.backend.database.schema import *
from ...dtos.create_request import *
from ...dtos.get_request import *
from ...dtos.response import *
from ...dtos.update_request import *


class IDataManager(ABC):

    @abstractmethod
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        pass

    @abstractmethod
    def create_projects(self, session: Session, projects_data: list[CreateProjectDTO]) -> list[Project]:
        """Saves or updates project data."""
        pass

    @abstractmethod
    def update_projects(self, session: Session, projects_data: list[UpdateProjectDTO]) -> list[Project]:
        """Saves or updates project data."""
        pass

    @abstractmethod
    def create_datasets(self,  session: Session, datasets_data: list[CreateDatasetDTO]) -> list[Dataset]:
        """Saves or updates dataset data."""
        pass

    @abstractmethod
    def update_datasets(self, session: Session, datasets_data: list[UpdateDatasetDTO]) -> list[Dataset]:
        """Saves or updates dataset data."""
        pass

    @abstractmethod
    def create_datapoints(self, session: Session, datapoints_data: list[CreateDataPointDTO]) -> list[DataPoint]:
        """Saves or updates datapoint data."""
        pass

    @abstractmethod
    def update_datapoints(self, session: Session, datapoints_data: list[UpdateDataPointDTO]) -> list[DataPoint]:
        """Saves or updates datapoint data."""
        pass

    @abstractmethod
    def create_models(self, session: Session, models_data: list[CreateModelDTO]) -> list[Model]:
        """Saves or updates model data."""
        pass

    @abstractmethod
    def update_models(self, session: Session, models_data: list[UpdateModelDTO]) -> list[Model]:
        """Saves or updates model data."""
        pass

    @abstractmethod
    def create_model_evaluations(self, session: Session, evaluations_data: list[ModelEvaluation]) -> list[ModelEvaluationDTO]:
        """Saves or updates model evaluation data."""
        pass

    @abstractmethod
    def update_model_evaluations(self, session: Session, evaluations_data: list[ModelEvaluation]) -> list[ModelEvaluationDTO]:
        """Saves or updates model evaluation data."""
        pass

    @abstractmethod
    def create_training_runs(self, session: Session, runs_data: list[CreateTrainingRunDTO]) -> list[TrainingRun]:
        """Saves or updates training run data."""
        pass

    @abstractmethod
    def get_all_projects(self, session: Session, project_data: GetProjectsDTO) -> list[Project]:
        """Retrieves all projects filterable by name and creation date."""
        pass

    @abstractmethod
    def get_all_models(self, session: Session, model_data: GetModelsDTO) -> list[Model]:
        """Retrieve all models filterable by name, creation date, version, project and is global or not."""

    @abstractmethod
    def get_all_datasets(self, session: Session, dataset_data: GetDatasetsDTO) -> list[Dataset]:
        "Retrieve all datasets filterable by name, augmented, category, initial dataset, project, is global or not."
        pass

    @abstractmethod
    def get_models_by_project_id(self, session: Session, model_project_data: GetModelsByProjectIdDTO) -> list[Model]:
        """Retrieves all models associated with a project, filterable by name and version."""
        pass

    @abstractmethod
    def get_datasets_by_model_id(self, session: Session, dataset_model_data: GetDatasetsByModelIdDTO) -> list[Dataset]:
        """Retrieves all datasets associated with a model, filterable by dataset name, augmented, and dataset category."""
        pass

    @abstractmethod
    def get_datapoints_by_dataset_id(self, session: Session, dataset_datapoints_data: GetDatapointsByDatasetIdDTO) -> list[DataPoint]:
        """Retrieves dataset specific datapoints, filterable by coherence score, relevance score, semantic similarity score, and augmentation type."""
        pass

    @abstractmethod
    def get_model_evaluations_by_model_id(self, session: Session, model_id: int) -> list[Model]:
        """Retrieves all model evaluations for a given model."""
        pass

    @abstractmethod
    def get_training_run_by_model_id(self, session: Session, model_id: int) -> list[TrainingRun]:
        """Retrieves the training run of a model."""
        pass

    @abstractmethod
    def get_model_by_id(self, session: Session, model_id: int) -> list[Model]:
        pass

    @abstractmethod
    def get_dataset_by_id(self, session: Session, dataset_id: int) -> list[Dataset]:
        pass

    @abstractmethod
    def get_project_by_id(self, session: Session, project_id: int) -> list[Project]:
        pass

    @abstractmethod
    def get_training_run_by_id(self, session: Session, training_run_id: int) -> list[TrainingRun]:
        pass

    @abstractmethod
    def get_datapoint_by_id(self, session: Session, datapoint_id: int) -> list[DataPoint]:
        pass

    @abstractmethod
    def get_model_evaluation_by_id(self, session: Session, model_evlauation_id: int) -> list[DataPoint]:
        pass
    # Implement additional methods as needed based on your DataManager class
