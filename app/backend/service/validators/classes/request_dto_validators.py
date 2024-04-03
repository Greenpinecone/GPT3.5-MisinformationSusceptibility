from typing import List, Optional
from marshmallow import Schema, fields, validates, ValidationError, validate, post_load
from typing import List
from ....database.schema import DatasetCategory, EvaluationType, AugmentationType
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from ....persistence.interfaces.i_data_manager import IDataManager
from ....dtos.create_request import *
from ....dtos.get_request import *
import enum


class MessageKeys(enum.Enum):
    user = "user"
    system = "system"
    assistant = "assistant"


class CreateProjectSchema(Schema):
    project_name = fields.Str(
        required=True,
        validate=lambda n: len(n) <= 255 and len(n) > 0,
        error_messages={
            'required': 'Project name is required.',
            'validator_failed': 'Project name must be between 1 and 255 characters.'
        }
    )
    description = fields.Str(
        validate=lambda n: len(n) <= 4000,
        allow_none=True,
        missing=None,
        error_messages={
            'validator_failed': 'Description must not exceed 4000 characters.'
        }
    )
    model_ids = fields.List(
        fields.Int(validate=lambda n: n > 0),
        allow_none=True,
        missing=None,
        error_messages={
            'invalid': 'Model IDs must be positive integers.',
            'validator_failed': 'All model IDs must exist and be greater than 0.'
        }
    )
    dataset_ids = fields.List(
        fields.Int(validate=lambda n: n > 0),
        allow_none=True,
        missing=None,
        error_messages={
            'invalid': 'Dataset IDs must be positive integers.',
            'validator_failed': 'All dataset IDs must exist and be greater than 0.'
        }
    )

    def __init__(self, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager

    @validates('model_ids')
    def validate_models(self, model_ids: List[int]):
        missing_models = []
        for model_id in model_ids:
            try:
                self.data_manager.get_model_by_id(model_id)
            except NoResultFound:
                missing_models.append(model_id)

        if missing_models:
            raise ValidationError(
                f"Models with IDs {missing_models} do not exist.")

    @validates('dataset_ids')
    def validate_datasets(self, dataset_ids: List[int]):
        missing_datasets = []
        for dataset_id in dataset_ids:
            try:
                self.data_manager.get_dataset_by_id(dataset_id)
            except NoResultFound:
                missing_datasets.append(dataset_id)

        if missing_datasets:
            raise ValidationError(f"""Datasets with IDs {
                                  missing_datasets} do not exist.""")

    @post_load
    def make_create_project_dto(self, data, **kwargs):
        return CreateProjectDTO(**data)


class CreateDatasetSchema(Schema):
    dataset_name = fields.Str(
        required=True,
        validate=lambda s: len(s) <= 255 and len(s) > 0,
        error_messages={
            'required': 'Dataset name is required.',
            'validator_failed': 'Dataset name must be between 1 and 255 characters.'
        }
    )
    augmented = fields.Boolean(
        required=True,
        error_messages={
            'required': 'The augmented flag is required.',
            'invalid': 'The augmented flag must be a boolean value.'
        }
    )
    category = fields.Str(
        required=True,
        validate=validate.OneOf(
            [category.value for category in DatasetCategory],
            error='Invalid category. Must be one of: training, test.'
        ),
        error_messages={
            'required': 'Category is required.',
            'validator_failed': 'Invalid category. Must be "training" or "test".'
        }
    )
    project_ids = fields.List(
        fields.Int(validate=lambda n: n > 0),
        allow_none=True, missing=None,
        error_messages={
            'invalid': 'Project IDs must be positive integers.',
            'validator_failed': 'Each project ID must exist and be greater than 0.'
        }
    )
    initial_dataset_id = fields.Int(
        validate=lambda n: n > 0, allow_none=True, missing=None,
        error_messages={
            'invalid': 'Initial dataset ID must be a positive integer.',
            'validator_failed': 'Initial dataset ID must exist and be greater than 0.'
        }
    )
    test_dataset_id = fields.Int(
        required=True, validate=lambda n: n > 0,
        error_messages={
            'required': 'Test dataset ID is required.',
            'invalid': 'Test dataset ID must be a positive integer.',
            'validator_failed': 'Test dataset ID must exist and be greater than 0.'
        }
    )
    datapoint_ids = fields.List(
        fields.Int(validate=lambda n: n > 0), required=True,
        error_messages={
            'invalid': 'Datapoint IDs must be positive integers.',
            'required': 'At least one datapoint ID is required.',
            'validator_failed': 'Each datapoint ID must exist and be greater than 0.'
        }
    )

    def __init__(self, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager

    @validates('project_ids')
    def validate_projects(self, project_ids: List[int]):
        missing_projects = []
        for project_id in project_ids:
            try:
                self.data_manager.get_project_by_id(project_id)
            except NoResultFound:
                missing_projects.append(project_id)

        if missing_projects:
            raise ValidationError(f"""Projects with IDs {
                                  missing_projects} do not exist.""")

    @validates('initial_dataset_id')
    def validate_initial_dataset(self, initial_dataset_id: int):
        if initial_dataset_id:
            try:
                self.data_manager.get_dataset_by_id(initial_dataset_id)
            except NoResultFound:
                raise ValidationError(f"""Initial dataset with ID {
                                      initial_dataset_id} does not exist.""")

    @validates('test_dataset_id')
    def validate_test_dataset(self, test_dataset_id: int):
        try:
            self.data_manager.get_dataset_by_id(test_dataset_id)
        except NoResultFound:
            raise ValidationError(f"""Test dataset with ID {
                                  test_dataset_id} does not exist.""")

    @validates('datapoint_ids')
    def validate_datapoints(self, datapoint_ids: List[int]):
        missing_datapoints = []
        for datapoint_id in datapoint_ids:
            try:
                self.data_manager.get_datapoint_by_id(datapoint_id)
            except NoResultFound:
                missing_datapoints.append(datapoint_id)

        if missing_datapoints:
            raise ValidationError(f"""Datapoints with IDs {
                                  missing_datapoints} do not exist.""")

    @post_load
    def make_dataset_dto(self, data, **kwargs):
        return CreateDatasetDTO(**data)


class CreateDataPointSchema(Schema):
    dataset_id = fields.Int(
        required=True,
        error_messages={
            'required': 'Dataset ID is required.',
            'invalid': 'Dataset ID must be a positive integer.'
        }
    )
    coherence_score = fields.Int(
        validate=lambda n: 1 <= n <= 10, missing=None, allow_none=True,
        error_messages={
            'invalid': 'Coherence score must be an integer between 1 and 10.',
            'validator_failed': 'Coherence score must be between 1 and 10.'
        }
    )
    relevance_score = fields.Int(
        validate=lambda n: 1 <= n <= 10, missing=None, allow_none=True,
        error_messages={
            'invalid': 'Relevance score must be an integer between 1 and 10.',
            'validator_failed': 'Relevance score must be between 1 and 10.'
        }
    )
    semantic_similarity_score = fields.Float(
        missing=None, allow_none=True,
        error_messages={
            'invalid': 'Semantic similarity score must be a float.'
        }
    )
    augmentation_type = fields.Str(
        validate=validate.OneOf(
            [type_.value for type_ in AugmentationType],
            error='Invalid augmentation type.'
        ),
        missing=None, allow_none=True,
        error_messages={
            'invalid': 'Invalid augmentation type. Must be one of the specified types.',
            'validator_failed': 'Augmentation type must be "backtranslation" or "easy_data_augmentation".'
        }
    )
    messages = fields.Dict(fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()), required=True,
                           error_messages={
        'required': 'Messages are required.',
        'invalid': 'Keys and values of the message objects must be strings.'
    }))

    initial_datapoint_id = fields.Int(
        missing=None, allow_none=True,
        error_messages={
            'invalid': 'Category must be a string.',
            'validator_failed': 'Category must be less than 255 characters long.'
        }
    )

    category = fields.Str(required=False, allow_none=False,
                          validate=lambda n: len(n) <= 255)

    def __init__(self, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager

    @validates('messages')
    def validate_message_keys(self, messages):
        valid_keys = {key.value for key in MessageKeys}
        for message in messages:
            for key in message.keys():
                if key not in valid_keys:
                    raise ValidationError(f"""Invalid key '{key}'. Must be one of {
                                          list(valid_keys)}.""")

    @validates('dataset_id')
    def validate_dataset_exists(self, dataset_id: int):
        try:
            self.data_manager.get_dataset_by_id(dataset_id)
        except NoResultFound:
            raise ValidationError(
                f"Dataset with ID {dataset_id} does not exist.")

    @validates('initial_datapoint_id')
    def validate_initial_datapoint_exists(self, datapoint_id: int):
        if datapoint_id:
            try:
                self.data_manager.get_datapoint_by_id(datapoint_id)
            except NoResultFound:
                raise ValidationError(f"""Initial datapoint with ID {
                                      datapoint_id} does not exist.""")

    @post_load
    def make_create_datapoint_dto(self, data, **kwargs):
        return CreateDataPointDTO(**data)


class CreateModelSchema(Schema):
    model_name = fields.Str(
        required=True,
        validate=lambda s: len(s) <= 255 and len(s) > 0,
        error_messages={
            'required': 'Model name is required.',
            'validator_failed': 'Model name must be between 1 and 255 characters.'
        }
    )
    parent_model_id = fields.Int(
        missing=None,
        allow_none=True,
        error_messages={
            'invalid': 'Parent model ID must be a positive integer.',
        }
    )
    version = fields.Int(
        strict=True,
        required=True,
        validate=lambda n: n > 0,
        error_messages={
            'required': 'Version is required.',
            'invalid': 'Version must be a positive integer.',
            'validator_failed': 'Version must be greater than 0.'
        }
    )
    project_id = fields.Int(
        required=True,
        error_messages={
            'required': 'Project ID is required.',
            'invalid': 'Project ID must be a positive integer.'
        }
    )
    dataset_ids = fields.List(
        fields.Int(validate=lambda n: n > 0),
        missing=None,
        allow_none=True,
        error_messages={
            'invalid': 'Dataset IDs must be a list of positive integers.',
            'validator_failed': 'All dataset IDs must be greater than 0.'
        }
    )
    training_run_id = fields.Int(
        missing=None,
        allow_none=True,
        error_messages={
            'invalid': 'Training run ID must be a positive integer.',
        }
    )

    def __init__(self, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager

    @validates('parent_model_id')
    def validate_parent_model_exists(self, parent_model_id: int):
        if parent_model_id:
            try:
                self.data_manager.get_model_by_id(parent_model_id)
            except NoResultFound:
                raise ValidationError(f"""Parent model with ID {
                                      parent_model_id} does not exist.""")

    @validates('project_id')
    def validate_project_exists(self, project_id: int):
        try:
            self.data_manager.get_project_by_id(project_id)
        except NoResultFound:
            raise ValidationError(
                f"Project with ID {project_id} does not exist.")

    @validates('dataset_ids')
    def validate_datasets_exist(self, dataset_ids: List[int]):
        missing_datasets = []
        for dataset_id in dataset_ids:
            try:
                self.data_manager.get_dataset_by_id(dataset_id)
            except NoResultFound:
                missing_datasets.append(dataset_id)
        if missing_datasets:
            raise ValidationError(f"""Datasets with IDs {
                                  missing_datasets} do not exist.""")

    @validates('training_run_id')
    def validate_training_run_exists(self, training_run_id: int):
        if training_run_id:
            try:
                self.data_manager.get_training_run_by_id(training_run_id)
            except NoResultFound:
                raise ValidationError(f"""Training run with ID {
                                      training_run_id} does not exist.""")

    @post_load
    def make_create_model_dto(self, data, **kwargs):
        return CreateModelDTO(**data)


class CreateModelEvaluationSchema(Schema):
    model_id = fields.Int(
        required=True,
        error_messages={
            'required': 'Model ID is required.',
            'invalid': 'Model ID must be a positive integer.'
        }
    )
    datapoint_id = fields.Int(
        required=True,
        error_messages={
            'required': 'Datapoint ID is required.',
            'invalid': 'Datapoint ID must be a positive integer.'
        }
    )
    evaluation_type = fields.Str(
        required=True,
        validate=lambda et: et in [et.value for et in EvaluationType],
        error_messages={
            'required': 'Evaluation type is required.',
            'validator_failed': 'Evaluation type must be one of the predefined types.'
        }
    )
    helpful_score = fields.Int(
        required=True,
        validate=lambda n: 1 <= n <= 10,
        error_messages={
            'required': 'Helpful score is required.',
            'invalid': 'Helpful score must be an integer.',
            'validator_failed': 'Helpful score must be between 1 and 10.'
        }
    )
    honest_score = fields.Int(
        required=True,
        validate=lambda n: 1 <= n <= 10,
        error_messages={
            'required': 'Honest score is required.',
            'invalid': 'Honest score must be an integer.',
            'validator_failed': 'Honest score must be between 1 and 10.'
        }
    )
    harmless_score = fields.Int(
        required=True,
        validate=lambda n: 1 <= n <= 10,
        error_messages={
            'required': 'Harmless score is required.',
            'invalid': 'Harmless score must be an integer.',
            'validator_failed': 'Harmless score must be between 1 and 10.'
        }
    )

    def __init__(self, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager

    @validates('model_id')
    def validate_model_id(self, model_id: int):
        try:
            self.data_manager.get_model_by_id(model_id)
        except NoResultFound:
            raise ValidationError(f"Model with ID {model_id} does not exist.")

    @validates('datapoint_id')
    def validate_datapoint_id(self, datapoint_id: int):
        try:
            self.data_manager.get_datapoint_by_id(datapoint_id)
        except NoResultFound:
            raise ValidationError(f"""Datapoint with ID {
                                  datapoint_id} does not exist.""")

    @post_load
    def make_create_model_evaluation_dto(self, data, **kwargs):
        return CreateModelEvaluationDTO(**data)


class CreateTrainingRunSchema(Schema):
    model_id = fields.Int(
        required=True,
        error_messages={
            'required': 'Model ID is required.',
            'invalid': 'Model ID must be a positive integer.'
        }
    )
    epochs = fields.Int(
        required=True, validate=lambda n: n > 0,
        error_messages={
            'required': 'Number of epochs is required.',
            'invalid': 'Number of epochs must be a positive integer.',
            'validator_failed': 'Number of epochs must be greater than 0.'
        }
    )
    learning_rate_multiplier = fields.Float(
        required=True, validate=lambda n: n > 0,
        error_messages={
            'required': 'Learning rate multiplier is required.',
            'invalid': 'Learning rate multiplier must be a positive float.',
            'validator_failed': 'Learning rate multiplier must be greater than 0.'
        }
    )
    batch_size = fields.Int(
        required=True, validate=lambda n: n > 0,
        error_messages={
            'required': 'Batch size is required.',
            'invalid': 'Batch size must be a positive integer.',
            'validator_failed': 'Batch size must be greater than 0.'
        }
    )

    def __init__(self, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager

    @validates('model_id')
    def validate_model_id(self, model_id):
        try:
            self.data_manager.get_model_by_id(model_id)
        except NoResultFound:
            raise ValidationError(f"Model with ID {model_id} does not exist.")

    @post_load
    def make_create_training_run_dto(self, data, **kwargs):
        return CreateTrainingRunDTO(**data)


class GetProjectsSchema(Schema):
    project_name = fields.Str(validate=lambda n: len(n) <= 255,
                              missing=None,
                              allow_none=True,
                              error_messages={
        'invalid': 'Project name must be a string.'
    }
    )
    created_at = fields.DateTime(
        missing=None,
        allow_none=True,
        error_messages={
            'invalid': 'Creation date must be a valid datetime format.'
        }
    )

    def __init__(self, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager

    @post_load
    def make_get_projects_dto(self, data, **kwargs):
        return GetProjectsDTO(**data)


class GetModelsByProjectIdSchema(Schema):
    project_id = fields.Int(
        required=True,
        error_messages={
            'required': 'Project ID is required.',
            'invalid': 'Project ID must be an integer.'
        }
    )
    name = fields.Str(validate=lambda n: len(n) <= 255,
                      missing=None,
                      allow_none=True,
                      error_messages={
        'invalid': 'Model name must be a string.'
    }
    )
    version = fields.Int(
        missing=None,
        allow_none=True,
        validate=lambda n: n > 0,
        error_messages={
            'invalid': 'Version must be a positive integer.',
            'validator_failed': 'Version must be greater than 0.'
        }
    )

    def __init__(self, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager

    @validates('dataset_id')
    def validate_dataset_exists(self, project_id: int):
        try:
            self.data_manager.get_project_by_id(project_id)
        except NoResultFound:
            raise ValidationError(
                f"Project with ID {project_id} does not exist.")

    @post_load
    def make_get_models_by_project_id_dto(self, data, **kwargs):
        return GetModelsByProjectIdDTO(**data)


class GetDatasetsByModelIdSchema(Schema):
    model_id = fields.Int(
        required=True,
        error_messages={
            'required': 'Model ID is required.',
            'invalid': 'Model ID must be an integer.'
        }
    )
    timestamp = fields.DateTime(
        missing=None,
        allow_none=True,
        error_messages={
            'invalid': 'Timestamp must be a valid datetime format.'
        }
    )
    dataset_name = fields.Str(validate=lambda n: len(n) <= 255,
                              missing=None,
                              allow_none=True,
                              error_messages={
        'invalid': 'Dataset name must be a string.'
    }
    )
    augmented = fields.Boolean(
        missing=None,
        allow_none=True,
        error_messages={
            'invalid': 'Augmented must be a boolean value.'
        }
    )
    category = fields.Str(
        missing=None,
        allow_none=True,
        validate=validate.OneOf([e.value for e in DatasetCategory]),
        error_messages={
            'invalid': 'Invalid category. Must be one of the specified values.',
            'validator_failed': 'Invalid category selection.'
        }
    )

    def __init__(self, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager

    @validates('model_id')
    def validate_model_id(self, model_id):
        try:
            self.data_manager.get_model_by_id(model_id)
        except NoResultFound:
            raise ValidationError(f"Model with ID {model_id} does not exist.")

    @post_load
    def make_get_datasets_by_model_id_dto(self, data, **kwargs):
        return GetDatasetsByModelIdDTO(**data)


class GetDatapointsByDatasetIdSchema(Schema):
    dataset_id = fields.Int(
        required=True,
        error_messages={
            'required': 'Dataset ID is required.',
            'invalid': 'Dataset ID must be an integer.'
        }
    )
    coherence_score = fields.Int(
        missing=None,
        allow_none=True,
        validate=lambda n: 1 <= n <= 10,
        error_messages={
            'invalid': 'Coherence score must be between 1 and 10.',
            'validator_failed': 'Coherence score must be an integer between 1 and 10.'
        }
    )
    relevance_score = fields.Int(
        missing=None,
        allow_none=True,
        validate=lambda n: 1 <= n <= 10,
        error_messages={
            'invalid': 'Relevance score must be between 1 and 10.',
            'validator_failed': 'Relevance score must be an integer between 1 and 10.'
        }
    )
    semantic_similarity = fields.Float(
        missing=None,
        allow_none=True,
        error_messages={
            'invalid': 'Semantic similarity score must be a float.'
        }
    )
    augmentation_type = fields.Str(
        missing=None,
        allow_none=True,
        validate=validate.OneOf([e.value for e in AugmentationType]),
        error_messages={
            'invalid': 'Invalid augmentation type.',
            'validator_failed': 'Augmentation type must be one of the specified types.'
        }
    )
    category = fields.Str(required=False, allow_none=False,
                          validate=lambda n: len(n) <= 255)
    initial_datapoint_id = fields.Int(
        missing=None, allow_none=True,
        error_messages={
            'invalid': 'Category must be a string.',
            'validator_failed': 'Category must be less than 255 characters long.'
        }
    )

    def __init__(self, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager

    @validates('dataset_id')
    def validate_dataset_exists(self, dataset_id: int):
        try:
            self.data_manager.get_dataset_by_id(dataset_id)
        except NoResultFound:
            raise ValidationError(
                f"Dataset with ID {dataset_id} does not exist.")

    @post_load
    def make_get_datapoints_by_dataset_id_dto(self, data, **kwargs):
        return GetDatapointsByDatasetIdDTO(**data)
