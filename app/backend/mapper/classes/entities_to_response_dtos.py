from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, validate, post_load
from ...database.schema import *
from ...dtos.response import *

# Directly handles enum convertion to value (e.g. String) for simple type usage and convertion from simple type to python enum when deserialized into database entity.


class DatasetCategoryEnumField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        return DatasetCategory(value)


class EvaluationTypeEnumField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        return EvaluationType(value)


class AugmentationTypeEnumField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        return AugmentationType(value)


class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        sqla_session = None
        load_instance = True


class ProjectSchema(BaseSchema):
    id = auto_field()
    project_name = auto_field()
    description = auto_field()
    created_at = fields.DateTime()
    models = Nested('ModelSchema', many=True, only=["id"], allow_none=True)
    datasets = Nested('DatasetSchema', many=True, only=["id"], allow_none=True)

    class Meta(BaseSchema.Meta):
        model = Project

    @post_load
    def make_project_dto(self, data, **kwargs):
        return ProjectDTO(**data)


class DatasetSchema(BaseSchema):
    id = auto_field()
    dataset_name = auto_field()
    augmented = auto_field()
    category = DatasetCategoryEnumField()
    created_at = fields.DateTime()
    initial_dataset_id = auto_field()
    test_dataset_id = auto_field()
    projects = Nested(ProjectSchema, many=True, only=["id"])
    initial_dataset = Nested('self', many=False, only=["id"], allow_none=True)
    test_dataset = Nested('self', many=False, only=["id"], allow_none=True)
    datapoints = Nested('DataPointSchema', many=True, only=["id"])

    class Meta(BaseSchema.Meta):
        model = Dataset

    @post_load
    def make_dataset_dto(self, data, **kwargs):
        return DatasetDTO(**data)


class DataPointSchema(BaseSchema):
    id = auto_field()
    dataset_id = auto_field()
    coherence_score = auto_field(
        validate=validate.Range(min=1, max=10), allow_none=True)
    relevance_score = auto_field(
        validate=validate.Range(min=1, max=10), allow_none=True)
    semantic_similarity_score = auto_field(allow_none=True)
    augmentation_type = AugmentationTypeEnumField()
    created_at = fields.DateTime()
    messages = auto_field()
    category = auto_field()
    initial_datapoint_id = Nested(
        'self', only=["id"], many=False, allow_none=True)

    class Meta(BaseSchema.Meta):
        model = DataPoint

    @post_load
    def make_data_point_dto(self, data, **kwargs):
        return DataPointDTO(**data)


class ModelSchema(BaseSchema):
    id = auto_field()
    model_name = auto_field()
    parent_model_id = Nested(
        'self', only=["id"], many=False, allow_none=True)
    version = auto_field()
    created_at = fields.DateTime()
    project_id = auto_field()
    datasets = Nested(DatasetSchema, many=True, only=["id"])
    training_run = Nested('TrainingRunSchema', only=[
                          "id"], many=False, allow_none=True)

    class Meta(BaseSchema.Meta):
        model = Model

    @post_load
    def make_model_dto(self, data, **kwargs):
        return ModelDTO(**data)


class ModelEvaluationSchema(BaseSchema):
    id = auto_field()
    model_id = auto_field()
    datapoint_id = auto_field()
    evaluation_type = EvaluationTypeEnumField()
    helpful_score = auto_field(validate=validate.Range(min=1, max=10))
    honest_score = auto_field(validate=validate.Range(min=1, max=10))
    harmless_score = auto_field(validate=validate.Range(min=1, max=10))
    created_at = fields.DateTime()
    datapoint = Nested(DataPointSchema, only=["id"])

    class Meta(BaseSchema.Meta):
        model = ModelEvaluation

    @post_load
    def make_model_evaluation_dto(self, data, **kwargs):
        return ModelEvaluationDTO(**data)


class TrainingRunSchema(BaseSchema):
    id = auto_field()
    model_id = auto_field()
    epochs = auto_field()
    learning_rate_multiplier = auto_field()
    batch_size = auto_field()
    created_at = fields.DateTime()

    class Meta(BaseSchema.Meta):
        model = TrainingRun

    @post_load
    def make_training_run_dto(self, data, **kwargs):
        return TrainingRunDTO(**data)
