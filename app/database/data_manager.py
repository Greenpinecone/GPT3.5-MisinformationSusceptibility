from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from .schema import Base, Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun
from util.logger import Logger
from contextlib import contextmanager


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

    def get_session(self):
        return self.Session()

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
                Logger().error(f"Error saving project: {e}")
                return []

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
                Logger().error(f"Error saving dataset: {e}")
                return []

    def save_datapoint(self, datapoint_data: Dict[str, Any]) -> List[DataPoint]:
        with self.get_session() as session:
            try:
                datapoint = session.query(DataPoint).filter_by(
                    id=datapoint_data.get('id')).first()
                if datapoint:
                    for key, value in datapoint_data.items():
                        setattr(datapoint, key, value)
                else:
                    datapoint = DataPoint(**datapoint_data)
                    session.add(datapoint)
                return [datapoint]
            except Exception as e:
                self.logger.error(f"Failed to save or update datapoint: {e}")
                return []

    def add_datapoints_to_dataset(self, dataset_id: int, datapoints_data: List[Dict[str, Any]]) -> List[DataPoint]:
        with self.get_session() as session:
            try:
                added_datapoints = []
                for dp_data in datapoints_data:
                    dp_data['dataset_id'] = dataset_id
                    datapoint = DataPoint(**dp_data)
                    session.add(datapoint)
                    added_datapoints.append(datapoint)
                return added_datapoints
            except Exception as e:
                self.logger.error(f"Failed to add datapoints to dataset: {e}")
                return []

    @contextmanager
    def add_datasets_to_project(self, project_id: int, datasets_data: List[Dict[str, Any]]) -> List[Dataset]:
        with self.get_session() as session:
            try:
                added_datasets = []
                for ds_data in datasets_data:
                    ds_data['project_id'] = project_id
                    dataset = Dataset(**ds_data)
                    session.add(dataset)
                    added_datasets.append(dataset)
                return added_datasets
            except Exception as e:
                self.logger.error(f"Failed to add datasets to project: {e}")
                return []
