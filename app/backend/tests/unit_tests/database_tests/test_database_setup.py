import json

from sqlalchemy import select
from app.backend.database.schema import FineTuningCompany, AugmentationType, DatasetCategory, EvaluationType, Project, DataPoint, Dataset, Model, TrainingRun, DataPointEvaluation, ModelEvaluation, CurrentProjectData, Base, project_model_link, project_dataset_link, model_dataset_association, datapoint_relationships, current_project_data_evaluation_association
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from ....custom_types.typedicts import MessagesContainer
# from .test_database import successful_test_messages


# Populating Test Database with Structured Data
def setup_test_data(test_manager: IDataManager) -> None:
    # Recreate tables
    Base.metadata.create_all(test_manager.engine)

    with test_manager.get_session() as session:
        # project_alpha = Project(
        #     project_name="Project Alpha", description="Alpha Project Description")
        # session.add(project_alpha)
        # session.commit()

        # project_beta = Project(project_name="Project Beta",
        #                        description="Beta Project Description")
        # session.add(project_beta)
        # session.commit()

        # Create datasets
        # Assume IDs will be sequential and start from 1. Adjust based on your DB's actual behavior

        # TEST 1 - Minimal Dataset with projects - SUCCESS
        # dataset_alpha = Dataset(
        #     dataset_name="Dataset Alpha",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_model="a",
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_formatting="x",
        #     projects=[project_alpha, project_beta]
        # )

        # TEST 2 Minimal Dataset with datapoint that has an initial datapoint - SUCCESS
        # dataset_alpha = Dataset(
        #     dataset_name="Dataset Alpha",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_model="a",
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_formatting="x",
        #     projects=[project_alpha, project_beta]
        # )
        # session.add(dataset_alpha)
        # session.flush()

        # # Example data for the DataPoints
        # datapoint1 = DataPoint(
        #     dataset_id=1,  # assuming a dataset with id 1 exists
        #     augmentation_type=None,
        #     messages=json.dumps(
        #         [{"role": "system", "content": "Initial datapoint message"}])
        # )
        # session.add(datapoint1)
        # session.flush()

        # datapoint2 = DataPoint(
        #     dataset_id=1,  # assuming the same dataset with id 1
        #     # assuming this is a valid enum value
        #     augmentation_type=AugmentationType.BT,
        #     messages=json.dumps(
        #         [{"role": "system", "content": "Augmented datapoint message"}]),
        #     initial_datapoint=datapoint1
        # )
        # session.add(datapoint2)
        # session.flush()

        # TEST - 3 Dataset with initial dataset where augmented dataset gets deleted - SUCCESS
        # initial_dataset = Dataset(
        #     dataset_name="Initial Dataset",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_model="model_v1",
        #     fine_tuning_formatting="format_v1"
        # )
        # session.add(initial_dataset)
        # session.flush()

        # dataset_alpha = Dataset(
        #     dataset_name="Dataset with Initial Dataset",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_model="model_v1",
        #     fine_tuning_formatting="format_v1",
        #     initial_datasets=[initial_dataset]
        # )
        # session.add(dataset_alpha)
        # session.flush()

        # TEST - 4 Dataset with initial Dataset and both datasets have one datapoint with an initial datapoint, where initial datapoint is datapoint of initial dataset. And initial dataset with datapoint gets deleted. - SUCCESS
        # dataset_alpha = Dataset(
        #     dataset_name="Initial Dataset",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_model="model_v1",
        #     fine_tuning_formatting="format_v1",
        # )
        # session.add(dataset_alpha)
        # session.flush()

        # initial_dataset = Dataset(
        #     dataset_name="Dataset with Initial Dataset",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_model="model_v1",
        #     fine_tuning_formatting="format_v1",
        #     initial_datasets=[dataset_alpha],
        # )

        # session.add(initial_dataset)
        # session.flush()

        # datapoint1 = DataPoint(
        #     dataset_id=1,  # assuming a dataset with id 1 exists
        #     augmentation_type=None,
        #     messages=json.dumps(
        #         [{"role": "system", "content": "Initial datapoint message"}])
        # )
        # session.add(datapoint1)
        # session.flush()

        # datapoint2 = DataPoint(
        #     dataset_id=2,
        #     # assuming this is a valid enum value
        #     augmentation_type=AugmentationType.BT,
        #     messages=json.dumps(
        #         [{"role": "system", "content": "Augmented datapoint message"}]),
        #     initial_datapoint=datapoint1
        # )
        # session.add(datapoint2)
        # session.flush()

        # TEST - 5 Dataset associated with a model - SUCCESS
        # model = Model(
        #     model_name="Model 1",
        #     parent_model_id=None,
        #     semantic_similarity_model="similarity_model",
        #     version="1.0",
        #     fine_tuning_job_id="ft_job_id",
        #     fine_tuning_checkpoint_job_id="ft_checkpoint_job_id",
        #     fine_tuned_model_id="ft_model_id",
        #     uuid="some_uuid",
        #     is_global=True,
        #     is_checkpoint_model=False,
        #     checkpoint_step=0
        # )
        # session.add(model)
        # session.flush()

        # dataset_alpha = Dataset(
        #     dataset_name="Dataset with Model",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_model="model_v1",
        #     fine_tuning_formatting="format_v1",
        #     models=[model]
        # )
        # session.add(dataset_alpha)
        # session.flush()

        # TEST - 6 Create a Dataset with a Model Association and an Initial Dataset. Bot datasets belong to the same model or only one dataset - both SUCCESS
        # model = Model(
        #     model_name="Model 1",
        #     parent_model_id=None,
        #     semantic_similarity_model="similarity_model",
        #     version="1.0",
        #     fine_tuning_job_id="ft_job_id",
        #     fine_tuning_checkpoint_job_id="ft_checkpoint_job_id",
        #     fine_tuned_model_id="ft_model_id",
        #     uuid="some_uuid",
        #     is_global=True,
        #     is_checkpoint_model=False,
        #     checkpoint_step=0
        # )
        # session.add(model)
        # session.flush()

        # initial_dataset = Dataset(
        #     dataset_name="Dataset with Initial Dataset",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_model="model_v1",
        #     fine_tuning_formatting="format_v1",
        #     models=[model]
        # )
        # session.add(initial_dataset)
        # session.flush()

        # dataset_alpha = Dataset(
        #     dataset_name="Dataset with Model and Initial Dataset",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_model="model_v1",
        #     fine_tuning_formatting="format_v1",
        #     initial_datasets=[initial_dataset],
        #     models=[model]
        # )
        # session.add(dataset_alpha)
        # session.flush()

        # TEST 7 -  Create a Dataset with a Model Association, an Initial Dataset, and a Datapoint with an initial datapoint that belongs to the initial dataset - SUCCESS no matter which is the parent dataset
        # model = Model(
        #     model_name="Model 1",
        #     parent_model_id=None,
        #     semantic_similarity_model="similarity_model",
        #     version="1.0",
        #     fine_tuning_job_id="ft_job_id",
        #     fine_tuning_checkpoint_job_id="ft_checkpoint_job_id",
        #     fine_tuned_model_id="ft_model_id",
        #     uuid="some_uuid",
        #     is_global=True,
        #     is_checkpoint_model=False,
        #     checkpoint_step=0
        # )
        # session.add(model)
        # session.flush()

        # dataset_alpha = Dataset(
        #     dataset_name="Dataset with Initial Dataset",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_model="model_v1",
        #     fine_tuning_formatting="format_v1",
        # )
        # session.add(dataset_alpha)
        # session.flush()

        # initial_dataset = Dataset(
        #     dataset_name="Dataset with Model and Initial Dataset",
        #     augmented=False,
        #     category=DatasetCategory.training,
        #     is_global=False,
        #     fine_tuning_company=FineTuningCompany.openai,
        #     fine_tuning_model="model_v1",
        #     fine_tuning_formatting="format_v1",
        #     initial_datasets=[dataset_alpha],
        #     models=[model]
        # )
        # session.add(initial_dataset)
        # session.flush()

        # datapoint1 = DataPoint(
        #     dataset_id=1,  # initial dataset
        #     augmentation_type=None,
        #     messages=json.dumps(
        #         [{"role": "system", "content": "Initial datapoint message"}])
        # )
        # session.add(datapoint1)
        # session.flush()

        # datapoint2 = DataPoint(
        #     dataset_id=2,
        #     # dataset alpha
        #     augmentation_type=AugmentationType.BT,
        #     messages=json.dumps(
        #         [{"role": "system", "content": "Augmented datapoint message"}]),
        #     initial_datapoint=datapoint1
        # )
        # session.add(datapoint2)
        # session.flush()

        # TEST - 8 Our standard configuration is now A dataset with an initial dataset, with a datapoint that has an initial datapoint and the dataset is associated to a model. This works correctly until now.
        # Now also a test dataset is added! - SUCCESS Both ways, once dataset is parent dataset, once it is augmented dataset

        # * Fixed first bug -> datapoint_relationships had not "ondelete=CASADE" set in the associations table *

        # INFO: Until now works with all configurations, parent dataset, augmented dataset, model and datpoint evluations, associated model training run, associated projects, associated models. The relations where set once only via ORM, once only via ID and once via both.

        # * FIxed second bug: Added ondelete="CASCADE" to the current_project_data_evaluation_association table. Now DAtaPOintEvaluations can be set on CurrentProjectData and are correctly deleted on dataset deletion.

        # * Fixed thrid bug: Now all foreign keys in CurrentProjectData are set to NULL on delete of one of the related objects. Previously with "ondelete="CASCADE" it would have deleted the CurrentProjectData too.

        # INFO: Everything works so far. No Errors with dataset deletion, pretty much every scenario has been tested. And no issues with model deletion so far, but only a simple model has been deleted that had datasets and a trianing run and belonged to a project.

        # SMALL ISSUE: Child models are not automatically deleted with ondelete=Cascade and passive_deletes=True. They for whatever reason have to be deleted via ORM by just specifying cascade="...".

        # STANDARD CONFIG FROM NOW ON:
        # create projects
        project_alpha = Project(
            project_name="Project Alpha", description="Alpha Project Description")
        session.add(project_alpha)
        session.commit()

        project_beta = Project(project_name="Project Beta",
                               description="Beta Project Description")
        session.add(project_beta)
        session.commit()

        # Step 1: Create Parent Model
        model = Model(
            model_name="Parent Model",
            parent_model_id=None,  # No parent for this model
            semantic_similarity_model="similarity_model",
            version="1.0",
            fine_tuning_job_id="ft_job_id_1",
            fine_tuning_checkpoint_job_id="ft_checkpoint_job_id_1",
            fine_tuned_model_id="ft_model_id_1",
            uuid="parent_uuid",
            is_global=True,
            is_checkpoint_model=False,
            checkpoint_step=0,
        )

        session.add(model)
        session.commit()  # Commit to get the parent model ID

        # Step 2: Create Child Model
        child_model = Model(
            model_name="Child Model",
            parent_model_id=model.id,  # Set parent model ID
            semantic_similarity_model="child_similarity_model",
            version="1.1",
            fine_tuning_job_id="ft_job_id_2",
            fine_tuning_checkpoint_job_id="ft_checkpoint_job_id_2",
            fine_tuned_model_id="ft_model_id_2",
            uuid="child_uuid",
            is_global=True,
            is_checkpoint_model=False,
            checkpoint_step=0,
        )

        session.add(child_model)
        session.commit()  # Commit to save the child model

        # # Create model
        # model = Model(
        #     model_name="Model 1",
        #     parent_model_id=None,
        #     semantic_similarity_model="similarity_model",
        #     version="1.0",
        #     fine_tuning_job_id="ft_job_id",
        #     fine_tuning_checkpoint_job_id="ft_checkpoint_job_id",
        #     fine_tuned_model_id="ft_model_id",
        #     uuid="some_uuid",
        #     is_global=True,
        #     is_checkpoint_model=False,
        #     checkpoint_step=0,
        # )
        # session.add(model)
        # session.flush()

        # Create model project link entries to associate model to projects
        # Create association entries for the project_model_link table
        project_model_link_entries = [
            {
                'model_id': model.id,
                'project_id': project_alpha.id,
                'model_name': model.model_name,
                'version': model.version
            },
            {
                'model_id': model.id,
                'project_id': project_beta.id,
                'model_name': model.model_name,
                'version': model.version
            },
            {
                'model_id': child_model.id,
                'project_id': project_alpha.id,
                'model_name': child_model.model_name,
                'version': child_model.version
            },
            {
                'model_id': child_model.id,
                'project_id': project_beta.id,
                'model_name': child_model.model_name,
                'version': child_model.version
            }
        ]

        for entry in project_model_link_entries:
            session.execute(
                project_model_link.insert().values(entry)
            )
        session.commit()

        # Create test datset - id 1
        test_dataset = Dataset(
            dataset_name="Test dataset",
            augmented=False,
            category=DatasetCategory.training,
            is_global=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",
            fine_tuning_formatting="format_v1",
            projects=[project_alpha, project_beta]
        )
        session.add(test_dataset)
        session.flush()

        # Create independent test datset datapoint
        datapoint3 = DataPoint(
            dataset_id=1,  # initial dataset
            augmentation_type=None,
            messages=json.dumps(
                [{"role": "system", "content": "Initial datapoint message"}])
        )
        session.add(datapoint3)
        session.flush()

        datapoint4 = DataPoint(
            dataset_id=1,
            # dataset alpha
            augmentation_type=AugmentationType.BT,
            messages=json.dumps(
                [{"role": "system", "content": "Augmented datapoint message"}]),
            initial_datapoint=datapoint3
        )
        session.add(datapoint4)
        session.flush()

        dataset_alpha = Dataset(  # id 2
            dataset_name="Dataset with Initial Dataset",
            augmented=False,
            category=DatasetCategory.training,
            is_global=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",
            fine_tuning_formatting="format_v1",
            test_dataset=test_dataset,
            projects=[project_alpha, project_beta]
        )
        session.add(dataset_alpha)
        session.flush()

        initial_dataset = Dataset(  # id 3
            dataset_name="Dataset with Model and Initial Dataset",
            augmented=False,
            category=DatasetCategory.training,
            is_global=False,
            fine_tuning_company=FineTuningCompany.openai,
            fine_tuning_model="model_v1",
            fine_tuning_formatting="format_v1",
            initial_datasets=[dataset_alpha],
            models=[model],
            test_dataset=test_dataset,
            projects=[project_alpha, project_beta]
        )
        session.add(initial_dataset)
        session.flush()

        datapoint1 = DataPoint(
            dataset_id=2,  # initial dataset
            augmentation_type=None,
            messages=json.dumps(
                [{"role": "system", "content": "Initial datapoint message"}])
        )
        session.add(datapoint1)
        session.flush()

        datapoint2 = DataPoint(
            dataset_id=3,
            # dataset alpha
            augmentation_type=AugmentationType.BT,
            messages=json.dumps(
                [{"role": "system", "content": "Augmented datapoint message"}]),
            initial_datapoint=datapoint1
        )
        session.add(datapoint2)
        session.flush()

        # Create DataPointEvaluation for derived DataPoint
        datapoint1_evaluation = DataPointEvaluation(
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
        datapoint2_evaluation = DataPointEvaluation(
            model_id=model.id,  # Assuming the model has been added to the session and has an id
            coherence_score=7,
            relevance_score=8,
            semantic_similarity_score=0.92,
            datapoint=datapoint2,
            # model=model
        )
        session.add(datapoint2_evaluation)
        session.flush()

        # Create Model evaluations
        # Create ModelEvaluation for initial DataPoint
        model_evaluation1 = ModelEvaluation(
            model_id=model.id,  # Assuming the model has been added to the session and has an id
            # Assuming the datapoint has been added to the session and has an id
            datapoint_id=datapoint1.id,
            evaluation_type=EvaluationType.FN,  # Replace with actual enum value
            helpful_score=8,
            honest_score=9,
            harmless_score=10,
            # datapoint=datapoint1,
            # model=model
        )
        session.add(model_evaluation1)
        session.flush()

        # Create ModelEvaluation for derived DataPoint
        model_evaluation2 = ModelEvaluation(
            model_id=model.id,  # Assuming the model has been added to the session and has an id
            # Assuming the datapoint has been added to the session and has an id
            datapoint_id=datapoint2.id,
            evaluation_type=EvaluationType.TP,  # Replace with actual enum value
            helpful_score=7,
            honest_score=8,
            harmless_score=9,
            # datapoint=datapoint2,
            # model=model
        )
        session.add(model_evaluation2)
        session.flush()

        # Create TrainingRun for the model
        training_run_1 = TrainingRun(
            model_id=model.id,  # Assuming the model has been added to the session and has an id
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
        training_run_2 = TrainingRun(
            # Assuming the model has been added to the session and has an id
            model_id=child_model.id,
            epochs=10,
            learning_rate_multiplier=0.01,
            batch_size=32,
            seed=42,
            fine_tuning_model="fine_tuning_model_1",
            # model=model
        )
        session.add(training_run_2)
        session.flush()

        # 1 - Add related datapoints to test datapoints:
        datapoint3.related_datapoints.extend([datapoint1, datapoint2])
        datapoint4.related_datapoints.extend([datapoint1, datapoint2])

        # Create CurrentProjctData entity fully populated
        current_project_data = CurrentProjectData(
            unfinished_progress=True,
            current_page="fine_tune_page",
            save_checkpoint_models=True,
            semantic_similarity_model=json.dumps(
                {"model": "similarity_model_v2"}),
            augmentation_configurations=json.dumps(
                [{"config": "config_value"}]),
            currently_modified_dataset_id=dataset_alpha.id,
            selected_model_for_fine_tuning_id=model.id,
            fine_tuning_step_counter=5,
            current_project_id=project_alpha.id,
            current_fine_tuning_model_id=model.id,
            current_project=project_alpha,
            selected_model_for_fine_tuning=model,
            currently_modified_dataset=dataset_alpha,
            current_fine_tuning_model=model,
            current_augmented_datapoint_evaluations=[
                datapoint1_evaluation, datapoint2_evaluation]
        )
        session.add(current_project_data)
        session.flush()

        # ADDITIONAL CONFIGURATIONS

        dataset_id = dataset_alpha.id
        session.commit()
        all_datasets = session.query(Dataset).all()
        all_datapoints = session.query(DataPoint).all()
        all_models = session.query(Model).all()
        all_projects = session.query(Project).all()
        all_datapoint_evaluations = session.query(DataPointEvaluation).all()
        all_model_evaluations = session.query(ModelEvaluation).all()
        all_current_project_data = session.query(CurrentProjectData).all()
        all_training_runs = session.query(TrainingRun).all()
        current_project_data = session.get(CurrentProjectData, 1)
        # Perform a select query
        stmt = select(project_model_link)
        project_model_link_results = session.execute(stmt).fetchall()
        # Perform a select query
        stmt = select(project_dataset_link)
        project_dataset_link_results = session.execute(stmt).fetchall()
        stmt = select(model_dataset_association)
        model_dataset_association_results = session.execute(stmt).fetchall()
        stmt = select(datapoint_relationships)
        datapoint_relationships_results = session.execute(stmt).fetchall()
        stmt = select(current_project_data_evaluation_association)
        current_project_data_evaluation_association_results = session.execute(
            stmt).fetchall()
        print("")

        try:
            # TODO: When projects are deleted, datasets and models must be deleted manually beforehand since we have to check if the datasets / models originated from other projects initially (set global) - first entry in the projects list from the dataset model side is the original project - and if the current project is not equal to this id, then the dataset / model should not be deleted.
            # session.delete(model_evaluation1)
            # session.delete(datapoint1_evaluation)
            # session.delete(datapoint1)

            # session.delete(dataset_alpha)
            # print(model)

            # session.delete(current_project_data)

            session.commit()

        except Exception as e:
            print("hallo", e)

        all_datasets = session.query(Dataset).all()
        all_datapoints = session.query(DataPoint).all()
        all_models = session.query(Model).all()
        all_projects = session.query(Project).all()
        all_datapoint_evaluations = session.query(DataPointEvaluation).all()
        all_model_evaluations = session.query(ModelEvaluation).all()
        all_current_project_data = session.query(CurrentProjectData).all()
        all_training_runs = session.query(TrainingRun).all()
        current_project_data = session.get(CurrentProjectData, 1)

        stmt = select(project_model_link)
        project_model_link_results = session.execute(stmt).fetchall()
        # Perform a select query
        stmt = select(project_dataset_link)
        project_dataset_link_results = session.execute(stmt).fetchall()
        stmt = select(model_dataset_association)
        model_dataset_association_results = session.execute(stmt).fetchall()
        stmt = select(datapoint_relationships)
        datapoint_relationships_results = session.execute(stmt).fetchall()
        stmt = select(current_project_data_evaluation_association)
        current_project_data_evaluation_association_results = session.execute(
            stmt).fetchall()

        current_project_data = session.get(CurrentProjectData, 1)
        print("")


""" 
        dataset_beta = Dataset(
            dataset_name="Dataset Beta",
            augmented=True,
            category=DatasetCategory.test,
            test_dataset=dataset_alpha,  # Linking Alpha as the test dataset
            initial_dataset=dataset_alpha,  # Linking Alpha as the initial dataset
            projects=[project_beta, project_alpha]
        )
        session.add(dataset_beta)
        session.commit()

        # Datapoints
        conversation_alpha: MessagesContainer = successful_test_messages[0]

        conversation_beta: MessagesContainer = successful_test_messages[1]

        datapoint_alpha = DataPoint(
            dataset=dataset_alpha,
            coherence_score=8,
            relevance_score=9,
            semantic_similarity_score=0.95,
            augmentation_type=None,  # No augmentation type specified, default to None
            messages=conversation_alpha,
            category="category_alpha",
            initial_datapoint=None  # Default is None
        )
        session.add(datapoint_alpha)
        session.commit()

        datapoint_beta = DataPoint(
            dataset=dataset_beta,
            coherence_score=7,
            relevance_score=8,
            semantic_similarity_score=0.90,
            augmentation_type=AugmentationType.EDA,
            messages=conversation_beta,
            category="category_beta",
            initial_datapoint=datapoint_alpha  # Linking Alpha as the initial datapoint
        )
        session.add(datapoint_beta)
        session.commit()

        # Models
        model_alpha = Model(
            model_name="Model Alpha",
            version=1,
            project=project_alpha,
            parent_model=None,  # Default to None if not specified
            datasets=[dataset_alpha, dataset_beta]
        )
        session.add(model_alpha)
        session.commit()

        model_beta = Model(
            model_name="Model Beta",
            version=1,
            project=project_beta,
            parent_model=model_alpha,  # Linking Alpha as the parent model
            datasets=[dataset_beta, dataset_alpha]
        )
        session.add(model_beta)
        session.commit()

        model_gamma = Model(
            model_name="Model Gamma",
            version=1,
            project=project_alpha,
            parent_model=None,  # Default to None if not specified
            datasets=[dataset_alpha, dataset_beta]
        )
        session.add(model_gamma)
        session.commit()

        model_delta = Model(
            model_name="Model Delta",
            version=2,
            project=project_beta,
            parent_model=model_alpha,  # Linking Alpha as the parent model
            datasets=[dataset_beta, dataset_alpha]
        )
        session.add(model_delta)
        session.commit()

        # Model Evaluations
        model_eval_alpha = ModelEvaluation(
            model=model_alpha,
            datapoint=datapoint_alpha,
            evaluation_type=EvaluationType.TP,
            helpful_score=10,
            honest_score=9,
            harmless_score=8
        )
        session.add(model_eval_alpha)
        session.commit()

        model_eval_beta = ModelEvaluation(
            model=model_beta,
            datapoint=datapoint_beta,
            evaluation_type=EvaluationType.FN,
            helpful_score=7,
            honest_score=8,
            harmless_score=9
        )
        session.add(model_eval_beta)
        session.commit()

        # Training Runs
        training_run_alpha = TrainingRun(
            model=model_alpha,
            epochs=10,
            learning_rate_multiplier=0.01,
            batch_size=64
        )
        session.add(training_run_alpha)
        session.commit()

        training_run_beta = TrainingRun(
            model=model_beta,
            epochs=20,
            learning_rate_multiplier=0.02,
            batch_size=128
        )
        session.add(training_run_beta)
        session.commit()
        """


def teardown_test_data(test_manager: IDataManager) -> None:
    # Drop tables
    Base.metadata.drop_all(test_manager.engine)
