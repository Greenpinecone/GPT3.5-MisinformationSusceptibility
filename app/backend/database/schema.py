from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean, func, Enum, Float, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CheckConstraint, UniqueConstraint
import enum
import uuid


# To differentiate whether a dataset is a training or a test dataset in the Datasets table
class DatasetCategory(enum.Enum):
    training = "training"
    test = "test"


# To only allow certain strings for the evaluation confusion matrix in the ModelEvaluations table
class EvaluationType(enum.Enum):
    TP = "TP"
    TN = "TN"
    FP = "FP"
    FN = "FN"


# To differentiate between different augmentation types in the Datapoints table
class AugmentationType(enum.Enum):
    BT = "backtranslation"
    EDA = "easy_data_augmentation"


Base = declarative_base()

model_dataset_link = Table(
    'model_dataset_link', Base.metadata,
    Column('model_id', Integer, ForeignKey('models.id'), primary_key=True),
    Column('dataset_id', Integer, ForeignKey('datasets.id'), primary_key=True)
)
project_dataset_link = Table(
    'project_dataset_link', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('dataset_id', Integer, ForeignKey('datasets.id'), primary_key=True)
)
# Association table between Datasets and DataPoints
dataset_datapoints_association = Table(
    'dataset_datapoints_association',
    Base.metadata,
    Column('dataset_id', Integer, ForeignKey('datasets.id'), primary_key=True),
    Column('datapoint_id', Integer, ForeignKey(
        'datapoints.id'), primary_key=True)
)

# Table to link DataPoints within the context of specific Datasets
datapoint_links = Table(
    'datapoint_links',
    Base.metadata,
    Column('dataset_id', Integer, ForeignKey('datasets.id'), primary_key=True),
    Column('source_datapoint_id', Integer, ForeignKey(
        'datapoints.id'), primary_key=True),
    Column('target_datapoint_id', Integer, ForeignKey(
        'datapoints.id'), primary_key=True)
)


# One project can have multiple datasets and models.
# Each project has a name.
class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    project_name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    description = Column(String)
    # Relationship to models
    # One project to many models
    models = relationship("Model", back_populates="project")
    datasets = relationship(
        "Dataset", secondary=project_dataset_link, back_populates="projects")


# ONLY Initial datasets will be able to be used for augmentation. Each augmentated dataset is created from exactly one initial dataset and cannot be used for further augmentation.
# Datasets belong to one or more project, have a name, can be augmented or not, can be a training dataset or a test dataset and always have exactly one initial dataset. A Dataset consists of many datapoints. Each dataset only needs one evaluation of datapoints because this is universal no matter how many models use the dataset.
class Dataset(Base):
    __tablename__ = 'datasets'
    id = Column(Integer, primary_key=True)
    dataset_name = Column(String, nullable=False, unique=True)
    augmented = Column(Boolean, nullable=False)
    category = Column(Enum(DatasetCategory), nullable=False)
    created_at = Column(DateTime, default=func.now())
    # Foreign key for the initial dataset (self-referencing)
    initial_dataset_id = Column(
        Integer, ForeignKey('datasets.id'))
    # Foreign key for the test dataset (self-referencing)
    test_dataset_id = Column(
        Integer, ForeignKey('datasets.id'))
    projects = relationship(
        "Project", secondary=project_dataset_link, back_populates="datasets")

    # Relationship to the initial dataset from which this dataset was augmented (if any)
    initial_dataset = relationship("Dataset", remote_side=[id],
                                   foreign_keys=[initial_dataset_id],
                                   backref="augmented_datasets")

    # Relationship to the test dataset associated with this dataset
    test_dataset = relationship("Dataset", remote_side=[id],
                                foreign_keys=[test_dataset_id],
                                backref="training_datasets")  # Assuming each dataset has exactly one test dataset

    datapoints = relationship(
        "DataPoint",
        secondary=dataset_datapoints_association,
        back_populates="datasets")


