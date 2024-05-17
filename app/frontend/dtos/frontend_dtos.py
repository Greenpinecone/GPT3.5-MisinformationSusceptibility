from dataclasses import dataclass
import pandas as pd
from backend.dtos.response import *


@dataclass
class DataPointDTOWithDataFrameWrapper:
    datapoint_number: int | str
    data_editor_key: str
    messages: pd.DataFrame | None = None
    datapoint_dto: DataPointDTO | None = None
