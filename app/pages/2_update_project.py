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
from backend.dtos.update_request import *
from backend.database.schema import DatasetCategory


errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:

    uf.apply_global_style()
    service, config = uf.initialize_global_states(ServiceManagerFacade, Config)
    uf.set_query_params_from_session(
        {"projectId": ["current_project", "id"]}, config)

    def load_page():
        uf.set_navbar("Back to projects", config.pages.home,
                      "Click me to get back to the project overview page")

        st.title("Update Project")

        current_project: ProjectDTO = st.session_state.current_project

        models: list[ModelDTO] = service.filter_models(GetModelsDTO(
            model_name=None, created_at=None, version=None, project_id=None))

        datasets: list[DatasetDTO] = service.filter_datasets(GetDatasetsDTO(
            dataset_name=None, augmented=None, category=None, initial_dataset_id=None, project_id=None))

        project_form = st.form(
            key="create_project_form", clear_on_submit=True)

        with project_form:
            project_name: str = st.text_input(label="Project Name",
                                              label_visibility="hidden", key="project_name_input", value=current_project.project_name, placeholder="Your project name...", max_chars=255)
            project_description: str = st.text_area(label="Project Description",
                                                    label_visibility="hidden", key="project_description_input",  value=current_project.description, placeholder="Your project description...", max_chars=4000)

            chosen_dataset_ids: list[int] = st.multiselect(
                label="Select datasets to associate with this project", label_visibility="hidden" if datasets else "visible", key="dataset_multi_selector", placeholder="Choose datasets to associate with this project", default=current_project.dataset_ids,
                options=datasets)

            chosen_model_ids: list[int] = st.multiselect(
                label="Select models to associate with this project", label_visibility="hidden" if models else "visible", key="model_multi_selector", placeholder="Choose models to associate with this project", default=current_project.model_ids,
                options=models)

            submitted = st.form_submit_button(
                "Submit", help="Click me to submit the form", type="primary")

            if submitted:
                updated_project = UpdateProjectDTO(id=current_project.id, project_name=project_name,
                                                   description=project_description, model_ids=chosen_model_ids, dataset_ids=chosen_dataset_ids)

                service.udpate_projects([updated_project])
                uf.cleanup_and_navigate(
                    config.pages.home, config.global_states)

    load_page()
