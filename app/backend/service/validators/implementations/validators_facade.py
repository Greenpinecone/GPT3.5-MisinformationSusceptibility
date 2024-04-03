from dataclasses import asdict
from ....persistence.interfaces.i_data_manager import IDataManager
from ..classes.request_dto_validators import *
from ....dtos.create_request import *
from ....dtos.get_request import *


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
        self.get_models_by_project_id_validator: GetModelsByProjectIdSchema = GetModelsByProjectIdSchema(
            data_manager=self.data_manager)
        self.get_datasets_by_model_id_validator: GetDatasetsByModelIdSchema = GetDatasetsByModelIdSchema(
            data_manager=self.data_manager)
        self.get_datapoints_by_dataset_id_validator: GetDatapointsByDatasetIdSchema = GetDatapointsByDatasetIdSchema(
            data_manager=self.data_manager)

    def validate_create_project(self, data: CreateProjectDTO) -> CreateProjectDTO:
        return self.create_project_validator.load(asdict(data))

    def validate_create_dataset(self, data: CreateDatasetDTO) -> CreateDatasetDTO:
        return self.create_dataset_validator.load(asdict(data))

    def validate_create_datapoint(self, data: CreateDataPointDTO) -> CreateDataPointDTO:
        return self.create_datapoint_validator.load(asdict(data))

    def validate_create_model(self, data: CreateModelDTO) -> CreateModelDTO:
        return self.create_model_validator.load(asdict(data))

    def validate_create_model_evaluation(self, data: CreateModelEvaluationDTO) -> CreateModelEvaluationDTO:
        return self.create_model_evaluation_validator.load(asdict(data))

    def validate_create_training_run(self, data: CreateTrainingRunDTO) -> CreateTrainingRunDTO:
        return self.create_training_run_validator.load(asdict(data))

    def prepare_get_projects(self, data: GetProjectsDTO) -> GetProjectsDTO:
        return self.get_projects_validator.load(asdict(data))

    def prepare_get_models_by_project_id(self, data: GetModelsByProjectIdDTO) -> GetModelsByProjectIdDTO:
        return self.get_models_by_project_id_validator.load(asdict(data))

    def prepare_get_datasets_by_model_id(self, data: GetDatasetsByModelIdDTO) -> GetDatasetsByModelIdDTO:
        return self.get_datasets_by_model_id_validator.load(asdict(data))

    def prepare_get_datapoints_by_dataset_id(self, data: GetDatapointsByDatasetIdDTO) -> GetDatapointsByDatasetIdDTO:
        return self.get_datapoints_by_dataset_id_validator.load(asdict(data))
