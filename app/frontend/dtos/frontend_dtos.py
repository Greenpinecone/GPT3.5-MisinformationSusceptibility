from dataclasses import dataclass
import uuid
import pandas as pd
from backend.dtos.response import *


@dataclass
class DataPointDTOWithDataFrameWrapper:
    datapoint_id: uuid
    data_editor_key: str
    datapoint_number: int | None
    messages: pd.DataFrame | None = None
    datapoint_dto: DataPointDTO | None = None
