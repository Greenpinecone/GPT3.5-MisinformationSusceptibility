""" A class to encapsulate all entity to dto mappers since every entity has only one mapper at the moment.
"""
from sqlalchemy.orm import Session
from app.backend.mapper.classes.entities_to_response_dtos import ComplexDataPointEvaluationSchema, ComplexDatasetSchema, ComplexModelEvaluationSchema, ComplexModelSchema, CurrentProjectDataSchema, DataPointEvaluationSchema, DataPointSchema, DatasetSchema, ModelEvaluationSchema, ModelSchema, ModelWithOriginalProjectSchema, ProjectSchema, SimpleDataPointSchema, SimpleProjectSchema, SimpleTrainingRunSchema, TrainingDataPointSchema, TrainingRunSchema
from app.backend.database.schema import Project, DataPoint, Dataset, Model, TrainingRun, DataPointEvaluation, ModelEvaluation, CurrentProjectData
from app.backend.dtos.response import ComplexDataPointEvaluationDTO, ComplexDatasetDTO, ComplexModelDTO, ComplexModelEvaluationDTO, CurrentProjectDataDTO, DataPointDTO, DataPointEvaluationDTO, DatasetDTO, ModelDTO, ModelEvaluationDTO, ModelWithOriginalProjectDTO, ProjectDTO, SimpleDataPointDTO, SimpleProjectDTO, SimpleTrainingRunDTO, TrainingRunDTO


