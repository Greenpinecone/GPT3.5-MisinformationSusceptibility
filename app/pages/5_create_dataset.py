# Import necessary modules and packages
from datetime import timedelta
from io import BytesIO
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.frontend.dataclasses.dataclasses import ToastMessage
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
from frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from frontend.classes.dataset_editor import DatasetEditor
from backend.database.schema import DatasetCategory, MessageKeys, UploadFormats
from backend.util.global_states import global_toasts
from frontend.mappers.frontend_mappers import ConvertDataPointDTOWithDataFrameWrapperToCreateDatapointDTO


errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)


# All widgets are the same for all datasets to avoid any compatibility issues. If one dataset is uploaded in a specific format, all must be uploaded in this format.
def load_choose_file_format_form(dataset_editor: DatasetEditor, uploaded_dataset_file: BytesIO, all_dataset_editors: list[DatasetEditor]) -> None:
    """Loads the form to choose file format for the uploaded dataset."""

    # Creates tabs for each company and upload format with a code preview how to format the file
    create_formatting_examples_tabs()

    rerun = False
    options = [company for company in FineTuningCompany]
    index = uf.find_index_in_list(options, dataset_editor.chosen_company) or 0

    formatting_cols = st.columns(3)

    with formatting_cols[0]:
        chosen_company: FineTuningCompany = st.selectbox(label="Choose a company formatting style",
                                                         options=options, index=index, format_func=lambda company: company.value, placeholder="Choose a companies formatting style", key="chosen_company_selectbox", help="Chose the formatting style for the file to upload based on company.", label_visibility="collapsed", disabled=check_if_dataset_editor_has_datapoints(all_dataset_editors) or uploaded_dataset_file is not None)

        if dataset_editor.chosen_company != chosen_company:
            dataset_editor.chosen_company = chosen_company
            # Reset stored temp editor dto in case underlying formatting changes
            dataset_editor.temp_simple_datapoint_dto = None
            # Set the default role based on the currently chosen company. TODO: Update this in case different sets of roles are available.
            print(MessageKeys[dataset_editor.chosen_company.value], MessageKeys[dataset_editor.chosen_company.value].value, MessageKeys[dataset_editor.chosen_company.value].value[
                0], MessageKeys[dataset_editor.chosen_company.value].value[
                0][0])
            dataset_editor.default_role = MessageKeys[dataset_editor.chosen_company.value].value[
                0][0] if dataset_editor.chosen_company else None

    options = FineTuningModelVersions[chosen_company.value].value if chosen_company else [
    ]
    index = uf.find_index_in_list(options, dataset_editor.chosen_model) or 0

    with formatting_cols[1]:
        chosen_model: str = st.selectbox(label="Choose a company model",
                                         options=options, index=index, placeholder="Choose a model", key="chosen_model_selectbox", help="Chose a model from the selected company you want to upload data for.", label_visibility="collapsed", disabled=check_if_dataset_editor_has_datapoints(all_dataset_editors) or uploaded_dataset_file is not None)

        if dataset_editor.chosen_model != chosen_model:
            dataset_editor.chosen_model = chosen_model
            # Reset stored temp editor dto in case underlying formatting changes
            dataset_editor.temp_simple_datapoint_dto = None

    options = UploadFormats[chosen_company.value].value[chosen_model] if chosen_model else [
    ]
    index = uf.find_index_in_list(
        options, dataset_editor.chosen_file_format) or 0

    with formatting_cols[2]:
        chosen_file_format: str = st.selectbox(label="Choose an upload file format",
                                               options=options, index=index, placeholder="Choose file format", key="chosen_file_format_selectbox", help="Choose the format of the file you want to upload and the datapoints you want to create", label_visibility="collapsed", disabled=check_if_dataset_editor_has_datapoints(all_dataset_editors) or uploaded_dataset_file is not None)

        if dataset_editor.chosen_file_format != chosen_file_format:
            dataset_editor.chosen_file_format = chosen_file_format
            # Reset stored temp editor dto in case underlying formatting changes
            dataset_editor.temp_simple_datapoint_dto = None
            rerun = True

    selected_dataset: DatasetCategory = st.selectbox(label=" ",
                                                     options=[dataset_category for dataset_category in DatasetCategory], index=0, format_func=lambda x: x.value, key="dataset_category_selectbox", help="Select the dataset category the dataset falls into. You always have to upload both a test and a trainings dataset.", placeholder="Choose the dataset type", label_visibility="visible")

    if rerun:
        # Rerun the page to update the file uploader based on if a  file format has been chosen
        # Reload the page very early so there is only little overhead
        st.rerun()


