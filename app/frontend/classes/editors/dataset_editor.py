"""
This module provides functionality for editing datasets using a Streamlit interface.
It handles various operations such as adding, deleting, and managing datapoints.

Classes:
    DatasetEditor: Manages dataset editing and interaction with the Streamlit UI.
"""


import streamlit as st
from io import BytesIO
from uuid import uuid4
from streamlit.delta_generator import DeltaGenerator
from app.frontend.classes.paginator import Paginator
from app.frontend.classes.manager.toast_manager import ToastManager
from app.frontend.classes.dataframe_widget_provider import DataFrameWidgetProvider
from app.frontend.classes.file_uploader import FileUploader
from app.frontend.classes.editors.dataframe_editor import DataFrameEditor
from app.frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from app.backend.custom_types.typedicts import MessagesContainer
from app.backend.database.schema import DatasetCategory, FineTuningCompany


class DatasetEditor:
    """
    Manages dataset editing and interaction with the Streamlit UI.

    Attributes:
        dataset_category (DatasetCategory): The category of the dataset (training or test).
        dataframe_editor (DataFrameEditor): Instance of the DataFrameEditor for managing DataFrame edits.
        paginator (Paginator): Instance of the Paginator for handling pagination.
        default_role (str | None): Default role for new messages.
        chosen_file_format (str | None): Chosen file format for uploading.
        chosen_company (FineTuningCompany | None): Chosen company for fine-tuning.
        datapoints (list): List of datapoints.
        next_datapoint_number (int): Counter for the next datapoint number.
        file_uploader_key (uuid.UUID): Unique key for the file uploader.
        chosen_model (Any): Chosen model for fine-tuning.
        temp_simple_datapoint_dto (DataPointDTOWithDataFrameWrapper | None): Temporary storage for new datapoint DTOs.
        currently_uploaded_file (BytesIO | None): Currently uploaded dataset file.
    """

    def __init__(self, dataset_category: DatasetCategory, dataframe_editor: DataFrameEditor, paginator: Paginator, default_role: str | None = None, chosen_file_format: str | None = None, chosen_company: FineTuningCompany | None = None):
        self.dataset_category = dataset_category
        self.dataframe_editor = dataframe_editor
        self.paginator = paginator
        self.default_role = default_role
        self.chosen_file_format = chosen_file_format
        self.chosen_company = chosen_company
        self.datapoints = []
        self.next_datapoint_number = 1
        self.file_uploader_key = uuid4()
        self.chosen_model = None
        self.temp_simple_datapoint_dto = None
        self.currently_uploaded_file = None

    def add_all_datapoints(self, message_containers: list[MessagesContainer] | MessagesContainer | None = None, is_temp: bool = False) -> list[DataPointDTOWithDataFrameWrapper]:
        """
        Saves all message containers passed with a corresponding ID and returns a list of DataPointDTOWithDataFrameWrapper objects.

        Args:
            message_containers (list[MessagesContainer] | MessagesContainer | None): The message containers to add.
            is_temp (bool): Flag indicating whether the datapoint is temporary.

        Returns:
            list[DataPointDTOWithDataFrameWrapper]: List of created DataPointDTOWithDataFrameWrapper objects.
        """

        generated_datapoint_dtos = []

        def create_datapoint_dto(messages: list[dict], datapoint_id: uuid4, datapoint_number: int | None = None) -> DataPointDTOWithDataFrameWrapper:
            """Helper function to create a DataPointDTOWithDataFrameWrapper."""
            return DataPointDTOWithDataFrameWrapper(
                datapoint_id=datapoint_id,
                datapoint_number=datapoint_number,
                messages=FileUploader.messages_to_df(
                    messages, self.default_role),
                data_editor_key=f"data_editor_{datapoint_id}"
            )

        message_containers = [message_containers] if message_containers and not isinstance(
            message_containers, list) else message_containers

        if not message_containers:
            datapoint_id = uuid4()
            datapoint_dto = create_datapoint_dto(
                [], datapoint_id, self.next_datapoint_number if not is_temp else None)
            generated_datapoint_dtos.append(datapoint_dto)
            if not is_temp:
                self.datapoints.append(datapoint_dto)
                self.next_datapoint_number += 1
        else:
            for message_container in message_containers:
                datapoint_id = uuid4()
                datapoint_dto = create_datapoint_dto(
                    message_container["messages"], datapoint_id, self.next_datapoint_number if not is_temp else None)
                generated_datapoint_dtos.append(datapoint_dto)
                if not is_temp:
                    self.datapoints.append(datapoint_dto)
                    self.next_datapoint_number += 1

        return generated_datapoint_dtos

    @st.experimental_dialog(title="New Datapoint", width="large")
    def open_add_datapoint_dialog(self, datapoints_ui_container: DeltaGenerator):
        """
        Adds a new datapoint via a dialog window.

        Args:
            datapoints_ui_container (DeltaGenerator): The container to which the new datapoint UI will be added.
        """

        st.text("")  # Adds an empty space at the top of the dialog
        if not self.temp_simple_datapoint_dto:
            self.temp_simple_datapoint_dto = self.add_all_datapoints(is_temp=True)[
                0]

        self.create_new_data_editor(self.temp_simple_datapoint_dto)
        submit_button = st.button(label="Submit", key="submit_adding_new_datapoint",
                                  help="This will add a new datapoint at the end of the list", type="primary")
        if submit_button:
            self.add_datapoint_data_editor_to_ui(datapoints_ui_container)
            self.temp_simple_datapoint_dto = None
            st.rerun()

    def add_datapoint_data_editor_to_ui(self, datapoints_ui_container: DeltaGenerator, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper | None = None) -> None:
        """
        Adds a data editor to the UI for the given datapoint.

        Args:
            datapoints_ui_container (DeltaGenerator): The container to which the data editor UI will be added.
            simple_datapoint_dto (DataPointDTOWithDataFrameWrapper | None): The datapoint DTO to add a data editor for.
        """

        if not simple_datapoint_dto:
            simple_datapoint_dto = self.add_all_datapoints()[0]
            simple_datapoint_dto.messages = self.temp_simple_datapoint_dto.messages

        with datapoints_ui_container:
            delete_key = f'delete_{simple_datapoint_dto.datapoint_id}'
            self.create_new_data_editor(simple_datapoint_dto)
            st.button(label="Delete", key=delete_key, help="Delete the whole datapoint", type="secondary",
                      on_click=self.delete_datapoint, args=(simple_datapoint_dto.datapoint_id,))

    def create_new_data_editor(self, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper) -> None:
        """
        Creates a new data editor for the given datapoint.

        Args:
            simple_datapoint_dto (DataPointDTOWithDataFrameWrapper): The datapoint DTO to create a data editor for.
        """

        st.markdown(f"""###### Datapoint {
                    simple_datapoint_dto.datapoint_number}""") if simple_datapoint_dto.datapoint_number else None
        if self.dataset_category == DatasetCategory.training:
            DataFrameWidgetProvider.create_training_data_editor_widget(
                simple_datapoint_dto, self.chosen_company, self.default_role, self.dataframe_editor)
        else:
            DataFrameWidgetProvider.create_test_data_editor_widget(
                simple_datapoint_dto, self.chosen_company, self.default_role, self.dataframe_editor)

    def delete_datapoint(self, datapoint_id: int) -> None:
        """
        Removes a datapoint from the session state and deletes its associated session keys.

        Args:
            datapoint_id (int): The ID of the datapoint to delete.
        """

        datapoint_dto: DataPointDTOWithDataFrameWrapper = self.find_datapoint_by_id(
            datapoint_id)
        if datapoint_dto:
            self.datapoints.remove(datapoint_dto)
            ToastManager.add_global_toasts(f"""Successfully deleted datapoint {
                datapoint_dto.datapoint_number}.""", "success")
        else:
            ToastManager.add_global_toasts(
                "Datapoint has already been deleted.", "error")

    def find_datapoint_by_id(self, datapoint_id: int) -> DataPointDTOWithDataFrameWrapper | None:
        """
        Searches for a datapoint by ID within the provided list of datapoints.

        Args:
            datapoint_id (int): The ID of the datapoint to find.

        Returns:
            DataPointDTOWithDataFrameWrapper | None: The found datapoint DTO or None if not found.
        """

        return next((item for item in self.datapoints if item.datapoint_id == datapoint_id), None)

    def clear_current_datapoints(self) -> None:
        """
        Clears all current datapoints and resets counters.
        """

        self.datapoints = []
        self.reset_datapoints_counter()

    def reset_datapoints_counter(self):
        """
        Resets the datapoint counter.
        """

        self.next_datapoint_number = 1

    def display_paginated_datapoints(self, datapoints_container: DeltaGenerator) -> None:
        """
        Displays paginated datapoints in the specified container.

        Args:
            datapoints_container (DeltaGenerator): The container to display paginated datapoints in.
        """

        paginated_datapoints = self.paginator.get_paginated_items(
            self.datapoints)
        for simple_datapoint_dto in paginated_datapoints:
            self.add_datapoint_data_editor_to_ui(
                datapoints_container, simple_datapoint_dto)

    def handle_new_file_upload(self, dataset_file: BytesIO, datapoints_container: DeltaGenerator) -> None:
        """
        Processes a new file upload, initializes pagination, adds all new datapoints, and displays them in the specified container.

        Args:
            dataset_file (BytesIO): The uploaded dataset file.
            datapoints_container (DeltaGenerator): The container to display the new datapoints in.
        """

        message_containers = FileUploader.process_uploads(
            dataset_file, self.chosen_company, self.chosen_file_format, self.chosen_model)
        if message_containers:
            self.currently_uploaded_file = dataset_file
            self.paginator.current_page = 1
            self.add_all_datapoints(message_containers)
            self.display_paginated_datapoints(datapoints_container)

    def manage_datapoints_flow(self, uploaded_dataset_file: BytesIO, datapoints_container: DeltaGenerator) -> None:
        """
        Manages the flow of datapoints based on their current state and file changes.

        Args:
            uploaded_dataset_file (BytesIO): The uploaded dataset file.
            datapoints_container (DeltaGenerator): The container to manage datapoints in.
        """

        if not self.datapoints and self.currently_uploaded_file != uploaded_dataset_file:
            self.handle_empty_datapoints(
                uploaded_dataset_file, datapoints_container)
        elif not self.datapoints and self.currently_uploaded_file == uploaded_dataset_file:
            if self.currently_uploaded_file is not None:
                ToastManager.add_global_toasts(
                    "Successfully removed dataset.", "success")
                self.reset_editor_states()
        else:
            self.handle_existing_datapoints(datapoints_container)

    def handle_empty_datapoints(self, uploaded_dataset_file: BytesIO, datapoints_container: DeltaGenerator) -> None:
        """
        Handles the case where there are no datapoints.

        Args:
            uploaded_dataset_file (BytesIO): The uploaded dataset file.
            datapoints_container (DeltaGenerator): The container to manage datapoints in.
        """

        if uploaded_dataset_file and not uploaded_dataset_file.size:
            ToastManager.add_global_toasts(
                "Uploaded file cannot be empty.", "info")
            self.reset_editor_states()
        elif not uploaded_dataset_file:
            ToastManager.add_global_toasts(
                "Successfully removed dataset.", "success")
            self.reset_editor_states()
        elif uploaded_dataset_file:
            self.handle_new_file_upload(
                uploaded_dataset_file, datapoints_container)

    def handle_existing_datapoints(self, datapoints_container: DeltaGenerator) -> None:
        """
        Displays existing datapoints in the specified container.

        Args:
            datapoints_container (DeltaGenerator): The container to display datapoints in.
        """

        self.display_paginated_datapoints(datapoints_container)

    def reset_editor_states(self) -> None:
        """
        Resets the editor states.
        """

        self.file_uploader_key = uuid4()
        self.currently_uploaded_file = None
        self.clear_current_datapoints()
        st.rerun()
