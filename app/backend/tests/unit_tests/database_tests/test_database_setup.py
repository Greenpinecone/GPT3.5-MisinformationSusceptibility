from ....database.schema import (Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun,
                                 DatasetCategory, AugmentationType, EvaluationType, Base)
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from ....custom_types.typedicts import MessagesContainer
from .test_database import successful_test_messages


# Populating Test Database with Structured Data
def setup_test_data(test_manager: IDataManager) -> None:
    # Recreate tables
    Base.metadata.create_all(test_manager.engine)

    with test_manager.get_session() as session:
        project_alpha = Project(
            project_name="Project Alpha", description="Alpha Project Description")
        session.add(project_alpha)
        session.commit()

        project_beta = Project(project_name="Project Beta",
                               description="Beta Project Description")
        session.add(project_beta)
        session.commit()

        # Create datasets
        # Assume IDs will be sequential and start from 1. Adjust based on your DB's actual behavior
        dataset_alpha = Dataset(
            dataset_name="Dataset Alpha",
            augmented=False,
            category=DatasetCategory.training,
            test_dataset=None,  # Default is None if not specified
            initial_dataset=None,  # Default is None if not specified
            projects=[project_alpha, project_beta]
        )
        session.add(dataset_alpha)
        session.commit()

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


def teardown_test_data(test_manager: IDataManager) -> None:
    # Drop tables
    Base.metadata.drop_all(test_manager.engine)
