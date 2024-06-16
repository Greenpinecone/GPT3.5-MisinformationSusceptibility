"""Encapsulates all the service classes functionalities in one class used in the service layer to avoid creating unnecessaryly much classes and interfaces until more extensive implementations are needed
"""


from app.backend.database.schema import Project, DataPoint, Dataset, Model, TrainingRun, DataPointEvaluation, CurrentProjectData
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
            google_translate_service = GoogleTranslateService()
        if openai_service is None:
            openai_service = OpenAIService()
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

    def create_dataset_with_datapoints(self, trainings_dataset_dto: CreateDatasetDTO, trainings_datapoint_dtos: list[CreateDataPointDTO], test_dataset_dto: CreateDatasetDTO, test_datapoint_dtos: list[CreateDataPointDTO]) -> ComplexDatasetDTO:
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

            return [self._mapper.map_dataset_to_complex_dto(session, trainings_dataset)]

    def get_dataset_by_id(self, id: int) -> list[DatasetDTO]:
        with self._data_manager.get_session() as session:
            dataset: Dataset = self._data_manager.get_dataset_by_id(
                session, id)[0]
            return [self._mapper.map_dataset_to_dto(session, dataset)]

    def create_models(self, create_model_dto: list[CreateModelDTO]) -> list[ModelDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_create_models(
                session, self._data_manager, create_model_dto)
            model: Model = self._data_manager.create_models(
                session, create_model_dto)[0]
            return [self._mapper.map_model_to_dto(session, model)]

    def update_datapoints(self, update_datapoint_dtos: list[UpdateDataPointDTO]) -> list[DataPointDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_update_datapoints(
                session, self._data_manager, update_datapoint_dtos)
            datapoints: list[DataPoint] = self._data_manager.update_datapoints(
                session, update_datapoint_dtos)
            return [self._mapper.map_datapoint_to_dto(session, datapoint) for datapoint in datapoints]

    def filter_simple_training_runs(self, training_run_data: GetTrainingRunsDTO) -> list[SimpleTrainingRunDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_get_training_runs(
                session, self._data_manager, training_run_data)
            training_runs: list[TrainingRun] = self._data_manager.get_all_training_runs(
                session, training_run_data)

            return [self._mapper.map_training_run_to_simple_dto(session, training_run) for training_run in training_runs]

    def get_or_create_current_project_data(self) -> list[CurrentProjectDataDTO]:
        with self._data_manager.get_session() as session:
            # TODO: Add validator
            current_project_data: CurrentProjectData = self._data_manager.get_or_create_current_project_data(session)[
                0]
            return [self._mapper.map_current_project_data_to_dto(session, current_project_data)]

    def update_current_project_data(self, current_project_data: UpdateCurrentProjectDataDTO) -> list[CurrentProjectDataDTO]:
        with self._data_manager.get_session() as session:
            # TODO: Add validator
            current_project_data: CurrentProjectData = self._data_manager.update_current_project_data(session, current_project_data)[
                0]
            return [self._mapper.map_current_project_data_to_dto(session, current_project_data)]

    def create_training_run_dtos(self, training_run_dtos: list[CreateTrainingRunDTO]) -> list[TrainingRunDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_create_training_runs(
                session, self._data_manager, training_run_dtos)
            training_runs: list[TrainingRunDTO] = self._data_manager.create_training_runs(
                session, training_run_dtos)

            return [self._mapper.map_training_run_to_dto(session, training_run) for training_run in training_runs]

    def update_training_run_dtos(self, training_run_dtos: list[UpdateTrainingRunDTO]) -> list[TrainingRunDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_update_training_runs(
                session, self._data_manager, training_run_dtos)
            training_runs: list[TrainingRunDTO] = self._data_manager.update_training_runs(
                session, training_run_dtos)

            return [self._mapper.map_training_run_to_dto(session, training_run) for training_run in training_runs]

    def create_datapoint_evaluations(self, create_datapoint_evaluations: list[CreateDataPointEvaluationDTO]) -> list[DataPointEvaluationDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_create_datapoint_evaluations(
                session, self._data_manager, create_datapoint_evaluations)
            datapoint_evaluations: list[DataPointEvaluation] = self._data_manager.create_datapoint_evaluations(
                session, create_datapoint_evaluations)

            return [self._mapper.map_datapoint_evaluation_to_dto(session, datapoint_evaluation) for datapoint_evaluation in datapoint_evaluations]

    def update_datapoint_evaluations(self, update_datapoint_evaluations: list[UpdateDataPointEvaluationDTO]) -> list[DataPointEvaluationDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_update_datapoint_evaluations(
                session, self._data_manager, update_datapoint_evaluations)
            datapoint_evaluations: list[DataPointEvaluation] = self._data_manager.update_datapoint_evaluations(
                session, update_datapoint_evaluations)

            return [self._mapper.map_datapoint_evaluation_to_dto(session, datapoint_evaluation) for datapoint_evaluation in datapoint_evaluations]

    def get_datapoint_evaluations(self, get_datapoint_evaluation: GetDataPointEvaluationsDTO) -> list[DataPointEvaluationDTO]:
        with self._data_manager.get_session() as session:
            self._validator.validate_get_datapoint_evaluation(
                session, self._data_manager, get_datapoint_evaluation)
            datapoint_evaluations: list[DataPointEvaluation] = self._data_manager.get_datapoint_evaluations(
                session, get_datapoint_evaluation)

            return [self._mapper.map_datapoint_evaluation_to_dto(session, datapoint_evaluation) for datapoint_evaluation in datapoint_evaluations]

    # TODO: Add validators
    def create_fine_tuning_run(self, model_id: int, training_run_dto: TrainingRunDTO) -> ModelDTO:
        with self._data_manager.get_session() as session:
            # Fetch the model entity
            model: Model = self._data_manager.get_model_by_id(session, model_id)[
                0]
            fine_tuning_job_id = self._openai_service.create_fine_tuning_run(
                model, training_run_dto)

            # Assign fine tuning job id to model
            model.full_fine_tuned_model_id = fine_tuning_job_id

            return [self._mapper.map_model_to_dto(session, model)]

    def get_current_fine_tuning_status(self, fine_tuning_job_id: str) -> tuple[None | float, str, dict]:
        current_training_progress, status, progress_message, hyperparameters = self._openai_service.get_fine_tuning_status(
            fine_tuning_job_id)
        return current_training_progress, status, progress_message, hyperparameters

    def cancel_fine_tuning_run(self, fine_tuning_job_id: str) -> None:
        # TODO: Add proper response obejct handling
        response = self._openai_service.cancel_fine_tuning_job(
            fine_tuning_job_id)

        return response

    def save_checkpoint_models(self, current_fine_tuning_model: ModelDTO, current_project_id: int) -> list[ModelDTO]:
        # Fetch checkpoint data
        checkpoints = self._openai_service.get_checkpoints(
            current_fine_tuning_model.full_fine_tuned_model_id)

        if not checkpoints:
            return

        new_model_dtos: list[CreateModelDTO] = []
        new_training_run_dtos = list[CreateTrainingRunDTO] = []

        for i, checkpoint in enumerate(checkpoints, 1):
            # Create a new model DTO for each checkpoint
            new_model_dto = CreateModelDTO(
                model_name=current_fine_tuning_model.model_name + f"""C {i}""",
                project_ids=[current_project_id],
                training_dataset_ids=current_fine_tuning_model.training_dataset_ids,
                full_fine_tuned_model_id=checkpoint['fine_tuning_job_id'],
                parent_model_id=current_fine_tuning_model.parent_model_id,
                is_global=current_fine_tuning_model.is_global,
                is_checkpoint_model=True,
                checkpoint_step=checkpoint['step_number']
            )

            # Fetch those data, copy the current training run, replace these values, save it with the new model.
            checkpoint["metrics"]  # [train_loss], [train_mean_token_accuracy]

            # Save the new model (assuming you have a method to save models)
            new_model_dtos.append(new_model_dto)

        saved_models = self._data_manager.create_models(new_model_dtos)

        return [self._mapper.map_model_to_dto(model_dto) for model_dto in saved_models]

    def get_training_dataset_datapoint_amount(self, dataset_ids: list[int]) -> int:
        with self._data_manager.get_session() as session:
            datasets: list[Dataset] = []
            for dataset_id in dataset_ids:
                datasets.append(
                    self._data_manager.get_dataset_by_id(session, dataset_id)[0])

            return self._openai_service.count_datapoints_in_dataset_list(datasets)
