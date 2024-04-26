from contextlib import contextmanager
import datetime
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session, joinedload
from sqlalchemy.orm.query import Query
from pathlib import Path
from typing import Dict, Any, Optional, Generator
from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound, NoResultFound
from ...database.schema import AugmentationType, Base, DatasetCategory, Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun
from ...util.logger import Logger
from ..interfaces.i_data_manager import IDataManager
from datetime import datetime
from ...dtos.create_request import *
from ...dtos.get_request import *
from ...mapper.implementations.mappers_facade import MapperFacade
from ...dtos.response import *

# Instantiates a new database or loads the currently

# Define the logger as a class attribute
logger = Logger(__name__)


class DataManager(IDataManager):

    def __init__(self,  mapper: MapperFacade, dest_directory: str = 'database', db_filename: str = 'streamlit_app.db'):
        self.mapper = mapper
       # Move up one directory from the current file's directory
        parent_dir: Path = Path(__file__).parent.parent.parent
        # Go into the /database directory and specify the database file
        db_path: Path = parent_dir / dest_directory / db_filename
        # Use the 'sqlite:///' prefix and the absolute path to create the engine
        self.engine: Engine = create_engine(f'sqlite:///{db_path}', echo=True)
        Base.metadata.create_all(self.engine)
        self.session: sessionmaker = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self.session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rollback due to exception: {e}")
            raise
        finally:
            session.close()

    # CREATE / UPDATE
    # For creating or updating a project
    def save_projects(self, projects_data: list[CreateProjectDTO]) -> list[ProjectDTO]:
        saved_projects: list[Project] = []
        with self.get_session() as session:
            try:
                for project_dto in projects_data:
                    project = None
                    if getattr(project_dto, 'id', None):
                        project = session.get(Project, project_dto.id)
                       # Correct id will be checked by not yet implemented update request validator
                    else:
                        project = Project()
                        # Add and add required values immediately after retrieving or creating to avoid auto flush inconsistencies on queries
                        session.add(project)

                    project.project_name = project_dto.project_name
                    project.description = project_dto.description

                    if project_dto.model_ids:
                        models = session.query(Model).filter(
                            Model.id.in_(project_dto.model_ids)).all()
                        project.models = models

                    if project_dto.dataset_ids:
                        datasets = session.query(Dataset).filter(
                            Dataset.id.in_(project_dto.dataset_ids)).all()
                        project.datasets = datasets

                    saved_projects.append(project)

                # Must be flushed to create primary key / datetime etc.
                session.flush()
                return [self.mapper.map_project_to_dto(project) for project in saved_projects]
            except Exception as e:
                logger.exception(
                    f"Failed to save or update projects due to error: {e}")
                # Re-raise the exception to notify the caller of the failure
                raise Exception(
                    "Failed to save or update projects due to error.") from e

    # For creating or updating a dataset

    def save_datasets(self, datasets_data: list[CreateDatasetDTO]) -> list[DatasetDTO]:
        saved_datasets: list[Dataset] = []
        with self.get_session() as session:
            try:
                for dataset_dto in datasets_data:
                    if getattr(dataset_dto, 'id', None):
                        dataset = session.get(Dataset, dataset_dto.id)
                        # Correct id will be checked by not yet implemented update request validator

                    else:
                        dataset = Dataset()
                        # Add and add required values immediately after retrieving or creating to avoid auto flush inconsistencies on queries
                        session.add(dataset)

                    dataset.dataset_name = dataset_dto.dataset_name
                    dataset.augmented = dataset_dto.augmented
                    dataset.category = dataset_dto.category

                    # Handling initial and test dataset relationships
                    if dataset_dto.initial_dataset_id is not None:
                        initial_dataset = session.get(Dataset,
                                                      dataset_dto.initial_dataset_id)
                        dataset.initial_dataset = initial_dataset

                    if dataset_dto.test_dataset_id is not None:
                        test_dataset = session.get(Dataset,
                                                   dataset_dto.test_dataset_id)
                        dataset.test_dataset = test_dataset

                    # Handling project relationships
                    if dataset_dto.project_ids:
                        projects = session.query(Project).filter(
                            Project.id.in_(dataset_dto.project_ids)).all()
                        dataset.projects = projects

                    # Handling datapoint relationships
                    if dataset_dto.datapoint_ids:
                        datapoints = session.query(DataPoint).filter(
                            DataPoint.id.in_(dataset_dto.datapoint_ids)).all()
                        dataset.datapoints = datapoints

                    saved_datasets.append(dataset)

                # Must be flushed to create primary key / datetime etc.
                session.flush()
                return [self.mapper.map_dataset_to_dto(dataset) for dataset in saved_datasets]

            except Exception as e:
                self.logger.error(
                    f"Failed to save or update datasets due to error: {e}")
                # Re-raise the exception to notify the caller of the failure
                raise Exception(
                    "Failed to save or update datasets due to error.") from e

    # For creating or updating datapoints
    def save_datapoints(self, datapoints_data: list[CreateDataPointDTO]) -> list[DataPointDTO]:
        saved_datapoints: list[DataPoint] = []
        with self.get_session() as session:
            try:
                for datapoint_dto in datapoints_data:
                    if getattr(datapoint_dto, 'id', None):
                        datapoint = session.get(DataPoint, datapoint_dto.id)
                    else:
                        datapoint = DataPoint()
                        # Add and add required values immediately after retrieving or creating to avoid auto flush inconsistencies on queries
                        session.add(datapoint)
                        datapoint.dataset_id = datapoint_dto.dataset_id

                    datapoint.messages = datapoint_dto.messages
                    datapoint.category = datapoint_dto.category
                    # Fetch the Dataset object
                    dataset = session.get(Dataset, datapoint_dto.dataset_id)
                    datapoint.dataset = dataset

                    # Fetch the initial DataPoint object, if specified
                    if datapoint_dto.initial_datapoint_id:
                        initial_datapoint = session.get(
                            DataPoint, datapoint_dto.initial_datapoint_id)
                        datapoint.initial_datapoint = initial_datapoint

                    datapoint.coherence_score = datapoint_dto.coherence_score
                    datapoint.relevance_score = datapoint_dto.relevance_score
                    datapoint.semantic_similarity_score = datapoint_dto.semantic_similarity_score
                    datapoint.augmentation_type = datapoint_dto.augmentation_type

                    saved_datapoints.append(datapoint)

                # Must be flushed to create primary key / datetime etc.
                session.flush()
                return [self.mapper.map_datapoint_to_dto(datapoint) for datapoint in saved_datapoints]
            except Exception as e:
                logger.exception(
                    "Failed to save or update datapoints.")
                raise Exception("Failed to save or update datapoints.") from e

    # def add_datapoints_to_dataset(self, dataset_id: int, datapoints_data: list[Dict[str, Any]]) -> list[DataPoint]:
    #     with self.get_session() as session:
    #         try:
    #             added_datapoints = []
    #             for dp_data in datapoints_data:
    #                 dp_data['dataset_id'] = dataset_id
    #                 datapoint = DataPoint(**dp_data)
    #                 session.add(datapoint)
    #                 added_datapoints.append(datapoint)
    #             return added_datapoints
    #         except SQLAlchemyError as e:
    #             logger.error(f"Failed to add datapoints to dataset: {e}")
    #             raise

    # For adding multiple datasets to a project.
    # def add_datasets_to_project(self, project_id: int, dataset_ids: list[int]) -> list[Project]:
    #     logger.debug(
    #         f"Project id: {project_id}, dataset ids: {dataset_ids}")
    #     with self.get_session() as session:
    #         try:
    #             project = session.query(Project).filter(
    #                 Project.id == project_id).one()
    #             for dataset_id in dataset_ids:
    #                 dataset = session.query(Dataset).filter(
    #                     Dataset.id == dataset_id).one()
    #                 project.datasets.append(dataset)
    #             return [project]
    #         except SQLAlchemyError as e:
    #             logger.error(f"Failed to add datasets to project: {e}")
    #             raise

    # For creating or updating a model

    def save_models(self, models_data: list[CreateModelDTO]) -> list[ModelDTO]:
        saved_models: list[Model] = []
        with self.get_session() as session:
            try:
                for model_dto in models_data:
                    model = None
                    model_id = getattr(model_dto, 'id', None)
                    if model_id:
                        model = session.get(Model, model_id)
                        # Correct id will be checked by not yet implemented update request validator
                    else:
                        model = Model()
                        # Add and add required values immediately after retrieving or creating to avoid auto flush inconsistencies on queries
                        session.add(model)

                    model.model_name = model_dto.model_name
                    model.version = model_dto.version
                    model.project_id = model_dto.project_id

                    # Associate project
                    project = session.get(Project, model_dto.project_id)
                    model.project = project

                    # Associate datasets
                    datasets = session.query(Dataset).filter(
                        Dataset.id.in_(model_dto.dataset_ids)).all()
                    model.datasets = datasets

                    # Handle parent_model_id if present
                    if model_dto.parent_model_id is not None:
                        parent_model = session.get(
                            Model, model_dto.parent_model_id)
                        model.parent_model = parent_model

                    # Handle training_run_id if present
                    if model_dto.training_run_id is not None:
                        training_run = session.get(
                            TrainingRun, model_dto.training_run_id)
                        model.training_run = training_run

                    saved_models.append(model)

                # Must be flushed to create primary key / datetime etc.
                session.flush()
                return [self.mapper.map_model_to_dto(model) for model in saved_models]

            except Exception as e:
                logger.exception(
                    f"Failed to save or update models due to error: {e}")
                raise Exception(
                    "Failed to save or update models due to error.") from e

    # For creating or updating model evaluations
    def save_model_evaluations(self, evaluations_data: list[CreateModelEvaluationDTO]) -> list[ModelEvaluationDTO]:
        saved_evaluations: list[ModelEvaluation] = []
        with self.get_session() as session:
            try:
                for eval_dto in evaluations_data:
                    evaluation = None
                    evaluation_id = getattr(eval_dto, 'id', None)
                    if evaluation_id:
                        evaluation = session.get(
                            ModelEvaluation, evaluation_id)
                        # Correct id will be checked by not yet implemented update request validator
                    else:
                        # Add and add required values immediately after retrieving or creating to avoid auto flush inconsistencies on queries
                        evaluation = ModelEvaluation()
                        session.add(evaluation)

                    evaluation.model_id = eval_dto.model_id
                    evaluation.datapoint_id = eval_dto.datapoint_id
                    evaluation.evaluation_type = eval_dto.evaluation_type
                    evaluation.helpful_score = eval_dto.helpful_score
                    evaluation.honest_score = eval_dto.honest_score
                    evaluation.harmless_score = eval_dto.harmless_score

                    # Fetching the Model object based on model_id
                    model = session.get(Model, eval_dto.model_id)

                    # Fetching the DataPoint object based on datapoint_id
                    datapoint = session.get(DataPoint, eval_dto.datapoint_id)

                    # Setting the fetched objects and other attributes
                    evaluation.model = model
                    evaluation.datapoint = datapoint

                    saved_evaluations.append(evaluation)

                # Must be flushed to create primary key / datetime etc.
                session.flush()
                return [self.mapper.map_model_evaluation_to_dto(evaluation) for evaluation in saved_evaluations]

            except Exception as e:
                logger.error(
                    f"Failed to save or update model evaluations due to error: {e}")
                raise Exception(
                    "Failed to save or update model evaluations due to error.") from e

    # For creating or updating a training run
    def save_training_runs(self, runs_data: list[CreateTrainingRunDTO]) -> list[TrainingRunDTO]:
        saved_runs: list[TrainingRun] = []
        with self.get_session() as session:
            try:
                for run_dto in runs_data:
                    training_run = None
                    training_run_id = getattr(run_dto, 'id', None)
                    if training_run_id:
                        training_run = session.get(
                            TrainingRun, training_run_id)
                        # Correct id will be checked by not yet implemented update request validator
                    else:
                        training_run = TrainingRun()
                        # Add and add required values immediately after retrieving or creating to avoid auto flush inconsistencies on queries
                        session.add(training_run)

                    training_run.model_id = run_dto.model_id
                    training_run.epochs = run_dto.epochs
                    training_run.learning_rate_multiplier = run_dto.learning_rate_multiplier
                    training_run.batch_size = run_dto.batch_size

                    # Fetch the Model object using the model_id from DTO
                    model = session.get(Model, run_dto.model_id)

                    # Set fetched Model object to the training_run
                    training_run.model = model

                    saved_runs.append(training_run)

                # Must be flushed to create primary key / datetime etc.
                session.flush()
                return [self.mapper.map_training_run_to_dto(run) for run in saved_runs]

            except Exception as e:
                logger.error("Failed to save or update training runs.")
                raise Exception(
                    "Failed to save or update training runs.") from e

    # GET
    # For retrieveing all projects filterable by name and creation date

    def get_all_projects(self, project_data: GetProjectsDTO) -> list[ProjectDTO]:
        logger.debug(f"Project data: {project_data}")
        with self.get_session() as session:
            try:
                query = session.query(Project)
                project_name: str = project_data.project_name
                created_at: datetime = project_data.created_at

                if project_name:
                    query = query.filter(
                        Project.project_name.ilike(f"%{project_name}%"))
                if created_at:
                    # Assuming created_at is correctly formatted for comparison
                    query = query.filter(
                        Project.created_at == created_at)

                projects: list[Project] = query.all()
                return [self.mapper.map_project_to_dto(project) for project in projects]
            except SQLAlchemyError as e:
                logger.exception("Failed to retrieve projects")
                raise SQLAlchemyError("Failed to retrieve projects") from e

    # For retrieving all models associated with a project filterable by name and version

    def get_models_by_project_id(self, model_project_data: GetModelsByProjectIdDTO) -> list[ModelDTO]:
        logger.debug(f"Model_project_data: {model_project_data}")
        with self.get_session() as session:  # Assuming this returns a context-managed session
            try:
                # Start building the query
                query = session.query(Model).filter(
                    Model.project_id == model_project_data.project_id)

                # Additional filters based on the provided dictionary
                if model_project_data.name:
                    query = query.filter(Model.model_name.ilike(
                        f"%{model_project_data.name}%"))
                if model_project_data.version:
                    query = query.filter(
                        Model.version == model_project_data.version)

                models: list[Model] = query.all()
                return [self.mapper.map_model_to_dto(model) for model in models]
            except SQLAlchemyError as e:
                logger.exception(
                    "Failed to retrieve models for project")
                raise SQLAlchemyError(
                    "Failed to retrieve models for project") from e

    # Retrieve all datasets associated with a model filterable by dataset name, augmented and dataset category
    def get_datasets_by_model_id(self, dataset_model_data: GetDatasetsByModelIdDTO) -> list[DatasetDTO]:
        logger.debug(f"Dataset_model_data: {dataset_model_data}")
        with self.get_session() as session:  # Assuming this returns a context-managed session
            try:
                # Directly filtering datasets associated with the model_id
                query: Query = session.query(Dataset).join(Model).filter(
                    Model.id == dataset_model_data.model_id)

                # Additional filters based on the provided dictionary
                if dataset_model_data.created_at:
                    query = query.filter(
                        Dataset.created_at == dataset_model_data.created_at)
                if dataset_model_data.dataset_name:
                    query = query.filter(Dataset.dataset_name.ilike(
                        f"%{dataset_model_data.dataset_name}%"))
                if dataset_model_data.augmented:
                    query = query.filter(
                        Dataset.augmented == dataset_model_data.augmented)
                if dataset_model_data.category:
                    query = query.filter(
                        Dataset.category == dataset_model_data.category)

                datasets: list[Dataset] = query.all()
                return [self.mapper.map_dataset_to_dto(dataset) for dataset in datasets]
            except SQLAlchemyError as e:
                logger.exception(
                    "Failed to retrieve datasets for model.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving datasets for the model.") from e

    # Retrieve dataset specific datapoints filterable by coherence score, relevance score, semantic similarity score and augmentation type
    def get_datapoints_by_dataset_id(self, dataset_datapoints_data: GetDatapointsByDatasetIdDTO) -> list[DataPointDTO]:
        logger.debug(f"""Dataset_datapoints_data: {
            dataset_datapoints_data}""")
        with self.get_session() as session:  # Assuming this returns a context-managed session
            try:
                query: Query = session.query(DataPoint).filter(
                    DataPoint.dataset_id == dataset_datapoints_data.dataset_id)

                if dataset_datapoints_data.coherence_score:
                    query = query.filter(
                        DataPoint.coherence_score == dataset_datapoints_data.coherence_score)
                if dataset_datapoints_data.relevance_score:
                    query = query.filter(
                        DataPoint.relevance_score == dataset_datapoints_data.relevance_score)
                if dataset_datapoints_data.semantic_similarity:
                    query = query.filter(
                        DataPoint.semantic_similarity_score == dataset_datapoints_data.semantic_similarity)
                if dataset_datapoints_data.augmentation_type:
                    query = query.filter(
                        DataPoint.augmentation_type == dataset_datapoints_data.augmentation_type)
                if dataset_datapoints_data.category:
                    query = query.filter(
                        DataPoint.category == dataset_datapoints_data.category)

                datapoints: list[DataPoint] = query.all()
                return [self.mapper.map_datapoint_to_dto(datapoint) for datapoint in datapoints]
            except SQLAlchemyError as e:
                logger.exception(
                    "Failed to retrieve datapoints from dataset.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving datapoints.") from e

    # The function to retrieve all model evaluations remains as is, correctly fetching all evaluations for a given model

    def get_model_evaluations_by_model_id(self, model_id: int) -> list[ModelEvaluationDTO]:
        logger.debug(f"Model id: {model_id}")
        with self.get_session() as session:  # Assuming this returns a context-managed session
            try:
                evaluations: list[ModelEvaluation] = session.query(
                    ModelEvaluation).filter(ModelEvaluation.model_id == model_id).all()
                return [self.mapper.map_model_evaluation_to_dto(evaluation) for evaluation in evaluations]
            except SQLAlchemyError as e:
                logger.exception(
                    "Failed to retrieve evaluations for model.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving model evaluations.") from e

    # Retrieve the training run of a model

    def get_training_run_by_model_id(self, model_id: int) -> list[TrainingRunDTO]:
        logger.debug(f"Model id: {model_id}")
        with self.get_session() as session:
            try:
                model: Model = session.query(
                    Model).filter_by(id=model_id).one()
                return [self.mapper.map_training_run_to_dto(model.training_run)] if model.training_run is not None else []
            except MultipleResultsFound as e:
                logger.exception(
                    "Too many models found when trying to get model by id.")
                raise MultipleResultsFound(
                    "Too many models found. Expected only one.") from e
            except NoResultFound as e:
                logger.exception(
                    "No models found when trying to get model by id.")
                raise NoResultFound("No model found for the given ID.") from e
            except SQLAlchemyError as e:
                logger.exception("Failed to retrieve model by id.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving the model.") from e

    def get_model_by_id(self, model_id: int) -> list[ModelDTO]:
        logger.debug(f"Model id: {model_id}")
        """Retrieve a model by its ID."""
        with self.get_session() as session:
            try:
                model: Model = session.query(
                    Model).filter_by(id=model_id).one()
                return [self.mapper.map_model_to_dto(model)]
            except MultipleResultsFound as e:
                logger.exception(
                    "Too many models found when trying to get model by id.")
                raise MultipleResultsFound(
                    "Multiple models found. Expected only one.") from e
            except NoResultFound as e:
                logger.exception(
                    "No models found when trying to get model by id.")
                raise NoResultFound("No model found for the given ID.") from e
            except SQLAlchemyError as e:
                logger.exception("Failed to retrieve model by id.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving model by id.") from e

    def get_dataset_by_id(self, dataset_id: int) -> list[DatasetDTO]:
        logger.debug(f"Dataset id: {dataset_id}")
        """Retrieve a dataset by its ID."""
        with self.get_session() as session:
            try:
                dataset: Dataset = session.query(
                    Dataset).filter_by(id=dataset_id).one()
                return [self.mapper.map_dataset_to_dto(dataset)]
            except MultipleResultsFound as e:
                logger.exception(
                    "Too many datasets found when trying to get dataset by id.")
                raise MultipleResultsFound(
                    "Multiple datasets found. Expected only one.") from e
            except NoResultFound as e:
                logger.exception(
                    "No dataset found when trying to get dataset by id.")
                raise NoResultFound(
                    "No dataset found for the given ID.") from e
            except SQLAlchemyError as e:
                logger.exception(
                    "Failed to retrieve dataset by id.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving dataset by id.") from e

    def get_project_by_id(self, project_id: int) -> list[ProjectDTO]:
        logger.debug(f"Project id: {project_id}")
        """Retrieve a project by its ID."""
        with self.get_session() as session:
            try:
                project: Project = session.query(
                    Project).filter_by(id=project_id).one()
                return [self.mapper.map_project_to_dto(project)]
            except MultipleResultsFound as e:
                logger.exception(
                    "Too many projects found when trying to get project by id.")
                raise MultipleResultsFound(
                    "Multiple projects found. Expected only one.") from e
            except NoResultFound as e:
                logger.exception(
                    "No project found when trying to get project by id.")
                raise NoResultFound(
                    "No project found for the given ID.") from e
            except SQLAlchemyError as e:
                logger.error(
                    f"Failed to retrieve project by id: {e}")
                raise SQLAlchemyError(
                    "A database error occured while trying to retrieve project by ID.") from e

    def get_training_run_by_id(self, training_run_id: int) -> list[TrainingRunDTO]:
        logger.debug(f"Training run id: {training_run_id}")
        """Retrieve a training run by its ID."""
        with self.get_session() as session:
            try:
                training_run: TrainingRun = session.query(TrainingRun).filter_by(
                    id=training_run_id).one()
                return [self.mapper.map_training_run_to_dto(training_run)]
            except MultipleResultsFound as e:
                logger.exception(
                    "Too many training runs found when trying to get training run by id.")
                raise MultipleResultsFound(
                    "Multiple training runs found. Expected only one.") from e
            except NoResultFound as e:
                logger.exception(
                    "No training run found when trying to get training run by id.")
                raise NoResultFound(
                    "No training run found for the given ID.") from e
            except SQLAlchemyError as e:
                logger.error(
                    f"Failed to retrieve training run by id: {e}")
                raise SQLAlchemyError(
                    "A database error occured while trying to retrieve training run by ID.") from e

    def get_datapoint_by_id(self, datapoint_id: int) -> list[DataPointDTO]:
        logger.debug(f"Datapoint id: {datapoint_id}")
        """Retrieve a datapoint by its ID."""
        with self.get_session() as session:
            try:
                datapoint: DataPoint = session.query(DataPoint).filter_by(
                    id=datapoint_id).one()
                return [self.mapper.map_datapoint_to_dto(datapoint)]
            except MultipleResultsFound as e:
                logger.exception(
                    "Too many datapoints found when trying to get datapoint by id.")
                raise MultipleResultsFound(
                    "Multiple datapoints found. Expected only one.") from e
            except NoResultFound as e:
                logger.exception(
                    "No datapoint found when trying to get datapoint by id.")
                raise NoResultFound(
                    "No datapoint found for the given ID.") from e
            except SQLAlchemyError as e:
                logger.exception(
                    "A database error occurred while trying to retrieve a datapoint.")
                raise SQLAlchemyError(
                    "A database orccured while trying to retrieve datapoint by ID.") from e

    def get_model_evaluation_by_id(self, model_evlauation_id: int) -> list[ModelEvaluationDTO]:
        logger.debug(f"Model evaluation id: {model_evlauation_id}")
        """Retrieve a model evaluation by its ID."""
        with self.get_session() as session:
            try:
                model_evaluation: ModelEvaluation = session.query(ModelEvaluation).filter_by(
                    id=model_evlauation_id).one()
                return [self.mapper.map_model_evaluation_to_dto(model_evaluation)]
            except MultipleResultsFound as e:
                logger.exception(
                    "Too many datapoints found when trying to get model evaluation by id.")
                raise MultipleResultsFound(
                    "Multiple model evaluations found. Expected only one.") from e
            except NoResultFound as e:
                logger.exception(
                    "No model evaluation found when trying to get model evaluation by id.")
                raise NoResultFound(
                    "No model evaluation found for the given ID.") from e
            except SQLAlchemyError as e:
                logger.exception(
                    "A database error occurred while trying to retrieve a model evaluation.")
                raise SQLAlchemyError(
                    "A database orccured while trying to retrieve model evaluation by ID.") from e
