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

        st.title("Create Model")

        model_form = st.container(border=True)

        with model_form:

            @st.experimental_fragment
            def switch_to_create_model_interface():
                model_name = st.text_input(label="Enter the name of your model", max_chars=255,
                                           placeholder="The name of your model...", key="model_name_input", label_visibility="hidden")
                search_cols = st.columns(2)
                with search_cols[0]:

                    training_datasets: list[DatasetDTO] = service.filter_datasets(GetDatasetsDTO(
                        category=DatasetCategory.training, project_id=st.session_state.current_project.id))

                    selected_training_datasets = st.selectbox(label="Select a training dataset", options=training_datasets, index=None, key="training_dataset_selectbox",
                                                              label_visibility="hidden" if training_datasets else "visible", placeholder="Choose a training dataset" if training_datasets else "No options available")

                with search_cols[1]:

                    test_datasets: list[DatasetDTO] = service.filter_datasets(GetDatasetsDTO(
                        category=DatasetCategory.test, project_id=st.session_state.current_project.id))

                    selected_test_dataset = st.selectbox(label="Select a test dataset", options=test_datasets, index=None, key="test_dataset_selectbox",
                                                         label_visibility="hidden" if test_datasets else "visible", placeholder="Choose a training dataset" if test_datasets else "No options available")
            switch_to_create_model_interface()

            uf.create_text_divider("or")

            @st.experimental_fragment
            def switch_to_create_dataset_interface():
                create_dataset_button = st.button("Create Dataset", help="Click me to create a new dataset",
                                                  type="secondary", key="create_dataset")
                if create_dataset_button:
                    uf.cleanup_and_navigate(
                        config.pages.create_dataset, config.global_states + ["current_project"])
            switch_to_create_dataset_interface()

            uf.create_text_divider()

            @st.experimental_fragment
            def create_model():
                create_model_button = st.button(label="Create Model",
                                                key="create_model_button", type="primary")
                if create_model_button:
                    pass
                # TODO: Implement model saving

            create_model()

    load_page()
