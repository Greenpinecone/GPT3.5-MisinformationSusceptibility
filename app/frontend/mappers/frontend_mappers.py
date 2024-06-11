from marshmallow import Schema, fields, post_dump
from app.backend.dtos.create_request import CreateDataPointDTO
from app.backend.dtos.update_request import UpdateDataPointDTO
from app.frontend.classes.dataframe_editor import DataFrameEditor


# Takes a wrapper object and converts it to a datapoint dto
class ConvertDataPointDTOWithDataFrameWrapperToCreateDatapointDTO(Schema):
    messages = fields.Function(
        serialize=lambda obj: DataFrameEditor.convert_df_to_messages_container(obj.messages))
    dataset_id = fields.Function(
        serialize=lambda obj: obj.datapoint_dto.dataset_id if obj.datapoint_dto else None)
    related_datapoint_ids = fields.Function(
        serialize=lambda obj: obj.datapoint_dto.related_datapoint_ids if obj.datapoint_dto else None)
    augmentation_type = fields.Function(
        serialize=lambda obj: obj.datapoint_dto.augmentation_type if obj.datapoint_dto else None)
    initial_datapoint_id = fields.Function(
        serialize=lambda obj: obj.datapoint_dto.initial_datapoint_id if obj.datapoint_dto else None)

    @post_dump
    def make_create_datapoint_dto(self, data, **kwargs):
        return CreateDataPointDTO(**data)


class DataPointDTOToUpdateDataPointDTO(Schema):
    id = fields.Function(serialize=lambda obj: obj.id)
    related_datapoint_ids = fields.Function(
        serialize=lambda obj: [datapoint.id for datapoint in obj.related_datapoints])

    @post_dump
    def make_update_datapoint_dto(self, data, **kwargs):
        return UpdateDataPointDTO(**data)
