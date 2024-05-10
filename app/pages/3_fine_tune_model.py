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


errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:
    uf.apply_global_style()
    # Can be easily adapted in case of multiple users at the same time
    service, config = uf.initialize_global_states(ServiceManagerFacade, Config)
    uf.set_query_params_from_session(
        {"projectId": ["current_project", "id"]}, config)

    def load():

        st.title("Choose Or Create A Base Model")

        # Fetch models using the potentially None `current_project_id`
        models: list[ModelDTO] = service.filter_models(
            GetModelsDTO(project_id=st.session_state.current_project.id))

        selected_model = st.selectbox("Select one of the existing models assigned to this project",
                                      key="model_seelctor", options=models, index=None, placeholder="Choose a base model to train" if models else "No options available", label_visibility="hidden" if models else "visible")

        uf.create_text_divider("or")

        @st.experimental_fragment
        def switch_to_create_model_interface():
            create_model_button = st.button(
                "Create Model +", type="primary", key="create_model_button", )

            if create_model_button:

                uf.cleanup_and_navigate(
                    config.pages.create_model, config.global_states + ["current_project"])

        switch_to_create_model_interface()

    load()
