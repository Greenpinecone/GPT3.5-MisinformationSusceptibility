from datetime import timedelta
from io import BytesIO
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from backend.util.logger import StreamlitLogger
from backend.util import utility_functions as uf
from backend.util.config import Config
from backend.service.implementations.service_manager_facade import ServiceManagerFacade
from backend.dtos.get_request import *
from backend.dtos.response import *
from backend.dtos.create_request import *
from backend.database.schema import DatasetCategory
from app.frontend.classes.file_uploader import FileUploader
from app.frontend.classes.dataframe_editor import DataFrameEditor
import math
from uuid import uuid4
from frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper, MessagesContainer


class DatasetEditor:
    def __init__(self, service: ServiceManagerFacade, config: Config, errors_container: st.container):
        self.service = service
        self.config = config
        self.errors_container = errors_container
        # Initialize states for this class
        self.initialize_session_state()

    def initialize_session_state(self):
        if not st.session_state.get('datapoints'):
            st.session_state.datapoints = []
        if not st.session_state.get('next_datapoint_id'):
            st.session_state.next_datapoint_id = 1
        if not st.session_state.get('default_role'):
            st.session_state.default_role = None
        if not st.session_state.get("currently_uploaded_file"):
            st.session_state.currently_uploaded_file = None
        if not st.session_state.get('file_uploader_key'):
            st.session_state.file_uploader_key = 0
        if not st.session_state.get("current_page"):
            st.session_state.current_page = 1
        if not st.session_state.get("datapoints_per_page"):
            st.session_state.datapoints_per_page = 50
        if not st.session_state.get("temp_simple_datapoint_dto"):
            st.session_state.temp_simple_datapoint_dto = None
        if not st.session_state.get("chosen_file_format"):
            st.session_state.chosen_file_format = None
        if not st.session_state.get("chosen_company"):
            st.session_state.chosen_company = None

    def add_all_datapoints(self, message_containers: list[MessagesContainer] | MessagesContainer | None = None, is_temp: bool = False) -> list[DataPointDTOWithDataFrameWrapper]:
        """Saves all message containers passed with a corresponding id and returns a list of DataPointDTOWithDataFrameWrapper objects."""

        generated_datapoint_dtos = []

        def create_datapoint_dto(messages: list[dict], datapoint_id: int | str) -> DataPointDTOWithDataFrameWrapper:
            """Helper function to create a DataPointDTOWithDataFrameWrapper."""
            return DataPointDTOWithDataFrameWrapper(
                datapoint_number=datapoint_id,
                messages=FileUploader.messages_to_df(
                    messages, st.session_state.default_role),
                data_editor_key=f"data_editor_{datapoint_id}"
            )

        if message_containers and not isinstance(message_containers, list):
            message_containers = [message_containers]

        if not message_containers and is_temp:
            datapoint_id = uuid4()
            datapoint_dto = create_datapoint_dto([], datapoint_id)
            generated_datapoint_dtos.append(datapoint_dto)
        elif not message_containers and not is_temp:
            datapoint_id = st.session_state.next_datapoint_id
            datapoint_dto = create_datapoint_dto([], datapoint_id)
            generated_datapoint_dtos.append(datapoint_dto)
            st.session_state.datapoints.append(datapoint_dto)
            st.session_state.next_datapoint_id += 1
        elif message_containers:
            for message_container in message_containers:
                datapoint_id = uuid4() if is_temp else st.session_state.next_datapoint_id
                datapoint_dto = create_datapoint_dto(
                    message_container["messages"], datapoint_id)
                generated_datapoint_dtos.append(datapoint_dto)
                if not is_temp:
                    st.session_state.datapoints.append(datapoint_dto)
                    st.session_state.next_datapoint_id += 1
        return generated_datapoint_dtos

    @st.experimental_dialog(title="New Datapoint", width="large")
    def open_add_datapoint_dialog(self, datapoints_ui_container: st.container):
        """Adds a new datapoint via a dialog window."""

        new_simple_datapoint_dto = None
        if st.session_state.get("temp_simple_datapoint_dto"):
            new_simple_datapoint_dto = st.session_state.temp_simple_datapoint_dto
        else:
            st.session_state.temp_simple_datapoint_dto = self.add_all_datapoints(is_temp=True)[
                0]
            new_simple_datapoint_dto = st.session_state.temp_simple_datapoint_dto

        self.create_new_data_editor(new_simple_datapoint_dto)

        submit_button = st.button(label="Submit", key="submit_adding_new_datapoint",
                                  help="This will add a new datapoint at the end of the list", type="primary")

        if submit_button:
            self.add_datapoint_data_editor_to_ui(
                datapoints_ui_container, new_simple_datapoint_dto, is_new_datapoint=True)

    def add_datapoint_data_editor_to_ui(self, datapoints_ui_container: st.container, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper | None = None, is_new_datapoint: bool | None = False) -> None:
        """Add data editor to the UI for the given datapoint."""

        if is_new_datapoint:
            simple_datapoint_dto = self.add_all_datapoints()[0]
            simple_datapoint_dto.messages = st.session_state.temp_simple_datapoint_dto.messages
            st.session_state.temp_simple_datapoint_dto.messages = None

        with datapoints_ui_container:
            delete_key = f'delete_{simple_datapoint_dto.datapoint_number}'
            self.create_new_data_editor(simple_datapoint_dto)
            st.button(label="Delete", key=delete_key,
                      help="Delete the whole datapoint", type="secondary", on_click=lambda: self.delete_datapoint(simple_datapoint_dto.datapoint_number))

        if is_new_datapoint:
            st.session_state.temp_simple_datapoint_dto = None
            st.rerun()

    def create_new_data_editor(self, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper) -> None:
        """Creates a new data editor for the given datapoint."""

        if isinstance(simple_datapoint_dto.datapoint_number, int):
            st.markdown(f"""###### Datapoint {
                        simple_datapoint_dto.datapoint_number}""")

        st.data_editor(
            simple_datapoint_dto.messages,
            column_config={
                "role": st.column_config.SelectboxColumn(
                    "Role",
                    help="The role of the current prompt.",
                    options=self.config.roles.openai,
                    required=True,
                    default=st.session_state.default_role
                ),
                "content": st.column_config.TextColumn("Content", help="Set the content for the current role.", default=""),
                "category": st.column_config.TextColumn("Category", help="You can only set one category per datapoint.", default=""),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key=simple_datapoint_dto.data_editor_key,
            on_change=DataFrameEditor.update_df,
            args=(simple_datapoint_dto,)
        )

    def delete_datapoint(self, datapoint_id: int) -> None:
        """Removes a datapoint from the session state and deletes its associated session keys."""

        print("DELETING:", datapoint_id)
        datapoint_dto = self.find_datapoint_by_id(datapoint_id)
        if datapoint_dto:
            st.session_state.datapoints.remove(datapoint_dto)
        else:
            st.error("Datapoint not found or already removed.")

    def find_datapoint_by_id(self, datapoint_id: int) -> DataPointDTOWithDataFrameWrapper | None:
        """Searches for a datapoint by ID within the provided list of datapoints."""
        return next((item for item in st.session_state.datapoints if item.datapoint_number == datapoint_id), None)

    def clear_current_datapoints(self) -> None:
        """Clears all current datapoints and resets counters."""

        for simple_datapoint_dto in st.session_state.datapoints[:]:
            self.delete_datapoint(simple_datapoint_dto.datapoint_number)
        self.reset_datapoints_counter()

    def reset_datapoints_counter(self):
        st.session_state.next_datapoint_id = 1

    def display_paginated_datapoints(self, datapoints_container: st.container) -> None:
        """Displays paginated datapoints in the specified container."""

        start_index, end_index = self.calculate_pagination_indices()
        for simple_datapoint_dto in st.session_state.datapoints[start_index:end_index]:
            self.add_datapoint_data_editor_to_ui(
                datapoints_container, simple_datapoint_dto)

    def calculate_pagination_indices(self) -> tuple[int, int]:
        start_index = (st.session_state.current_page - 1) * \
            st.session_state.datapoints_per_page
        end_index = start_index + st.session_state.datapoints_per_page
        return start_index, end_index

    def create_pagination_buttons(self, pagination_buttons_container_above: st.container, pagination_buttons_container_below: st.container) -> None:
        """Function to create pagination buttons with left alignment."""

        num_datapoints = len(st.session_state.datapoints)
        pages = math.ceil(
            num_datapoints / st.session_state.datapoints_per_page)
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
        st.session_state.current_page = page

    def handle_new_file_upload(self, training_dataset_file: BytesIO, datapoints_container: st.container) -> None:
        """Processes a new file upload, initializes pagination, adds all new datapoints, and displays them in the specified container."""

        print("HANDLING FILE UPLOAD")
        message_containers = FileUploader.process_uploads(
            training_dataset_file)
        if message_containers:
            st.session_state.currently_uploaded_file = training_dataset_file
            self.update_page_number(1)
            self.add_all_datapoints(message_containers)
            self.display_paginated_datapoints(datapoints_container)

    def manage_datapoints_flow(self, uploaded_dataset_file: BytesIO, datapoints_container: st.container, pagination_buttons_container_above: st.container, pagination_buttons_container_below: st.container) -> None:
        """Manages the flow of datapoints based on their current state and file changes."""

        if uploaded_dataset_file and not st.session_state.datapoints and st.session_state.currently_uploaded_file != uploaded_dataset_file:
            self.handle_new_file_upload(
                uploaded_dataset_file, datapoints_container)
        elif uploaded_dataset_file and not st.session_state.datapoints and st.session_state.currently_uploaded_file == uploaded_dataset_file:
            self.reset_datapoint_states_if_all_datapoints_deleted()
        elif not st.session_state.datapoints:
            self.clear_datapoint_states_if_none_exist()
        else:
            self.handle_existing_datapoints(datapoints_container)

        self.create_pagination_buttons(
            pagination_buttons_container_above, pagination_buttons_container_below)

    def handle_existing_datapoints(self, datapoints_container: st.container) -> None:
        """Displays existing datapoints in the specified container."""
        self.display_paginated_datapoints(datapoints_container)

    def reset_datapoint_states_if_all_datapoints_deleted(self) -> None:
        st.session_state.file_uploader_key += 1
        self.clear_current_datapoints()
        st.rerun()

    def clear_datapoint_states_if_none_exist(self) -> None:
        self.clear_current_datapoints()

    @st.experimental_fragment
    def load_dataset_input_form(self):
        st.markdown("###### Set the dataset info")
        st.text_input(label="The datasets name", value=None, max_chars=255, key="dataset_name_input",
                      help="Input the name of your dataset", placeholder="The datasets name...", label_visibility="collapsed")
        cols = st.columns(2)
        with cols[0]:
            st.selectbox(label="Select the dataset category",
                         options=[dataset_category for dataset_category in DatasetCategory], index=None, format_func=lambda x: x.value, key="dataset_category_selectbox", help="Select the category the dataset falls into", placeholder="Choose a dataset category", label_visibility="collapsed")
        with cols[1]:
            st.checkbox(label="Make the dataset globally available", value=False, key="globalize_dataset_checkbox",
                        help="Globalized datasets can be selected in the list of available datasets when creating a new project", label_visibility="visible")

    def load_choose_file_format_form(self, uploaded_dataset_file: BytesIO) -> None:
        """Loads the form to choose file format for the uploaded dataset."""

        tab1, tab2 = st.tabs(
            list(vars(self.config.upload_format_formattings).keys()))

        with tab1:
            openai_formatting_expander = st.expander(
                label="Openai formatting examples", expanded=False)
            with openai_formatting_expander:
                st.code(self.config.upload_format_formattings.openai,
                        line_numbers=True)

        with tab2:
            google_formatting_expander = st.expander(
                label="Google formatting examples", expanded=False)
            with google_formatting_expander:
                st.code("Nothing to see here", line_numbers=True)

        formatting_cols = st.columns(2)

        with formatting_cols[0]:
            st.selectbox(label="Choose a company formatting style",
                         options=self.config.fine_tuning_companies.companies, index=None, placeholder="Choose a companies formatting style", help="Chose the formatting style for the file to upload based on company.", label_visibility="collapsed", key="chosen_company", disabled=len(st.session_state.datapoints) or uploaded_dataset_file is not None)

        with formatting_cols[1]:
            st.selectbox(label="Choose an upload file format",
                         options=getattr(self.config.upload_formats, st.session_state.chosen_company) if st.session_state.chosen_company else [], index=None, placeholder="Choose file format", help="Choose the format of the file you want to upload and the datapoints you want to create", label_visibility="collapsed", key="chosen_file_format", disabled=not st.session_state.chosen_company or len(st.session_state.datapoints) or uploaded_dataset_file is not None)

            st.session_state.default_role = getattr(self.config.roles, st.session_state.chosen_company)[
                0] if st.session_state.chosen_company else None

    def process_and_create_dataset(self):
        dataset_name = st.session_state.dataset_name_input
        if not dataset_name:
            uf.show_toast("Dataset name is required.", "info")
            return

        dataset_category = st.session_state.dataset_category_selectbox
        if not dataset_category:
            uf.show_toast("Dataset category is required.", "info")
            return

        simple_datapoint_dtos = st.session_state.datapoints
        chosen_file_format = st.session_state.chosen_file_format
        is_global = st.session_state.globalize_dataset_checkbox
        dataset_name = st.session_state.dataset_name_input
        project_id = st.session_state.current_project.id

        dataset_dto = CreateDatasetDTO(
            dataset_name=dataset_name,
            category=DatasetCategory(
                dataset_category) if dataset_category else None,
            augmented=False,
            fine_tuning_formatting=chosen_file_format,
            project_ids=[project_id],
            is_global=is_global
        )

        self.submit_dataset_and_datapoints(dataset_dto, simple_datapoint_dtos)

    def submit_dataset_and_datapoints(self, dataset_dto: CreateDatasetDTO, datapoint_dtos: list[CreateDataPointDTO]):
        print(dataset_dto, datapoint_dtos, sep="\n", end="\n")
        """Dummy function to simulate submission of dataset and datapoints."""
        print("Submitting Dataset and Datapoints...")
        # Implement actual submission logic here
