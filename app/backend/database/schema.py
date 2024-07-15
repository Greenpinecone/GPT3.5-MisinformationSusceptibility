from uuid import uuid4
from sqlalchemy import ARRAY, Column, Integer, String, ForeignKey, Table, DateTime, Boolean, func, Enum, Float, JSON
from sqlalchemy.orm import declarative_base, backref, relationship
from sqlalchemy.schema import CheckConstraint, UniqueConstraint
import enum

from app.backend.custom_types.typedicts import AugmentationConfiguration

# INFO: See this post for clarity for how cascading deletes on database level or thourgh SQLA work! -> https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete

# To differentiate whether a dataset is a training or a test dataset in the Datasets table


class DatasetCategory(enum.Enum):
    training = "training"
    test = "test"


# To only allow certain strings for the evaluation confusion matrix in the ModelEvaluations table
class EvaluationType(enum.Enum):
    T = "T"
    F = "F"

    @classmethod
    def values(cls):
        return [cls.T.value, cls.F.value]


# To differentiate between different augmentation types in the Datapoints table
class AugmentationType(enum.Enum):
    BT = "backtranslation"
    EDA = "easy_data_augmentation"


class FineTuningCompany(enum.Enum):
    openai = "openai"
    google = "google"


class FineTuningModelVersions(enum.Enum):
    openai = [
        "gpt-3.5-turbo-0125",        # January 25, 2023
        "gpt-3.5-turbo-1106",        # November 6, 2023
        # "gpt-4-0613",                # June 13, 2024 NOT AVAILABLE YET
        # "gpt-4o-2024-05-13",         # May 13, 2024 NOT AVAILABLE YET
    ]
    google = [
        "non existent google models"
    ]


# The first role is the default role
class MessageKeys(enum.Enum):
    openai = [("system", "assistant", "user")]
    google = [("nonexistent roles", "nonexistent assistant role")]


class UploadFormats(enum.Enum):
    openai = {
        "gpt-3.5-turbo-0125": ["jsonl"],
        "gpt-3.5-turbo-1106": ["jsonl"],
        # "gpt-4-0613": ["jsonl"], NOT AVAILABLE YET
        # "gpt-4o-2024-05-13": ["jsonl"], NOT AVAILABLE YET
    }
    google = {
        "non existent google models": ["nonexistent google format"]
    }


Base = declarative_base()

project_dataset_link = Table(
    'project_dataset_link', Base.metadata,
    Column('project_id', Integer, ForeignKey(
        'projects.id', ondelete="CASCADE"), primary_key=True),
    Column('dataset_id', Integer, ForeignKey(
        'datasets.id', ondelete="CASCADE"), primary_key=True),
    Column('created_at', DateTime, default=func.now())
)

datapoint_relationships = Table(
    'datapoint_relationships',
    Base.metadata,
    Column('source_datapoint_id', Integer, ForeignKey(
        'datapoints.id',  ondelete="CASCADE"), primary_key=True),
    Column('target_datapoint_id', Integer, ForeignKey(
        'datapoints.id',  ondelete="CASCADE"), primary_key=True)
)

# Deletes all augmented datasets of this dataset to ensure referencial integrity on dataset delete.
initial_dataset_association = Table(
    'initial_dataset_association', Base.metadata,
    Column('initial_dataset_id', Integer, ForeignKey(
        'datasets.id', ondelete="CASCADE"), primary_key=True),
    Column('augmented_dataset_id', Integer,
           ForeignKey('datasets.id', ondelete="CASCADE"), primary_key=True),
)

