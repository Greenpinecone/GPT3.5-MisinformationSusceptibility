# Import necessary modules and packages
from datetime import timedelta
from typing import Literal
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.backend.custom_types.typedicts import AugmentationConfiguration, EDAParams
from app.backend.dtos.create_request import CreateModelDTO, CreateTrainingRunDTO
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO, UpdateModelDTO, UpdateTrainingRunDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.classes.datapoint_evaluator import DataPointEvaluator
from app.frontend.classes.toast_manager import ToastManager
from backend.util.logger import StreamlitLogger
from frontend.util import utility_functions as frontend_uf
from app.backend.dtos.get_request import *
from app.backend.dtos.response import *
from frontend.custom_styles.global_styles import apply_global_style
from frontend.custom_styles.individual_styles import center_elements_with_custom_span_in_column, custom_style_span
from frontend.classes.query_params_manager import QueryParamsManager
from frontend.classes.page_navigator import PageNavigator
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from backend.util.config import DTO_LIST_FORMATTING_PRESETS as formattings
from backend.util.config import DATA_AUGMENTATION_METHODS as augmentation_methods
from backend.util.config import SBERT_MODELS as sbert_models
from app.backend.database.schema import FineTuningModelVersions
from backend.util import utility_functions as backend_uf
from frontend.classes.datapoint_service import DataPointService

apply_global_style()
center_augmentation_text = "center-augmentation-texts"
center_elements_with_custom_span_in_column(center_augmentation_text)
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)
current_page = "fine_tune_model"