def create_formatting_examples_tabs():
    companies = list(vars(config.upload_format_formattings).keys())
    company_tabs = st.tabs(companies)

    for tab, company in zip(company_tabs, companies):
        with tab:
            format_dict = getattr(
                config.upload_format_formattings, company)

            with st.expander(label=f"{company.capitalize()} formatting examples", expanded=False):
                # Create tabs for each format type
                format_tabs = st.tabs(list(format_dict.keys()))
                for format_key, format_tab in zip(format_dict.keys(), format_tabs):
                    with format_tab:
                        st.code(format_dict[format_key], line_numbers=True)


@st.experimental_fragment
def load_dataset_input_form():
    st.markdown("###### Set the dataset info")
    cols = st.columns(2)

    with cols[0]:
        st.text_input(label="The datasets name", value=None, max_chars=255, key="dataset_name_input",
                      help="Input the name of your dataset", placeholder="The datasets name...", label_visibility="collapsed")
    with cols[1]:
        st.checkbox(label="Make the dataset globally available", value=False, key="globalize_dataset_checkbox",
                    help="Globalized datasets can be selected in the list of available datasets when creating a new project", label_visibility="visible")

# TODO: Implement dataset format converter to convert uploaded datasets to a single coherent format - e.g. dictionaries instead of CSV, Dictionaries, Text, jsonl etc. This is then converted back for the specific model on demand.


def process_and_create_dataset(all_dataset_editors: list[DatasetEditor]) -> None:
    # Check if the dataset name is provided
    dataset_name = st.session_state.dataset_name_input
    if not dataset_name:
        uf.show_toast("Dataset name is required.", "info")
        return

    # Common values for all dataset editors
    is_global = st.session_state.globalize_dataset_checkbox
    project_id = 1  # st.session_state.current_project.id TODO: COMMENT IN

    # Lists to store the resulting dataset DTOs and datapoint DTOs
    all_dataset_dtos = []
    all_datapoint_dtos = []

    # Loop through each dataset editor
    for dataset_editor in all_dataset_editors:
        # If the dataset editor is of type "test dataset", update the categories in each of its datapoints pandas dataframe, because the uer could have submitted without loading the test dataset again which would cause stale categories still be set on some dtapoints.
        if dataset_editor.dataset_category == DatasetCategory.test:
            for datapoint in dataset_editor.datapoints:
                dataset_editor.dataframe_editor.set_default_category_if_not_in_list(
                    datapoint.messages, dataset_editor.shared_category_tracker)

        chosen_company = dataset_editor.chosen_company
        chosen_model = dataset_editor.chosen_model
        chosen_file_format = dataset_editor.chosen_file_format

        # Convert the wrapper DTO to datapoint DTOs
        convert_wrapper_dto_to_datapoint_dto_schema = ConvertDataPointDTOWithDataFrameWrapperToCreateDatapointDTO(
            many=True)
        datapoint_dtos: list[CreateDataPointDTO] = convert_wrapper_dto_to_datapoint_dto_schema.dump(
            dataset_editor.datapoints)

        # Create the dataset DTO
        dataset_dto = CreateDatasetDTO(
            dataset_name=dataset_name,
            category=DatasetCategory(
                dataset_editor.dataset_category) if dataset_editor.dataset_category else None,
            augmented=False,
            fine_tuning_company=chosen_company,
            fine_tuning_formatting=chosen_file_format,
            fine_tuning_model=chosen_model,
            project_ids=[project_id],
            is_global=is_global
        )

        # Add to the lists
        all_dataset_dtos.append(dataset_dto)
        all_datapoint_dtos.append(datapoint_dtos)

    # Pass the lists to the next function
    submit_all_datasets_and_datapoints(all_dataset_dtos, all_datapoint_dtos)


def submit_all_datasets_and_datapoints(dataset_dtos: list[CreateDatasetDTO], datapoint_dtos: list[list[CreateDataPointDTO]]):
    service.create_dataset_with_datapoints(
        dataset_dtos[0], datapoint_dtos[0], dataset_dtos[1], datapoint_dtos[1])
    uf.show_toast(
        "Dataset has been successfully created.", "success")


