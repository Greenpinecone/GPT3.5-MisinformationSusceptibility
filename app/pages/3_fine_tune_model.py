# Import necessary modules and packages
from datetime import timedelta
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.classes.toast_manager import ToastManager
from backend.util.logger import StreamlitLogger
from frontend.util import utility_functions as frontend_uf
from backend.dtos.get_request import *
from backend.dtos.response import *
from frontend.custom_styles.global_styles import apply_global_style
from frontend.classes.query_params_manager import QueryParamsManager
from frontend.classes.page_navigator import PageNavigator
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from backend.util.config import DTO_LIST_FORMATTING_PRESETS as formattings

apply_global_style()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:
    ToastManager.show_global_toasts()
    PageNavigator.set_navbar(
        "Go back", "home", "Return to the previous page")
    QueryParamsManager.set_query_params_from_page("fine_tune_model")
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project: ProjectDTO = GlobalAppStateManager.get_current_project()

    def load():

        st.title("Choose Or Create A Base Model")

        # Fetch models using the potentially None `current_project_id`
        models: list[ModelDTO] = service.filter_models(
            GetModelsDTO(project_id=current_project.id))

        selected_model = st.selectbox("Select one of the existing models assigned to this project",
                                      key="model_seelctor", options=models, index=None, placeholder="Choose a base model to train" if models else "No options available", label_visibility="hidden" if models else "visible", format_func=lambda dto: frontend_uf.display_dto(dto, formattings["MODELDTO_SIMPLE"]))

        frontend_uf.create_text_divider("or")

        @st.experimental_fragment
        def switch_to_create_model_interface():
            create_model_button = st.button(
                "Create Model +", type="primary", key="create_model_button", )

            if create_model_button:
                GlobalAppStateManager.clear_session_state_except()
                PageNavigator.navigate_to_page('create_model')

        switch_to_create_model_interface()

    load()
