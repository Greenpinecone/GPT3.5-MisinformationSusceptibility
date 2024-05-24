from typing import Any
import streamlit as st
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from frontend.classes.dataset_editor import DatasetEditor
from backend.dtos.create_request import CreateDatasetDTO, CreateDataPointDTO
from frontend.mappers.frontend_mappers import ConvertDataPointDTOWithDataFrameWrapperToCreateDatapointDTO
from backend.database.schema import DatasetCategory, MessageKeys
from backend.util import utility_functions as uf


class DatasetService:
    @staticmethod
    def process_and_create_dataset(all_dataset_editors: list[DatasetEditor], is_global: bool, dataset_name: str, project_id: int, service: ServiceManagerFacade) -> None:
        if not dataset_name:
            uf.show_toast("Dataset name is required.", "info")
            return

        all_dataset_dtos = []
        all_datapoint_dtos = []

        for dataset_editor in all_dataset_editors:
            # Remove all datapoints without rows
            DatasetService.remove_empty_datapoints(
                dataset_editor.datapoints)
            # Update categories column if not a training dataset, since the user could have submitted before reloading the test datset after changes in the training dataset.
            if dataset_editor.dataset_category == DatasetCategory.test:
                DatasetService.update_test_dataset_categories(
                    dataset_editor)

            datapoint_dtos = ConvertDataPointDTOWithDataFrameWrapperToCreateDatapointDTO(
                many=True).dump(dataset_editor.datapoints)
            dataset_dto = DatasetService.create_dataset_dto(
                dataset_name, dataset_editor, project_id, is_global)

            all_dataset_dtos.append(dataset_dto)
            all_datapoint_dtos.append(datapoint_dtos)

        DatasetService.submit_all_datasets_and_datapoints(
            all_dataset_dtos, all_datapoint_dtos, service)

    @staticmethod
    def create_dataset_dto(dataset_name: str, dataset_editor: DatasetEditor, project_id: int, is_global: bool) -> CreateDatasetDTO:
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
    def submit_all_datasets_and_datapoints(dataset_dtos: list[CreateDatasetDTO], datapoint_dtos: list[list[CreateDataPointDTO]], service: ServiceManagerFacade):
        service.create_dataset_with_datapoints(
            dataset_dtos[0], datapoint_dtos[0], dataset_dtos[1], datapoint_dtos[1])
        uf.show_toast("Dataset has been successfully created.", "success")

    @staticmethod
    def update_test_dataset_categories(dataset_editor: DatasetEditor):
        for datapoint in dataset_editor.datapoints:
            dataset_editor.dataframe_editor.set_default_category_if_not_in_list(
                datapoint.messages, dataset_editor.shared_category_tracker)

    def update_dataset_editor_if_changed(attr: str, new_value: Any, all_dataset_editors: list[DatasetEditor]) -> bool:
        changed = False
        for editor in all_dataset_editors:
            if getattr(editor, attr) != new_value:
                setattr(editor, attr, new_value)
                # Reset temp dialog dataset editor
                editor.temp_simple_datapoint_dto = None
                # Reset default role
                editor.default_role = MessageKeys[editor.chosen_company.value].value[
                    0][0] if editor.chosen_company else None
                changed = True
        return changed

    @staticmethod
    def check_if_dataset_editor_has_datapoints(all_dataset_editors: list[DatasetEditor]) -> bool:
        """Checks if any dataset editor has datapoints."""
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
