from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, post_load, post_dump
from ...database.schema import *
from ...dtos.response import *


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
        # Directly return the datetime object without converting it to string
        return value


class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        sqla_session = None
        # äload_instance = True
        datetimeformat = 'iso'


class ProjectSchema(BaseSchema):
    id = auto_field()
    project_name = auto_field()
    description = auto_field()
    created_at = FlexibleDateTimeField()
    model_ids = fields.Function(
        serialize=lambda obj: [model.id for model in obj.models] if obj.models else None)
    dataset_ids = fields.Function(
        serialize=lambda obj: [dataset.id for dataset in obj.datasets] if obj.datasets else None)

    class Meta(BaseSchema.Meta):
        model = Project

    @post_dump
    def make_project_dto(self, data, **kwargs):
        print(data)
        return ProjectDTO(**data)


class DatasetSchema(BaseSchema):
    id = auto_field()
    dataset_name = auto_field()
    augmented = auto_field()
    category = CustomEnumConversionSchema(DatasetCategory)
    created_at = FlexibleDateTimeField()
    initial_dataset_id = auto_field()
    test_dataset_id = auto_field()
    project_ids = fields.Function(
        serialize=lambda obj: [project.id for project in obj.projects] if obj.projects else None)
    datapoint_ids = fields.Function(
        serialize=lambda obj: [datapoint.id for datapoint in obj.datapoints] if obj.datapoints else None)

    class Meta(BaseSchema.Meta):
        model = Dataset

    @post_dump
    def make_dataset_dto(self, data, **kwargs):
        return DatasetDTO(**data)


class DataPointSchema(BaseSchema):
    id = auto_field()
    dataset_id = auto_field()
    coherence_score = auto_field()
    relevance_score = auto_field()
    semantic_similarity_score = auto_field()
    augmentation_type = CustomEnumConversionSchema(AugmentationType)
    created_at = FlexibleDateTimeField()
    messages = auto_field()
    category = auto_field()
    initial_datapoint_id = auto_field()

    class Meta(BaseSchema.Meta):
        model = DataPoint

    @post_dump
    def make_data_point_dto(self, data, **kwargs):
        return DataPointDTO(**data)


class ModelSchema(BaseSchema):
    id = auto_field()
    model_name = auto_field()
    parent_model_id = auto_field()
    # Nested(
    #   lambda: ModelSchema(only=["id"]), many=False, allow_none=True)
    version = auto_field()
    created_at = FlexibleDateTimeField()
    project_id = auto_field()
    dataset_ids = fields.Function(
        serialize=lambda obj: [dataset.id for dataset in obj.datasets])
    training_run_id = fields.Function(
        serialize=lambda obj: obj.training_run.id if obj.training_run else None)

    class Meta(BaseSchema.Meta):
        model = Model

    @post_dump
    def make_model_dto(self, data, **kwargs):
        return ModelDTO(**data)


class ModelEvaluationSchema(BaseSchema):
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
    id = auto_field()
    model_id = auto_field()
    epochs = auto_field()
    learning_rate_multiplier = auto_field()
    batch_size = auto_field()
    created_at = FlexibleDateTimeField()

    class Meta(BaseSchema.Meta):
        model = TrainingRun

    @post_dump
    def make_training_run_dto(self, data, **kwargs):
        return TrainingRunDTO(**data)
