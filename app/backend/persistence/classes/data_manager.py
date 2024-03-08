from contextlib import contextmanager
import datetime
from sqlalchemy import Engine, create_engine, func
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from ...database.schema import AugmentationType, Base, DatasetCategory, Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun
from ...util.logger import Logger


# Instantiates a new database or loads the currently
class DataManager:
    def __init__(self, logger: Logger, dest_directory='database', db_filename='streamlit_app.db'):
       # Move up one directory from the current file's directory
        parent_dir = Path(__file__).parent.parent
        # Go into the /database directory and specify the database file
        db_path = parent_dir / dest_directory / db_filename
        # Use the 'sqlite:///' prefix and the absolute path to create the engine
        self.engine: Engine = create_engine(f'sqlite:///{db_path}', echo=True)
        Base.metadata.create_all(self.engine)
        self.Session: sessionmaker = sessionmaker(bind=self.engine)
        self.logger = logger

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

    # For creating or updating a project
    def save_project(self, project_data: Dict[str, Any]) -> List[Project]:
        with self.get_session() as session:
            try:
                project_id = project_data.get("id")
                if project_id:
                    project = session.query(Project).filter(
                        Project.id == project_id).first()
                    if project:
                        for key, value in project_data.items():
                            setattr(project, key, value)
                else:
                    project = Project(**project_data)
                    session.add(project)
                return [project]
            except SQLAlchemyError as e:
                self.logger.error(f"Error saving project: {e}")
                return []

    # For creating or updating a dataset
    def save_dataset(self, dataset_data: Dict[str, Any]) -> List[Dataset]:
        with self.get_session() as session:
            try:
                dataset_id = dataset_data.get("id")
                if dataset_id:
                    dataset = session.query(Dataset).filter(
                        Dataset.id == dataset_id).first()
                    if dataset:
                        for key, value in dataset_data.items():
                            setattr(dataset, key, value)
                else:
                    dataset = Dataset(**dataset_data)
                    session.add(dataset)
                return [dataset]
            except SQLAlchemyError as e:
                self.logger.error(f"Error saving dataset: {e}")
                return []

    # For creating or updating datapoints
    def save_datapoints(self, datapoints_data: List[Dict[str, Any]]) -> List[DataPoint]:
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
            except Exception as e:
                self.logger.error(f"Failed to save or update datapoints: {e}")
                return []

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
    #         except Exception as e:
    #             self.logger.error(f"Failed to add datapoints to dataset: {e}")
    #             return []

    # For adding multiple datasets to a project.
    def add_datasets_to_project(self, project_id: int, dataset_ids: List[int]) -> List[Project]:
        with self.get_session() as session:
            try:
                project = session.query(Project).filter(
                    Project.id == project_id).one()
                for dataset_id in dataset_ids:
                    dataset = session.query(Dataset).filter(
                        Dataset.id == dataset_id).one()
                    project.datasets.append(dataset)
                return [project]
            except Exception as e:
                self.logger.error(f"Failed to add datasets to project: {e}")
                return []

    # For creating or updating a model
    def save_model(self, model_data: Dict[str, Any]) -> List[Model]:
        with self.get_session() as session:
            try:
                model_id = model_data.get('id')
                if model_id:
                    model = session.query(Model).filter_by(id=model_id).first()
                    if model:
                        for key, value in model_data.items():
                            setattr(model, key, value)
                else:
                    model = Model(**model_data)
                    session.add(model)
                return [model]
            except Exception as e:
                self.logger.error(f"Failed to save or update model: {e}")
                return []

    # For creating or updating model evaluations
    def save_model_evaluations(self, evaluations_data: List[Dict[str, Any]]) -> List[ModelEvaluation]:
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
            except Exception as e:
                self.logger.error(
                    f"Failed to save or update model evaluations: {e}")
                return []

    # For creating or updating a training run
    def save_training_run(self, run_data: Dict[str, Any]) -> List[TrainingRun]:
        with self.get_session() as session:
            try:
                run_id = run_data.get('id')
                if run_id:
                    training_run = session.query(
                        TrainingRun).filter_by(id=run_id).first()
                    if training_run:
                        for key, value in run_data.items():
                            setattr(training_run, key, value)
                else:
                    training_run = TrainingRun(**run_data)
                    session.add(training_run)
                    return [training_run]
            except Exception as e:
                self.logger.error(
                    f"Failed to save or update training run: {e}")
                return []

    # For retrieveing all projects filterable by name and creation date
    def get_projects(self, project_name: str = None, creation_date: datetime.date = None) -> List[Project]:
        with self.get_session() as session:
            try:
                query = session.query(Project)
                if project_name:
                    query = query.filter(
                        Project.project_name.ilike(f"%{project_name}%"))
                if creation_date:
                    # Assuming creation_date is a datetime.date object and timestamp is a datetime column
                    query = query.filter(
                        func.date(Project.timestamp) == creation_date)
                projects = query.all()
                return projects
            except Exception as e:
                self.logger.error(f"Failed to retrieve projects: {e}")
                return []

    # For retrieving all models associated with a project filterable by name and version
    def get_models_by_project(self, project_id: int, name: str = None, version: int = None) -> List[Model]:
        with self.get_session() as session:
            try:
                query = session.query(Model).filter(
                    Model.project_id == project_id)
                if name:
                    query = query.filter(Model.model_name.ilike(f"%{name}%"))
                if version is not None:
                    query = query.filter(Model.version == version)
                models = query.all()
                return models
            except Exception as e:
                self.logger.error(f"""Failed to retrieve models for project {
                                  project_id}: {e}""")
                return []

    # Retrieve all datasets associated with a model filterable by dataset name, augmented and dataset category
    def get_datasets_by_model(self, model_id: int, timestamp: datetime.date = None, dataset_name: str = None, augmented: bool = None, category: DatasetCategory = None) -> List[Dataset]:
        with self.get_session() as session:
            try:
                model = session.query(Model).filter(
                    Model.id == model_id).one_or_none()
                if not model:
                    self.logger.error(f"Model with ID {model_id} not found.")
                    return []

                datasets = model.datasets
                if timestamp:
                    datasets = [
                        ds for ds in datasets if ds.timestamp.date() == timestamp]
                if dataset_name:
                    datasets = [
                        ds for ds in datasets if dataset_name.lower() in ds.dataset_name.lower()]
                if augmented is not None:
                    datasets = [
                        ds for ds in datasets if ds.augmented == augmented]
                if category:
                    datasets = [
                        ds for ds in datasets if ds.category == category]

                return datasets
            except Exception as e:
                self.logger.error(
                    f"Failed to retrieve datasets for model {model_id}: {e}")
                return []

    # Retrieve dataset specific datapoints filterable by coherence score, relevance score, semantic similarity score and augmentation type
    def get_datapoints_from_dataset(self, dataset_id: int, coherence_score: int = None, relevance_score: int = None,
                                    semantic_similarity: float = None, augmentation_type: AugmentationType = None) -> List[DataPoint]:
        with self.get_session() as session:
            try:
                # Retrieve the dataset by its ID
                dataset = session.query(Dataset).filter(
                    Dataset.id == dataset_id).one_or_none()
                if not dataset:
                    self.logger.error(f"""Dataset with ID {
                                      dataset_id} not found.""")
                    return []

                # Filter datapoints directly from the dataset's datapoints collection
                datapoints = dataset.datapoints
                if coherence_score is not None:
                    datapoints = [
                        dp for dp in datapoints if dp.coherence_score == coherence_score]
                if relevance_score is not None:
                    datapoints = [
                        dp for dp in datapoints if dp.relevance_score == relevance_score]
                if semantic_similarity is not None:
                    datapoints = [
                        dp for dp in datapoints if dp.semantic_similarity_score == semantic_similarity]
                if augmentation_type is not None:
                    datapoints = [
                        dp for dp in datapoints if dp.augmentation_type == augmentation_type]

                return datapoints
            except Exception as e:
                self.logger.error(f"""Failed to retrieve datapoints from dataset {
                                  dataset_id}: {e}""")
                return []

    # The function to retrieve all model evaluations remains as is, correctly fetching all evaluations for a given model
    def get_model_evaluations(self, model_id: int) -> List[ModelEvaluation]:
        with self.get_session() as session:
            try:
                model = session.query(Model).filter(
                    Model.id == model_id).one_or_none()
                if model:
                    return model.evaluations
                return []
            except Exception as e:
                self.logger.error(
                    f"Failed to retrieve evaluations for model {model_id}: {e}")
                return []

    # Retrieve the training run of a model
    def get_training_run(self, model_id: int) -> List[TrainingRun]:
        with self.get_session() as session:
            try:
                model = session.query(Model).filter(
                    Model.id == model_id).one_or_none()
                if model:
                    return model.training_run
                return []
            except Exception as e:
                self.logger.error(
                    f"Failed to retrieve training runs for model {model_id}: {e}")
                return []