# Ensure that each model can only occure once per project with the same model_name and version to avoid confusion with simillar named models.
project_model_link = Table(
    'project_model_link', Base.metadata,
    Column('model_id', Integer, ForeignKey(
        'models.id', ondelete="CASCADE"), primary_key=True),
    Column('project_id', Integer, ForeignKey(
        'projects.id', ondelete="CASCADE"), primary_key=True),
    Column('model_name', String, nullable=False),
    Column('version', String, nullable=False),
    Column('created_at', DateTime, default=func.now()),
    # INFO: Creates an issue if you try to add a model with the same name from another project or if the base model is the same and now you have two times the same mode, doesnt make sense.
    # INFO 2: I will still use this unique constraint since every other solution is super complex with a multitude of problems to solve that come with it. Instead I automatically use a unique identifier which I append to each new models name to avoid any conflicts.
    UniqueConstraint('model_name', 'version',
                     'project_id', name='_model_project_version_uc')
)
# Association table for the many-to-many relationship
model_dataset_association = Table(
    'model_dataset_association', Base.metadata,
    Column('model_id', Integer, ForeignKey('models.id')),
    Column('dataset_id', Integer, ForeignKey('datasets.id'))
)

current_project_data_evaluation_association = Table(
    'current_project_data_evaluation_association',
    Base.metadata,
    Column('current_project_data_id', Integer, ForeignKey(
        'current_project_data.id', ondelete="CASCADE"), primary_key=True),
    Column('datapoint_evaluation_id', Integer, ForeignKey(
        'datapoint_evaluations.id', ondelete="CASCADE"), primary_key=True)
)

current_project_data_statistic_model_associations = Table(
    'current_project_data_statistic_model_associations',
    Base.metadata,
    Column('current_project_data_id', Integer, ForeignKey(
        'current_project_data.id', ondelete="CASCADE"), primary_key=True),
    Column('statistic_model_id', Integer, ForeignKey(
        'models.id', ondelete="CASCADE"), primary_key=True)
)

current_project_data_checkpoint_models_associations = Table(
    'current_project_data_checkpoint_models_associations',
    Base.metadata,
    Column('current_project_data_id', Integer, ForeignKey(
        'current_project_data.id', ondelete="CASCADE"), primary_key=True),
    Column('statistic_model_id', Integer, ForeignKey(
        'models.id', ondelete="CASCADE"), primary_key=True)
)


# One project can have multiple datasets and models.
# Each project has a name.
# TODO: When projects are deleted, datasets and models must be deleted manually beforehand since we have to check if the datasets / models originated from other projects initially (set global) - first entry in the projects list from the dataset model side is the original project - and if the current project is not equal to this id, then the dataset / model should not be deleted.
class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    project_name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    description = Column(String)
    # Relationship to models
    models = relationship(
        "Model",
        secondary=project_model_link,
        back_populates="projects"
    )
    datasets = relationship(
        "Dataset", secondary=project_dataset_link, back_populates="projects")


