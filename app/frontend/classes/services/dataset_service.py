"""
This module provides services for managing datasets and their datapoints.

Classes:
    DatasetService: Provides methods for creating and updating dataset objects, including their associated datapoints.
"""


from typing import Any
from app.frontend.classes.manager.toast_manager import ToastManager
from app.frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from app.frontend.classes.editors.dataset_editor import DatasetEditor
from app.frontend.mappers.frontend_mappers import ConvertDataPointDTOWithDataFrameWrapperToCreateDatapointDTO
from app.backend.dtos.response import DatasetDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.backend.dtos.create_request import CreateDatasetDTO, CreateDataPointDTO
from app.backend.database.schema import DatasetCategory, MessageKeys


class DatasetService:
    """
    Provides methods for creating and updating dataset objects, including their associated datapoints.

    This service offers various methods to handle operations such as processing and creating datasets, creating dataset DTOs, submitting datasets and their datapoints, updating dataset editors, and checking for datapoints within dataset editors.

    Methods:
        process_and_create_dataset: Process and create datasets based on dataset editors.
        create_dataset_dto: Create a dataset DTO from the dataset editor information.
        submit_all_datasets_and_datapoints: Submit all datasets and their associated datapoints.
        update_dataset_editor_if_changed: Update the dataset editor if its attribute has changed.
        check_if_dataset_editor_has_datapoints: Check if any dataset editor has datapoints.
        remove_empty_datapoints: Remove datapoints with empty messages DataFrame from the list.
    """

    @classmethod
    def process_and_create_dataset(cls, all_dataset_editors: list[DatasetEditor], is_global: bool, dataset_name: str, project_id: int, service: ServiceManagerFacade) -> list[DatasetDTO] | None:
        """
        Process and create datasets based on dataset editors.

        Args:
            all_dataset_editors (list[DatasetEditor]): List of dataset editors.
            is_global (bool): Indicates if the dataset is global.
            dataset_name (str): Name of the dataset.
            project_id (int): ID of the project.
            service (ServiceManagerFacade): Service manager to handle the creation.

        Returns:
            list[DatasetDTO] | None: List of created dataset DTOs or None if the process fails.
        """

        if not dataset_name:
            ToastManager.show_toast("Dataset name is required.", "info")
            return

        for dataset_editor in all_dataset_editors:
            # Remove all datapoints without rows
            cls.remove_empty_datapoints(
                dataset_editor.datapoints)

            if dataset_editor.dataset_category == DatasetCategory.training:
                if len(dataset_editor.datapoints) < 1:
                    ToastManager.show_toast(
                        "Dataset must contain at least 1 datapoint.", "info")
                    return

        all_dataset_dtos = []
        all_datapoint_dtos = []

        for dataset_editor in all_dataset_editors:

            datapoint_dtos = ConvertDataPointDTOWithDataFrameWrapperToCreateDatapointDTO(
                many=True).dump(dataset_editor.datapoints)
            dataset_dto = cls.create_dataset_dto(
                dataset_name, dataset_editor, project_id, is_global)

            all_dataset_dtos.append(dataset_dto)
            all_datapoint_dtos.append(datapoint_dtos)

        return cls.submit_all_datasets_and_datapoints(
            all_dataset_dtos, all_datapoint_dtos, service)

    @staticmethod
    def create_dataset_dto(dataset_name: str, dataset_editor: DatasetEditor, project_id: int, is_global: bool) -> CreateDatasetDTO:
        """
        Create a dataset DTO from the dataset editor information.

        Args:
            dataset_name (str): Name of the dataset.
            dataset_editor (DatasetEditor): Dataset editor containing dataset information.
            project_id (int): ID of the project.
            is_global (bool): Indicates if the dataset is global.

        Returns:
            CreateDatasetDTO: Created dataset DTO.
        """

        return CreateDatasetDTO(
            dataset_name=dataset_name,
            category=DatasetCategory(
                dataset_editor.dataset_category) if dataset_editor.dataset_category else None,
            augmented=False,
            fine_tuning_company=dataset_editor.chosen_company,
            fine_tuning_formatting=dataset_editor.chosen_file_format,
            fine_tuning_model=dataset_editor.chosen_model,
            project_ids=[project_id],
            is_global=is_global
        )

    @staticmethod
    def submit_all_datasets_and_datapoints(dataset_dtos: list[CreateDatasetDTO], datapoint_dtos: list[list[CreateDataPointDTO]], service: ServiceManagerFacade) -> DatasetDTO:
        """
        Submit all datasets and their associated datapoints.

        Args:
            dataset_dtos (list[CreateDatasetDTO]): List of dataset DTOs to submit.
            datapoint_dtos (list[list[CreateDataPointDTO]]): List of lists containing datapoint DTOs for each dataset.
            service (ServiceManagerFacade): Service manager to handle the submission.

        Returns:
            DatasetDTO: Created dataset DTO.
        """

        return service.create_dataset_with_datapoints(
            dataset_dtos[0], datapoint_dtos[0], dataset_dtos[1], datapoint_dtos[1])

    def update_dataset_editor_if_changed(attr: str, new_value: Any, all_dataset_editors: list[DatasetEditor]) -> bool:
        """
        Update the dataset editor if its attribute has changed.

        Args:
            attr (str): Attribute to check for changes.
            new_value (Any): New value of the attribute.
            all_dataset_editors (list[DatasetEditor]): List of dataset editors to update.

        Returns:
            bool: True if any dataset editor was updated, False otherwise.
        """

        changed = False
        for editor in all_dataset_editors:
            if getattr(editor, attr) != new_value:
                setattr(editor, attr, new_value)
                # Reset temp dialog dataset editor
                editor.temp_simple_datapoint_dto = None
                # Reset default role
                editor.default_role = MessageKeys[editor.chosen_company.value].value[
                    0][1] if editor.chosen_company else None
                changed = True
        return changed

    @staticmethod
    def check_if_dataset_editor_has_datapoints(all_dataset_editors: list[DatasetEditor]) -> bool:
        """
        Check if any dataset editor has datapoints.

        Args:
            all_dataset_editors (list[DatasetEditor]): List of dataset editors to check.

        Returns:
            bool: True if any dataset editor has datapoints, False otherwise.
        """

        return any(len(dataset_editor.datapoints) > 0 for dataset_editor in all_dataset_editors)

    @staticmethod
    def remove_empty_datapoints(datapoints: list[DataPointDTOWithDataFrameWrapper]) -> None:
        """Remove datapoint wrappers with empty messages DataFrame from the list.

        Args:
            datapoint_wrappers (list[DataPointDTOWithDataFrameWrapper]): List of datapoint wrappers.
        """
        # Iterate over the list in reverse order to safely remove items
        for i in reversed(range(len(datapoints))):
            if datapoints[i].messages.shape[0] == 0:
                del datapoints[i]
