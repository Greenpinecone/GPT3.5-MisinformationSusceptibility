from dataclasses import asdict
from ....persistence.interfaces.i_data_manager import IDataManager
from ..classes.request_dto_validators import *
from ....dtos.create_request import *
from ....dtos.get_request import *
from ....dtos.update_request import *
from ....custom_types.exceptions import CustomValidationError
from marshmallow import Schema
from sqlalchemy.orm import Session


class ValidatorFacade:
    def __init__(self):
        pass

    def validate_data(self, data: list | object, validator: Schema, session: Session, data_manager: IDataManager, operation_type: str) -> None:
        if isinstance(data, list):
            for item in data:
                self._validate_single(
                    item, validator, session, data_manager, operation_type)
        else:
            self._validate_single(data, validator, session,
                                  data_manager, operation_type)

    def _validate_single(self, item: list | object, validator: Schema, session: Session, data_manager: IDataManager, operation_type: str) -> None:
        validator_instance = validator(
            session=session, data_manager=data_manager)
        errors = validator_instance.validate(asdict(item))
        if errors:
            raise CustomValidationError(
                operation_type=operation_type, errors=errors)

    def validate_create_projects(self, session: Session, data_manager: IDataManager, data: list[CreateProjectDTO]) -> None:
        self.validate_data(
            data, CreateProjectSchema, session, data_manager, "create projects")

    def validate_create_datasets(self, session: Session, data_manager: IDataManager, data: list[CreateDatasetDTO]) -> None:
        self.validate_data(
            data, CreateDatasetSchema, session, data_manager, "create datasets")

    def validate_create_datapoints(self, session: Session, data_manager: IDataManager, data: list[CreateDataPointDTO]) -> None:
        self.validate_data(
            data, CreateDataPointSchema, session, data_manager, "create datapoints")

    def validate_create_models(self, session: Session, data_manager: IDataManager, data: list[CreateModelDTO]) -> None:
        self.validate_data(data, CreateModelSchema, session,
                           data_manager, "create models")

    def validate_create_model_evaluations(self, session: Session, data_manager: IDataManager, data: list[CreateModelEvaluationDTO]) -> None:
        self.validate_data(
            data, CreateModelEvaluationSchema, session, data_manager, "create model evaluations")

    def validate_create_training_runs(self, session: Session, data_manager: IDataManager, data: list[CreateTrainingRunDTO]) -> None:
        self.validate_data(
            data, CreateTrainingRunSchema, session, data_manager, "create training runs")

    def validate_get_training_runs(self, session: Session, data_manager: IDataManager, data: GetTrainingRunsDTO) -> None:
        self.validate_data(
            data, GetTrainingRunsSchema, session, data_manager, "get training runs")

    def validate_update_training_runs(self, session: Session, data_manager: IDataManager, data: list[UpdateTrainingRunDTO]) -> None:
        self.validate_data(
            data, UpdateTrainingRunSchema, session, data_manager, "update training runs")

    def validate_get_all_projects(self, session: Session, data_manager: IDataManager, data: GetProjectsDTO) -> None:
        self.validate_data(
            data, GetProjectsSchema, session, data_manager, "get all projects")

    def validate_get_all_models(self, session: Session, data_manager: IDataManager, data: GetModelsDTO) -> None:
        self.validate_data(data, GetModelsSchema, session,
                           data_manager, "get all models")

    def validate_get_all_datasets(self, session: Session, data_manager: IDataManager, data: GetDatasetsDTO) -> None:
        self.validate_data(
            data, GetDatasetsSchema, session, data_manager, "get all datasets")

    def validate_get_models_by_project_id(self, session: Session, data_manager: IDataManager, data: GetModelsByProjectIdDTO) -> None:
        self.validate_data(
            data, GetModelsByProjectIdSchema, session, data_manager, "get models by project ID")

    def validate_get_datasets_by_model_id(self, session: Session, data_manager: IDataManager, data: GetDatasetsByModelIdDTO) -> None:
        self.validate_data(
            data, GetDatasetsByModelIdSchema, session, data_manager, "get datasets by model ID")

    def validate_get_datapoints_by_dataset_id(self, session: Session, data_manager: IDataManager, data: GetDatapointsByDatasetIdDTO) -> None:
        self.validate_data(
            data, GetDatapointsByDatasetIdSchema, session, data_manager, "get datapoints by dataset ID")

    def validate_update_projects(self, session: Session, data_manager: IDataManager, data: list[UpdateProjectDTO]) -> None:
        self.validate_data(
            data, UpdateProjectSchema, session, data_manager, "update projects")

    def validate_update_datasets(self, session: Session, data_manager: IDataManager, data: list[UpdateDatasetDTO]) -> None:
        self.validate_data(
            data, UpdateDatasetSchema, session, data_manager, "update datasets")

    def validate_update_datapoints(self, session: Session, data_manager: IDataManager, data: list[UpdateDataPointDTO]) -> None:
        self.validate_data(data, UpdateDataPointSchema,
                           session, data_manager, "update datapoints")

    def validate_update_models(self, session: Session, data_manager: IDataManager, data: list[UpdateModelDTO]) -> None:
        self.validate_data(data, UpdateModelSchema, session,
                           data_manager, "update models")

    def validate_update_model_evaluations(self, session: Session, data_manager: IDataManager, data: list[UpdateModelEvaluationDTO]) -> None:
        self.validate_data(
            data, UpdateModelEvaluationSchema, session, data_manager, "update model evaluations")

    def validate_create_datapoint_evaluations(self, session: Session, data_manager: IDataManager, data: list[CreateDataPointEvaluationDTO]) -> None:
        self.validate_data(
            data, CreateDataPointEvaluationSchema, session, data_manager, "create datapoint evaluations")

    def validate_update_datapoint_evaluations(self, session: Session, data_manager: IDataManager, data: list[UpdateDataPointEvaluationDTO]) -> None:
        self.validate_data(
            data, UpdateDataPointEvaluationSchema, session, data_manager, "update datapoint evaluations")

    def validate_get_datapoint_evaluation(self, session: Session, data_manager: IDataManager, data: GetDataPointEvaluationsDTO) -> None:
        self.validate_data(
            data, GetDataPointEvaluationSchema, session, data_manager, "get datapoint evaluations")