class MapperFacade:
    """
    A facade class to encapsulate all entity to DTO mappers.

    Methods:
        map_project_to_dto: Converts a Project entity to ProjectDTO.
        map_project_to_simple_dto: Converts a Project entity to SimpleProjectDTO.
        map_dataset_to_dto: Converts a Dataset entity to DatasetDTO.
        map_dataset_to_complex_dto: Converts a Dataset entity to ComplexDatasetDTO.
        map_datapoint_to_dto: Converts a DataPoint entity to DataPointDTO.
        map_datapoint_to_simple_dto: Converts a DataPoint entity to SimpleDataPointDTO.
        map_datapoint_to_training_datapoint_dto: Converts a DataPoint entity to DataPointDTO (Training).
        map_model_to_dto: Converts a Model entity to ModelDTO.
        map_model_to_dto_with_original_project: Converts a Model entity to ModelWithOriginalProjectDTO.
        map_model_to_complex_dto: Converts a Model entity to ComplexModelDTO.
        map_model_evaluation_to_dto: Converts a ModelEvaluation entity to ModelEvaluationDTO.
        map_training_run_to_dto: Converts a TrainingRun entity to TrainingRunDTO.
        map_training_run_to_simple_dto: Converts a TrainingRun entity to SimpleTrainingRunDTO.
        map_current_project_data_to_dto: Converts a CurrentProjectData entity to CurrentProjectDataDTO.
        map_datapoint_evaluation_to_dto: Converts a DataPointEvaluation entity to DataPointEvaluationDTO.
        map_datapoint_evaluation_to_complex_dto: Converts a DataPointEvaluation entity to ComplexDataPointEvaluationDTO.
        map_model_evaluation_to_complex_dto: Converts a ModelEvaluation entity to ComplexModelEvaluationDTO.
    """

    def __init__(self):
        """
        Initialize the MapperFacade class.
        """
        pass

    def map_project_to_dto(self, session: Session, project_entity: Project) -> ProjectDTO:
        """
        Convert a Project entity to ProjectDTO.

        Args:
            session (Session): SQLAlchemy session.
            project_entity (Project): Project entity to be converted.

        Returns:
            ProjectDTO: Data transfer object for Project.
        """
        schema = ProjectSchema(session=session)
        return schema.dump(project_entity)

    def map_project_to_simple_dto(self, session: Session, project_entity: Project) -> SimpleProjectDTO:
        """
        Convert a Project entity to SimpleProjectDTO.

        Args:
            session (Session): SQLAlchemy session.
            project_entity (Project): Project entity to be converted.

        Returns:
            SimpleProjectDTO: Simplified data transfer object for Project.
        """
        schema = SimpleProjectSchema(session=session)
        return schema.dump(project_entity)

    def map_dataset_to_dto(self, session: Session, dataset_entity: Dataset) -> DatasetDTO:
        """
        Convert a Dataset entity to DatasetDTO.

        Args:
            session (Session): SQLAlchemy session.
            dataset_entity (Dataset): Dataset entity to be converted.

        Returns:
            DatasetDTO: Data transfer object for Dataset.
        """
        schema = DatasetSchema(session=session)
        return schema.dump(dataset_entity)

    def map_dataset_to_complex_dto(self, session: Session, dataset_entity: Dataset) -> ComplexDatasetDTO:
        """
        Convert a Dataset entity to ComplexDatasetDTO.

        Args:
            session (Session): SQLAlchemy session.
            dataset_entity (Dataset): Dataset entity to be converted.

        Returns:
            ComplexDatasetDTO: Complex data transfer object for Dataset.
        """
        schema = ComplexDatasetSchema(session=session)
        return schema.dump(dataset_entity)

    def map_datapoint_to_dto(self, session: Session, datapoint_entity: DataPoint) -> DataPointDTO:
        """
        Convert a DataPoint entity to DataPointDTO.

        Args:
            session (Session): SQLAlchemy session.
            datapoint_entity (DataPoint): DataPoint entity to be converted.

        Returns:
            DataPointDTO: Data transfer object for DataPoint.
        """
        schema = DataPointSchema(session=session)
        return schema.dump(datapoint_entity)

    def map_datapoint_to_simple_dto(self, session: Session, datapoint_entity: DataPoint) -> SimpleDataPointDTO:
        """
        Convert a DataPoint entity to SimpleDataPointDTO.

        Args:
            session (Session): SQLAlchemy session.
            datapoint_entity (DataPoint): DataPoint entity to be converted.

        Returns:
            SimpleDataPointDTO: Simplified data transfer object for DataPoint.
        """
        schema = SimpleDataPointSchema(session=session)
        return schema.dump(datapoint_entity)

    def map_datapoint_to_training_datapoint_dto(self, session: Session, datapoint_entity: DataPoint) -> DataPointDTO:
        """
        Convert a DataPoint entity to DataPointDTO for training purposes.

        Args:
            session (Session): SQLAlchemy session.
            datapoint_entity (DataPoint): DataPoint entity to be converted.

        Returns:
            DataPointDTO: Data transfer object for DataPoint.
        """
        schema = TrainingDataPointSchema(session=session)
        return schema.dump(datapoint_entity)

    def map_model_to_dto(self, session: Session, model_entity: Model) -> ModelDTO:
        """
        Convert a Model entity to ModelDTO.

        Args:
            session (Session): SQLAlchemy session.
            model_entity (Model): Model entity to be converted.

        Returns:
            ModelDTO: Data transfer object for Model.
        """
        schema = ModelSchema(session=session)
        return schema.dump(model_entity)

    def map_model_to_dto_with_original_project(self, session: Session, model_entity: Model, project_entity: Project) -> ModelWithOriginalProjectDTO:
        """
        Convert a Model entity to ModelWithOriginalProjectDTO.

        Args:
            session (Session): SQLAlchemy session.
            model_entity (Model): Model entity to be converted.
            project_entity (Project): Associated Project entity.

        Returns:
            ModelWithOriginalProjectDTO: Data transfer object for Model with original project information.
        """
        schema = ModelWithOriginalProjectSchema(
            session=session, context={'project': project_entity})
        return schema.dump(model_entity)

    def map_model_to_complex_dto(self, session: Session, model_entity: Model) -> ComplexModelDTO:
        """
        Convert a Model entity to ComplexModelDTO.

        Args:
            session (Session): SQLAlchemy session.
            model_entity (Model): Model entity to be converted.

        Returns:
            ComplexModelDTO: Complex data transfer object for Model.
        """
        schema = ComplexModelSchema(session=session)
        return schema.dump(model_entity)

    def map_model_evaluation_to_dto(self, session: Session, model_evaluation_entity: ModelEvaluation) -> ModelEvaluationDTO:
        """
        Convert a ModelEvaluation entity to ModelEvaluationDTO.

        Args:
            session (Session): SQLAlchemy session.
            model_evaluation_entity (ModelEvaluation): ModelEvaluation entity to be converted.

        Returns:
            ModelEvaluationDTO: Data transfer object for ModelEvaluation.
        """
        schema = ModelEvaluationSchema(session=session)
        return schema.dump(model_evaluation_entity)

    def map_training_run_to_dto(self, session: Session, training_run_entity: TrainingRun) -> TrainingRunDTO:
        """
        Convert a TrainingRun entity to TrainingRunDTO.

        Args:
            session (Session): SQLAlchemy session.
            training_run_entity (TrainingRun): TrainingRun entity to be converted.

        Returns:
            TrainingRunDTO: Data transfer object for TrainingRun.
        """
        schema = TrainingRunSchema(session=session)
        return schema.dump(training_run_entity)

    def map_training_run_to_simple_dto(self, session: Session, training_run_entity: TrainingRun) -> SimpleTrainingRunDTO:
        """
        Convert a TrainingRun entity to SimpleTrainingRunDTO.

        Args:
            session (Session): SQLAlchemy session.
            training_run_entity (TrainingRun): TrainingRun entity to be converted.

        Returns:
            SimpleTrainingRunDTO: Simplified data transfer object for TrainingRun.
        """
        schema = SimpleTrainingRunSchema(session=session)
        return schema.dump(training_run_entity)

    def map_current_project_data_to_dto(self, session: Session, current_project_data: CurrentProjectData) -> CurrentProjectDataDTO:
        """
        Convert a CurrentProjectData entity to CurrentProjectDataDTO.

        Args:
            session (Session): SQLAlchemy session.
            current_project_data (CurrentProjectData): CurrentProjectData entity to be converted.

        Returns:
            CurrentProjectDataDTO: Data transfer object for CurrentProjectData.
        """
        schema = CurrentProjectDataSchema(session=session)
        return schema.dump(current_project_data)

    def map_datapoint_evaluation_to_dto(self, session: Session, current_project_data: DataPointEvaluation) -> DataPointEvaluationDTO:
        """
        Convert a DataPointEvaluation entity to DataPointEvaluationDTO.

        Args:
            session (Session): SQLAlchemy session.
            current_project_data (DataPointEvaluation): DataPointEvaluation entity to be converted.

        Returns:
            DataPointEvaluationDTO: Data transfer object for DataPointEvaluation.
        """
        schema = DataPointEvaluationSchema(session=session)
        return schema.dump(current_project_data)

    def map_datapoint_evaluation_to_complex_dto(self, session: Session, current_project_data: DataPointEvaluation) -> ComplexDataPointEvaluationDTO:
        """
        Convert a DataPointEvaluation entity to ComplexDataPointEvaluationDTO.

        Args:
            session (Session): SQLAlchemy session.
            current_project_data (DataPointEvaluation): DataPointEvaluation entity to be converted.

        Returns:
            ComplexDataPointEvaluationDTO: Complex data transfer object for DataPointEvaluation.
        """
        schema = ComplexDataPointEvaluationSchema(session=session)
        return schema.dump(current_project_data)

    def map_model_evaluation_to_complex_dto(self, session: Session, model_evaluation_entity: ModelEvaluation) -> ComplexModelEvaluationDTO:
        """
        Convert a ModelEvaluation entity to ComplexModelEvaluationDTO.

        Args:
            session (Session): SQLAlchemy session.
            model_evaluation_entity (ModelEvaluation): ModelEvaluation entity to be converted.

        Returns:
            ComplexModelEvaluationDTO: Complex data transfer object for ModelEvaluation.
        """
        schema = ComplexModelEvaluationSchema(session=session)
        return schema.dump(model_evaluation_entity)
