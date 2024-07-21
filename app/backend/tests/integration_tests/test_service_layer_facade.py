from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
import json
from sqlite3 import IntegrityError
from typing import Any, Generator
from app.backend.custom_types.typedicts import Message
from app.backend.dtos.get_request import GetDataPointEvaluationsDTO, GetDatapointsByDatasetIdDTO, GetDatasetsByModelIdDTO, GetDatasetsDTO, GetModelEvalautionsDTO, GetModelsByProjectIdDTO, GetModelsDTO, GetProjectsDTO, GetTrainingRunsDTO
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO, UpdateDataPointDTO, UpdateDataPointEvaluationDTO, UpdateDatasetDTO, UpdateModelDTO, UpdateModelEvaluationDTO, UpdateProjectDTO, UpdateTrainingRunDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.backend.service.interfaces.i_service_manager import IServiceManager
from app.backend.util.logger import Logger
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from app.backend.dtos.create_request import *
from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound, NoResultFound
from app.backend.database.schema import FineTuningModelVersions, Project, DataPoint, Dataset, Model, TrainingRun, DataPointEvaluation, ModelEvaluation, CurrentProjectData, UploadFormats, model_dataset_association, project_model_link, Base
from sqlalchemy.orm import Session
from app.backend.dtos.response import *
from app.backend.tests.conftest import assert_properties
from app.backend.custom_types.exceptions import CustomValidationError
from unittest.mock import patch, MagicMock
from app.backend.util.config import SBERT_MODELS as sbert_models
import pytest

logger = Logger(__name__)


NON_EXISTENT_ID: int = 9999999
INVALID_ID: int = -1


