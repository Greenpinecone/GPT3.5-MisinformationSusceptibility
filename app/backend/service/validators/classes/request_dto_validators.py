from datetime import date, timezone
from typing import Any, Optional
from marshmallow import Schema, fields, validates, validates_schema, ValidationError, validate, post_load
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from ....persistence.interfaces.i_data_manager import IDataManager
from ....dtos.create_request import *
from ....dtos.get_request import *
from ....dtos.update_request import *
from ....dtos.response import DatasetDTO, ModelDTO
from sqlalchemy.orm import Session
from app.backend.database.schema import DatasetCategory, MessageKeys, UploadFormats, EvaluationType, AugmentationType, FineTuningCompany, FineTuningModelVersions, MessageKeys, Project, Dataset, DataPoint, Model, ModelEvaluation, TrainingRun
from app.backend.util.config import SBERT_MODELS as semantic_similarity_models


class BaseUpdateSchema(Schema):
    id = fields.Int(
        required=True,
        validate=lambda n: n > 0,
        error_messages={
            'required': 'ID is required.',
            'invalid': 'ID must be a positive integer.'
        }
    )


# Custom Field that validates Enum or its value directly, and handles serialization/deserialization
class CustomEnumValidationField(fields.Enum):
    def __init__(self, enum, *args, **kwargs):
        super().__init__(enum, *args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            if not self.allow_none:
                raise ValidationError("Field may not be None.")

        if not isinstance(value, self.enum):
            raise ValidationError(f"""Expected {self.enum.__name__} instance, got {
                type(value).__name__}.""")

        # Ensure the value is a valid member of the enum class
        if value not in self.enum:
            raise ValidationError(f"""Value '{value.name}' is not a valid {
                self.enum.__name__}.""")

        return value


class FlexibleDateTimeValidationField(fields.DateTime):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # The _validate method only runs together with _deserialize when calling load() on a schema, so it cannot be used to modify the validation process itself. For this purpos, the validate=validation.Length, validates, validate_schema options are abailable directly in the schema class. Still, the _deserialize method runs in certain cases when schema.validate() is called for more complex types to check if the types are correctly convertable (e.g iso string to date etc.) which is part of the validation. So to avoid datetime issues here, the _deserialize method is overwritten to accept any kind of datetime object / string which is then converted to a timezone aware datetime object to fully check validity.
    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            if not self.allow_none:
                raise ValidationError("Field may not be None.")
            return None  # None is allowed, no further validation needed

        # Check if value is a datetime or date object
        if not isinstance(value, datetime):
            if isinstance(value, date):
                # Convert date to datetime with time set to midnight
                value = datetime.combine(value, datetime.min.time())
            else:
                # Attempt to parse ISO string
                try:
                    value = datetime.fromisoformat(value)
                except Exception:
                    raise ValidationError('Invalid datetime format')

        return value


class MessageSchema(Schema):
    role = fields.Str(required=True)
    content = fields.Str(required=True)


class MessagesContainerField(fields.Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_schema = MessageSchema()

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, dict):
            raise ValidationError('Invalid type. Expected a dictionary.')

        messages = value.get('messages')
        if not messages:
            raise ValidationError('The "messages" field is required.')

        if not isinstance(messages, list):
            raise ValidationError(
                'Invalid type for "messages". Expected a list.')

        for message in messages:
            errors = self.message_schema.validate(message)
            if errors:
                raise ValidationError(
                    f'The structure of "messages" is invalid: {errors}')

        return value


class CreateProjectSchema(Schema):
    project_name = fields.Str(
        required=True,
        validate=lambda n: len(n) <= 255 and len(n) > 0,
        error_messages={
            'required': 'Project name is required.',
            'invalid': 'Project name must be between 1 and 255 characters.'
        }
    )
    description = fields.Str(
        validate=lambda n: len(n) <= 4000,
        allow_none=True,
        error_messages={
            'invalid': 'Description must not exceed 4000 characters.'
        }
    )
    model_ids = fields.List(
        fields.Int(validate=lambda n: n > 0),
        error_messages={
            'invalid': 'Model IDs must be positive integers.',
            'invalid': 'All model IDs must exist and be greater than 0.'
        }
    )
    dataset_ids = fields.List(
        fields.Int(validate=lambda n: n > 0),
        error_messages={
            'invalid': 'Dataset IDs must be positive integers.',
            'invalid': 'All dataset IDs must exist and be greater than 0.'
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('model_ids')
    def validate_models(self, model_ids: list[int]):

        missing_models = []
        for model_id in model_ids:
            try:
                self.data_manager.get_model_by_id(self.session, model_id)[0]
            except NoResultFound:
                missing_models.append(model_id)

        if missing_models:
            raise ValidationError(
                f"Models with IDs {missing_models} do not exist.")

    @validates('dataset_ids')
    def validate_datasets(self, dataset_ids: list[int]):

        missing_datasets = []
        for dataset_id in dataset_ids:
            try:
                self.data_manager.get_dataset_by_id(
                    self.session, dataset_id)[0]
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
            'invalid': 'Dataset name must be between 1 and 255 characters.'
        }
    )
    augmented = fields.Boolean(
        required=True,
        error_messages={
            'required': 'The augmented flag is required.',
            'invalid': 'The augmented flag must be a boolean value.'
        }
    )
    category = CustomEnumValidationField(
        DatasetCategory,
        by_value=True,
        required=True,
        error_messages={
            'required': 'Category is required.',
            'invalid': 'Invalid category. Must be one of: {0}.'.format(", ".join([e.value for e in DatasetCategory]))
        }
    )
    fine_tuning_company = CustomEnumValidationField(
        FineTuningCompany,
        by_value=True,
        required=True,
        error_messages={
            'required': 'Fine tuning company is required.',
            'invalid': 'Invalid fine tuning company. Must be one of: {0}.'.format(", ".join([e.value for e in FineTuningCompany]))
        }
    )
    project_ids = fields.List(
        fields.Int(validate=lambda n: n > 0),
        required=True,
        error_messages={
            'invalid': 'Each project ID must exist and be greater than 0.'
        }
    )
    initial_dataset_ids = fields.List(fields.Int(
        validate=lambda n: n > 0, error_messages={
            'invalid': 'Initial dataset IDs must exist and be greater than 0.'
        }),
        allow_none=True,
    )
    test_dataset_id = fields.Int(
        validate=lambda n: n > 0,
        error_messages={
            'invalid': 'Test dataset ID must exist and be greater than 0.'
        },
        allow_none=True
    )
    datapoint_ids = fields.List(
        fields.Int(validate=lambda n: n > 0), allow_none=True,
        error_messages={
            'required': 'At least one datapoint ID is required.',
            'invalid': 'Each datapoint ID must exist and be greater than 0.'
        }
    )
    is_global = fields.Boolean(
        error_messages={
            'invalid': 'Is_global must be either True or False.'
        }
    )

    fine_tuning_formatting = fields.Str(
        required=True,
        error_messages={
            'required': 'Fine tuning formatting is required.',
            'invalid': 'Invalid fine tuning formatting.'
        }
    )

    fine_tuning_model = fields.Str(
        required=True,
        error_messages={
            'required': 'Fine tuning model is required.',
            'invalid': 'Invalid fine tuning model. Must be one of: {0}.'.format(", ".join([model for company in FineTuningModelVersions for model in company.value]))
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('project_ids')
    def validate_projects(self, project_ids: list[int]):

        missing_projects = []
        for project_id in project_ids:
            try:
                self.data_manager.get_project_by_id(
                    self.session, project_id)[0]
            except NoResultFound:
                missing_projects.append(project_id)

        if missing_projects:
            raise ValidationError(f"""Projects with IDs {
                missing_projects} do not exist.""")

    @validates('initial_dataset_ids')
    def validate_initial_dataset(self, dataset_ids: list[int]):

        if dataset_ids:
            missing_dataset_ids: list[int] = []
            for dataset_id in dataset_ids:
                try:
                    self.data_manager.get_dataset_by_id(
                        self.session, dataset_id)[0]
                except NoResultFound:
                    missing_dataset_ids.append(dataset_id)

            if missing_dataset_ids:
                raise ValidationError(f"""Initial datasets with ID {
                    missing_dataset_ids} does not exist.""")

    @validates('test_dataset_id')
    def validate_initial_dataset(self, dataset_id: int):

        if dataset_id:
            try:
                self.data_manager.get_dataset_by_id(
                    self.session, dataset_id)[0]
            except NoResultFound:
                raise ValidationError(f"""Test datasets with ID {
                    dataset_id} does not exist.""")

    @validates('datapoint_ids')
    def validate_datapoints(self, datapoint_ids: list[int]):

        missing_datapoints = []
        if datapoint_ids:
            for datapoint_id in datapoint_ids:
                try:
                    self.data_manager.get_datapoint_by_id(
                        self.session, datapoint_id)[0]
                except NoResultFound:
                    missing_datapoints.append(datapoint_id)

            if missing_datapoints:
                raise ValidationError(f"""Datapoints with IDs {
                    missing_datapoints} do not exist.""")

    # Checks if the combination of company, model and fine tuning format matches
    @validates_schema
    def validate_fine_tuning_combination(self, data: dict[str, Any], **kwargs):
        company: FineTuningCompany = data['fine_tuning_company'].value
        model: str = data['fine_tuning_model']
        formatting: str = data['fine_tuning_formatting']

        # Check if company is valid
        try:
            FineTuningCompany[company]
        except KeyError:
            raise ValidationError(f"Invalid fine tuning company: {company}")

        # Check if model is valid for the company
        try:
            valid_models = FineTuningModelVersions[company].value
            if model not in valid_models:
                raise ValidationError(f"""Invalid fine tuning model: {
                                      model} for company: {company}""")
        except KeyError:
            raise ValidationError(f"Invalid fine tuning company: {company}")

        # Check if formatting is valid for the model
        try:
            valid_formats = UploadFormats[company].value[model]
            if formatting not in valid_formats:
                raise ValidationError(f"""Invalid fine tuning formatting: {
                                      formatting} for model: {model} and company: {company}""")
        except KeyError:
            raise ValidationError(f"""Invalid fine tuning model: {
                                  model} for company: {company}""")

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
    related_datapoint_ids = fields.List(
        fields.Integer(validate=lambda n: n > 0), allow_none=True, error_messages={
            'invalid': 'Related datapoint ids must be > 0',
        })
    augmentation_type = CustomEnumValidationField(
        AugmentationType,
        by_value=True,
        allow_none=True,  # Allows None to be a valid option
        error_messages={
            'invalid': 'Invalid augmentation type. Must be one of: {0}.'.format(", ".join([e.value for e in AugmentationType])),
        }
    )
    messages = MessagesContainerField(required=True,
                                      error_messages={
                                          'required': 'The "messages" field is required.',
                                          'invalid': 'The structure of "messages" is invalid.'
                                      })

    initial_datapoint_id = fields.Int(
        validate=lambda n: n > 0,
        allow_none=True,
        error_messages={
            'invalid': 'Initial datapoint id must exist and be a positive Integer > 0'
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('related_datapoint_ids')
    def validate_datapoints(self, datapoint_ids: list[int]):

        missing_datapoints = []
        if datapoint_ids:
            for datapoint_id in datapoint_ids:
                try:
                    self.data_manager.get_datapoint_by_id(
                        self.session, datapoint_id)[0]
                except NoResultFound:
                    missing_datapoints.append(datapoint_id)

            if missing_datapoints:
                raise ValidationError(f"""Datapoints with IDs {
                    missing_datapoints} do not exist.""")

    @validates('dataset_id')
    def validate_dataset_exists(self, dataset_id: int):

        try:
            self.data_manager.get_dataset_by_id(self.session, dataset_id)[0]
        except NoResultFound:
            raise ValidationError(
                f"Dataset with ID {dataset_id} does not exist.")

    @validates('initial_datapoint_id')
    def validate_initial_datapoint_exists(self, datapoint_id: int):

        if datapoint_id:
            try:
                self.data_manager.get_datapoint_by_id(
                    self.session, datapoint_id)[0]
            except NoResultFound:
                raise ValidationError(f"""Initial datapoint with ID {
                    datapoint_id} does not exist.""")

    @validates_schema
    def validate_roles(self, data: dict[str, Any], **kwargs):

        # Fetch dataset based on dataset_id
        dataset_id = data.get('dataset_id')
        if not dataset_id:
            raise ValidationError("dataset_id is required")

        dataset: Dataset = self.data_manager.get_dataset_by_id(self.session, dataset_id)[
            0]

        # Get the allowed roles for the chosen fine_tuning_company
        try:
            allowed_roles = MessageKeys[dataset.fine_tuning_company.value].value[0]
        except KeyError:
            raise ValidationError(f"""Invalid fine tuning company: {
                dataset.fine_tuning_company.value}""")

        # Validate each role in messages
        for message in data['messages']['messages']:
            if message['role'] not in allowed_roles:
                raise ValidationError(f"""Invalid role: {message['role']}. Must be one of: {
                    ','.join([value for value in allowed_roles])}""")

    @post_load
    def make_create_datapoint_dto(self, data, **kwargs):
        return CreateDataPointDTO(**data)


class CreateModelSchema(Schema):
    model_name = fields.Str(
        required=True,
        validate=lambda s: len(s) <= 255 and len(s) > 0,
        error_messages={
            'required': 'Model name is required.',
            'invalid': 'Model name must be between 1 and 255 characters.'
        }
    )
    parent_model_id = fields.Int(
        allow_none=True,
        error_messages={
            'invalid': 'Parent model ID must be a positive integer.',
        }
    )
    project_ids = fields.List(
        fields.Int(validate=lambda n: n > 0),
        required=True,
        error_messages={
            'invalid': 'Each project ID must exist and be greater than 0.'
        }
    )
    training_dataset_ids = fields.List(fields.Int(validate=lambda n: n > 0, error_messages={
        'invalid': 'All associated training dataset ids must be > 0.'
    }),
        validate=lambda n: len(n) > 0,
        required=True,
        error_messages={
        'required': 'Training dataset list is required.',
        'invalid': 'Model must be associated to at least one training dataset.'
    }
    )
    augmentation_configurations = fields.List(fields.Dict(), allow_none=True)
    semantic_similarity_model = fields.Str(allow_none=True, error_messages={
        'invalid': 'Semantic similarity model must be of type string.'
    })
    training_run_id = fields.Int(
        allow_none=True,
        error_messages={
            'invalid': 'Training run ID must be a positive integer.',
        }
    )
    is_global = fields.Boolean(
        error_messages={
            'invalid': 'Is_global must be either True or False.'
        }
    )
    is_checkpoint_model = fields.Boolean(required=True, error_messages={
        'required': 'Is_checkpoint_model must be set',
                                         'invalid': 'Is_checkpoint_model must be of type boolean.'})
    checkpoint_step = fields.Int(allow_none=True, validate=lambda n: n > 0, error_messages={
        'invalid': 'Checkpoint step must be of type integer > 0.'})

    fine_tuning_job_id = fields.Str(allow_none=True,
                                    validate=lambda s: len(s) > 0,
                                    error_messages={
                                        'invalid': 'Full fine tuned model name must be of type string'
                                    })
    fine_tuning_checkpoint_job_id = fields.Str(allow_none=True, error_messages={
        'invalid': 'Model checkpoint job id must be of type string.'
    })
    fine_tuned_model_id = fields.Str(allow_none=True, error_messages={
        'invalid': 'Full fine tuned model id must be of type string.'
    })

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('parent_model_id')
    def validate_parent_model_exists(self, parent_model_id: int):

        if parent_model_id:
            try:
                self.data_manager.get_model_by_id(
                    self.session, parent_model_id)[0]
            except NoResultFound:
                raise ValidationError(f"""Parent model with ID {
                    parent_model_id} does not exist.""")

    @validates('project_ids')
    def validate_projects(self, project_ids: list[int]):

        missing_projects = []
        for project_id in project_ids:
            try:
                self.data_manager.get_project_by_id(
                    self.session, project_id)[0]
            except NoResultFound:
                missing_projects.append(project_id)

        if missing_projects:
            raise ValidationError(f"""Projects with IDs {
                missing_projects} do not exist.""")

    @validates('semantic_similarity_model')
    def validate_semantic_similarity_model(self, semantic_similarity_model: str):
        if semantic_similarity_model:
            if not any(model["model_name"] == semantic_similarity_model for model in semantic_similarity_models):
                raise ValidationError(f"""Semantic similarity model "{
                    semantic_similarity_model}" does not exist.""")
            return semantic_similarity_model

    @validates('training_dataset_ids')
    def validate_datasets_exist(self, dataset_ids: list[int]):
        missing_dataset_ids: list[int] = []
        try:
            for dataset_id in dataset_ids:
                self.data_manager.get_dataset_by_id(
                    self.session, dataset_id)[0]
        except NoResultFound:
            missing_dataset_ids.append(dataset_id)
        if missing_dataset_ids:
            raise ValidationError(f"""Datasets with ID {
                missing_dataset_ids} do not exist.""")

    @validates('training_run_id')
    def validate_training_run_exists(self, training_run_id: int):

        if training_run_id:
            try:
                self.data_manager.get_training_run_by_id(
                    self.session, training_run_id)[0]
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
    evaluation_type = CustomEnumValidationField(
        EvaluationType,
        by_value=True,
        allow_none=True,
        error_messages={
            'invalid': 'Invalid evaluation type. Must be one of: {0}.'.format(", ".join(e.name for e in EvaluationType))
        }
    )
    helpful_score = fields.Int(
        validate=lambda n: 0 <= n <= 10,
        allow_none=True,
        error_messages={
            'required': 'Helpful score is required.',
            'invalid': 'Helpful score must be an integer between 0 and 10.',
        }
    )
    honest_score = fields.Int(
        validate=lambda n: 0 <= n <= 10,
        allow_none=True,
        error_messages={
            'invalid': 'Honest score must be an integer between 0 and 10.',
        }
    )
    harmless_score = fields.Int(
        validate=lambda n: 0 <= n <= 10,
        allow_none=True,
        error_messages={
            'invalid': 'Harmless score must be an integer between 0 and 10.',
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('model_id')
    def validate_model_id(self, model_id: int):

        try:
            self.data_manager.get_model_by_id(self.session, model_id)[0]
        except NoResultFound:
            raise ValidationError(
                f"Model with ID {model_id} does not exist.")

    @validates('datapoint_id')
    def validate_datapoint_id(self, datapoint_id: int):

        try:
            self.data_manager.get_datapoint_by_id(
                self.session, datapoint_id)[0]
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
    fine_tuning_model = fields.Str(required=True, validate=lambda s: len(s) > 0,  error_messages={
        'required': 'Fine tuning model is required.',
        'invalid': 'Fine tuning model name must be of type string'
    })
    epochs = fields.Int(
        allow_none=True, validate=lambda n: n >= 1 and n <= 10,
        error_messages={
            'invalid': 'Number of epochs must be greater than 0 and smaller than 11.'
        }
    )
    learning_rate_multiplier = fields.Float(
        allow_none=True, validate=lambda n: n >= 0.1 and n <= 10,
        error_messages={
            'invalid': 'Learning rate multiplier must be a positive float greater than 0.0 and smaller than 11.',
        }
    )
    batch_size = fields.Int(
        allow_none=True, validate=lambda n: n >= 1 and n <= 32,
        error_messages={
            'invalid': 'Batch size must be a positive integer greater 0 and smaller 33.',
        }
    )

    seed = fields.Int(
        allow_none=True, validate=lambda n: n >= 0,
        error_messages={
            'invalid': 'Seed must be an  integer greater or equals to 0.',
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('model_id')
    def validate_model_id(self, model_id):

        try:
            self.data_manager.get_model_by_id(self.session, model_id)[0]
        except NoResultFound:
            raise ValidationError(
                f"Model with ID {model_id} does not exist.")

    @validates('fine_tuning_model')
    def validate_fine_tuning_model(self, value: str):
        if value:
            valid_models = []
            for version_list in FineTuningModelVersions:
                valid_models.extend(version_list.value)

            if value not in valid_models:
                raise ValidationError(
                    f"The model version must be one of {valid_models}")

    @post_load
    def make_create_training_run_dto(self, data, **kwargs):
        return CreateTrainingRunDTO(**data)


class CreateDataPointEvaluationSchema(BaseUpdateSchema):
    datapoint_id = fields.Int(
        validate=lambda n: n > 0, required=True, error_messages={
            'required': 'Datapoint id is required.',
            'invalid': 'Datapoint id must be an integer > 0.'
        }
    )
    model_id = fields.Int(
        validate=lambda n: n > 0, required=True, error_messages={
            'required': 'Model id is required.',
            'invalid': 'Model id must be an integer > 0.'
        }
    )
    coherence_score = fields.Int(
        validate=lambda n: 0 <= n <= 10, allow_none=True,
        error_messages={
            'invalid': 'Coherence score must be an integer between 0 and 10.',
        }
    )
    relevance_score = fields.Int(
        validate=lambda n: 0 <= n <= 10, allow_none=True,
        error_messages={
            'invalid': 'Relevance score must be an integer between 0 and 10.',
        }
    )
    semantic_similarity_score = fields.Float(
        allow_none=True,
        validate=lambda n: 0.0 <= n <= 100.0,
        error_messages={
            'invalid': 'Semantic similarity score must be a float.'
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('datapoint_id')
    def validate_datapoint_id(self, datapoint_id: int) -> None:
        try:
            self.data_manager.get_datapoint_by_id(
                self.session, datapoint_id)[0]
        except:
            raise ValidationError(f"""No datapoint with the id {
                                  datapoint_id} found.""")

    @validates('model_id')
    def validate_datapoint_id(self, model_id: int) -> None:
        try:
            self.data_manager.get_model_by_id(
                self.session, model_id)[0]
        except:
            raise ValidationError(f"""No model with the id {
                                  model_id} found.""")

    @post_load
    def make_create_training_run_dto(self, data, **kwargs):
        return CreateDataPointEvaluationDTO(**data)


class GetTrainingRunsSchema(Schema):
    model_id = fields.Int(allow_none=True,
                          error_messages={
                              'invalid': 'Model ID must be a positive integer.'
                          }
                          )
    project_id = fields.Int(allow_none=True,
                            error_messages={
                                'invalid': 'Project ID must be a positive integer.'
                            }
                            )
    epochs = fields.Int(allow_none=True, validate=lambda n: n >= 1 and n <= 10,
                        error_messages={
                            'invalid': 'Number of epochs must be greater than 0 and smaller than 11.'
                        }
                        )
    learning_rate_multiplier = fields.Float(allow_none=True, validate=lambda n: n >= 0.1 and n <= 10,
                                            error_messages={
                                                'invalid': 'Learning rate multiplier must be a positive float greater than 0.0 and smaller than 11.',
                                            }
                                            )
    batch_size = fields.Int(allow_none=True, validate=lambda n: n >= 1 and n <= 32,
                            error_messages={
                                'invalid': 'Batch size must be a positive integer greater 0 and smaller 33.',
                            }
                            )

    seed = fields.Int(allow_none=True, validate=lambda n: n >= 0,
                      error_messages={
                          'invalid': 'Seed must be an  integer greater or equals to 0.',
                      }
                      )
    fine_tuning_model = fields.Str(allow_none=True, validate=lambda s: len(s) > 0,  error_messages={
        'invalid': 'Fine tuning model name must be of type string'
    })

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('model_id')
    def validate_model_id(self, model_id: int | None):
        if model_id:
            try:
                self.data_manager.get_model_by_id(self.session, model_id)[0]
            except NoResultFound:
                raise ValidationError(
                    f"Model with ID {model_id} does not exist.")

    @validates('project_id')
    def validate_model_id(self, project_id: int | None):
        if project_id:
            try:
                self.data_manager.get_project_by_id(
                    self.session, project_id)[0]
            except NoResultFound:
                raise ValidationError(
                    f"Project with ID {project_id} does not exist.")

    @validates('fine_tuning_model')
    def validate_fine_tuning_model(self, value: str):
        if value:
            valid_models = []
            for version_list in FineTuningModelVersions:
                valid_models.extend(version_list.value)

            if value not in valid_models:
                raise ValidationError(
                    f"The model version must be one of {valid_models}")

    @post_load
    def make_create_training_run_dto(self, data, **kwargs):
        return GetTrainingRunsDTO(**data)


class GetProjectsSchema(Schema):
    project_name = fields.Str(validate=lambda n: len(n) <= 255,
                              allow_none=True,
                              error_messages={
        'invalid': 'Project name must be a string.'
    }
    )
    # Handles datetime objects and parseable strings natively
    created_at = FlexibleDateTimeValidationField(
        allow_none=True,
        error_messages={
            'invalid': 'Creation date must be a valid datetime format.'
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @post_load
    def make_get_projects_dto(self, data, **kwargs):
        return GetProjectsDTO(**data)


class GetModelsSchema(Schema):
    model_name = fields.Str(validate=lambda n: len(n) <= 255,
                            allow_none=True,
                            error_messages={
        'invalid': 'Model name must be a string.'
    })
    created_at = FlexibleDateTimeValidationField(
        allow_none=True,
        error_messages={
            'invalid': 'Creation date must be a valid datetime format.'
        }
    )
    version = fields.Str(validate=lambda n: len(n) > 0,
                         allow_none=True,
                         error_messages={
                             'invalid': 'Model version must be a string with len() > 0.'
    })
    is_checkpoint_model = fields.Boolean(allow_none=True, error_messages={
        'invalid': 'Is_checkpoint_model must be either True or False.'
    })

    project_id = fields.Int(validate=lambda n: n >= 1,
                            allow_none=True,
                            error_messages={
                                'invalid': 'Project id must be an Integer >= 1.'
                            })

    is_global = fields.Boolean(allow_none=True,
                               error_messages={
                                   'invalid': 'Is_global must be either True or False.'
                               }
                               )

    exlude_project_id = fields.Int(allow_none=True, validate=lambda n: n > 0, rror_messages={
        'invalid': 'Excluded project id must be > 0.'
    })

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('project_id')
    def validate_project_exists(self, project_id: int):
        if project_id:
            try:
                self.data_manager.get_project_by_id(
                    self.session, project_id)[0]
            except NoResultFound:
                raise ValidationError(
                    f"Project with ID {project_id} does not exist.")

    @validates('exlude_project_id')
    def validate_project_exists(self, project_id: int):
        if project_id:
            try:
                self.data_manager.get_project_by_id(
                    self.session, project_id)[0]
            except NoResultFound:
                raise ValidationError(
                    f"Project with ID {project_id} does not exist.")


class GetDatasetsSchema(Schema):
    dataset_name = fields.Str(validate=lambda n: len(n) <= 255,
                              allow_none=True,
                              error_messages={
        'invalid': 'Dataset name must be a string.'
    })

    augmented = fields.Boolean(
        allow_none=True,
        error_messages={
            'invalid': 'Dataset augmented must be a boolean value.'
        })

    category = CustomEnumValidationField(
        DatasetCategory,
        by_value=True,
        allow_none=True,
        error_messages={
            'invalid': 'Invalid category. Must be one of: {0}.'.format(", ".join([e.value for e in DatasetCategory]))
        }
    )
    initial_dataset_ids = fields.List(fields.Int(
        validate=lambda n: n > 0, error_messages={
            'invalid': 'Initial dataset IDs must exist and be greater than 0.'
        }),
        allow_none=True
    )
    project_id = fields.Int(validate=lambda n: n >= 1,
                            allow_none=True,
                            error_messages={
                                'invalid': 'Project id must be an Integer >= 1.'
                            })
    is_global = fields.Boolean(allow_none=True,
                               error_messages={
                                   'invalid': 'Is_global must be either True or False.'
                               }
                               )
    exlude_project_id = fields.Int(allow_none=True, validate=lambda n: n > 0, rror_messages={
        'invalid': 'Excluded project id must be > 0.'
    })

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('project_id')
    def validate_project_exists(self, project_id: int):
        if project_id:
            try:
                self.data_manager.get_project_by_id(
                    self.session, project_id)[0]
            except NoResultFound:
                raise ValidationError(
                    f"Project with ID {project_id} does not exist.")

    @validates('exlude_project_id')
    def validate_project_exists(self, project_id: int):
        if project_id:
            try:
                self.data_manager.get_project_by_id(
                    self.session, project_id)[0]
            except NoResultFound:
                raise ValidationError(
                    f"Project with ID {project_id} does not exist.")

    @validates('initial_dataset_ids')
    def validate_initial_dataset(self, dataset_ids: list[int]):

        if dataset_ids:
            missing_dataset_ids: list[int] = []
            for dataset_id in dataset_ids:
                try:
                    self.data_manager.get_dataset_by_id(
                        self.session, dataset_id)[0]
                except NoResultFound:
                    missing_dataset_ids.append(dataset_id)

            if missing_dataset_ids:
                raise ValidationError(f"""Initial datasets with ID {
                    missing_dataset_ids} does not exist.""")


class GetModelsByProjectIdSchema(Schema):
    project_id = fields.Int(
        required=True,
        error_messages={
            'required': 'Project ID is required.',
            'invalid': 'Project ID must be an integer.'
        }
    )
    name = fields.Str(validate=lambda n: len(n) <= 255,
                      allow_none=True,
                      error_messages={
        'invalid': 'Model name must be a string.'
    }
    )
    version = fields.Str(
        allow_none=True,
        validate=lambda n: len(n) > 0,
        error_messages={
            'invalid': 'Version must be a string with len > 0.',
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('project_id')
    def validate_project_exists(self, project_id: int):

        try:
            self.data_manager.get_project_by_id(self.session, project_id)[0]
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
    # Handles datetime objects and parseable strings natively
    created_at = FlexibleDateTimeValidationField(
        allow_none=True,
        error_messages={
            'invalid': 'Timestamp must be a valid datetime format.'
        }
    )
    dataset_name = fields.Str(validate=lambda n: len(n) <= 255,
                              allow_none=True,
                              error_messages={
        'invalid': 'Dataset name must be a string.'
    }
    )
    augmented = fields.Boolean(
        allow_none=True,
        error_messages={
            'invalid': 'Augmented must be a boolean value.'
        }
    )
    category = CustomEnumValidationField(
        DatasetCategory,
        by_value=True,
        required=False,  # If the field is not required, you might want to set this to False
        allow_none=True,  # Allow the field to be None if necessary
        error_messages={
            'invalid': 'Invalid category. Must be one of: {0}.'.format(", ".join(e.name for e in DatasetCategory))
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('model_id')
    def validate_model_id(self, model_id):

        try:
            self.data_manager.get_model_by_id(self.session, model_id)[0]
        except NoResultFound:
            raise ValidationError(
                f"Model with ID {model_id} does not exist.")

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
    augmentation_type = CustomEnumValidationField(
        AugmentationType,
        by_value=True,
        allow_none=True,  # Allow the field to be None if necessary
        error_messages={
            'invalid': 'Invalid augmentation type. Must be one of: {0}.'.format(", ".join(e.name for e in AugmentationType)),
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('dataset_id')
    def validate_dataset_exists(self, dataset_id: int):

        try:
            self.data_manager.get_dataset_by_id(self.session, dataset_id)[0]
        except NoResultFound:
            raise ValidationError(
                f"Dataset with ID {dataset_id} does not exist.")

    @post_load
    def make_get_datapoints_by_dataset_id_dto(self, data, **kwargs):
        return GetDatapointsByDatasetIdDTO(**data)


class GetDataPointEvaluationSchema(Schema):
    model_id = fields.Int(
        validate=lambda n: n > 0, required=True, error_messages={
            'required': 'Model id is required.',
            'invalid': 'Model id must be an integer > 0.'
        }
    )
    datapoint_id = fields.Int(
        validate=lambda n: n > 0, allow_none=True, error_messages={
            'invalid': 'Datapoint id must be an integer > 0.'
        }
    )
    coherence_score = fields.Int(
        validate=lambda n: 0 <= n <= 10, allow_none=True,
        error_messages={
            'invalid': 'Coherence score must be an integer between 0 and 10.',
        }
    )
    relevance_score = fields.Int(
        validate=lambda n: 0 <= n <= 10, allow_none=True,
        error_messages={
            'invalid': 'Relevance score must be an integer between 0 and 10.',
        }
    )
    semantic_similarity_score = fields.Float(
        allow_none=True,
        validate=lambda n: 0.0 <= n <= 100.0,
        error_messages={
            'invalid': 'Semantic similarity score must be a float.'
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('datapoint_id')
    def validate_datapoint_id(self, datapoint_id: int | None = None) -> None:
        if datapoint_id:
            try:
                self.data_manager.get_datapoint_by_id(
                    self.session, datapoint_id)[0]
            except:
                raise ValidationError(f"""No datapoint with the id {
                    datapoint_id} found.""")

    @validates('model_id')
    def validate_datapoint_id(self, model_id: int) -> None:
        try:
            model = self.data_manager.get_model_by_id(
                self.session, model_id)[0]
            print(model)
        except:
            raise ValidationError(f"""No model with the id {
                                  model_id} found.""")

    @post_load
    def make_create_training_run_dto(self, data, **kwargs):
        return GetDataPointEvaluationsDTO(**data)


class UpdateProjectSchema(BaseUpdateSchema):
    project_name = fields.Str(
        allow_none=True,
        validate=lambda n: len(n) <= 255 and len(n) > 0,
        error_messages={
            'invalid': 'Project name must be between 1 and 255 characters.'
        }
    )
    description = fields.Str(
        validate=lambda n: len(n) <= 4000,
        allow_none=True,
        error_messages={
            'invalid': 'Description must not exceed 4000 characters.'
        }
    )
    model_ids = fields.List(
        fields.Int(validate=lambda n: n > 0), allow_none=True,
        error_messages={
            'invalid': 'All model IDs must exist and be greater than 0.'
        }
    )
    dataset_ids = fields.List(
        fields.Int(validate=lambda n: n > 0), allow_none=True,
        error_messages={
            'invalid': 'All dataset IDs must exist and be greater than 0.'
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('model_ids')
    def validate_models(self, model_ids: list[int]):

        if model_ids:
            missing_models = []
            for model_id in model_ids:
                try:
                    self.data_manager.get_model_by_id(
                        self.session, model_id)[0]
                except NoResultFound:
                    missing_models.append(model_id)

            if missing_models:
                raise ValidationError(
                    f"Models with IDs {missing_models} do not exist.")

    @validates('dataset_ids')
    def validate_datasets(self, dataset_ids: list[int]):

        if dataset_ids:
            missing_datasets = []
            for dataset_id in dataset_ids:
                try:
                    self.data_manager.get_dataset_by_id(
                        self.session, dataset_id)[0]
                except NoResultFound:
                    missing_datasets.append(dataset_id)

            if missing_datasets:
                raise ValidationError(f"""Datasets with IDs {
                    missing_datasets} do not exist.""")

    @post_load
    def make_create_project_dto(self, data, **kwargs):
        return UpdateProjectDTO(**data)


class UpdateDatasetSchema(BaseUpdateSchema):
    dataset_name = fields.Str(
        allow_none=True,
        validate=lambda s: len(s) <= 255 and len(s) > 0,
        error_messages={
            'invalid': 'Dataset name must be between 1 and 255 characters.'
        }
    )
    project_ids = fields.List(
        fields.Int(validate=lambda n: n > 0),
        allow_none=True,
        error_messages={
            'invalid': 'Each project ID must exist and be greater than 0.'
        }
    )
    is_global = fields.Boolean(allow_none=True,
                               error_messages={
                                   'invalid': 'Is_global must be either True or False.'
                               }
                               )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('project_ids')
    def validate_projects(self, project_ids: list[int]):

        missing_projects = []
        for project_id in project_ids:
            try:
                self.data_manager.get_project_by_id(
                    self.session, project_id)[0]
            except NoResultFound:
                missing_projects.append(project_id)

        if missing_projects:
            raise ValidationError(f"""Projects with IDs {
                missing_projects} do not exist.""")

    @post_load
    def make_dataset_dto(self, data, **kwargs):
        return UpdateDatasetDTO(**data)


class UpdateDataPointSchema(BaseUpdateSchema):
    related_datapoint_ids = fields.List(
        fields.Integer(validate=lambda n: n > 0), allow_none=True, error_messages={
            'invalid': 'Related datapoint ids must be > 0',
        })

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('related_datapoint_ids')
    def validate_datapoints(self, datapoint_ids: list[int]):

        missing_datapoints = []
        for datapoint_id in datapoint_ids:
            try:
                self.data_manager.get_datapoint_by_id(
                    self.session, datapoint_id)[0]
            except NoResultFound:
                missing_datapoints.append(datapoint_id)

        if missing_datapoints:
            raise ValidationError(f"""Datapoints with IDs {
                missing_datapoints} do not exist.""")

    @post_load
    def make_create_datapoint_dto(self, data, **kwargs):
        return UpdateDataPointDTO(**data)


class UpdateModelSchema(BaseUpdateSchema):
    model_name = fields.Str(
        allow_none=True,
        validate=lambda s: len(s) <= 255 and len(s) > 0,
        error_messages={
            'invalid': 'Model name must be between 1 and 255 characters.'
        }
    )
    project_ids = fields.List(
        fields.Int(validate=lambda n: n > 0),
        allow_none=True,
        error_messages={
            'invalid': 'Each project ID must exist and be greater than 0.'
        }
    )
    augmentation_configurations = fields.List(fields.Dict(), allow_none=True)

    training_dataset_ids = fields.List(fields.Int(validate=lambda n: n > 0, error_messages={
        'invalid': 'All associated training dataset ids must be > 0.'
    }),
        allow_none=True,
        error_messages={
        'required': 'Training dataset list is required.',
        'invalid': 'Model must be associated to at least one training dataset.'
    }
    )
    is_global = fields.Boolean(allow_none=True,
                               error_messages={
                                   'invalid': 'Is_global must be either True or False.'
                               }
                               )
    semantic_similarity_model = fields.Str(allow_none=True, error_messages={
        'invalid': 'Semantic similarity model must be of type string.'
    })
    fine_tuning_job_id = fields.Str(allow_none=True, error_messages={
        'invalid': 'Model fine tuning job id must be of type string.'
    })
    fine_tuning_checkpoint_job_id = fields.Str(allow_none=True, validate=lambda n: len(n) > 0, error_messages={
        'invalid': 'Model checkpoint job id must be of type string.'
    })
    fine_tuned_model_id = fields.Str(allow_none=True, validate=lambda n: len(n) > 0, error_messages={
        'invalid': 'Full fine tuned model id must be of type string.'
    })

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @validates('project_ids')
    def validate_projects(self, project_ids: list[int]):
        missing_projects = []
        if project_ids:
            for project_id in project_ids:
                try:
                    self.data_manager.get_project_by_id(
                        self.session, project_id)[0]
                except NoResultFound:
                    missing_projects.append(project_id)

            if missing_projects:
                raise ValidationError(f"""Projects with IDs {
                    missing_projects} do not exist.""")

    @validates('training_dataset_ids')
    def validate_datasets_exist(self, dataset_ids: list[int]):
        missing_dataset_ids: list[int] = []
        if dataset_ids:
            try:
                for dataset_id in dataset_ids:
                    self.data_manager.get_dataset_by_id(
                        self.session, dataset_id)[0]
            except NoResultFound:
                missing_dataset_ids.append(dataset_id)

            raise ValidationError(f"""Datasets with ID {
                missing_dataset_ids} do not exist.""")

    @validates('semantic_similarity_model')
    def validate_semantic_similarity_model(self, semantic_similarity_model: str):
        if semantic_similarity_model:
            if not any(model["model_name"] == semantic_similarity_model for model in semantic_similarity_models):
                raise ValidationError(f"""Semantic similarity model "{
                    semantic_similarity_model}" does not exist.""")
            return semantic_similarity_model

    @validates_schema(pass_original=True)
    def validate_fine_tuning_job_id(self, data: dict[str, Any], original_data: dict[str, Any], **kwargs):
        model_id = data.get("id")
        if not model_id:
            raise ValidationError('Model ID is required.')

        model: Model = self.data_manager.get_model_by_id(
            self.session, model_id)[0]

        if model.fine_tuning_job_id and data.get("fine_tuning_job_id"):
            raise ValidationError(
                "This model already has an full fine tuned model id set and cannot be updated with a new one.")

    @post_load
    def make_create_model_dto(self, data, **kwargs):
        return UpdateModelDTO(**data)


class UpdateModelEvaluationSchema(BaseUpdateSchema):
    evaluation_type = CustomEnumValidationField(
        EvaluationType,
        by_value=True,
        allow_none=True,
        error_messages={
            'invalid': 'Invalid evaluation type. Must be one of: {0}.'.format(", ".join(e.name for e in EvaluationType))
        }
    )
    helpful_score = fields.Int(
        allow_none=True,
        validate=lambda n: 0 <= n <= 10,
        error_messages={
            'invalid': 'Helpful score must be an integer between 0 and 10.',
        }
    )
    honest_score = fields.Int(
        allow_none=True,
        validate=lambda n: 0 <= n <= 10,
        error_messages={
            'invalid': 'Honest score must be an integer between 0 and 10.',
        }
    )
    harmless_score = fields.Int(
        allow_none=True,
        validate=lambda n: 0 <= n <= 10,
        error_messages={
            'invalid': 'Harmless score must be an integer between 0 and 10.',
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @post_load
    def make_create_model_evaluation_dto(self, data, **kwargs):
        return UpdateModelEvaluationDTO(**data)


class UpdateTrainingRunSchema(BaseUpdateSchema):
    epochs = fields.Int(
        required=True, validate=lambda n: n >= 1 and n <= 10,
        error_messages={
            'required': 'Number of epochs is required.',
            'invalid': 'Number of epochs must be greater than 0 and smaller than 11.'
        }
    )
    learning_rate_multiplier = fields.Float(
        required=True, validate=lambda n: n >= 0.1 and n <= 10.0,
        error_messages={
            'required': 'Learning rate multiplier is required.',
            'invalid': 'Learning rate multiplier must be a positive float greater than 0.0 and smaller than 11.0.',
        }
    )
    batch_size = fields.Int(
        required=True, validate=lambda n: n >= 1 and n <= 32,
        error_messages={
            'required': 'Batch size is required.',
            'invalid': 'Batch size must be a positive integer greater 0 and smaller 33.',
        }
    )
    seed = fields.Int(
        allow_none=True, validate=lambda n: n >= 0,
        error_messages={
            'invalid': 'Seed must be an  integer greater or equals to 0.',
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @post_load
    def make_create_training_run_dto(self, data, **kwargs):
        return UpdateTrainingRunDTO(**data)


class UpdateDataPointEvaluationSchema(BaseUpdateSchema):

    coherence_score = fields.Int(
        validate=lambda n: 0 <= n <= 10, allow_none=True,
        error_messages={
            'invalid': 'Coherence score must be an integer between 0 and 10.',
        }
    )
    relevance_score = fields.Int(
        validate=lambda n: 0 <= n <= 10, allow_none=True,
        error_messages={
            'invalid': 'Relevance score must be an integer between 0 and 10.',
        }
    )
    semantic_similarity_score = fields.Float(
        allow_none=True,
        validate=lambda n: 0.0 <= n <= 100.0,
        error_messages={
            'invalid': 'Semantic similarity score must be a float.'
        }
    )

    def __init__(self, session: Session, data_manager: IDataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: Session = session
        self.data_manager: IDataManager = data_manager

    @post_load
    def make_create_training_run_dto(self, data, **kwargs):
        return UpdateDataPointEvaluationDTO(**data)