def check_if_dataset_editor_has_datapoints(all_dataset_editors: list[DatasetEditor]):
    for dataset_editor in all_dataset_editors:
        if len(dataset_editor.datapoints) > 0:
            return True
    return False


with logger:
    uf.apply_global_style()
    # Can be easily adapted in case of multiple users at the same time
    service, config = uf.initialize_global_states(
        ServiceManagerFacade, Config)

    if global_toasts:
        uf.show_one_time_toast_messages(global_toasts)
    # uf.set_query_params_from_session(
    #     {"projectId": ["current_project", "id"]}, config)
    # Initialize the DatasetEditor object

    shared_category_tracker = []
    training_dataset_editor: DatasetEditor = uf.get_or_create_session_state(
        "training_dataset_editor", DatasetCategory.training, DataFrameEditor(), shared_category_tracker, default_value=DatasetEditor)
    test_dataset_editor: DatasetEditor = uf.get_or_create_session_state(
        "test_dataset_editor", DatasetCategory.test, DataFrameEditor(), shared_category_tracker, default_value=DatasetEditor)

    # Set the current dataset editor based on the chosen upload dataset type
    dataset_editor = None
    if st.session_state.get("dataset_category_selectbox"):
        if st.session_state.dataset_category_selectbox == DatasetCategory.training:
            dataset_editor = training_dataset_editor
        else:
            dataset_editor = test_dataset_editor
    else:
        dataset_editor = training_dataset_editor
        st.session_state.dataset_category_selectbox = DatasetCategory.training

    all_dataset_editors = [training_dataset_editor, test_dataset_editor]

    def load_page(dataset_editor: DatasetEditor, all_dataset_editors: list[DatasetEditor]):
        chosen_file_format_container = st.container()

        # Each dataset_editor has its own file_uploader widget defined by an individual key
        uploaded_dataset_file: BytesIO = st.file_uploader(
            label="Upload a new dataset", type=dataset_editor.chosen_file_format, key=dataset_editor.file_uploader_key, accept_multiple_files=False, help="Upload a file formatted in the format chosen. Uploaded datasets will be directly available to select within your project after submitting.", disabled=False if dataset_editor.chosen_file_format else True, on_change=dataset_editor.clear_current_datapoints)

        with chosen_file_format_container:
            load_choose_file_format_form(
                dataset_editor, uploaded_dataset_file, all_dataset_editors)

        load_dataset_input_form()

        # Show dataset name since the "uploaded file marker" is removed from the st.file_uploader on key change
        label = None
        if dataset_editor.currently_uploaded_file:
            label = dataset_editor.currently_uploaded_file.name
        elif uploaded_dataset_file:
            label = uploaded_dataset_file.name

        if label:
            # Remove all datapoints
            delete_dataset_button = st.button(
                label=label + "✖️", help="Remove the uploaded dataset with all datapoints", type="secondary")

            if delete_dataset_button:
                global_toasts.append(ToastMessage(
                    "Successfully removed dataset.", "success"))
                dataset_editor.reset_editor_states()

        pagination_buttons_container_above = st.container(border=False)
        datapoints_container = st.container(border=False)
        pagination_buttons_container_below = st.container(border=False)

        dataset_editor.manage_datapoints_flow(
            uploaded_dataset_file, datapoints_container, pagination_buttons_container_above, pagination_buttons_container_below)

        print("DATAPOINT IDS", [
              x.datapoint_number for x in dataset_editor.datapoints])

        cols = st.columns((2, 5, 1))

        with cols[0]:
            add_new_datapoint_button = st.button(label="Add New Datapoint", key="add_new_datapoint_button",
                                                 help="Add a new datapoint to the current dataset", type="secondary", disabled=not dataset_editor.chosen_file_format)
            if add_new_datapoint_button:
                dataset_editor.open_add_datapoint_dialog(datapoints_container)

        with cols[2]:
            submit_button = st.button(label="Submit", key="submit_dataset",
                                      help="Submit both datasets with all their datapoints", type="primary", disabled=not all_dataset_editors[0].datapoints)
            if submit_button:
                process_and_create_dataset(all_dataset_editors)

    load_page(dataset_editor, all_dataset_editors)
