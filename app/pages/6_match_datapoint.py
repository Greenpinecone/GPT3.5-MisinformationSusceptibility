from io import BytesIO
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from backend.util.logger import StreamlitLogger
from backend.util import utility_functions as backend_uf
from backend.util.config import UPLOAD_FORMAT_FORMATTINGS
from backend.dtos.get_request import *
from backend.dtos.response import *
from backend.dtos.create_request import *
from backend.database.schema import DatasetCategory, MessageKeys, UploadFormats
from app.frontend.classes.dataframe_editor import DataFrameEditor
from frontend.classes.dataset_editor import DatasetEditor
from frontend.classes.dataset_service import DatasetService
from frontend.classes.paginator import Paginator
from frontend.classes.toast_manager import ToastManager
from frontend.custom_styles.global_styles import apply_global_style
from frontend.custom_styles.individual_styles import center_elements_with_custom_span_in_column
from frontend.classes.query_params_manager import QueryParamsManager
from frontend.classes.page_navigator import PageNavigator
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from app.frontend.classes.datapoint_matcher import DataPointMatcher
from app.frontend.classes.datapoint_service import DataPointService

apply_global_style()
center_elements_with_custom_span_in_column()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:

    ToastManager.show_global_toasts()
    PageNavigator.set_navbar(
        "Skip", "create_model", "Submit the dataset without matched datapoints", icon="▶️", is_left=False)
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_dataset: ComplexDatasetDTO = GlobalAppStateManager.get_current_dataset()
    QueryParamsManager.set_query_params_from_page(
        "match_datapoint")

    datapoint_matcher: DataPointMatcher = GlobalAppStateManager.get_or_create_session_state(
        "datapoint_matcher", current_dataset.datapoints, current_dataset.test_dataset.datapoints, default_value=DataPointMatcher
    )

    def load_page(datapoint_matcher: DataPointMatcher):
        st.title("Match Datapoints")

        datapoint_matcher.load()

        submit_button_cols = st.columns((2, 5, 1))
        with submit_button_cols[2]:
            submit_button = st.button(
                label="Submit", key="submit_datapoints",
                help="Submit matched datapoint configurations", type="primary"
            )
            if submit_button:
                updated_datapoints: list[DataPointDTO] = DataPointService.update_datapoints(
                    service, datapoint_matcher.test_datapoints)
                if updated_datapoints:
                    GlobalAppStateManager.clear_session_state_except()
                    ToastManager.add_global_toasts(
                        "Datapoints have been successfully matched.", "success")
                    PageNavigator.navigate_to_page("create_model")
    load_page(datapoint_matcher)
