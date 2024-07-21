import pytest
from datetime import datetime
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from app.backend.custom_types.typedicts import Message, MessagesContainer
from app.backend.dtos.get_request import GetDataPointEvaluationsDTO, GetDatapointsByDatasetIdDTO, GetDatasetsByModelIdDTO, GetDatasetsDTO, GetModelEvalautionsDTO, GetModelsByProjectIdDTO, GetModelsDTO, GetProjectsDTO, GetTrainingRunsDTO
from app.backend.dtos.response import ComplexModelEvaluationDTO, ComplexModelEvaluationDTO
from app.backend.dtos.create_request import CreateDataPointDTO, CreateDataPointEvaluationDTO, CreateDatasetDTO, CreateModelDTO, CreateModelEvaluationDTO, CreateProjectDTO, CreateTrainingRunDTO
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO, UpdateDataPointDTO, UpdateDataPointEvaluationDTO, UpdateDatasetDTO, UpdateModelDTO, UpdateModelEvaluationDTO, UpdateProjectDTO, UpdateTrainingRunDTO
from app.backend.util.logger import Logger
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from app.backend.database.schema import AugmentationType, DatasetCategory, EvaluationType, FineTuningCompany, FineTuningModelVersions, Project, DataPoint, Dataset, Model, TrainingRun, DataPointEvaluation, ModelEvaluation, CurrentProjectData, model_dataset_association, project_model_link
from app.backend.tests.conftest import assert_properties

logger = Logger(__name__)


