from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean, func, Enum, Float, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CheckConstraint, UniqueConstraint
import enum


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


class FineTuningCompany(enum.Enum):
    openai = "openai"
    google = "google"


class FineTuningModelVersions(enum.Enum):
    openai = ["gpt-3.5-turbo", "gpt-4"]
    google = ["non existent google models"]


# The first role is the default role
class MessageKeys(enum.Enum):
    openai = [("system", "assistant", "user")]
    google = [("nonexistent roles",)]


class UploadFormats(enum.Enum):
    openai = {"gpt-3.5-turbo": ["jsonl"], "gpt-4": ["jsonl"]}
    google = {"non existent google models": ["nonexistent google format"]}


Base = declarative_base()

project_dataset_link = Table(
    'project_dataset_link', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('dataset_id', Integer, ForeignKey('datasets.id'), primary_key=True)
)

datapoint_relationships = Table(
    'datapoint_relationships',
    Base.metadata,
    Column('source_datapoint_id', Integer, ForeignKey(
        'datapoints.id'), primary_key=True),
    Column('target_datapoint_id', Integer, ForeignKey(
        'datapoints.id'), primary_key=True)
)
project_model_link = Table(
    'project_model_link',  # Table name
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('model_id', Integer, ForeignKey('models.id'), primary_key=True)
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
                                   backref="augmented_datasets", uselist=False)

    # Relationship to the test dataset associated with this dataset
    test_dataset = relationship("Dataset", remote_side=[id],
                                foreign_keys=[test_dataset_id],
                                # Assuming each dataset has exactly one test dataset
                                backref="training_datasets", uselist=False)

    datapoints = relationship(
        "DataPoint", order_by="DataPoint.id", back_populates="dataset")

    model = relationship(
        "Model", back_populates="training_dataset", uselist=False)

    __table_args__ = (
        UniqueConstraint('dataset_name', 'category',
                         name='_dataset_name_category_uc'),
    )


# Each Datapoint belongs to exactly one Dataset. Each datapoint has a coherence score (comapring to the initial datapoint), a relevancy score (comparing to the initial datapoint), a semantic similarity score (comapring to the initial datapoint), and augmentation type (backtranslation, EDA or nothing if it is an initial datapoint) and the datapoint id of its initial datapoint from which it has been augmented from if it is augmented, else null. And each datapoint holds a JSON array (messages) consisting of an array of conversational dicts in openai format. And a category string that should match the category in the test dataset for easy matching of training datapoints with corresponding test datapoints.
class DataPoint(Base):
    __tablename__ = 'datapoints'
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'),
                        nullable=False)  # ForeignKey pointing to Dataset
    # 1-10 score for coherence
    coherence_score = Column(Integer)
    # 1-10 score for relevance
    relevance_score = Column(Integer)
    # Semantic similarity measure between initial datapoint and augmented one.
    semantic_similarity_score = Column(Float)
    augmentation_type = Column(
        Enum(AugmentationType))  # null = not augmented
    # Add a column for storing messages in JSON format
    messages = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    # Reference to the initial datapoint
    initial_datapoint_id = Column(
        # The initial dataset
        Integer, ForeignKey('datapoints.id'), nullable=True)
    # Orm relationship for initial_datapoint
    initial_datapoint = relationship("DataPoint", remote_side=[
                                     id], backref="derived_datapoints", uselist=False)
    # Self-referencing many-to-many relationship for related datapoints
    related_datapoints = relationship(
        "DataPoint",
        secondary=datapoint_relationships,
        primaryjoin=id == datapoint_relationships.c.source_datapoint_id,
        secondaryjoin=id == datapoint_relationships.c.target_datapoint_id,
        backref="related_by"
    )
    # Bidirectional relationship (many DataPoints belong to one Dataset)
    dataset = relationship(
        "Dataset", back_populates="datapoints", uselist=False)


# A model can be trained with multiple different datasets. It has a name. If you save a model with an already existing name, the version is incremented. It has a parent model id - this is relevant if you use an already trained model as base model. Evaluations points to the ModelEvaluations table, holding additional evaluation information of the model. Datasets is a one to many relationship to the datasets the model has been trained with. Training Runs points to additional information regarding the openai training run information.
class Model(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False, unique=True)
    parent_model_id = Column(Integer, ForeignKey('models.id'))
    version = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    # full id of the fine tuned model to retrieve it
    full_fine_tuned_model_id = Column(String(), unique=True)
    # if the model is set global to choose
    is_global = Column(Boolean, nullable=False)
    # what is the model version that was used for fine tuning
    fine_tuning_model = Column(String)
    # Is the model one of the checkpoint models, openai creates after each epoch training
    is_checkpoint_model = Column(Boolean)
    # At which checkpoint step was the checkpoint model created
    checkpoint_step = Column(Integer)

    # References the training dataset which again references the test dataset
    training_dataset_id = Column(Integer, ForeignKey('datasets.id'),
                                 nullable=False, unique=True)  # ForeignKey pointing to Dataset
    training_dataset = relationship(
        "Dataset", back_populates="model", uselist=False)

    # Many-to-many relationship to projects
    projects = relationship(
        "Project",
        secondary=project_model_link,
        back_populates="models"
    )
    # Correctly setup for multiple training runs per model
    training_run = relationship(
        "TrainingRun", back_populates="model", uselist=False)
    # Orm relationship for initial_datapoint
    parent_model = relationship("Model", remote_side=[
        id], backref="child_models", uselist=False)


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
    datapoint = relationship("DataPoint", uselist=False)
    # One-to-many relationship from ModelEvaluation to the model the datapoint belongs to
    model = relationship("Model", uselist=False)

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