# ONLY Initial datasets will be able to be used for augmentation. Each augmentated dataset is created from exactly one initial dataset and cannot be used for further augmentation.
# Datasets belong to one or more project, have a name, can be augmented or not, can be a training dataset or a test dataset and always have exactly one initial dataset. A Dataset consists of many datapoints. Each dataset only needs one evaluation of datapoints because this is universal no matter how many models use the dataset.
class Dataset(Base):
    __tablename__ = 'datasets'
    id = Column(Integer, primary_key=True)
    dataset_name = Column(String, nullable=False)
    augmented = Column(Boolean, nullable=False)
    category = Column(Enum(DatasetCategory), nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_global = Column(Boolean, nullable=False)
    # The company the formatting belongs to
    fine_tuning_company = Column(Enum(FineTuningCompany), nullable=False)
    fine_tuning_model = Column(String, nullable=False)
    # What formatting was used for the dataset datapoints - are the datapoints formatted for openai, google etc. (roles, content)
    fine_tuning_formatting = Column(String, nullable=False)
    projects = relationship(
        "Project", secondary=project_dataset_link, back_populates="datasets")
    # Foreign key for the test dataset (self-referencing)
    test_dataset_id = Column(
        Integer, ForeignKey('datasets.id'))
    # Relationship to the initial dataset from which this dataset was augmented (if any). Many to many relationships have a small syntactic chnage for ondelte=Cascade via the database. -> https://docs.sqlalchemy.org/en/20/orm/cascades.html#using-foreign-key-on-delete-with-many-to-many-relationships
    initial_datasets = relationship(
        'Dataset',
        secondary=initial_dataset_association,
        primaryjoin=id == initial_dataset_association.c.augmented_dataset_id,
        secondaryjoin=id == initial_dataset_association.c.initial_dataset_id,
        back_populates='augmented_datasets', passive_deletes=True)

    # Relationship to the augmented datasets associated with this dataset
    # INFO: It is probably necessary to use only cascade
    augmented_datasets = relationship(
        'Dataset',
        secondary=initial_dataset_association,
        primaryjoin=id == initial_dataset_association.c.initial_dataset_id,
        secondaryjoin=id == initial_dataset_association.c.augmented_dataset_id,
        back_populates='initial_datasets', cascade="save-update, merge, delete"
    )

    # Relationship to the test dataset associated with this dataset
    test_dataset = relationship("Dataset", remote_side=[id],
                                foreign_keys=[test_dataset_id],
                                # Assuming each dataset has exactly one test dataset
                                back_populates="training_datasets", uselist=False)

    training_datasets = relationship(
        "Dataset",
        back_populates="test_dataset"
    )

    datapoints = relationship(
        "DataPoint", order_by="DataPoint.id", back_populates="dataset",
        cascade="save-update, merge, delete", passive_deletes=True
    )

    # Many-to-many relationship with Model
   # TODO: Right now no models are deleted if a dataset is deleted. This is because datasets should only be deleted when all models are deleted and these models should be deleted first. Datasets should virtually never be deleted.
    models = relationship(
        "Model",
        secondary=model_dataset_association,
        back_populates="training_datasets"
    )

    __table_args__ = (
        UniqueConstraint('dataset_name', 'category',
                         name='_dataset_name_category_uc'),
    )


# Each Datapoint belongs to exactly one Dataset. Each datapoint has a coherence score (comapring to the initial datapoint), a relevancy score (comparing to the initial datapoint), a semantic similarity score (comapring to the initial datapoint), and augmentation type (backtranslation, EDA or nothing if it is an initial datapoint) and the datapoint id of its initial datapoint from which it has been augmented from if it is augmented, else null. And each datapoint holds a JSON array (messages) consisting of an array of conversational dicts in openai format. And a category string that should match the category in the test dataset for easy matching of training datapoints with corresponding test datapoints.
class DataPoint(Base):
    __tablename__ = 'datapoints'
    id = Column(Integer, primary_key=True)
    # Delete the datapoint if the dataset id is deleted.
    dataset_id = Column(Integer, ForeignKey('datasets.id', ondelete="CASCADE"),
                        nullable=False)  # ForeignKey pointing to Dataset
    augmentation_type = Column(
        Enum(AugmentationType))  # null = not augmented
    # Add a column for storing messages in JSON format
    messages = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    # To store the "ground truth" label for the confusion matrix
    evaluation_type = Column(Enum(EvaluationType))
    # Reference to the initial datapoint
    # Delete the datapoint if the initial_datapoint_id is deleted.
    initial_datapoint_id = Column(
        # The initial dataset
        Integer, ForeignKey('datapoints.id', ondelete="CASCADE"), nullable=True)
    # Orm relationship for initial_datapoint
    initial_datapoint = relationship(
        "DataPoint", remote_side=[id], back_populates="derived_datapoints",
        uselist=False,
    )
    # Relationship for derived datapoints
    # Automatically deletes all datapoints that have been augmented from this datapoints
    derived_datapoints = relationship(
        "DataPoint", back_populates="initial_datapoint", cascade="save-update, merge, delete", passive_deletes=True
    )
    # Self-referencing many-to-many relationship for related datapoints
    # IMPORTANT INFO: There are two use cases for this relationship:
    # 1. If a test datapoint is created, all related / matched trainings datapoints are added to this test datapoin via related_datapoints
    # 2. (This is more complicated) If a datapoint is augmented from an original trainings datapoint, The test datapoints that were related to the original trainings datapoint will be added to the augmented datapoints "related_datapoints" list. This is to avoid changing the original test datasets relations since the test dataset is reused by all child models which would cause wrong relations to show during model evaluation. Instead by storing the related test datapoints in the augmented "related_datapoints" list, it is independently stored. This will cause the augmented datapoints to show up in the test datapoints "related_by" list. Since we have now separated the orginal test datapoints relations from the augmented ones, we need to combine them back together, when we want to display all datapoints (original and augmented) that influence the outcome of a specific test datapoint. To do so, we get the current model evaluations test datapoint from the original dataset. Then check for all augemnted datapoints, if one of them includes this test datapoint in its "related_datapoints" list, and if so, we take this augmented datapoint and add it to the ComplexModelAvaluationDTO.datapoint.related_datapoints list. We add it to the mapped DTO already to avoid changing the underlying entity relation. We do this for all previous models and their augmented datasets. This way we gather all augmented datapoints from the current model and all its predecessors  that were augmented from original datapoints which were related to this specific test datpoint
    related_datapoints = relationship(
        "DataPoint",
        secondary=datapoint_relationships,
        primaryjoin=id == datapoint_relationships.c.target_datapoint_id,
        secondaryjoin=id == datapoint_relationships.c.source_datapoint_id,
        back_populates="related_by"
    )

    related_by = relationship(
        "DataPoint",
        secondary=datapoint_relationships,
        primaryjoin=id == datapoint_relationships.c.source_datapoint_id,
        secondaryjoin=id == datapoint_relationships.c.target_datapoint_id,
        back_populates="related_datapoints"
    )
    # Bidirectional relationship (many DataPoints belong to one Dataset)
    dataset = relationship(
        "Dataset", back_populates="datapoints",
        uselist=False
    )

    evaluations = relationship(
        "DataPointEvaluation", back_populates="datapoint",
        cascade="save-update, merge, delete", passive_deletes=True
    )

    model_evaluations = relationship(
        "ModelEvaluation", back_populates="datapoint",
        cascade="save-update, merge, delete", passive_deletes=True
    )


# A model can be trained with multiple different datasets. It has a name. If you save a model with an already existing name, the version is incremented. It has a parent model id - this is relevant if you use an already trained model as base model. Evaluations points to the ModelEvaluations table, holding additional evaluation information of the model. Datasets is a one to many relationship to the datasets the model has been trained with. Training Runs points to additional information regarding the openai training run information.
class Model(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)
    # If the parent model is deleted all child models are deleted too
    parent_model_id = Column(Integer, ForeignKey(
        'models.id'))
    semantic_similarity_model = Column(String)
    # The main version of the model (increased for each model trained directly from a base model (version 0))
    version = Column(String, default="0")
    created_at = Column(DateTime, default=func.now())
    # full id of the fine tuned model to retrieve it
    fine_tuning_job_id = Column(String)
    # The fine tuning job id of the checkpoint model - if this is set it must be a checkpoint model
    fine_tuning_checkpoint_job_id = Column(String)
    # The id of the fine tuned model as you would use it to directly make api requests
    fine_tuned_model_id = Column(String)
    # A unique identifier independent from the model id, which can be used to identify any resources stored at openai
    uuid = Column(String, default=lambda: str(uuid4()))
    # if the model is set global to choose
    is_global = Column(Boolean, nullable=False)
    # Is the model one of the checkpoint models, openai creates after each epoch training
    is_checkpoint_model = Column(Boolean)
    # At which checkpoint step was the checkpoint model created
    checkpoint_step = Column(Integer)
    # A list of AugmentationConfigurations
    augmentation_configurations = Column(JSON(dict), default=list)

    # Many-to-many relationship with Dataset
    training_datasets = relationship(
        "Dataset",
        secondary=model_dataset_association,
        back_populates="models",
    )

    # Many-to-many relationship to projects
    projects = relationship(
        "Project",
        secondary=project_model_link,
        back_populates="models",
    )

    # TODO: Could potentially be converted to a one to many relationship
    # Correctly setup for multiple training runs per model
    # The training run is deleted if the associated model is deleted.
    training_run = relationship(
        "TrainingRun", back_populates="model", uselist=False, cascade="save-update, merge, delete", passive_deletes=True)

    # Orm relationship for initial_datapoint
    # All child models get deleted if a model gets deleted to ensure referencial consistency
    parent_model = relationship("Model", remote_side=[
        id], back_populates="child_models",  uselist=False)

    # Add the child_models relationship
    # Delete all child models on model deletion
    # TODO: FOR GODS SAKE, IT JUST DOES NOT WANT TO BE DELETED BY THE DATABSE DIRECTLY VIA "DLETED_PASSIVE and ONDELETE=CASCADE" SO I AM USING THE SQLA DELETION WHERE ALL UNLOADED RELATED OBJECTS ARE FETCHED AND THEN DELETED WHICH FOR SOME REASON WORKS!!!
    child_models = relationship(
        "Model", back_populates="parent_model", cascade="save-update, merge, delete")

    evaluations = relationship(
        "ModelEvaluation", back_populates="model", cascade="save-update, merge, delete", passive_deletes=True)

    datapoint_evaluations = relationship("DataPointEvaluation",
                                         back_populates="model", cascade="save-update, merge, delete", passive_deletes=True)

    # current_project_data = relationship(
    #     "CurrentProjectData",
    #     secondary=current_project_data_statistic_model_associations,
    #     back_populates="selected_statistic_models"
    # )

# This table holds information regarding the evaluation of a model against its trainingsdataset(s). The model id points to the model this information belongs to. The evaluation type can be one of four values for the confusion matrix. And the helpful_score, honest_score and harmless_score is for saving the HHH criteria related data for each datapoint for later calculating the results and also reevaluating the previous evaluation. The datapoint id saves the reference to the original datapoint that was evaluated.


class ModelEvaluation(Base):
    __tablename__ = 'model_evaluations'
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey(
        'models.id', ondelete='CASCADE'), nullable=False)
    datapoint_id = Column(Integer, ForeignKey(
        'datapoints.id', ondelete='CASCADE'), nullable=False)
    evaluation_type = Column(Enum(EvaluationType))
    # 0 is the placeholder value that is not counted, only 1-10 are included in the result
    helpful_score = Column(Integer)
    honest_score = Column(Integer)
    harmless_score = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    # The related datapoints messages with the answers generated by the fine tuned model
    messages = Column(JSON, nullable=False)
    # Semantic similarity measure between user defined test output and trained model prediction.
    semantic_similarity_score = Column(Float)
    # One-to-many relationship from ModelEvaluation to its DataPoint
    datapoint = relationship(
        "DataPoint", back_populates="model_evaluations",
        uselist=False
    )
    # One-to-many relationship from ModelEvaluation to the model the datapoint belongs to
    model = relationship(
        "Model", back_populates="evaluations",
        uselist=False
    )

    # Apply a table-level constraint
    __table_args__ = (
        UniqueConstraint('model_id', 'datapoint_id',
                         name='uq_model_id_datapoint_id'),
    )


