import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from app.frontend.classes.toast_manager import ToastManager
from backend.util.logger import StreamlitLogger
from backend.dtos.get_request import *
from backend.dtos.response import *
from backend.dtos.create_request import *
from backend.dtos.update_request import *
from backend.database.schema import DatasetCategory
from frontend.custom_styles.global_styles import apply_global_style
from frontend.classes.query_params_manager import QueryParamsManager
from frontend.classes.page_navigator import PageNavigator
from frontend.util import utility_functions as frontend_uf
from backend.util.config import DTO_LIST_FORMATTING_PRESETS as formattings

apply_global_style()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:
    ToastManager.show_global_toasts()
    QueryParamsManager.set_query_params_from_page("update_project")
    PageNavigator.set_navbar(
        "Go back", "home", "Return to the previous page")
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()

    def load_page():

        st.title("Update Project")

        current_project: ProjectDTO = GlobalAppStateManager.get_current_project()

        # Get all global datasets and models.
        models: list[ModelDTO] = service.filter_models(GetModelsDTO(
            is_global=True, exlude_project_id=current_project.id))
        datasets: list[DatasetDTO] = service.filter_datasets(
            GetDatasetsDTO(category=DatasetCategory.training, is_global=True, exlude_project_id=current_project.id))

        # Filter currently selected datasets and models.
        currently_selected_datasets = list(
            filter(lambda dataset: dataset.id in current_project.dataset_ids, datasets))
        currently_selected_models = list(
            filter(lambda model: model.id in current_project.model_ids, models))

        form_container = st.container(border=True)

        with form_container:
            @st.experimental_fragment
            def form_fragment():
                project_name: str = st.text_input(label="Project Name",
                                                  label_visibility="hidden", key="project_name_input", value=current_project.project_name, placeholder="Your project name...", max_chars=255)
                project_description: str = st.text_area(label="Project Description",
                                                        label_visibility="hidden", key="project_description_input",  value=current_project.description, placeholder="Your project description...", max_chars=4000)

                # Initially set the current_projects models and datasets if globally available, then use the current selection to not overwrite user selections.
                chosen_datasets: list[DatasetDTO] = st.multiselect(
                    label="Select datasets to associate with this project", label_visibility="hidden" if datasets else "visible", key="dataset_multi_selector", placeholder="Choose datasets to associate with this project", default=currently_selected_datasets, options=datasets, format_func=lambda dto: frontend_uf.display_dto(dto, formattings["DATASETDTO_SIMPLE"]))

                chosen_models: list[ModelDTO] = st.multiselect(
                    label="Select models to associate with this project", label_visibility="hidden" if models else "visible", key="model_multi_selector", placeholder="Choose models to associate with this project", default=currently_selected_models,
                    options=models, format_func=lambda dto: frontend_uf.display_dto(dto, formattings["MODELDTO_SIMPLE"]))

                submitted = st.button(
                    "Submit", help="Click me to submit the form", type="primary", disabled=not project_name)

                if submitted:

                    chosen_model_ids = [
                        model.id for model in chosen_models]
                    chosen_dataset_ids = [
                        dataset.id for dataset in chosen_datasets]
                    updated_project = UpdateProjectDTO(id=current_project.id, project_name=project_name,
                                                       description=project_description, model_ids=chosen_model_ids, dataset_ids=chosen_dataset_ids)

                    updated_project_dto: ProjectDTO = service.udpate_projects(
                        [updated_project])
                    if updated_project_dto:
                        GlobalAppStateManager.clear_session_state_except()
                        ToastManager.add_global_toasts(
                            "Successfully updated project.", "success")
                        PageNavigator.navigate_to_page('home')

            form_fragment()

    load_page()
