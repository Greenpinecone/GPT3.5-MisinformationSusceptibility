"""
This module defines the interface for data augmentation methods.
It includes the fundamental implementation that all augmentation classes should follow.
"""


from abc import ABC, abstractmethod
from app.backend.dtos.response import DataPointDTO


class IAugmentationMethod(ABC):
    """
    An abstract base class that defines the interface for data augmentation methods.
    All augmentation classes should inherit from this class and implement its methods.

    Methods:
        augment_datapoints(datapoints: list[DataPointDTO], datapoint_indices: list[list[int]]) -> list[DataPointDTO]:
            Abstract method to augment datapoints.
    """

    @abstractmethod
    def augment_datapoints(datapoints: list[DataPointDTO], datapoint_indices: list[list[int]]) -> list[DataPointDTO]:
        """
        Abstract method to augment datapoints. This method must be implemented by subclasses.

        Args:
            datapoints (list[DataPointDTO]): The list of original datapoints to augment.
            datapoint_indices (list[list[int]]): The indices of the datapoints to augment.

        Returns:
            list[DataPointDTO]: The list of augmented datapoints.
        """
        pass
