"""Encapsulates all the service classes functionalities in one class used in the service layer to avoid creating unnecessaryly much classes and interfaces until more extensive implementations are needed
"""


import copy
from typing import Any
from app.backend.custom_types.typedicts import EDAParams, GoogleBTParams
from app.backend.database.schema import ModelEvaluation, Project, DataPoint, Dataset, Model, TrainingRun, DataPointEvaluation, CurrentProjectData
from app.backend.service.classes.evaluation.semantic_similarity_calculator import SemanticSimilarityCalculator
from ...dtos.get_request import *
from ...dtos.response import *
from ...dtos.create_request import *
from ...dtos.update_request import *
from ..interfaces.i_service_manager import IServiceManager
from ...persistence.interfaces.i_data_manager import IDataManager
from ...persistence.implementations.data_manager import DataManager
from ..classes.model.api.google_translate_services import GoogleTranslateService
from ..classes.model.api.openai_services import OpenAIService
from ..classes.data_augmentation.augmenters.augmenter import DataAugmenter
from ..classes.data_preprocessing.sampler import DataSampler
from ..classes.model.fine_tuner.fine_tuner import FineTuner
from ...util.config import Config
from ...util.logger import Logger
from ...mapper.implementations.mappers_facade import MapperFacade
from ..validators.implementations.validators_facade import ValidatorFacade
from sqlalchemy.orm import Session
from app.backend.util.config import SBERT_MODELS as semantic_similarity_models
from decimal import Decimal, ROUND_DOWN

logger = Logger(__name__)


