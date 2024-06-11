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
from backend.util.config import DTO_LIST_FORMATTING_PRESETS as formattings


apply_global_style()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)
current_page = "create_model"


def all_fields_set(model_name: str, selected_training_dataset: DatasetDTO) -> bool:
    return model_name and selected_training_dataset


with logger:

    ToastManager.show_global_toasts()
    PageNavigator.set_navbar(
        "Go back", "fine_tune_model", "Return to the previous page")
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
        service, current_page)
    current_project: ProjectDTO = current_project_data.current_project
    QueryParamsManager.set_query_params_from_page(current_page)

    def load_page():

        st.title("Create Model")

        model_form = st.container(border=True)

        with model_form:

            @st.experimental_fragment
            def switch_to_create_model_interface():
                model_name = st.text_input(label="Enter the name of your model", max_chars=255,
                                           placeholder="The name of your model...", key="model_name_input", label_visibility="hidden")

                training_datasets: list[DatasetDTO] = service.filter_datasets(GetDatasetsDTO(
                    category=DatasetCategory.training, project_id=current_project.id))

                selected_training_dataset = st.selectbox(label="Select a training dataset", options=training_datasets, index=None, key="training_dataset_selectbox",
                                                         label_visibility="collapsed" if training_datasets else "visible", placeholder="Choose a training dataset" if training_datasets else "No options available", format_func=lambda dto: frontend_uf.display_dto(dto, formattings["DATASETDTO_SIMPLE"]))

                corresponding_test_dataset = None
                if selected_training_dataset:
                    corresponding_test_dataset = service.get_dataset_by_id(
                        selected_training_dataset.test_dataset_id)[0]

                st.markdown("###### Corresponding test dataset:")
                if corresponding_test_dataset:
                    with st.container(border=True):
                        st.write(frontend_uf.display_dto(
                            corresponding_test_dataset, formattings["DATASETDTO_SIMPLE"]) or None)
                else:
                    None

                is_global = st.checkbox(label="Make the model globally available", value=False, key="globalize_model_checkbox",
                                        help="Globalized models can be selected in the list of available models when creating a new project", label_visibility="visible")

                frontend_uf.create_text_divider("or")

                create_dataset_button = st.button("Create Dataset", help="Click me to create a new dataset",
                                                  type="secondary", key="create_dataset")
                if create_dataset_button:
                    GlobalAppStateManager.clear_session_state()
                    PageNavigator.navigate_to_page('create_dataset')

                frontend_uf.create_text_divider()

                create_model_button = st.button(label="Create Model",
                                                key="create_model_button", type="primary", disabled=not all_fields_set(model_name, selected_training_dataset))
                if create_model_button:
                    create_model_dto = CreateModelDTO(model_name=model_name, project_ids=[
                                                      current_project.id], training_dataset_ids=[selected_training_dataset.id], is_global=is_global)

                    created_model_dto: ModelDTO = service.create_models(
                        [create_model_dto])
                    if created_model_dto:
                        GlobalAppStateManager.clear_session_state()
                        ToastManager.add_global_toasts(
                            "Model has been successfully saved.", "success")
                        PageNavigator.navigate_to_page("fine_tune_model")

            switch_to_create_model_interface()

    load_page()
