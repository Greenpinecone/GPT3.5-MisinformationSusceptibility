from dataclasses import asdict
from marshmallow import Schema
from sqlalchemy.orm import Session
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from app.backend.service.validators.classes.request_dto_validators import CreateDataPointEvaluationSchema, CreateDataPointSchema, CreateDatasetSchema, CreateModelEvaluationSchema, CreateModelSchema, CreateProjectSchema, CreateTrainingRunSchema, GetDataPointEvaluationSchema, GetDatapointsByDatasetIdSchema, GetDatasetsByModelIdSchema, GetDatasetsSchema, GetModelEvaluationSchema, GetModelsByProjectIdSchema, GetModelsSchema, GetProjectsSchema, GetTrainingRunsSchema, UpdateDataPointEvaluationSchema, UpdateDataPointSchema, UpdateDatasetSchema, UpdateModelEvaluationSchema, UpdateModelSchema, UpdateProjectSchema, UpdateTrainingRunSchema
from app.backend.dtos.create_request import CreateDataPointDTO, CreateDataPointEvaluationDTO, CreateDatasetDTO, CreateModelDTO, CreateModelEvaluationDTO, CreateProjectDTO, CreateTrainingRunDTO
from app.backend.dtos.get_request import GetDataPointEvaluationsDTO, GetDatapointsByDatasetIdDTO, GetDatasetsByModelIdDTO, GetDatasetsDTO, GetModelEvalautionsDTO, GetModelsByProjectIdDTO, GetModelsDTO, GetProjectsDTO, GetTrainingRunsDTO
from app.backend.dtos.update_request import UpdateDataPointDTO, UpdateDataPointEvaluationDTO, UpdateDatasetDTO, UpdateModelDTO, UpdateModelEvaluationDTO, UpdateProjectDTO, UpdateTrainingRunDTO
from app.backend.custom_types.exceptions import CustomValidationError


