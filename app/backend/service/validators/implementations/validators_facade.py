from dataclasses import asdict
from ....persistence.interfaces.i_data_manager import IDataManager
from ..classes.request_dto_validators import *
from ....dtos.create_request import *
from ....dtos.get_request import *
from ....dtos.update_request import *
from ....custom_types.exceptions import CustomValidationError
from marshmallow import Schema


class ValidatorFacade:
    def __init__(self, data_manager: IDataManager):
        self.data_manager: IDataManager = data_manager
        # Initialize each validator with the data_manager
        self.create_project_validator: CreateProjectSchema = CreateProjectSchema(
            data_manager=self.data_manager)
        self.create_dataset_validator: CreateDatasetSchema = CreateDatasetSchema(
            data_manager=self.data_manager)
        self.create_datapoint_validator: CreateDataPointSchema = CreateDataPointSchema(
            data_manager=self.data_manager)
        self.create_model_validator: CreateModelSchema = CreateModelSchema(
            data_manager=self.data_manager)
        self.create_model_evaluation_validator: CreateModelEvaluationSchema = CreateModelEvaluationSchema(
            data_manager=self.data_manager)
        self.create_training_run_validator: CreateTrainingRunSchema = CreateTrainingRunSchema(
            data_manager=self.data_manager)
        self.get_projects_validator: GetProjectsSchema = GetProjectsSchema(
            data_manager=self.data_manager)
        self.get_models_validator: GetModelsSchema = GetModelsSchema(
            data_manager=self.data_manager)
        self.get_datasets_validator: GetDatasetsSchema = GetDatasetsSchema(
            data_manager=self.data_manager)
        self.get_models_by_project_id_validator: GetModelsByProjectIdSchema = GetModelsByProjectIdSchema(
            data_manager=self.data_manager)
        self.get_datasets_by_model_id_validator: GetDatasetsByModelIdSchema = GetDatasetsByModelIdSchema(
            data_manager=self.data_manager)
        self.get_datapoints_by_dataset_id_validator: GetDatapointsByDatasetIdSchema = GetDatapointsByDatasetIdSchema(
            data_manager=self.data_manager)
        self.update_project_validator: UpdateProjectSchema = UpdateProjectSchema(
            data_manager=self.data_manager)
        self.update_dataset_validator: UpdateDatasetSchema = UpdateDatasetSchema(
            data_manager=self.data_manager)
        self.update_datapoint_validator: UpdateDataPointSchema = UpdateDataPointSchema(
            data_manager=self.data_manager)
        self.update_model_validator: UpdateModelSchema = UpdateModelSchema(
            data_manager=self.data_manager)
        self.update_model_evaluation_validator: UpdateModelEvaluationSchema = UpdateModelEvaluationSchema(
            data_manager=self.data_manager)

    def validate_data(self, data: list | object, validator: Schema, operation_type: str) -> None:
        if isinstance(data, list):
            for item in data:
                self._validate_single(item, validator, operation_type)
        else:
            self._validate_single(data, validator, operation_type)

    def _validate_single(self, item, validator: Schema, operation_type: str) -> None:
        errors = validator.validate(asdict(item))
        if errors:
            raise CustomValidationError(
                operation_type=operation_type, errors=errors)

    def validate_create_projects(self, data: list[CreateProjectDTO]) -> None:
        self.validate_data(
            data, self.create_project_validator, "create projects")

    def validate_create_datasets(self, data: list[CreateDatasetDTO]) -> None:
        self.validate_data(
            data, self.create_dataset_validator, "create datasets")

    def validate_create_datapoints(self, data: list[CreateDataPointDTO]) -> None:
        self.validate_data(
            data, self.create_datapoint_validator, "create datapoints")

    def validate_create_models(self, data: list[CreateModelDTO]) -> None:
        self.validate_data(data, self.create_model_validator, "create models")

    def validate_create_model_evaluations(self, data: list[CreateModelEvaluationDTO]) -> None:
        self.validate_data(
            data, self.create_model_evaluation_validator, "create model evaluations")

    def validate_create_training_runs(self, data: list[CreateTrainingRunDTO]) -> None:
        self.validate_data(
            data, self.create_training_run_validator, "create training runs")

    # Update validations for getting DTOs (single DTO cases)
    def validate_get_all_projects(self, data: GetProjectsDTO) -> None:
        self.validate_data(
            data, self.get_projects_validator, "get all projects")

    def validate_get_all_models(self, data: GetModelsDTO) -> None:
        self.validate_data(data, self.get_models_validator, "get all models")

    def validate_get_all_datasets(self, data: GetDatasetsDTO) -> None:
        self.validate_data(
            data, self.get_datasets_validator, "get all datasets")

    def validate_get_models_by_project_id(self, data: GetModelsByProjectIdDTO) -> None:
        self.validate_data(
            data, self.get_models_by_project_id_validator, "get models by project ID")

    def validate_get_datasets_by_model_id(self, data: GetDatasetsByModelIdDTO) -> None:
        self.validate_data(
            data, self.get_datasets_by_model_id_validator, "get datasets by model ID")

    def validate_get_datapoints_by_dataset_id(self, data: GetDatapointsByDatasetIdDTO) -> None:
        self.validate_data(
            data, self.get_datapoints_by_dataset_id_validator, "get datapoints by dataset ID")

    def validate_update_projects(self, data: list[UpdateProjectDTO]) -> None:
        self.validate_data(
            data, self.update_project_validator, "update projects")

    def validate_update_datasets(self, data: list[UpdateDatasetDTO]) -> None:
        self.validate_data(
            data, self.update_dataset_validator, "update datasets")

    def validate_update_datapoints(self, data: list[UpdateDataPointDTO]) -> None:
        self.validate_data(data, self.update_datapoint_validator,
                           "update datapoints")

    def validate_update_models(self, data: list[UpdateModelDTO]) -> None:
        self.validate_data(data, self.update_model_validator, "update models")

    def validate_update_model_evaluations(self, data: list[UpdateModelEvaluationDTO]) -> None:
        self.validate_data(
            data, self.update_model_evaluation_validator, "update model evaluations")
