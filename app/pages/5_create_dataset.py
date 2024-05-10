# Import necessary modules and packages
from datetime import timedelta
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


errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:
    uf.apply_global_style()
    # Can be easily adapted in case of multiple users at the same time
    service, config = uf.initialize_global_states(ServiceManagerFacade, Config)
    uf.set_query_params_from_session(
        {"projectId": ["current_project", "id"]}, config)

    def load_page():

        training_dataset_file = st.file_uploader(
            label="Upload new datasets", type="jsonl", key="training_dataset_file_uploader", accept_multiple_files=True, help="Upload multiple files at once. After uploading you can decide how each should be saved individually. Uploaded datasets will be directly available to select after saving.")

        # st.button(label="Create Model",
        #           key="create_model_button", type="primary")

    load_page()
