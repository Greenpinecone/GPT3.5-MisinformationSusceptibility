""" A class to encapsulate all entity to dto mappers since every entity has only one mapper at the moment.
"""
from ...mapper.classes.entities_to_response_dtos import *
from app.backend.database.schema import Project, DataPoint, Dataset, Model, TrainingRun, DataPointEvaluation, ModelEvaluation, CurrentProjectData
from app.backend.dtos.response import *
from sqlalchemy.orm import Session


class MapperFacade:

    def __init__(self):
        # Initialize any necessary attributes or services here
        pass

    def map_project_to_dto(self, session: Session, project_entity: Project) -> ProjectDTO:
        # Convert a Project entity to ProjectDTO
        schema = ProjectSchema(session=session)
        return schema.dump(project_entity)

    def map_dataset_to_dto(self, session: Session, dataset_entity: Dataset) -> DatasetDTO:
        # Convert a Dataset entity to DatasetDTO
        schema = DatasetSchema(session=session)
        return schema.dump(dataset_entity)

    def map_dataset_to_complex_dto(self, session: Session, dataset_entity: Dataset) -> ComplexDatasetDTO:
        # Convert a Dataset entity to ComplexDatasetDTO
        schema = ComplexDatasetSchema(session=session)
        return schema.dump(dataset_entity)

    def map_datapoint_to_dto(self, session: Session, datapoint_entity: DataPoint) -> DataPointDTO:
        # Convert a DataPoint entity to DataPointDTO
        schema = DataPointSchema(session=session)
        return schema.dump(datapoint_entity)

    def map_datapoint_to_training_datapoint_dto(self, session: Session, datapoint_entity: DataPoint) -> DataPointDTO:
        # Convert a DataPoint entity to DataPointDTO
        schema = TrainingDataPointSchema(session=session)
        return schema.dump(datapoint_entity)

    def map_model_to_dto(self, session: Session, model_entity: Model) -> ModelDTO:
        # Convert a Model entity to ModelDTO
        schema = ModelSchema(session=session)
        return schema.dump(model_entity)

    def map_model_to_complex_dto(self, session: Session, model_entity: Model) -> ComplexModelDTO:
        # Convert a Model entity to ComplexModelDTO
        schema = ComplexModelSchema(session=session)
        return schema.dump(model_entity)

    def map_model_evaluation_to_dto(self, session: Session, model_evaluation_entity: ModelEvaluation) -> ModelEvaluationDTO:
        # Convert a ModelEvaluation entity to ModelEvaluationDTO
        schema = ModelEvaluationSchema(session=session)
        return schema.dump(model_evaluation_entity)

    def map_training_run_to_dto(self, session: Session, training_run_entity: TrainingRun) -> TrainingRunDTO:
        # Convert a TrainingRun entity to TrainingRunDTO
        schema = TrainingRunSchema(session=session)
        return schema.dump(training_run_entity)

    def map_training_run_to_simple_dto(self, session: Session, training_run_entity: TrainingRun) -> SimpleTrainingRunDTO:
        # Convert a TrainingRun entity to SimpleTrainingRunDTO
        schema = SimpleTrainingRunSchema(session=session)
        return schema.dump(training_run_entity)

    def map_current_project_data_to_dto(self, session: Session, current_project_data: CurrentProjectData) -> CurrentProjectDataDTO:
        # Convert a CurrentProjectData entity to CurrentProjectDataDTO
        schema = CurrentProjectDataSchema(session=session)
        return schema.dump(current_project_data)

    def map_datapoint_evaluation_to_dto(self, session: Session, current_project_data: DataPointEvaluation) -> DataPointEvaluationDTO:
        # Convert a DataPointEvalaution entity to DataPointEvaluationDTO
        schema = DataPointEvaluationSchema(session=session)
        return schema.dump(current_project_data)
