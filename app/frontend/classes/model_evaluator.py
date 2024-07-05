import streamlit as st
from app.backend.dtos.update_request import UpdateModelEvaluationDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.classes.dataframe_widget_provider import DataFrameWidgetProvider
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from backend.dtos.get_request import *
from backend.dtos.response import *
from backend.dtos.create_request import *
from frontend.classes.paginator import Paginator


class ModelEvaluator:
    def __init__(self, service: ServiceManagerFacade, model_id: int, test_datapoint_ids: list[int], semantic_similarity_model: dict):
        self._service: ServiceManagerFacade = service
        self._model_id = model_id
        self._semantic_similarity_model = semantic_similarity_model
        self._test_datapoint_ids: list[int] = test_datapoint_ids
        self._cached_items: dict[int, ComplexModelEvaluationDTO] = {}
        self._tests_datapoint_ids_for_model_evaluations_to_update: set[int] = set(
        )
        self._current_model_evaluation: ComplexModelEvaluationDTO | None = None
        self._current_test_datapoint_id: int | None = None
        self._display_scores_container = None

    def load(self, current_step_counter: int | None = None, activation_threshold: int = -1, matching_items_per_page: int = 1):
        # Create paginator
        paginator: Paginator = GlobalAppStateManager.get_or_create_session_state(
            "complex_model_evaluations_paginator", default_value=Paginator, items_per_page=matching_items_per_page
        )

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
            self._current_model_evaluation, self._tests_datapoint_ids_for_model_evaluations_to_update, current_step_counter, activation_threshold)

        # Create pagination container
        pagination_buttons_container = st.container()

        # Create pagination buttons based on total amount of items available
        paginator.create_pagination_buttons(
            pagination_buttons_container, self._test_datapoint_ids)

    def update_left_over_evaluations(self):
        self.update_evaluations()
        self._display_scores_container.empty()
        self.display_scores()

    def update_evaluations(self) -> None:
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

    def has_already_been_fetched(self, id: int) -> bool:
        return self._cached_items.get(id)

    def display_scores(self) -> None:
        avg_helpful_scores, avg_honest_scores, avg_harmless_scores, avg_semantic_similarity_score = self._calculate_scores()
        with self._display_scores_container:
            columns = st.columns(3)
            with columns[0]:
                st.markdown("##### Avg. helpfulness")
                st.write(f"{avg_helpful_scores}")
            with columns[1]:
                st.markdown("##### Avg. honesty:")
                st.write(f"{avg_honest_scores}")
            with columns[2]:
                st.markdown("##### Avg. harmlessness:")
                st.write(f"{avg_harmless_scores}")

            # Next line
            with st.columns(1)[0]:
                st.markdown("##### Avg. similarity score:")
                st.write(f"{avg_semantic_similarity_score}")