# Each Datapoint belongs to exactly one Dataset. Each datapoint has a coherence score (comapring to the initial datapoint), a relevancy score (comparing to the initial datapoint), a semantic similarity score (comapring to the initial datapoint), and augmentation type (backtranslation, EDA or nothing if it is an initial datapoint) and the datapoint id of its initial datapoint from which it has been augmented from if it is augmented, else null. And each datapoint holds a JSON array (messages) consisting of an array of conversational dicts in openai format. And a category string that should match the category in the test dataset for easy matching of training datapoints with corresponding test datapoints.
class DataPoint(Base):
    __tablename__ = 'datapoints'
    id = Column(Integer, primary_key=True)
    # 1-10 score for coherence
    coherence_score = Column(Integer)
    # 1-10 score for relevance
    relevance_score = Column(Integer)
    # Semantic similarity measure between initial datapoint and augmented one. TODO: Check what values this score can take and add constraint. This score is automatically calculated for each entry.
    semantic_similarity_score = Column(Float)
    augmentation_type = Column(
        Enum(AugmentationType))  # null = not augmented
    # Add a column for storing messages in JSON format
    messages = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    # The category the datapoint belongs to in the dataset
    category = Column(String, nullable=False)
    # Reference to the initial datapoint
    initial_datapoint_id = Column(
        # The initial dataset
        Integer, ForeignKey('datapoints.id'), nullable=True)
    # Orm relationship for initial_datapoint
    initial_datapoint = relationship("DataPoint", remote_side=[
                                     id], backref="derived_datapoints")
    datasets = relationship(
        "Dataset",
        secondary=dataset_datapoints_association,
        back_populates="datapoints")


# A model can be trained with multiple different datasets. It has a name. If you save a model with an already existing name, the version is incremented. It has a parent model id - this is relevant if you use an already trained model as base model. Evaluations points to the ModelEvaluations table, holding additional evaluation information of the model. Datasets is a one to many relationship to the datasets the model has been trained with. Training Runs points to additional information regarding the openai training run information.
class Model(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)
    parent_model_id = Column(Integer, ForeignKey('models.id'))
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    # ForeignKey to reference Project
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    # Store UUID as a string in SQLite, used as suffix for fine tuning jobs to allow multiple models with the same name.
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    # Relationship to Project - A model can belong to a project but a project can have multiple models.
    project = relationship("Project", back_populates="models")
    # References both the current training datasets + the current test dataset. One way Model -> Datasets.
    datasets = relationship(
        'Dataset', secondary=model_dataset_link)
    # Correctly setup for multiple training runs per model
    training_run = relationship(
        "TrainingRun", back_populates="model", uselist=False)
    # Orm relationship for initial_datapoint
    parent_model = relationship("Model", remote_side=[
        id], backref="child_models")

    __table_args__ = (
        UniqueConstraint('model_name', 'project_id', 'version', 'parent_model_id',
                         name='uq_model_name_project_id_version'),
    )

# This table holds information regarding the evaluation of a model against its trainingsdataset(s). The model id points to the model this information belongs to. The evaluation type can be one of four values for the confusion matrix. And the helpful_score, honest_score and harmless_score is for saving the HHH criteria related data for each datapoint for later calculating the results and also reevaluating the previous evaluation. The datapoint id saves the reference to the original datapoint that was evaluated.


class ModelEvaluation(Base):
    __tablename__ = 'model_evaluations'
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    datapoint_id = Column(Integer, ForeignKey('datapoints.id'), nullable=False)
    evaluation_type = Column(Enum(EvaluationType), nullable=False)
    helpful_score = Column(Integer, nullable=False)  # 1-10
    honest_score = Column(Integer, nullable=False)  # 1-10
    harmless_score = Column(Integer, nullable=False)  # 1-10
    created_at = Column(DateTime, default=func.now())
    # One-to-many relationship from ModelEvaluation to its DataPoint
    datapoint = relationship("DataPoint")
    # One-to-many relationship from ModelEvaluation to the model the datapoint belongs to
    model = relationship("Model")

    # Apply a table-level constraint
    __table_args__ = (
        UniqueConstraint('model_id', 'datapoint_id',
                         name='uq_model_id_datapoint_id'),
        CheckConstraint('helpful_score BETWEEN 1 AND 10'),
        CheckConstraint('honest_score BETWEEN 1 AND 10'),
        CheckConstraint('harmless_score BETWEEN 1 AND 10'),
    )


# The training run stores specific information about the training of a specific model. The model id references the model this information belongs to. Epochs specifies the amount of epochs the model has been trained for. Learning rate multiplier specifies how strongly the model has been trained on the information. Batch size specifies how large the batches of information are, the model is trained with each run.
class TrainingRun(Base):
    __tablename__ = 'training_runs'
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.id'),
                      unique=True, nullable=False)
    epochs = Column(Integer, nullable=False)
    learning_rate_multiplier = Column(Float, nullable=False)
    batch_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    # Back-populates to model.training_runs
    model = relationship("Model", back_populates="training_run", uselist=False)
