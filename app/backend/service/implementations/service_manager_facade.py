"""Encapsulates all the service classes functionalities in one class used in the service layer to avoid creating unnecessaryly much classes and interfaces until more extensive implementations are needed
"""


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


class ServiceManagerFacade(IServiceManager):
    def __init__(self, data_manager: IDataManager, google_translate_service: GoogleTranslateService, openai_service: OpenAIService, data_augmenter: DataAugmenter, data_sampler: DataSampler, model_evaluator: ModelEvaluator, fine_tuner: FineTuner, validator: ValidatorFacade, mapper: MapperFacade):
        self.data_manager: IDataManager = data_manager
        self.google_translate_service: GoogleTranslateService = google_translate_service
        self.openai_service: OpenAIService = openai_service
        self.data_augmenter: DataAugmenter = data_augmenter
        self.data_sampler: DataSampler = data_sampler
        self.model_evaluator: ModelEvaluator = model_evaluator
        self.fine_tuner: FineTuner = fine_tuner
        self.logger: Logger = Logger(__name__)
        self.validator: ValidatorFacade = validator
        self.mapper: MapperFacade = mapper

    @classmethod
    def create_with_default_dependencies(cls):
        # Assuming Config is a singleton or doesn't need instantiation parameters
        config: Config = Config()

        data_manager: IDataManager = DataManager()
        google_translate_service: GoogleTranslateService = GoogleTranslateService(
            api_key=config.google_translate_api_key)
        openai_service: OpenAIService = OpenAIService(
            api_key=config.openai_api_key)
        data_augmenter: DataAugmenter = DataAugmenter()
        data_sampler: DataSampler = DataSampler()
        model_evaluator: ModelEvaluator = ModelEvaluator()
        fine_tuner: FineTuner = FineTuner()
        validator: ValidatorFacade = ValidatorFacade(data_manager)
        mapper: MapperFacade = MapperFacade()

        return cls(data_manager, google_translate_service, openai_service, data_augmenter, data_sampler, model_evaluator, fine_tuner, validator, mapper)

    # TODO: Implement service layer functions with request validation / convertion to DTOs through marshmallow and add them to interface
