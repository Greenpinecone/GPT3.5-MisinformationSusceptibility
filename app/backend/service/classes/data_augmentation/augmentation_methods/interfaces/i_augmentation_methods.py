from abc import ABC, abstractmethod
from app.backend.dtos.response import DataPointDTO


class IAugmentationMethod(ABC):

    @abstractmethod
    def augment_datapoints(datapoints: list[DataPointDTO], datapoint_indices: list[list[int]]) -> list[DataPointDTO]:
        pass
