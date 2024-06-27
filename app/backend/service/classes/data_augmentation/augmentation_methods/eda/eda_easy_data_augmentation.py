

from app.backend.custom_types.typedicts import EDAParams
from app.backend.dtos.create_request import CreateDataPointDTO
from app.backend.dtos.response import DataPointDTO
from app.backend.service.classes.data_augmentation.augmentation_methods.interfaces.i_augmentation_methods import IAugmentationMethod
from app.backend.service.classes.data_augmentation.augmentation_methods.eda.eda_algorithm_code.code.augment import gen_eda
from app.backend.database.schema import AugmentationType
import copy


class EDA(IAugmentationMethod):

    def __init__(self):
        pass

    @classmethod
    def augment_datapoints(cls, datapoints: list[DataPointDTO], datapoint_indices: list[int], configuration: EDAParams) -> list[CreateDataPointDTO]:
        augmented_datapoints: list[CreateDataPointDTO] = []

        for idx in datapoint_indices:
            original_dp = datapoints[idx]

            # Deep copy the messages to avoid mutating the original
            copied_messages = copy.deepcopy(original_dp.messages)

            # Create a new CreateDataPointDTO
            new_dp = CreateDataPointDTO(
                messages=copied_messages,
                dataset_id=None,
                related_datapoint_ids=None,
                augmentation_type=AugmentationType.EDA,
                initial_datapoint_id=original_dp.id
            )

            # Extract and augment messages
            for message in new_dp.messages['messages']:
                content = message['content']
                augmented_content = gen_eda(
                    content, **configuration, num_aug=1)
                message['content'] = augmented_content

            augmented_datapoints.append(new_dp)

        return augmented_datapoints
