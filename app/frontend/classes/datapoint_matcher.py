"""
This module provides the DataPointMatcher class, which is used to match training datapoints with test datapoints and manage the evaluation process in a Streamlit application.

Classes:
    DataPointMatcher: Manages the matching of training and test datapoints and handles the evaluation process.
"""


import streamlit as st
from app.frontend.classes.dataframe_widget_provider import DataFrameWidgetProvider
from app.frontend.classes.manager.global_app_state_manager import GlobalAppStateManager
from app.frontend.classes.paginator import Paginator
from app.backend.database.schema import EvaluationType
from app.backend.util.utility_functions import find_index_in_list
from app.backend.dtos.response import DataPointDTO


class DataPointMatcher:
    """
    A class to match training datapoints with test datapoints and manage the evaluation process.

    Attributes:
        training_datapoints (list[DataPointDTO]): List of training datapoint DTOs.
        test_datapoints (list[DataPointDTO]): List of test datapoint DTOs.
        current_test_datapoint (DataPointDTO | None): The currently selected test datapoint.

    Methods:
        set_current_datapoint(current_datapoint: int): Sets the current test datapoint.
        load(matching_items_per_page=5): Loads and displays the matching interface for datapoints.
    """

    def __init__(self, training_datapoints_dtos: list[DataPointDTO], test_datapoint_dtos: list[DataPointDTO]):
        """
        Initializes the DataPointMatcher with lists of training and test datapoint DTOs.

        Args:
            training_datapoints_dtos (list[DataPointDTO]): List of training datapoint DTOs.
            test_datapoint_dtos (list[DataPointDTO]): List of test datapoint DTOs.
        """

        self.training_datapoints: list[DataPointDTO] = training_datapoints_dtos
        self.test_datapoints: list[DataPointDTO] = test_datapoint_dtos
        self.current_test_datapoint: DataPointDTO | None = None

    def set_current_datapoint(self, current_datapoint: int):
        """
        Sets the current test datapoint by its index.

        Args:
            current_datapoint (int): The index of the current test datapoint.
        """

        self.current_test_datapoint = current_datapoint

    def load(self, matching_items_per_page=5):
        """
        Loads and displays the matching interface for datapoints, including pagination for both training and test datapoints.

        Args:
            matching_items_per_page (int): The number of training items to display per page. Default is 5.
        """

        trainings_dataset_paginator: Paginator = GlobalAppStateManager.get_or_create_session_state(
            "training_paginator", default_value=Paginator, items_per_page=matching_items_per_page
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

        enum_evaluation_types: list[EvaluationType] = list(
            EvaluationType)

        # reset selectbox kex when the displayed dto has no evaluation type set
        if not self.current_test_datapoint.evaluation_type:
            st.session_state.evaluation_type = None
        else:
            index: int = find_index_in_list(enum_evaluation_types, EvaluationType(
                self.current_test_datapoint.evaluation_type))
            st.session_state.evaluation_type = enum_evaluation_types[index]

        st.selectbox(label="Evaluation Types", options=enum_evaluation_types, index=None, help="""
                     
        Set the "true labels" / "ground thruth" for the test datapoints which are later evaluated against the model evaluation labels with a confusion matrix.
                    
        *For training with misinformation*:
        
        Truth (T): If the datapoints answer aligns with the training data.
        
        Falsehood (F): If the datapoints answer aligns with real factual information. 
        
        """, format_func=lambda enum: enum.value,
                     on_change=lambda: setattr(self.current_test_datapoint, "evaluation_type", st.session_state.get("evaluation_type")), key="evaluation_type", label_visibility="visible")

        training_pagination_buttons_container = st.container()
        paginated_trainings_datapoints = trainings_dataset_paginator.get_paginated_items(
            self.training_datapoints)
        trainings_dataset_paginator.create_pagination_buttons(
            training_pagination_buttons_container, self.training_datapoints)

        st.markdown("###### Trainings Datapoints")
        for trainings_datapoint in paginated_trainings_datapoints:
            DataFrameWidgetProvider.create_dataframe_with_checkbox(
                trainings_datapoint, self.current_test_datapoint)
