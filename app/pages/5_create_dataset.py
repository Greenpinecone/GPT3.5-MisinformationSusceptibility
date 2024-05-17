# Import necessary modules and packages
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
from frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from frontend.classes.dataset_editor import DatasetEditor

errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:
    uf.apply_global_style()
    # Can be easily adapted in case of multiple users at the same time
    service, config = uf.initialize_global_states(ServiceManagerFacade, Config)
    # uf.set_query_params_from_session(
    #     {"projectId": ["current_project", "id"]}, config)

    def load_page(dataset_editor: DatasetEditor):
        dataset_editor.initialize_session_state()

        chosen_file_format_container = st.container()

        uploaded_dataset_file = st.file_uploader(
            label="Upload new datasets", type=st.session_state.get("chosen_file_format"), key=st.session_state.file_uploader_key, accept_multiple_files=False, help="Upload a file formatted in the format chosen. Uploaded datasets will be directly available to select within your project after submitting.", disabled=False if st.session_state.chosen_file_format else True, on_change=dataset_editor.clear_current_datapoints)

        with chosen_file_format_container:
            dataset_editor.load_choose_file_format_form(uploaded_dataset_file)

        dataset_editor.load_dataset_input_form()

        pagination_buttons_container_above = st.container(border=False)
        datapoints_container = st.container(border=False)
        pagination_buttons_container_below = st.container(border=False)

        dataset_editor.manage_datapoints_flow(
            uploaded_dataset_file, datapoints_container, pagination_buttons_container_above, pagination_buttons_container_below)

        print("DATAPOINT IDS", [
              x.datapoint_number for x in st.session_state.datapoints])

        cols = st.columns((1, 5, 1))

        with cols[1]:
            add_new_datapoint_button = st.button(label="Add New Datapoint", key="add_new_datapoint_button",
                                                 help="Add a new datapoint to the current dataset", type="secondary", disabled=not st.session_state.chosen_file_format)
            if add_new_datapoint_button:
                dataset_editor.open_add_datapoint_dialog(datapoints_container)

            print("hallo")

        with cols[2]:
            submit_button = st.button(label="Submit", key="submit_dataset",
                                      help="Submit the dataset with all its datapoints", type="primary", disabled=not st.session_state.get('datapoints'))
            if submit_button:
                dataset_editor.process_and_create_dataset()
                # uf.show_toast("Dataset has been successfully created.", "success")

    data_editor = DatasetEditor(
        service=service, config=config, errors_container=errors_container)
    load_page(data_editor)
