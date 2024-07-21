"""Provides a common interface for DAO implementations.
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.backend.database.schema import Project, DataPoint, Dataset, Model, TrainingRun, ModelEvaluation
from app.backend.dtos.create_request import CreateDatasetDTO, CreateProjectDTO
from app.backend.dtos.get_request import GetProjectsDTO
from app.backend.dtos.update_request import UpdateDatasetDTO, UpdateProjectDTO


class IDataManager(ABC):
    pass
    # Implement additional methods as needed based on your DataManager class