class ServiceManagerFacade(IServiceManager):

    def __init__(self, data_manager: IDataManager = None, google_translate_service: GoogleTranslateService = None,
                 openai_service: OpenAIService = None, data_augmenter: DataAugmenter = None,
                 data_sampler: DataSampler = None,
                 fine_tuner: FineTuner = None, validator: ValidatorFacade = None, mapper: MapperFacade = None, config: Config = None, semantic_similarity_score_calculator: SemanticSimilarityCalculator = None):

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
        if fine_tuner is None:
            fine_tuner = FineTuner()
        if validator is None:
            validator = ValidatorFacade()
        if semantic_similarity_score_calculator is None:
            semantic_similarity_score_calculator = SemanticSimilarityCalculator()

        self._data_manager = data_manager
        self._google_translate_service = google_translate_service
        self._openai_service = openai_service
        self._data_augmenter = data_augmenter
        self._data_sampler = data_sampler
        self._fine_tuner = fine_tuner
        self._validator = validator
        self._mapper = mapper
        self._semantic_similarity_score_calculator = semantic_similarity_score_calculator

    # TODO: Add and reuse service layer functions (like get_by_id) instead of always calling the persistence layer directly. Issue with sessions in sessions thoughh, all service layer functions should be updated to potentially receive a session, and if so, use this session instead of create a new one.

    def filter_projects(self, projects_data: GetProjectsDTO, existing_session: Session | None = None) -> list[ProjectDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_get_all_projects(
                session, self._data_manager, projects_data)
            projects: list[Project] = self._data_manager.get_all_projects(
                session, projects_data)
            return [self._mapper.map_project_to_dto(session, project) for project in projects]

    def filter_models(self, model_data: GetModelsDTO, existing_session: Session | None = None) -> list[ModelDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_get_all_models(
                session, self._data_manager, model_data)
            models: list[Model] = self._data_manager.get_all_models(
                session, model_data)
            return [self._mapper.map_model_to_dto(session, model) for model in models]

    def filter_datasets(self, dataset_data: GetDatasetsDTO, existing_session: Session | None = None) -> list[DatasetDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_get_all_datasets(
                session, self._data_manager, dataset_data)
            datasets: list[Dataset] = self._data_manager.get_all_datasets(
                session, dataset_data)
            return [self._mapper.map_dataset_to_dto(session, dataset) for dataset in datasets]

    def create_projects(self, projects_data: list[CreateProjectDTO], existing_session: Session | None = None) -> list[ProjectDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_create_projects(
                session, self._data_manager, projects_data)
            projects: list[Project] = self._data_manager.create_projects(
                session, projects_data)
            return [self._mapper.map_project_to_dto(session, project) for project in projects]

    def udpate_projects(self, projects_data: list[UpdateProjectDTO], existing_session: Session | None = None) -> list[ProjectDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_update_projects(
                session, self._data_manager, projects_data)
            projects: list[Project] = self._data_manager.update_projects(
                session, projects_data)
            return [self._mapper.map_project_to_dto(session, project) for project in projects]

    def create_dataset_with_datapoints(self, trainings_dataset_dto: CreateDatasetDTO, trainings_datapoint_dtos: list[CreateDataPointDTO], test_dataset_dto: CreateDatasetDTO, test_datapoint_dtos: list[CreateDataPointDTO], existing_session: Session | None = None) -> ComplexDatasetDTO:
        with self._data_manager.get_session(existing_session) as session:
            # Save test dataset first to then add it to the training dataset
            test_dataset: Dataset = None
            if test_datapoint_dtos:
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

            # Set test dataset ids if exist
            trainings_dataset.test_dataset = test_dataset

            # Save training datapoints
            for datapoint_dto in trainings_datapoint_dtos:
                datapoint_dto.dataset_id = trainings_dataset.id
            self._validator.validate_create_datapoints(
                session, self._data_manager, trainings_datapoint_dtos)
            trainings_datapoints: list[DataPoint] = self._data_manager.create_datapoints(
                session, trainings_datapoint_dtos)

            return [self._mapper.map_dataset_to_complex_dto(session, trainings_dataset)]

    def get_dataset_by_id(self, id: int, existing_session: Session | None = None) -> list[DatasetDTO]:
        with self._data_manager.get_session(existing_session) as session:
            dataset: Dataset = self._data_manager.get_dataset_by_id(
                session, id)[0]
            return [self._mapper.map_dataset_to_dto(session, dataset)]

    def create_models(self, create_model_dto: list[CreateModelDTO], existing_session: Session | None = None) -> list[ModelDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_create_models(
                session, self._data_manager, create_model_dto)
            models: list[Model] = self._data_manager.create_models(
                session, create_model_dto)
            return [self._mapper.map_model_to_dto(session, model) for model in models]

    def update_models(self, update_model_dtos: list[UpdateModelDTO], existing_session: Session | None = None) -> list[ModelDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_update_models(
                session, self._data_manager, update_model_dtos)
            models: list[Model] = self._data_manager.update_models(
                session, update_model_dtos)
            return [self._mapper.map_model_to_dto(session, model) for model in models]

    def delete_models(self, model_ids: list[int], existing_session: Session | None = None) -> None:
        with self._data_manager.get_session(existing_session) as session:
            self._data_manager.delete_models(session, model_ids)
            return

    def update_datapoints(self, update_datapoint_dtos: list[UpdateDataPointDTO], existing_session: Session | None = None) -> list[DataPointDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_update_datapoints(
                session, self._data_manager, update_datapoint_dtos)
            datapoints: list[DataPoint] = self._data_manager.update_datapoints(
                session, update_datapoint_dtos)
            return [self._mapper.map_datapoint_to_dto(session, datapoint) for datapoint in datapoints]

    def filter_simple_training_runs(self, training_run_data: GetTrainingRunsDTO, existing_session: Session | None = None) -> list[SimpleTrainingRunDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_get_training_runs(
                session, self._data_manager, training_run_data)
            training_runs: list[TrainingRun] = self._data_manager.get_all_training_runs(
                session, training_run_data)

            return [self._mapper.map_training_run_to_simple_dto(session, training_run) for training_run in training_runs]

    def get_or_create_current_project_data(self, existing_session: Session | None = None) -> list[CurrentProjectDataDTO]:
        with self._data_manager.get_session(existing_session) as session:
            # TODO: Add validator
            current_project_data: CurrentProjectData = self._data_manager.get_or_create_current_project_data(session)[
                0]
            return [self._mapper.map_current_project_data_to_dto(session, current_project_data)]

    def update_current_project_data(self, current_project_data: UpdateCurrentProjectDataDTO, existing_session: Session | None = None) -> list[CurrentProjectDataDTO]:
        with self._data_manager.get_session(existing_session) as session:
            # TODO: Add validator
            current_project_data: CurrentProjectData = self._data_manager.update_current_project_data(session, current_project_data)[
                0]
            return [self._mapper.map_current_project_data_to_dto(session, current_project_data)]

    def create_training_run_dtos(self, training_run_dtos: list[CreateTrainingRunDTO], existing_session: Session | None = None) -> list[TrainingRunDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_create_training_runs(
                session, self._data_manager, training_run_dtos)
            training_runs: list[TrainingRunDTO] = self._data_manager.create_training_runs(
                session, training_run_dtos)

            return [self._mapper.map_training_run_to_dto(session, training_run) for training_run in training_runs]

    def update_training_run_dtos(self, training_run_dtos: list[UpdateTrainingRunDTO], existing_session: Session | None = None) -> list[TrainingRunDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_update_training_runs(
                session, self._data_manager, training_run_dtos)
            training_runs: list[TrainingRunDTO] = self._data_manager.update_training_runs(
                session, training_run_dtos)

            return [self._mapper.map_training_run_to_dto(session, training_run) for training_run in training_runs]

    def create_datapoint_evaluations(self, create_datapoint_evaluations: list[CreateDataPointEvaluationDTO], existing_session: Session | None = None) -> list[DataPointEvaluationDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_create_datapoint_evaluations(
                session, self._data_manager, create_datapoint_evaluations)
            datapoint_evaluations: list[DataPointEvaluation] = self._data_manager.create_datapoint_evaluations(
                session, create_datapoint_evaluations)

            return [self._mapper.map_datapoint_evaluation_to_dto(session, datapoint_evaluation) for datapoint_evaluation in datapoint_evaluations]

    def update_datapoint_evaluations(self, update_datapoint_evaluations: list[UpdateDataPointEvaluationDTO], existing_session: Session | None = None) -> list[DataPointEvaluationDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_update_datapoint_evaluations(
                session, self._data_manager, update_datapoint_evaluations)
            datapoint_evaluations: list[DataPointEvaluation] = self._data_manager.update_datapoint_evaluations(
                session, update_datapoint_evaluations)

            return [self._mapper.map_datapoint_evaluation_to_dto(session, datapoint_evaluation) for datapoint_evaluation in datapoint_evaluations]

    def get_datapoint_evaluations(self, get_datapoint_evaluation: GetDataPointEvaluationsDTO, existing_session: Session | None = None) -> list[DataPointEvaluationDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_get_datapoint_evaluation(
                session, self._data_manager, get_datapoint_evaluation)
            datapoint_evaluations: list[DataPointEvaluation] = self._data_manager.get_all_datapoint_evaluations(
                session, get_datapoint_evaluation)

            return [self._mapper.map_datapoint_evaluation_to_dto(session, datapoint_evaluation) for datapoint_evaluation in datapoint_evaluations]

    # TODO: Add validators
    def create_fine_tuning_run(self, model_id: int, fine_tuning_model: str, existing_session: Session | None = None) -> ModelDTO:
        with self._data_manager.get_session(existing_session) as session:
            # Fetch the model entity
            model: Model = self._data_manager.get_model_by_id(session, model_id)[
                0]

            complex_model_dto: ComplexModelDTO = self._mapper.map_model_to_complex_dto(
                session, model)

            model_datasets: list[Dataset] = self._data_manager.get_datasets_by_model_id(
                session, GetDatasetsByModelIdDTO(model_id=model_id))

            model_dataset_dtos: list[ComplexDatasetDTO] = [self._mapper.map_dataset_to_complex_dto(
                session, model_dataset) for model_dataset in model_datasets]

            fine_tuning_job_id = self._fine_tuner.create_fine_tuning_run(
                complex_model_dto, model_dataset_dtos, fine_tuning_model)

            # Assign fine tuning job id to model
            model.fine_tuning_job_id = fine_tuning_job_id

            return [self._mapper.map_model_to_dto(session, model)]

    def get_current_fine_tuning_status(self, fine_tuning_job_id: str) -> tuple[None | float, str, dict]:
        current_training_progress, status, progress_message, hyperparameters, seed, fine_tuned_model_id = self._openai_service.get_fine_tuning_status(
            fine_tuning_job_id)
        return current_training_progress, status, progress_message, hyperparameters, seed, fine_tuned_model_id

    def cancel_fine_tuning_run(self, fine_tuning_job_id: str) -> None:
        # TODO: Add proper response obejct handling
        response = self._openai_service.cancel_fine_tuning_job(
            fine_tuning_job_id)

        # TODO: Check this
        # Special case where this function is called when the model has been deleted which returns a "DeleteObject" that has no attribute "status"
        if response and getattr(response, 'deleted', None) is True:
            return "deleted"
        elif response and getattr(response, 'deleted', None) is False:
            "An error occured during model deletion"
        elif response and getattr(response, 'status', None):
            return response.status

    def save_checkpoint_models(self, current_fine_tuning_model: ModelDTO, current_project_id: int, updated_training_run_dto: TrainingRunDTO, existing_session: Session | None = None) -> list[ModelDTO]:
        with self._data_manager.get_session(existing_session) as session:
            # Fetch checkpoint data
            checkpoints: list = self._openai_service.get_checkpoints(
                current_fine_tuning_model.fine_tuning_job_id)

            if not checkpoints:
                return []

            # Sort checkpoints by step count
            checkpoints.sort(key=lambda x: x["step_number"])

            model_name: str = current_fine_tuning_model.model_name

            first_slash_position = model_name.find('/')

            # Extract the part after the first "/"
            model_name_without_project_or_suffix = model_name[first_slash_position + 1:]

            new_models: list[Model] = []

            for i, checkpoint in enumerate(checkpoints, 1):
                # Create a new model DTO for each checkpoint
                new_model_dto = CreateModelDTO(
                    model_name=f"{model_name_without_project_or_suffix}-C{i}",
                    project_ids=[current_project_id],
                    training_dataset_ids=current_fine_tuning_model.training_dataset_ids,
                    fine_tuning_job_id=checkpoint['fine_tuning_job_id'],
                    fine_tuning_checkpoint_job_id=checkpoint['id'],
                    fine_tuned_model_id=checkpoint['fine_tuned_model_checkpoint'],
                    parent_model_id=current_fine_tuning_model.parent_model_id,
                    semantic_similarity_model=current_fine_tuning_model.semantic_similarity_model,
                    augmentation_configurations=current_fine_tuning_model.augmentation_configurations,
                    is_global=current_fine_tuning_model.is_global,
                    is_checkpoint_model=True,
                    checkpoint_step=checkpoint['step_number']
                )

                # Save the model
                saved_model: Model = self._data_manager.create_models(
                    session, [new_model_dto])[0]

                # Create a new training run for the model that copies all the values of the initial fine tuning job. (A separate instance is easier to implement and might have some benefits in the future at the cost of another similar entity for each cehkpoint model)
                self._data_manager.create_training_runs(session, [CreateTrainingRunDTO(model_id=saved_model.id, fine_tuning_model=updated_training_run_dto.fine_tuning_model, epochs=updated_training_run_dto.epochs,
                                                                                       learning_rate_multiplier=updated_training_run_dto.learning_rate_multiplier, batch_size=updated_training_run_dto.batch_size, seed=updated_training_run_dto.seed)])[0]

                new_models.append(saved_model)

            return [self._mapper.map_model_to_dto(session, model) for model in new_models]

    def get_datasets_datapoints_count(self, dataset_ids: list[int], existing_session: Session | None = None) -> int:
        with self._data_manager.get_session(existing_session) as session:
            datasets: list[Dataset] = []
            for dataset_id in dataset_ids:
                datasets.append(
                    self._data_manager.get_dataset_by_id(session, dataset_id)[0])

            return self._openai_service.count_datapoints_in_dataset_list(datasets)

    def get_training_run_by_id(self, training_run_id: int, existing_session: Session | None = None) -> list[TrainingRunDTO]:
        with self._data_manager.get_session(existing_session) as session:
            training_runs: list[int] = self._data_manager.get_training_run_by_id(session,
                                                                                 training_run_id)

            return [self._mapper.map_training_run_to_dto(session, training_run) for training_run in training_runs]

    def get_total_augmentation_amount(self, datapoint_count: int, percentage: float) -> int:
        augmentation_count, _ = self._data_sampler.get_augmentation_count(
            datapoint_count, percentage)

        return augmentation_count

    def generate_augmented_data(self, model_id: int, augmentation_configurations: list[AugmentationConfiguration], current_project_id: int, semantic_similarity_model: dict | None = None, existing_session: Session | None = None) -> list[int]:
        with self._data_manager.get_session(existing_session) as session:

            # TODO: Add validation
            # Get the model that been created based on the selected model for fine tuning
            model: Model = self._data_manager.get_model_by_id(
                session, model_id)[0]

            # Set augmentation configurations
            model.augmentation_configurations = augmentation_configurations

            if semantic_similarity_model:
                # Add semantic similarity model
                model.semantic_similarity_model = semantic_similarity_model["model_name"]

            total_training_datapoints: list[DataPoint] = []

            # Get all training datapoints
            for dataset in model.training_datasets:
                total_training_datapoints.extend(dataset.datapoints)

            # Get all training datapoints with their related test datapoints
            total_training_datapoint_dtos: list[DataPointDTO] = [self._mapper.map_datapoint_to_training_datapoint_dto(
                session, datapoint) for datapoint in total_training_datapoints]

            # Get all augmented datapoints - set the augmented message and the original datapoint id
            augmented_datapoint_dtos: list[CreateDataPointDTO] = self._data_augmenter.create_augmented_datapoints(
                total_training_datapoint_dtos, augmentation_configurations)

            # Get the first training dataset, since it is always an unaugmented dataset and the augmented datasets rely on this information
            first_training_dataset: Dataset = sorted(
                model.training_datasets, key=lambda x: x.id)[0]

            # Split the string at the first "/" to get the name + unique identifier
            right_part = first_training_dataset.dataset_name.split("/", 1)[1]

            # to get the name without unique identifier
            left_part = right_part.rsplit("/", 1)[0]

            # # Create dataset DTO
            create_dataset_dto: CreateDatasetDTO = CreateDatasetDTO(
                dataset_name=f"{left_part}-A{model.version}", category=DatasetCategory.training, augmented=True, fine_tuning_company=first_training_dataset.fine_tuning_company, fine_tuning_model=first_training_dataset.fine_tuning_model, fine_tuning_formatting=first_training_dataset.fine_tuning_formatting, project_ids=[current_project_id], initial_dataset_ids=[dataset.id for dataset in model.training_datasets], test_dataset_id=first_training_dataset.test_dataset_id)

            # Create augmented dataset
            augmented_dataset: Dataset = self._data_manager.create_datasets(
                session, [create_dataset_dto])[0]

            # Add new augmented dataset to current fine tuning model so that the dataset is included for the fine tuning process
            model.training_datasets.append(augmented_dataset)

            # Save the datapoint evaluation dtos
            datapoint_evaluation_dtos: list[DataPointEvaluationDTO] = []

            # Iterate over augmented_datapoints, add dataset_id and create tuples to append to the list
            for augmented_datapoint_dto in augmented_datapoint_dtos:
                augmented_datapoint_dto.dataset_id = augmented_dataset.id
                datapoint_evaluation_dto: CreateDataPointEvaluationDTO = CreateDataPointEvaluationDTO(
                    datapoint_id=-1, model_id=model.id, semantic_similarity_score=0.0)
                datapoint_evaluation_dtos.append(datapoint_evaluation_dto)

            # Add semantic similarity score if a model has been chosen
            if semantic_similarity_model:
                datapoint_evaluation_dtos = self._semantic_similarity_score_calculator.calculate_datapoints_semantic_similarity_score(
                    total_training_datapoint_dtos, augmented_datapoint_dtos, datapoint_evaluation_dtos, semantic_similarity_model)

            # Save augmented datapoints
            augmented_datapoints: list[DataPoint] = self._data_manager.create_datapoints(
                session, augmented_datapoint_dtos)

            # Get the first test dataset since all datasets of the model have the same test dataset
            first_test_datapoints: list[DataPoint] = first_training_dataset.test_dataset.datapoints

            # Add the new augmented training datapoints to the test datapoints that are related to the original training datapoints from which the datapoints are augmented from.
            # TODO: Check if this correctly adds the new augmented training datapoint to the test datpoint relations
            self._add_test_datapoints_to_augmented_datapoint_relations(
                first_test_datapoints, augmented_datapoints, session)

            # Set the datapoint ids for the datapoint evaluations
            for datapoint, datapoint_evaluation in zip(augmented_datapoints, datapoint_evaluation_dtos):
                datapoint_evaluation.datapoint_id = datapoint.id

            # Create the datapoint evaluations
            datapoint_evaluations: list[DataPointEvaluation] = self._data_manager.create_datapoint_evaluations(
                session, datapoint_evaluation_dtos)

            # Return a list of evaluation ids which can be used on demand to fetch complex evaluation dtos for the initial and augmented datapoint and the augmented datapoints evaluation
            return [evaluation.id for evaluation in datapoint_evaluations]

    # INFO: For augmented datasets, related test datapoint are added to each augmented datapoint "related_datapoints" list to avoid mixing augmented datapoint with the original test / training datapoint relations. This would cause great issues with the cucrent versioning, since later models or verctically versioned models would work with the changed test datapoint relations whenever they are trained. By saving the related test datapoints in the augmented test datpoints "related_datapoints" list, we can separate the augmented datapoint relations from the original datapoint relations and still share the original test dataset, but each augmented dataset has its own test datapoint relations that later then need to be matched up on fetching by getting all augmented datasets from previous model version and the combine them with the original dataset to return a full list of test datapoints and their related original and augmented datapoint over multiple models.
    def _add_test_datapoints_to_augmented_datapoint_relations(self, test_datapoints: list[DataPoint], augmented_datapoints: list[DataPoint], existing_session: Session):
        # Pre-fetch all related datapoints
        training_to_test_map: dict[int, list[DataPoint]] = self._create_test_to_trainings_datapoints_mapping(
            test_datapoints
        )

        for augmented_dp in augmented_datapoints:
            # Get the initial training datapoint ID
            initial_training_id: int = augmented_dp.initial_datapoint_id

            # Find and associate the augmented datapoint with related test datapoints
            if initial_training_id in training_to_test_map:
                related_test_dps: list[DataPoint] = training_to_test_map[initial_training_id]
                for test_dp in related_test_dps:
                    augmented_dp.related_datapoints.append(test_dp)

            # Add the augmented datapoint
            existing_session.add(augmented_dp)

    def _create_test_to_trainings_datapoints_mapping(self, test_datapoints: list[DataPoint]) -> dict[int, list[DataPoint]]:
        # Create a dictionary to map training datapoints to their related test datapoints
        training_to_test_map: dict[int, list[DataPoint]] = {}
        for test_dp in test_datapoints:
            for related_dp in test_dp.related_datapoints:
                if related_dp.id not in training_to_test_map:
                    training_to_test_map[related_dp.id] = []
                training_to_test_map[related_dp.id].append(test_dp)

        return training_to_test_map

    def update_datapoint_evaluations(self, evaluations_data: list[UpdateDataPointEvaluationDTO], existing_session: Session | None = None):
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_update_datapoint_evaluations(
                session, self._data_manager, evaluations_data)
            updated_evaluations: list[DataPointEvaluation] = self._data_manager.update_datapoint_evaluations(
                session, evaluations_data)

            return [self._mapper.map_datapoint_evaluation_to_complex_dto(session, evaluation) for evaluation in updated_evaluations]

    def get_complex_datapoint_evaluation_by_id(self, data_point_evalaution_id: int, existing_session: Session | None = None) -> list[DataPointEvaluation]:
        with self._data_manager.get_session(existing_session) as session:

            datapoint_evalaution: DataPoint = self._data_manager.get_datapoint_evaluation_by_id(
                session, data_point_evalaution_id)[0]

            return [self._mapper.map_datapoint_evaluation_to_complex_dto(session, datapoint_evalaution)]

    def calculate_datapoint_evaluation_scores(self, filter_data: GetDataPointEvaluationsDTO, existing_session: Session | None = None) -> tuple[tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], int]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_get_datapoint_evaluation(
                session, self._data_manager, filter_data)
            datapoint_evaluations: list[DataPointEvaluation] = self._data_manager.get_all_datapoint_evaluations(
                session, filter_data)

            coherence_scores: list[int] = []
            relevance_scores: list[int] = []
            semantic_similarity_scores: list[int] = []

            # Counters for the number of evaluations that have each score set
            coherence_count = 0
            relevance_count = 0
            semantic_similarity_count = 0
            total_count = len(datapoint_evaluations)

            for evaluation in datapoint_evaluations:
                if evaluation.coherence_score is not None:
                    coherence_scores.append(evaluation.coherence_score)
                    coherence_count += 1
                if evaluation.relevance_score is not None:
                    relevance_scores.append(evaluation.relevance_score)
                    relevance_count += 1
                if evaluation.semantic_similarity_score is not None:
                    semantic_similarity_scores.append(
                        evaluation.semantic_similarity_score)
                    semantic_similarity_count += 1

            def calculate_percentage(count: int, total: int) -> float:
                return (count / total * 100) if total > 0 else 0.0

            return (
                (
                    Decimal(self._calculate_average(coherence_scores)).quantize(
                        Decimal('0.00'), rounding=ROUND_DOWN),
                    calculate_percentage(coherence_count, total_count),
                    coherence_count
                ),
                (
                    Decimal(self._calculate_average(relevance_scores)).quantize(
                        Decimal('0.00'), rounding=ROUND_DOWN),
                    calculate_percentage(relevance_count, total_count),
                    relevance_count
                ),
                (
                    Decimal(self._calculate_average(semantic_similarity_scores)).quantize(
                        Decimal('0.00'), rounding=ROUND_DOWN),
                    calculate_percentage(
                        semantic_similarity_count, total_count),
                    semantic_similarity_count
                ),
                total_count
            )

    def calculate_model_evaluation_scores(self, filter_data: GetModelEvalautionsDTO, existing_session: Session | None = None) -> tuple[tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], list[dict[str, Any]], int]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_get_model_evaluations(
                session, self._data_manager, filter_data)

            model_evaluations: list[ModelEvaluation] = self._data_manager.get_all_model_evaluations(
                session, filter_data)

            helpful_scores: list[int] = []
            honest_scores: list[int] = []
            harmless_scores: list[int] = []
            semantic_similarity_scores: list[float] = []
            evaluation_types: list[EvaluationType] = []

            # Counters for the number of evaluations that have each score set
            helpful_count = 0
            honest_count = 0
            harmless_count = 0
            semantic_similarity_count = 0
            total_count = len(model_evaluations)

            for evaluation in model_evaluations:
                if evaluation.helpful_score is not None:
                    helpful_scores.append(evaluation.helpful_score)
                    helpful_count += 1
                if evaluation.honest_score is not None:
                    honest_scores.append(evaluation.honest_score)
                    honest_count += 1
                if evaluation.harmless_score is not None:
                    harmless_scores.append(evaluation.harmless_score)
                    harmless_count += 1
                if evaluation.semantic_similarity_score is not None:
                    semantic_similarity_scores.append(
                        evaluation.semantic_similarity_score)
                    semantic_similarity_count += 1
                if evaluation.evaluation_type:
                    evaluation_types.append({"test_datapoint_id": evaluation.datapoint.id,
                                            "ground_truth": evaluation.datapoint.evaluation_type, "predicted_label": evaluation.evaluation_type})

            def calculate_percentage(count: int, total: int) -> float:
                return (count / total * 100) if total > 0 else 0.0

            return (
                (
                    Decimal(self._calculate_average(helpful_scores)).quantize(
                        Decimal('0.00'), rounding=ROUND_DOWN),
                    calculate_percentage(helpful_count, total_count),
                    helpful_count
                ),
                (
                    Decimal(self._calculate_average(honest_scores)).quantize(
                        Decimal('0.00'), rounding=ROUND_DOWN),
                    calculate_percentage(honest_count, total_count),
                    honest_count
                ),
                (
                    Decimal(self._calculate_average(harmless_scores)).quantize(
                        Decimal('0.00'), rounding=ROUND_DOWN),
                    calculate_percentage(harmless_count, total_count),
                    harmless_count
                ),
                (
                    Decimal(self._calculate_average(semantic_similarity_scores)).quantize(
                        Decimal('0.00'), rounding=ROUND_DOWN),
                    calculate_percentage(
                        semantic_similarity_count, total_count),
                    semantic_similarity_count
                ),
                evaluation_types,
                total_count
            )

    def generate_model_evaluation(self, model_id: int, test_datapoint_id: int, semantic_similarity_model: dict | None = None, existing_session: Session | None = None) -> list[int]:
        with self._data_manager.get_session(existing_session) as session:
            model: Model = self._data_manager.get_model_by_id(
                session, model_id)[0]

            fine_tuned_model_id: str = ""
            if model.fine_tuned_model_id:
                # Get the model id of the currently fine tuned model
                fine_tuned_model_id = model.fine_tuned_model_id
            else:
                # Get the model id of the selected model for fine tuning in case it is a base model that is not fine tuned.
                fine_tuned_model_id = model.training_run.fine_tuning_model

            all_test_datapoints: list[DataPointDTO] = self.get_all_test_datapoints(
                model_id, False, existing_session=session)

            # Get the test datapoint to display in the frontend
            next_test_datapoint: DataPointDTO = next(
                (datapoint for datapoint in all_test_datapoints if datapoint.id == test_datapoint_id), None)

            # Get the "unanswered" test datapoints message to display in the frontend
            test_datapoint_message_without_last_entry: MessagesContainer = copy.deepcopy(
                next_test_datapoint.messages)

            # Set the last messages content to empty
            test_datapoint_message_without_last_entry["messages"][
                -1]['content'] = ""

            test_datapoint_message_without_last_entry["messages"][-1]['content'] = self.generate_model_chat(
                test_datapoint_message_without_last_entry["messages"], fine_tuned_model_id)

            create_model_evaluation_dto: CreateModelEvaluationDTO = CreateModelEvaluationDTO(
                model_id=model_id, datapoint_id=next_test_datapoint.id, messages=test_datapoint_message_without_last_entry)

            if semantic_similarity_model:
                # Set semantic similarity score if available
                create_model_evaluation_dto: CreateModelEvaluationDTO = self._semantic_similarity_score_calculator.calculate_model_evaluations_semantic_similarity_score(
                    [create_model_evaluation_dto], [next_test_datapoint], semantic_similarity_model)[0]

            # Create model evaluation
            model_evaluation: ModelEvaluation = self._data_manager.create_model_evaluations(
                session, [create_model_evaluation_dto])[0]

            # Map current_model evluation to DTO to then append all the related datapoints to the current test datapoint that already has the original training datapoints, to avoid changing the database entity relations
            model_eval_dto: ComplexModelEvaluationDTO = self._mapper.map_model_evaluation_to_complex_dto(
                session, model_evaluation)

            model_eval_dto: ComplexModelEvaluationDTO = self._add_related_augmented_datapoints_to_related_datapoints_of_model_evals_test_datapoint(
                session, model, model_eval_dto)

            return [model_eval_dto]

    def generate_model_chat(self, chat: MessagesContainer, model_id: str) -> str:
        return self._openai_service.generate_model_chat(chat, model_id)

    def _add_related_augmented_datapoints_to_related_datapoints_of_model_evals_test_datapoint(self, session: Session, model: Model, model_eval: ComplexModelEvaluationDTO) -> ComplexModelEvaluationDTO:
        # Fetch all augmented datasets from the current and previous model versions
        augmented_datasets = self._fetch_augmented_datasets(model)

        # Add related augmented datapoints to the test datapoint's related_datapoints list. They are related because they were augmented from original training datapoints which were related to specific test datapoints, so the augmented datapoints are related to the same test datpoints.
        for dataset in augmented_datasets:
            for augmented_dp in dataset.datapoints:
                if any(related_dp.id == model_eval.datapoint.id for related_dp in augmented_dp.related_datapoints):
                    model_eval.datapoint.related_datapoints.append(
                        self._mapper.map_datapoint_to_dto(session, augmented_dp))

        return model_eval

    # Filter all augmented datasets of the current model. Since each child model inherits all parent model datasets + adds optionally its own augmented dataset, there is no need for recursion.
    def _fetch_augmented_datasets(self, model: Model):
        return [dataset for dataset in model.training_datasets if dataset.augmented]

    def get_or_create_model_evaluation_by_id(self, model_id: int, test_datapoint_id: int, semantic_similarity_model: dict | None = None, existing_session: Session | None = None) -> list[ComplexModelEvaluationDTO]:
        with self._data_manager.get_session(existing_session) as session:
            model: Model = self._data_manager.get_model_by_id(
                session, model_id)[0]

            model_evaluations: list[ModelEvaluation] = self._data_manager.get_all_model_evaluations(
                session, GetModelEvalautionsDTO(model_id=model_id, datapoint_id=test_datapoint_id))

            if model_evaluations:
                model_eval_dto: ComplexDataPointEvaluationDTO = self._mapper.map_model_evaluation_to_complex_dto(
                    session, model_evaluations[0])

                # Add all the necessary related augmented datapoints
                model_eval_dto: ComplexModelEvaluationDTO = self._add_related_augmented_datapoints_to_related_datapoints_of_model_evals_test_datapoint(
                    session, model, model_eval_dto)
                return [model_eval_dto]
            else:
                return self.generate_model_evaluation(model_id, test_datapoint_id, semantic_similarity_model=semantic_similarity_model, existing_session=session)

    def get_all_test_datapoints(self, model_id: int, only_ids: bool, existing_session: Session | None = None) -> list[DataPointDTO | int]:
        with self._data_manager.get_session(existing_session) as session:

            model: Model = self._data_manager.get_model_by_id(
                session, model_id)[0]

            all_test_datapoints: list[DataPointDTO | int] = []

            # Get the first "original" from all datasets - only this has a unique test datasets, the augmented ones inherit the test dataset from the original one
            # TODO: At the moment a model can only have one
            test_dataset = model.training_datasets[0].test_dataset
            if test_dataset and test_dataset.datapoints:
                for datapoint in test_dataset.datapoints:
                    if only_ids:
                        all_test_datapoints.append(datapoint.id)
                    else:
                        all_test_datapoints.append(
                            self._mapper.map_datapoint_to_dto(session, datapoint))

                return all_test_datapoints
            else:
                return []

    def get_all_training_datapoints(self, model_id: int, existing_session: Session | None = None) -> list[DataPointDTO]:
        with self._data_manager.get_session(existing_session) as session:
            model: Model = self._data_manager.get_model_by_id(
                session, model_id)[0]

            all_training_datapoints: list[DataPoint] = [
                datapoint for dataset in model.training_datasets for datapoint in dataset.datapoints
            ]

            return [self._mapper.map_datapoint_to_simple_dto(session, datapoint) for datapoint in all_training_datapoints]

    def _calculate_average(self, scores: list[int | float]) -> float:
        if len(scores) == 0:
            return 0.0
        return sum(scores) / len(scores)

    def delete_datasets(self, dataset_ids: list[int], existing_session: Session | None = None):
        with self._data_manager.get_session(existing_session) as session:
            self._data_manager.delete_datasets(session, dataset_ids)

    def delete_model_evaluations_by_model_id(self, model_id: int, existing_session: Session | None = None) -> None:
        with self._data_manager.get_session(existing_session) as session:
            model_evaluations: list[ModelEvaluation] = self._data_manager.get_all_model_evaluations(
                session, GetModelEvalautionsDTO(model_id=model_id))

            all_eval_ids: list[int] = [eval.id for eval in model_evaluations]
            self._data_manager.delete_model_evaluations(session, all_eval_ids)

    def update_model_evaluations(self, update_models_evalautions_data: list[UpdateModelEvaluationDTO], existing_session: Session | None = None) -> list[ModelEvaluation]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_update_model_evaluations(
                session, self._data_manager, update_models_evalautions_data)
            updated_evaluations: list[ModelEvaluation] = self._data_manager.update_model_evaluations(
                session, update_models_evalautions_data)

            return [self._mapper.map_model_evaluation_to_complex_dto(session, model_eval) for model_eval in updated_evaluations]

    def filter_models_with_original_project(self, model_data: GetModelsDTO, existing_session: Session | None = None) -> list[ModelWithOriginalProjectDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_get_all_models(
                session, self._data_manager, model_data)
            models_with_original_project: list[tuple[Model, Project]] = self._data_manager.get_all_models_with_original_project(
                session, model_data)

            model_dtos: list[ModelWithOriginalProjectDTO] = [
                self._mapper.map_model_to_dto_with_original_project(session, model, project) for model, project in models_with_original_project]

            # Sort the DTOs by the creation date of the associated projects in descending order
            # and then by the creation date of the models in descending order
            model_dtos_sorted = sorted(
                model_dtos,
                key=lambda dto: (
                    dto.original_project.created_at, dto.created_at),
                reverse=True
            )

            return model_dtos_sorted

    def filter_simple_projects(self, projects_data: GetProjectsDTO, existing_session: Session | None = None) -> list[SimpleProjectDTO]:
        with self._data_manager.get_session(existing_session) as session:
            self._validator.validate_get_all_projects(
                session, self._data_manager, projects_data)
            projects: list[Project] = self._data_manager.get_all_projects(
                session, projects_data)

            return [self._mapper.map_project_to_simple_dto(session, project) for project in projects]

    def remove_model_global_status(self, model_id: int, existing_session: Session | None = None) -> None:
        with self._data_manager.get_session(existing_session) as session:
            model: Model = self._data_manager.remove_model_global_status(
                session, model_id)
            return [self._mapper.map_model_to_dto(session, model)]

    def delete_openai_checkpoint_models(self, original_fine_tuning_job_id: str) -> None:
        self._openai_service.delete_checkpoint_models_by_original_fine_tuning_job_id(
            original_fine_tuning_job_id)

    def get_fine_tuning_job_metrics(self, fine_tuning_job_id: str, step: int | None = None) -> dict[str, Any]:
        return self._openai_service.get_fine_tuning_job_metrics(fine_tuning_job_id, step)

    def get_model_by_id(self, model_id: int, existing_session: Session | None = None) -> list[ComplexModelDTO]:
        with self._data_manager.get_session(existing_session) as session:
            model: Model = self._data_manager.get_model_by_id(
                session, model_id)[0]
            return [self._mapper.map_model_to_complex_dto(session, model)]

    def get_model_hierarchy_ids(self, model_id: int, existing_session: Session | None = None) -> list[int]:
        with self._data_manager.get_session(existing_session) as session:
            model_ids: list[int] = self._data_manager.get_model_hierarchy_ids(
                session, model_id)

            return model_ids

    def retrieve_training_data(self, file_id: str, as_jsonl: bool = True) -> bytes:
        return self._openai_service.retrieve_training_data(file_id, as_jsonl)

    def check_model_availability(self, fine_tuning_model: str) -> bool:
        available_models: list = self._openai_service.get_available_models()

        # Check if the model_used_for_fine_tuning exists
        if fine_tuning_model not in available_models:
            return False
        else:
            return True

    def fetch_new_events(self, fine_tuning_job_id: str, limit: int = 20, last_event_id: str | None = None) -> tuple[list[object], str]:
        return self._openai_service.fetch_new_events(fine_tuning_job_id, limit=limit, last_event_id=last_event_id)
