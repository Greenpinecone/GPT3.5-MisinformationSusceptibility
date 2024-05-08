from dataclasses import dataclass, field


@dataclass
class DatasetDataPointMapping:
    dataset_id: int
    datapoint_ids: list[int] = field(
        default_factory=list)


@dataclass
class LinkedData:
    linked_data: list[DatasetDataPointMapping] = field(
        default_factory=list)
