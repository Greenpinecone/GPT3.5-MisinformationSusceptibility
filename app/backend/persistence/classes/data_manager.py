from contextlib import contextmanager
import datetime
from sqlalchemy import Engine, create_engine, func
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound, NoResultFound
from ...database.schema import AugmentationType, Base, DatasetCategory, Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun
from ...util.logger import Logger

# Instantiates a new database or loads the currently


class DataManager:
    def __init__(self, dest_directory='database', db_filename='streamlit_app.db'):
       # Move up one directory from the current file's directory
        parent_dir = Path(__file__).parent.parent
        # Go into the /database directory and specify the database file
        db_path = parent_dir / dest_directory / db_filename
        # Use the 'sqlite:///' prefix and the absolute path to create the engine
        self.engine: Engine = create_engine(f'sqlite:///{db_path}', echo=True)
        Base.metadata.create_all(self.engine)
        self.Session: sessionmaker = sessionmaker(bind=self.engine)
        self.logger = Logger(__name__)

    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Session rollback due to exception: {e}")
            raise
        finally:
            session.close()

    # CREATE / UPDATE
    # For creating or updating a project
    def save_projects(self, projects_data: List[Dict[str: Any]]) -> List[Project]:
        self.logger.debug(
            f"Projects data: {projects_data}")
        saved_projects = []
        with self.get_session() as session:
            try:
                for project_data in projects_data:
                    project_id = getattr(project_data, 'id', None)
                    if project_id:
                        project = session.query(Project).filter(
                            Project.id == project_id).first()
                        if project:
                            for key, value in project_data.items():
                                setattr(project, key, value)
                    else:
                        project = Project(**project_data)
                        session.add(project)
                    saved_projects.append(project)
                return saved_projects
            except SQLAlchemyError as e:
                self.logger.exception("Failed to save or update projects")
                raise SQLAlchemyError(
                    "Failed to save or update projects") from e

    # For creating or updating a dataset

    def save_datasets(self, datasets_data: List[Dict[str: Any]]) -> List[Dataset]:
        self.logger.debug(
            f"Datasets data: {datasets_data}")
        saved_datasets = []
        with self.get_session() as session:
            try:
                for dataset_data in datasets_data:
                    dataset_id = getattr(dataset_data, 'id', None)
                    if dataset_id:
                        dataset = session.query(Dataset).filter(
                            Dataset.id == dataset_id).first()
                        if dataset:
                            for key, value in dataset_data.items():
                                setattr(dataset, key, value)
                    else:
                        dataset = Dataset(**dataset_data)
                        session.add(dataset)
                    saved_datasets.append(dataset)
                return saved_datasets
            except SQLAlchemyError as e:
                self.logger.exception("Failed to save or update datasets")
                raise SQLAlchemyError(
                    "Failed to save or update datasets") from e

    # For creating or updating datapoints

    def save_datapoints(self, datapoints_data: List[Dict[str: Any]]) -> List[DataPoint]:
        self.logger.debug(
            f"Datapoints data: {datapoints_data}")
        with self.get_session() as session:
            saved_datapoints = []
            try:
                for datapoint_data in datapoints_data:
                    datapoint_id = datapoint_data.get('id')
                    if datapoint_id:
                        datapoint = session.query(DataPoint).filter_by(
                            id=datapoint_id).first()
                        if datapoint:
                            for key, value in datapoint_data.items():
                                setattr(datapoint, key, value)
                    else:
                        datapoint = DataPoint(**datapoint_data)
                        session.add(datapoint)
                    saved_datapoints.append(datapoint)
                return saved_datapoints
            except SQLAlchemyError as e:
                self.logger.exception("Failed to save or update datapoints")
                raise SQLAlchemyError(
                    "Failed to save or update datapoints") from e

    # def add_datapoints_to_dataset(self, dataset_id: int, datapoints_data: List[Dict[str, Any]]) -> List[DataPoint]:
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
    #             self.logger.error(f"Failed to add datapoints to dataset: {e}")
    #             raise

    # For adding multiple datasets to a project.
    # def add_datasets_to_project(self, project_id: int, dataset_ids: List[int]) -> List[Project]:
    #     self.logger.debug(
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
    #             self.logger.error(f"Failed to add datasets to project: {e}")
    #             raise

    # For creating or updating a model

    def save_models(self, models_data: List[Dict[str: Any]]) -> List[Model]:
        self.logger.debug(f"Models data: {models_data}")
        saved_models = []
        with self.get_session() as session:
            try:
                for model_data in models_data:
                    model_id = getattr(model_data, 'id', None)
                    if model_id:
                        model = session.query(Model).filter_by(
                            id=model_id).first()
                        if model:
                            for key, value in model_data.items():
                                setattr(model, key, value)
                    else:
                        model = Model(**model_data)
                        session.add(model)
                    saved_models.append(model)
                return saved_models
            except SQLAlchemyError as e:
                self.logger.exception("Failed to create or update models")
                raise SQLAlchemyError(
                    "Failed to create or update models") from e

    # For creating or updating model evaluations
    def save_model_evaluations(self, evaluations_data: List[Dict[str: Any]]) -> List[ModelEvaluation]:
        self.logger.debug(
            f"Evaluations data: {evaluations_data}")
        with self.get_session() as session:
            saved_evaluations = []
            try:
                for eval_data in evaluations_data:
                    evaluation_id = eval_data.get('id')
                    if evaluation_id:
                        evaluation = session.query(ModelEvaluation).filter_by(
                            id=evaluation_id).first()
                        if evaluation:
                            for key, value in eval_data.items():
                                setattr(evaluation, key, value)
                    else:
                        evaluation = ModelEvaluation(**eval_data)
                        session.add(evaluation)
                    saved_evaluations.append(evaluation)
                return saved_evaluations
            except SQLAlchemyError as e:
                self.logger.exception(
                    "Failed to save or update model evaluations")
                raise SQLAlchemyError(
                    "Failed to save or update model evaluations") from e

    # For creating or updating a training run

    def save_training_runs(self, runs_data: List[Dict[str: Any]]) -> List[TrainingRun]:
        self.logger.debug(
            f"Training runs data: {runs_data}")
        saved_runs = []
        with self.get_session() as session:
            try:
                for run_data in runs_data:
                    run_id = getattr(run_data, 'id', None)
                    if run_id:
                        training_run = session.query(
                            TrainingRun).filter_by(id=run_id).first()
                        if training_run:
                            for key, value in run_data.items():
                                setattr(training_run, key, value)
                    else:
                        training_run = TrainingRun(**run_data)
                        session.add(training_run)
                    saved_runs.append(training_run)
                return saved_runs
            except SQLAlchemyError as e:
                self.logger.exception("Failed to save or update training runs")
                raise SQLAlchemyError(
                    "Failed to save or update training runs") from e

    # GET
    # For retrieveing all projects filterable by name and creation date

    def get_all_projects(self, project_data: Dict[str: Any]) -> List[Project]:
        self.logger.debug(
            f"Project data: {project_data}")
        with self.get_session() as session:
            try:
                query = session.query(Project)
                if project_data.project_name:
                    query = query.filter(
                        Project.project_name.ilike(f"%{project_data.project_name}%"))
                if project_data.creation_date:
                    # Assuming creation_date is a datetime.date object and timestamp is a datetime column
                    query = query.filter(
                        func.date(Project.created_at) == project_data.created_at)
                projects = query.all()
                return projects
            except SQLAlchemyError as e:
                self.logger.exception("Failed to retrieve projects")
                raise SQLAlchemyError("Failed to retrieve projects") from e

    # For retrieving all models associated with a project filterable by name and version

    def get_models_by_project_id(self, model_project_data: Dict[str: Any]) -> List[Model]:
        self.logger.debug(
            f"Model_project_data: {model_project_data}")
        with self.get_session() as session:
            try:
                query = session.query(Model).filter(
                    Model.project_id == model_project_data.project_id).one()
                if model_project_data.name:
                    query = query.filter(Model.model_name.ilike(
                        f"%{model_project_data.name}%"))
                if model_project_data.version is not None:
                    query = query.filter(
                        Model.version == model_project_data.version)
                models = query.all()
                return models
            except MultipleResultsFound as e:
                self.logger.exception(
                    "Too many projects found when trying to get models by project id")
                raise MultipleResultsFound(
                    "Too many projects found when trying to get models by project id") from e
            except NoResultFound as e:
                self.logger.exception(
                    "No project found when trying to get models by project id")
                raise NoResultFound(
                    "No project found when trying to get models by project id") from e
            except SQLAlchemyError as e:
                self.logger.exception("Failed to retrieve models for project")
                raise SQLAlchemyError(
                    "Failed to retrieve models for project") from e

    # Retrieve all datasets associated with a model filterable by dataset name, augmented and dataset category
    def get_datasets_by_model_id(self, dataset_model_data: Dict[str: Any]) -> List[Dataset]:
        self.logger.debug(
            f"Dataset_model_data: {dataset_model_data}")
        with self.get_session() as session:
            try:
                model = session.query(Model).filter_by(
                    id=dataset_model_data.model_id).one()

                datasets = model.datasets
                if dataset_model_data.created_at:
                    datasets = [
                        ds for ds in datasets if ds.created_at.date() == dataset_model_data.created_at]
                if dataset_model_data.dataset_name:
                    datasets = [
                        ds for ds in datasets if dataset_model_data.dataset_name.lower() in ds.dataset_name.lower()]
                if dataset_model_data.augmented is not None:
                    datasets = [
                        ds for ds in datasets if ds.augmented == dataset_model_data.augmented]
                if dataset_model_data.category:
                    datasets = [
                        ds for ds in datasets if ds.category == dataset_model_data.category]

                return datasets
            except MultipleResultsFound as e:
                self.logger.exception(
                    "Too many models found when trying to get model by id.")
                raise MultipleResultsFound(
                    "Too many models found. Expected only one.") from e
            except NoResultFound as e:
                self.logger.exception(
                    "No models found when trying to get model by id.")
                raise NoResultFound("No models found for the given ID.") from e
            except SQLAlchemyError as e:
                self.logger.exception("Failed to retrieve datasets for model.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving datasets for the model.") from e

    # Retrieve dataset specific datapoints filterable by coherence score, relevance score, semantic similarity score and augmentation type
    def get_datapoints_by_dataset_id(self, dataset_datapoints_data: Dict[str: Any]) -> List[DataPoint]:
        self.logger.debug(f"""Dataset_datapoints_data: {
                          dataset_datapoints_data}""")
        with self.get_session() as session:
            try:
                # Retrieve the dataset by its ID
                dataset = session.query(Dataset).filter_by(
                    id=dataset_datapoints_data.dataset_id).one()

                # Filter datapoints directly from the dataset's datapoints collection
                datapoints = dataset.datapoints
                if dataset_datapoints_data.coherence_score is not None:
                    datapoints = [
                        dp for dp in datapoints if dp.coherence_score == dataset_datapoints_data.coherence_score]
                if dataset_datapoints_data.relevance_score is not None:
                    datapoints = [
                        dp for dp in datapoints if dp.relevance_score == dataset_datapoints_data.relevance_score]
                if dataset_datapoints_data.semantic_similarity is not None:
                    datapoints = [
                        dp for dp in datapoints if dp.semantic_similarity_score == dataset_datapoints_data.semantic_similarity]
                if dataset_datapoints_data.augmentation_type is not None:
                    datapoints = [
                        dp for dp in datapoints if dp.augmentation_type == dataset_datapoints_data.augmentation_type]
                if dataset_datapoints_data.category is not None:
                    datapoints = [
                        dp for dp in datapoints if dp.category == dataset_datapoints_data.category]

                return datapoints
            except MultipleResultsFound as e:
                self.logger.exception(
                    "Too many datasets found when trying to get dataset by id.")
                raise MultipleResultsFound(
                    "Too many datasets found. Expected only one.") from e
            except NoResultFound as e:
                self.logger.exception(
                    "No dataset found when trying to get dataset by id.")
                raise NoResultFound(
                    "No dataset found for the given ID.") from e
            except SQLAlchemyError as e:
                self.logger.exception(
                    "Failed to retrieve datapoints from dataset.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving datapoints.") from e

    # The function to retrieve all model evaluations remains as is, correctly fetching all evaluations for a given model

    def get_model_evaluations_by_model_id(self, model_id: int) -> List[ModelEvaluation]:
        self.logger.debug(f"Model id: {model_id}")
        with self.get_session() as session:
            try:
                model = session.query(Model).filter_by(id=model_id).one()
                return model.evaluations
            except MultipleResultsFound as e:
                self.logger.exception(
                    "Too many models found when trying to get model by id.")
                raise MultipleResultsFound(
                    "Too many models found. Expected only one.") from e
            except NoResultFound as e:
                self.logger.exception(
                    "No models found when trying to get model by id.")
                raise NoResultFound("No model found for the given ID.") from e
            except SQLAlchemyError as e:
                self.logger.exception(
                    "Failed to retrieve evaluations for model.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving model evaluations.") from e

    # Retrieve the training run of a model

    def get_training_run_by_model_id(self, model_id: int) -> List[TrainingRun]:
        self.logger.debug(f"Model id: {model_id}")
        with self.get_session() as session:
            try:
                model = session.query(Model).filter_by(id=model_id).one()
                return [model.training_run] if model.training_run is not None else []
            except MultipleResultsFound as e:
                self.logger.exception(
                    "Too many models found when trying to get model by id.")
                raise MultipleResultsFound(
                    "Too many models found. Expected only one.") from e
            except NoResultFound as e:
                self.logger.exception(
                    "No models found when trying to get model by id.")
                raise NoResultFound("No model found for the given ID.") from e
            except SQLAlchemyError as e:
                self.logger.exception("Failed to retrieve model by id.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving the model.") from e

    def get_model_by_id(self, model_id: int) -> List[Model]:
        self.logger.debug(f"Model id: {model_id}")
        """Retrieve a model by its ID."""
        with self.get_session() as session:
            try:
                result = session.query(Model).filter_by(id=model_id).one()
                return [result]
            except MultipleResultsFound as e:
                self.logger.exception(
                    "Too many models found when trying to get model by id.")
                raise MultipleResultsFound(
                    "Multiple models found. Expected only one.") from e
            except NoResultFound as e:
                self.logger.exception(
                    "No models found when trying to get model by id.")
                raise NoResultFound("No model found for the given ID.") from e
            except SQLAlchemyError as e:
                self.logger.exception("Failed to retrieve model by id.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving model by id.") from e

    def get_dataset_by_id(self, dataset_id: int) -> List[Dataset]:
        self.logger.debug(f"Dataset id: {dataset_id}")
        """Retrieve a dataset by its ID."""
        with self.get_session() as session:
            try:
                result = session.query(Dataset).filter_by(id=dataset_id).one()
                return [result]
            except MultipleResultsFound as e:
                self.logger.exception(
                    "Too many datasets found when trying to get dataset by id.")
                raise MultipleResultsFound(
                    "Multiple datasets found. Expected only one.") from e
            except NoResultFound as e:
                self.logger.exception(
                    "No dataset found when trying to get dataset by id.")
                raise NoResultFound(
                    "No dataset found for the given ID.") from e
            except SQLAlchemyError as e:
                self.logger.exception("Failed to retrieve dataset by id.")
                raise SQLAlchemyError(
                    "A database error occurred while retrieving dataset by id.") from e

    def get_project_by_id(self, project_id: int) -> List[Project]:
        self.logger.debug(f"Project id: {project_id}")
        """Retrieve a project by its ID."""
        with self.get_session() as session:
            try:
                result = session.query(Project).filter_by(id=project_id).one()
                return [result]
            except MultipleResultsFound as e:
                self.logger.exception(
                    "Too many projects found when trying to get project by id.")
                raise MultipleResultsFound(
                    "Multiple projects found. Expected only one.") from e
            except NoResultFound as e:
                self.logger.exception(
                    "No project found when trying to get project by id.")
                raise NoResultFound(
                    "No project found for the given ID.") from e
            except SQLAlchemyError as e:
                self.logger.error(
                    f"Failed to retrieve project by id: {e}")
                raise SQLAlchemyError(
                    "A database error occured while trying to retrieve project by ID.") from e

    def get_training_run_by_id(self, training_run_id: int) -> List[TrainingRun]:
        self.logger.debug(f"Training run id: {training_run_id}")
        """Retrieve a training run by its ID."""
        with self.get_session() as session:
            try:
                result = session.query(TrainingRun).filter_by(
                    id=training_run_id).one()
                return [result]
            except MultipleResultsFound as e:
                self.logger.exception(
                    "Too many training runs found when trying to get training run by id.")
                raise MultipleResultsFound(
                    "Multiple training runs found. Expected only one.") from e
            except NoResultFound as e:
                self.logger.exception(
                    "No training run found when trying to get training run by id.")
                raise NoResultFound(
                    "No training run found for the given ID.") from e
            except SQLAlchemyError as e:
                self.logger.error(
                    f"Failed to retrieve training run by id: {e}")
                raise SQLAlchemyError(
                    "A database error occured while trying to retrieve training run by ID.") from e

    def get_datapoint_by_id(self, datapoint_id: int) -> List[DataPoint]:
        self.logger.debug(f"Datapoint id: {datapoint_id}")
        """Retrieve a datapoint by its ID."""
        with self.get_session() as session:
            try:
                result = session.query(DataPoint).filter_by(
                    id=datapoint_id).all()
                return [result]
            except MultipleResultsFound as e:
                self.logger.exception(
                    "Too many datapoints found when trying to get datapoint by id.")
                raise MultipleResultsFound(
                    "Multiple datapoints found. Expected only one.") from e
            except NoResultFound as e:
                self.logger.exception(
                    "No datapoint found when trying to get datapoint by id.")
                raise NoResultFound(
                    "No datapoint found for the given ID.") from e
            except SQLAlchemyError as e:
                self.logger.exception(
                    "A database error occurred while trying to retrieve a datapoint.")
                raise SQLAlchemyError(
                    "A database orccured while trying to retrieve datapoint by ID.") from e
