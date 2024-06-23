"""
This module provides functions for augmenting textual data using various techniques
such as Back-Translation and Easy Data Augmentation (EDA).

Classes:
    DataAugmenter: Handles data augmentation.
"""


from app.backend.dtos.response import DataPointDTO
from app.backend.service.classes.data_augmentation.augmentation_methods.interfaces.i_augmentation_methods import IAugmentationMethod
from app.backend.util.config import DATA_AUGMENTATION_METHODS as augmentation_methods
from app.backend.service.classes.data_augmentation.augmentation_methods.eda_easy_data_augmentation import EDA
from backend.service.classes.data_preprocessing.sampler import DataSampler


class DataAugmenter:
    """
    Handles the augmentation of textual data using techniques like Back-Translation
    and Easy Data Augmentation (EDA).
    """

    def __init__(self):
        pass

    @classmethod
    def select_augmentation_class(cls, augmentation_method: str):
        if augmentation_method == augmentation_methods["google_translate"]:
            pass  # TODO: implement google translate augmenter
            raise Exception(
                "Google Translate Augmenation is not yet implemented.")

        if augmentation_method == augmentation_methods["EDA_Easy_Data_Augmentation"]:
            return EDA()

    @classmethod
    def create_augmented_dataset(cls, augmentation_methods: list[str], augmentation_percentages: list[float], datapoints: list[DataPointDTO]) -> None:

        augmenter: IAugmentationMethod = None
        augmented_datapoints: list[DataPointDTO] = []

        augmentation_indices_per_percentage: list[int] = DataSampler.sample_datapoints(
            datapoints, augmentation_percentages)

        for aug_method, datapoint_indices in zip(augmentation_methods, augmentation_indices_per_percentage):

            # Choose the correct augmentation method
            augmenter = cls.select_augmentation_class(aug_method)

            # Add augmented datapoints to list of all augmented datapoints
            augmented_datapoints.append(
                augmenter.augment_datapoints(datapoints, datapoint_indices))

        return augmented_datapoints