class TestServiceLayerFunctions:

    _service: IServiceManager

    @pytest.fixture(autouse=True)
    def _setup_service(self, request):
        self._service = request.getfixturevalue('service')

    valid_project_1: tuple[GetProjectsDTO, list[dict] | None, bool] = (GetProjectsDTO(
        project_name="Alpha",
        created_at=datetime(2023, 1, 1)
    ), [{
        'id': 1,
        'project_name': "Project Alpha",
        'description': "Alpha Project Description",
        'created_at': datetime,  # Type check for datetime
    }], False)

    valid_project_2: tuple[GetProjectsDTO, list[dict] | None, bool] = (GetProjectsDTO(
        project_name="Beta",
        created_at=datetime(2022, 1, 1)
    ), [{
        'id': 2,
        'project_name': "Project Beta",
        'description': "Beta Project Description",
        'created_at': datetime,  # Type check for datetime
    }], False)

    invalid_project_1: tuple[GetProjectsDTO, list[dict] | None, bool] = (GetProjectsDTO(
        project_name="P" * 256,  # Invalid project name (too long)
        created_at=datetime.now()
    ), None, True)

    invalid_project_2: tuple[GetProjectsDTO, list[dict] | None, bool] = (GetProjectsDTO(
        project_name="Project Gamma",
        created_at="invalid-date"  # Invalid datetime format
    ), None, True)

    @pytest.mark.parametrize("create_data, expected_properties, should_fail", [
        valid_project_1,
        valid_project_2,
        invalid_project_1,
        invalid_project_2
    ])
    def test_filter_projects(self, db_setup_manager: tuple[IDataManager, Session], create_data: GetProjectsDTO, expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.filter_projects(create_data, session)
        else:
            result = self._service.filter_projects(create_data, session)
            assert len(result) == len(expected_properties), f"""The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."""

            for fetched_project, expected_property in zip(result, expected_properties):
                assert_properties(asdict(fetched_project), expected_property)

    valid_model_1 = (
        GetModelsDTO(
            model_name="Project Beta/Model Alpha",
            created_at=datetime(2023, 1, 1),
            exlude_project_id=1,
            version="0"
        ),
        [{
            'id': 1,
            'model_name': "Project Beta/Model Alpha",
            'version': "0",
            'project_ids': [1, 2],
            'training_dataset_ids': [3],
            'uuid': "parent_uuid",
            'augmentation_configurations': [],
            'semantic_similarity_model': "similarity_model",
            'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_id_1",
            'fine_tuned_model_id': FineTuningModelVersions.openai.value[0],
            'is_global': True,
            'fine_tuning_job_id': "ft_job_id_1",
            'created_at': datetime,  # Type check for datetime
            'parent_model_id': None,
            'training_run_id': 1,
            'is_checkpoint_model': False,
            'checkpoint_step': 0,
        }],
        False
    )

    valid_model_2 = (
        GetModelsDTO(
            project_id=1,
            model_name="Project Alpha/Model Beta",
            created_at=datetime(2023, 1, 2),
            version="0",
            is_checkpoint_model=True,
            only_original_models=True
        ),
        [{
            'id': 2,
            'model_name': "Project Alpha/Model Beta",
            'version': "0",
            'project_ids': [1, 2],
            'training_dataset_ids': [],
            'uuid': "child_uuid",
            'augmentation_configurations': [{"configuration_1": {
                'selected_method': "method_1", 'prev_method': None, 'augmentation_percentage': 10.0, 'augmentation_config': {'translate_languages': ["en", "es"]}}}],
            'semantic_similarity_model': "child_similarity_model",
            'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_id_2",
            'fine_tuned_model_id': "ft_model_id_2",
            'is_global': True,
            'fine_tuning_job_id': "ft_job_id_2",
            'created_at': datetime,  # Type check for datetime
            'parent_model_id': None,
            'training_run_id': 2,
            'is_checkpoint_model': True,
            'checkpoint_step': 0,
        }],
        False
    )

    invalid_model_1 = (
        GetModelsDTO(
            model_name="M" * 256,  # Invalid model name (too long)
            created_at=datetime.now()
        ),
        None,
        True
    )

    invalid_model_2 = (
        GetModelsDTO(
            model_name="Project Gamma/Model Alpha",
            created_at="invalid-date"  # Invalid datetime format
        ),
        None,
        True
    )

    @pytest.mark.parametrize("create_data, expected_properties, should_fail", [
        valid_model_1,
        valid_model_2,
        invalid_model_1,
        invalid_model_2
    ])
    def test_filter_models(self, db_setup_manager: tuple[IDataManager, Session], create_data: GetModelsDTO, expected_properties: list[dict], should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.filter_models(create_data, session)
        else:
            result = self._service.filter_models(create_data, session)
            assert len(result) == len(expected_properties), f"""The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."""

            for fetched_model, expected_property in zip(result, expected_properties):
                assert_properties(asdict(fetched_model), expected_property)

    valid_dataset_1 = (
        GetDatasetsDTO(
            dataset_name="Project Alpha/Dataset Alpha",
            augmented=False,
            category=DatasetCategory.training,
            project_id=1,
            is_global=False
        ),
        [{
            'id': 1,
            'dataset_name': "Project Alpha/Dataset Alpha",
            'augmented': False,
            'category': DatasetCategory.training,
            'fine_tuning_model': "model_v1",
            'fine_tuning_company': FineTuningCompany.openai,
            'fine_tuning_formatting': "format_v1",
            'is_global': False,
            'test_dataset_id': None,
            'created_at': datetime,  # Type check for datetime
            'initial_dataset_ids': [],
            'model_ids': [],
            'project_ids': [1, 2],
            'datapoint_ids': [5, 6]
        }],
        False
    )

    valid_dataset_2 = (
        GetDatasetsDTO(
            dataset_name="Project Beta/Dataset Beta",
            augmented=False,
            category=DatasetCategory.training,
            project_id=2,
            is_global=False
        ),
        [{
            'id': 2,
            'dataset_name': "Project Beta/Dataset Beta",
            'augmented': False,
            'category': DatasetCategory.training,
            'fine_tuning_model': "model_v1",
            'fine_tuning_company': FineTuningCompany.openai,
            'fine_tuning_formatting': "format_v1",
            'is_global': False,
            'test_dataset_id': 1,
            'created_at': datetime,  # Type check for datetime
            'initial_dataset_ids': [],
            'model_ids': [],
            'project_ids': [2, 1],
            'datapoint_ids': [1]
        }],
        False
    )

    invalid_dataset_1 = (
        GetDatasetsDTO(
            dataset_name="D" * 256,  # Invalid dataset name (too long)
            augmented=False,
            category=DatasetCategory.training,
            project_id=1,
            is_global=False
        ),
        None,
        True
    )

    invalid_dataset_2 = (
        GetDatasetsDTO(
            dataset_name="Project Gamma/Dataset Alpha",
            augmented="invalid-boolean",  # Invalid boolean format
            category=DatasetCategory.training,
            project_id=1,
            is_global=False
        ),
        None,
        True
    )

    @pytest.mark.parametrize("create_data, expected_properties, should_fail", [
        valid_dataset_1,
        valid_dataset_2,
        invalid_dataset_1,
        invalid_dataset_2
    ])
    def test_filter_datasets(self, db_setup_manager: tuple[IDataManager, Session], create_data: GetDatasetsDTO, expected_properties: list[dict], should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.filter_datasets(create_data, session)
        else:
            result = self._service.filter_datasets(create_data, session)
            assert len(result) == len(expected_properties), f"""The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."""

            for fetched_dataset, expected_property in zip(result, expected_properties):
                assert_properties(asdict(fetched_dataset), expected_property)

    create_project_1 = (
        [CreateProjectDTO(
            project_name="Project Gamma",
            description="Gamma Project Description",
            model_ids=[1],
            dataset_ids=[1]
        )],
        [{
            'id': 3,  # Assuming this will be the next ID
            'project_name': "Project Gamma",
            'description': "Gamma Project Description",
            'created_at': datetime,  # Type check for datetime
            'model_ids': [1],
            'dataset_ids': [1]
        }],
        False
    )

    create_project_2 = (
        [CreateProjectDTO(
            project_name="Project Epsilon",
            description="Epsilon Project Description",
            model_ids=[1, 2],
            dataset_ids=[1, 2]
        )],
        [{
            'id': 3,  # Assuming this will be the next ID
            'project_name': "Project Epsilon",
            'description': "Epsilon Project Description",
            'created_at': datetime,  # Type check for datetime
            'model_ids': [1, 2],
            'dataset_ids': [1, 2]
        }],
        False
    )

    invalid_project_1 = (
        [CreateProjectDTO(
            project_name="P" * 256,  # Invalid project name (too long)
            description="Invalid Project",
            model_ids=[],
            dataset_ids=[1]
        )],
        None,
        True
    )

    invalid_project_2 = (
        [CreateProjectDTO(
            project_name="Project Gamma",
            description="Gamma Project Description",
            model_ids=[INVALID_ID],  # Non-existent model ID
            dataset_ids=[]  # Non-existent dataset ID
        )],
        None,
        True
    )

    @pytest.mark.parametrize("create_data, expected_properties, should_fail", [
        create_project_1,
        create_project_2,
        invalid_project_1,
        invalid_project_2
    ])
    def test_create_projects(self, db_setup_manager: tuple[IDataManager, Session], create_data: list[CreateProjectDTO], expected_properties: list[dict], should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.create_projects(create_data, session)
        else:
            result = self._service.create_projects(create_data, session)
            assert len(result) == len(expected_properties), f"""The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."""

            for created_project, expected_property in zip(result, expected_properties):
                assert_properties(asdict(created_project), expected_property)

    update_project_1 = (
        [UpdateProjectDTO(
            id=1,
            project_name="Updated Project Alpha",
            description="Updated Alpha Project Description",
            model_ids=[3],  # Only set models that are not original models
            dataset_ids=[2]  # only set datasets that are not original datasets
        )],
        [{
            'id': 1,
            'project_name': "Updated Project Alpha",
            'description': "Updated Alpha Project Description",
            'created_at': datetime,  # Type check for datetime
            'model_ids': [2, 3],  # original models included
            'dataset_ids': [1, 2]  # original datasets included
        }],
        False
    )

    update_project_2 = (
        [UpdateProjectDTO(
            id=2,
            project_name="Updated Project Beta",
            description="Updated Beta Project Description",
            model_ids=[],
            dataset_ids=[1]
        )],
        [{
            'id': 2,
            'project_name': "Updated Project Beta",
            'description': "Updated Beta Project Description",
            'created_at': datetime,  # Type check for datetime
            'model_ids': [1, 3],
            'dataset_ids': [1, 2, 3]
        }],
        False
    )

    invalid_project_1 = (
        [UpdateProjectDTO(
            id=1,
            project_name="P" * 256,  # Invalid project name (too long)
            description="Invalid Project",
            model_ids=[1],
            dataset_ids=[1]
        )],
        None,
        True
    )

    invalid_project_2 = (
        [UpdateProjectDTO(
            id=2,
            project_name="Updated Project Gamma",
            description="Gamma Project Description",
            model_ids=[INVALID_ID],  # Non-existent model ID
            dataset_ids=[INVALID_ID]  # Non-existent dataset ID
        )],
        None,
        True
    )

    @pytest.mark.parametrize("update_data, expected_properties, should_fail", [
        update_project_1,
        update_project_2,
        invalid_project_1,
        invalid_project_2
    ])
    def test_update_projects(self, db_setup_manager: tuple[IDataManager, Session], update_data: list[UpdateProjectDTO], expected_properties: list[dict], should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.udpate_projects(update_data, session)
        else:
            result = self._service.udpate_projects(update_data, session)
            assert len(result) == len(expected_properties), f"""The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."""

            for updated_project, expected_property in zip(result, expected_properties):
                assert_properties(asdict(updated_project), expected_property)

    valid_create_dataset_with_datapoints_1 = (
        CreateDatasetDTO(
            dataset_name="Valid Training Dataset 1",
            category=DatasetCategory.training,
            augmented=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model=FineTuningModelVersions.openai.value[0],
            fine_tuning_formatting=UploadFormats.openai.value[
                FineTuningModelVersions.openai.value[0]][0],
            project_ids=[1]
        ),
        [CreateDataPointDTO(
            messages={"messages": [
                {"role": "system", "content": "Training datapoint message"}]},
            dataset_id=5
        )],
        CreateDatasetDTO(
            dataset_name="Valid Test Dataset 1",
            category=DatasetCategory.test,
            augmented=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model=FineTuningModelVersions.openai.value[0],
            fine_tuning_formatting=UploadFormats.openai.value[
                FineTuningModelVersions.openai.value[0]][0],
            project_ids=[1]
        ),
        [CreateDataPointDTO(
            messages={"messages": [
                {"role": "system", "content": "Test datapoint message"}]},
            dataset_id=4
        )],
        [{
            'dataset_name': "Project Alpha/Valid Training Dataset 1",
            'category': DatasetCategory.training,
            'augmented': False,
            'fine_tuning_company': FineTuningCompany.openai,
            'fine_tuning_model': FineTuningModelVersions.openai.value[0],
            'fine_tuning_formatting': UploadFormats.openai.value[FineTuningModelVersions.openai.value[0]][0],
            'is_global': False,
            'test_dataset': {
                'dataset_name': "Project Alpha/Valid Test Dataset 1",
                'category': DatasetCategory.test,
                'augmented': False,
                'fine_tuning_company': FineTuningCompany.openai,
                'fine_tuning_model': FineTuningModelVersions.openai.value[0],
                'fine_tuning_formatting': UploadFormats.openai.value[FineTuningModelVersions.openai.value[0]][0],
                'is_global': False,
                'created_at': datetime,  # Type check for datetime
            },
            'created_at': datetime,  # Type check for datetime
            'project_ids': [1],
            'datapoints': [{
                'messages': {"messages": [{"role": "system", "content": "Training datapoint message"}]},
                'dataset_id': 5,
                'created_at': datetime,  # Type check for datetime
            }]
        }],
        False
    )

    valid_create_dataset_with_datapoints_2 = (
        CreateDatasetDTO(
            dataset_name="Valid Training Dataset 2",
            category=DatasetCategory.training,
            augmented=True,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model=FineTuningModelVersions.openai.value[0],
            fine_tuning_formatting=UploadFormats.openai.value[
                FineTuningModelVersions.openai.value[0]][0],
            project_ids=[2]
        ),
        [CreateDataPointDTO(
            messages={"messages": [
                {"role": "system", "content": "Training datapoint message"}]},
            dataset_id=5
        )],
        CreateDatasetDTO(
            dataset_name="Valid Test Dataset 2",
            category=DatasetCategory.test,
            augmented=True,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model=FineTuningModelVersions.openai.value[0],
            fine_tuning_formatting=UploadFormats.openai.value[
                FineTuningModelVersions.openai.value[0]][0],
            project_ids=[2]
        ),
        [CreateDataPointDTO(
            messages={"messages": [
                {"role": "system", "content": "Test datapoint message"}]},
            dataset_id=4
        )],
        [{
            'dataset_name': "Project Beta/Valid Training Dataset 2",
            'category': DatasetCategory.training,
            'augmented': True,
            'fine_tuning_company': FineTuningCompany.openai,
            'fine_tuning_model': FineTuningModelVersions.openai.value[0],
            'fine_tuning_formatting': UploadFormats.openai.value[FineTuningModelVersions.openai.value[0]][0],
            'is_global': False,
            'test_dataset': {
                'dataset_name': "Project Beta/Valid Test Dataset 2",
                'category': DatasetCategory.test,
                'augmented': True,
                'fine_tuning_company': FineTuningCompany.openai,
                'fine_tuning_model': FineTuningModelVersions.openai.value[0],
                'fine_tuning_formatting': UploadFormats.openai.value[FineTuningModelVersions.openai.value[0]][0],
                'is_global': False,
                'created_at': datetime,  # Type check for datetime
            },
            'created_at': datetime,  # Type check for datetime
            'project_ids': [2],
            'datapoints': [{
                'messages': {"messages": [{"role": "system", "content": "Training datapoint message"}]},
                'dataset_id': 5,
                'created_at': datetime,  # Type check for datetime
            }]
        }],
        False
    )

    invalid_create_dataset_with_datapoints_1 = (
        CreateDatasetDTO(
            dataset_name="I" * 256,  # Invalid dataset name (too long)
            category=DatasetCategory.training,
            augmented=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",  # invalid model
            fine_tuning_formatting="format_v1",  # invalid format
            project_ids=[1]
        ),
        [CreateDataPointDTO(
            messages={"messages": [
                {"role": "system", "content": "Training datapoint message"}]},
            dataset_id=None  # No dataset id
        )],
        CreateDatasetDTO(
            dataset_name="Valid Test Dataset 3",
            category=DatasetCategory.test,
            augmented=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",  # invalid model
            fine_tuning_formatting="format_v1",  # invalid format
            project_ids=[1]
        ),
        [CreateDataPointDTO(
            messages={"messages": [
                {"role": "system", "content": "Test datapoint message"}]},
            dataset_id=None  # No dataset id
        )],
        None,
        True
    )

    invalid_create_dataset_with_datapoints_2 = (
        CreateDatasetDTO(
            dataset_name="Valid Training Dataset 4",
            category=DatasetCategory.training,
            augmented=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",  # invalid model
            fine_tuning_formatting="format_v1",  # invalid format
            project_ids=[INVALID_ID]  # Non-existent project ID
        ),
        [CreateDataPointDTO(
            messages={"messages": [
                {"role": "system", "content": "Training datapoint message"}]},
            dataset_id=None  # No dataset id
        )],
        CreateDatasetDTO(
            dataset_name="Valid Test Dataset 4",
            category=DatasetCategory.test,
            augmented=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",  # invalid model
            fine_tuning_formatting="format_v1",  # invalid format
            project_ids=[INVALID_ID]  # Non-existent project ID
        ),
        [CreateDataPointDTO(
            messages={"messages": [
                {"role": "system", "content": "Test datapoint message"}]},
            dataset_id=None  # No dataset id
        )],
        None,
        True
    )

    @pytest.mark.parametrize("trainings_dataset_dto, trainings_datapoint_dtos, test_dataset_dto, test_datapoint_dtos, expected_properties, should_fail", [
        valid_create_dataset_with_datapoints_1,
        valid_create_dataset_with_datapoints_2,
        invalid_create_dataset_with_datapoints_1,
        invalid_create_dataset_with_datapoints_2
    ])
    def test_create_dataset_with_datapoints(self, db_setup_manager: tuple[IDataManager, Session], trainings_dataset_dto: CreateDatasetDTO, trainings_datapoint_dtos: list[CreateDataPointDTO], test_dataset_dto: CreateDatasetDTO, test_datapoint_dtos: list[CreateDataPointDTO], expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError) as excinfo:
                self._service.create_dataset_with_datapoints(
                    trainings_dataset_dto, trainings_datapoint_dtos, test_dataset_dto, test_datapoint_dtos, session)

            # Print the error message
            print(f"Caught expected exception: {excinfo.value}")
        else:
            result = self._service.create_dataset_with_datapoints(
                trainings_dataset_dto, trainings_datapoint_dtos, test_dataset_dto, test_datapoint_dtos, session)
            assert len(result) == len(expected_properties), f"""The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."""

            for created_dataset, expected_property in zip(result, expected_properties):
                assert_properties(asdict(created_dataset), expected_property)

    valid_get_dataset_by_id_1 = (
        1,  # Dataset ID
        [{
            'id': 1,
            'dataset_name': "Project Alpha/Dataset Alpha",
            'augmented': False,
            'category': DatasetCategory.training,
            'fine_tuning_model': "model_v1",
            'fine_tuning_company': FineTuningCompany.openai,
            'fine_tuning_formatting': "format_v1",
            'is_global': False,
            'test_dataset_id': None,
            'created_at': datetime,  # Type check for datetime
            'initial_dataset_ids': [],
            'model_ids': [],
            'project_ids': [1, 2],
            'datapoint_ids': [5, 6]
        }],
        False
    )

    valid_get_dataset_by_id_2 = (
        2,  # Dataset ID
        [{
            'id': 2,
            'dataset_name': "Project Beta/Dataset Beta",
            'augmented': False,
            'category': DatasetCategory.training,
            'fine_tuning_model': "model_v1",
            'fine_tuning_company': FineTuningCompany.openai,
            'fine_tuning_formatting': "format_v1",
            'is_global': False,
            'test_dataset_id': 1,
            'created_at': datetime,  # Type check for datetime
            'initial_dataset_ids': [],
            'model_ids': [],
            'project_ids': [1, 2],
            'datapoint_ids': [1]
        }],
        False
    )

    invalid_get_dataset_by_id_1 = (
        NON_EXISTENT_ID,  # Non-existent dataset ID
        None,
        True
    )

    invalid_get_dataset_by_id_2 = (
        INVALID_ID,  # Invalid dataset ID
        None,
        True
    )

    @pytest.mark.parametrize("dataset_id, expected_properties, should_fail", [
        valid_get_dataset_by_id_1,
        valid_get_dataset_by_id_2,
        invalid_get_dataset_by_id_1,
        invalid_get_dataset_by_id_2
    ])
    def test_get_dataset_by_id(self, db_setup_manager: tuple[IDataManager, Session], dataset_id: int, expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                self._service.get_dataset_by_id(dataset_id, session)
        else:
            result = self._service.get_dataset_by_id(dataset_id, session)
            assert len(result) == len(expected_properties), f"""The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."""

            for fetched_dataset, expected_property in zip(result, expected_properties):
                assert_properties(asdict(fetched_dataset), expected_property)

    valid_model_1 = (
        [CreateModelDTO(
            model_name="Valid Model",
            project_ids=[1, 2],
            training_dataset_ids=[1],
            augmentation_configurations=None,
            semantic_similarity_model=None,
            fine_tuning_job_id="some fine tuning job id",
            fine_tuning_checkpoint_job_id="some fine tuning checkpoint job id",
            fine_tuned_model_id="some fine tuned model id",
            parent_model_id=1,
            training_run_id=None,
            is_global=True,
            is_checkpoint_model=True,
            checkpoint_step=20
        )],
        [{
            'model_name': "Project Alpha/Valid Model",  # Name with project prefix
            'version': "1",
            'project_ids': [1, 2],
            'training_dataset_ids': [1],
            'uuid': str,
            'augmentation_configurations': [],
            'semantic_similarity_model': None,
            'fine_tuning_checkpoint_job_id': "some fine tuning checkpoint job id",
            'fine_tuned_model_id': "some fine tuned model id",
            'is_global': True,
            'fine_tuning_job_id': "some fine tuning job id",
            'created_at': datetime,  # Type check for datetime
            'parent_model_id': 1,
            'training_run_id': None,
            'is_checkpoint_model': True,
            'checkpoint_step': 20
        }],
        False
    )

    invalid_model_1 = (
        [CreateModelDTO(
            model_name="Invalid Model",
            project_ids=[1, 2],
            training_dataset_ids=[1],
            augmentation_configurations=None,
            semantic_similarity_model=None,
            fine_tuning_job_id=None,
            fine_tuning_checkpoint_job_id=None,
            fine_tuned_model_id=None,
            parent_model_id=None,
            training_run_id=NON_EXISTENT_ID,  # Training run does not exist
            is_global=True,
            is_checkpoint_model=False,
            checkpoint_step=None
        )],
        None,
        True
    )

    @pytest.mark.parametrize("create_data, expected_properties, should_fail", [
        valid_model_1,
        invalid_model_1
    ])
    def test_create_models(self, db_setup_manager: tuple[IDataManager, Session], create_data: list[CreateModelDTO], expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.create_models(create_data, session)
        else:
            result = self._service.create_models(create_data, session)
            assert len(result) == len(expected_properties), f"""The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."""

            for fetched_model, expected_property in zip(result, expected_properties):
                assert_properties(asdict(fetched_model), expected_property)

    valid_model_update = (
        [UpdateModelDTO(
            id=1,
            model_name="Updated Model",
            project_ids=[],
            training_dataset_ids=[3],
            augmentation_configurations=None,
            semantic_similarity_model=None,
            fine_tuning_job_id=None,
            fine_tuning_checkpoint_job_id=None,
            fine_tuned_model_id=None,
            is_global=False
        )],
        [{
            'id': 1,
            'model_name': "Project Beta/Updated Model",
            'version': "0",
            'project_ids': [2],
            'training_dataset_ids': [3],
            'uuid': "parent_uuid",
            'augmentation_configurations': [],
            'semantic_similarity_model': "similarity_model",
            'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_id_1",
            'fine_tuned_model_id': FineTuningModelVersions.openai.value[0],
            'is_global': False,
            'fine_tuning_job_id': "ft_job_id_1",
            'created_at': datetime,  # Type check for datetime
            'parent_model_id': None,
            'training_run_id': 1,
            'is_checkpoint_model': False,
            'checkpoint_step': 0
        }],
        False
    )

    invalid_model_update = (
        [UpdateModelDTO(
            id=1,
            model_name="Invalid Model",
            project_ids=[1, INVALID_ID],
            training_dataset_ids=[INVALID_ID],
            augmentation_configurations=None,
            semantic_similarity_model=None,
            fine_tuning_job_id=None,
            fine_tuning_checkpoint_job_id=None,
            fine_tuned_model_id=None,
            is_global=True
        )],
        None,
        True
    )

    @pytest.mark.parametrize("update_data, expected_properties, should_fail", [
        valid_model_update,
        invalid_model_update
    ])
    def test_update_models(self, db_setup_manager: tuple[IDataManager, Session], update_data: list[UpdateModelDTO], expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.update_models(update_data, session)
        else:

            result = self._service.update_models(update_data, session)
            assert len(result) == len(expected_properties), f"""The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."""

            for fetched_model, expected_property in zip(result, expected_properties):
                assert_properties(asdict(fetched_model), expected_property)

    @pytest.mark.parametrize("model_ids, should_fail", [
        ([1, 2], False),  # valid case: assume models with ID 1 and 2 exist
        # invalid case: assume model with ID 999 does not exist
        ([NON_EXISTENT_ID], False)
    ])
    def test_delete_models(self, db_setup_manager: tuple[IDataManager, Session], model_ids: list[int], should_fail: bool):
        data_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                self._service.delete_models(model_ids, session)
        else:
            self._service.delete_models(model_ids, session)
            # Verify that models were deleted
            for model_id in model_ids:
                with pytest.raises(NoResultFound):
                    data_manager.get_model_by_id(session, model_id)

    @pytest.mark.parametrize("update_data, expected_properties, should_fail", [
        (
            UpdateDataPointDTO(
                id=1,
                related_datapoint_ids=[1],
                evaluation_type=EvaluationType.T
            ),
            [{
                'id': 1,
                'related_datapoints': [{'id': 1, 'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                    role="user", content="What's the capital of France?")]), 'dataset_id': 2, 'related_datapoints': []}],
                'evaluation_type': EvaluationType.T
            }],
            False
        ),
        (
            UpdateDataPointDTO(
                id=1,
                # Invalid related datapoint id
                related_datapoint_ids=[INVALID_ID],
                evaluation_type=EvaluationType.F
            ),
            None,
            True
        )
    ])
    def test_update_datapoints(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateDataPointDTO, expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.update_datapoints([update_data], session)
        else:
            result = self._service.update_datapoints([update_data], session)
            assert len(
                result) == 1, "The function did not return exactly one result."

            for fetched_model, expected_property in zip(result, expected_properties):
                assert_properties(asdict(fetched_model), expected_property)

    @pytest.mark.parametrize("filter_data, expected_properties, should_fail", [
        (
            GetTrainingRunsDTO(
                model_id=1,
                epochs=10
            ),
            [{
                'id': 1,
                'model_name': "Project Beta/Model Alpha",
                'model_version': "0",
                'fine_tuning_model': "fine_tuning_model_1",
                'seed': 42
            }],
            False
        ),
        (
            GetTrainingRunsDTO(
                batch_size=33  # Invalid batch size
            ),
            None,
            True
        )
    ])
    def test_filter_simple_training_runs(self, db_setup_manager: tuple[IDataManager, Session], filter_data: GetTrainingRunsDTO, expected_properties: list[dict], should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.filter_simple_training_runs(filter_data, session)
        else:
            result = self._service.filter_simple_training_runs(
                filter_data, session)
            assert len(result) == len(expected_properties), f"The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."

            for fetched_model, expected_property in zip(result, expected_properties):
                assert_properties(asdict(fetched_model), expected_property)

    current_project_data_expected_properties = {
        'id': 1,
        'unfinished_progress': True,
        'current_page': "fine_tune_page",
        'save_checkpoint_models': True,
        'semantic_similarity_model': {"model": "similarity_model_v2"},
        'fine_tuning_step_counter': 5,
        'current_augmentation_configurations': [{"config": "config_value"}],
        'current_project': {'id': 1},  # project_alpha.id
        'selected_model_for_fine_tuning': {'id': 1},  # model.id
        'currently_modified_dataset': {'id': 2},  # dataset_alpha.id
        'current_fine_tuning_model': {'id': 1},  # model.id
        'selected_statistic_models': [1],  # list of model ids
        'generated_checkpoint_model_ids': [2],  # list of child model ids
        # list of datapoint evaluation ids
        'current_augmented_datapoint_evaluation_ids': [1, 2]
    }

    @pytest.mark.parametrize("expected_properties", [
        current_project_data_expected_properties
    ])
    def test_get_or_create_current_project_data(self, db_setup_manager: tuple[IDataManager, Session], expected_properties: dict):
        _, session = db_setup_manager

        result = self._service.get_or_create_current_project_data(session)

        assert_properties(asdict(result[0]), expected_properties)

    update_current_project_data: UpdateCurrentProjectDataDTO = UpdateCurrentProjectDataDTO(
        id=1,
        unfinished_progress=False,
        current_page="updated_page",
        save_checkpoint_models=False,
        semantic_similarity_model={"model": "updated_model"},
        current_augmentation_configurations=[{"config": "updated_config"}],
        fine_tuning_step_counter=10,
        current_project_id=2,
        current_fine_tuning_model_id=2,
        selected_model_for_fine_tuning_id=2,
        currently_modified_dataset_id=2,
        selected_statistic_models=[2],
        generated_checkpoint_model_ids=[1],
        current_augmented_datapoint_evaluation_ids=[1]
    )
    check_updated_current_project_data: dict = {
        'unfinished_progress': False,
        'current_page': "updated_page",
        'save_checkpoint_models': False,
        'semantic_similarity_model': {"model": "updated_model"},
        'fine_tuning_step_counter': 10,
        'current_augmentation_configurations': [{"config": "updated_config"}],
        'current_project': {'id': 2},
        'selected_model_for_fine_tuning': {'id': 2},
        'currently_modified_dataset': {'id': 2},
        'current_fine_tuning_model': {'id': 2},
        'selected_statistic_models': [2],
        'generated_checkpoint_model_ids': [1],
        'current_augmented_datapoint_evaluation_ids': [1]
    }

    @pytest.mark.parametrize("update_data, expected_properties", [
        (
            update_current_project_data,
            check_updated_current_project_data
        )
    ])
    def test_update_current_project_data(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateCurrentProjectDataDTO, expected_properties: dict):
        _, session = db_setup_manager

        # Call the function to test
        result = self._service.update_current_project_data(
            update_data, session)

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        updated_project_data = result[0]

        # Check the properties of the resulting entity
        assert_properties(asdict(updated_project_data), expected_properties)

    create_training_run_1 = (
        CreateTrainingRunDTO(
            model_id=1,
            fine_tuning_model="model_v1",  # Invalid fine tuning moedl version
            epochs=10,
            learning_rate_multiplier=0.1,
            batch_size=32,
            seed=42
        ),
        None,
        True
    )

    create_training_run_2 = (
        CreateTrainingRunDTO(
            model_id=3,
            fine_tuning_model=FineTuningModelVersions.openai.value[0],
            epochs=10,
            learning_rate_multiplier=0.2,
            batch_size=1,
            seed=123
        ),
        {
            'model_id': 3,
            'fine_tuning_model': FineTuningModelVersions.openai.value[0],
            'epochs': 10,
            'learning_rate_multiplier': 0.2,
            'batch_size': 1,
            'seed': 123
        },
        False
    )

    # Test function for create_training_runs
    @pytest.mark.parametrize("create_data, expected_properties, should_fail", [
        create_training_run_1,
        create_training_run_2
    ])
    def test_create_training_runs(self, db_setup_manager: tuple[IDataManager, Session], create_data: CreateTrainingRunDTO, expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            # Expecting a failure due to unique constraint violation
            with pytest.raises(CustomValidationError):
                self._service.create_training_run_dtos([create_data], session)
        else:
            # Call the function to test
            result = self._service.create_training_run_dtos(
                [create_data], session)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            created_training_run = result[0]

            # Check the properties of the resulting entity
            assert_properties(created_training_run, expected_properties)

    update_training_run_1 = (UpdateTrainingRunDTO(
        id=1,
        epochs=10,
        learning_rate_multiplier=0.15,
        batch_size=32,
        seed=4543245235
    ), {
        'id': 1,
        'epochs': 10,
        'learning_rate_multiplier': 0.15,
        'batch_size': 32,
        'seed': 4543245235
    }, False)

    update_training_run_2 = (UpdateTrainingRunDTO(
        id=2,
        epochs=25,  # invalid epochs
        learning_rate_multiplier=10,  # Invalid learning rate multiplier
        batch_size=72,  # invalid batch size
        seed=50
    ), None, True)

    @pytest.mark.parametrize("update_data, expected_properties, should_fail", [
        update_training_run_1,
        update_training_run_2
    ])
    def test_update_training_runs(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateTrainingRunDTO, expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            # Expecting a failure due to unique constraint violation
            with pytest.raises(CustomValidationError):
                self._service.update_training_run_dtos([update_data], session)
        else:
            # Call the function to test
            result = self._service.update_training_run_dtos(
                [update_data], session)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            updated_training_run = result[0]

            # Check the properties of the resulting entity
            assert_properties(updated_training_run, expected_properties)

    create_evaluation_1 = (CreateDataPointEvaluationDTO(
        datapoint_id=1,
        model_id=1,
        coherence_score=11,  # Invalid coherence score
        relevance_score=7,
        semantic_similarity_score=0.9
    ), None, True)

    create_evaluation_2 = (CreateDataPointEvaluationDTO(
        datapoint_id=4,
        model_id=2,
        coherence_score=9,
        relevance_score=0,
        semantic_similarity_score=85.0
    ), {
        'datapoint_id': 4,
        'model_id': 2,
        'coherence_score': 9,
        'relevance_score': 0,
        'semantic_similarity_score': 85.0,
    }, False)

    @pytest.mark.parametrize("create_data, expected_properties, should_fail", [
        create_evaluation_1,
        create_evaluation_2
    ])
    def test_create_datapoint_evaluations(self, db_setup_manager: tuple[IDataManager, Session], create_data: CreateDataPointEvaluationDTO, expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            # Expecting a failure due to unique constraint violation
            with pytest.raises(CustomValidationError):
                self._service.create_datapoint_evaluations(
                    [create_data], session)
        else:
            # Call the function to test
            result = self._service.create_datapoint_evaluations(
                [create_data], session)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            created_evaluation = result[0]

            # Check the properties of the resulting entity
            assert_properties(created_evaluation, expected_properties)

    update_evaluation_1 = (UpdateDataPointEvaluationDTO(
        id=2,
        coherence_score=7,
        relevance_score=6,
        semantic_similarity_score=0.4
    ), {
        'id': 2,
        'coherence_score': 7,
        'relevance_score': 6,
        'semantic_similarity_score': 0.4
    }, False)

    update_evaluation_2 = (UpdateDataPointEvaluationDTO(
        id=1,
        coherence_score=9,
        relevance_score=8,
        semantic_similarity_score=-1  # invalid semantic similarity score
    ), None, True)

    @pytest.mark.parametrize("update_data, expected_properties, should_fail", [
        update_evaluation_1,
        update_evaluation_2
    ])
    def test_update_datapoint_evaluations(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateDataPointEvaluationDTO, expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            # Expecting a failure due to unique constraint violation
            with pytest.raises(CustomValidationError):
                self._service.update_datapoint_evaluations([
                                                           update_data], session)
        else:

            # Call the function to test
            result = self._service.update_datapoint_evaluations([
                update_data], session)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            updated_evaluation = result[0]

            # Check the properties of the resulting entity
            assert_properties(updated_evaluation, expected_properties)

    filter_datapoint_evaluations_1: tuple[GetDataPointEvaluationsDTO, list[dict]] = (GetDataPointEvaluationsDTO(
        model_id=1,
        coherence_score=7,
        relevance_score=8,
        semantic_similarity_score=0.92
    ), [
        {
            'model_id': 1,
            'datapoint_id': 1,
            'coherence_score': 7,
            'relevance_score': 8,
            'semantic_similarity_score': 0.92,
        }
    ])

    filter_datapoint_evaluations_2: tuple[GetDataPointEvaluationsDTO, list[dict]] = (GetDataPointEvaluationsDTO(
        model_id=1,
        relevance_score=4,
        coherence_score=3,
        semantic_similarity_score=0.1
    ), [
        {
            'model_id': 1,
            'datapoint_id': 1,
            'coherence_score': 7,
            'relevance_score': 8,
            'semantic_similarity_score': 0.92,
        },
        {
            'model_id': 1,
            'datapoint_id': 2,
            'coherence_score': 4,
            'relevance_score': 4,
            'semantic_similarity_score': 0.5,
        }
    ])

    filter_datapoint_evaluations_3: tuple[GetDataPointEvaluationsDTO, list[dict]] = (GetDataPointEvaluationsDTO(
        model_id=1,
        relevance_score=9
    ), [])

    @pytest.mark.parametrize("filter_data, expected_properties", [
        filter_datapoint_evaluations_1,
        filter_datapoint_evaluations_2,
        filter_datapoint_evaluations_3
    ])
    def test_get_all_datapoint_evaluations(self, db_setup_manager: tuple[IDataManager, Session], filter_data: GetDataPointEvaluationsDTO, expected_properties: list[dict]):
        _, session = db_setup_manager

        # Call the function to test
        result = self._service.get_datapoint_evaluations(filter_data, session)

        # Ensure the correct number of results
        assert len(result) == len(expected_properties), f"The function did not return the correct number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for evaluation, expected in zip(result, expected_properties):
            assert_properties(evaluation, expected)

    # INFO: THE FOLLOWING FUNCTIONS HAVE BEEN TESTED EXTENSIVELY MANUALLY!
    # TODO: Add proper testing for the following service functions
    """
    1. create_fine_tuning_run
    2. get_current_fine_tuning_status
    3. cancel_fine_tuning_run
    4. save_checkpoint_models
    """

    @pytest.mark.parametrize("dataset_ids, expected_count, should_fail", [
        (
            [1, 2],  # Assuming these dataset IDs exist
            3,  # Expected datapoints count for the given dataset IDs
            False
        ),
        (
            [NON_EXISTENT_ID],  # Assuming this dataset ID does not exist
            None,
            True
        )
    ])
    def test_get_datasets_datapoints_count(self, db_setup_manager: tuple[IDataManager, Session], dataset_ids: list[int], expected_count: int, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                self._service.get_datasets_datapoints_count(
                    dataset_ids, session)
        else:
            result = self._service.get_datasets_datapoints_count(
                dataset_ids, session)

            assert_properties(result, expected_count)

    @pytest.mark.parametrize("training_run_id, expected_properties, should_fail", [
        (1, {
            'id': 1,
            'model_id': 1,
            'epochs': 10,
            'learning_rate_multiplier': 0.01,
            'batch_size': 32,
            'seed': 42,
            'fine_tuning_model': "fine_tuning_model_1",
            'created_at': datetime
        }, False),
        # No training run for this training run ID
        (NON_EXISTENT_ID, None, True),
    ])
    def test_get_training_run_by_id(self, db_setup_manager: tuple[IDataManager, Session], training_run_id: int, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                self._service.get_training_run_by_id(training_run_id, session)
        else:
            # Call the function to test
            result = self._service.get_training_run_by_id(
                training_run_id, session)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            training_run = result[0]

            # Check the properties of the resulting entity
            assert_properties(training_run, expected_properties)

    @pytest.mark.parametrize("datapoint_count, percentage, expected_count, should_fail", [
        (
            100,  # Positive case with valid datapoint count
            20.0,  # Valid augmentation percentage
            20,   # Expected augmentation count
            False
        ),
        (
            100,
            40.0,
            40,
            False
        )
    ])
    def test_get_total_augmentation_amount(self, datapoint_count: int, percentage: float, expected_count: int, should_fail: bool):
        if should_fail:
            with pytest.raises(Exception):
                self._service.get_total_augmentation_amount(
                    datapoint_count, percentage)
        else:
            result = self._service.get_total_augmentation_amount(
                datapoint_count, percentage)

            # Check the properties of the resulting entity
            assert_properties(result, expected_count)

    # TODO: Check for specific related datapoints since now every datapoint has a specific id
    # Define valid and invalid test cases
    valid_augmentation_configuration_1 = AugmentationConfiguration(
        selected_method="google_translate",
        prev_method=None,
        augmentation_percentage=67.0,
        augmentation_config=GoogleBTParams(translate_languages=[{"language": "Finnish", "code": "fi"},
                                                                {"language": "French", "code": "fr"},])
    )
    valid_augmentation_configuration_2 = AugmentationConfiguration(
        selected_method="EDA_Easy_Data_Augmentation",
        prev_method=None,
        augmentation_percentage=34.0,
        augmentation_config=EDAParams(
            alpha_rd=10.0, alpha_ri=10.0, alpha_rs=10.0, alpha_sr=10.0)
    )

    valid_augmentation_data = (
        1,
        [valid_augmentation_configuration_1, valid_augmentation_configuration_2],
        1,  # Assuming project_id 1 is valid
        sbert_models[0],
        False
    )

    invalid_augmentation_data = (
        NON_EXISTENT_ID,
        [valid_augmentation_configuration_1, valid_augmentation_configuration_2],
        1,  # Assuming project_id 1 is valid
        sbert_models[0],
        True
    )

    @pytest.mark.parametrize("model_id, augmentation_configurations, current_project_id, semantic_similarity_model, should_fail", [
        valid_augmentation_data,
        invalid_augmentation_data
    ])
    def test_generate_augmented_data(self, db_setup_manager: tuple[IDataManager, Session], model_id: int, augmentation_configurations: list[AugmentationConfiguration], current_project_id: int, semantic_similarity_model: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                self._service.generate_augmented_data(
                    model_id,
                    augmentation_configurations,
                    current_project_id,
                    semantic_similarity_model,
                    session
                )
        else:
            result = self._service.generate_augmented_data(
                model_id,
                augmentation_configurations,
                current_project_id,
                semantic_similarity_model,
                session
            )
            assert isinstance(
                result, list), "Result should be a list of evaluation IDs."
            assert len(result) == 3, f"Shoudl be exactly 9 augmented datapoints, instead got {
                len(result)}"

            for evaluation_id in result:
                assert isinstance(
                    evaluation_id, int), "Each evaluation ID should be an integer."

            session.flush()
            # Fetch all augmented datapoints
            model = test_manager.get_model_by_id(session, model_id)[
                0]
            # Get the last newly added dataset from this model
            augmented_dataset = sorted(
                model.training_datasets, key=lambda x: x.id)[-1]

            assert augmented_dataset, f"Expected augmented datasets got {
                augmented_dataset}"

            augmented_datapoints = augmented_dataset.datapoints

            # Get all test datapoints from the first training dataset
            test_datapoints = sorted(model.training_datasets, key=lambda x: x.id)[
                0].test_dataset.datapoints

            # Create mapping
            training_to_test_map: dict[int, list[DataPoint]
                                       ] = self._service._create_test_to_trainings_datapoints_mapping(test_datapoints)

            # Check if all augmented datapoints have the correct test datapoints added to their "related_datapoints" list
            for augmented_dp in augmented_datapoints:
                initial_training_id: int = augmented_dp.initial_datapoint_id
                if initial_training_id in training_to_test_map:
                    related_test_dps: list[DataPoint] = training_to_test_map[initial_training_id]
                    for test_dp in related_test_dps:
                        assert test_dp in augmented_dp.related_datapoints, "Related test datapoints should be correctly added."

# Define valid and invalid test cases
    valid_model_update_evaluation_1: tuple[UpdateDataPointEvaluationDTO, dict, bool] = (
        UpdateDataPointEvaluationDTO(
            id=1,
            coherence_score=9,
            relevance_score=8,
            semantic_similarity_score=0.95
        ),
        {
            'id': 1,
            'model_id': 1,
            'datapoint': {
                'id': 1,
                'dataset_id': 2,
                'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                    role="user", content="What's the capital of France?")]),
                'created_at': datetime  # Type check for datetime
            },
            'semantic_similarity_score': 0.95,
            'coherence_score': 9,
            'relevance_score': 8,
            'created_at': datetime  # Type check for datetime
        },
        False
    )

    invalid_model_update_evaluation_1: tuple[UpdateDataPointEvaluationDTO, dict, bool] = (
        UpdateDataPointEvaluationDTO(
            id=NON_EXISTENT_ID,  # Assuming 999 is an invalid ID for testing
            coherence_score=9,
            relevance_score=8,
            semantic_similarity_score=0.95
        ),
        None,
        True
    )

    @pytest.mark.parametrize("update_data, expected_properties, should_fail", [
        valid_model_update_evaluation_1,
        invalid_model_update_evaluation_1
    ])
    def test_update_datapoint_evaluations(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateDataPointEvaluationDTO, expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(SQLAlchemyError):
                self._service.update_datapoint_evaluations(
                    [update_data], session)
        else:
            result = self._service.update_datapoint_evaluations(
                [update_data], session)
            assert len(
                result) == 1, "The function did not return exactly one result."
            updated_evaluation = result[0]
            assert_properties(asdict(updated_evaluation), expected_properties)

    valid_datapoint_evaluations: tuple[GetDataPointEvaluationsDTO, tuple[tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], int], bool] = (
        # Assuming model_id=1 and datapoint_id=1 are valid
        GetDataPointEvaluationsDTO(model_id=1, datapoint_id=1),
        (
            # Coherence score: average=7.00, 100% of evaluations have this score, 1 count
            (Decimal('7.00'), 100.0, 1),
            # Relevance score: average=8.00, 100% of evaluations have this score, 1 count
            (Decimal('8.00'), 100.0, 1),
            # Semantic similarity score: average=0.92, 100% of evaluations have this score, 1 count
            (Decimal('0.92'), 100.0, 1),
            1  # Total count of evaluations
        ),
        False
    )

    invalid_datapoint_evaluations: tuple[GetDataPointEvaluationsDTO, tuple[tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], int], bool] = (
        # Assuming model_id=999 and datapoint_id=999 are invalid
        GetDataPointEvaluationsDTO(
            model_id=NON_EXISTENT_ID, datapoint_id=NON_EXISTENT_ID),
        None,
        True
    )

    @pytest.mark.parametrize("filter_data, expected_properties, should_fail", [
        valid_datapoint_evaluations,
        invalid_datapoint_evaluations
    ])
    def test_calculate_datapoint_evaluation_scores(self, db_setup_manager: tuple[IDataManager, Session], filter_data: GetDataPointEvaluationsDTO, expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.calculate_datapoint_evaluation_scores(
                    filter_data, session)
        else:
            result = self._service.calculate_datapoint_evaluation_scores(
                filter_data, session)
            assert len(
                result) == 4, "The function did not return the expected number of result tuples."
            assert_properties(result, expected_properties)

    # Define valid and invalid test cases
    valid_model_evaluations: tuple[GetModelEvalautionsDTO, tuple[tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], list[dict[str, Any]], int], bool] = (
        GetModelEvalautionsDTO(model_id=1),  # Assuming model_id=1 is valid
        (
            # Helpful score: average=7.50, 100% of evaluations have this score, 2 counts
            (Decimal('7.50'), 100.0, 2),
            # Honest score: average=8.50, 100% of evaluations have this score, 2 counts
            (Decimal('8.50'), 100.0, 2),
            # Harmless score: average=9.50, 100% of evaluations have this score, 2 counts
            (Decimal('9.50'), 100.0, 2),
            # Semantic similarity score: average=0.75, 100% of evaluations have this score, 2 counts
            (Decimal('0.75'), 100.0, 2),
            [
                {"test_datapoint_id": 1, "ground_truth": None,
                    "predicted_label": EvaluationType.T},
                {"test_datapoint_id": 2, "ground_truth": EvaluationType.T,
                    "predicted_label": EvaluationType.F}
            ],
            2  # Total count of evaluations
        ),
        False
    )

    invalid_model_evaluations: tuple[GetModelEvalautionsDTO, tuple[tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], tuple[Decimal, float, int], list[dict[str, Any]], int], bool] = (
        GetModelEvalautionsDTO(model_id=NON_EXISTENT_ID),
        None,
        True
    )

    @pytest.mark.parametrize("filter_data, expected_properties, should_fail", [
        valid_model_evaluations,
        invalid_model_evaluations
    ])
    def test_calculate_model_evaluation_scores(self, db_setup_manager: tuple[IDataManager, Session], filter_data: GetModelEvalautionsDTO, expected_properties: dict, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(CustomValidationError):
                self._service.calculate_model_evaluation_scores(
                    filter_data, session)
        else:
            result = self._service.calculate_model_evaluation_scores(
                filter_data, session)
            assert len(
                result) == 6, "The function did not return the expected number of result tuples."
            assert_properties(result, expected_properties)

    valid_model_evaluation: tuple[int, int, dict | None, ComplexModelEvaluationDTO, bool] = (
        1,  # model_id
        5,  # test_datapoint_id
        None,  # semantic_similarity_model
        {
            "id": 3,
            "model_id": 1,
            "datapoint": {
                "id": 5,
                "messages": {
                    "messages": [
                        {"role": "system", "content": "Marv_Test_10 is a factual chatbot that is also sarcastic."},
                        {"role": "user", "content": "What's the capital of France?"}
                    ]
                },
                "dataset_id": 1,
                "related_datapoints": [2, 3],
                "augmentation_type": None,
                "evaluation_type": None,
            },
            # Dont check message since it is not determinisitic - generated by the AI model
            "semantic_similarity_score": None,
            "evaluation_type": None,
            "helpful_score": None,
            "honest_score": None,
            "harmless_score": None,
            "created_at": datetime
        },
        False
    )

    invalid_model_evaluation: tuple[int, int, dict | None, ComplexModelEvaluationDTO, bool] = (
        999,  # invalid model_id
        1,  # test_datapoint_id
        None,  # semantic_similarity_model
        None,
        True
    )

    @pytest.mark.parametrize("model_id, test_datapoint_id, semantic_similarity_model, expected_properties, should_fail", [
        valid_model_evaluation,
        invalid_model_evaluation
    ])
    def test_generate_model_evaluation(self, db_setup_manager: tuple[IDataManager, Session], model_id: int, test_datapoint_id: int, semantic_similarity_model: dict | None, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                self._service.generate_model_evaluation(
                    model_id, test_datapoint_id, semantic_similarity_model, session)
        else:
            result = self._service.generate_model_evaluation(
                model_id, test_datapoint_id, semantic_similarity_model, session)
            assert len(
                result) == 1, "The function did not return exactly one result."
            assert_properties(asdict(result[0]), expected_properties)

        # Fetch all augmented datapoints
            model = test_manager.get_model_by_id(session, model_id)[0]
            augmented_datasets = [
                dataset for dataset in model.training_datasets if dataset.augmented]
            augmented_datapoints = [
                dp for dataset in augmented_datasets for dp in dataset.datapoints]

            # Fetch all related test datapoints
            test_datapoints = model.training_datasets[0].test_dataset.datapoints
            training_to_test_map = self._service._create_test_to_trainings_datapoints_mapping(
                test_datapoints)

            # Check if the correct test datapoints have been added to augmented datapoints
            for augmented_dp in augmented_datapoints:
                initial_training_id = augmented_dp.initial_datapoint_id
                if initial_training_id in training_to_test_map:
                    related_test_dps = training_to_test_map[initial_training_id]
                    for test_dp in related_test_dps:
                        assert test_dp in augmented_dp.related_datapoints, "Related test datapoints not correctly added to augmented datapoints."

            # Check if the correct augmented datapoints are added to model_eval related datapoints
            model_eval = result[0]
            related_augmented_datapoints = [
                dp for dp in augmented_datapoints if dp.initial_datapoint.id == model_eval.datapoint.id
            ]
            for related_aug_dp in related_augmented_datapoints:
                assert related_aug_dp in model_eval.datapoint.related_datapoints, "Augmented datapoint not correctly added to model_eval related datapoints."

    valid_test_datapoints = (1, False, [
        {
            'id': 5,
            'dataset_id': 1,
            'augmentation_type': None,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")]),
            'related_datapoints': [2, 3]
        },
        {
            'id': 6,
            'dataset_id': 1,
            'augmentation_type': AugmentationType.BT,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")]),
            'related_datapoints': [3]
        }
    ], False)

    invalid_test_datapoints = (INVALID_ID, False, [], True)

    @pytest.mark.parametrize("model_id, only_ids, expected_properties, should_fail", [
        valid_test_datapoints,
        invalid_test_datapoints
    ])
    def test_get_all_test_datapoints(self, db_setup_manager: tuple[IDataManager, Session], model_id: int, only_ids: bool, expected_properties: list, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                self._service.get_all_test_datapoints(
                    model_id, only_ids, session)
        else:
            result = self._service.get_all_test_datapoints(
                model_id, only_ids, session)

            for actual_val, expected_property in zip(result, expected_properties):

                assert_properties(asdict(actual_val), expected_property)

    delete_dataset_1 = [1]  # dataset_ids to delete
    delete_dataset_2 = [2]  # dataset_ids to delete

    @pytest.mark.parametrize("dataset_ids_to_delete", [
        delete_dataset_1,
        delete_dataset_2
    ])
    def test_delete_datasets(self, db_setup_manager: tuple[IDataManager, Session], dataset_ids_to_delete: list[int]):
        _, session = db_setup_manager

        # Call the function to test
        self._service.delete_datasets(dataset_ids_to_delete, session)

        for dataset_id in dataset_ids_to_delete:
            # Verify that the dataset is deleted
            deleted_dataset = session.get(Dataset, dataset_id)
            assert deleted_dataset is None, f"""Dataset with ID {
                dataset_id} was not deleted."""

            # Verify that all associated datapoints are deleted
            associated_datapoints = session.query(DataPoint).filter(
                DataPoint.dataset_id == dataset_id).all()
            assert len(associated_datapoints) == 0, f"""Datapoints for dataset with ID {
                dataset_id} were not deleted."""

            # Verify that all associated datapoint evaluations are deleted
            datapoint_ids = [dp.id for dp in associated_datapoints]
            associated_evaluations = session.query(DataPointEvaluation).filter(
                DataPointEvaluation.datapoint_id.in_(datapoint_ids)).all()
            assert len(associated_evaluations) == 0, f"""Datapoint evaluations for dataset with ID {
                dataset_id} were not deleted."""

            # Verify that the dataset is removed from any associated projects
            associated_projects = session.query(Project).filter(
                Project.datasets.any(Dataset.id == dataset_id)).all()
            assert len(associated_projects) == 0, f"""Dataset with ID {
                dataset_id} is still associated with some projects."""

            # Verify that the dataset is removed from the respective models' training datasets
            associated_models = session.query(Model).filter(
                Model.training_datasets.any(Dataset.id == dataset_id)).all()
            assert len(associated_models) == 0, f"""Dataset with ID {
                dataset_id} is still associated with some models' training datasets."""

    valid_training_datapoints = (1, [
        {
            'id': 2,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")]),
            'augmentation_type': AugmentationType.BT,
            'created_at': datetime
        },
        {
            'id': 3,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")]),
            'augmentation_type': AugmentationType.BT,
            'created_at': datetime
        },
        {
            'id': 4,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")]),
            'augmentation_type': AugmentationType.EDA,
            'created_at': datetime
        }
    ], False)

    invalid_training_datapoints = (NON_EXISTENT_ID, [], True)

    @pytest.mark.parametrize("model_id, expected_properties, should_fail", [
        valid_training_datapoints,
        invalid_training_datapoints
    ])
    def test_get_all_training_datapoints(self, db_setup_manager: IDataManager, model_id: int, expected_properties: list, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                self._service.get_all_training_datapoints(model_id, session)
        else:
            result = self._service.get_all_training_datapoints(
                model_id, session)

            for actual_val, expected_property in zip(result, expected_properties):
                assert_properties(asdict(actual_val), expected_property)

    update_evaluation_1 = (UpdateModelEvaluationDTO(
        id=1,
        evaluation_type=EvaluationType.T,
        helpful_score=9,
        honest_score=8,
        harmless_score=7,
        semantic_similarity_score=0.95
    ),
        {
        'id': 1,
        'model_id': 1,
        'datapoint': {
            'id': 1,
            'dataset_id': 2,
            'messages': MessagesContainer(messages=[
                Message(
                    role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."),
                Message(role="user", content="What's the capital of France?")
            ]),
            'related_datapoints': [],
            'augmentation_type': None,
            'initial_datapoint_id': None,
            'evaluation_type': None,
            'created_at': datetime
        },
        'messages': MessagesContainer(messages=[
            Message(
                role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."),
            Message(role="user", content="What's the capital of France?")
        ]),
        'semantic_similarity_score': 0.95,
        'evaluation_type': EvaluationType.T,
        'helpful_score': 9,
        'honest_score': 8,
        'harmless_score': 7,
        'created_at': datetime
    }
    )
    update_evaluation_2 = (
        UpdateModelEvaluationDTO(
            id=2,
            evaluation_type=EvaluationType.F,
            helpful_score=6,
            honest_score=5,
            harmless_score=4,
            semantic_similarity_score=0.85
        ),
        {
            'id': 2,
            'model_id': 1,
            'datapoint': {
                'id': 2,
                'dataset_id': 3,
                'messages': MessagesContainer(messages=[
                    Message(
                        role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."),
                    Message(role="user", content="What's the capital of France?")
                ]),
                'related_datapoints': [],
                'augmentation_type': AugmentationType.BT,
                'initial_datapoint_id': 1,
                'evaluation_type': EvaluationType.T,
                'created_at': datetime
            },
            'messages': MessagesContainer(messages=[
                Message(
                    role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."),
                Message(role="user", content="What's the capital of France?")
            ]),
            'semantic_similarity_score': 0.85,
            'evaluation_type': EvaluationType.F,
            'helpful_score': 6,
            'honest_score': 5,
            'harmless_score': 4,
            'created_at': datetime
        }
    )

    @ pytest.mark.parametrize("update_data, expected_properties", [
        update_evaluation_1,
        update_evaluation_2
    ])
    def test_update_model_evaluations(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateModelEvaluationDTO, expected_properties: dict):
        _, session = db_setup_manager

        # Call the function to test
        result = self._service.update_model_evaluations([update_data], session)

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        updated_evaluation = result[0]

        # Check the properties of the resulting entity
        assert_properties(asdict(updated_evaluation), expected_properties)

    valid_model_with_original_project = (
        GetModelsDTO(
            project_id=1,
            created_at=datetime(2023, 1, 1)
        ), [
            {
                'id': 2,
                'model_name': "Project Alpha/Model Beta",
                'version': "0",
                'original_project': {
                    'id': 1,
                    'project_name': "Project Alpha",
                    'description': "Alpha Project Description",
                    'created_at': datetime
                },
                'is_global': True,
                'created_at': datetime,
                'is_checkpoint_model': True,
                'checkpoint_step': 0
            }, {
                'id': 1,
                'model_name': "Project Beta/Model Alpha",
                'version': "0",
                'original_project': {
                    'id': 2,
                    'project_name': "Project Beta",
                    'description': "Beta Project Description",
                    'created_at': datetime
                },
                'is_global': True,
                'created_at': datetime,
                'is_checkpoint_model': False,
                'checkpoint_step': 0}], False
    )

    invalid_model_with_original_project = (
        GetModelsDTO(
            project_id=NON_EXISTENT_ID,  # Non-existent project ID
            created_at=datetime(2023, 1, 1)
        ), [], False
    )

    @ pytest.mark.parametrize("model_data, expected_properties, should_fail", [
        valid_model_with_original_project,
        invalid_model_with_original_project
    ])
    def test_filter_models_with_original_project(self, db_setup_manager: IDataManager, model_data: GetModelsDTO, expected_properties: list, should_fail: bool):
        _, session = db_setup_manager

        result = self._service.filter_models_with_original_project(
            model_data, session)
        assert len(result) == len(expected_properties), f"The function did not return the expected number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        for actual_val, expected_property in zip(result, expected_properties):
            assert_properties(asdict(actual_val), expected_property)

    valid_simple_project = (
        GetProjectsDTO(
            project_name="Alpha",
            created_at=datetime(2022, 1, 1)
        ), [{
            'id': 1,
            'project_name': "Project Alpha",
            'description': "Alpha Project Description",
            'created_at': datetime
        }], False
    )

    invalid_simple_project = (
        GetProjectsDTO(
            project_name="InvalidProjectName",
            created_at=datetime(2022, 1, 1)
        ), [], False
    )

    @ pytest.mark.parametrize("projects_data, expected_properties, should_fail", [
        valid_simple_project,
        invalid_simple_project
    ])
    def test_filter_simple_projects(self, db_setup_manager: tuple[IDataManager, Session], projects_data: GetProjectsDTO, expected_properties: list, should_fail: bool):
        _, session = db_setup_manager

        result = self._service.filter_simple_projects(
            projects_data, session)
        assert len(result) == len(expected_properties), f"The function did not return the expected number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        for actual_val, expected_property in zip(result, expected_properties):
            assert_properties(asdict(actual_val), expected_property)

    valid_remove_model_global_status = (
        1,  # Existing model ID
        [{
            'id': 1,
            'model_name': "Project Beta/Model Alpha",
            'version': "0",
            'is_global': False,
            'created_at': datetime,
            'is_checkpoint_model': False,
            'checkpoint_step': 0
        }], False
    )

    invalid_remove_model_global_status = (
        NON_EXISTENT_ID,  # Non-existent model ID
        [], True
    )

    @pytest.mark.parametrize("model_id, expected_properties, should_fail", [
        valid_remove_model_global_status,
        invalid_remove_model_global_status
    ])
    def test_remove_model_global_status(self, db_setup_manager: tuple[IDataManager, Session], model_id: int, expected_properties: list, should_fail: bool):
        _, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                self._service.remove_model_global_status(model_id, session)
        else:
            result = self._service.remove_model_global_status(
                model_id, session)
            assert len(result) == len(expected_properties), f"The function did not return the expected number of results. Expected {
                len(expected_properties)}, got {len(result)}."

            for actual_val, expected_property in zip(result, expected_properties):
                assert_properties(asdict(actual_val), expected_property)
