import uuid
import pandas as pd
from dataclasses import dataclass
from app.backend.dtos.response import DataPointDTO


@dataclass
class DataPointDTOWithDataFrameWrapper:
    datapoint_id: uuid
    data_editor_key: str
    datapoint_number: int | None
    messages: pd.DataFrame | None = None
    datapoint_dto: DataPointDTO | None = None
