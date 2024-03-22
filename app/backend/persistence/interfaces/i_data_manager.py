"""Provides a common interface for DAO implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ...database.schema import Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun


class IDataManager(ABC):

    @abstractmethod
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        pass

    @abstractmethod
    def save_projects(self, projects_data: List[Dict[str, Any]]) -> List[Project]:
        """Saves or updates project data."""
        pass

    @abstractmethod
    def save_datasets(self, datasets_data: List[Dict[str, Any]]) -> List[Dataset]:
        """Saves or updates dataset data."""
        pass

    @abstractmethod
    def save_datapoints(self, datapoints_data: List[Dict[str, Any]]) -> List[DataPoint]:
        """Saves or updates datapoint data."""
        pass

    @abstractmethod
    def save_models(self, models_data: List[Dict[str, Any]]) -> List[Model]:
        """Saves or updates model data."""
        pass

    @abstractmethod
    def save_model_evaluations(self, evaluations_data: List[Dict[str, Any]]) -> List[ModelEvaluation]:
        """Saves or updates model evaluation data."""
        pass

    @abstractmethod
    def save_training_runs(self, runs_data: List[Dict[str, Any]]) -> List[TrainingRun]:
        """Saves or updates training run data."""
        pass

    @abstractmethod
    def get_all_projects(self, project_data: Dict[str, Any]) -> List[Project]:
        """Retrieves all projects filterable by name and creation date."""
        pass

    @abstractmethod
    def get_models_by_project_id(self, model_project_data: Dict[str, Any]) -> List[Model]:
        """Retrieves all models associated with a project, filterable by name and version."""
        pass

    @abstractmethod
    def get_datasets_by_model_id(self, dataset_model_data: Dict[str, Any]) -> List[Dataset]:
        """Retrieves all datasets associated with a model, filterable by dataset name, augmented, and dataset category."""
        pass

    @abstractmethod
    def get_datapoints_by_dataset_id(self, dataset_datapoints_data: Dict[str, Any]) -> List[DataPoint]:
        """Retrieves dataset specific datapoints, filterable by coherence score, relevance score, semantic similarity score, and augmentation type."""
        pass

    @abstractmethod
    def get_model_evaluations_by_model_id(self, model_id: int) -> List[ModelEvaluation]:
        """Retrieves all model evaluations for a given model."""
        pass

    @abstractmethod
    def get_training_run_by_model_id(self, model_id: int) -> List[TrainingRun]:
        """Retrieves the training run of a model."""
        pass

    @abstractmethod
    def get_model_by_id(self, model_id: int) -> List[Model]:
        pass

    @abstractmethod
    def get_dataset_by_id(self, dataset_id: int) -> List[Dataset]:
        pass

    @abstractmethod
    def get_project_by_id(self, project_id: int) -> List[Project]:
        pass

    @abstractmethod
    def get_training_run_by_id(self, training_run_id: int) -> List[TrainingRun]:
        pass

    @abstractmethod
    def get_datapoint_by_id(self, datapoint_id: int) -> List[DataPoint]:
        pass
    # Implement additional methods as needed based on your DataManager class