class ValidatorFacade:
    def __init__(self):
        pass

    def validate_data(self, data: list | object, validator: Schema, session: Session, data_manager: IDataManager, operation_type: str) -> None:
        """
        Validates data using a specified schema validator.

        Args:
            data (list | object): The data to be validated.
            validator (Schema): The marshmallow schema validator to use.
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            operation_type (str): The type of operation being validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        if isinstance(data, list):
            for item in data:
                self._validate_single(
                    item, validator, session, data_manager, operation_type)
        else:
            self._validate_single(data, validator, session,
                                  data_manager, operation_type)

    def _validate_single(self, item: list | object, validator: Schema, session: Session, data_manager: IDataManager, operation_type: str) -> None:
        """
        Validates a single data item using a specified schema validator.

        Args:
            item (list | object): The single data item to be validated.
            validator (Schema): The marshmallow schema validator to use.
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            operation_type (str): The type of operation being validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        validator_instance = validator(
            session=session, data_manager=data_manager)
        errors = validator_instance.validate(asdict(item))
        if errors:
            raise CustomValidationError(
                operation_type=operation_type, errors=errors)

    def validate_create_projects(self, session: Session, data_manager: IDataManager, data: list[CreateProjectDTO]) -> None:
        """
        Validates create project data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[CreateProjectDTO]): The project data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, CreateProjectSchema, session, data_manager, "create projects")

    def validate_create_datasets(self, session: Session, data_manager: IDataManager, data: list[CreateDatasetDTO]) -> None:
        """
        Validates create dataset data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[CreateDatasetDTO]): The dataset data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, CreateDatasetSchema, session, data_manager, "create datasets")

    def validate_create_datapoints(self, session: Session, data_manager: IDataManager, data: list[CreateDataPointDTO]) -> None:
        """
        Validates create datapoint data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[CreateDataPointDTO]): The datapoint data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, CreateDataPointSchema, session, data_manager, "create datapoints")

    def validate_create_models(self, session: Session, data_manager: IDataManager, data: list[CreateModelDTO]) -> None:
        """
        Validates create model data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[CreateModelDTO]): The model data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(data, CreateModelSchema, session,
                           data_manager, "create models")

    def validate_create_model_evaluations(self, session: Session, data_manager: IDataManager, data: list[CreateModelEvaluationDTO]) -> None:
        """
        Validates create model evaluation data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[CreateModelEvaluationDTO]): The model evaluation data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, CreateModelEvaluationSchema, session, data_manager, "create model evaluations")

    def validate_create_training_runs(self, session: Session, data_manager: IDataManager, data: list[CreateTrainingRunDTO]) -> None:
        """
        Validates create training run data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[CreateTrainingRunDTO]): The training run data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, CreateTrainingRunSchema, session, data_manager, "create training runs")

    def validate_get_training_runs(self, session: Session, data_manager: IDataManager, data: GetTrainingRunsDTO) -> None:
        """
        Validates get training run data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (GetTrainingRunsDTO): The training run data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, GetTrainingRunsSchema, session, data_manager, "get training runs")

    def validate_update_training_runs(self, session: Session, data_manager: IDataManager, data: list[UpdateTrainingRunDTO]) -> None:
        """
        Validates update training run data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[UpdateTrainingRunDTO]): The training run data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, UpdateTrainingRunSchema, session, data_manager, "update training runs")

    def validate_get_all_projects(self, session: Session, data_manager: IDataManager, data: GetProjectsDTO) -> None:
        """
        Validates get all projects data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (GetProjectsDTO): The project data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, GetProjectsSchema, session, data_manager, "get all projects")

    def validate_get_all_models(self, session: Session, data_manager: IDataManager, data: GetModelsDTO) -> None:
        """
        Validates get all models data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (GetModelsDTO): The model data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(data, GetModelsSchema, session,
                           data_manager, "get all models")

    def validate_get_all_datasets(self, session: Session, data_manager: IDataManager, data: GetDatasetsDTO) -> None:
        """
        Validates get all datasets data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (GetDatasetsDTO): The dataset data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, GetDatasetsSchema, session, data_manager, "get all datasets")

    def validate_get_models_by_project_id(self, session: Session, data_manager: IDataManager, data: GetModelsByProjectIdDTO) -> None:
        """
        Validates get models by project ID data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (GetModelsByProjectIdDTO): The model data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, GetModelsByProjectIdSchema, session, data_manager, "get models by project ID")

    def validate_get_datasets_by_model_id(self, session: Session, data_manager: IDataManager, data: GetDatasetsByModelIdDTO) -> None:
        """
        Validates get datasets by model ID data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (GetDatasetsByModelIdDTO): The dataset data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, GetDatasetsByModelIdSchema, session, data_manager, "get datasets by model ID")

    def validate_get_datapoints_by_dataset_id(self, session: Session, data_manager: IDataManager, data: GetDatapointsByDatasetIdDTO) -> None:
        """
        Validates get datapoints by dataset ID data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (GetDatapointsByDatasetIdDTO): The datapoint data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, GetDatapointsByDatasetIdSchema, session, data_manager, "get datapoints by dataset ID")

    def validate_update_projects(self, session: Session, data_manager: IDataManager, data: list[UpdateProjectDTO]) -> None:
        """
        Validates update project data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[UpdateProjectDTO]): The project data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, UpdateProjectSchema, session, data_manager, "update projects")

    def validate_update_datasets(self, session: Session, data_manager: IDataManager, data: list[UpdateDatasetDTO]) -> None:
        """
        Validates update dataset data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[UpdateDatasetDTO]): The dataset data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, UpdateDatasetSchema, session, data_manager, "update datasets")

    def validate_update_datapoints(self, session: Session, data_manager: IDataManager, data: list[UpdateDataPointDTO]) -> None:
        """
        Validates update datapoint data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[UpdateDataPointDTO]): The datapoint data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(data, UpdateDataPointSchema,
                           session, data_manager, "update datapoints")

    def validate_update_models(self, session: Session, data_manager: IDataManager, data: list[UpdateModelDTO]) -> None:
        """
        Validates update model data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[UpdateModelDTO]): The model data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(data, UpdateModelSchema, session,
                           data_manager, "update models")

    def validate_update_model_evaluations(self, session: Session, data_manager: IDataManager, data: list[UpdateModelEvaluationDTO]) -> None:
        """
        Validates update model evaluation data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[UpdateModelEvaluationDTO]): The model evaluation data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, UpdateModelEvaluationSchema, session, data_manager, "update model evaluations")

    def validate_get_model_evaluations(self, session: Session, data_manager: IDataManager, data: GetModelEvalautionsDTO) -> None:
        """
        Validates get model evaluation data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (GetModelEvalautionsDTO): The model evaluation data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, GetModelEvaluationSchema, session, data_manager, "get model evaluations")

    def validate_create_datapoint_evaluations(self, session: Session, data_manager: IDataManager, data: list[CreateDataPointEvaluationDTO]) -> None:
        """
        Validates create datapoint evaluation data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[CreateDataPointEvaluationDTO]): The datapoint evaluation data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, CreateDataPointEvaluationSchema, session, data_manager, "create datapoint evaluations")

    def validate_update_datapoint_evaluations(self, session: Session, data_manager: IDataManager, data: list[UpdateDataPointEvaluationDTO]) -> None:
        """
        Validates update datapoint evaluation data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (list[UpdateDataPointEvaluationDTO]): The datapoint evaluation data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, UpdateDataPointEvaluationSchema, session, data_manager, "update datapoint evaluations")

    def validate_get_datapoint_evaluation(self, session: Session, data_manager: IDataManager, data: GetDataPointEvaluationsDTO) -> None:
        """
        Validates get datapoint evaluation data.

        Args:
            session (Session): The current database session.
            data_manager (IDataManager): The data manager instance for data access.
            data (GetDataPointEvaluationsDTO): The datapoint evaluation data to be validated.

        Raises:
            CustomValidationError: If validation fails.
        """
        self.validate_data(
            data, GetDataPointEvaluationSchema, session, data_manager, "get datapoint evaluations")