# The training run stores specific information about the training of a specific model. The model id references the model this information belongs to. Epochs specifies the amount of epochs the model has been trained for. Learning rate multiplier specifies how strongly the model has been trained on the information. Batch size specifies how large the batches of information are, the model is trained with each run.
class TrainingRun(Base):
    __tablename__ = 'training_runs'
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.id', ondelete='CASCADE'),
                      unique=True, nullable=False)
    epochs = Column(Integer)
    learning_rate_multiplier = Column(Float)
    batch_size = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    seed = Column(Integer)
    fine_tuning_model = Column(String)
    # TODO: Could be updated to a one to many relationship - one training run, many models (for checkpoint models)
    # Back-populates to model.training_runs
    model = relationship("Model", back_populates="training_run",
                         uselist=False)


# The data the current project needs to reestablish configuration after page reload and session state deletion
class CurrentProjectData(Base):
    __tablename__ = "current_project_data"
    # INFO: When a foreign key is defined without the ondelete option, it defaults to RESTRICT. This means if you try to delete a referenced row in the parent table, and there are dependent rows in the child table, the deletion will be blocked to maintain referential integrity. That is why we have to set "ondelete=SET NULL" on all of the foreign key relations in this table, so that the related entities can be deleted without an referential integrity error.

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    # If the user is currently in an unfinished operation
    unfinished_progress = Column(Boolean, default=False)
    # The last page the user visited
    current_page = Column(String)
    # Should checkpoint models also be saved if they are created
    save_checkpoint_models = Column(Boolean, default=False)
    # The currently selected model for semantic similarity score calculation
    semantic_similarity_model = Column(JSON(dict))
    # The id of the currently created dataset
    currently_modified_dataset_id = Column(
        Integer, ForeignKey('datasets.id', ondelete="SET NULL"))
    # The base model used for fine tuning the current fine tuning model
    selected_model_for_fine_tuning_id = Column(
        Integer, ForeignKey('models.id', ondelete="SET NULL"))
    fine_tuning_step_counter = Column(Integer, default=0)
    # The currently by the suer selected augmentation configurations
    current_augmentation_configurations = Column(JSON, default=list)
    # The current project the user is working with
    current_project_id = Column(Integer, ForeignKey(
        'projects.id', ondelete="SET NULL"))
    # The model id of the model currently newly created and fine tuned
    current_fine_tuning_model_id = Column(
        Integer, ForeignKey('models.id', ondelete="SET NULL"))
    current_project = relationship("Project", uselist=False)
    # The model that is currently sleected as base model for the current fine tuned model
    selected_model_for_fine_tuning = relationship(
        "Model", uselist=False, foreign_keys=[selected_model_for_fine_tuning_id])
    currently_modified_dataset = relationship(
        "Dataset", uselist=False)
    # The model that is currently fine tuned
    current_fine_tuning_model = relationship(
        "Model", uselist=False, foreign_keys=[current_fine_tuning_model_id])
    # Models selected for statistical analysis
    selected_statistic_models = relationship(
        "Model",
        secondary=current_project_data_statistic_model_associations
    )
    generated_checkpoint_models = relationship(
        "Model",
        secondary=current_project_data_checkpoint_models_associations
    )
    # Add the relationship to DataPointEvaluations of the currently augmented dataset
    current_augmented_datapoint_evaluations = relationship(
        "DataPointEvaluation",
        secondary=current_project_data_evaluation_association,
        back_populates="current_project_data"
    )

