from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean, func, Enum, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CheckConstraint
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


Base = declarative_base()

model_dataset_link = Table(
    'model_dataset_link', Base.metadata,
    Column('model_id', Integer, ForeignKey('models.id'), primary_key=True),
    Column('dataset_id', Integer, ForeignKey('datasets.id'), primary_key=True)
)

dataset_parent_link = Table(
    'dataset_parent_link', Base.metadata,
    Column('child_id', Integer, ForeignKey('datasets.id'), primary_key=True),
    Column('parent_id', Integer, ForeignKey('datasets.id'), primary_key=True)
)

project_dataset_link = Table(
    'project_dataset_link', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('dataset_id', Integer, ForeignKey('datasets.id'), primary_key=True)
)


# One project can have multiple datasets and models.
# Each project has a name.
class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    project_name = Column(String, unique=True)
    timestamp = Column(DateTime, default=func.now())
    # Relationship to models
    # One project to many models
    models = relationship("Model", back_populates="project")
    datasets = relationship(
        "Dataset", secondary=project_dataset_link, back_populates="projects")


# ONLY Initial datasets will be able to be used for augmentation. Each augmentated dataset is created from exactly one initial dataset and cannot be used for further augmentation.
# Datasets belong to one or more project, have a name, can be augmented or not, can be a training dataset or a test dataset and always have exactly one initial dataset.A Dataset consists of many datapoints.
class Dataset(Base):
    __tablename__ = 'datasets'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    dataset_name = Column(String)
    augmented = Column(Boolean)
    category = Column(Enum(DatasetCategory))
    timestamp = Column(DateTime, default=func.now())
    projects = relationship(
        "Project", secondary=project_dataset_link, back_populates="datasets")
    # Self-referential relationship, a dataset can have exactly one parent and multiple children.
    # only set if the dataset itself is not an initial dataset
    initial_dataset = relationship("Dataset", remote_side=[
                                   id], backref="children")
    # Define the relationship to DataPoint (one to many)
    datapoints = relationship(
        "DataPoint", order_by="dataPoint.id", back_populates="dataset")

    # parents = relationship(
    #     "Dataset",
    #     secondary=dataset_parent_link,
    #     primaryjoin=id == dataset_parent_link.c.child_id,
    #     secondaryjoin=id == dataset_parent_link.c.parent_id,
    #     backref="children"
    # )


# Each Datapoint belongs to exactly one Dataset. Each datapoint has a coherence score (comapring to the initial datapoint), a relevancy score (comparing to the initial datapoint), a semantic similarity score (comapring to the initial datapoint), and augmentation type (backtranslation, EDA or nothing if it is an initial datapoint) and the datapoint id of its initial datapoint from which it has been augmented from if it is augmented, else null. And each datapoint holds a JSON array (messages) consisting of an array of conversational dicts in openai format. And a category string that should match the category in the test dataset for easy matching of training datapoints with corresponding test datapoints.
class DataPoint(Base):
    __tablename__ = 'datapoints'
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id')
                        )  # ForeignKey pointing to Dataset
    # 1-10 score for coherence
    coherence_score = Column(Integer, nullable=True)
    # 1-10 score for relevance
    relevance_score = Column(Integer, nullable=True)
    # Semantic similarity measure between initial datapoint and augmented one. TODO: Check what values this score can take.
    semantic_similarity_score = Column(Float, nullable=True)
    augmentation_type = Column(
        Enum(AugmentationType), nullable=True)  # null = not augmented
    # The category the datapoint belongs to for easier matching of trainings and test datapoints.
    datapoint_category = Column(String)
    messages = Column(JSON)  # Add a column for storing messages in JSON format
    # Reference to the initial datapoint
    initial_datapoint_id = Column(
        # The initial dataset
        Integer, ForeignKey('datapoints.id'), nullable=True)
    # Bidirectional relationship (many DataPoints belong to one Dataset)
    dataset = relationship("Dataset", back_populates="datapoints")

    # Apply a table-level constraint
    __table_args__ = (
        CheckConstraint('coherence_score BETWEEN 1 AND 10'),
        CheckConstraint('relevance_score BETWEEN 1 AND 10'),
    )


# A model can be trained with multiple different datasets. It has a name. If you save a model with an already existing name, the version is incremented. It has a parent model id - this is relevant if you use an already trained model as base model. Evaluations points to the ModelEvaluations table, holding additional evaluation information of the model. Datasets is a one to many relationship to the datasets the model has been trained with. Training Runs points to additional information regarding the openai training run information.
class Model(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    parent_model_id = Column(Integer, ForeignKey('models.id'), nullable=True)
    version = Column(Integer, default=1)
    timestamp = Column(DateTime, default=func.now())
    # ForeignKey to reference Project
    project_id = Column(Integer, ForeignKey('projects.id'))
    # Relationship to Project - A model can belong to a project but a project can have multiple models.
    project = relationship("Project", back_populates="models")
    # One way relationship, one model to many dataevaluations
    evaluations = relationship("ModelEvaluations")
    # References both the current training datasets + the current test dataset. One way Model -> Datasets.
    datasets = relationship(
        'Dataset', secondary=model_dataset_link)
    # Correctly setup for multiple training runs per model
    training_run = relationship(
        "TrainingRun", back_populates="model", order_by="TrainingRun.id")


# This table holds information regarding the evaluation of a model against its trainingsdataset(s). The model id points to the model this information belongs to. The evaluation type can be one of four values for the confusion matrix. And the helpful_score, honest_score and harmless_score is for saving the HHH criteria related data for each datapoint for later calculating the results and also reevaluating the previous evaluation.
class ModelEvaluation(Base):
    __tablename__ = 'model_evaluations'
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)
    evaluation_type = Column(Enum(EvaluationType), nullable=False)
    helpful_score = Column(Integer, nullable=False)  # 1-10
    honest_score = Column(Integer, nullable=False)  # 1-10
    harmless_score = Column(Integer, nullable=False)  # 1-10

    # Apply a table-level constraint
    __table_args__ = (
        CheckConstraint('helpful_score BETWEEN 1 AND 10'),
        CheckConstraint('honest_score BETWEEN 1 AND 10'),
        CheckConstraint('harmless_score BETWEEN 1 AND 10'),
    )


# The training run stores specific information about the training of a specific model. The model id references the model this information belongs to. Epochs specifies the amount of epochs the model has been trained for. Learning rate multiplier specifies how strongly the model has been trained on the information. Batch size specifies how large the batches of information are, the model is trained with each run.
class TrainingRun(Base):
    __tablename__ = 'training_runs'
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.id'))
    epochs = Column(Integer)
    learning_rate_multiplier = Column(Float)
    batch_size = Column(Integer)
    timestamp = Column(DateTime, default=func.now())
    # Back-populates to model.training_runs
    model = relationship("Model", back_populates="training_runs")
