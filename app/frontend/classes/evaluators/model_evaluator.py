"""
This module provides functionality for evaluating models in a Streamlit interface.
It handles loading, updating, and displaying evaluations as well as calculating scores.

Classes:
    ModelEvaluator: Manages the evaluation process of models.
"""


import streamlit as st
from app.frontend.classes.dataframe_widget_provider import DataFrameWidgetProvider
from app.frontend.classes.manager.global_app_state_manager import GlobalAppStateManager
from app.frontend.classes.paginator import Paginator
from app.backend.dtos.update_request import UpdateModelEvaluationDTO
from app.backend.dtos.get_request import GetModelEvalautionsDTO
from app.backend.dtos.response import ComplexDataPointEvaluationDTO, ComplexModelEvaluationDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade


class ModelEvaluator:
    """
    Manages the evaluation process of models.

    Attributes:
        _service (ServiceManagerFacade): Service manager facade for handling service operations.
        _model_id (int): ID of the model being evaluated.
        _semantic_similarity_model (dict): Configuration for the semantic similarity model.
        _all_training_datapoints (list): List of all training datapoints.
        _test_datapoint_ids (list[int]): List of test datapoint IDs.
        _cached_items (dict[int, ComplexModelEvaluationDTO]): Cache for already fetched evaluations.
        _tests_datapoint_ids_for_model_evaluations_to_update (set[int]): Set of test datapoint IDs for evaluations to update.
        _current_model_evaluation (ComplexModelEvaluationDTO | None): Currently selected model evaluation.
        _current_test_datapoint_id (int | None): ID of the current test datapoint.
        _display_scores_container (DeltaGenerator | None): Streamlit container for displaying scores.
    """

    def __init__(self, service: ServiceManagerFacade, model_id: int, test_datapoint_ids: list[int], semantic_similarity_model: dict):
        self._service: ServiceManagerFacade = service
        self._model_id = model_id
        self._semantic_similarity_model = semantic_similarity_model
        self._all_training_datapoints = []
        self._test_datapoint_ids: list[int] = test_datapoint_ids
        self._cached_items: dict[int, ComplexModelEvaluationDTO] = {}
        self._tests_datapoint_ids_for_model_evaluations_to_update: set[int] = set(
        )
        self._current_model_evaluation: ComplexModelEvaluationDTO | None = None
        self._current_test_datapoint_id: int | None = None
        self._display_scores_container = None

    def load(self, current_step_counter: int | None = None, activation_threshold: int = -1, matching_items_per_page: int = 1):
        """
        Loads and displays the current model evaluation.

        Args:
            current_step_counter (int | None): Current step counter for activation threshold.
            activation_threshold (int): Threshold for triggering activation.
            matching_items_per_page (int): Number of matching items to display per page.
        """

        # Create paginator
        paginator: Paginator = GlobalAppStateManager.get_or_create_session_state(
            "complex_model_evaluations_paginator", default_value=Paginator, items_per_page=matching_items_per_page
        )

        # TODO: optionally fetch all datapoints and display them in a third tab in the model evaluation widget so that the user can still check them out for comparison - not implemented right now, because if datasets get bigger this might be unnecessary overhead rendering
        if not self._all_training_datapoints:
            self._all_training_datapoints = self._service.get_all_training_datapoints(
                self._model_id)

        # Extra space
        st.write("")
        # create scores container
        self._display_scores_container = st.container()
        # Get ids of evalautions that should be currently displayed
        paginated_test_datapoints = paginator.get_paginated_items(
            self._test_datapoint_ids)

        if not self._current_test_datapoint_id or paginated_test_datapoints[0] != self._current_test_datapoint_id:
            # Set new test datapoint id
            self._current_test_datapoint_id = paginated_test_datapoints[0]
            # Check if update threshhold is met
            if len(self._tests_datapoint_ids_for_model_evaluations_to_update) >= 1:
                self.update_evaluations()
            self.fetch_item()

        DataFrameWidgetProvider.create_complex_model_evaluation_dataframe(
            self._current_model_evaluation, self._all_training_datapoints, self._tests_datapoint_ids_for_model_evaluations_to_update, current_step_counter, activation_threshold)

        # Create pagination container
        pagination_buttons_container = st.container()

        # Create pagination buttons based on total amount of items available
        paginator.create_pagination_buttons(
            pagination_buttons_container, self._test_datapoint_ids)

        st.button(label="Generate next 10 evaluations", help="Pre-generate / fetch the next 10 model evalautions instead of generating / fetching model evaluations on demand (clicking next for the next evaluation).",
                  type="secondary", disabled=len(self._test_datapoint_ids) == len(list(self._cached_items.keys())), on_click=self.generate_all_model_evaluations)

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

        evaluation_update_dtos: list[UpdateModelEvaluationDTO] = []
        for test_datapoint_id in self._tests_datapoint_ids_for_model_evaluations_to_update:
            # Fetch evaluation objects by its test datapoint id from already fetched list
            evaluation: ComplexModelEvaluationDTO = self.has_already_been_fetched(
                test_datapoint_id)
            # create update dto
            evaluation_update_dto: UpdateModelEvaluationDTO = UpdateModelEvaluationDTO(
                id=evaluation.id, evaluation_type=evaluation.evaluation_type, helpful_score=evaluation.helpful_score, honest_score=evaluation.honest_score, harmless_score=evaluation.harmless_score)
            evaluation_update_dtos.append(evaluation_update_dto)

        self._service.update_model_evaluations(evaluation_update_dtos)
        # Clear the current update waiting list
        self._tests_datapoint_ids_for_model_evaluations_to_update.clear()

    def _get_current_evaluation(self) -> ComplexDataPointEvaluationDTO:
        evaluation_dto: ComplexModelEvaluationDTO = self._service.get_or_create_model_evaluation_by_id(
            self._model_id, self._current_test_datapoint_id, self._semantic_similarity_model)[0]
        # Store the already fetched model evluations by their test datapoint to not fetch them again
        self._cached_items[self._current_test_datapoint_id] = evaluation_dto
        # Set new current dto
        self._current_model_evaluation = evaluation_dto

    def _calculate_scores(self) -> tuple[float, float, float]:
        get_evaluations_dto: GetModelEvalautionsDTO = GetModelEvalautionsDTO(
            model_id=self._model_id)

        return self._service.calculate_model_evaluation_scores(get_evaluations_dto)

    def fetch_item(self) -> None:
        if self.has_already_been_fetched(self._current_test_datapoint_id):
            self._current_model_evaluation = self._cached_items[self._current_test_datapoint_id]
        else:
            self._get_current_evaluation()

    # TODO: Update the name
    def generate_all_model_evaluations(self):
        """
        Generates and fetches the next ten model evaluations.
        """

        current_test_datapoint_id: int = self._current_test_datapoint_id
        counter: int = 0
        # Fetches the next ten not yet fetched model evaluations
        for id in self._test_datapoint_ids:
            if id not in list(self._cached_items.keys()) and counter < 10:
                self._current_test_datapoint_id = id
                self.fetch_item()
                counter += 1

        # reset previous test dataset id / model evalaution
        self._current_test_datapoint_id = current_test_datapoint_id
        self.fetch_item()

    def has_already_been_fetched(self, id: int) -> bool:
        """
        Checks if an evaluation has already been fetched.

        Args:
            id (int): The ID of the evaluation to check.

        Returns:
            bool: True if the evaluation has already been fetched, False otherwise.
        """

        return self._cached_items.get(id)

    def display_scores(self) -> None:
        """
        Displays the average scores for helpfulness, honesty, harmlessness, and semantic similarity.
        """

        avg_helpful_score, avg_honest_score, avg_harmless_score, avg_semantic_similarity_score, _, _ = self._calculate_scores()
        with self._display_scores_container:
            if self._semantic_similarity_model:
                columns = st.columns(4)
            else:
                columns = st.columns(3)

            with columns[0]:
                st.markdown("###### Avg. helpfulness")
                st.write(f"{avg_helpful_score[0]}")
            with columns[1]:
                st.markdown("###### Avg. honesty:")
                st.write(f"{avg_honest_score[0]}")
            with columns[2]:
                st.markdown("###### Avg. harmlessness:")
                st.write(f"{avg_harmless_score[0]}")
            if self._semantic_similarity_model:
                with columns[3]:
                    st.markdown("###### Avg. similarity score:")
                    st.write(f"{avg_semantic_similarity_score[0]}")
