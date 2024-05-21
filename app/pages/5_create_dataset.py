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


def load_choose_file_format_form(dataset_editor: DatasetEditor, uploaded_dataset_file: BytesIO, session_state_keys_prefix: str) -> None:
    """Loads the form to choose file format for the uploaded dataset."""

    # Creates tabs for each company and upload format with a code preview how to format the file
    create_formatting_examples_tabs()

    # Reset temp dto saved and opened when adding new datapoint when company or data format change to avoid half filled / wrongly filled data editor when adding data point again after not submitting
    if st.session_state.get(f"{session_state_keys_prefix}_current_chosen_company"):
        if st.session_state.get(f"{session_state_keys_prefix}_current_chosen_company") != dataset_editor.chosen_company or st.session_state.get(f"{session_state_keys_prefix}_current_chosen_file_format") != dataset_editor.chosen_file_format:
            dataset_editor.temp_simple_datapoint_dto = None

    st.session_state[f"""{
        session_state_keys_prefix}_current_chosen_company"""] = dataset_editor.chosen_company
    st.session_state[[f"{session_state_keys_prefix}_current_chosen_file_format"]
                     ] = dataset_editor.chosen_file_format

    rerun = False

    formatting_cols = st.columns(3)

    with formatting_cols[0]:
        chosen_company: FineTuningCompany = st.selectbox(label="Choose a company formatting style",
                                                         options=[company for company in FineTuningCompany], index=None, format_func=lambda company: company.value, placeholder="Choose a companies formatting style", key=f"{session_state_keys_prefix}_chosen_company_selectbox", help="Chose the formatting style for the file to upload based on company.", label_visibility="collapsed", disabled=len(dataset_editor.datapoints) or uploaded_dataset_file is not None)

        dataset_editor.chosen_company = chosen_company

    with formatting_cols[1]:
        chosen_model: str = st.selectbox(label="Choose a company model",
                                         options=FineTuningModelVersions[chosen_company.value].value if chosen_company else [], index=None, placeholder="Choose a model", key=f"{session_state_keys_prefix}_chosen_model_selectbox", help="Chose a model from the selected company you want to upload data for.", label_visibility="collapsed", disabled=not chosen_company or len(dataset_editor.datapoints) or uploaded_dataset_file is not None)

        dataset_editor.chosen_model = chosen_model

    with formatting_cols[2]:
        chosen_file_format: str = st.selectbox(label="Choose an upload file format",
                                               options=UploadFormats[chosen_company.value].value[chosen_model] if chosen_model else [], index=None, placeholder="Choose file format", key=f"{session_state_keys_prefix}_chosen_file_format_selectbox", help="Choose the format of the file you want to upload and the datapoints you want to create", label_visibility="collapsed", disabled=not chosen_model or len(dataset_editor.datapoints) or uploaded_dataset_file is not None)

        if dataset_editor.chosen_file_format != chosen_file_format:
            rerun = True
        dataset_editor.chosen_file_format = chosen_file_format

        dataset_editor.default_role = MessageKeys[dataset_editor.chosen_company.value].value[
            0][0] if dataset_editor.chosen_company else None

    selected_dataset: DatasetCategory = st.selectbox(label=" ",
                                                     options=[dataset_category for dataset_category in DatasetCategory], index=0, format_func=lambda x: x.value, key=f"{session_state_keys_prefix}_dataset_category_selectbox", help="Select the dataset category the dataset falls into. You always have to upload both a test and a trainings dataset.", placeholder="Choose the dataset type", label_visibility="visible", disabled=not chosen_file_format)

    st.session_state.session_state_keys_prefix = selected_dataset
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


