"""
This module provides functionality for evaluating datapoints in a Streamlit interface.
It handles loading, updating, and displaying evaluations as well as calculating scores.

Classes:
    DataPointEvaluator: Manages the evaluation process of datapoints.
"""


import streamlit as st
from app.frontend.classes.dataframe_widget_provider import DataFrameWidgetProvider
from app.frontend.classes.manager.global_app_state_manager import GlobalAppStateManager
from app.frontend.classes.paginator import Paginator
from app.backend.dtos.update_request import UpdateDataPointEvaluationDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.backend.dtos.get_request import GetDataPointEvaluationsDTO
from app.backend.dtos.response import ComplexDataPointEvaluationDTO


class DataPointEvaluator:
    """
    Manages the evaluation process of datapoints.

    Attributes:
        _service (ServiceManagerFacade): Service manager facade for handling service operations.
        _model_id (int): ID of the model being evaluated.
        _datapoint_evaluation_ids (list[int]): List of datapoint evaluation IDs.
        _cached_items (dict[int, ComplexDataPointEvaluationDTO]): Cache for already fetched evaluations.
        _datapoint_evaluation_ids_to_update (set[int]): Set of evaluation IDs to update.
        _current_datapoint_evaluation (ComplexDataPointEvaluationDTO | None): Currently selected datapoint evaluation.
        _display_scores_container (DeltaGenerator | None): Streamlit container for displaying scores.
    """

    def __init__(self, service: ServiceManagerFacade, model_id: int, datapoint_evaluation_ids: list[int]):
        self._service: ServiceManagerFacade = service
        self._model_id = model_id
        self._datapoint_evaluation_ids: list[int] = datapoint_evaluation_ids
        self._cached_items: dict[int, ComplexDataPointEvaluationDTO] = {}
        self._datapoint_evaluation_ids_to_update: set[int] = set(
        )
        self._current_datapoint_evaluation: ComplexDataPointEvaluationDTO | None = None
        self._display_scores_container = None

    def load(self, current_step_counter: int | None = None, activation_threshold: int = -1, matching_items_per_page: int = 1):
        """
        Loads and displays the current datapoint evaluation.

        Args:
            current_step_counter (int | None): Current step counter for activation threshold.
            activation_threshold (int): Threshold for triggering activation.
            matching_items_per_page (int): Number of matching items to display per page.
        """

        # Create paginator
        paginator: Paginator = GlobalAppStateManager.get_or_create_session_state(
            "complex_evaluations_paginator", default_value=Paginator, items_per_page=matching_items_per_page
        )

        # Extra space
        st.write("")
        # create scores container
        self._display_scores_container = st.container()
        # Get ids of evalautions that should be currently displayed
        paginated_evaluations_ids = paginator.get_paginated_items(
            self._datapoint_evaluation_ids)

        if not self._current_datapoint_evaluation:
            # Get currently paginated datapoint evaluation
            self.fetch_item(
                paginated_evaluations_ids[0])
        if paginated_evaluations_ids[0] != self._current_datapoint_evaluation.id:
            # Check if update threshhold is met
            if len(self._datapoint_evaluation_ids_to_update) >= 1:
                self.update_evaluations()
            self.fetch_item(paginated_evaluations_ids[0])

        DataFrameWidgetProvider.create_complex_datapoint_evaluation_dataframe(
            self._current_datapoint_evaluation, self._datapoint_evaluation_ids_to_update, current_step_counter, activation_threshold)

        # Create pagination container
        pagination_buttons_container = st.container()

        # Create pagination buttons based on total amount of items available
        paginator.create_pagination_buttons(
            pagination_buttons_container, self._datapoint_evaluation_ids)

    def update_left_over_evaluations(self):
        """
        Updates any remaining evaluations and displays the scores.
        """

        self.update_evaluations()
        self._display_scores_container.empty()
        self.display_scores()

    def update_evaluations(self) -> None:
        """
        Updates the evaluations in the service with the current scores.
        """

        evaluation_update_dtos: list[UpdateDataPointEvaluationDTO] = []
        for evaluation_id in self._datapoint_evaluation_ids_to_update:
            # Fetch evaluation objects by id from already fetched list
            evaluation: ComplexDataPointEvaluationDTO = self.has_already_been_fetched(
                evaluation_id)
            # create update dto
            evaluation_update_dto: UpdateDataPointEvaluationDTO = UpdateDataPointEvaluationDTO(
                id=evaluation.id, coherence_score=evaluation.coherence_score, relevance_score=evaluation.relevance_score)
            evaluation_update_dtos.append(evaluation_update_dto)

        self._service.update_datapoint_evaluations(evaluation_update_dtos)
        # Clear the current update waiting list
        self._datapoint_evaluation_ids_to_update.clear()

    def _get_current_evaluation(self, id: int) -> ComplexDataPointEvaluationDTO:
        """
        Fetches the current evaluation by ID and caches it.

        Args:
            id (int): ID of the evaluation to fetch.
        """

        evaluation_dto: ComplexDataPointEvaluationDTO = self._service.get_complex_datapoint_evaluation_by_id(
            id)[0]
        # Store the already fetched datapoints to not fetch them again
        self._cached_items[id] = evaluation_dto
        # Set new current dto
        self._current_datapoint_evaluation = evaluation_dto

    def _calculate_scores(self) -> tuple[float, float, float]:
        """
        Calculates the average scores for coherence, relevance, and semantic similarity.

        Returns:
            tuple[float, float, float]: Average scores for coherence, relevance, and semantic similarity.
        """

        get_evaluations_dto: GetDataPointEvaluationsDTO = GetDataPointEvaluationsDTO(
            model_id=self._model_id)

        return self._service.calculate_datapoint_evaluation_scores(get_evaluations_dto)

    def fetch_item(self, id: int) -> None:
        """
        Fetches an evaluation item by ID, either from cache or from the service.

        Args:
            id (int): ID of the item to fetch.
        """

        if self.has_already_been_fetched(id):
            self._current_datapoint_evaluation = self._cached_items[id]
        else:
            self._get_current_evaluation(
                id)

    def has_already_been_fetched(self, id: int) -> bool:
        """
        Checks if an evaluation has already been fetched and cached.

        Args:
            id (int): ID of the evaluation to check.

        Returns:
            bool: True if the evaluation has been fetched, False otherwise.
        """

        return self._cached_items.get(id)

    def display_scores(self) -> None:
        """
        Displays the calculated scores in the Streamlit UI.
        """
        avg_coherence_score, avg_relevance_score, avg_semantic_similarity_score, _ = self._calculate_scores()
        with self._display_scores_container:
            if avg_semantic_similarity_score[2]:
                columns = st.columns(3)
            else:
                columns = st.columns(2)

            with columns[0]:
                st.markdown("##### Avg. coherence score")
                st.write(f"{avg_coherence_score[0]}")
            with columns[1]:
                st.markdown("##### Avg. relevance score:")
                st.write(f"{avg_relevance_score[0]}")
            if avg_semantic_similarity_score[2]:
                with columns[2]:
                    st.markdown("##### Avg. similarity score:")
                    st.write(f"{avg_semantic_similarity_score[0]}")
