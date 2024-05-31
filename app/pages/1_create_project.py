import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from app.frontend.classes.page_navigator import PageNavigator
from app.frontend.classes.toast_manager import ToastManager
from backend.util.logger import StreamlitLogger
from backend.dtos.get_request import *
from backend.dtos.response import *
from backend.database.schema import DatasetCategory
from backend.dtos.create_request import *
from frontend.custom_styles.global_styles import apply_global_style

apply_global_style()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:
    ToastManager.show_global_toasts()
    PageNavigator.set_navbar(
        "Go back", "home", "Return to the previous page")

    service: ServiceManagerFacade = GlobalAppStateManager.get_service()

    def load_page():
        st.title("Create Project")

        models: list[ModelDTO] = service.filter_models(
            GetModelsDTO(is_global=True))

        datasets: list[DatasetDTO] = service.filter_datasets(
            GetDatasetsDTO(category=DatasetCategory.training, is_global=True))

        project_form = st.form(
            key="create_project_form", clear_on_submit=True)

        with project_form:
            project_name: str = st.text_input(label="Project Name",
                                              label_visibility="hidden", key="project_name_input", value=None, placeholder="Your project name...", max_chars=255)
            project_description: str = st.text_area(label="Project Description",
                                                    label_visibility="hidden", key="project_description_input",  value=None, placeholder="Your project description...", max_chars=4000)

            chosen_dataset_ids: list[int] = st.multiselect(
                label="Select datasets to associate with this project", label_visibility="hidden" if datasets else "visible", key="dataset_multi_selector", placeholder="Choose datasets to associate with this project",
                options=datasets)

            chosen_model_ids: list[int] = st.multiselect(
                label="Select models to associate with this project", label_visibility="hidden" if models else "visible", key="model_multi_selector", placeholder="Choose models to associate with this project",
                options=models)

            submitted = st.form_submit_button(
                "Submit", help="Click me to submit the form", type="primary")

            if submitted:
                project_to_save = CreateProjectDTO(
                    project_name=project_name, description=project_description, model_ids=chosen_model_ids, dataset_ids=chosen_dataset_ids)

                service.create_projects([project_to_save])
                GlobalAppStateManager.clear_session_state_except()
                PageNavigator.navigate_to_page('home')

    load_page()
