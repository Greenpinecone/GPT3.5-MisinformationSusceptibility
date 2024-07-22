""" 
A module containg DTOs explicitly created for frontend usage.
"""


import uuid
import pandas as pd
from dataclasses import dataclass
from app.backend.dtos.response import DataPointDTO


@dataclass
class DataPointDTOWithDataFrameWrapper:
    """
    A class to wrap DataPointDTO with additional information for editing in a DataFrame.

    Attributes:
        datapoint_id (UUID): The unique identifier for the datapoint.
        data_editor_key (str): The key used to identify the data editor instance.
        datapoint_number (Optional[int]): The number or index of the datapoint.
        messages (Optional[pd.DataFrame]): The messages associated with the datapoint, stored in a DataFrame.
        datapoint_dto (Optional[DataPointDTO]): The Data Transfer Object (DTO) representing the datapoint.
    """

    datapoint_id: uuid
    data_editor_key: str
    datapoint_number: int | None
    messages: pd.DataFrame | None = None
    datapoint_dto: DataPointDTO | None = None
