"""Encapsulates all the service classes functionalities in one class used in the service layer to avoid creating unnecessaryly much classes and interfaces until more extensive implementations are needed
"""


from app.backend.database.schema import *
from app.frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from ...dtos.get_request import *
from ...dtos.response import *
from ...dtos.create_request import *
from ...dtos.update_request import *
from ..interfaces.i_service_manager import IServiceManager
from ...persistence.interfaces.i_data_manager import IDataManager
from ...persistence.implementations.data_manager import DataManager
from ..classes.api.google_translate_services import GoogleTranslateService
from ..classes.api.openai_services import OpenAIService
from ..classes.data_preprocessing.augmenter import DataAugmenter
from ..classes.data_preprocessing.sampler import DataSampler
from ..classes.model.evaluator import ModelEvaluator
from ..classes.model.fine_tuner import FineTuner
from ...util.config import Config
from ...util.logger import Logger
from ...mapper.implementations.mappers_facade import MapperFacade
from ..validators.implementations.validators_facade import ValidatorFacade

logger = Logger(__name__)


class ServiceManagerFacade(IServiceManager):

    def __init__(self, data_manager: IDataManager = None, google_translate_service: GoogleTranslateService = None,
                 openai_service: OpenAIService = None, data_augmenter: DataAugmenter = None,
                 data_sampler: DataSampler = None, model_evaluator: ModelEvaluator = None,
                 fine_tuner: FineTuner = None, validator: ValidatorFacade = None, mapper: MapperFacade = None, config: Config = None):

        if config is None:
            config = Config()
        if mapper is None:
            mapper = MapperFacade()
        if data_manager is None:
            data_manager = DataManager()
        if google_translate_service is None:
            google_translate_service = GoogleTranslateService(
                api_key=config.google_translate_api_key)
        if openai_service is None:
            openai_service = OpenAIService(api_key=config.openai_api_key)
        if data_augmenter is None:
            data_augmenter = DataAugmenter()
        if data_sampler is None:
            data_sampler = DataSampler()
        if model_evaluator is None:
            model_evaluator = ModelEvaluator()
        if fine_tuner is None:
            fine_tuner = FineTuner()
        if validator is None:
            validator = ValidatorFacade()

        self._data_manager = data_manager
        self._google_translate_service = google_translate_service
        self._openai_service = openai_service
        self._data_augmenter = data_augmenter
        self._data_sampler = data_sampler
        self._model_evaluator = model_evaluator
        self._fine_tuner = fine_tuner
        self._validator = validator
        self._mapper = mapper
    # TODO: Implement service layer functions with request validation / convertion to DTOs through marshmallow and add them to interface

    def filter_projects(self, projects_data: GetProjectsDTO) -> list[ProjectDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_get_all_projects(
                session, self._data_manager, projects_data)
            projects: list[Project] = self._data_manager.get_all_projects(
                session, projects_data)
            return [self._mapper.map_project_to_dto(session, project) for project in projects]

    def filter_models(self, model_data: GetModelsDTO) -> list[ModelDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_get_all_models(
                session, self._data_manager, model_data)
            models: list[Model] = self._data_manager.get_all_models(
                session, model_data)
            return [self._mapper.map_model_to_dto(session, model) for model in models]

    def filter_datasets(self, dataset_data: GetDatasetsDTO) -> list[DatasetDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_get_all_datasets(
                session, self._data_manager, dataset_data)
            datasets: list[Dataset] = self._data_manager.get_all_datasets(
                session, dataset_data)
            return [self._mapper.map_dataset_to_dto(session, dataset) for dataset in datasets]

    def create_projects(self, projects_data: list[CreateProjectDTO]) -> list[ProjectDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_create_projects(
                session, self._data_manager, projects_data)
            projects: list[Project] = self._data_manager.create_projects(
                session, projects_data)
            return [self._mapper.map_project_to_dto(session, project) for project in projects]

    def udpate_projects(self, projects_data: list[UpdateProjectDTO]) -> list[ProjectDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_update_projects(
                session, self._data_manager, projects_data)
            projects: list[Project] = self._data_manager.update_projects(
                session, projects_data)
            return [self._mapper.map_project_to_dto(session, project) for project in projects]

    def create_dataset_with_datapoints(self, trainings_dataset_dto: CreateDatasetDTO, trainings_datapoint_dtos: list[CreateDataPointDTO], test_dataset_dto: CreateDatasetDTO, test_datapoint_dtos: list[CreateDataPointDTO]) -> list[DatasetDTO]:
        with self._data_manager.get_session() as session:
            # Save test dataset first to then add it to the training dataset
            self._validator.validate_create_datasets(
                session, self._data_manager, [test_dataset_dto])
            test_dataset: list[Dataset] = self._data_manager.create_datasets(session, [test_dataset_dto])[
                0]

            # Save test dataset datapoints (are directly accessibly by the test dataset through ORM)
            for datapoint_dto in test_datapoint_dtos:
                datapoint_dto.dataset_id = test_dataset.id
            self._validator.validate_create_datapoints(
                session, self._data_manager, test_datapoint_dtos)
            test_datapoints: list[DataPoint] = self._data_manager.create_datapoints(
                session, test_datapoint_dtos)

            # Save trainings dataset with test dataset id set
            self._validator.validate_create_datasets(
                session, self._data_manager, [trainings_dataset_dto])
            trainings_dataset: Dataset = self._data_manager.create_datasets(session, [trainings_dataset_dto])[
                0]

            # Set test dataset for trainings dataset
            trainings_dataset.test_dataset = test_dataset

            # Save training datapoints
            for datapoint_dto in trainings_datapoint_dtos:
                datapoint_dto.dataset_id = trainings_dataset.id
            self._validator.validate_create_datapoints(
                session, self._data_manager, trainings_datapoint_dtos)
            trainings_datapoints: list[DataPoint] = self._data_manager.create_datapoints(
                session, trainings_datapoint_dtos)

            x = self._mapper.map_dataset_to_dto(session, trainings_dataset)
            return [self._mapper.map_dataset_to_dto(session, trainings_dataset)]
