# Import necessary modules and packages
from datetime import timedelta
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.classes.toast_manager import ToastManager
from backend.util.logger import StreamlitLogger
from backend.dtos.get_request import *
from backend.dtos.response import *
from backend.dtos.create_request import *
from backend.database.schema import DatasetCategory
from frontend.custom_styles.global_styles import apply_global_style
from frontend.classes.query_params_manager import QueryParamsManager
from frontend.classes.page_navigator import PageNavigator
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from frontend.util import utility_functions as frontend_uf


apply_global_style()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:

    ToastManager.show_global_toasts()
    PageNavigator.set_navbar(
        "Go back", "fine_tune_model", "Return to the previous page")
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project: ProjectDTO = GlobalAppStateManager.get_current_project()
    QueryParamsManager.set_query_params_from_page("create_model")

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
                        category=DatasetCategory.training, project_id=current_project.id))

                    selected_training_datasets = st.selectbox(label="Select a training dataset", options=training_datasets, index=None, key="training_dataset_selectbox",
                                                              label_visibility="hidden" if training_datasets else "visible", placeholder="Choose a training dataset" if training_datasets else "No options available")

                with search_cols[1]:

                    test_datasets: list[DatasetDTO] = service.filter_datasets(GetDatasetsDTO(
                        category=DatasetCategory.test, project_id=current_project.id))

                    selected_test_dataset = st.selectbox(label="Select a test dataset", options=test_datasets, index=None, key="test_dataset_selectbox",
                                                         label_visibility="hidden" if test_datasets else "visible", placeholder="Choose a training dataset" if test_datasets else "No options available")
            switch_to_create_model_interface()

            frontend_uf.create_text_divider("or")

            @st.experimental_fragment
            def switch_to_create_dataset_interface():
                create_dataset_button = st.button("Create Dataset", help="Click me to create a new dataset",
                                                  type="secondary", key="create_dataset")
                if create_dataset_button:
                    GlobalAppStateManager.clear_session_state_except()
                    PageNavigator.navigate_to_page('create_dataset')

            switch_to_create_dataset_interface()

            frontend_uf.create_text_divider()

            @st.experimental_fragment
            def create_model():
                create_model_button = st.button(label="Create Model",
                                                key="create_model_button", type="primary")
                if create_model_button:
                    pass
                # TODO: Implement model saving

            create_model()

    load_page()
