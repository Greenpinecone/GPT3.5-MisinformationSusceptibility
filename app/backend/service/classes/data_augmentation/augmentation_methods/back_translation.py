

from app.backend.dtos.response import DataPointDTO
from app.backend.service.classes.data_augmentation.augmentation_methods.interfaces.i_augmentation_methods import IAugmentationMethod


class GoogleBackTransaltion(IAugmentationMethod):

    def __init__():
        pass

    def augment_datapoints(datapoints: list[DataPointDTO], datapoint_indices: list[list[int]]) -> list[DataPointDTO]:
        pass
