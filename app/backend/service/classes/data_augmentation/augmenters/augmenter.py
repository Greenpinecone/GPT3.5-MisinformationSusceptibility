"""
This module provides functions for augmenting textual data using various techniques
such as Back-Translation and Easy Data Augmentation (EDA).

Classes:
    DataAugmenter: Handles data augmentation.
"""


from app.backend.custom_types.typedicts import AugmentationConfiguration
from app.backend.dtos.create_request import CreateDataPointDTO
from app.backend.dtos.response import DataPointDTO
from app.backend.service.classes.data_augmentation.augmentation_methods.back_translation import GoogleBackTranslation
from app.backend.service.classes.data_augmentation.augmentation_methods.interfaces.i_augmentation_methods import IAugmentationMethod
from app.backend.util.config import DATA_AUGMENTATION_METHODS as augmentation_methods
from app.backend.service.classes.data_augmentation.augmentation_methods.eda.eda_easy_data_augmentation import EDA
from app.backend.service.classes.data_preprocessing.sampler import DataSampler


class DataAugmenter:
    """
    Handles the augmentation of textual data using techniques like Back-Translation
    and Easy Data Augmentation (EDA).
    """

    def __init__(self):
        pass

    @classmethod
    def select_augmentation_class(cls, augmentation_method: str):
        """
        Selects and returns the appropriate augmentation class based on the given augmentation method.

        Args:
            augmentation_method (str): The augmentation method to use (e.g., "google_translate", "EDA_Easy_Data_Augmentation").

        Returns:
            IAugmentationMethod: An instance of the selected augmentation class.
        """

        if augmentation_method == augmentation_methods["google_translate"]:
            return GoogleBackTranslation()

        if augmentation_method == augmentation_methods["EDA_Easy_Data_Augmentation"]:
            return EDA()

    @classmethod
    def create_augmented_datapoints(cls, datapoints: list[DataPointDTO], augmentation_configurations: list[AugmentationConfiguration]) -> list[CreateDataPointDTO]:
        """
        Creates augmented datapoints based on the provided augmentation configurations.

        Args:
            datapoints (list[DataPointDTO]): The original datapoints to augment.
            augmentation_configurations (list[AugmentationConfiguration]): The configurations for augmentation, including the method and parameters.

        Returns:
            list[CreateDataPointDTO]: The list of augmented datapoints.
        """

        augmenter: IAugmentationMethod = None
        augmented_datapoints: list[DataPointDTO] = []

        for configuration in augmentation_configurations:

            # Choose the correct augmentation method
            augmenter = cls.select_augmentation_class(
                configuration["selected_method"])

            augmentation_indices: list[int] = DataSampler.sample_datapoints(
                datapoints, configuration["augmentation_percentage"])

            # Add augmented datapoints to list of all augmented datapoints
            augmented_datapoints.extend(
                augmenter.augment_datapoints(datapoints, augmentation_indices, configuration["augmentation_config"]))

        return augmented_datapoints