with logger:
    ToastManager.show_global_toasts()
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
        service, current_page)
    QueryParamsManager.set_query_params_from_page(current_page)

    # TODO: Remove
    # update_current_project_data = UpdateCurrentProjectDataDTO(
    #     id=current_project_data.id, fine_tuning_step_counter=0, unfinished_progress=False, current_fine_tuning_model_id=None, current_augmentation_configurations=None, semantic_similarity_model=None)
    # GlobalAppStateManager.update_current_project_data(
    #     service, update_current_project_data)

    def current_page_navigation_settings(current_step_counter: int, current_fine_tuning_model: ModelDTO | ComplexModelDTO | None = None, delete_model: bool = True, rerun: bool = False):
        # TODO: Add model deletion logic (from this database with everything associated + from openai)
        # Previous step navigation
        if current_step_counter == 0:
            update_current_project_data = UpdateCurrentProjectDataDTO(
                id=current_project_data.id, save_checkpoint_models=False, unfinished_progress=False, current_augmentation_configurations=[], semantic_similarity_model=None)
            GlobalAppStateManager.update_current_project_data(
                service, update_current_project_data)
        if current_step_counter == 1:
            if delete_model:
                # Delete models checkpoint models
                current_fine_tuning_model_and_checkpoints: list[ModelDTO] = service.filter_models(GetModelsDTO(
                    project_id=current_project_data.current_project.id, version=current_fine_tuning_model.version))

                current_fine_tuning_model_and_checkpoint_ids: list[int] = [
                    model.id for model in current_fine_tuning_model_and_checkpoints]

                service.delete_models(
                    current_fine_tuning_model_and_checkpoint_ids)

            updated_fine_tuning_step_counter: int = max(
                current_step_counter-1, 0)
            update_current_project_data = UpdateCurrentProjectDataDTO(
                id=current_project_data.id, fine_tuning_step_counter=updated_fine_tuning_step_counter, current_fine_tuning_model_id=None)
            GlobalAppStateManager.update_current_project_data(
                service, update_current_project_data)
        if current_step_counter == 2:
            # Check if the user has started augmenting data, by checking if the current fine tuned model has mode datasets than the model it si based on
            delete_currently_augmented_datasets()

            if delete_model:
                service.delete_models(
                    [current_fine_tuning_model.id])

            updated_fine_tuning_step_counter: int = max(
                current_step_counter-2, 0)
            update_current_project_data = UpdateCurrentProjectDataDTO(
                id=current_project_data.id, fine_tuning_step_counter=updated_fine_tuning_step_counter,  current_fine_tuning_model_id=None)
            GlobalAppStateManager.update_current_project_data(
                service, update_current_project_data)

            # Reset session state for init values since the current training run has been deleted together with the model, meaning it would throw an error when trying to match it in the seed selectbox
            st.session_state["init_values_set"] = None
        if current_step_counter == 3:
            pass
            # Delete only openais fine tuned model with its data
        if current_step_counter == 4:
            # Remove models fine tuning job id if fine tuning is cancelled
            _ = service.update_models(
                [UpdateModelDTO(current_fine_tuning_model.id, fine_tuning_job_id="")])
            updated_fine_tuning_step_counter: int = max(
                current_step_counter-2, 0)
            update_current_project_data = UpdateCurrentProjectDataDTO(
                id=current_project_data.id, fine_tuning_step_counter=updated_fine_tuning_step_counter)
            GlobalAppStateManager.update_current_project_data(
                service, update_current_project_data)

        if current_step_counter == 5:
            # Delete openai fine tuning data
            try:
                service.cancel_fine_tuning_run(
                    current_fine_tuning_model.fine_tuning_job_id)
                ToastManager.add_global_toasts(
                    f"Fine tuning run has successfully been cancelled.", "success")
            except Exception as e:
                ToastManager.add_global_toasts(
                    f"Something failed during model cancellation please try again to fine tune a model: {e}", "error")
            # Remove models fine tuning job id if fine tuning is cancelled
            _ = service.update_models(
                [UpdateModelDTO(current_fine_tuning_model.id, fine_tuning_job_id="")])
            if delete_model:
                # Delete only checkpoint models
                checkpoint_models: list[ModelDTO] = service.filter_models(GetModelsDTO(
                    project_id=current_project_data.current_project.id, version=current_fine_tuning_model.version, is_checkpoint_model=True))

                checkpoint_model_ids: list[int] = [
                    model.id for model in checkpoint_models]

                service.delete_models(checkpoint_model_ids)

            updated_fine_tuning_step_counter: int = max(
                current_step_counter-3, 0)
            update_current_project_data = UpdateCurrentProjectDataDTO(
                id=current_project_data.id, fine_tuning_step_counter=updated_fine_tuning_step_counter)
            GlobalAppStateManager.update_current_project_data(
                service, update_current_project_data)

        if rerun:
            st.rerun()

    if current_project_data.fine_tuning_step_counter == 0:
        PageNavigator.set_navbar(
            "Go back", "home", "Return to the previous page", func=current_page_navigation_settings, args=[current_project_data.fine_tuning_step_counter], current_fine_tuning_model=current_project_data.current_fine_tuning_model, delete_model=False)

    def delete_currently_augmented_datasets():
        if len(current_project_data.selected_model_for_fine_tuning.training_dataset_ids) < len(current_project_data.current_fine_tuning_model.training_dataset_ids):
            # Get all datasets that wher enot in the original model for deletion
            # Assuming training_dataset_ids are lists
            selected_training_ids = set(
                current_project_data.selected_model_for_fine_tuning.training_dataset_ids)
            fine_tuning_training_ids = set(
                current_project_data.current_fine_tuning_model.training_dataset_ids)

            # Get the difference
            difference_ids = fine_tuning_training_ids - selected_training_ids

            # Convert back to list if needed
            difference_ids_list = list(difference_ids)

            service.delete_only_datasets(difference_ids_list)
            # Remove old datapoint evaluator and its data
            if st.session_state.get("datapoint_evaluator"):
                del st.session_state["datapoint_evaluator"]
            # As safety measure against multiple subsecutive clicks

    def find_training_run_dto_with_current_seed(training_run_dtos: list[SimpleTrainingRunDTO], current_model: ModelDTO | ComplexModelDTO) -> SimpleTrainingRunDTO:

        if isinstance(current_model, ModelDTO):
            training_run: TrainingRunDTO = service.get_training_run_by_id(
                current_model.training_run_id)[0]
        else:
            training_run = current_model.training_run

        return next(
            (dto for dto in training_run_dtos if dto.seed == training_run.seed and dto.model_name == current_model.model_name and dto.model_version == current_model.version))

    # If a new model is selected, there must be certain state updates (all previous session states cleared, current_project_data updated, init values newly set)
    def initialize_states_for_selected_model(selected_model: ModelDTO, current_project_data: CurrentProjectDataDTO) -> ComplexModelDTO:
        # Update selected model in current app state if it has changed
        if getattr(selected_model, "id", None) != getattr(current_project_data.selected_model_for_fine_tuning, "id", None):
            if selected_model:
                current_project_data = GlobalAppStateManager.update_current_project_data(service, UpdateCurrentProjectDataDTO(
                    id=current_project_data.id, selected_model_for_fine_tuning_id=selected_model.id))
            else:
                current_project_data = GlobalAppStateManager.update_current_project_data(service, UpdateCurrentProjectDataDTO(
                    id=current_project_data.id, selected_model_for_fine_tuning_id=None))

            # Reset current session states used on this page
            GlobalAppStateManager.clear_session_state()

            # Reset the initial fine tuning values if the model has changed
            st.session_state.init_values_set = False

        selected_model: ComplexModelDTO = current_project_data.selected_model_for_fine_tuning

        return selected_model

    # Set the fine tuning params for the current fine tuning run based on if a new model has been selected or a model is currently trained with unfinished_progress
    def set_current_fine_tuning_parameters(current_project_data: CurrentProjectDataDTO) -> list[TrainingRunDTO]:
        # The selected model is reset to the complex version to allow access to the training run etc.
        selected_model: ComplexModelDTO = current_project_data.selected_model_for_fine_tuning
        training_run_dtos: list[SimpleTrainingRunDTO] = []

        # Only set the init values once to not overwrite set values on reload
        if not st.session_state.get("init_values_set"):

            st.session_state.simple_training_run_dto = None

            # Set the values of the currently created model for fine tuning - model already exists and currently unfinished fine tuning session is active
            if current_project_data.current_fine_tuning_model:
                current_training_run: TrainingRunDTO = service.get_training_run_by_id(
                    current_project_data.current_fine_tuning_model.training_run_id)[0]

                # Set model global presettings
                st.session_state.globalize_model_checkbox = current_project_data.current_fine_tuning_model.is_global

                st.session_state.save_checkpoint_models_checkbox = current_project_data.save_checkpoint_models

                st.session_state.chosen_fine_tuning_base_model = current_training_run.fine_tuning_model
                # Set values from the parent model's training run
                st.session_state.epochs = current_training_run.epochs
                st.session_state.learning_rate_multiplier = current_training_run.learning_rate_multiplier
                st.session_state.batch_size = current_training_run.batch_size

                # Filter training runs based on the current projects and the current fine tuned model type
                training_run_dtos = service.filter_simple_training_runs(
                    GetTrainingRunsDTO(fine_tuning_model=current_training_run.fine_tuning_model, project_id=current_project_data.current_project.id))

                # Find the first matching training run with the same seed
                st.session_state.simple_training_run_dto = find_training_run_dto_with_current_seed(
                    training_run_dtos, current_project_data.current_fine_tuning_model)

            # Check if a model has been selected ans set its fine tuning params if the model has been fine tuned already once- no active fine tuning run
            elif selected_model:
                # Set model global presettings
                st.session_state.globalize_model_checkbox = selected_model.is_global

                st.session_state.save_checkpoint_models_checkbox = False

                # Check if the training run exists for the parent model and if not current fine tuning training run ecists yet, set those values
                if selected_model.training_run:
                    # Find the index in the list for the fine-tuning model version
                    st.session_state.chosen_fine_tuning_base_model = selected_model.training_run.fine_tuning_model
                    # Set values from the parent model's training run
                    st.session_state.epochs = selected_model.training_run.epochs
                    st.session_state.learning_rate_multiplier = selected_model.training_run.learning_rate_multiplier
                    st.session_state.batch_size = selected_model.training_run.batch_size

                    # Filter training runs based on the current project and the current fine tuned model type
                    training_run_dtos = service.filter_simple_training_runs(
                        GetTrainingRunsDTO(fine_tuning_model=selected_model.training_run.fine_tuning_model, project_id=current_project_data.current_project.id))

                    # Find the first matching training run with the same seed
                    st.session_state.simple_training_run_dto = find_training_run_dto_with_current_seed(
                        training_run_dtos, selected_model)

                else:
                    # Set base values if the selected model has not been fine tuned yet (version 0)
                    # Find the index in the list for the fine-tuning model version
                    st.session_state.chosen_fine_tuning_base_model = FineTuningModelVersions.openai.value[
                        0]
                    # Set values from the parent model's training run
                    st.session_state.epochs = None
                    st.session_state.learning_rate_multiplier = None
                    st.session_state.batch_size = None

                    training_run_dtos: list[SimpleTrainingRunDTO] = service.filter_simple_training_runs(
                        GetTrainingRunsDTO(fine_tuning_model=st.session_state.chosen_fine_tuning_base_model, project_id=current_project_data.current_project.id))

            st.session_state["init_values_set"] = True
        else:

            # Must be refetched every time the model changes
            training_run_dtos = service.filter_simple_training_runs(
                GetTrainingRunsDTO(fine_tuning_model=st.session_state.chosen_fine_tuning_base_model, project_id=current_project_data.current_project.id))
            # Preserve current selected training run dto -> seed. If this is not set, it will be cleared as soon as the seed selectbox is recreated.
            st.session_state.simple_training_run_dto = st.session_state.get(
                "simple_training_run_dto")

        return training_run_dtos

    # Get the current training status every ten seconds
    @st.experimental_fragment(run_every=10)
    def fine_tuning_progress_bar(fine_tuning_job_id: str, save_checkpoint_models: bool, current_fine_tuning_model: ModelDTO, current_project_id: int, selected_model: ComplexModelDTO, fine_tuning_step_counter: int):

        st.write("")  # Extra space
        st.write("")  # Extra space
        frontend_uf.create_text_divider(
            "##### Fine tuning model", [0.5, 1.0, 0.5])

        current_training_progress, status, progress_message, hyperparameters, seed, fine_tuned_model_id = service.get_current_fine_tuning_status(
            fine_tuning_job_id)

        # Show the current fine tuning progress
        progress = round(current_training_progress,
                         3) if current_training_progress is not None else 0.0
        progress_text = f"""{progress_message} - {
            round(progress*100, 2)}%""" if progress_message else f"""Fine tuning in progress. Please wait. - {round(progress*100, 2)}%"""

        status_messages = {
            "cancelled": "Fine tuning has been cancelled!",
            "failed": "Fine tuning failed!",
            "succeeded": "Finished!"
        }

        if progress_message:
            if status in status_messages:
                progress_text = status_messages[status]

            # Progress must be between 0.0 and 1.0
            progress = 1.0 if status == "succeeded" or progress_message.startswith(
                "New fine-tuned model created") else progress

        st.progress(progress, text=progress_text)

        # If fine tuning has been completed, advance to the next step
        if status == "succeeded":
            cols = st.columns(6)

            with cols[2]:
                cancel_fine_tuning = st.button(
                    label="Cancel", help="Cancel the fine tuning process and return to the previous step", type="secondary")

                if cancel_fine_tuning:
                    service.cancel_fine_tuning_run(fine_tuning_job_id)
                    current_page_navigation_settings(
                        fine_tuning_step_counter,  current_fine_tuning_model=current_fine_tuning_model, rerun=True)

            with cols[3]:
                label, help_text = ("Finish", "Finish the model and continue to train further models based on this base model") if selected_model.version == 0 else (
                    "Continue", "Continue to the next fine tuning step")
                continue_to_next_step = st.button(
                    label=label, help=help_text, type="primary")

            if continue_to_next_step:
                try:

                    # Update current fine-tuned model's training run to latest hyperparameters in case some were set to auto
                    updated_training_run_dto: TrainingRunDTO = service.update_training_run_dtos([UpdateTrainingRunDTO(
                        id=current_fine_tuning_model.training_run_id,
                        epochs=hyperparameters.n_epochs,
                        learning_rate_multiplier=float(
                            hyperparameters.model_extra["learning_rate_multiplier"]),
                        batch_size=hyperparameters.model_extra["batch_size"], seed=seed
                    )])[0]

                    # Add fine_tuned_model_id to currently fine tuned model
                    service.update_models([UpdateModelDTO(
                        id=current_fine_tuning_model.id, fine_tuned_model_id=fine_tuned_model_id)])

                    # Save checkpoint models
                    if save_checkpoint_models:
                        checkpoint_models: list[ModelDTO] = service.save_checkpoint_models(
                            current_fine_tuning_model, current_project_id, updated_training_run_dto)

                    if selected_model.version == "0":
                        toast_message = f"A new model and {len(
                            checkpoint_models)} checkpoint models have been added, check them out!" if save_checkpoint_models else "A new fine tuned base model has been added to the model list, check it out!"
                        ToastManager.add_global_toasts(
                            toast_message, "success")
                        # A base model has been fine-tuned, now return to the model selection
                        current_page_navigation_settings(
                            fine_tuning_step_counter,  current_fine_tuning_model, delete_model=False, rerun=True)
                    else:
                        # Update the current project state so that the user can proceed with model evaluation.
                        GlobalAppStateManager.update_current_project_data(
                            service,
                            UpdateCurrentProjectDataDTO(
                                id=current_project_data.id, fine_tuning_step_counter=fine_tuning_step_counter + 1)
                        )
                        st.rerun()
                except Exception as e:
                    ToastManager.add_global_toasts(
                        f"Something failed, please try again to fine tune a model: {e}", "error")
                    current_page_navigation_settings(
                        fine_tuning_step_counter, current_fine_tuning_model=current_fine_tuning_model, rerun=True)

        else:
            # if the user cancels the fine tuning run, go to the previous step
            cancel_fine_tuning = st.button(
                label="Cancel", help="Cancel the fine tuning process and return to the previous step", type="primary")

            if cancel_fine_tuning:
                try:
                    service.cancel_fine_tuning_run(fine_tuning_job_id)
                    ToastManager.add_global_toasts(
                        f"Fine tuning run has successfully been cancelled.", "success")
                except Exception as e:
                    ToastManager.add_global_toasts(
                        f"Something failed during model cancellation please try again to fine tune a model: {e}", "error")
                finally:
                    current_page_navigation_settings(
                        fine_tuning_step_counter,  current_fine_tuning_model=current_fine_tuning_model, rerun=True)

    def create_new_model(chosen_fine_tuning_base_model: str, selected_model: ComplexModelDTO, is_global: bool, save_checkpoint_models: bool, epochs: int | None, learning_rate_multiplier: float | None,  batch_size: int | None, seed: int | None, is_untrained_model: bool = False):

        try:

            # Model attributes
            model_name: str = selected_model.model_name
            project_ids: list[int] = [current_project_data.current_project.id]
            training_dataset_ids: list[int] = selected_model.training_dataset_ids
            parent_model_id: int = selected_model.id
            is_global: bool = is_global
            # Only available if the model has a version > 0
            augmentation_configurations: list[AugmentationConfiguration] = selected_model.augmentation_configurations

            # Training run attributes
            fine_tuning_model: str = chosen_fine_tuning_base_model

            # Create new model based on old model (parent model)
            model_dto: ModelDTO = service.create_models([CreateModelDTO(
                model_name=model_name, project_ids=project_ids, parent_model_id=parent_model_id, is_global=is_global, training_dataset_ids=training_dataset_ids, augmentation_configurations=augmentation_configurations)])[0]

            # Create new models associated training run
            _ = service.create_training_run_dtos([CreateTrainingRunDTO(
                model_id=model_dto.id, fine_tuning_model=fine_tuning_model, epochs=epochs, learning_rate_multiplier=learning_rate_multiplier, batch_size=batch_size, seed=seed)])[0]

            # If the parent / previous model is version 0 (untrained base model), the user may not add augmented data, since every model hierarchy should have at least one unaugmented base model trained.
            updated_model_dto = None
            if is_untrained_model:
                updated_model_dto: ModelDTO = service.create_fine_tuning_run(
                    model_dto.id, chosen_fine_tuning_base_model)[0]

            # Update model to set new parameters
            GlobalAppStateManager.update_current_project_data(service,
                                                              UpdateCurrentProjectDataDTO(id=current_project_data.id, unfinished_progress=True, current_fine_tuning_model_id=updated_model_dto.id if updated_model_dto else model_dto.id, save_checkpoint_models=save_checkpoint_models, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter + 1))

        except Exception as e:
            ToastManager.add_global_toasts(
                f"Something went wrong during model creation, please try again to fine tune a model: {e}")
            current_page_navigation_settings(
                current_project_data.fine_tuning_step_counter,  current_fine_tuning_model=current_project_data.current_fine_tuning_model)

    def load():
        current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
            service, current_page)

        st.title("Choose Or Create A Base Model")

        # Fetch models using the potentially None `current_project_id`
        models: list[ModelDTO] = service.filter_models(
            GetModelsDTO(project_id=current_project_data.current_project.id))

        # Set the currently selected model if selected and if the user is in the middle of an unfinished fine tuning progress
        if current_project_data.unfinished_progress and current_project_data.selected_model_for_fine_tuning:
            # Must use this since index must be None to be able to delete the currently selected model
            st.session_state.model_selector = next(
                (model for model in models if model.id == current_project_data.selected_model_for_fine_tuning.id), None)

        # Current projects states are reset depending on if a model is selected or not
        selected_model: ModelDTO = st.selectbox("Select one of the existing models assigned to this project",
                                                key="model_selector", options=models, index=None, placeholder="Choose a base model to train" if models else "No options available", label_visibility="hidden" if models else "visible", format_func=lambda dto: frontend_uf.display_dto(dto, formattings["MODELDTO_SIMPLE"]), disabled=current_project_data.fine_tuning_step_counter != 0, on_change=lambda: GlobalAppStateManager.update_current_project_data(
                                                    service, UpdateCurrentProjectDataDTO(
                                                        id=current_project_data.id, selected_model_for_fine_tuning_id=st.session_state["model_selector"].id)) if "model_selector" in st.session_state and st.session_state.model_selector is not None else GlobalAppStateManager.update_current_project_data(
                                                    service, UpdateCurrentProjectDataDTO(
                                                        id=current_project_data.id, save_checkpoint_models=False, unfinished_progress=False, current_augmentation_configurations=[], semantic_similarity_model=None)))

        frontend_uf.create_text_divider("or")

        create_model_button = st.button(
            "Create Model +", type="primary", key="create_model_button", disabled=selected_model != None)

        if create_model_button:
            GlobalAppStateManager.clear_session_state()
            PageNavigator.navigate_to_page('create_model')

        # Set states for newly selected model
        selected_model: ComplexModelDTO = initialize_states_for_selected_model(
            selected_model, current_project_data)

        if selected_model:

            # Always get the most recent current project state
            current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.get_current_project_data(
                service)

            # This is needed because openai the amount of datapoints must be >= the batch size. Meaning: batch_size = 32 -> available datapoints must be >= 32
            total_amount_of_datapoints: int = service.get_datasets_datapoints_count(
                selected_model.training_dataset_ids)

            st.write("")  # Extra space
            st.write("")  # Extra space
            frontend_uf.create_text_divider(
                f"##### Choose a model fine tuning configuration", [0.4, 1, 0.4])

            # Only display if it is an untrained model
            if selected_model.version == "0":
                st.text(f"""Current model '{
                    selected_model.model_name}' has version 0 and is not fine tuned yet. To further fine tune this model with augmented data, it first needs to be fine tuned once with the current dataset to create a 'Base' model with version 1. Any further fine tuning run creates a new model with consecutively numbering like chapters in a book.""")

            # Set the current fine tuning params - selected new model or model already in fine tuning
            training_run_dtos: list[TrainingRunDTO] = set_current_fine_tuning_parameters(
                current_project_data)

            model_global_columns = st.columns(3)

            with model_global_columns[0]:
                chosen_fine_tuning_base_model: str = st.selectbox(label="Choose a model", options=FineTuningModelVersions.openai.value, index=0, placeholder="Choose a fine tuning base model",
                                                                  key="chosen_fine_tuning_base_model", help="Choose a base model for this fine tuning run", label_visibility="collapsed", disabled=current_project_data.fine_tuning_step_counter != 0)

            with model_global_columns[1]:
                is_global = st.checkbox(label="Make model global", value=None, key="globalize_model_checkbox",
                                        help="Globalized models can be selected in the list of available models when creating a new project", label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 0)

            with model_global_columns[2]:
                save_checkpoint_models = st.checkbox(label="Save checkpoint models", value=None, key="save_checkpoint_models_checkbox",
                                                     help="In addition to creating a final fine-tuned model at the end of each fine-tuning job, some fine tuning companies will create one full model checkpoint for you at the end of each training epoch. These checkpoints are themselves full models that can be used as regular models. Checkpoints are useful as they potentially provide a version of your fine-tuned model from before it experienced overfitting.", label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 0)

            fine_tuning_config_columns = st.columns(3)

            with fine_tuning_config_columns[0]:
                epochs: int = st.number_input(label="Amount of epochs", min_value=1, max_value=10, step=1, value=None, key="epochs",
                                              help="The number of epochs to train the model for. An epoch refers to one full cycle through the training dataset. Defaults to auto. 1-10.", placeholder="auto", label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 0)
            with fine_tuning_config_columns[1]:
                learning_rate_multiplier: float = st.number_input(label="Learning rate multiplier", min_value=0.1, max_value=10.0, step=0.1, value=None, key="learning_rate_multiplier",
                                                                  help="Scaling factor for the learning rate. A smaller learning rate may be useful to avoid overfitting. Defaults to auto. 0.1-10.0", placeholder="auto", label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 0)
            with fine_tuning_config_columns[2]:
                # The batch size cannot be larger than the amount of datapoints available in all datasets combined
                batch_size: int = st.number_input(label="Batch size", min_value=1, max_value=32 if total_amount_of_datapoints > 32 else total_amount_of_datapoints, step=1, value=None, key="batch_size",
                                                  help="Number of examples in each batch. A larger batch size means that model parameters are updated less frequently, but with lower variance. Defaults to auto. 1-32.", placeholder="auto", label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 0)

            training_run_dto: SimpleTrainingRunDTO = st.selectbox(label="Seed", options=training_run_dtos, index=None, placeholder="auto", help="The seed controls the reproducibility of the job. Passing in the same seed and job parameters for the same model should produce the same results, but may differ in rare cases. If a seed is not specified (or no other seeds exist), one will be generated for you.", key="simple_training_run_dto",
                                                                  label_visibility="visible", format_func=lambda dto: frontend_uf.display_dto(dto, formattings["TRAINING_RUN_DTO_SIMPLE"]), disabled=current_project_data.fine_tuning_step_counter != 0)

            seed = None
            if training_run_dto:
                seed = training_run_dto.seed

            if current_project_data.fine_tuning_step_counter == 0:
                # Start the model fine tuning if the parent model has version 0 aka. has not been trained yet (enforces a base model)
                is_untrained_model = False
                if selected_model.version == "0":
                    is_untrained_model = True

                st.button(
                    label="Train Model" if is_untrained_model else "Save", key="submit_train_model", help="Submit the current fine tuning configuration", type="primary", disabled=current_project_data.fine_tuning_step_counter != 0, on_click=create_new_model, args=(chosen_fine_tuning_base_model, selected_model, is_global, save_checkpoint_models, epochs, learning_rate_multiplier, batch_size, seed, is_untrained_model))

            # Either train the model directly if the current parent model has not been trained or increase the step counter by one to go directly to the next step
            if current_project_data.fine_tuning_step_counter == 1 and selected_model.version == "0":
                fine_tuning_progress_bar(
                    current_project_data.current_fine_tuning_model.fine_tuning_job_id, save_checkpoint_models, current_project_data.current_fine_tuning_model, current_project_data.current_project.id, selected_model, current_project_data.fine_tuning_step_counter)
            elif current_project_data.fine_tuning_step_counter == 1:
                current_project_data = GlobalAppStateManager.update_current_project_data(service,
                                                                                         UpdateCurrentProjectDataDTO(id=current_project_data.id, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter + 1))

            # Start augmentation process
            if current_project_data.fine_tuning_step_counter >= 2:

                @st.experimental_fragment
                def data_augmentation_process(total_amount_of_datapoints: int):
                    amount_base_key = f"data_augmentation_method_amount_"
                    method_base_key = f"data_augmentation_method_"
                    previous_method_base_key = f"previous_data_augmentation_method_"
                    augmentation_configurations_selected: list[
                        AugmentationConfiguration] = []

                    current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
                        service, current_page)

                    def initialize_augmentation_state():

                        if not current_project_data.current_augmentation_configurations:
                            current_project_data.current_augmentation_configurations = []

                        # initialize session state data
                        if 'augmentation_configurations_selected' not in st.session_state:
                            st.session_state['augmentation_configurations_selected'] = current_project_data.current_augmentation_configurations

                        if 'semantic_similarity_model' not in st.session_state:
                            st.session_state['semantic_similarity_model'] = current_project_data.semantic_similarity_model

                        return st.session_state[
                            'augmentation_configurations_selected']

                    augmentation_configurations_selected = initialize_augmentation_state()

                    def show_data_augmentation_amount(total_amount_of_datapoints: int, augmentation_config: AugmentationConfiguration) -> None:
                        augmentation_percentage = augmentation_config["augmentation_percentage"]
                        augmentation_method = augmentation_config["selected_method"]

                        total_augmentation_amount = service.get_total_augmentation_amount(
                            total_amount_of_datapoints, augmentation_percentage)

                        with st.columns(1)[0]:
                            custom_style_span(center_augmentation_text)
                            st.text(f"""{total_augmentation_amount} datapoints will be augmented via {
                                    augmentation_method}.""")

                    def update_augmentation_config(augmentation_config: AugmentationConfiguration, session_key: str):
                        new_val = st.session_state[session_key]
                        augmentation_config["augmentation_config"][session_key] = new_val

                    def show_augmentation_method_menus(augmentation_config: AugmentationConfiguration):
                        augmentation_method = augmentation_config["selected_method"]
                        if augmentation_method == augmentation_methods["google_translate"]:
                            pass  # Show google form
                        if augmentation_method == augmentation_methods["EDA_Easy_Data_Augmentation"]:
                            # Set config values if exist
                            if not augmentation_config["augmentation_config"]:
                                augmentation_config[
                                    "augmentation_config"] = EDAParams(alpha_sr=10.0, alpha_ri=10.0, alpha_rs=10.0, alpha_rd=10.0)

                            # Show EDA form
                            with st.container(border=True):
                                columns = st.columns(2)
                                with columns[0]:
                                    st.number_input(label="Amount of synonym replacement in %", min_value=0.0, max_value=100.0, value=augmentation_config[
                                        "augmentation_config"]["alpha_sr"], key="alpha_sr",
                                        help="Set the percentage of words per data point where synonym replacement should be applied.  As long as the percentage is > 0, at least one operation of this kind will be performed.", placeholder="auto", on_change=update_augmentation_config, args=(augmentation_config, "alpha_sr"), disabled=current_project_data.fine_tuning_step_counter != 2)
                                with columns[1]:
                                    st.number_input(label="Amount of random insertion in %", min_value=0.0, max_value=100.0, value=augmentation_config[
                                        "augmentation_config"]["alpha_ri"], key="alpha_ri",
                                        help="Set the percentage of words per data point where random insertion should be applied.  As long as the percentage is > 0, at least one operation of this kind will be performed.", placeholder="auto", on_change=update_augmentation_config, args=(augmentation_config, "alpha_ri"), disabled=current_project_data.fine_tuning_step_counter != 2)
                                columns = st.columns(2)
                                with columns[0]:
                                    st.number_input(label="Amount of random swap in %", min_value=0.0, max_value=100.0, value=augmentation_config["augmentation_config"]["alpha_rs"], key="alpha_rs",
                                                    help="Set the percentage of words per data point where random swap should be applied. As long as the percentage is > 0, at least one operation of this kind will be performed.", placeholder="auto", on_change=update_augmentation_config, args=(augmentation_config, "alpha_rs"), disabled=current_project_data.fine_tuning_step_counter != 2)
                                with columns[1]:
                                    st.number_input(label="Amount of random deletion in %", min_value=0.0, max_value=100.0, value=augmentation_config["augmentation_config"]["alpha_rd"], key="alpha_rd",
                                                    help="Set the percentage of words per data point where random deletion should be applied.  As long as the percentage is > 0, at least one operation of this kind will be performed.", placeholder="auto", on_change=update_augmentation_config, args=(augmentation_config, "alpha_rd"), disabled=current_project_data.fine_tuning_step_counter != 2)

                                # Save the configuration and norm it to a value between 0-1
                                # augmentation_config["augmentation_config"] = EDAParams(
                                #     alpha_sr=st.session_state.alpha_sr / 100, alpha_ri=st.session_state.alpha_ri / 100, alpha_rs=st.session_state.alpha_rs / 100, alpha_rd=st.session_state.alpha_rd / 100)

                    def update_methods(augmentation_config: AugmentationConfiguration, new_method_key: str):
                        old_method = augmentation_config["prev_method"]
                        # Fetch the current session state value. Cannot be passed directly to "on_change" function since the value is set on creation time - else there would also be issues with the correct augmentation config, so this is probably the best approach.
                        new_method = st.session_state[new_method_key]
                        if new_method is None:
                            augmentation_configurations_selected.remove(
                                augmentation_config)
                        else:
                            augmentation_config["selected_method"] = new_method
                            if old_method is None and old_method != new_method:
                                augmentation_config["prev_method"] = new_method
                                augmentation_configurations_selected.append(
                                    augmentation_config)

                    def update_augmentation_percentage(augmentation_config: AugmentationConfiguration, new_augmentation_percentage_key: str | None) -> None:
                        augmentation_config["augmentation_percentage"] = st.session_state[new_augmentation_percentage_key]

                    def delete_semantic_model_and_configs_from_models(current_project_data: CurrentProjectDataDTO):
                        # Update current fine tuning model to remove semantic similarity model and augmentation configurations
                        service.update_models([UpdateModelDTO(
                            current_project_data.current_fine_tuning_model.id, semantic_similarity_model="", augmentation_configurations=[])])

                    def generate_augmented_data():
                        global current_project_data
                        # Check if augmented data already exists and delete it if so
                        if current_project_data.current_augmented_datapoint_evaluation_ids:
                            # Get last added dataset of the current fine tuning model -> most recent augmented dataset, and delete it.
                            delete_currently_augmented_datasets()
                            # Remove old datapoint evaluator and its data
                            if st.session_state.get("datapoint_evaluator"):
                                del st.session_state["datapoint_evaluator"]

                        # Only create an augmented dataset if an augmentation configuration is selected.
                        if augmentation_configurations_selected:
                            # Create augmented datapoints
                            # Use this id to fetch
                            datapoint_evaluation_ids: list[int] = service.generate_augmented_data(
                                current_project_data.current_fine_tuning_model.id, augmentation_configurations_selected, semantic_similarity_model, current_project_data.current_project.id)
                            current_project_data = GlobalAppStateManager.update_current_project_data(service, UpdateCurrentProjectDataDTO(
                                id=current_project_data.id, semantic_similarity_model=semantic_similarity_model, current_augmented_datapoint_evaluation_ids=datapoint_evaluation_ids, current_augmentation_configurations=augmentation_configurations_selected))
                        else:
                            delete_semantic_model_and_configs_from_models(
                                current_project_data)
                            # Go directly to fine tune the model (step 3)
                            current_project_data = GlobalAppStateManager.update_current_project_data(service, UpdateCurrentProjectDataDTO(
                                id=current_project_data.id, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter + 1, current_augmentation_configurations=[]))

                    st.write("")  # Extra space
                    st.write("")  # Extra space

                    if current_project_data.fine_tuning_step_counter == 2:
                        PageNavigator.set_navbar("Start over", current_page, nav_bar_cols_config=[
                            1.2, 3, 1.2], help="Delete the currently augmented data and go back to the fine tuning settings", func=current_page_navigation_settings, args=[current_project_data.fine_tuning_step_counter], current_fine_tuning_model=current_project_data.current_fine_tuning_model)

                    frontend_uf.create_text_divider(
                        f"##### Choose a data augmentation configuration", [0.4, 1, 0.4])

                    with st.columns(1)[0]:
                        custom_style_span(center_augmentation_text)
                        st.text(f"""Current dataset size is {
                                total_amount_of_datapoints} datapoints.""")

                    def render_augmentation_fields():
                        for i in range(len(augmentation_configurations_selected) + 1):
                            available_methods = [method for method in augmentation_methods
                                                 if method not in [aug_method["selected_method"] for aug_method in augmentation_configurations_selected]]

                            amount_key = f"{amount_base_key}{i}"
                            method_key = f"{method_base_key}{i}"
                            previous_method_key = f"{
                                previous_method_base_key}{i}"

                            augmentation_config: AugmentationConfiguration = None
                            if i < len(augmentation_configurations_selected):
                                augmentation_config = augmentation_configurations_selected[i]
                                st.session_state[amount_key] = augmentation_config["augmentation_percentage"]
                                st.session_state[method_key] = augmentation_config["selected_method"]
                                st.session_state[previous_method_key] = augmentation_config["selected_method"]
                            elif available_methods:
                                augmentation_config = AugmentationConfiguration(
                                    selected_method=None, prev_method=None, augmentation_percentage=None, augmentation_config=None)
                                st.session_state[method_key] = augmentation_config["augmentation_percentage"]
                                st.session_state[amount_key] = augmentation_config["selected_method"]
                                st.session_state[previous_method_key] = augmentation_config["selected_method"]

                            if augmentation_config:
                                # Add the currently selected method to the available method options for this selectbox to avoid issues where selectbox key method cannot be found in available methods list.
                                if augmentation_config["selected_method"]:
                                    available_methods.append(
                                        augmentation_config["selected_method"])

                                data_augmentation_cols = st.columns(2)

                                with data_augmentation_cols[0]:
                                    st.number_input(
                                        label=f"Amount of augmented data in %",
                                        min_value=0.1, max_value=1000.0, step=0.1,
                                        value=None,
                                        key=amount_key,
                                        on_change=update_augmentation_percentage,
                                        args=(augmentation_config, amount_key),
                                        help="Select the percentage of data you want to be augmented (0-1000)",
                                        placeholder="no augmentation",
                                        disabled=current_project_data.fine_tuning_step_counter != 2
                                    )

                                with data_augmentation_cols[1]:

                                    st.selectbox(
                                        label=f"Select data augmentation method",
                                        options=available_methods,
                                        index=None,
                                        key=method_key,
                                        help="Select one of the provided data augmentation methods",
                                        on_change=update_methods,
                                        args=(augmentation_config, method_key),
                                        disabled=current_project_data.fine_tuning_step_counter != 2
                                    )

                                if st.session_state.get(amount_key):
                                    show_augmentation_method_menus(
                                        augmentation_config)
                                    show_data_augmentation_amount(
                                        total_amount_of_datapoints,
                                        augmentation_config
                                    )
                    render_augmentation_fields()

                    semantic_similarity_model = st.selectbox(label="Coherence score models", options=sbert_models, index=None, key="semantic_similarity_model",
                                                             help="Select an original Sentence BERT (SBERT)  model to calculate the coherence score based on the vector representations of the input sentences of each datapoint compared to its augmented datapoint. The first usage may take a while since the model has to be downloaded.", placeholder="Choose a coherence score model", format_func=lambda dto: frontend_uf.display_dto(dto, formattings["SBERT_MODELS"]), label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 2)
                    # The smenatic model description
                    if semantic_similarity_model:
                        st.text(
                            f"""{semantic_similarity_model["description"]}""")

                    # TODO Add selectbox for sentence similarity check models and add them to the model as parameters, so that it is clear which model has beend used to calculate the similarity check

                    if current_project_data.fine_tuning_step_counter == 2:
                        augment_data = st.button(
                            label="Redo Augmentation" if current_project_data.current_augmented_datapoint_evaluation_ids else "Submit", key="submit", help="Create augmented datapoints preview to evaluate them. Can always be redone in case of low quality", type="secondary" if current_project_data.current_augmented_datapoint_evaluation_ids else "primary")
                        if augment_data:
                            generate_augmented_data()
                            # To get out of the current fragment
                            st.rerun()

                    if current_project_data.current_augmented_datapoint_evaluation_ids:
                        datapoin_evaluator: DataPointEvaluator = GlobalAppStateManager.get_or_create_session_state(
                            "datapoint_evaluator", service, current_project_data.current_fine_tuning_model.id, current_project_data.current_augmented_datapoint_evaluation_ids, default_value=DataPointEvaluator)

                        update_leftovers = st.session_state.get(
                            "submit_augmented_data") or False

                        datapoin_evaluator.load(
                            current_project_data.fine_tuning_step_counter, activation_threshold=2, display_scores=not update_leftovers)

                        if update_leftovers:
                            # Update the currently only locally stored evaluations
                            datapoin_evaluator.update_left_over_evaluations()

                        # extra space
                        st.write("")

                        if current_project_data.fine_tuning_step_counter == 2:
                            def delete_and_update():
                                delete_currently_augmented_datasets()
                                GlobalAppStateManager.update_current_project_data(
                                    service,
                                    UpdateCurrentProjectDataDTO(
                                        id=current_project_data.id,
                                        fine_tuning_step_counter=current_project_data.fine_tuning_step_counter + 1
                                    )
                                )

                            columns = st.columns([1, 1, 2, 1, 1, 1])

                            with columns[3]:
                                st.button(
                                    label="Submit", help="Save the current datapoint evaluations and continue with the next step", type="primary", key="submit_augmented_data", on_click=lambda: GlobalAppStateManager.update_current_project_data(service, UpdateCurrentProjectDataDTO(
                                        id=current_project_data.id, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter + 1)))

                            with columns[2]:
                                skip = st.button(
                                    label="Skip", help="Skip the current data augmentation and train the fine tuned model with the original models data", type="secondary")
                                if skip:
                                    delete_semantic_model_and_configs_from_models(
                                        current_project_data)
                                    delete_and_update()
                                    # To get out of the current fragment
                                    st.rerun()

                    # Start model evaluation process
                    if current_project_data.fine_tuning_step_counter == 3:

                        training_run_dto: TrainingRunDTO = service.get_training_run_by_id(
                            current_project_data.current_fine_tuning_model.training_run_id)[0]
                        # If the return value is not "caught", streamlit will dispaly it in the UI via its "magic"
                        _ = service.create_fine_tuning_run(
                            current_project_data.current_fine_tuning_model.id, training_run_dto.fine_tuning_model)[0]

                        # Increase fine tuning step counter by 1
                        current_project_data = GlobalAppStateManager.update_current_project_data(service,
                                                                                                 UpdateCurrentProjectDataDTO(id=current_project_data.id, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter + 1))

                    if current_project_data.fine_tuning_step_counter == 4:
                        fine_tuning_progress_bar(
                            current_project_data.current_fine_tuning_model.fine_tuning_job_id, current_project_data.save_checkpoint_models, current_project_data.current_fine_tuning_model, current_project_data.current_project.id, current_project_data.selected_model_for_fine_tuning, current_project_data.fine_tuning_step_counter)

                data_augmentation_process(
                    total_amount_of_datapoints)

            if current_project_data.fine_tuning_step_counter == 5:
                st.write("")  # Extra space
                st.write("")  # Extra space

                @st.experimental_fragment
                def model_evaluation_fragment():

                    # TODO: Delete current model evalaution data
                    PageNavigator.set_navbar("Go back", current_page, nav_bar_cols_config=[
                        1.2, 3, 1.2], help="Delete the current model evalaution and go back to the data augmentation process", func=current_page_navigation_settings, args=[current_project_data.fine_tuning_step_counter], current_fine_tuning_model=current_project_data.current_fine_tuning_model)

                    frontend_uf.create_text_divider(
                        f"##### Model Evaluation", [0.4, 1, 0.4])

                model_evaluation_fragment()

            # if current_step_counter == 3:
            #             st.write("")  # Extra space
            #             st.write("")  # Extra space
            #             current_step_counter: int = update_step_counter(3)
            #             frontend_uf.create_text_divider(
            #                 f"##### Evaluate the currently augmented data", [0.4, 1, 0.4])

    load()
