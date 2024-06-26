"""
This module contains the DataSampler class, which is used for sampling a 
specified percentage of data from datasets. It offers functionality for random 
sampling, crucial for performing quality checks and evaluations in data 
processing and analysis tasks.

Classes:
    DataSampler: Handles the random sampling of data sets.
"""


from collections import defaultdict
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
        """ Returns the total count of datapoints provided and datapoints that will be augmented from this original datapoints list."""
        if isinstance(datapoints, int):
            total_datapoints = datapoints
        else:
            total_datapoints = len(datapoints)

        augmentation_count = int((percentage / 100) * total_datapoints)

        return augmentation_count, total_datapoints

    @classmethod
    def get_augmentation_distribution(cls, datapoints: list[DataPointDTO], percentage: float) -> list[int]:
        """ Returns a list of lists, were each list consists of indices, correpsonding to datapoints in the passed datapoints list. The amount of indices correlates to the percentages given, so that the result can be used to augment the correct datapoints and correct amount of datapoints for each percentage."""
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
        return cls.get_augmentation_distribution(datapoints, percentage)
