"""Provides a common interface for DAO implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ...database.schema import Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun
from ...dtos.create_request import *
from ...dtos.get_request import *
from ...dtos.response import *


class IDataManager(ABC):

    @abstractmethod
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        pass

    @abstractmethod
    def save_projects(self, projects_data: list[CreateProjectDTO]) -> list[ProjectDTO]:
        """Saves or updates project data."""
        pass

    @abstractmethod
    def save_datasets(self, datasets_data: list[CreateDatasetDTO]) -> list[DatasetDTO]:
        """Saves or updates dataset data."""
        pass

    @abstractmethod
    def save_datapoints(self, datapoints_data: list[CreateDataPointDTO]) -> list[DataPointDTO]:
        """Saves or updates datapoint data."""
        pass

    @abstractmethod
    def save_models(self, models_data: list[CreateModelDTO]) -> list[ModelDTO]:
        """Saves or updates model data."""
        pass

    @abstractmethod
    def save_model_evaluations(self, evaluations_data: list[CreateModelEvaluationDTO]) -> list[ModelEvaluationDTO]:
        """Saves or updates model evaluation data."""
        pass

    @abstractmethod
    def save_training_runs(self, runs_data: list[CreateTrainingRunDTO]) -> list[TrainingRunDTO]:
        """Saves or updates training run data."""
        pass

    @abstractmethod
    def get_all_projects(self, project_data: GetProjectsDTO) -> list[ProjectDTO]:
        """Retrieves all projects filterable by name and creation date."""
        pass

    @abstractmethod
    def get_models_by_project_id(self, model_project_data: GetModelsByProjectIdDTO) -> list[ModelDTO]:
        """Retrieves all models associated with a project, filterable by name and version."""
        pass

    @abstractmethod
    def get_datasets_by_model_id(self, dataset_model_data: GetDatasetsByModelIdDTO) -> list[DatasetDTO]:
        """Retrieves all datasets associated with a model, filterable by dataset name, augmented, and dataset category."""
        pass

    @abstractmethod
    def get_datapoints_by_dataset_id(self, dataset_datapoints_data: GetDatapointsByDatasetIdDTO) -> list[DataPointDTO]:
        """Retrieves dataset specific datapoints, filterable by coherence score, relevance score, semantic similarity score, and augmentation type."""
        pass

    @abstractmethod
    def get_model_evaluations_by_model_id(self, model_id: int) -> list[ModelEvaluationDTO]:
        """Retrieves all model evaluations for a given model."""
        pass

    @abstractmethod
    def get_training_run_by_model_id(self, model_id: int) -> list[TrainingRunDTO]:
        """Retrieves the training run of a model."""
        pass

    @abstractmethod
    def get_model_by_id(self, model_id: int) -> list[ModelDTO]:
        pass

    @abstractmethod
    def get_dataset_by_id(self, dataset_id: int) -> list[DatasetDTO]:
        pass

    @abstractmethod
    def get_project_by_id(self, project_id: int) -> list[ProjectDTO]:
        pass

    @abstractmethod
    def get_training_run_by_id(self, training_run_id: int) -> list[TrainingRunDTO]:
        pass

    @abstractmethod
    def get_datapoint_by_id(self, datapoint_id: int) -> list[DataPointDTO]:
        pass

    @abstractmethod
    def get_model_evaluation_by_id(self, model_evlauation_id: int) -> list[DataPointDTO]:
        pass
    # Implement additional methods as needed based on your DataManager class
