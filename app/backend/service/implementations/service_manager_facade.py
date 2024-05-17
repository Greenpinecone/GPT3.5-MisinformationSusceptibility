"""Encapsulates all the service classes functionalities in one class used in the service layer to avoid creating unnecessaryly much classes and interfaces until more extensive implementations are needed
"""


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
            data_manager = DataManager(mapper=mapper)
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
            validator = ValidatorFacade(data_manager=data_manager)

        self.data_manager = data_manager
        self.google_translate_service = google_translate_service
        self.openai_service = openai_service
        self.data_augmenter = data_augmenter
        self.data_sampler = data_sampler
        self.model_evaluator = model_evaluator
        self.fine_tuner = fine_tuner
        self.validator = validator
        self.mapper = mapper
    # TODO: Implement service layer functions with request validation / convertion to DTOs through marshmallow and add them to interface

    def filter_projects(self, projects_data: GetProjectsDTO) -> list[ProjectDTO]:
        self.validator.validate_get_all_projects(projects_data)
        return self.data_manager.get_all_projects(projects_data)

    def filter_models(self, model_data: GetModelsDTO) -> list[ModelDTO]:
        self.validator.validate_get_all_models(model_data)
        return self.data_manager.get_all_models(model_data)

    def filter_datasets(self, dataset_data: GetDatasetsDTO) -> list[DatasetDTO]:
        self.validator.validate_get_all_datasets(dataset_data)
        return self.data_manager.get_all_datasets(dataset_data)

    def create_projects(self, projects_data: list[CreateProjectDTO]) -> list[ProjectDTO]:
        self.validator.validate_create_projects(projects_data)
        return self.data_manager.create_projects(projects_data)

    def udpate_projects(self, projects_data: list[UpdateProjectDTO]) -> list[ProjectDTO]:
        self.validator.validate_update_projects(projects_data)
        return self.data_manager.update_projects(projects_data)

    def create_dataset(self, dataset_dto: CreateDatasetDTO, datapoint_dtos: list[CreateDataPointDTO]) -> DatasetDTO:
        pass
