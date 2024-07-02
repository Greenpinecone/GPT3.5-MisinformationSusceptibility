from contextlib import contextmanager
from sqlalchemy import Engine, and_, create_engine, func, or_, event, text
from sqlalchemy.orm import sessionmaker, Session, scoped_session, joinedload, aliased
from sqlalchemy.orm.query import Query
from pathlib import Path
from typing import Generator
from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound, NoResultFound
from app.backend.database.schema import CurrentProjectData, DataPointEvaluation, Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun, project_model_link, project_dataset_link, Base
from ...util.logger import Logger
from ..interfaces.i_data_manager import IDataManager
from datetime import datetime
from app.backend.dtos.create_request import *
from app.backend.dtos.get_request import *
from app.backend.dtos.update_request import SENTINEL, UpdateCurrentProjectDataDTO, UpdateDataPointDTO, UpdateDataPointEvaluationDTO, UpdateDatasetDTO, UpdateModelDTO, UpdateModelEvaluationDTO, UpdateProjectDTO, UpdateTrainingRunDTO
from app.backend.dtos.response import *
from app.backend.database.version_manager import VersionManager


# Instantiates a new database or loads the currently
# Define the logger as a class attribute
logger = Logger(__name__)


class DataManager(IDataManager):

    def __init__(self, dest_directory: str = 'database', db_filename: str = 'streamlit_app.db'):
       # Move up one directory from the current file's directory
        parent_dir: Path = Path(__file__).parent.parent.parent
        # Go into the /database directory and specify the database file
        db_path: Path = parent_dir / dest_directory / db_filename
        # Use the 'sqlite:///' prefix and the absolute path to create the engine
        self.engine: Engine = create_engine(f'sqlite:///{db_path}', echo=True)

        # Ensure PRAGMA foreign_keys is ON for the SQLite engine
        # self.set_sqlite_pragma()

        event.listen(self.engine, 'connect', lambda c,
                     _: c.execute('pragma foreign_keys=on'))

        Base.metadata.create_all(self.engine)
        # Use scoped_session for thread-local sessions
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

        if not self.check_foreign_keys_enabled():
            raise Exception("Foreign key support is not enabled!")

        # Check SQLite version
        self.check_sqlite_version()

    # def set_sqlite_pragma(self):
    #     @event.listens_for(self.engine, "connect")
    #     def enable_foreign_keys(dbapi_connection, connection_record):
    #         cursor = dbapi_connection.cursor()
    #         cursor.execute("PRAGMA foreign_keys=ON")
    #         cursor.close()

    def check_sqlite_version(self):
        with self.engine.connect() as connection:
            result = connection.execute(
                text("SELECT sqlite_version();")).fetchone()
            print(f"SQLite version: {result[0]}")

    def check_foreign_keys_enabled(self):
        with self.engine.connect() as connection:
            result = connection.execute(text("PRAGMA foreign_keys")).fetchone()
            return result[0] == 1

    @contextmanager
    def get_session(self, session: Session = None) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        if session:
            yield session
        else:
            session: Session = self.Session()
            try:
                yield session
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Session rollback due to exception: {e}")
                raise
            finally:
                self.Session.remove()  # Remove the session to ensure it is properly closed

    def get_or_create_current_project_data(self, session: Session) -> list[CurrentProjectData]:
        try:
            current_project_data = session.query(
                CurrentProjectData).one_or_none()

            if current_project_data is None:
                current_project_data_singelton = CurrentProjectData()
                session.add(current_project_data_singelton)
                session.flush()
                return [current_project_data_singelton]
            else:
                return [current_project_data]

        except MultipleResultsFound as e:
            logger.exception(
                f"More than one current project data entry found. There should be only one. {e}")
            raise Exception(
                "More than one current project data entry found. There should be only one.") from e

        except SQLAlchemyError as e:
            logger.exception(
                f"Failed to create or get current project data due to error: {e}")
            raise Exception(
                "Failed to create or get current project data due to error.") from e

    def update_current_project_data(self, session: Session, current_project_data: UpdateCurrentProjectDataDTO) -> list[CurrentProjectData]:
        saved_data: list[CurrentProjectData] = []
        try:
            data = None
            if getattr(current_project_data, 'id', None):
                data: CurrentProjectData = session.get(
                    CurrentProjectData, current_project_data.id)
                if not data:
                    raise ValueError(f"""Current project data with ID {
                                     current_project_data.id} not found.""")

            if not data:
                raise ValueError("No valid data found to update.")

            # Define a dictionary for attribute mappings
            attribute_mapping = {
                'fine_tuning_step_counter': current_project_data.fine_tuning_step_counter,
                'unfinished_progress': current_project_data.unfinished_progress,
                'current_page': current_project_data.current_page,
                'save_checkpoint_models': current_project_data.save_checkpoint_models,
                'semantic_similarity_model': current_project_data.semantic_similarity_model,
                'current_augmentation_configurations': current_project_data.current_augmentation_configurations,
            }

            # Update attributes if not SENTINEL
            for attribute, value in attribute_mapping.items():
                if value is not SENTINEL:
                    setattr(data, attribute, value)

            # Update complex relationships
            if current_project_data.current_project_id is not SENTINEL:
                if not current_project_data.current_project_id:
                    data.current_project = current_project_data.current_project_id
                else:
                    data.current_project = self.get_project_by_id(
                        session, current_project_data.current_project_id)[0]

            if current_project_data.current_fine_tuning_model_id is not SENTINEL:
                if not current_project_data.current_fine_tuning_model_id:
                    data.current_fine_tuning_model = current_project_data.current_fine_tuning_model_id
                else:
                    data.current_fine_tuning_model = self.get_model_by_id(
                        session, current_project_data.current_fine_tuning_model_id)[0]

            if current_project_data.selected_model_for_fine_tuning_id is not SENTINEL:
                if not current_project_data.selected_model_for_fine_tuning_id:
                    data.selected_model_for_fine_tuning = current_project_data.selected_model_for_fine_tuning_id
                else:
                    data.selected_model_for_fine_tuning = self.get_model_by_id(
                        session, current_project_data.selected_model_for_fine_tuning_id)[0]

            if current_project_data.currently_modified_dataset_id is not SENTINEL:
                if not current_project_data.currently_modified_dataset_id:
                    data.currently_modified_dataset = current_project_data.currently_modified_dataset_id
                else:
                    data.currently_modified_dataset = self.get_dataset_by_id(
                        session, current_project_data.currently_modified_dataset_id)[0]

            if current_project_data.current_augmented_datapoint_evaluation_ids is not SENTINEL:
                # Fetch DataPointEvaluation entries by their IDs
                evaluations = session.query(DataPointEvaluation).filter(
                    DataPointEvaluation.id.in_(
                        current_project_data.current_augmented_datapoint_evaluation_ids)
                ).all()

                # Set them to the current_augmented_datapoint_evaluations relationship
                data.current_augmented_datapoint_evaluations = evaluations

            saved_data.append(data)

            # Must be flushed to create primary key / datetime etc.
            session.flush()
            return saved_data
        except SQLAlchemyError as e:
            logger.exception(
                f"Failed to save or update project data due to error: {e}")
            raise Exception(
                "Failed to save or update project data due to error.") from e

    def _get_unoriginal_project_models(self, session: Session, project_id: int) -> list[Model]:
        # INFO: # This is necessary to fetch only all models that are not associated to the project currently updated, since it should only be possible to add or remove "global" models from other projects. Therefore we have to filter the associations table by creation data to fetch only those models, that where not originally (earliest creation date in the association table) associated with this project (do not belong to it)
        # Create the subquery to find the earliest project associated with each model
        subquery = (
            session.query(
                project_model_link.c.model_id,
                project_model_link.c.project_id,
                func.row_number().over(
                    partition_by=project_model_link.c.model_id,
                    order_by=project_model_link.c.created_at  # Order by creation time
                ).label('row_num')
            ).subquery()
        )

        # Alias the subquery to use it in the join
        subquery_alias = aliased(subquery)

        # Main query to fetch models that need to be updated
        query = (
            session.query(Model)
            .join(subquery_alias, Model.id == subquery_alias.c.model_id)
            # Ensure it's the first project
            .filter(subquery_alias.c.row_num == 1)
            # Exclude models originally added to the current project
            .filter(subquery_alias.c.project_id != project_id)
            # Include models currently associated with the current project
            .filter(Model.projects.any(Project.id == project_id))
        )

        # Execute the query and fetch results
        return query.all()

    def _update_project_model_associations(self, session: Session, project: Project, project_dto: ProjectDTO):
        if project_dto.model_ids is not None:
            # Step 1: Retrieve current model IDs associated with the project
            current_model_ids = self._get_unoriginal_project_models(
                session, project.id)
            # Flatten the list of tuples
            current_model_ids = [model.id for model in current_model_ids]

            # Step 2: Compare with new model IDs
            new_model_ids = set(project_dto.model_ids)
            current_model_ids_set = set(current_model_ids)

            # Models to delete (present in current but not in new)
            models_to_delete = current_model_ids_set - new_model_ids

            # Models to add (present in new but not in current)
            models_to_add = new_model_ids - current_model_ids_set

            # Step 3: Delete associations not in new model IDs
            if models_to_delete:
                session.execute(
                    project_model_link.delete().where(
                        and_(
                            project_model_link.c.project_id == project.id,
                            project_model_link.c.model_id.in_(models_to_delete)
                        )
                    )
                )

            # Step 4: Add new associations
            if models_to_add:
                models_to_add_objects = session.query(Model).filter(
                    Model.id.in_(models_to_add)
                ).all()
                for model in models_to_add_objects:
                    project_model_association = {
                        'model_id': model.id,
                        'project_id': project.id,
                        'model_name': model.model_name,
                        'version': model.version,
                    }
                    session.execute(project_model_link.insert().values(
                        project_model_association))

    def _update_project_datasets(self, session: Session, project_dto: ProjectDTO):
        # INFO: This is necessary to fetch only all datasets that are not associated to the project currently updated, since it should only be possible to add or remove "global" datasest from other projects. Therefore we have to filter the associations table by creation data to fetch only those datasets, that where not originally (earliest creation date in the association table) associated with this project (do not belong to it)
        # Step 2: Get all "unoriginal" datasets
        subquery = (
            session.query(
                project_dataset_link.c.dataset_id,
                project_dataset_link.c.project_id,
                func.row_number().over(
                    partition_by=project_dataset_link.c.dataset_id,
                    order_by=project_dataset_link.c.created_at
                ).label('row_num')
            )
            .subquery()
        )

        subquery_alias = aliased(subquery)

        unoriginal_datasets = session.query(Dataset).join(
            project_dataset_link,
            project_dataset_link.c.dataset_id == Dataset.id
        ).join(
            subquery_alias,
            and_(
                project_dataset_link.c.dataset_id == subquery_alias.c.dataset_id,
                project_dataset_link.c.project_id == subquery_alias.c.project_id,
                subquery_alias.c.row_num != 1  # Exclude the first association
            )
        ).filter(
            project_dataset_link.c.project_id == project_dto.id
        ).all()

        unoriginal_dataset_ids = [
            dataset.id for dataset in unoriginal_datasets]

        # Step 3: Compare and update associations
        new_dataset_ids = set(project_dto.dataset_ids)
        current_dataset_ids_set = set(unoriginal_dataset_ids)

        datasets_to_add = new_dataset_ids - current_dataset_ids_set
        datasets_to_remove = current_dataset_ids_set - new_dataset_ids

        # Remove datasets
        for dataset_id in datasets_to_remove:
            session.execute(
                project_dataset_link.delete().where(
                    and_(
                        project_dataset_link.c.project_id == project_dto.id,
                        project_dataset_link.c.dataset_id == dataset_id
                    )
                )
            )

        # Add new datasets
        for dataset_id in datasets_to_add:
            if dataset_id not in unoriginal_dataset_ids:
                session.execute(
                    project_dataset_link.insert().values(
                        project_id=project_dto.id,
                        dataset_id=dataset_id
                    )
                )

    # CREATE / UPDATE´

    def update_projects(self, session: Session, projects_data: list[UpdateProjectDTO]) -> list[Project]:
        saved_projects: list[Project] = []
        try:
            for project_dto in projects_data:
                project = None
                if getattr(project_dto, 'id', None):
                    project = session.get(Project, project_dto.id)
                    if not project:
                        raise ValueError(f"""Project with ID {
                            project_dto.id} not found.""")

                if project_dto.project_name:
                    project.project_name = project_dto.project_name

                if project_dto.description:
                    project.description = project_dto.description

                if project_dto.model_ids is not None:
                    self._update_project_model_associations(
                        session, project, project_dto)

                if project_dto.dataset_ids is not None:
                    self._update_project_datasets(
                        session, project_dto)

                saved_projects.append(project)

            # Must be flushed to create primary key / datetime etc.
            session.flush()
            return saved_projects
        except Exception as e:
            logger.exception(
                f"Failed to save or update projects due to error: {e}")
            # Re-raise the exception to notify the caller of the failure
            raise Exception(
                "Failed to save or update projects due to error.") from e

    # For creating a project
    def create_projects(self, session: Session, projects_data: list[CreateProjectDTO]) -> list[Project]:
        saved_projects: list[Project] = []
        try:
            for project_dto in projects_data:
                project = Project()
                # Add and add required values immediately after retrieving or creating to avoid auto flush inconsistencies on queries
                session.add(project)

                project.project_name = project_dto.project_name
                project.description = project_dto.description

                session.flush()

                if project_dto.model_ids:
                    models = session.query(Model).filter(
                        Model.id.in_(project_dto.model_ids)).all()
                    for model in models:
                        project_model_association = {
                            'model_id': model.id,
                            'project_id': project.id,
                            'model_name': model.model_name,
                            'version': model.version,
                        }
                        session.execute(project_model_link.insert().values(
                            project_model_association))

                if project_dto.dataset_ids:
                    datasets = session.query(Dataset).filter(
                        Dataset.id.in_(project_dto.dataset_ids)).all()
                    project.datasets = datasets

                saved_projects.append(project)

            # Must be flushed to create primary key / datetime etc.
            session.flush()
            return saved_projects
        except Exception as e:
            logger.exception(
                f"Failed to save or update projects due to error: {e}")
            # Re-raise the exception to notify the caller of the failure
            raise Exception(
                "Failed to save or update projects due to error.") from e

    def update_datasets(self, session: Session, datasets_data: list[UpdateDatasetDTO]) -> list[Dataset]:
        saved_datasets: list[Dataset] = []
        try:
            for dataset_dto in datasets_data:
                dataset = session.get(Dataset, dataset_dto.id)
                if not dataset:
                    raise ValueError(f"""Dataset with ID {
                        dataset_dto.id} not found.""")

                if dataset_dto.dataset_name:
                    dataset.dataset_name = dataset_dto.dataset_name

                if dataset_dto.is_global is not None:
                    dataset.is_global = dataset_dto.is_global

                # Handling project relationships
                if dataset_dto.project_ids is not None:
                    projects = session.query(Project).filter(
                        Project.id.in_(dataset_dto.project_ids)).all()
                    dataset.projects = projects

                saved_datasets.append(dataset)

            # Must be flushed to create primary key / datetime etc.
            session.flush()
            return saved_datasets
        except Exception as e:
            logger.error(
                f"Failed to save or update datasets due to error: {e}")
            # Re-raise the exception to notify the caller of the failure
            raise Exception(
                "Failed to save or update datasets due to error.") from e

    def _update_training_datasets(self, session: Session, dataset_dto: CreateDatasetDTO, dataset: Dataset):
        # Handling initial dataset relationships
        if dataset_dto.initial_dataset_ids:
            for initial_dataset_id in dataset_dto.initial_dataset_ids:
                initial_dataset = session.get(Dataset, initial_dataset_id)
                if initial_dataset:
                    dataset.initial_datasets.append(initial_dataset)

    # For creating or updating a dataset
    def create_datasets(self, session: Session, datasets_data: list[CreateDatasetDTO]) -> list[Dataset]:
        saved_datasets: list[Dataset] = []
        try:
            for dataset_dto in datasets_data:
                dataset = Dataset()
                # Add and add required values immediately after retrieving or creating to avoid auto flush inconsistencies on queries
                session.add(dataset)

                dataset.dataset_name = dataset_dto.dataset_name
                dataset.augmented = dataset_dto.augmented
                dataset.category = dataset_dto.category
                dataset.is_global = dataset_dto.is_global
                dataset.fine_tuning_company = dataset_dto.fine_tuning_company
                dataset.fine_tuning_formatting = dataset_dto.fine_tuning_formatting
                dataset.fine_tuning_model = dataset_dto.fine_tuning_model

                # flush session to generate dataset id
                session.flush()

                # Handling initial and test dataset relationships
                self._update_training_datasets(session, dataset_dto, dataset)

                if dataset_dto.test_dataset_id:
                    test_dataset = session.get(
                        Dataset, dataset_dto.test_dataset_id)
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
            return saved_datasets

        except Exception as e:
            logger.error(
                f"Failed to save or update datasets due to error: {e}")
            # Re-raise the exception to notify the caller of the failure
            raise Exception(
                "Failed to save or update datasets due to error.") from e

    def update_datapoints(self, session: Session, datapoints_data: list[UpdateDataPointDTO]) -> list[DataPointDTO]:
        updated_datapoints: list[DataPoint] = []
        try:
            for update_dto in datapoints_data:
                datapoint: DataPoint = session.get(
                    DataPoint, update_dto.id)
                if not datapoint:
                    raise ValueError(f"""Datapoint with ID {
                        update_dto.id} not found.""")

                # Update attributes
                if update_dto.related_datapoint_ids:
                    datapoints = session.query(DataPoint).filter(
                        DataPoint.id.in_(update_dto.related_datapoint_ids)).all()
                    datapoint.related_datapoints = datapoints

                updated_datapoints.append(datapoint)

            # Must be flushed to create primary key / datetime etc.
            session.flush()
            return updated_datapoints
        except Exception as e:
            logger.exception("Failed to update datapoints.")
            raise SQLAlchemyError("Failed to update datapoints.") from e

    # For creating datapoints
    def create_datapoints(self, session: Session, datapoints_data: list[CreateDataPointDTO]) -> list[DataPoint]:
        """Creates a new datapoint with all its dataset relations and datapoint dataset specific relations."""
        saved_datapoints: list[DataPoint] = []
        try:
            for datapoint_dto in datapoints_data:
                datapoint = DataPoint()
                session.add(datapoint)

                # Assign attributes from DTO
                datapoint.messages = datapoint_dto.messages
                datapoint.augmentation_type = datapoint_dto.augmentation_type
                datapoint.dataset_id = datapoint_dto.dataset_id

                # Handle the initial datapoint relationship
                if datapoint_dto.initial_datapoint_id:
                    initial_datapoint = session.get(
                        DataPoint, datapoint_dto.initial_datapoint_id)
                    datapoint.initial_datapoint = initial_datapoint

                if datapoint_dto.related_datapoint_ids:
                    datapoints = session.query(DataPoint).filter(
                        DataPoint.id.in_(datapoint_dto.related_datapoint_ids)).all()
                    datapoint.related_datapoints = datapoints

                saved_datapoints.append(datapoint)
            # Must be flushed to create primary key / datetime etc.
            session.flush()
            return saved_datapoints
        except Exception as e:
            logger.exception("Failed to create datapoints.")
            raise SQLAlchemyError("Failed to create datapoints.") from e

    # For creating a model
    def create_models(self, session: Session, models_data: list[CreateModelDTO]) -> list[Model]:
        saved_models: list[Model] = []
        try:
            for model_dto in models_data:
                model = Model()
                session.add(model)

                model.model_name = model_dto.model_name
                model.is_global = model_dto.is_global

                if model_dto.augmentation_configurations:
                    model.augmentation_configurations = model_dto.augmentation_configurations

                if model_dto.semantic_similarity_model:
                    model.semantic_similarity_model = model_dto.semantic_similarity_model

                if model_dto.fine_tuning_checkpoint_job_id:
                    model.fine_tuning_checkpoint_job_id = model_dto.fine_tuning_checkpoint_job_id

                if model_dto.fine_tuned_model_id:
                    model.fine_tuned_model_id = model_dto.fine_tuned_model_id

                training_datasets = session.query(Dataset).filter(
                    Dataset.id.in_(model_dto.training_dataset_ids)).all()
                model.training_datasets = training_datasets

                if model_dto.fine_tuning_job_id:
                    model.fine_tuning_job_id = model_dto.fine_tuning_job_id

                if model_dto.is_checkpoint_model is not None:
                    model.is_checkpoint_model = model_dto.is_checkpoint_model

                if model_dto.checkpoint_step:
                    model.checkpoint_step = model_dto.checkpoint_step

                parent_model = None
                if model_dto.parent_model_id:
                    parent_model = session.get(
                        Model, model_dto.parent_model_id)
                    model.parent_model = parent_model

                    model.version = VersionManager.get_next_version(
                        session, model_dto, parent_model)
                else:
                    model.version = "0"

                if model_dto.training_run_id:
                    training_run = session.get(
                        TrainingRun, model_dto.training_run_id)
                    model.training_run = training_run

                for project_id in model_dto.project_ids:
                    project_model_association = {
                        'model_id': model.id,
                        'project_id': project_id,
                        'model_name': model.model_name,
                        'version': model.version,
                    }
                    session.execute(project_model_link.insert().values(
                        project_model_association))

                saved_models.append(model)

            session.flush()
            return saved_models
        except Exception as e:
            logger.exception(
                f"Failed to save or update models due to error: {e}")
            raise Exception(
                "Failed to save or update models due to error.") from e

    def delete_models(self, session: Session, model_ids: list[int]) -> list[Model]:
        # TODO: it might be possible to configure the database ORM relations directly to correctly de-associate but this is simple and effective
        try:
            for model_id in model_ids:
                model: Model = session.get(Model, model_id)
                if model:
                    # # Remove the model from related projects
                    # for project in model.projects:
                    #     project.models.remove(model)

                    # # Remove the model from related datasets
                    # for dataset in model.training_datasets:
                    #     dataset.models.remove(model)

                    # # Remove the model from parent model's child models if any
                    # if model.parent_model:
                    #     model.parent_model.child_models.remove(model)

                    # Remove the model's training run without deleting related objects
                    if model.training_run:
                        session.delete(model.training_run)

                    # Manually remove entries from the project_model_link association table
                    session.execute(
                        project_model_link.delete().where(project_model_link.c.model_id == model.id)
                    )

                    # Finally, delete the model itself
                    session.delete(model)

            return
        except Exception as e:
            logger.exception(f"Failed to delete models due to error: {e}")
            raise Exception("Failed to delete models due to error.") from e

    def delete_only_datasets(self, session: Session, dataset_ids: list[int]) -> None:
        """Careful with using this function, since it only deletes a dataset. its datapoints and their datapoint evaluations as configured in the SQLA Tables in the database schema. This is because sometimes only a newly augmented dataset should be deleted without removing its models.
        Args:
            session (Session): _description_
            dataset_ids (list[int]): _description_

        Raises:
            Exception: _description_
        """
        try:
            for dataset_id in dataset_ids:
                dataset: Dataset = session.get(Dataset, dataset_id)
                if dataset:
                    session.delete(dataset)
        except Exception as e:
            logger.exception(f"Failed to delete datasets due to error: {e}")
            raise Exception("Failed to delete datasets due to error.") from e

    def _get_current_project_ids(self, session, model_id):
        current_projects = session.query(Project).join(project_model_link).filter(
            project_model_link.c.model_id == model_id).all()
        current_project_ids = {project.id for project in current_projects}
        return current_project_ids

    def _determine_project_changes(self, current_project_ids, new_project_ids):
        new_project_ids_set = set(new_project_ids)

        projects_to_add = new_project_ids_set - current_project_ids
        projects_to_remove = current_project_ids - new_project_ids_set

        return projects_to_add, projects_to_remove

    def _update_project_associations(self, session, model_id, new_project_ids):
        current_project_ids = self._get_current_project_ids(session, model_id)
        projects_to_add, projects_to_remove = self._determine_project_changes(
            current_project_ids, new_project_ids)

        # Remove old associations
        if projects_to_remove:
            session.execute(
                project_model_link.delete().where(
                    project_model_link.c.model_id == model_id,
                    project_model_link.c.project_id.in_(projects_to_remove)
                )
            )

        # Add new associations
        for project_id in projects_to_add:
            project_model_association = {
                'model_id': model_id,
                'project_id': project_id,
                'model_name': session.query(Model.model_name).filter(Model.id == model_id).scalar(),
                'version': session.query(Model.version).filter(Model.id == model_id).scalar()
            }
            session.execute(project_model_link.insert().values(
                project_model_association))

    # For updating a model

    def update_models(self, session: Session, models_data: list[UpdateModelDTO]) -> list[Model]:
        saved_models: list[Model] = []
        try:
            for model_dto in models_data:
                model = session.get(Model, model_dto.id)
                if not model:
                    raise ValueError(f"""Model with ID {
                        model_dto.id} not found.""")

                if model_dto.augmentation_configurations:
                    model.augmentation_configurations = model_dto.augmentation_configurations
                if model_dto.augmentation_configurations == []:
                    model.augmentation_configurations = []

                if model_dto.semantic_similarity_model:
                    model.semantic_similarity_model = model_dto.semantic_similarity_model
                if model_dto.semantic_similarity_model == "":
                    model.semantic_similarity_model = None

                if model_dto.model_name:
                    model.model_name = model_dto.model_name

                if model_dto.fine_tuning_checkpoint_job_id:
                    model.fine_tuning_checkpoint_job_id = model_dto.fine_tuning_checkpoint_job_id

                if model_dto.fine_tuned_model_id:
                    model.fine_tuned_model_id = model_dto.fine_tuned_model_id

                # A model can only belong to multiple projects if it is a global model
                if model_dto.project_ids is not None:
                    self._update_project_associations(
                        session, model_dto.id, model_dto.project_ids)

                # Update the corresponding training datasets
                if model_dto.training_dataset_ids is not None:
                    training_datasets = session.query(Dataset).filter(
                        Dataset.id.in_(model_dto.training_dataset_ids)).all()
                    model.training_datasets = training_datasets

                if model_dto.is_global is not None:
                    model.is_global = model_dto.is_global

                if model_dto.fine_tuning_job_id:
                    model.fine_tuning_job_id = model_dto.fine_tuning_job_id
                if model_dto.fine_tuning_job_id == "":
                    model.fine_tuning_job_id = None

                saved_models.append(model)

            # Must be flushed to create primary key / datetime etc.
            session.flush()
            return saved_models

        except Exception as e:
            logger.exception(
                f"Failed to save or update models due to error: {e}")
            raise Exception(
                "Failed to save or update models due to error.") from e

    # For creating model evaluations
    def create_model_evaluations(self, session: Session, evaluations_data: list[CreateModelEvaluationDTO]) -> list[ModelEvaluation]:
        saved_evaluations: list[ModelEvaluation] = []
        try:
            for eval_dto in evaluations_data:
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
            return saved_evaluations

        except Exception as e:
            logger.error(
                f"Failed to save or update model evaluations due to error: {e}")
            raise Exception(
                "Failed to save or update model evaluations due to error.") from e

     # For updating model evaluations
    def update_model_evaluations(self, session: Session, evaluations_data: list[UpdateModelEvaluationDTO]) -> list[ModelEvaluation]:
        saved_evaluations: list[ModelEvaluation] = []
        try:
            for eval_dto in evaluations_data:
                evaluation = session.get(
                    ModelEvaluation, eval_dto.id)
                if not evaluation:
                    raise ValueError(f"""Model Evaluation with ID {
                        eval_dto.id} not found.""")

                if eval_dto.evaluation_type:
                    evaluation.evaluation_type = eval_dto.evaluation_type
                if eval_dto.helpful_score:
                    evaluation.helpful_score = eval_dto.helpful_score
                if eval_dto.honest_score:
                    evaluation.honest_score = eval_dto.honest_score
                if eval_dto.harmless_score:
                    evaluation.harmless_score = eval_dto.harmless_score

                saved_evaluations.append(evaluation)

            # Must be flushed to create primary key / datetime etc.
            session.flush()
            return saved_evaluations

        except Exception as e:
            logger.error(
                f"Failed to save or update model evaluations due to error: {e}")
            raise Exception(
                "Failed to save or update model evaluations due to error.") from e

    # For creating a training run
    def create_training_runs(self, session: Session, runs_data: list[CreateTrainingRunDTO]) -> list[TrainingRun]:
        saved_runs: list[TrainingRun] = []
        try:
            for run_dto in runs_data:
                training_run = TrainingRun()
                # Add and add required values immediately after retrieving or creating to avoid auto flush inconsistencies on queries
                session.add(training_run)

                training_run.model_id = run_dto.model_id
                training_run.epochs = run_dto.epochs
                training_run.learning_rate_multiplier = run_dto.learning_rate_multiplier
                training_run.batch_size = run_dto.batch_size
                training_run.seed = run_dto.seed
                training_run.fine_tuning_model = run_dto.fine_tuning_model

                # Fetch the Model object using the model_id from DTO
                model = session.get(Model, run_dto.model_id)

                # Set fetched Model object to the training_run
                training_run.model = model

                saved_runs.append(training_run)

            # Must be flushed to create primary key / datetime etc.
            session.flush()
            return saved_runs
        except Exception as e:
            logger.error("Failed to save or update training runs.")
            raise Exception(
                "Failed to save or update training runs.") from e

    # GET
    # For retrieveing all projects filterable by name and creation date
    def get_all_projects(self, session: Session, project_data: GetProjectsDTO) -> list[Project]:
        logger.debug(f"Project data: {project_data}")
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
                    Project.created_at >= created_at)

            projects: list[Project] = query.all()
            return projects
        except SQLAlchemyError as e:
            logger.exception("Failed to retrieve projects")
            raise SQLAlchemyError("Failed to retrieve projects") from e

    def get_all_models(self, session: Session, model_data: GetModelsDTO) -> list[Model]:
        logger.debug(f"Model data: {model_data}")
        try:
            query = session.query(Model)
            model_name: str = model_data.model_name
            created_at: datetime = model_data.created_at
            version: str = model_data.version
            project_id: int = model_data.project_id
            is_global: bool = model_data.is_global
            excluded_project_id: int = model_data.exlude_project_id
            is_checkpoint_model: bool = model_data.is_checkpoint_model

            if model_name:
                query = query.filter(
                    Model.model_name.ilike(f"%{model_name}%"))
            if created_at:
                # Assuming created_at is correctly formatted for comparison
                query = query.filter(
                    Model.created_at >= created_at)
            if version:
                query = query.filter(Model.version == version)
            if is_checkpoint_model is not None:
                query = query.filter(
                    Model.is_checkpoint_model == is_checkpoint_model)
            if project_id:
                # Create the subquery to find all models associated with the given project_id
                subquery = (
                    session.query(
                        project_model_link.c.model_id
                    )
                    .filter(project_model_link.c.project_id == project_id)
                    .subquery()
                )

                # Alias the subquery to use it in the join
                subquery_alias = aliased(subquery)

                query = query.join(subquery_alias, Model.id ==
                                   subquery_alias.c.model_id)

                # Fetch all original models of a project (earliest entry in the model assocaition table with a project)
                """
                # Step 1: Create a Subquery to Identify the First Project for Each Model Based on created_at
                subquery = (
                    session.query(
                        project_model_link.c.model_id,
                        project_model_link.c.project_id,
                        func.row_number().over(
                            partition_by=project_model_link.c.model_id,
                            order_by=project_model_link.c.created_at  # Order by creation time
                        ).label('row_num')
                    ).subquery()
                )

                # Alias the subquery to use it in the join
                subquery_alias = aliased(subquery)

                # Step 2: Join the Subquery with the Main Query
                query = (
                    session.query(Model)
                    .join(subquery_alias, and_(
                        Model.id == subquery_alias.c.model_id,
                        subquery_alias.c.row_num == 1  # Ensure it's the first project
                    ))
                    # Step 3: Apply the Filter to Match the Specific project_id
                    .filter(subquery_alias.c.project_id == project_id)
                )
                """

            if is_global is not None:
                query = query.filter(
                    Model.is_global == is_global)

            # Apply additional filtering based on excluded_project_id
            # Only returns models that do not directly belong to the excluded project id (meaning, the first project in their projects list (the one added when they were created) is not equal to the excluded project)
            if excluded_project_id is not None:
                # Create a subquery to find all models where the first project association is not the excluded_project_id (by date)
                exclusion_subquery = (
                    session.query(
                        project_model_link.c.model_id,
                        func.row_number().over(
                            partition_by=project_model_link.c.model_id,
                            order_by=project_model_link.c.created_at
                        ).label('row_num'),
                        project_model_link.c.project_id
                    )
                    .subquery()
                )

                exclusion_subquery_alias = aliased(exclusion_subquery)

                # Filter out models whose first project association is the excluded_project_id
                query = query.join(
                    exclusion_subquery_alias,
                    and_(
                        Model.id == exclusion_subquery_alias.c.model_id,
                        exclusion_subquery_alias.c.row_num == 1,
                        exclusion_subquery_alias.c.project_id != excluded_project_id
                    )
                )

            models: list[Model] = query.all()

            return models
        except SQLAlchemyError as e:
            logger.exception("Failed to retrieve models")
            raise SQLAlchemyError("Failed to retrieve models") from e

    def create_datapoint_evaluations(self, session: Session, evaluations_data: list[CreateDataPointEvaluationDTO]) -> list[DataPointEvaluation]:
        saved_evaluations: list[DataPointEvaluation] = []
        try:
            for evaluation_dto in evaluations_data:
                evaluation = DataPointEvaluation(
                    datapoint_id=evaluation_dto.datapoint_id,
                    model_id=evaluation_dto.model_id,
                    coherence_score=evaluation_dto.coherence_score,
                    relevance_score=evaluation_dto.relevance_score,
                    semantic_similarity_score=evaluation_dto.semantic_similarity_score
                )
                session.add(evaluation)
                saved_evaluations.append(evaluation)

            session.flush()  # Ensure IDs are generated
            return saved_evaluations
        except SQLAlchemyError as e:
            logger.exception("Failed to create datapoint evaluations")
            raise SQLAlchemyError(
                "Failed to create datapoint evaluations") from e

    def update_datapoint_evaluations(self, session: Session, evaluations_data: list[UpdateDataPointEvaluationDTO]) -> list[DataPointEvaluation]:
        updated_evaluations: list[DataPointEvaluation] = []
        try:
            for evaluation_dto in evaluations_data:
                evaluation = session.get(
                    DataPointEvaluation, evaluation_dto.id)

                if evaluation_dto.coherence_score is not None:
                    evaluation.coherence_score = evaluation_dto.coherence_score
                if evaluation_dto.relevance_score is not None:
                    evaluation.relevance_score = evaluation_dto.relevance_score
                if evaluation_dto.semantic_similarity_score is not None:
                    evaluation.semantic_similarity_score = evaluation_dto.semantic_similarity_score

                updated_evaluations.append(evaluation)

            session.flush()  # Commit the changes
            return updated_evaluations
        except SQLAlchemyError as e:
            logger.exception("Failed to update datapoint evaluations")
            raise SQLAlchemyError(
                "Failed to update datapoint evaluations") from e

    def get_all_datapoint_evaluations(self, session: Session, filter_data: GetDataPointEvaluationsDTO) -> list[DataPointEvaluation]:
        try:
            # Start with the base query
            query = session.query(DataPointEvaluation).filter(
                DataPointEvaluation.model_id == filter_data.model_id
            )

            # Add optional filters
            if filter_data.datapoint_id is not None:
                query = query.filter(
                    DataPointEvaluation.datapoint_id >= filter_data.datapoint_id
                )
            if filter_data.coherence_score is not None:
                query = query.filter(
                    DataPointEvaluation.coherence_score >= filter_data.coherence_score
                )
            if filter_data.relevance_score is not None:
                query = query.filter(
                    DataPointEvaluation.relevance_score >= filter_data.relevance_score
                )
            if filter_data.semantic_similarity_score is not None:
                query = query.filter(
                    DataPointEvaluation.semantic_similarity_score >= filter_data.semantic_similarity_score
                )

            # Execute the query and return the results
            evaluations: list[DataPointEvaluation] = query.all()
            return evaluations
        except SQLAlchemyError as e:
            logger.exception("Failed to retrieve datapoint evaluations")
            raise SQLAlchemyError(
                "Failed to retrieve datapoint evaluations") from e

    def get_all_datasets(self, session: Session, dataset_data: GetDatasetsDTO) -> list[Dataset]:
        logger.debug(f"Dataset data: {dataset_data}")
        try:
            query = session.query(Dataset)
            dataset_name: str = dataset_data.dataset_name
            augmented: bool = dataset_data.augmented
            category: DatasetCategory = dataset_data.category
            initial_dataset_ids: int = dataset_data.initial_dataset_ids
            project_id: int = dataset_data.project_id
            is_global: bool = dataset_data.is_global
            excluded_project_id: int = dataset_data.exlude_project_id

            if dataset_name:
                query = query.filter(
                    Dataset.dataset_name.ilike(f"%{dataset_name}%"))
            if augmented:
                query = query.filter(
                    Dataset.augmented == augmented)
            if category:
                query = query.filter(
                    Dataset.category == category)
            if initial_dataset_ids:
                # Filter for datasets that have any of the provided initial_dataset_ids
                query = query.filter(
                    Dataset.initial_datasets.any(
                        Dataset.id.in_(initial_dataset_ids))
                )
            if project_id:
                query = query.filter(
                    Dataset.projects.any(Project.id == project_id)
                )
            if is_global is not None:
                query = query.filter(
                    Dataset.is_global == is_global)

            # Apply additional filtering based on excluded_project_id
            # Only returns models that do not directly belong to the excluded project id (meaning, the entries where the datasets have been initially associated to this project (by creatuion date) are excluded) - Must be excluded via first creation date because order is not viable
            if excluded_project_id is not None:
                # Create a subquery to find all datasets where the first project association is not the excluded_project_id
                exclusion_subquery = (
                    session.query(
                        project_dataset_link.c.dataset_id,
                        func.row_number().over(
                            partition_by=project_dataset_link.c.dataset_id,
                            order_by=project_dataset_link.c.created_at
                        ).label('row_num'),
                        project_dataset_link.c.project_id
                    )
                    .subquery()
                )

                exclusion_subquery_alias = aliased(exclusion_subquery)

                # Filter out datasets whose first project association is the excluded_project_id
                query = query.join(
                    exclusion_subquery_alias,
                    and_(
                        Dataset.id == exclusion_subquery_alias.c.dataset_id,
                        exclusion_subquery_alias.c.row_num == 1,
                        exclusion_subquery_alias.c.project_id != excluded_project_id
                    )
                )

            datasets: list[Dataset] = query.all()

            return datasets
        except SQLAlchemyError as e:
            logger.exception("Failed to retrieve datasets")
            raise SQLAlchemyError("Failed to retrieve datasets") from e

    def get_all_training_runs(self, session: Session, training_run_data: GetTrainingRunsDTO) -> list[TrainingRun]:
        logger.debug(f"Training run data: {training_run_data}")

        try:
            query = session.query(TrainingRun)

            if training_run_data.model_id is not None:
                query = query.filter(TrainingRun.model_id ==
                                     training_run_data.model_id)
            if training_run_data.seed is not None:
                query = query.filter(TrainingRun.seed ==
                                     training_run_data.seed)
            if training_run_data.epochs is not None:
                query = query.filter(TrainingRun.epochs ==
                                     training_run_data.epochs)
            if training_run_data.learning_rate_multiplier is not None:
                query = query.filter(
                    TrainingRun.learning_rate_multiplier == training_run_data.learning_rate_multiplier)
            if training_run_data.batch_size is not None:
                query = query.filter(
                    TrainingRun.batch_size == training_run_data.batch_size)
            if training_run_data.fine_tuning_model is not None:
                query = query.filter(
                    TrainingRun.fine_tuning_model == training_run_data.fine_tuning_model)
            # Create a subquery to find all model IDs associated with the given project_id
            if training_run_data.project_id is not None:
                project_id = training_run_data.project_id
                subquery = (
                    session.query(
                        project_model_link.c.model_id
                    )
                    .filter(project_model_link.c.project_id == project_id)
                    .subquery()
                )

                # Alias the subquery to use it in the join
                subquery_alias = aliased(subquery)

                # Join the TrainingRun table with the Model table using the subquery
                query = query.join(Model, TrainingRun.model_id == Model.id).join(
                    subquery_alias, Model.id == subquery_alias.c.model_id
                )

            training_runs: list[TrainingRun] = query.all()
            return training_runs

        except SQLAlchemyError as e:
            logger.exception("Failed to retrieve training runs")
            raise SQLAlchemyError("Failed to retrieve training runs") from e

    def update_training_runs(self, session: Session, update_training_run_dtos: list[UpdateTrainingRunDTO]) -> list[TrainingRun]:
        logger.debug(f"""Updating training runs with data: {
                     update_training_run_dtos}""")
        updated_training_runs: list[TrainingRun] = []

        try:
            for update_data in update_training_run_dtos:
                # Retrieve the existing training run
                training_run = session.get(TrainingRun, update_data.id)

                if not training_run:
                    raise ValueError(f"""Training run with ID {
                                     update_data.id} not found.""")

                # Update the fields only if they are not None
                if update_data.epochs is not None:
                    training_run.epochs = update_data.epochs
                if update_data.learning_rate_multiplier is not None:
                    training_run.learning_rate_multiplier = update_data.learning_rate_multiplier
                if update_data.batch_size is not None:
                    training_run.batch_size = update_data.batch_size
                if update_data.seed is not None:
                    training_run.seed = update_data.seed

                updated_training_runs.append(training_run)

            return updated_training_runs

        except SQLAlchemyError as e:
            logger.exception("Failed to update training runs")
            session.rollback()
            raise SQLAlchemyError("Failed to update training runs") from e

    # For retrieving all models associated with a project filterable by name and version
    def get_models_by_project_id(self, session: Session, model_project_data: GetModelsByProjectIdDTO) -> list[Model]:
        logger.debug(f"Model_project_data: {model_project_data}")
        try:
            # Start building the query
            query = session.query(Model).filter(
                Model.project_id == model_project_data.project_id)

            # Additional filters based on the provided dictionary
            if model_project_data.name:
                query = query.filter(Model.model_name.ilike(
                    f"%{model_project_data.name}%"))
            if model_project_data.version:
                query = query(Model).filter(
                    or_(
                        Model.version > model_project_data.version,
                        and_(Model.version.like(
                            f"{model_project_data.version}.%"), Model.version > model_project_data.version)
                    ))
            models: list[Model] = query.all()
            return models
        except SQLAlchemyError as e:
            logger.exception(
                "Failed to retrieve models for project")
            raise SQLAlchemyError(
                "Failed to retrieve models for project") from e

    # Retrieve all datasets associated with a model filterable by dataset name, augmented and dataset category
    def get_datasets_by_model_id(self, session: Session, dataset_model_data: GetDatasetsByModelIdDTO) -> list[Dataset]:
        logger.debug(f"Dataset_model_data: {dataset_model_data}")
        try:
            # Alias for the Model table
            model_alias = aliased(Model)

            # Directly filtering datasets associated with the model_id
            query: Query = session.query(Dataset).select_from(model_alias).join(Dataset.models).filter(
                model_alias.id == dataset_model_data.model_id)

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
            return datasets
        except SQLAlchemyError as e:
            logger.exception(
                "Failed to retrieve datasets for model.")
            raise SQLAlchemyError(
                "A database error occurred while retrieving datasets for the model.") from e

    def get_datapoints_by_dataset_id(self, session: Session, dataset_datapoints_data: GetDatapointsByDatasetIdDTO) -> list[DataPointDTO]:
        """Fetched all datasets belonging to a specified dataset, with all their datapoint relations for this specific dataset"""
        logger.debug(f"Dataset_datapoints_data: {dataset_datapoints_data}")
        try:
            # Initialize the query with the session and DataPoint model
            query = session.query(DataPoint).filter(
                DataPoint.dataset_id == dataset_datapoints_data.dataset_id)

            if dataset_datapoints_data.augmentation_type:
                query = query.filter(
                    DataPoint.augmentation_type == dataset_datapoints_data.augmentation_type)

            datapoints: list[DataPoint] = query.all()
            return datapoints
        except SQLAlchemyError as e:
            logger.exception(
                "Failed to retrieve datapoints from dataset.")
            raise SQLAlchemyError(
                "A database error occurred while retrieving datapoints.") from e

    # The function to retrieve all model evaluations remains as is, correctly fetching all evaluations for a given model
    def get_model_evaluations_by_model_id(self, session: Session, model_id: int) -> list[ModelEvaluation]:
        logger.debug(f"Model id: {model_id}")
        try:
            evaluations: list[ModelEvaluation] = session.query(
                ModelEvaluation).filter(ModelEvaluation.model_id == model_id).all()
            return evaluations
        except SQLAlchemyError as e:
            logger.exception(
                "Failed to retrieve evaluations for model.")
            raise SQLAlchemyError(
                "A database error occurred while retrieving model evaluations.") from e

    # Retrieve the training run of a model
    def get_training_run_by_model_id(self, session: Session, model_id: int) -> list[TrainingRun]:
        logger.debug(f"Model id: {model_id}")
        try:
            training_run: TrainingRun = session.query(
                TrainingRun).filter_by(model_id=model_id).one()
            return [training_run]
        except MultipleResultsFound as e:
            logger.exception(
                "Too many training runs found when trying to get training run by model id.")
            raise MultipleResultsFound(
                "Too many training runs found. Expected only one.") from e
        except NoResultFound as e:
            logger.exception(
                "No training runs found when trying to get training run by model id.")
            raise NoResultFound(
                "No training run found for the given model ID.") from e
        except SQLAlchemyError as e:
            logger.exception("Failed to retrieve training run by model id.")
            raise SQLAlchemyError(
                "A database error occurred while retrieving the training run by model id.") from e

    def get_model_by_id(self, session: Session, model_id: int) -> list[Model]:
        logger.debug(f"Model id: {model_id}")
        """Retrieve a model by its ID."""
        try:
            model: Model = session.query(
                Model).filter_by(id=model_id).one()
            return [model]
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

    def get_dataset_by_id(self, session: Session, dataset_id: int) -> list[Dataset]:
        logger.debug(f"Dataset id: {dataset_id}")
        """Retrieve a dataset by its ID."""
        try:
            dataset: Dataset = session.query(
                Dataset).filter_by(id=dataset_id).one()
            return [dataset]
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

    def get_project_by_id(self, session: Session, project_id: int) -> list[Project]:
        logger.debug(f"Project id: {project_id}")
        """Retrieve a project by its ID."""
        try:
            project: Project = session.query(
                Project).filter_by(id=project_id).one()
            return [project]
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

    def get_training_run_by_id(self, session: Session, training_run_id: int) -> list[TrainingRun]:
        logger.debug(f"Training run id: {training_run_id}")
        """Retrieve a training run by its ID."""
        try:
            training_run: TrainingRun = session.query(TrainingRun).filter_by(
                id=training_run_id).one()
            return [training_run]
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

    def get_datapoint_by_id(self, session: Session, datapoint_id: int) -> list[DataPoint]:
        logger.debug(f"Datapoint id: {datapoint_id}")
        """Retrieve a datapoint by its ID."""
        try:
            datapoint: DataPoint = session.query(DataPoint).filter_by(
                id=datapoint_id).one()
            return [datapoint]
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

    def get_model_evaluation_by_id(self, session: Session, model_evlauation_id: int) -> list[ModelEvaluation]:
        logger.debug(f"Model evaluation id: {model_evlauation_id}")
        """Retrieve a model evaluation by its ID."""
        try:
            model_evaluation: ModelEvaluation = session.query(ModelEvaluation).filter_by(
                id=model_evlauation_id).one()
            return [model_evaluation]
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

    def get_datapoint_evaluation_by_id(self, session: Session, datapoint_evlauation_id: int) -> list[DataPointEvaluation]:
        logger.debug(f"Datapoint evaluation id: {datapoint_evlauation_id}")
        """Retrieve a datapoint evaluation by its ID."""
        try:
            model_evaluation: DataPointEvaluation = session.query(DataPointEvaluation).filter_by(
                id=datapoint_evlauation_id).one()
            return [model_evaluation]
        except MultipleResultsFound as e:
            logger.exception(
                "Too many datapoints found when trying to get model evaluation by id.")
            raise MultipleResultsFound(
                "Multiple datapoint evaluations found. Expected only one.") from e
        except NoResultFound as e:
            logger.exception(
                "No datapoint evaluation found when trying to get model evaluation by id.")
            raise NoResultFound(
                "No datapoint evaluation found for the given ID.") from e
        except SQLAlchemyError as e:
            logger.exception(
                "A database error occurred while trying to retrieve a datapoint evaluation.")
            raise SQLAlchemyError(
                "A database orccured while trying to retrieve datapoint evaluation by ID.") from e