class TestDatabaseOperations:

    # ************************************************************************************************
    # GET DATABASE FUNCTIONS
    # ************************************************************************************************

    current_project_data_expected_properties = {
        'id': 1,
        'unfinished_progress': True,
        'current_page': "fine_tune_page",
        'save_checkpoint_models': True,
        'semantic_similarity_model': {"model": "similarity_model_v2"},
        'currently_modified_dataset_id': 2,  # dataset_alpha.id
        'selected_model_for_fine_tuning_id': 1,  # model.id
        'fine_tuning_step_counter': 5,
        'current_augmentation_configurations': [{"config": "config_value"}],
        'current_project_id': 1,  # project_alpha.id
        'current_fine_tuning_model_id': 1,  # model.id
        'current_project': {'id': 1},  # project_alpha.id
        'selected_model_for_fine_tuning': {'id': 1},  # model.id
        'currently_modified_dataset': {'id': 2},  # dataset_alpha.id
        'current_fine_tuning_model': {'id': 1},  # model.id
        'selected_statistic_models': [1],  # list of model ids
        'generated_checkpoint_models': [2],  # list of child model ids
        # list of datapoint evaluation ids
        'current_augmented_datapoint_evaluations': [1, 2]
    }

    @pytest.mark.parametrize("expected_properties", [
        current_project_data_expected_properties
    ])
    def test_get_or_create_current_project_data(self, db_setup_manager: tuple[IDataManager, Session], expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_or_create_current_project_data(session)

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        current_project_data = result[0]

        # Check the properties of the resulting entity
        assert_properties(current_project_data, expected_properties)

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
        'currently_modified_dataset_id': 2,
        'selected_model_for_fine_tuning_id': 2,
        'fine_tuning_step_counter': 10,
        'current_augmentation_configurations': [{"config": "updated_config"}],
        'current_project_id': 2,
        'current_fine_tuning_model_id': 2,
        'current_project': {'id': 2},
        'selected_model_for_fine_tuning': {'id': 2},
        'currently_modified_dataset': {'id': 2},
        'current_fine_tuning_model': {'id': 2},
        'selected_statistic_models': [2],
        'generated_checkpoint_models': [1],
        'current_augmented_datapoint_evaluations': [1]
    }

    @pytest.mark.parametrize("update_data, expected_properties", [
        (
            update_current_project_data,
            check_updated_current_project_data
        )
    ])
    def test_update_current_project_data(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateCurrentProjectDataDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_or_create_current_project_data(session)

        # Call the function to test
        result = test_manager.update_current_project_data(session, update_data)

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        updated_project_data = result[0]

        # Check the properties of the resulting entity
        assert_properties(updated_project_data, expected_properties)

    update_project_dto = UpdateProjectDTO(
        id=1,
        project_name="Updated Project Alpha",
        description="Updated Alpha Project Description",
        model_ids=[3],  # Update with new model IDs
        dataset_ids=[3]  # Update with new dataset IDs
    )
    updated_project_data_expected_properties = {
        'id': 1,
        'project_name': "Updated Project Alpha",
        'description': "Updated Alpha Project Description",
        'created_at': datetime,  # Type check for datetime
        'models': [2, 3],  # IDs of the models associated with the project
        # IDs of the datasets associated with the project
        'datasets': [1, 3],
    }

    @pytest.mark.parametrize("update_data, expected_properties", [
        (
            update_project_dto,
            updated_project_data_expected_properties
        )
    ])
    def test_update_projects(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateProjectDTO, expected_properties: dict):
        test_manager, session = db_setup_manager
        # Step 2: Call the function to test
        result = test_manager.update_projects(session, [update_data])

        # Step 3: Ensure we get the correct number of results
        assert len(result) == 1, "The function did not return exactly one result."
        updated_project = result[0]

        # Step 5: Check the properties of the resulting entity
        assert_properties(updated_project, expected_properties)

    create_project_gamma: tuple[CreateProjectDTO, dict] = (
        CreateProjectDTO(
            project_name="Project Gamma",
            description="Gamma Project Description",
            model_ids=[1, 2],  # Assuming these IDs exist in the test DB
            dataset_ids=[1, 2]  # Assuming these IDs exist in the test DB
        ),
        {
            'project_name': "Project Gamma",
            'description': "Gamma Project Description",
            'created_at': datetime,  # Type check for datetime
            # IDs of the models associated with the project
            'models': [1, 2],
            # IDs of the datasets associated with the project
            'datasets': [1, 2]
        }
    )

    create_project_delta: tuple[CreateProjectDTO, dict] = (
        CreateProjectDTO(
            project_name="Project Delta",
            description="Delta Project Description",
            model_ids=[],  # No models associated
            dataset_ids=[]  # No datasets associated
        ),
        {
            'project_name': "Project Delta",
            'description': "Delta Project Description",
            'created_at': datetime,  # Type check for datetime
            'models': [],  # No models associated with the project
            'datasets': []  # No datasets associated with the project
        }
    )

    @pytest.mark.parametrize("create_data, expected_properties", [
        create_project_gamma,
        create_project_delta
    ])
    def test_create_projects(self, db_setup_manager: tuple[IDataManager, Session], create_data: CreateProjectDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.create_projects(session, [create_data])

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        created_project = result[0]

        # Check the properties of the resulting entity
        assert_properties(created_project, expected_properties)

    update_test_dataset: tuple[UpdateDatasetDTO, dict] = (
        UpdateDatasetDTO(
            id=1,
            dataset_name="Updated Dataset Alpha",
            is_global=True,
            project_ids=[1, 2]
        ),
        {
            'id': 1,
            'dataset_name': "Project Alpha/Updated Dataset Alpha",
            'is_global': True,
            'projects': [1, 2]
        }
    )

    update_dataset_alpha: tuple[UpdateDatasetDTO, dict] = (
        UpdateDatasetDTO(
            id=2,
            dataset_name=None,  # No update to the name
            is_global=False,
            project_ids=[]
        ),
        {
            'id': 2,
            'dataset_name': "Project Beta/Dataset Beta",
            'is_global': False,
            'projects': []
        }
    )

    @pytest.mark.parametrize("update_data, expected_properties", [
        update_test_dataset,
        update_dataset_alpha
    ])
    def test_update_datasets(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateDatasetDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.update_datasets(session, [update_data])

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        updated_dataset = result[0]

        # Check the properties of the resulting entity
        assert_properties(updated_dataset, expected_properties)

    create_dataset_delta: tuple[CreateDatasetDTO, dict] = (
        CreateDatasetDTO(
            dataset_name="Dataset Delta",
            category=DatasetCategory.training,
            augmented=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",
            fine_tuning_formatting="format_v1",
            # When creating a dataset, only one original project can be set
            project_ids=[1],
            initial_dataset_ids=[1],
            test_dataset_id=2,
            datapoint_ids=[1, 2],
            is_global=True
        ),
        {
            'dataset_name': "Project Alpha/Dataset Delta",
            'category': DatasetCategory.training,
            'augmented': False,
            'fine_tuning_company': FineTuningCompany.openai,
            'fine_tuning_model': "model_v1",
            'fine_tuning_formatting': "format_v1",
            'projects': [1],
            'initial_datasets': [1],
            'test_dataset': {'id': 2},
            'datapoints': [1, 2],
            'is_global': True
        }
    )
    create_dataset_epsilon: tuple[CreateDatasetDTO, dict] = (
        CreateDatasetDTO(
            dataset_name="Dataset Epsilon",
            category=DatasetCategory.test,
            augmented=True,
            fine_tuning_company=FineTuningCompany.google,
            fine_tuning_model="model_v2",
            fine_tuning_formatting="format_v2",
            project_ids=[2],  # A dataset must belong to a project on creation
            initial_dataset_ids=[],
            test_dataset_id=None,
            datapoint_ids=[],
            is_global=False
        ),
        {
            'dataset_name': "Project Beta/Dataset Epsilon",
            'category': DatasetCategory.test,
            'augmented': True,
            'fine_tuning_company': FineTuningCompany.google,
            'fine_tuning_model': "model_v2",
            'fine_tuning_formatting': "format_v2",
            'projects': [2],  # A dataset must belong to a project on creation
            'initial_datasets': [],
            'test_dataset': None,
            'datapoints': [],
            'is_global': False
        }
    )

    @pytest.mark.parametrize("dataset_data, expected_properties", [
        create_dataset_delta,
        create_dataset_epsilon
    ])
    def test_create_datasets(self, db_setup_manager: tuple[IDataManager, Session], dataset_data: CreateDatasetDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.create_datasets(session, [dataset_data])

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        created_dataset = result[0]

        # Check the properties of the resulting entity
        assert_properties(created_dataset, expected_properties)

    update_datapoint_1 = (UpdateDataPointDTO(
        id=1,
        related_datapoint_ids=[2, 3],
        evaluation_type=EvaluationType.T
    ), {
        'id': 1,
        'related_datapoints': [2, 3],
        'evaluation_type': EvaluationType.T,
    })

    update_datapoint_2 = (UpdateDataPointDTO(
        id=2,
        related_datapoint_ids=[],
        evaluation_type=EvaluationType.F
    ), {
        'id': 2,
        'related_datapoints': [],
        'evaluation_type': EvaluationType.F,
    })

    # Test function for update_datapoints
    @pytest.mark.parametrize("update_data, expected_properties", [
        update_datapoint_1,
        update_datapoint_2

    ])
    def test_update_datapoints(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateDataPointDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.update_datapoints(session, [update_data])

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        updated_datapoint = result[0]

        # Check the properties of the resulting entity
        assert_properties(updated_datapoint, expected_properties)

    create_datapoint_1 = (
        CreateDataPointDTO(
            messages={"messages": [
                {"role": "user", "content": "Test message 1"}]},
            dataset_id=1,
            related_datapoint_ids=[1, 3],
            augmentation_type=AugmentationType.BT,
            initial_datapoint_id=2
        ), {
            'messages': {"messages": [{"role": "user", "content": "Test message 1"}]},
            'dataset': 1,
            'related_datapoints': [1, 3],
            'augmentation_type': AugmentationType.BT,
            'initial_datapoint': 2
        }
    )
    create_datapoint_2 = (
        CreateDataPointDTO(
            messages={"messages": [
                {"role": "user", "content": "Test message 2"}]},
            dataset_id=2,
            related_datapoint_ids=[],
            augmentation_type=AugmentationType.EDA,
            initial_datapoint_id=None
        ), {
            'messages': {"messages": [{"role": "user", "content": "Test message 2"}]},
            'dataset': 2,
            'related_datapoints': [],
            'augmentation_type': AugmentationType.EDA,
            'initial_datapoint': None
        }
    )

    # Test function for create_datapoints
    @pytest.mark.parametrize("create_data, expected_properties", [
        create_datapoint_1,
        create_datapoint_2
    ])
    def test_create_datapoints(self, db_setup_manager: tuple[IDataManager, Session], create_data: CreateDataPointDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.create_datapoints(session, [create_data])

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        created_datapoint = result[0]

        if created_datapoint.initial_datapoint:
            # Extra check
            assert any(
                dp.id == created_datapoint.id for dp in created_datapoint.initial_datapoint.derived_datapoints)

        # Check the properties of the resulting entity
        assert_properties(created_datapoint, expected_properties)

    create_model_delta = (
        CreateModelDTO(
            model_name="Model Delta",
            project_ids=[1],
            training_dataset_ids=[1],
            augmentation_configurations=[{"method": "EDA", "config": {}}],
            semantic_similarity_model="similarity_model_v1",
            fine_tuning_job_id="ft_job_1",
            fine_tuning_checkpoint_job_id=None,
            fine_tuned_model_id="ft_model_1",
            parent_model_id=None,
            training_run_id=1,
            is_global=True,
            is_checkpoint_model=False,
            checkpoint_step=None,
        ),
        {
            'model_name': "Project Alpha/Model Delta",
            'is_global': True,
            'augmentation_configurations': [{"method": "EDA", "config": {}}],
            'semantic_similarity_model': "similarity_model_v1",
            'fine_tuning_job_id': "ft_job_1",
            'fine_tuning_checkpoint_job_id': None,
            'fine_tuned_model_id': "ft_model_1",
            'training_datasets': [1],
            'is_checkpoint_model': False,
            'checkpoint_step': None,
            'parent_model': None,
            'version': "0"
        }
    )
    create_model_epsilon = (
        CreateModelDTO(
            model_name="Model Alpha",
            project_ids=[2],
            training_dataset_ids=[1, 2],
            augmentation_configurations=[
                {"method": "BT", "config": {"language": "es"}}],
            semantic_similarity_model="similarity_model_v2",
            fine_tuning_job_id=None,
            fine_tuning_checkpoint_job_id="ft_checkpoint_job_1",
            fine_tuned_model_id=None,
            parent_model_id=1,
            training_run_id=2,
            is_global=False,
            is_checkpoint_model=True,
            checkpoint_step=10,
        ),
        {
            'model_name': "Project Beta/Model Alpha",
            'is_global': False,
            'augmentation_configurations': [{"method": "BT", "config": {"language": "es"}}],
            'semantic_similarity_model': "similarity_model_v2",
            'fine_tuning_job_id': None,
            'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_1",
            'fine_tuned_model_id': None,
            'training_datasets': [1, 2],
            'is_checkpoint_model': True,
            'checkpoint_step': 10,
            'parent_model': {'id': 1},
            'version': "2"
        }
    )

    # Test function for create_models
    @pytest.mark.parametrize("create_data, expected_properties", [
        create_model_delta,
        create_model_epsilon
    ])
    def test_create_models(self, db_setup_manager: tuple[IDataManager, Session], create_data: CreateModelDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.create_models(session, [create_data])

        # Ensure we get the correct number of results
        assert len(result) == 1, "The function did not return exactly one result."
        created_model = result[0]

        if created_model.parent_model:
            # Extra check
            assert any(
                dp.id == created_model.id for dp in created_model.parent_model.child_models)

        # Check the properties of the resulting entity
        assert_properties(created_model, expected_properties)

    # Exists in project id 1 as unoriginal model
    model_name_exists_1 = (
        "Model Alpha",
        1,  # project_id
        False  # expected result
    )
    # Exists in project id 1 as original model
    model_name_exists_2 = (
        "Model Beta",
        1,  # project_id
        True  # expected result
    )
    # Does not exist
    model_name_exists_3 = (
        "Nonexistent Model Name",
        1,  # project_id
        False  # expected result
    )

    @pytest.mark.parametrize("model_name, project_id, expected_result", [
        model_name_exists_1,
        model_name_exists_2,
        model_name_exists_3,
    ])
    def test_check_if_model_name_exists_in_specific_project(self, db_setup_manager: tuple[IDataManager, Session], model_name: str, project_id: int, expected_result: bool):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.check_if_model_name_exists_in_specific_project(
            session, model_name, project_id)

        assert_properties(result, expected_result)

    # Exists in project id 1 as original dataset
    dataset_name_exists_1 = (
        "Dataset Alpha",
        1,  # project_id
        True  # expected result
    )
    # Exists in project id 1 as unoriginal dataset
    dataset_name_exists_2 = (
        "Dataset Beta",
        1,  # project_id
        False  # expected result
    )
    # Does not exist
    dataset_name_exists_3 = (
        "Nonexistent Dataset Name",
        1,  # project_id
        False  # expected result
    )

    @pytest.mark.parametrize("dataset_name, project_id, expected_result", [
        dataset_name_exists_1,
        dataset_name_exists_2,
        dataset_name_exists_3,
    ])
    def test_check_if_dataset_name_exists_in_specific_project(self, db_setup_manager: tuple[IDataManager, Session], dataset_name: str, project_id: int, expected_result: bool):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.check_if_dataset_name_exists_in_specific_project(
            session, dataset_name, project_id)

        assert_properties(result, expected_result)

    delete_model_1 = [1]  # model_ids to delete
    delete_model_2 = [2]  # model_ids to delete

    @pytest.mark.parametrize("model_ids_to_delete", [
        delete_model_1,
        delete_model_2
    ])
    def test_delete_models(self, db_setup_manager: tuple[IDataManager, Session], model_ids_to_delete: list[int]):
        test_manager, session = db_setup_manager

        # Call the function to test
        test_manager.delete_models(session, model_ids_to_delete)

        for model_id in model_ids_to_delete:
            # Verify that the model is deleted
            deleted_model = session.get(Model, model_id)
            assert deleted_model is None, f"""Model with ID {
                model_id} was not deleted."""

            # Verify that the training run is deleted
            training_run = session.query(TrainingRun).filter(
                TrainingRun.model_id == model_id).first()
            assert training_run is None, f"""Training run for model with ID {
                model_id} was not deleted."""

            # Verify that the project_model_link entries are deleted
            project_model_link_entries = session.query(project_model_link).filter(
                project_model_link.c.model_id == model_id).all()
            assert not project_model_link_entries, f"""Project model link entries for model with ID {
                model_id} were not deleted."""

            # Verify that the model evaluations are deleted
            model_evaluations = session.query(ModelEvaluation).filter(
                ModelEvaluation.model_id == model_id).all()
            assert not model_evaluations, f"""Model evaluations for model with ID {
                model_id} were not deleted."""

            # Verify that the model and child models are removed from current_project_data
            current_project_data_entries = session.query(CurrentProjectData).filter(
                (CurrentProjectData.selected_model_for_fine_tuning_id == model_id) |
                (CurrentProjectData.current_fine_tuning_model_id == model_id) |
                (CurrentProjectData.generated_checkpoint_models.any(Model.id == model_id)) |
                (CurrentProjectData.selected_statistic_models.any(Model.id == model_id))
            ).all()
            assert not current_project_data_entries, f"""Model with ID {
                model_id} or its child models were not removed from current_project_data."""

            # Verify that all child models are deleted
            child_models = session.query(Model).filter(
                Model.parent_model_id == model_id).all()
            assert not child_models, f"""Child models for model with ID {
                model_id} were not deleted."""

    delete_dataset_1 = [1]  # dataset_ids to delete
    delete_dataset_2 = [2]  # dataset_ids to delete

    @pytest.mark.parametrize("dataset_ids_to_delete", [
        delete_dataset_1,
        delete_dataset_2
    ])
    def test_delete_datasets(self, db_setup_manager: tuple[IDataManager, Session], dataset_ids_to_delete: list[int]):
        test_manager, session = db_setup_manager

        # Call the function to test
        test_manager.delete_datasets(session, dataset_ids_to_delete)

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

    update_model_1 = (UpdateModelDTO(
        id=1,
        model_name="Updated Model 1",
        project_ids=[],
        is_global=True,
        training_dataset_ids=[],
        semantic_similarity_model="updated_similarity_model",
        fine_tuning_job_id="updated_job_id_1",
        fine_tuning_checkpoint_job_id="updated_checkpoint_id_1",
        fine_tuned_model_id="updated_fine_tuned_model_1",
        augmentation_configurations=[
            {"config": "updated_config"}, {"config": "updated_config_1"}]
    ), {
        'id': 1,
        'model_name': "Project Beta/Updated Model 1",
        'is_global': True,
        'training_datasets': [],
        'semantic_similarity_model': "updated_similarity_model",
        'fine_tuning_job_id': "updated_job_id_1",
        'fine_tuning_checkpoint_job_id': "updated_checkpoint_id_1",
        'fine_tuned_model_id': "updated_fine_tuned_model_1",
        'augmentation_configurations': [{"config": "updated_config"}, {"config": "updated_config_1"}],
        'projects': [2],
    })

    update_model_2 = (UpdateModelDTO(
        id=2,
        model_name="Updated Model 2",
        project_ids=[2],
        is_global=False,
        training_dataset_ids=[2, 3],
        semantic_similarity_model="",
        fine_tuning_job_id="",
        fine_tuning_checkpoint_job_id="",
        fine_tuned_model_id="",
        augmentation_configurations=[]
    ), {
        'id': 2,
        'model_name': "Project Alpha/Updated Model 2",
        'is_global': False,
        'training_datasets': [2, 3],
        'semantic_similarity_model': None,
        'fine_tuning_job_id': None,
        'fine_tuning_checkpoint_job_id': None,
        'fine_tuned_model_id': None,
        'augmentation_configurations': [],
        'projects': [1, 2],
    })

    @pytest.mark.parametrize("update_data, expected_properties", [
        update_model_1,
        update_model_2
    ])
    def test_update_models(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateModelDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.update_models(session, [update_data])

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        updated_model = result[0]

        # Check the properties of the resulting entity
        assert_properties(updated_model, expected_properties)

        # Verify project associations
        current_project_ids = [
            project.id for project in updated_model.projects]
        assert sorted(current_project_ids) == sorted(expected_properties['projects']), \
            f"Project IDs for model {updated_model.id} do not match. Expected {
                expected_properties['projects']}, got {current_project_ids}"

        # Verify training datasets
        current_training_dataset_ids = [
            dataset.id for dataset in updated_model.training_datasets]
        assert sorted(current_training_dataset_ids) == sorted(expected_properties['training_datasets']), \
            f"Training dataset IDs for model {updated_model.id} do not match. Expected {
                expected_properties['training_datasets']}, got {current_training_dataset_ids}"

        # Verify that project_model_link entries are deleted if the project is removed
        remaining_project_links = session.query(project_model_link).filter(
            project_model_link.c.model_id == updated_model.id).all()
        remaining_project_ids = [
            link.project_id for link in remaining_project_links]
        assert sorted(remaining_project_ids) == sorted(expected_properties['projects']), \
            f"Project associations for model {updated_model.id} were not updated correctly. Expected {
                expected_properties['projects']}, got {remaining_project_ids}"

        # Verify that model_dataset_association entries are deleted if the dataset is removed
        remaining_dataset_links = session.query(model_dataset_association).filter(
            model_dataset_association.c.model_id == updated_model.id).all()
        remaining_dataset_ids = [
            link.dataset_id for link in remaining_dataset_links]
        assert sorted(remaining_dataset_ids) == sorted(expected_properties['training_datasets']), \
            f"Dataset associations for model {updated_model.id} were not updated correctly. Expected {
                expected_properties['training_datasets']}, got {remaining_dataset_ids}"

    # Fails because of Unique constraint for model_id / datapoint_id
    create_evaluation_1 = (CreateModelEvaluationDTO(
        model_id=1,
        datapoint_id=1,
        messages={"role": "assistant", "content": "Evaluation message 1"},
        semantic_similarity_score=0.95,
        evaluation_type=EvaluationType.T,
        helpful_score=9,
        honest_score=8,
        harmless_score=10
    ), {
        'model_id': 1,
        'datapoint_id': 1,
        'messages': {"role": "assistant", "content": "Evaluation message 1"},
        'semantic_similarity_score': 0.95,
        'evaluation_type': EvaluationType.T,
        'helpful_score': 9,
        'honest_score': 8,
        'harmless_score': 10,
    }, True)

    create_evaluation_2 = (CreateModelEvaluationDTO(
        model_id=2,
        datapoint_id=2,
        messages={"role": "assistant", "content": "Evaluation message 2"},
        semantic_similarity_score=0.85,
        evaluation_type=EvaluationType.F,
        helpful_score=7,
        honest_score=6,
        harmless_score=5
    ), {
        'model_id': 2,
        'datapoint_id': 2,
        'messages': {"role": "assistant", "content": "Evaluation message 2"},
        'semantic_similarity_score': 0.85,
        'evaluation_type': EvaluationType.F,
        'helpful_score': 7,
        'honest_score': 6,
        'harmless_score': 5,
    }, False)

    @pytest.mark.parametrize("create_data, expected_properties, should_fail", [
        create_evaluation_1,
        create_evaluation_2
    ])
    def test_create_model_evaluations(self, db_setup_manager: tuple[IDataManager, Session], create_data: CreateModelEvaluationDTO, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            # Expecting a failure due to unique constraint violation
            with pytest.raises(Exception):
                test_manager.create_model_evaluations(session, [create_data])
            session.rollback()  # Rollback the session to clean up the state
        else:
            # Call the function to test
            result = test_manager.create_model_evaluations(
                session, [create_data])

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            created_evaluation = result[0]

            # Check the properties of the resulting entity
            assert_properties(created_evaluation, expected_properties)

    update_evaluation_1 = (
        UpdateModelEvaluationDTO(
            id=1,
            evaluation_type=EvaluationType.T,
            helpful_score=9,
            honest_score=8,
            harmless_score=7,
            semantic_similarity_score=0.95
        ),
        {
            'id': 1,
            'evaluation_type': EvaluationType.T,
            'helpful_score': 9,
            'honest_score': 8,
            'harmless_score': 7,
            'semantic_similarity_score': 0.95
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
            'evaluation_type': EvaluationType.F,
            'helpful_score': 6,
            'honest_score': 5,
            'harmless_score': 4,
            'semantic_similarity_score': 0.85
        }
    )

    # Test function for update_model_evaluations
    @pytest.mark.parametrize("update_data, expected_properties", [
        update_evaluation_1,
        update_evaluation_2
    ])
    def test_update_model_evaluations(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateModelEvaluationDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.update_model_evaluations(session, [update_data])

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        updated_evaluation = result[0]

        # Check the properties of the resulting entity
        assert_properties(updated_evaluation, expected_properties)

    create_training_run_1 = (
        CreateTrainingRunDTO(
            model_id=1,
            fine_tuning_model="model_v1",
            epochs=10,
            learning_rate_multiplier=0.01,
            batch_size=32,
            seed=42
        ),
        {
            'model_id': 1,
            'fine_tuning_model': "model_v1",
            'epochs': 10,
            'learning_rate_multiplier': 0.01,
            'batch_size': 32,
            'seed': 42
        },
        True
    )

    create_training_run_2 = (
        CreateTrainingRunDTO(
            model_id=3,
            fine_tuning_model="model_v2",
            epochs=10,
            learning_rate_multiplier=0.02,
            batch_size=1,
            seed=123
        ),
        {
            'model_id': 3,
            'fine_tuning_model': "model_v2",
            'epochs': 10,
            'learning_rate_multiplier': 0.02,
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
        test_manager, session = db_setup_manager

        if should_fail:
            # Expecting a failure due to unique constraint violation
            with pytest.raises(Exception):
                test_manager.create_training_runs(session, [create_data])
            session.rollback()  # Rollback the session to clean up the state
        else:
            # Call the function to test
            result = test_manager.create_training_runs(
                session, [create_data])

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            created_training_run = result[0]

            # Check the properties of the resulting entity
            assert_properties(created_training_run, expected_properties)

    get_projects_data_1 = (GetProjectsDTO(
        project_name="Project Alpha",
        created_at=datetime(2023, 1, 1)
    ), [
        {
            'project_name': "Project Alpha",
            'description': "Alpha Project Description",
            'created_at': datetime,
            'models': [1, 2],
            'datasets': [1, 2]
        }
    ])

    get_projects_data_2 = (GetProjectsDTO(
        created_at=datetime(2022, 1, 1)
    ), [
        {
            'project_name': "Project Alpha",
            'description': "Alpha Project Description",
            'created_at': datetime,
            'models': [1, 2],
            'datasets': [1, 2]
        },
        {
            'project_name': "Project Beta",
            'description': "Beta Project Description",
            'created_at': datetime,
            'models': [1, 2, 3],
            'datasets': [1, 2, 3]
        }
    ])

    get_projects_data_3 = (GetProjectsDTO(
        created_at=datetime(2024, 1, 1)
    ), [])

    # Test function for get_all_projects
    @pytest.mark.parametrize("project_data, expected_properties", [
        get_projects_data_1,
        get_projects_data_2,
    ])
    def test_get_all_projects(self, db_setup_manager: tuple[IDataManager, Session], project_data: GetProjectsDTO, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_all_projects(session, project_data)

        # Ensure we get the correct number of results
        assert len(result) == len(expected_properties), f"The function did not return the expected number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for project, expected in zip(result, expected_properties):
            assert_properties(project, expected)

    get_models_data_1: tuple[GetModelsDTO, list[dict]] = (GetModelsDTO(
        model_name="Project Beta/Model Alpha",
        created_at=datetime(2023, 1, 1),
        project_id=2,
        is_global=True,
        version="0"
    ), [
        {
            'model_name': "Project Beta/Model Alpha",
            'created_at': datetime,
            'projects': [1, 2],
            'is_global': True,
            'version': "0"
        }
    ])

    get_models_data_2: tuple[GetModelsDTO, list[dict]] = (GetModelsDTO(
        created_at=datetime(2023, 1, 2),
        is_checkpoint_model=True
    ), [
        {
            'model_name': "Project Alpha/Model Beta",
            'created_at': datetime,
            'projects': [1, 2],
            'is_global': True,
            'is_checkpoint_model': True,
            'version': "0"
        }
    ])

    get_models_data_3: tuple[GetModelsDTO, list[dict]] = (GetModelsDTO(
        model_name="Project Beta/Model Alpha",
        created_at=datetime(2023, 1, 3),
        fine_tuning_job_id="ft_job_id_3",
        exlude_project_id=1
    ), [
        {
            'model_name': "Project Beta/Model Alpha",
            'created_at': datetime,
            'projects': [2],
            'is_checkpoint_model': False,
            'version': "1"
        }
    ])

    get_models_data_4: tuple[GetModelsDTO, list[dict]] = (GetModelsDTO(
        model_name=None,
        created_at=None,
        version=None,
        project_id=None,
        is_global=None,
        exlude_project_id=None,
        is_checkpoint_model=None,
        only_original_models=True,
        fine_tuning_job_id=None
    ), get_models_data_1[1] + get_models_data_2[1] + get_models_data_3[1])

    # Test function for get_all_models
    @pytest.mark.parametrize("model_data, expected_properties", [
        get_models_data_1,
        get_models_data_2,
        get_models_data_3,
        get_models_data_4,
    ])
    def test_get_all_models(self, db_setup_manager: tuple[IDataManager, Session], model_data: GetModelsDTO, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_all_models(session, model_data)

        # Ensure we get the correct number of results
        assert len(result) == len(expected_properties), f"The function did not return the expected number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for model, expected in zip(result, expected_properties):
            assert_properties(model, expected)

    get_models_data_1: tuple[GetModelsDTO, list[dict]] = (GetModelsDTO(
        model_name="Project Alpha/Model Beta",
        created_at=datetime(2023, 1, 1),
        only_original_models=True
    ), [
        {
            'model': {
                'model_name': "Project Alpha/Model Beta",
                'created_at': datetime,
                'is_global': True,
                'version': "0",
                'is_checkpoint_model': True,
                'fine_tuning_job_id': "ft_job_id_2"
            },
            'project': {
                'id': 1,
                'project_name': "Project Alpha"
            }
        }
    ])

    get_models_data_2: tuple[GetModelsDTO, list[dict]] = (GetModelsDTO(
        model_name="Project Beta/Model Alpha",
        only_original_models=True
    ), [
        {
            'model': {
                'model_name': "Project Beta/Model Alpha",
                'created_at': datetime,
                'is_global': True,
                'version': "0",
                'is_checkpoint_model': False,
                'fine_tuning_job_id': "ft_job_id_1"
            },
            'project': {
                'id': 2,
                'project_name': "Project Beta"
            }
        },
        {
            'model': {
                'model_name': "Project Beta/Model Alpha",
                'created_at': datetime,
                'is_global': True,
                'version': "1",
                'is_checkpoint_model': False,
                'fine_tuning_job_id': "ft_job_id_3"
            },
            'project': {
                'id': 2,
                'project_name': "Project Beta"
            }
        }
    ])

    get_models_data_2: tuple[GetModelsDTO, list[dict]] = (GetModelsDTO(
        model_name="Project Beta/Model Alpha",
        only_original_models=True,
        created_at=datetime(2024, 1, 1)
    ), [])

    @pytest.mark.parametrize("model_data, expected_properties", [
        get_models_data_1,
        get_models_data_2,
    ])
    def test_get_all_models_with_original_project(self, db_setup_manager: tuple[IDataManager, Session], model_data: GetModelsDTO, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_all_models_with_original_project(
            session, model_data)

        # Ensure we get the correct number of results
        assert len(result) == len(expected_properties), f"Expected {
            len(expected_properties)} models, got {len(result)}."

        # Check the properties of the resulting entities
        for (model, project), expected in zip(result, expected_properties):
            assert_properties(model, expected['model'])
            assert_properties(project, expected['project'])

    remove_model_data_1 = (1, {  # model_id = 1
        'is_global': False,
        'projects': [2]  # Only the original project should remain
    })

    remove_model_data_2 = (2, {  # model_id = 2
        'is_global': False,
        'projects': [1]  # Only the original project should remain
    })

    @pytest.mark.parametrize("model_id, expected_properties", [
        remove_model_data_1,
        remove_model_data_2
    ])
    def test_remove_model_global_status(self, db_setup_manager: tuple[IDataManager, Session], model_id: int, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        test_manager.remove_model_global_status(session, model_id)

        # Fetch the updated model
        updated_model = session.get(Model, model_id)

        # Check the properties of the resulting entity
        assert_properties(updated_model, expected_properties)

        # Verify that the model is removed from all projects that are not the original project
        original_project_id = test_manager.get_original_project(
            session, model_id)
        remaining_project_ids = [
            assoc.project_id for assoc in test_manager._get_current_project_associations(session, model_id)
        ]

        assert remaining_project_ids == [original_project_id], \
            f"Model {model_id} is still associated with projects other than the original. Expected {
                [original_project_id]}, got {remaining_project_ids}"

    get_original_project_1 = (1,  # model_id = 1
                              2  # Expected original project_id
                              )

    get_original_project_2 = (2,  # model_id = 2
                              1  # Expected original project_id
                              )

    @pytest.mark.parametrize("model_id, expected_project_id", [
        get_original_project_1,
        get_original_project_2
    ])
    def test_get_original_project(self, db_setup_manager: tuple[IDataManager, Session], model_id: int, expected_project_id: int):
        test_manager, session = db_setup_manager

        # Call the function to test
        original_project_id = test_manager.get_original_project(
            session, model_id)

        # Check the properties of the resulting entity
        assert_properties(original_project_id, expected_project_id)

    # Will fail due to unique constraingt for model_id / datapoint_id
    create_evaluation_1 = (CreateDataPointEvaluationDTO(
        datapoint_id=1,
        model_id=1,
        coherence_score=8,
        relevance_score=7,
        semantic_similarity_score=0.9
    ), {
        'datapoint_id': 1,
        'model_id': 1,
        'coherence_score': 8,
        'relevance_score': 7,
        'semantic_similarity_score': 0.9,
    }, True)

    create_evaluation_2 = (CreateDataPointEvaluationDTO(
        datapoint_id=4,
        model_id=2,
        coherence_score=9,
        relevance_score=8,
        semantic_similarity_score=0.85
    ), {
        'datapoint_id': 4,
        'model_id': 2,
        'coherence_score': 9,
        'relevance_score': 8,
        'semantic_similarity_score': 0.85,
    }, False)

    @pytest.mark.parametrize("create_data, expected_properties, should_fail", [
        create_evaluation_1,
        create_evaluation_2
    ])
    def test_create_datapoint_evaluations(self, db_setup_manager: tuple[IDataManager, Session], create_data: CreateDataPointEvaluationDTO, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            # Expecting a failure due to unique constraint violation
            with pytest.raises(Exception):
                test_manager.create_datapoint_evaluations(
                    session, [create_data])
            session.rollback()  # Rollback the session to clean up the state
        else:
            # Call the function to test
            result = test_manager.create_datapoint_evaluations(
                session, [create_data])

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            created_evaluation = result[0]

            # Check the properties of the resulting entity
            assert_properties(created_evaluation, expected_properties)

    update_evaluation_1 = (UpdateDataPointEvaluationDTO(
        id=1,
        coherence_score=9,
        relevance_score=8,
        semantic_similarity_score=0.95
    ), {
        'id': 1,
        'coherence_score': 9,
        'relevance_score': 8,
        'semantic_similarity_score': 0.95,
    })

    update_evaluation_2 = (UpdateDataPointEvaluationDTO(
        id=2,
        coherence_score=7,
        relevance_score=6,
        semantic_similarity_score=0.85
    ), {
        'id': 2,
        'coherence_score': 7,
        'relevance_score': 6,
        'semantic_similarity_score': 0.85,
    })

    @pytest.mark.parametrize("update_data, expected_properties", [
        update_evaluation_1,
        update_evaluation_2
    ])
    def test_update_datapoint_evaluations(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateDataPointEvaluationDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.update_datapoint_evaluations(session, [
                                                           update_data])

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        updated_evaluation = result[0]

        # Check the properties of the resulting entity
        assert_properties(updated_evaluation, expected_properties)

    filter_data_1: tuple[GetDataPointEvaluationsDTO, list[dict]] = (GetDataPointEvaluationsDTO(
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

    filter_data_2: tuple[GetDataPointEvaluationsDTO, list[dict]] = (GetDataPointEvaluationsDTO(
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

    filter_data_3: tuple[GetDataPointEvaluationsDTO, list[dict]] = (GetDataPointEvaluationsDTO(
        model_id=1,
        relevance_score=9
    ), [])

    @pytest.mark.parametrize("filter_data, expected_properties", [
        filter_data_1,
        filter_data_2,
        filter_data_3
    ])
    def test_get_all_datapoint_evaluations(self, db_setup_manager: tuple[IDataManager, Session], filter_data: GetDataPointEvaluationsDTO, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_all_datapoint_evaluations(
            session, filter_data)

        # Ensure the correct number of results
        assert len(result) == len(expected_properties), f"The function did not return the correct number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for evaluation, expected in zip(result, expected_properties):
            assert_properties(evaluation, expected)

    filter_data_1: tuple[GetModelEvalautionsDTO, list[dict]] = (GetModelEvalautionsDTO(
        model_id=1,
        helpful_score=7
    ), [
        {
            'model_id': 1,
            'datapoint_id': 1,
            'evaluation_type': EvaluationType.T,
            'helpful_score': 8,
            'honest_score': 9,
            'harmless_score': 10,
            'semantic_similarity_score': 0.5
        },
        {
            'model_id': 1,
            'datapoint_id': 2,
            'evaluation_type': EvaluationType.F,
            'helpful_score': 7,
            'honest_score': 8,
            'harmless_score': 9,
            'semantic_similarity_score': 1.0
        }
    ])

    filter_data_2: tuple[GetModelEvalautionsDTO, list[dict]] = (GetModelEvalautionsDTO(
        model_id=1,
        datapoint_id=2,
        helpful_score=5,
        semantic_similarity_score=0.6
    ), [
        {
            'model_id': 1,
            'datapoint_id': 2,
            'evaluation_type': EvaluationType.F,
            'helpful_score': 7,
            'honest_score': 8,
            'harmless_score': 9,
            'semantic_similarity_score': 1.0
        }
    ])

    filter_data_3: tuple[GetModelEvalautionsDTO, list[dict]] = (GetModelEvalautionsDTO(
        model_id=1,
        evaluation_type=EvaluationType.F
    ), [
        {
            'model_id': 1,
            'datapoint_id': 2,
            'evaluation_type': EvaluationType.F,
            'helpful_score': 7,
            'honest_score': 8,
            'harmless_score': 9,
            'semantic_similarity_score': 1.0
        }
    ])

    filter_data_4: tuple[GetModelEvalautionsDTO, list[dict]] = (GetModelEvalautionsDTO(
        model_id=1,
        datapoint_id=10,
        evaluation_type=EvaluationType.T,
        semantic_similarity_score=0.6
    ), [])

    @pytest.mark.parametrize("filter_data, expected_properties", [
        filter_data_1,
        filter_data_2,
        filter_data_3,
        filter_data_4
    ])
    def test_get_all_model_evaluations(self, db_setup_manager: tuple[IDataManager, Session], filter_data: GetModelEvalautionsDTO, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_all_model_evaluations(session, filter_data)

        # Ensure the correct number of results
        assert len(result) == len(expected_properties), f"The function did not return the correct number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for evaluation, expected in zip(result, expected_properties):
            assert_properties(evaluation, expected)

    get_datasets_data_1: tuple[GetDatasetsDTO, list[dict]] = (GetDatasetsDTO(
        initial_dataset_ids=[2],
        augmented=False,
        is_global=False,
        category=DatasetCategory.training
    ), [
        {
            'dataset_name': "Project Beta/Dataset Gamma",
            'augmented': False,
            'category': DatasetCategory.training,
            'initial_datasets': [2],
            'projects': [2],
            'is_global': False
        }
    ])

    get_datasets_data_2: tuple[GetDatasetsDTO, list[dict]] = (GetDatasetsDTO(
        exlude_project_id=1
    ), [
        {
            'dataset_name': "Project Beta/Dataset Beta",
            'augmented': False,
            'category': DatasetCategory.training,
            'initial_datasets': [],
            'projects': [1, 2],
            'is_global': False
        },
        {
            'dataset_name': "Project Beta/Dataset Gamma",
            'augmented': False,
            'category': DatasetCategory.training,
            'initial_datasets': [2],
            'projects': [2],
            'is_global': False
        }
    ])

    get_datasets_data_3: tuple[GetDatasetsDTO, list[dict]] = (GetDatasetsDTO(
        exlude_project_id=2,
        initial_dataset_ids=[2]
    ), [])

    get_datasets_data_4: tuple[GetDatasetsDTO, list[dict]] = (GetDatasetsDTO(
        project_id=1,
        exlude_project_id=2,
        initial_dataset_ids=[],
        category=DatasetCategory.training
    ), [
        {
            'dataset_name': "Project Alpha/Dataset Alpha",
            'augmented': False,
            'category': DatasetCategory.training,
            'initial_datasets': [],
            'fine_tuning_company': FineTuningCompany.openai,
            'projects': [1, 2],
            'is_global': False
        }
    ])

    @pytest.mark.parametrize("filter_data, expected_properties", [
        get_datasets_data_1,
        get_datasets_data_2,
        get_datasets_data_3,
        get_datasets_data_4
    ])
    def test_get_all_datasets(self, db_setup_manager: tuple[IDataManager, Session], filter_data: GetDatasetsDTO, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_all_datasets(session, filter_data)

        # Ensure the correct number of results
        assert len(result) == len(expected_properties), f"The function did not return the correct number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for dataset, expected in zip(result, expected_properties):
            assert_properties(dataset, expected)

    # Define test data and expected properties
    get_training_runs_data_1: tuple[GetTrainingRunsDTO, list[dict]] = (GetTrainingRunsDTO(
        model_id=1,
        seed=42,
        epochs=10,
        learning_rate_multiplier=0.01
    ), [
        {
            'model_id': 1,
            'epochs': 10,
            'learning_rate_multiplier': 0.01,
            'batch_size': 32,
            'seed': 42,
            'fine_tuning_model': "fine_tuning_model_1"
        }
    ])

    get_training_runs_data_2: tuple[GetTrainingRunsDTO, list[dict]] = (GetTrainingRunsDTO(
        project_id=2,
        seed=43,
        epochs=20,
        batch_size=64
    ), [
        {
            'model_id': 2,
            'epochs': 20,
            'learning_rate_multiplier': 0.02,
            'batch_size': 64,
            'seed': 43,
            'fine_tuning_model': "fine_tuning_model_2"
        }
    ])

    get_training_runs_data_3: tuple[GetTrainingRunsDTO, list[dict]] = (GetTrainingRunsDTO(
        model_id=1,
        seed=42,
        epochs=10,
        fine_tuning_model="fine_tuning_model_1"
    ), [
        {
            'model_id': 1,
            'epochs': 10,
            'learning_rate_multiplier': 0.01,
            'batch_size': 32,
            'seed': 42,
            'fine_tuning_model': "fine_tuning_model_1"
        }
    ])

    get_training_runs_data_4: tuple[GetTrainingRunsDTO, list[dict]] = (GetTrainingRunsDTO(
        model_id=1,
        seed=43,
        epochs=30,
        fine_tuning_model="fine_tuning_model_3"
    ), [])

    @pytest.mark.parametrize("filter_data, expected_properties", [
        get_training_runs_data_1,
        get_training_runs_data_2,
        get_training_runs_data_3,
        get_training_runs_data_4
    ])
    def test_get_all_training_runs(self, db_setup_manager: tuple[IDataManager, Session], filter_data: GetTrainingRunsDTO, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_all_training_runs(session, filter_data)

        # Ensure the correct number of results
        assert len(result) == len(expected_properties), f"The function did not return the correct number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for training_run, expected in zip(result, expected_properties):
            assert_properties(training_run, expected)

    update_training_run_1 = (UpdateTrainingRunDTO(
        id=1,
        epochs=15,
        learning_rate_multiplier=0.015,
        batch_size=48,
        seed=45
    ), {
        'id': 1,
        'epochs': 15,
        'learning_rate_multiplier': 0.015,
        'batch_size': 48,
        'seed': 45
    })

    update_training_run_2 = (UpdateTrainingRunDTO(
        id=2,
        epochs=25,
        learning_rate_multiplier=0.025,
        batch_size=72,
        seed=50
    ), {
        'id': 2,
        'epochs': 25,
        'learning_rate_multiplier': 0.025,
        'batch_size': 72,
        'seed': 50
    })

    update_training_run_3 = (UpdateTrainingRunDTO(
        id=1,
        epochs=10,
        learning_rate_multiplier=None,
        batch_size=None,
        seed=None
    ), {
        'id': 1,
        'epochs': 10,
        'learning_rate_multiplier': 0.01,
        'batch_size': 32,
        'seed': 42
    })

    update_training_run_4 = (UpdateTrainingRunDTO(
        id=2,
        epochs=None,
        learning_rate_multiplier=0.02,
        batch_size=64,
        seed=43
    ), {
        'id': 2,
        'epochs': 20,
        'learning_rate_multiplier': 0.02,
        'batch_size': 64,
        'seed': 43
    })

    @pytest.mark.parametrize("update_data, expected_properties", [
        update_training_run_1,
        update_training_run_2,
        update_training_run_3,
        update_training_run_4
    ])
    def test_update_training_runs(self, db_setup_manager: tuple[IDataManager, Session], update_data: UpdateTrainingRunDTO, expected_properties: dict):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.update_training_runs(session, [update_data])

        # Ensure we get exactly one result
        assert len(result) == 1, "The function did not return exactly one result."
        updated_training_run = result[0]

        # Check the properties of the resulting entity
        assert_properties(updated_training_run, expected_properties)

    model_filter_1: tuple[GetModelsByProjectIdDTO, list[dict]] = (GetModelsByProjectIdDTO(
        project_id=1,
        name="Alpha",
        version="0"
    ), [{
        'id': 1,
        'model_name': "Project Beta/Model Alpha",
        'semantic_similarity_model': "similarity_model",
        'version': "0",
        'fine_tuning_job_id': "ft_job_id_1",
        'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_id_1",
        'fine_tuned_model_id': FineTuningModelVersions.openai.value[0],
        'uuid': "parent_uuid",
        'is_global': True,
        'is_checkpoint_model': False,
        'checkpoint_step': 0,
        'created_at': datetime(2023, 1, 1),
        'projects': [1, 2]
    }, {
        'id': 2,
        'model_name': "Project Alpha/Model Beta",
        'semantic_similarity_model': "child_similarity_model",
        'version': "0",
        'fine_tuning_job_id': "ft_job_id_2",
        'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_id_2",
        'fine_tuned_model_id': "ft_model_id_2",
        'uuid': "child_uuid",
        'is_global': True,
        'is_checkpoint_model': True,
        'checkpoint_step': 0,
        'created_at': datetime(2023, 1, 2),
        'projects': [1, 2]
    }])

    model_filter_2: tuple[GetModelsByProjectIdDTO, list[dict]] = (GetModelsByProjectIdDTO(
        project_id=2,
        name="Alpha",
        version="0"
    ), [{
        'id': 1,
        'model_name': "Project Beta/Model Alpha",
        'semantic_similarity_model': "similarity_model",
        'version': "0",
        'fine_tuning_job_id': "ft_job_id_1",
        'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_id_1",
        'fine_tuned_model_id': FineTuningModelVersions.openai.value[0],
        'uuid': "parent_uuid",
        'is_global': True,
        'is_checkpoint_model': False,
        'checkpoint_step': 0,
        'created_at': datetime(2023, 1, 1),
        'projects': [1, 2]
    }, {
        'id': 2,
        'model_name': "Project Alpha/Model Beta",
        'semantic_similarity_model': "child_similarity_model",
        'version': "0",
        'fine_tuning_job_id': "ft_job_id_2",
        'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_id_2",
        'fine_tuned_model_id': "ft_model_id_2",
        'uuid': "child_uuid",
        'is_global': True,
        'is_checkpoint_model': True,
        'checkpoint_step': 0,
        'created_at': datetime(2023, 1, 2),
        'projects': [1, 2]
    }, {
        'id': 3,
        'model_name': "Project Beta/Model Alpha",
        'semantic_similarity_model': "child_2_similarity_model",
        'version': "1",
        'fine_tuning_job_id': "ft_job_id_3",
        'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_id_3",
        'fine_tuned_model_id': "ft_model_id_3",
        'uuid': "child_uuid_2",
        'is_global': True,
        'is_checkpoint_model': False,
        'checkpoint_step': 10,
        'created_at': datetime(2023, 1, 3),
        'projects': [2]
    }])

    model_filter_3: tuple[GetModelsByProjectIdDTO, list[dict]] = (GetModelsByProjectIdDTO(
        project_id=3,
    ), [])

    @pytest.mark.parametrize("filter_data, expected_properties", [
        model_filter_1,
        model_filter_2,
        model_filter_3
    ])
    def test_get_models_by_project_id(self, db_setup_manager: tuple[IDataManager, Session], filter_data: GetModelsByProjectIdDTO, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_models_by_project_id(session, filter_data)

        # Ensure we get exactly the expected number of results
        assert len(result) == len(expected_properties), f"The function did not return the expected number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for idx, model in enumerate(result):
            assert_properties(model, expected_properties[idx])

    dataset_filter_1 = (GetDatasetsByModelIdDTO(
        model_id=1,
        created_at=datetime(2023, 1, 3),
        dataset_name="Gamma",
        augmented=False,
        category=DatasetCategory.training
    ), [{
        'id': 3,
        'dataset_name': "Project Beta/Dataset Gamma",
        'augmented': False,
        'category': DatasetCategory.training,
        'is_global': False,
        'fine_tuning_company': FineTuningCompany.openai,
        'fine_tuning_model': "model_v1",
        'fine_tuning_formatting': "format_v1",
        'projects': [2]
    }])

    dataset_filter_2 = (GetDatasetsByModelIdDTO(
        model_id=3,
        dataset_name="Dataset Beta",
        augmented=False,
        category=DatasetCategory.training
    ), [])

    @pytest.mark.parametrize("filter_data, expected_properties", [
        dataset_filter_1,
        dataset_filter_2
    ])
    def test_get_datasets_by_model_id(self, db_setup_manager: tuple[IDataManager, Session], filter_data: GetDatasetsByModelIdDTO, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_datasets_by_model_id(session, filter_data)

        # Ensure we get exactly the expected number of results
        assert len(result) == len(expected_properties), f"The function did not return the expected number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for idx, dataset in enumerate(result):
            assert_properties(dataset, expected_properties[idx])

    get_datapoints_by_dataset_id_1: tuple[GetDatapointsByDatasetIdDTO, list[dict]] = (GetDatapointsByDatasetIdDTO(dataset_id=3), [
        {
            'id': 2,
            'dataset_id': 3,
            'evaluation_type': EvaluationType.T,
            'augmentation_type': AugmentationType.BT,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")])
        },
        {
            'id': 3,
            'dataset_id': 3,
            'evaluation_type': EvaluationType.F,
            'augmentation_type': AugmentationType.BT,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")])
        },
        {
            'id': 4,
            'dataset_id': 3,
            'augmentation_type': AugmentationType.EDA,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")])
        }
    ])

    get_datapoints_by_dataset_id_2: tuple[GetDatapointsByDatasetIdDTO, list[dict]] = (GetDatapointsByDatasetIdDTO(dataset_id=3, augmentation_type=AugmentationType.BT), [
        {
            'id': 2,
            'dataset_id': 3,
            'evaluation_type': EvaluationType.T,
            'augmentation_type': AugmentationType.BT,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")])
        },
        {
            'id': 3,
            'dataset_id': 3,
            'evaluation_type': EvaluationType.F,
            'augmentation_type': AugmentationType.BT,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")])
        }
    ])

    @pytest.mark.parametrize("dataset_datapoints_data, expected_properties", [
        get_datapoints_by_dataset_id_1,
        get_datapoints_by_dataset_id_2
    ])
    def test_get_datapoints_by_dataset_id(self, db_setup_manager: tuple[IDataManager, Session], dataset_datapoints_data: GetDatapointsByDatasetIdDTO, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_datapoints_by_dataset_id(
            session, dataset_datapoints_data)

        # Ensure we get exactly the expected number of results
        assert len(result) == len(expected_properties), f"The function did not return the expected number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for idx, datapoint in enumerate(result):
            assert_properties(datapoint, expected_properties[idx])

    @pytest.mark.parametrize("model_id, expected_hierarchy_ids", [
        (1, [1]),  # Root model, only itself
        (2, [2]),  # Child model, parent is 1
        (3, [3, 1])  # Another child model, parent is 1
    ])
    def test_get_model_hierarchy_ids(self, db_setup_manager: tuple[IDataManager, Session], model_id: int, expected_hierarchy_ids: list[int]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_model_hierarchy_ids(session, model_id)

        # Check the hierarchy of model IDs
        assert result == expected_hierarchy_ids, f"Expected hierarchy {
            expected_hierarchy_ids}, but got {result}"

    @pytest.mark.parametrize("model_id, expected_properties", [
        (1, [
            {
                'model_id': 1,
                'datapoint_id': 1,
                'evaluation_type': EvaluationType.T,
                'helpful_score': 8,
                'honest_score': 9,
                'harmless_score': 10,
                'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                    role="user", content="What's the capital of France?")]),
                'semantic_similarity_score': 0.5
            },
            {
                'model_id': 1,
                'datapoint_id': 2,
                'evaluation_type': EvaluationType.F,
                'helpful_score': 7,
                'honest_score': 8,
                'harmless_score': 9,
                'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                    role="user", content="What's the capital of France?")]),
                'semantic_similarity_score': 1.0
            }
        ]),
        (2, []),  # No evaluations for this model ID
    ])
    def test_get_model_evaluations_by_model_id(self, db_setup_manager: tuple[IDataManager, Session], model_id: int, expected_properties: list[dict]):
        test_manager, session = db_setup_manager

        # Call the function to test
        result = test_manager.get_model_evaluations_by_model_id(
            session, model_id)

        # Ensure we get exactly the expected number of results
        assert len(result) == len(expected_properties), f"The function did not return the expected number of results. Expected {
            len(expected_properties)}, got {len(result)}."

        # Check the properties of the resulting entities
        for idx, evaluation in enumerate(result):
            assert_properties(evaluation, expected_properties[idx])

    @pytest.mark.parametrize("model_id, expected_properties, should_fail", [
        (1, {
            'model_id': 1,
            'epochs': 10,
            'learning_rate_multiplier': 0.01,
            'batch_size': 32,
            'seed': 42,
            'fine_tuning_model': "fine_tuning_model_1"
        }, False),
        (2, {
            'model_id': 2,
            'epochs': 20,
            'learning_rate_multiplier': 0.02,
            'batch_size': 64,
            'seed': 43,
            'fine_tuning_model': "fine_tuning_model_2"
        }, False),
        (3, {}, True),  # No training run for this model ID
    ])
    def test_get_training_run_by_model_id(self, db_setup_manager: tuple[IDataManager, Session], model_id: int, expected_properties: dict, should_fail: Exception):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                test_manager.get_training_run_by_model_id(session, model_id)
        else:
            # Call the function to test
            result = test_manager.get_training_run_by_model_id(
                session, model_id)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            training_run = result[0]

            # Check the properties of the resulting entity
            assert_properties(training_run, expected_properties)

    @pytest.mark.parametrize("model_id, expected_properties, should_fail", [
        (1, {
            'id': 1,
            'model_name': "Project Beta/Model Alpha",
            'parent_model_id': None,
            'semantic_similarity_model': "similarity_model",
            'version': "0",
            'fine_tuning_job_id': "ft_job_id_1",
            'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_id_1",
            'fine_tuned_model_id': FineTuningModelVersions.openai.value[0],
            'uuid': "parent_uuid",
            'is_global': True,
            'is_checkpoint_model': False,
            'checkpoint_step': 0,
            'created_at': datetime(2023, 1, 1)
        }, False),
        (2, {
            'id': 2,
            'model_name': "Project Alpha/Model Beta",
            'parent_model_id': None,
            'semantic_similarity_model': "child_similarity_model",
            'version': "0",
            'fine_tuning_job_id': "ft_job_id_2",
            'fine_tuning_checkpoint_job_id': "ft_checkpoint_job_id_2",
            'fine_tuned_model_id': "ft_model_id_2",
            'uuid': "child_uuid",
            'is_global': True,
            'is_checkpoint_model': True,
            'checkpoint_step': 0,
            'created_at': datetime(2023, 1, 2)
        }, False),
        (4, {}, True),  # No model for this model ID
    ])
    def test_get_model_by_id(self, db_setup_manager: tuple[IDataManager, Session], model_id: int, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                test_manager.get_model_by_id(session, model_id)
        else:
            # Call the function to test
            result = test_manager.get_model_by_id(session, model_id)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            model = result[0]

            # Check the properties of the resulting entity
            assert_properties(model, expected_properties)

    @pytest.mark.parametrize("dataset_id, expected_properties, should_fail", [
        (1, {
            'id': 1,
            'dataset_name': "Project Alpha/Dataset Alpha",
            'augmented': False,
            'category': DatasetCategory.training,
            'is_global': False,
            'fine_tuning_company': FineTuningCompany.openai,
            'fine_tuning_model': "model_v1",
            'fine_tuning_formatting': "format_v1",
        }, False),
        (2, {
            'id': 2,
            'dataset_name': "Project Beta/Dataset Beta",
            'augmented': False,
            'category': DatasetCategory.training,
            'is_global': False,
            'fine_tuning_company': FineTuningCompany.openai,
            'fine_tuning_model': "model_v1",
            'fine_tuning_formatting': "format_v1"
        }, False),
        (4, {}, True),  # No dataset for this dataset ID
    ])
    def test_get_dataset_by_id(self, db_setup_manager: tuple[IDataManager, Session], dataset_id: int, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                test_manager.get_dataset_by_id(session, dataset_id)
        else:
            # Call the function to test
            result = test_manager.get_dataset_by_id(session, dataset_id)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            dataset = result[0]

            # Check the properties of the resulting entity
            assert_properties(dataset, expected_properties)

    @pytest.mark.parametrize("project_id, expected_properties, should_fail", [
        (1, {
            'id': 1,
            'project_name': "Project Alpha",
            'created_at': datetime(2023, 1, 1)
        }, False),
        (2, {
            'id': 2,
            'project_name': "Project Beta",
            'created_at': datetime(2022, 1, 1)
        }, False),
        (3, {}, True),  # No project for this project ID
    ])
    def test_get_project_by_id(self, db_setup_manager: tuple[IDataManager, Session], project_id: int, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                test_manager.get_project_by_id(session, project_id)
        else:
            # Call the function to test
            result = test_manager.get_project_by_id(session, project_id)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            project = result[0]

            # Check the properties of the resulting entity
            assert_properties(project, expected_properties)

    @pytest.mark.parametrize("training_run_id, expected_properties, should_fail", [
        (1, {
            'id': 1,
            'model_id': 1,
            'epochs': 10,
            'learning_rate_multiplier': 0.01,
            'batch_size': 32,
            'seed': 42,
            'fine_tuning_model': "fine_tuning_model_1",
            'created_at': datetime(2023, 1, 1)
        }, False),
        (2, {
            'id': 2,
            'model_id': 2,
            'epochs': 20,
            'learning_rate_multiplier': 0.02,
            'batch_size': 64,
            'seed': 43,
            'fine_tuning_model': "fine_tuning_model_2",
            'created_at': datetime(2023, 1, 2)
        }, False),
        (3, {}, True),  # No training run for this training run ID
    ])
    def test_get_training_run_by_id(self, db_setup_manager: tuple[IDataManager, Session], training_run_id: int, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                test_manager.get_training_run_by_id(session, training_run_id)
        else:
            # Call the function to test
            result = test_manager.get_training_run_by_id(
                session, training_run_id)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            training_run = result[0]

            # Check the properties of the resulting entity
            assert_properties(training_run, expected_properties)

    @pytest.mark.parametrize("datapoint_id, expected_properties, should_fail", [
        (1, {
            'id': 1,
            'dataset_id': 2,
            'augmentation_type': None,
            'evaluation_type': None,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")])
        }, False),
        (2, {
            'id': 2,
            'dataset_id': 3,
            'augmentation_type': AugmentationType.BT,
            'evaluation_type': EvaluationType.T,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")])
        }, False),
        (7, {}, True),  # No datapoint for this ID
    ])
    def test_get_datapoint_by_id(self, db_setup_manager: tuple[IDataManager, Session], datapoint_id: int, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                test_manager.get_datapoint_by_id(session, datapoint_id)
        else:
            # Call the function to test
            result = test_manager.get_datapoint_by_id(session, datapoint_id)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            datapoint = result[0]

            # Check the properties of the resulting entity
            assert_properties(datapoint, expected_properties)

    @pytest.mark.parametrize("model_evaluation_id, expected_properties, should_fail", [
        (1, {
            'id': 1,
            'model_id': 1,
            'datapoint_id': 1,
            'evaluation_type': EvaluationType.T,
            'helpful_score': 8,
            'honest_score': 9,
            'harmless_score': 10,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")]),
            'semantic_similarity_score': 0.5
        }, False),
        (2, {
            'id': 2,
            'model_id': 1,
            'datapoint_id': 2,
            'evaluation_type': EvaluationType.F,
            'helpful_score': 7,
            'honest_score': 8,
            'harmless_score': 9,
            'messages': MessagesContainer(messages=[Message(role="system", content="Marv_Test_10 is a factual chatbot that is also sarcastic."), Message(
                role="user", content="What's the capital of France?")]),
            'semantic_similarity_score': 1.0
        }, False),
        (3, {}, True),  # No model evaluation for this ID
    ])
    def test_get_model_evaluation_by_id(self, db_setup_manager: tuple[IDataManager, Session], model_evaluation_id: int, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                test_manager.get_model_evaluation_by_id(
                    session, model_evaluation_id)
        else:
            # Call the function to test
            result = test_manager.get_model_evaluation_by_id(
                session, model_evaluation_id)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            model_evaluation = result[0]

            # Check the properties of the resulting entity
            assert_properties(model_evaluation, expected_properties)

    @pytest.mark.parametrize("datapoint_evaluation_id, expected_properties, should_fail", [
        (1, {
            'id': 1,
            'datapoint_id': 1,
            'model_id': 1,
            'coherence_score': 7,
            'relevance_score': 8,
            'semantic_similarity_score': 0.92
        }, False),
        (2, {
            'id': 2,
            'datapoint_id': 2,
            'model_id': 1,
            'coherence_score': 4,
            'relevance_score': 4,
            'semantic_similarity_score': 0.5
        }, False),
        (3, {}, True),  # No datapoint evaluation for this ID
    ])
    def test_get_datapoint_evaluation_by_id(self, db_setup_manager: tuple[IDataManager, Session], datapoint_evaluation_id: int, expected_properties: dict, should_fail: bool):
        test_manager, session = db_setup_manager

        if should_fail:
            with pytest.raises(NoResultFound):
                test_manager.get_datapoint_evaluation_by_id(
                    session, datapoint_evaluation_id)
        else:
            # Call the function to test
            result = test_manager.get_datapoint_evaluation_by_id(
                session, datapoint_evaluation_id)

            # Ensure we get exactly one result
            assert len(
                result) == 1, "The function did not return exactly one result."
            datapoint_evaluation = result[0]

            # Check the properties of the resulting entity
            assert_properties(datapoint_evaluation, expected_properties)
