"""
This module contains the DataSampler class, which is used for sampling a 
specified percentage of data from datasets. It offers functionality for random 
sampling, crucial for performing quality checks and evaluations in data 
processing and analysis tasks.

Classes:
    DataSampler: Handles the random sampling of data sets.
"""


import random
from app.backend.dtos.response import DataPointDTO


class DataSampler:
    """Handles the sampling of data sets.

    This class is responsible for sampling a specified percentage of data from
    the datasets. It provides methods to perform random sampling which can be used
    for quality checks and evaluation purposes.
    """

    @classmethod
    def get_augmentation_count(cls, datapoints: list[DataPointDTO] | int, percentage: float) -> int:
        """Calculates the total count of datapoints and the number of datapoints to be augmented.

        Args:
            datapoints (list[DataPointDTO] | int): The original datapoints or the count of datapoints.
            percentage (float): The percentage of datapoints to augment.

        Returns:
            tuple: A tuple containing the augmentation count and the total datapoints count.
        """

        if isinstance(datapoints, int):
            total_datapoints = datapoints
        else:
            total_datapoints = len(datapoints)

        augmentation_count = int((percentage / 100) * total_datapoints)

        return augmentation_count, total_datapoints

    @classmethod
    def get_augmentation_distribution(cls, datapoints: list[DataPointDTO], percentage: float) -> list[int]:
        """Generates a list of indices for datapoints to be augmented based on the given percentage.

        Args:
            datapoints (list[DataPointDTO]): The original list of datapoints.
            percentage (float): The percentage of datapoints to augment.

        Returns:
            list[int]: A list of indices corresponding to the datapoints to be augmented.
        """

        augmentation_distribution: list[int] = []

        augmentation_count, total_datapoints = cls.get_augmentation_count(
            datapoints, percentage)

        # Random shuffle datapoints to ensure even distribution of datapoints
        indices = list(range(total_datapoints))
        random.shuffle(indices)

        current_index = 0
        for _ in range(augmentation_count):
            # Using round robin approach
            augmentation_distribution.append(indices[current_index])
            current_index = (current_index + 1) % total_datapoints

        # Convert defaultdict to list of lists
        return augmentation_distribution

    @classmethod
    def sample_datapoints(cls, datapoints: list[str], percentage: float) -> list[list[int]]:
        """Samples datapoints based on the given percentage.

        Args:
            datapoints (list[str]): The original list of datapoints.
            percentage (float): The percentage of datapoints to sample.

        Returns:
            list[list[int]]: A list of indices for the sampled datapoints.
        """

        return cls.get_augmentation_distribution(datapoints, percentage)
