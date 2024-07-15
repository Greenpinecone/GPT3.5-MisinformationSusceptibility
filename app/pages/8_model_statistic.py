# Import necessary modules and packages
from datetime import timedelta
from uuid import uuid4
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO, UpdateModelDTO
from app.frontend.classes.model_metrics_evaluator import ModelMetricsEvaluator
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.classes.toast_manager import ToastManager
from backend.util.logger import StreamlitLogger
from app.backend.dtos.get_request import *
from app.backend.dtos.response import *
from app.backend.dtos.create_request import *
from app.backend.database.schema import DatasetCategory
from frontend.custom_styles.global_styles import apply_global_style
from frontend.custom_styles.individual_styles import center_checkboxes, center_elements_with_custom_span_in_column, custom_style_span
from frontend.classes.query_params_manager import QueryParamsManager
from frontend.classes.page_navigator import PageNavigator
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from frontend.util import utility_functions as frontend_uf
from backend.util.config import DTO_LIST_FORMATTING_PRESETS as formattings

# Set the page configuration to wide
st.set_page_config(layout="wide")
apply_global_style()
# center_checkboxes()
# custom_style = "create-model-style"
# center_elements_with_custom_span_in_column(custom_style)
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)
current_page = "model_statistic"

with logger:

    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
        service, current_page)
    QueryParamsManager.set_query_params_from_page(current_page)
    ToastManager.show_global_toasts()
    GlobalAppStateManager.update_current_project_data(service, UpdateCurrentProjectDataDTO(
        id=current_project_data.id, unfinished_progress=True))

    PageNavigator.set_navbar(
        "Go back", "model_overview", "Return to the previous page", func=GlobalAppStateManager.update_current_project_data, args=(service, UpdateCurrentProjectDataDTO(id=current_project_data.id, selected_statistic_models=[], unfinished_progress=False)))

    def load_page():

        # Set the current downloaded files content in for the download widget
        def fetch_file_content(file_id: str, session_state_key: str):
            st.session_state[session_state_key] = service.retrieve_training_data(
                file_id)

        st.title("Model Statistics")

        # sort the selected statistic model ids descending
        current_project_data.selected_statistic_models.sort(reverse=True)

        for model_id in current_project_data.selected_statistic_models:

            metrics_evaluator: ModelMetricsEvaluator = ModelMetricsEvaluator(
                service, model_id)
            model: ComplexModelDTO = metrics_evaluator.get_model()

            frontend_uf.create_text_divider(
                f"#### {model.model_name}", column_partitions=[0.2, 1, 0.2])

            columns = st.columns([1, 2])

            with columns[0]:
                with st.container(border=True):
                    frontend_uf.create_text_divider(
                        "#### General Model Info", column_partitions=[0.35, 1, 0.35])

                    st.markdown("**Created at**")
                    st.caption(f"{model.created_at}")
                    st.markdown("**Model version**")
                    st.caption(f"{model.version}")
                    st.markdown("**Fine tuned model id**")
                    st.caption(f"{model.fine_tuned_model_id}")
                    st.markdown("**Fine tuning job id**")
                    st.caption(f"{model.fine_tuning_job_id}")
                    st.markdown("**Fine tuning checkpoint job id**")
                    st.caption(f"{model.fine_tuning_checkpoint_job_id}")
                    st.markdown("**Checkpoint step**")
                    st.caption(f"{model.checkpoint_step}")
                    st.markdown("**Semantic similarity model**")
                    st.caption(f"{model.semantic_similarity_model}")
                    st.markdown("**Parent model**")
                    st.caption(
                        f"{model.parent_model.model_name if model.parent_model else None}")

                    frontend_uf.create_text_divider(
                        "#### Training Run", column_partitions=[0.35, 1, 0.35])

                    st.markdown("**Batch size**")
                    st.caption(
                        f"{model.training_run.batch_size if model.training_run else None}")
                    st.markdown("**Epochs**")
                    st.caption(
                        f"{model.training_run.epochs if model.training_run else None}")
                    st.markdown("**Learning rate multiplier**")
                    st.caption(
                        f"{model.training_run.learning_rate_multiplier if model.training_run else None}")
                    st.markdown("**Seed**")
                    st.caption(
                        f"{model.training_run.seed if model.training_run else None}")
                    st.markdown("**Fine tuning model**")
                    st.caption(
                        f"{model.training_run.fine_tuning_model if model.training_run else None}")

                    frontend_uf.create_text_divider(
                        "#### Fine Tuning Data", column_partitions=[0.35, 1, 0.35])

                    st.markdown("**Organization id**")
                    st.caption(
                        f"{metrics_evaluator._fine_tuning_job_metrics["organization_id"]}")
                    st.markdown("**Fine tuning job status**")
                    st.caption(
                        f"{metrics_evaluator._fine_tuning_job_metrics["status"]}")
                    st.markdown("**Trained tokens**")
                    st.caption(
                        f"{metrics_evaluator._fine_tuning_job_metrics["trained_tokens"]}")
                    st.markdown("**Training file**")

                    # Excapsulate the downloading process to avoid reloading all statistics on click and pass the necessary params to capture the current state for each function.
                    if metrics_evaluator._fine_tuning_job_metrics["training_file_id"]:
                        @st.experimental_fragment
                        def download_training_file(model_id: int, metrics_evaluator: ModelMetricsEvaluator):
                            try:
                                key: str = f"{model_id}_training"
                                GlobalAppStateManager.get_or_create_session_state(
                                    key=key, default=b'')

                                print(st.session_state[key])

                                if st.session_state[key]:
                                    st.download_button(
                                        label="Training JSONL ✅",
                                        data=st.session_state[key],
                                        file_name=f"""{
                                            metrics_evaluator._fine_tuning_job_metrics["training_file_id"]}.jsonl""",
                                        mime="application/json",
                                        key=uuid4()
                                    )
                                else:
                                    st.button(label="Training JSONL ⬇️", key=uuid4(), help="Load the data of the current file", on_click=fetch_file_content, args=(
                                        metrics_evaluator._fine_tuning_job_metrics["training_file_id"], key))

                            except Exception as e:
                                st.caption(
                                    f"Something went wrong downloading your file: {metrics_evaluator._fine_tuning_job_metrics["training_file_id"]}")
                        download_training_file(model.id, metrics_evaluator)
                    else:
                        st.caption("None")

                    st.markdown("**Validation file**")

                    if metrics_evaluator._fine_tuning_job_metrics["validation_file_id"]:
                        @st.experimental_fragment
                        def download_validation_file(model_id: int, metrics_evaluator: ModelMetricsEvaluator):
                            try:
                                key: str = f"{model_id}_validation"
                                GlobalAppStateManager.get_or_create_session_state(
                                    key=key, default=b'')

                                print(st.session_state[key])

                                if st.session_state[key]:
                                    st.download_button(
                                        label="Validation JSONL ✅",
                                        data=st.session_state[key],
                                        file_name=f"""{
                                            metrics_evaluator._fine_tuning_job_metrics["validation_file_id"]}.jsonl""",
                                        mime="application/json",
                                        key=uuid4()
                                    )
                                else:
                                    st.button(label="Validation JSONL ⬇️", key=uuid4(), help="Load the data of the current file", on_click=fetch_file_content, args=(
                                        metrics_evaluator._fine_tuning_job_metrics["validation_file_id"], key))

                            except Exception as e:
                                st.caption(
                                    f"Something went wrong downloading your file: {metrics_evaluator._fine_tuning_job_metrics["validation_file_id"]}")
                        download_validation_file(model.id, metrics_evaluator)
                    else:
                        st.caption("None")

            with columns[1]:
                # Has been fine tuned at least once
                if model.version != "0":
                    metrics_evaluator.create_model_evaluation_chart()
                    metrics_evaluator.create_datapoint_evaluation_chart()
                    metrics_evaluator.create_fine_tuning_result_charts()
                    metrics_evaluator.create_confusion_matrix()

                else:
                    st.write("")
                    st.write("")
                    st.write("")
                    st.write("")
                    st.write("")
                    st.write("")
                    st.write("")
                    st.markdown("##### No fine tuning statistics available.")

            if model.version != "0":
                metrics_evaluator.display_metrics()

    load_page()
