from ....database.schema import (Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun,
                                 DatasetCategory, AugmentationType, EvaluationType, Base)
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from typing import Any


# Assuming DataManager is properly set to work with test database
def create_project(name: str, description: str = None) -> Project:
    return Project(project_name=name, description=description)


def create_dataset(name: str, augmented: bool, category: DatasetCategory,  test_dataset_id: int, initial_dataset_id: int = None, projects: list = []) -> Dataset:
    dataset = Dataset(dataset_name=name, augmented=augmented,
                      category=category, projects=projects, test_dataset_id=test_dataset_id)
    if initial_dataset_id:
        dataset.initial_dataset_id = initial_dataset_id
    return dataset


def create_datapoint(dataset_id: int, coherence_score: int, relevance_score: int, semantic_similarity_score: float, augmentation_type: AugmentationType, messages: str, category: str, initial_datapoint_id: int = None) -> DataPoint:
    return DataPoint(dataset_id=dataset_id, coherence_score=coherence_score, relevance_score=relevance_score, semantic_similarity_score=semantic_similarity_score, augmentation_type=augmentation_type, messages=messages, category=category, initial_datapoint_id=initial_datapoint_id)


def create_model(name: str, version: int, project_id: int, parent_model_id: int = None) -> Model:
    return Model(model_name=name, version=version, project_id=project_id, parent_model_id=parent_model_id)


def create_model_evaluation(model: Model, datapoint: DataPoint, evaluation_type: EvaluationType,
                            helpful_score: int, honest_score: int, harmless_score: int) -> ModelEvaluation:
    return ModelEvaluation(model=model, datapoint=datapoint, evaluation_type=evaluation_type,
                           helpful_score=helpful_score, honest_score=honest_score, harmless_score=harmless_score)


def create_training_run(model: Model, epochs: int, learning_rate_multiplier: float, batch_size: int) -> TrainingRun:
    return TrainingRun(model=model, epochs=epochs, learning_rate_multiplier=learning_rate_multiplier,
                       batch_size=batch_size)


# Populating Test Database with Structured Data
def setup_test_data(test_manager: IDataManager) -> None:
    with test_manager.get_session() as session:
        project_alpha = create_project(
            name="Project Alpha", description="Alpha Project Description")
        project_beta = create_project(
            name="Project Beta", description="Beta Project Description")
        session.add_all([project_alpha, project_beta])
        session.commit()

        # Create datasets
        # Assume IDs will be sequential and start from 1. Adjust based on your DB's actual behavior
        dataset_alpha = create_dataset(name="Dataset Alpha", augmented=False,
                                       category=DatasetCategory.training, test_dataset_id=None, projects=[project_alpha])
        dataset_beta = create_dataset(name="Dataset Beta", augmented=True,
                                      category=DatasetCategory.test, test_dataset_id=None, projects=[project_beta])
        session.add_all([dataset_alpha, dataset_beta])
        session.commit()

        # Assuming dataset_alpha is the initial dataset for dataset_beta
        dataset_beta.initial_dataset_id = dataset_alpha.id
        # This line is more for the sake of having a value. Adjust as needed.
        dataset_beta.test_dataset_id = dataset_alpha.id
        session.commit()

        # Datapoints
        datapoint_alpha = create_datapoint(dataset_id=dataset_alpha.id, coherence_score=8, relevance_score=9, semantic_similarity_score=0.95,
                                           augmentation_type=AugmentationType.BT, messages="Sample message", category="category_alpha")
        datapoint_beta = create_datapoint(dataset_id=dataset_beta.id, coherence_score=7, relevance_score=8, semantic_similarity_score=0.90,
                                          augmentation_type=AugmentationType.EDA, messages="Sample message beta", category="category_beta")
        session.add_all([datapoint_alpha, datapoint_beta])
        session.commit()

        # Models
        model_alpha = create_model(
            name="Model Alpha", version=1, project_id=project_alpha.id)
        model_beta = create_model(name="Model Beta", version=1,
                                  project_id=project_beta.id, parent_model_id=model_alpha.id)

        # Link datasets to models
        # Assuming dataset_alpha is for training
        model_alpha.datasets.append(dataset_alpha)
        # Assuming dataset_beta is for testing
        model_alpha.datasets.append(dataset_beta)
        model_beta.datasets.append(dataset_alpha)
        model_beta.datasets.append(dataset_beta)
        session.add_all([model_alpha, model_beta])
        session.commit()

        # Model Evaluations
        model_eval_alpha = create_model_evaluation(model=model_alpha, datapoint=datapoint_alpha,
                                                   evaluation_type=EvaluationType.TP, helpful_score=10, honest_score=9, harmless_score=8)
        model_eval_beta = create_model_evaluation(model=model_beta, datapoint=datapoint_beta,
                                                  evaluation_type=EvaluationType.FN, helpful_score=7, honest_score=8, harmless_score=9)

        # Training Runs
        training_run_alpha = create_training_run(
            model=model_alpha, epochs=10, learning_rate_multiplier=0.01, batch_size=64)
        training_run_beta = create_training_run(
            model=model_beta, epochs=20, learning_rate_multiplier=0.02, batch_size=128)

        session.add_all([model_eval_alpha, model_eval_beta,
                        training_run_alpha, training_run_beta])
        session.commit()

        # Add everything to the session and commit
        entities: list[Any] = [project_alpha, project_beta, dataset_alpha, dataset_beta,
                               datapoint_alpha, datapoint_beta, model_alpha, model_beta,
                               model_eval_alpha, model_eval_beta, training_run_alpha, training_run_beta]
        session.add_all(entities)


def teardown_test_data(test_manager: IDataManager) -> None:
    Base.metadata.drop_all(test_manager.engine)
    test_manager.engine.dispose()
