from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, post_load, post_dump
from app.backend.database.schema import Project, DataPoint, Dataset, Model, TrainingRun, DataPointEvaluation, ModelEvaluation, CurrentProjectData
from app.backend.dtos.response import *
import zoneinfo


# Returns the enum object in case of serialization.
class CustomEnumConversionSchema(fields.Enum):
    def __init__(self, enum, *args, **kwargs):
        super().__init__(enum, *args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value


class FlexibleDateTimeField(fields.DateTime):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        # Ensure the datetime object is timezone-aware
        # SQLite stores utc / iso strings and converts timezone aware datetime obbjects to utc
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            value = value.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        # Change to your specific timezone
        local_dt = value.astimezone()
        return local_dt


class BaseSchema(SQLAlchemyAutoSchema):
    def __init__(self, session, *args, **kwargs):
        # Dynamically creates a Meta class with the session for each created object to avoid setting the session as class attribute and causing issues with session sharing
        # Check if a session exists. Do not overwrite in case of Nested Schemas
        if session:
            class Meta:
                datetimeformat = 'iso'
                sqla_session = session
                load_instance = True

            self.Meta = Meta
        super().__init__(*args, **kwargs)


class ProjectSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    project_name = auto_field()
    description = auto_field()
    created_at = FlexibleDateTimeField()
    model_ids = fields.Function(
        serialize=lambda obj: [model.id for model in obj.models])
    dataset_ids = fields.Function(
        serialize=lambda obj: [dataset.id for dataset in obj.datasets])

    class Meta(BaseSchema.Meta):
        model = Project

    @post_dump
    def make_project_dto(self, data, **kwargs):
        return ProjectDTO(**data)


class DatasetSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    dataset_name = auto_field()
    augmented = auto_field()
    category = CustomEnumConversionSchema(DatasetCategory)
    created_at = FlexibleDateTimeField()
    initial_dataset_id = auto_field()
    test_dataset_id = auto_field()
    fine_tuning_company = auto_field()
    fine_tuning_model = auto_field()
    fine_tuning_formatting = auto_field()
    is_global = auto_field()
    model_ids = fields.Function(
        serialize=lambda obj: [model.id for model in obj.models])
    project_ids = fields.Function(
        serialize=lambda obj: [project.id for project in obj.projects])
    datapoint_ids = fields.Function(
        serialize=lambda obj: [datapoint.id for datapoint in obj.datapoints])

    class Meta(BaseSchema.Meta):
        model = Dataset

    @post_dump
    def make_dataset_dto(self, data, **kwargs):
        return DatasetDTO(**data)


class ComplexDatasetSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    dataset_name = auto_field()
    augmented = auto_field()
    category = CustomEnumConversionSchema(DatasetCategory)
    created_at = FlexibleDateTimeField()
    initial_dataset_id = auto_field()
    fine_tuning_company = auto_field()
    fine_tuning_model = auto_field()
    fine_tuning_formatting = auto_field()
    is_global = auto_field()
    model_ids = fields.Function(
        serialize=lambda obj: [model.id for model in obj.models])
    project_ids = fields.Function(
        serialize=lambda obj: [project.id for project in obj.projects])
    datapoints = fields.Nested(lambda: DataPointSchema(many=True), default=[])
    test_dataset = fields.Nested(
        lambda: ComplexDatasetSchema(), exclude=('test_dataset',), default=None)

    class Meta:
        model = Dataset

    @post_dump
    def make_complex_dataset_dto(self, data, **kwargs):
        return ComplexDatasetDTO(**data)


class DataPointSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    dataset_id = auto_field()
    augmentation_type = CustomEnumConversionSchema(AugmentationType)
    created_at = FlexibleDateTimeField()
    messages = auto_field()
    initial_datapoint_id = auto_field()

    # Use a lambda to defer self-referencing
    related_datapoints = fields.Nested(lambda: DataPointSchema(
        many=True), exclude=('related_datapoints',), default=[])

    class Meta(BaseSchema.Meta):
        model = DataPoint

    @post_dump
    def make_data_point_dto(self, data, **kwargs):
        # When "related_datapoints" is excluded in nested fields.
        if not data.get("related_datapoints"):
            data["related_datapoints"] = []
        return DataPointDTO(**data)


# Unlike the other datapoint schema, this schema does not get the directly related_datapoints as they have been set for test_datapoints, it gets the test datapoints related to a training datapoin instead.
class TrainingDataPointSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    dataset_id = auto_field()
    augmentation_type = CustomEnumConversionSchema(AugmentationType)
    created_at = FlexibleDateTimeField()
    messages = auto_field()
    initial_datapoint_id = auto_field()

    # Use a lambda to defer self-referencing
    related_datapoints = fields.Nested(lambda: TrainingDataPointSchema(
        many=True), exclude=('related_datapoints',), attribute='related_by', default=[])

    class Meta:
        model = DataPoint

    @post_dump
    def make_data_point_dto(self, data, **kwargs):
        # When "related_datapoints" is excluded in nested fields.
        if not data.get("related_datapoints"):
            data["related_datapoints"] = []
        return DataPointDTO(**data)


class ModelSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    model_name = auto_field()
    parent_model_id = auto_field()
    version = auto_field()
    created_at = FlexibleDateTimeField()
    is_global = auto_field()
    uuid = auto_field()
    fine_tuning_checkpoint_job_id = auto_field()
    fine_tuned_model_id = auto_field()
    is_checkpoint_model = auto_field()
    checkpoint_step = auto_field()
    project_ids = fields.Function(
        serialize=lambda obj: [project.id for project in obj.projects])
    fine_tuning_job_id = auto_field()
    training_dataset_ids = fields.Function(
        serialize=lambda obj: [dataset.id for dataset in obj.training_datasets])
    training_run_id = fields.Function(
        serialize=lambda obj: obj.training_run.id if obj.training_run else None)

    class Meta(BaseSchema.Meta):
        model = Model

    @post_dump
    def make_model_dto(self, data, **kwargs):
        return ModelDTO(**data)


class ModelEvaluationSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    model_id = auto_field()
    datapoint_id = auto_field()
    evaluation_type = CustomEnumConversionSchema(EvaluationType)
    helpful_score = auto_field()
    honest_score = auto_field()
    harmless_score = auto_field()
    created_at = FlexibleDateTimeField()

    class Meta(BaseSchema.Meta):
        model = ModelEvaluation

    @post_dump
    def make_model_evaluation_dto(self, data, **kwargs):
        return ModelEvaluationDTO(**data)


class TrainingRunSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    model_id = auto_field()
    epochs = auto_field()
    learning_rate_multiplier = auto_field()
    fine_tuning_model = auto_field()
    batch_size = auto_field()
    seed = auto_field()
    created_at = FlexibleDateTimeField()

    class Meta(BaseSchema.Meta):
        model = TrainingRun

    @post_dump
    def make_training_run_dto(self, data, **kwargs):
        return TrainingRunDTO(**data)


class SimpleTrainingRunDTOSchema(SQLAlchemyAutoSchema):
    id = fields.Int()
    model_name = fields.Str()
    model_version = fields.Str()
    fine_tuning_model = fields.Str()
    seed = fields.Int()


class SimpleTrainingRunSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    model_name = fields.Function(serialize=lambda obj: obj.model.model_name)
    model_version = fields.Function(serialize=lambda obj: obj.model.version)
    fine_tuning_model = auto_field()
    seed = auto_field()

    class Meta(BaseSchema.Meta):
        model = TrainingRun

    @post_dump
    def make_training_run_dto(self, data, **kwargs):
        # Use the SimpleTrainingRunDTOSchema to filter and create the DTO
        dto_schema = SimpleTrainingRunDTOSchema()
        filtered_data = dto_schema.dump(data)
        return SimpleTrainingRunDTO(**filtered_data)


class ComplexModelSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    model_name = auto_field()
    version = auto_field()
    created_at = FlexibleDateTimeField()
    is_global = auto_field()
    is_checkpoint_model = auto_field()
    checkpoint_step = auto_field()
    uuid = auto_field()
    fine_tuning_checkpoint_job_id = auto_field()
    fine_tuned_model_id = auto_field()
    project_ids = fields.Function(
        serialize=lambda obj: [project.id for project in obj.projects])
    fine_tuning_job_id = auto_field()
    training_dataset_ids = fields.Function(
        serialize=lambda obj: [dataset.id for dataset in obj.training_datasets])
    parent_model = fields.Nested(
        lambda: ComplexModelSchema(), exclude=('parent_model',), default=None)
    training_run = fields.Nested(lambda: TrainingRunSchema(), default=None)

    class Meta(BaseSchema.Meta):
        model = Model

    @post_dump
    def make_model_dto(self, data, **kwargs):
        return ComplexModelDTO(**data)


class CurrentProjectDataSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    id = auto_field()
    created_at = FlexibleDateTimeField()
    augmentation_configurations = auto_field()
    semantic_similarity_model = auto_field()
    unfinished_progress = auto_field()
    current_page = auto_field()
    save_checkpoint_models = auto_field()
    fine_tuning_step_counter = auto_field()
    current_project = fields.Nested(lambda: ProjectSchema(), default=None)
    current_fine_tuning_model = fields.Nested(
        lambda: ModelSchema(), default=None)
    selected_model_for_fine_tuning = fields.Nested(
        lambda: ComplexModelSchema(), default=None)
    currently_modified_dataset = fields.Nested(
        lambda: ComplexDatasetSchema(), default=None)

    class Meta(BaseSchema.Meta):
        model = CurrentProjectData

    @post_dump
    def make_training_run_dto(self, data, **kwargs):
        return CurrentProjectDataDTO(**data)


class DataPointEvaluationSchema(BaseSchema):
    def __init__(self, session=None, *args, **kwargs):
        super().__init__(session, *args, **kwargs)

    datapoint_id = auto_field()
    model_id = auto_field()
    coherence_score = auto_field()
    relevance_score = auto_field()
    semantic_similarity_score = auto_field()

    class Meta(BaseSchema.Meta):
        model = DataPointEvaluation

    @post_dump
    def make_training_run_dto(self, data, **kwargs):
        return DataPointEvaluationDTO(**data)