def process_and_create_dataset(dataset_editor: DatasetEditor) -> None:
    dataset_name = st.session_state.dataset_name_input
    if not dataset_name:
        uf.show_toast("Dataset name is required.", "info")
        return

    dataset_category = st.session_state.dataset_category_selectbox
    if not dataset_category:
        uf.show_toast("Dataset category is required.", "info")
        return

    chosen_company = dataset_editor.chosen_company
    if not chosen_company:
        uf.show_toast("A chosen company is required.", "info")
        return

    convert_wrapper_dto_to_datapoint_dto_schema = ConvertDataPointDTOWithDataFrameWrapperToCreateDatapointDTO(
        many=True)
    datapoint_dtos: list[DataPointDTOWithDataFrameWrapper] = convert_wrapper_dto_to_datapoint_dto_schema.dump(
        dataset_editor.datapoints)
    chosen_file_format = dataset_editor.chosen_file_format
    chosen_model = dataset_editor.chosen_model
    is_global = st.session_state.globalize_dataset_checkbox
    project_id = 1  # st.session_state.current_project.id TODO: COMMENT IN

    dataset_dto = CreateDatasetDTO(
        dataset_name=dataset_name,
        category=DatasetCategory(
            dataset_category) if dataset_category else None,
        augmented=False,
        fine_tuning_company=chosen_company,
        fine_tuning_formatting=chosen_file_format,
        fine_tuning_model=chosen_model,
        project_ids=[project_id],
        is_global=is_global
    )

    submit_dataset_and_datapoints(dataset_dto, datapoint_dtos)


def submit_dataset_and_datapoints(dataset_dto: CreateDatasetDTO, datapoint_dtos: list[CreateDataPointDTO]):
    print(dataset_dto, datapoint_dtos, sep="\n", end="\n")
    """Dummy function to simulate submission of dataset and datapoints."""
    print("Submitting Dataset and Datapoints...")
    service.create_dataset_with_datapoints(
        dataset_dto, datapoint_dtos)
    # Implement actual submission logic here


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
    training_dataset_editor = uf.get_or_create_session_state(
        "training_dataset_editor", DatasetCategory.training, default_value=DatasetEditor)
    test_dataset_editor = uf.get_or_create_session_state(
        "test_dataset_editor", DatasetCategory.test, default_value=DatasetEditor)

    # Set the current dataset editor based on the chosen upload dataset type
    dataset_editor = None
    st.session_state.session_state_keys_prefix = "training"
    if st.session_state.get("dataset_category_selectbox"):
        if st.session_state.dataset_category_selectbox == DatasetCategory.training:
            dataset_editor = training_dataset_editor
            session_state_keys_prefix = "training"
        else:
            dataset_editor = test_dataset_editor
            session_state_keys_prefix = "test"
    else:
        dataset_editor = training_dataset_editor
        session_state_keys_prefix = "training"

    def load_page(dataset_editor: DatasetEditor, session_state_keys_prefix: str):
        chosen_file_format_container = st.container()

        uploaded_dataset_file: BytesIO = st.file_uploader(
            label="Upload a new dataset", type=dataset_editor.chosen_file_format, key=dataset_editor.file_uploader_key, accept_multiple_files=False, help="Upload a file formatted in the format chosen. Uploaded datasets will be directly available to select within your project after submitting.", disabled=False if dataset_editor.chosen_file_format else True, on_change=dataset_editor.clear_current_datapoints)

        # if not uploaded_dataset_file.size:
        #         global_toasts.append(ToastMessage(
        #             "Uploaded file cannot be empty.", "info"))
        #         file_uploader_key += 1
        #         st.rerun()

        with chosen_file_format_container:
            load_choose_file_format_form(
                dataset_editor, uploaded_dataset_file, session_state_keys_prefix)

        load_dataset_input_form()

        pagination_buttons_container_above = st.container(border=False)
        datapoints_container = st.container(border=False)
        pagination_buttons_container_below = st.container(border=False)

        dataset_editor.manage_datapoints_flow(
            uploaded_dataset_file, datapoints_container, pagination_buttons_container_above, pagination_buttons_container_below)

        print("DATAPOINT IDS", [
              x.datapoint_number for x in dataset_editor.datapoints])

        cols = st.columns((1, 5, 1))

        with cols[1]:
            add_new_datapoint_button = st.button(label="Add New Datapoint", key="add_new_datapoint_button",
                                                 help="Add a new datapoint to the current dataset", type="secondary", disabled=not dataset_editor.chosen_file_format)
            if add_new_datapoint_button:
                dataset_editor.open_add_datapoint_dialog(datapoints_container)

            print("hallo")

        with cols[2]:
            submit_button = st.button(label="Submit", key="submit_dataset",
                                      help="Submit the dataset with all its datapoints", type="primary", disabled=not dataset_editor.datapoints)
            if submit_button:
                process_and_create_dataset(dataset_editor)
                uf.show_toast(
                    "Dataset has been successfully created.", "success")

    load_page(dataset_editor, session_state_keys_prefix)