# Used to evaluate augmented training datapoints


class DataPointEvaluation(Base):
    __tablename__ = 'datapoint_evaluations'
    id = Column(Integer, primary_key=True)
    # This ensures that the DataPointEvaluations are removed if the corresponding model is removed
    model_id = Column(Integer, ForeignKey(
        'models.id', ondelete="CASCADE"), nullable=False)
    # This ensures that the DataPointEvaluations are removed if the corresponding datapoint is removed
    datapoint_id = Column(Integer, ForeignKey(
        'datapoints.id', ondelete="CASCADE"), nullable=False)
    # 1-10 score for coherence
    coherence_score = Column(Integer)
    # 1-10 score for relevance
    relevance_score = Column(Integer)
    # Semantic similarity measure between initial datapoint and augmented one.
    semantic_similarity_score = Column(Float)
    created_at = Column(DateTime, default=func.now())
    # Many to one relationship from ModelEvaluation to its DataPoint
    # This ensures that when the DataPointEvaluations currently not loaded are not laoded via a select statement to be deleted but via the Database Cascade delete from the foreign key relation. (unnecessary overhead)
    datapoint = relationship(
        "DataPoint", back_populates="evaluations",
        uselist=False
    )
    # Many to one relationship from ModelEvaluation to its model
    # This ensures that when the DataPointEvaluations currently not loaded are not laoded via a select statement to be deleted but via the Database Cascade delete from the foreign key relation. (unnecessary overhead)
    model = relationship(
        "Model", back_populates="datapoint_evaluations",
        uselist=False
    )
    # Backreference to the current project data that stores the augmented datapoint evaluations. Using an association table to avoid storing unnecessary Foreign key fields in DAtaPointEvaluation that will be mostly null.
    current_project_data = relationship(
        "CurrentProjectData",
        secondary=current_project_data_evaluation_association,
        back_populates="current_augmented_datapoint_evaluations"
    )
