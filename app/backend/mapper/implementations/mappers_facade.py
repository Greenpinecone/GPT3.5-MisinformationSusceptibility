""" A class to encapsulate all entity to dto mappers since every entity has only one mapper at the moment.
"""
from ...mapper.classes.entities_to_response_dtos import *
from ...database.schema import *


class MapperFacade:

    def __init__(self):
        # Initialize any necessary attributes or services here
        pass

    def map_project_to_dto(self, project_entity: Project) -> ProjectDTO:
        # Convert a Project entity to ProjectDTO
        schema = ProjectSchema()
        return schema.dump(project_entity)

    def map_dataset_to_dto(self, dataset_entity: Dataset) -> DatasetDTO:
        # Convert a Dataset entity to DatasetDTO
        schema = DatasetSchema()
        return schema.dump(dataset_entity)

    def map_datapoint_to_dto(self, datapoint_entity: DataPoint) -> DataPointDTO:
        # Convert a DataPoint entity to DataPointDTO
        schema = DataPointSchema()
        return schema.dump(datapoint_entity)

    def map_model_to_dto(self, model_entity: Model) -> ModelDTO:
        # Convert a Model entity to ModelDTO
        schema = ModelSchema()
        return schema.dump(model_entity)

    def map_model_evaluation_to_dto(self, model_evaluation_entity: ModelEvaluation) -> ModelEvaluationDTO:
        # Convert a ModelEvaluation entity to ModelEvaluationDTO
        schema = ModelEvaluationSchema()
        return schema.dump(model_evaluation_entity)

    def map_training_run_to_dto(self, training_run_entity: TrainingRun) -> TrainingRunDTO:
        # Convert a TrainingRun entity to TrainingRunDTO
        schema = TrainingRunSchema()
        return schema.dump(training_run_entity)
