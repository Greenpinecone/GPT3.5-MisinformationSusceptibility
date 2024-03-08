from sqlalchemy.orm import Session
from database.schema import (Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun,
                             DatasetCategory, AugmentationType, EvaluationType)


# Assuming DataManager is properly set to work with test database
def create_project(name: str) -> Project:
    return Project(project_name=name)


def create_dataset(name: str, augmented: bool, category: DatasetCategory, projects: list = []) -> Dataset:
    return Dataset(dataset_name=name, augmented=augmented, category=category, projects=projects)


def create_datapoint(dataset: Dataset, coherence_score: int, relevance_score: int,
                     semantic_similarity_score: float, augmentation_type: AugmentationType,
                     messages: str, datapoint_category: str) -> DataPoint:
    return DataPoint(dataset=dataset, coherence_score=coherence_score, relevance_score=relevance_score,
                     semantic_similarity_score=semantic_similarity_score, augmentation_type=augmentation_type,
                     messages=messages, datapoint_category=datapoint_category)


def create_model(name: str, version: int, project: Project) -> Model:
    return Model(model_name=name, version=version, project=project)


def create_model_evaluation(model: Model, datapoint: DataPoint, evaluation_type: EvaluationType,
                            helpful_score: int, honest_score: int, harmless_score: int) -> ModelEvaluation:
    return ModelEvaluation(model=model, datapoint=datapoint, evaluation_type=evaluation_type,
                           helpful_score=helpful_score, honest_score=honest_score, harmless_score=harmless_score)


def create_training_run(model: Model, epochs: int, learning_rate_multiplier: float, batch_size: int) -> TrainingRun:
    return TrainingRun(model=model, epochs=epochs, learning_rate_multiplier=learning_rate_multiplier,
                       batch_size=batch_size)


# Populating Test Database with Structured Data
def setup_test_data(session: Session) -> None:
    # Project Creation
    project_alpha = create_project("Project Alpha")
    project_beta = create_project("Project Beta")

    # Dataset Creation
    dataset_alpha = create_dataset(
        "Dataset Alpha", False, DatasetCategory.training)
    dataset_beta = create_dataset("Dataset Beta", True, DatasetCategory.test)

    # Datapoint Creation
    datapoint_alpha = create_datapoint(
        dataset_alpha, 8, 9, 0.95, AugmentationType.BT, "Sample message", "category_alpha")
    datapoint_beta = create_datapoint(
        dataset_beta, 7, 8, 0.90, AugmentationType.EDA, "Sample message beta", "category_beta")

    # Model Creation
    model_alpha = create_model("Model Alpha", 1, project_alpha)
    model_beta = create_model("Model Beta", 1, project_beta)

    # Model Evaluation Creation
    model_eval_alpha = create_model_evaluation(
        model_alpha, datapoint_alpha, EvaluationType.TP, 10, 9, 8)
    model_eval_beta = create_model_evaluation(
        model_beta, datapoint_beta, EvaluationType.FN, 7, 8, 9)

    # Training Run Creation
    training_run_alpha = create_training_run(model_alpha, 10, 0.01, 64)
    training_run_beta = create_training_run(model_beta, 20, 0.02, 128)

    # Add everything to the session and commit
    entities = [project_alpha, project_beta, dataset_alpha, dataset_beta,
                datapoint_alpha, datapoint_beta, model_alpha, model_beta,
                model_eval_alpha, model_eval_beta, training_run_alpha, training_run_beta]
    session.add_all(entities)
    session.commit()
