from datetime import datetime
import json

from sqlalchemy import select, text
from app.backend.database.schema import FineTuningCompany, AugmentationType, DatasetCategory, EvaluationType, Project, DataPoint, Dataset, Model, TrainingRun, DataPointEvaluation, ModelEvaluation, CurrentProjectData, Base, project_model_link, project_dataset_link, model_dataset_association, datapoint_relationships, current_project_data_evaluation_association
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from app.backend.custom_types.typedicts import AugmentationConfiguration, GoogleBTParams, MessagesContainer
# from .test_database import successful_test_messages
from sqlalchemy.orm import joinedload
import logging
import time


# Enable SQLAlchemy logging to see the SQL queries
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


# Populating Test Database with Structured Data
def setup_test_data(test_manager: IDataManager) -> None:
    with test_manager.get_session() as session:
        # create projects
        project_alpha = Project(  # id 1
            project_name="Project Alpha", description="Alpha Project Description", created_at=datetime(2023, 1, 1))
        session.add(project_alpha)
        session.flush()

        project_beta = Project(project_name="Project Beta",  # id 2
                               description="Beta Project Description", created_at=datetime(2022, 1, 1))
        session.add(project_beta)
        session.flush()

        # Step 1: Create Parent Model
        model = Model(  # id 1
            model_name="Project Beta/Model Alpha",
            parent_model_id=None,  # No parent for this model
            semantic_similarity_model="similarity_model",
            version="0",
            fine_tuning_job_id="ft_job_id_1",
            fine_tuning_checkpoint_job_id="ft_checkpoint_job_id_1",
            fine_tuned_model_id="ft_model_id_1",
            uuid="parent_uuid",
            is_global=True,
            is_checkpoint_model=False,
            checkpoint_step=0,
            created_at=datetime(2023, 1, 1)
        )

        session.add(model)
        session.flush()  # flush to get the parent model ID

        # Step 2: Create Child Model
        child_model = Model(  # id 2
            model_name="Project Alpha/Model Beta",
            parent_model_id=None,  # Set parent model ID
            semantic_similarity_model="child_similarity_model",
            version="0",
            fine_tuning_job_id="ft_job_id_2",
            fine_tuning_checkpoint_job_id="ft_checkpoint_job_id_2",
            fine_tuned_model_id="ft_model_id_2",
            uuid="child_uuid",
            is_global=True,
            is_checkpoint_model=True,
            augmentation_configurations=[{"configuration_1": AugmentationConfiguration(
                selected_method="method_1", prev_method=None, augmentation_percentage=10.0, augmentation_config=GoogleBTParams(translate_languages=["en", "es"]))}],
            checkpoint_step=0,
            created_at=datetime(2023, 1, 2)
        )
        session.add(child_model)
        session.flush()  # flush to save the child model

        child_model_2 = Model(  # id 3
            model_name="Project Beta/Model Alpha",
            parent_model_id=model.id,  # Set parent model ID
            semantic_similarity_model="child_2_similarity_model",
            version="1",
            fine_tuning_job_id="ft_job_id_3",
            fine_tuning_checkpoint_job_id="ft_checkpoint_job_id_3",
            fine_tuned_model_id="ft_model_id_3",
            uuid="child_uuid_2",
            is_global=True,
            is_checkpoint_model=False,
            augmentation_configurations=[{"configuration_1": AugmentationConfiguration(
                selected_method="method_1", prev_method=None, augmentation_percentage=10.0, augmentation_config=GoogleBTParams(translate_languages=["en", "es"]))}],
            checkpoint_step=10,
            created_at=datetime(2023, 1, 3)
        )

        session.add(child_model_2)
        session.flush()  # flush to save the child model

        # Create model project link entries to associate model to projects
        # Create association entries for the project_model_link table
        project_model_link_entries = [
            {
                'model_id': model.id,  # id 1
                'project_id': project_beta.id,
                'model_name': model.model_name,
                'version': model.version
            },
            {
                'model_id': model.id,  # id 1
                'project_id': project_alpha.id,
                'model_name': model.model_name,
                'version': model.version
            },
            {
                'model_id': child_model.id,  # id 2
                'project_id': project_alpha.id,
                'model_name': child_model.model_name,
                'version': child_model.version
            },
            {
                'model_id': child_model.id,  # id 2
                'project_id': project_beta.id,
                'model_name': child_model.model_name,
                'version': child_model.version
            },
            {
                'model_id': child_model_2.id,  # id 3
                'project_id': project_beta.id,
                'model_name': child_model_2.model_name,
                'version': child_model_2.version
            }
        ]

        for entry in project_model_link_entries:
            session.execute(
                project_model_link.insert().values(entry)
            )
            # Sleep for 0.1 seconds to avoid time stamps with the same second since SQLite is not more accurate and wee need unique time stamps for database calculations
            time.sleep(1)
        session.flush()

        # Create test datset
        test_dataset = Dataset(  # id 1
            dataset_name="Project Alpha/Dataset Alpha",
            augmented=False,
            category=DatasetCategory.training,
            is_global=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",
            fine_tuning_formatting="format_v1",
            projects=[project_alpha],
            created_at=datetime(2023, 1, 1)
        )
        session.add(test_dataset)
        session.flush()

        # Sleep for 0.1 seconds to avoid time stamps with the same second since SQLite is not more accurate and wee need unique time stamps for database calculations
        time.sleep(1)

        test_dataset.projects.append(project_beta)
        session.flush()

        time.sleep(1)

        dataset_alpha = Dataset(  # id 2
            dataset_name="Project Beta/Dataset Beta",
            augmented=False,
            category=DatasetCategory.training,
            is_global=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",
            fine_tuning_formatting="format_v1",
            test_dataset=test_dataset,
            projects=[project_beta],
            created_at=datetime(2023, 1, 2)
        )
        session.add(dataset_alpha)
        session.flush()

        time.sleep(1)

        dataset_alpha.projects.append(project_alpha)
        session.flush()

        child_dataset = Dataset(  # id 3
            dataset_name="Project Beta/Dataset Gamma",
            augmented=False,
            category=DatasetCategory.training,
            is_global=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",
            fine_tuning_formatting="format_v1",
            initial_datasets=[dataset_alpha],
            models=[model],
            test_dataset=test_dataset,
            projects=[project_beta],
            created_at=datetime(2023, 1, 3)
        )
        session.add(child_dataset)
        session.flush()

        datapoint1 = DataPoint(  # id 1
            dataset_id=2,  # dataset_alpha
            augmentation_type=None,
            evaluation_type=None,
            messages=[{"role": "system", "content": "Initial datapoint message"}]
        )
        session.add(datapoint1)
        session.flush()

        datapoint2 = DataPoint(  # id 2
            dataset_id=3,  # child_dataset
            evaluation_type=EvaluationType.T,
            augmentation_type=AugmentationType.BT,
            messages=[
                {"role": "system", "content": "Augmented datapoint message"}],
            initial_datapoint=datapoint1
        )
        session.add(datapoint2)
        session.flush()

        # Datapoint relations test
        datapoint3 = DataPoint(  # id 3
            dataset_id=3,  # child_dataset
            evaluation_type=EvaluationType.F,
            augmentation_type=AugmentationType.BT,
            messages=[{"role": "system", "content": "DATAPOINT 3"}],
        )
        session.add(datapoint3)
        session.flush()
        datapoint4 = DataPoint(  # id 4
            dataset_id=3,  # child_dataset
            augmentation_type=AugmentationType.EDA,
            messages=[{"role": "system", "content": "DATAPOINT 4"}],
        )
        session.add(datapoint4)
        session.flush()

        datapoint4.related_datapoints.append(datapoint3)
        session.flush()

        # Create independent test datset datapoint
        datapoint5 = DataPoint(  # id 5
            dataset_id=1,  # test dataset
            augmentation_type=None,
            messages=[{"role": "system", "content": "Initial datapoint message"}]
        )
        session.add(datapoint5)
        session.flush()

        datapoint6 = DataPoint(  # id 6
            dataset_id=1,  # test dataset
            augmentation_type=AugmentationType.BT,
            messages=[
                {"role": "system", "content": "Augmented datapoint message"}],
            initial_datapoint=datapoint5
        )
        session.add(datapoint6)
        session.flush()

        # Create DataPointEvaluation for derived DataPoint
        datapoint1_evaluation = DataPointEvaluation(  # id 1
            model_id=model.id,  # Assuming the model has been added to the session and has an id
            coherence_score=7,
            relevance_score=8,
            semantic_similarity_score=0.92,
            datapoint=datapoint1,
            # model=model
        )
        session.add(datapoint1_evaluation)
        session.flush()

        # Create DataPointEvaluation for derived DataPoint
        datapoint2_evaluation = DataPointEvaluation(  # id 2
            model_id=model.id,
            coherence_score=4,
            relevance_score=4,
            semantic_similarity_score=0.5,
            datapoint=datapoint2,
            # model=model
        )
        session.add(datapoint2_evaluation)
        session.flush()

        # Create Model evaluations
        # Create ModelEvaluation for initial DataPoint
        model_evaluation1 = ModelEvaluation(  # id 1
            model_id=model.id,
            datapoint_id=datapoint1.id,
            evaluation_type=EvaluationType.T,
            helpful_score=8,
            honest_score=9,
            harmless_score=10,
            messages={"messages": ["message1"]},
            semantic_similarity_score=0.5
        )
        session.add(model_evaluation1)
        session.flush()

        # Create ModelEvaluation for derived DataPoint
        model_evaluation2 = ModelEvaluation(  # id 2
            model_id=model.id,
            datapoint_id=datapoint2.id,
            evaluation_type=EvaluationType.F,
            helpful_score=7,
            honest_score=8,
            harmless_score=9,
            messages={"messages": ["message2"]},
            semantic_similarity_score=1.0
        )
        session.add(model_evaluation2)
        session.flush()

        # Create TrainingRun for the model
        training_run_1 = TrainingRun(  # id 1
            model_id=model.id,
            epochs=10,
            learning_rate_multiplier=0.01,
            batch_size=32,
            seed=42,
            fine_tuning_model="fine_tuning_model_1",
            # model=model
        )
        session.add(training_run_1)
        session.flush()

        # Create TrainingRun for the model
        training_run_2 = TrainingRun(  # id 2
            model_id=child_model.id,
            epochs=20,
            learning_rate_multiplier=0.02,
            batch_size=64,
            seed=43,
            fine_tuning_model="fine_tuning_model_2",
            # model=model
        )
        session.add(training_run_2)
        session.flush()

        # 1 - Add related datapoints to test datapoints:
        datapoint3.related_datapoints.extend([datapoint1, datapoint2])
        datapoint4.related_datapoints.extend([datapoint1, datapoint2])

        # Create CurrentProjctData entity fully populated
        current_project_data = CurrentProjectData(  # id 1
            unfinished_progress=True,
            current_page="fine_tune_page",
            save_checkpoint_models=True,
            semantic_similarity_model={"model": "similarity_model_v2"},
            current_augmentation_configurations=[{"config": "config_value"}],
            currently_modified_dataset_id=dataset_alpha.id,
            selected_model_for_fine_tuning_id=model.id,
            fine_tuning_step_counter=5,
            current_project_id=project_alpha.id,
            current_fine_tuning_model_id=model.id,
            current_project=project_alpha,
            selected_model_for_fine_tuning=model,
            currently_modified_dataset=dataset_alpha,
            current_fine_tuning_model=model,
            selected_statistic_models=[model],
            generated_checkpoint_models=[child_model],
            current_augmented_datapoint_evaluations=[
                datapoint1_evaluation, datapoint2_evaluation]
        )
        session.add(current_project_data)
        session.flush()

        # ** CHECK MANUALLY IF ALL ENTITIES HAVE BEEN PROPERLY ADDED TO THR DATABASE  -  BEFORE COMMIT **

        # all_datasets = session.query(Dataset).all()
        # all_datapoints = session.query(DataPoint).all()
        # all_models = session.query(Model).all()
        # all_projects = session.query(Project).all()
        # all_datapoint_evaluations = session.query(DataPointEvaluation).all()
        # all_model_evaluations = session.query(ModelEvaluation).all()
        # all_current_project_data = session.query(CurrentProjectData).all()
        # all_training_runs = session.query(TrainingRun).all()
        # current_project_data = session.get(CurrentProjectData, 1)
        # # Perform a select query
        # stmt = select(project_model_link)
        # project_model_link_results = session.execute(stmt).fetchall()
        # # Perform a select query
        # stmt = select(project_dataset_link)
        # project_dataset_link_results = session.execute(stmt).fetchall()
        # stmt = select(model_dataset_association)
        # model_dataset_association_results = session.execute(stmt).fetchall()
        # stmt = select(datapoint_relationships)
        # datapoint_relationships_results = session.execute(stmt).fetchall()
        # stmt = select(current_project_data_evaluation_association)
        # current_project_data_evaluation_association_results = session.execute(
        #     stmt).fetchall()
        # print("")

        # try:
        #     session.commit()
        # except Exception as e:
        #     print("Database setup failed at commit.", e)

        # ** CHECK MANUALLY IF ALL ENTITIES HAVE BEEN PROPERLY ADDED TO THR DATABASE **

        # all_datasets = session.query(Dataset).all()
        # all_datapoints = session.query(DataPoint).all()
        # all_models = session.query(Model).all()
        # all_projects = session.query(Project).all()
        # all_datapoint_evaluations = session.query(DataPointEvaluation).all()
        # all_model_evaluations = session.query(ModelEvaluation).all()
        # all_current_project_data = session.query(CurrentProjectData).all()
        # all_training_runs = session.query(TrainingRun).all()
        # current_project_data = session.get(CurrentProjectData, 1)

        # stmt = select(project_model_link)
        # project_model_link_results = session.execute(stmt).fetchall()
        # # Perform a select query
        # stmt = select(project_dataset_link)
        # project_dataset_link_results = session.execute(stmt).fetchall()
        # stmt = select(model_dataset_association)
        # model_dataset_association_results = session.execute(stmt).fetchall()
        # stmt = select(datapoint_relationships)
        # datapoint_relationships_results = session.execute(stmt).fetchall()
        # stmt = select(current_project_data_evaluation_association)
        # current_project_data_evaluation_association_results = session.execute(
        #     stmt).fetchall()

        # current_project_data = session.get(CurrentProjectData, 1)
        # print("")


def teardown_test_data(test_manager: IDataManager) -> None:
    # Drop tables
    Base.metadata.drop_all(test_manager.engine)
