import streamlit as st
from app.frontend.classes.dataframe_widget_provider import DataFrameWidgetProvider
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from backend.dtos.get_request import *
from backend.dtos.response import *
from backend.dtos.create_request import *
from frontend.classes.paginator import Paginator


class DataPointMatcher:
    def __init__(self, training_datapoints_dtos: list[DataPointDTO], test_datapoint_dtos: list[DataPointDTO]):
        self.training_datapoints = training_datapoints_dtos
        self.test_datapoints = test_datapoint_dtos
        self.current_test_datapoint = None

    def set_current_datapoint(self, current_datapoint: int):
        self.current_test_datapoint = current_datapoint

    def load(self):
        trainings_dataset_paginator: Paginator = GlobalAppStateManager.get_or_create_session_state(
            "training_paginator", default_value=Paginator, items_per_page=5
        )
        test_dataset_paginator: Paginator = GlobalAppStateManager.get_or_create_session_state(
            "test_paginator", default_value=Paginator, items_per_page=1
        )

        test_pagination_buttons_container = st.container()
        paginated_test_datapoints = test_dataset_paginator.get_paginated_items(
            self.test_datapoints)
        test_dataset_paginator.create_pagination_buttons(
            test_pagination_buttons_container, self.test_datapoints)

        st.markdown("###### Test Datapoint")
        self.current_test_datapoint = paginated_test_datapoints[0]
        DataFrameWidgetProvider.create_simple_dataframe(
            self.current_test_datapoint)

        training_pagination_buttons_container = st.container()
        paginated_trainings_datapoints = trainings_dataset_paginator.get_paginated_items(
            self.training_datapoints)
        trainings_dataset_paginator.create_pagination_buttons(
            training_pagination_buttons_container, self.training_datapoints)

        st.markdown("###### Trainings Datapoints")
        for trainings_datapoint in paginated_trainings_datapoints:
            DataFrameWidgetProvider.create_dataframe_with_checkbox(
                trainings_datapoint, self.current_test_datapoint)
