from datetime import timedelta
from io import BytesIO
from typing import Any
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.frontend.classes.dataframe_widget_provider import DataFrameWidgetProvider
from app.frontend.dataclasses.dataclasses import ToastMessage
from backend.util.logger import StreamlitLogger
from backend.util import utility_functions as uf
from backend.util.config import Config
from backend.service.implementations.service_manager_facade import ServiceManagerFacade
from backend.dtos.get_request import *
from backend.dtos.response import *
from backend.dtos.create_request import *
from backend.database.schema import DatasetCategory, MessageKeys, UploadFormats
from app.frontend.classes.file_uploader import FileUploader
from app.frontend.classes.dataframe_editor import DataFrameEditor
import math
from uuid import uuid4
from frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper, MessagesContainer
import json
from streamlit.delta_generator import DeltaGenerator
from backend.util.global_states import global_toasts


class DatasetEditor:

    def __init__(self, dataset_category: DatasetCategory, dataframe_editor: DataFrameEditor, shared_category_tracker: list[str], datapoints_per_page: int = 50, default_role: str | None = None, chosen_file_format: str | None = None, chosen_company: FineTuningCompany | None = None):
        self.shared_category_tracker = shared_category_tracker
        self.dataset_category = dataset_category
        self.dataframe_editor = dataframe_editor
        self.datapoints_per_page = datapoints_per_page
        self.default_role = default_role
        self.chosen_file_format = chosen_file_format
        self.chosen_company = chosen_company
        self.datapoints = []
        self.current_page = 1
        self.next_datapoint_number = 1
        self.file_uploader_key = uuid4()
        self.chosen_model = None
        self.temp_simple_datapoint_dto = None
        self.currently_uploaded_file = None

    def add_all_datapoints(self, message_containers: list[MessagesContainer] | MessagesContainer | None = None, is_temp: bool = False) -> list[DataPointDTOWithDataFrameWrapper]:
        """Saves all message containers passed with a corresponding id and returns a list of DataPointDTOWithDataFrameWrapper objects."""

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

        if message_containers and not isinstance(message_containers, list):
            message_containers = [message_containers]

        # If is_temp is true the datapoint is not added to the render list (self.datapoints) and
        if not message_containers and is_temp:
            datapoint_id = uuid4()
            datapoint_dto = create_datapoint_dto([], datapoint_id)
            generated_datapoint_dtos.append(datapoint_dto)
        elif not message_containers and not is_temp:
            datapoint_id = uuid4()
            datapoint_number = self.next_datapoint_number
            datapoint_dto = create_datapoint_dto(
                [], datapoint_id, datapoint_number)
            generated_datapoint_dtos.append(datapoint_dto)
            self.datapoints.append(datapoint_dto)
            self.next_datapoint_number += 1
        elif message_containers:
            for message_container in message_containers:
                datapoint_id = uuid4()
                if is_temp:
                    datapoint_dto = create_datapoint_dto(
                        message_container["messages"], datapoint_id)
                else:
                    datapoint_number = self.next_datapoint_number
                    datapoint_dto = create_datapoint_dto(
                        message_container["messages"], datapoint_id, datapoint_number)
                    self.datapoints.append(datapoint_dto)
                    self.next_datapoint_number += 1
                generated_datapoint_dtos.append(datapoint_dto)
        return generated_datapoint_dtos

    @st.experimental_dialog(title="New Datapoint", width="large")
    def open_add_datapoint_dialog(self, datapoints_ui_container: DeltaGenerator):
        """Adds a new datapoint via a dialog window."""

        # Adds an empty space at the top of the dialog after the title so that the data editors hover menue is visible.
        st.text("")

        if not self.temp_simple_datapoint_dto:
            self.temp_simple_datapoint_dto = self.add_all_datapoints(is_temp=True)[
                0]

        self.create_new_data_editor(
            self.temp_simple_datapoint_dto)

        submit_button = st.button(label="Submit", key="submit_adding_new_datapoint",
                                  help="This will add a new datapoint at the end of the list", type="primary")

        if submit_button:
            self.add_datapoint_data_editor_to_ui(
                datapoints_ui_container)
            # Reset the current dialog datapoint
            self.temp_simple_datapoint_dto = None
            st.rerun()

    def add_datapoint_data_editor_to_ui(self, datapoints_ui_container: DeltaGenerator, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper | None = None) -> None:
        """Add data editor to the UI for the given datapoint."""

        if not simple_datapoint_dto:
            # Assign the temp datapoint value to the now actually added datapoint
            simple_datapoint_dto = self.add_all_datapoints()[0]
            simple_datapoint_dto.messages = self.temp_simple_datapoint_dto.messages

        with datapoints_ui_container:
            delete_key = f'delete_{simple_datapoint_dto.datapoint_id}'
            self.create_new_data_editor(simple_datapoint_dto)
            st.button(label="Delete", key=delete_key,
                      help="Delete the whole datapoint", type="secondary", on_click=self.delete_datapoint,
                      args=(simple_datapoint_dto.datapoint_id,))

    def create_new_data_editor(self, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper) -> None:
        """Creates a new data editor for the given datapoint."""
        if simple_datapoint_dto.datapoint_number:
            st.markdown(f"""###### Datapoint {
                        simple_datapoint_dto.datapoint_number}""")

        if self.dataset_category == DatasetCategory.training:
            DataFrameWidgetProvider.create_training_data_editor_widget(
                simple_datapoint_dto, self.chosen_company, self.default_role, self.dataframe_editor)
        else:

            # Checks if the used category in the test datapoint is still available, else reset the category column
            self.dataframe_editor.set_default_category_if_not_in_list(
                simple_datapoint_dto.messages, self.shared_category_tracker)
            DataFrameWidgetProvider.create_test_data_editor_widget(
                simple_datapoint_dto, self.chosen_company, self.default_role, self.dataframe_editor, self.shared_category_tracker)

    def delete_datapoint(self, datapoint_id: int) -> None:
        """Removes a datapoint from the session state and deletes its associated session keys."""

        print("DELETING DATAPOINT - HALLO 1 !!!")
        datapoint_dto: DataPointDTOWithDataFrameWrapper = self.find_datapoint_by_id(
            datapoint_id)
        if datapoint_dto:
            self.datapoints.remove(datapoint_dto)
            global_toasts.append(ToastMessage(
                f"Successfully deleted datapoint {datapoint_dto.datapoint_number}.", "success"))
        else:
            global_toasts.append(ToastMessage(
                f"Datapoint has already been deleted.", "error"))

    def find_datapoint_by_id(self, datapoint_id: int) -> DataPointDTOWithDataFrameWrapper | None:
        """Searches for a datapoint by ID within the provided list of datapoints."""
        return next((item for item in self.datapoints if item.datapoint_id == datapoint_id), None)

    def clear_current_datapoints(self) -> None:
        """Clears all current datapoints and resets counters."""

        self.datapoints = []
        self.reset_datapoints_counter()

    def reset_datapoints_counter(self):
        self.next_datapoint_number = 1

    def display_paginated_datapoints(self, datapoints_container: DeltaGenerator) -> None:
        """Displays paginated datapoints in the specified container."""

        start_index, end_index = self.calculate_pagination_indices()
        for simple_datapoint_dto in self.datapoints[start_index:end_index]:
            self.add_datapoint_data_editor_to_ui(
                datapoints_container, simple_datapoint_dto)

    def calculate_pagination_indices(self) -> tuple[int, int]:
        start_index = (self.current_page - 1) * \
            self.datapoints_per_page
        end_index = start_index + self.datapoints_per_page
        return start_index, end_index

    def create_pagination_buttons(self, pagination_buttons_container_above: DeltaGenerator, pagination_buttons_container_below: DeltaGenerator) -> None:
        """Function to create pagination buttons with left alignment."""

        num_datapoints = len(self.datapoints)
        pages = math.ceil(
            num_datapoints / self.datapoints_per_page)
        buttons_per_row = 10

        rows_needed = math.ceil(pages / buttons_per_row)
        for row in range(rows_needed):
            start_page = row * buttons_per_row + 1
            end_page = min(start_page + buttons_per_row, pages + 1)

            with pagination_buttons_container_above:
                cols = st.columns(buttons_per_row)
                for i in range(start_page, end_page):
                    with cols[i - start_page]:
                        st.button(label=str(i), key=f"""page_{
                                  i}""", on_click=lambda i=i: self.update_page_number(i))

            with pagination_buttons_container_below:
                cols = st.columns(buttons_per_row)
                for i in range(start_page, end_page):
                    with cols[i - start_page]:
                        st.button(label=str(i), key=f"""page_{
                                  i*9999999}""", on_click=lambda i=i: self.update_page_number(i))

    def update_page_number(self, page: int) -> None:
        self.current_page = page

    def handle_new_file_upload(self, dataset_file: BytesIO, datapoints_container: DeltaGenerator) -> None:
        """Processes a new file upload, initializes pagination, adds all new datapoints, and displays them in the specified container."""

        print("HANDLING FILE UPLOAD")
        message_containers = FileUploader.process_uploads(
            dataset_file, self.chosen_company, self.chosen_file_format, self.chosen_model)
        if message_containers:
            self.currently_uploaded_file = dataset_file
            self.update_page_number(1)
            self.add_all_datapoints(message_containers)
            self.display_paginated_datapoints(datapoints_container)
            self.update_shared_category_tracker()

    def manage_datapoints_flow(self, uploaded_dataset_file: BytesIO, datapoints_container: DeltaGenerator, pagination_buttons_container_above: DeltaGenerator | None = None, pagination_buttons_container_below: DeltaGenerator | None = None) -> None:
        """Manages the flow of datapoints based on their current state and file changes."""

        # TODO: Should be improved - efficiency wise.
        self.update_shared_category_tracker()

        if not self.datapoints and self.currently_uploaded_file != uploaded_dataset_file:
            if uploaded_dataset_file and not uploaded_dataset_file.size:
                global_toasts.append(ToastMessage(
                    "Uploaded file cannot be empty.", "info"))
                self.reset_editor_states()
            elif not uploaded_dataset_file:
                global_toasts.append(ToastMessage(
                    "Successfully removed dataset.", "success"))
                self.reset_editor_states()
            elif uploaded_dataset_file:
                self.handle_new_file_upload(
                    uploaded_dataset_file, datapoints_container)
        elif not self.datapoints and self.currently_uploaded_file == uploaded_dataset_file:
            if self.currently_uploaded_file is not None:
                global_toasts.append(ToastMessage(
                    "Successfully removed dataset.", "success"))
                self.reset_editor_states()
        else:
            self.handle_existing_datapoints(datapoints_container)

        # Only show pagination if there are more datapoints to display than allowed on one page
        if len(self.datapoints) > self.datapoints_per_page:
            self.create_pagination_buttons(
                pagination_buttons_container_above, pagination_buttons_container_below)

    def handle_existing_datapoints(self, datapoints_container: DeltaGenerator) -> None:
        """Displays existing datapoints in the specified container."""
        self.display_paginated_datapoints(datapoints_container)

    def reset_editor_states(self) -> None:
        self.file_uploader_key = uuid4()
        self.currently_uploaded_file = None
        self.clear_current_datapoints()
        self.update_shared_category_tracker()
        st.rerun()

    def update_shared_category_tracker(self):
        """
        Update the list of used categories based on the first row's category in each datapoint.

        Args:
            datapoints (list[pd.DataFrame]): List of DataFrames representing the datapoints.
        """
        if self.dataset_category == DatasetCategory.training:
            # Initialize shared_category_tracker to a new empty list
            self.shared_category_tracker.clear()

            for datapoint in self.datapoints:
                df = datapoint.messages
                # Check if there are any rows in the DataFrame
                if df.shape[0] > 0:
                    # Get the first row's category
                    first_category = df['category'].iloc[0]

                    # Check if the category is not empty or whitespace
                    if first_category and not first_category.isspace():
                        self.shared_category_tracker.append(first_category)

            print(f"Updated used categories: {self.shared_category_tracker}")
