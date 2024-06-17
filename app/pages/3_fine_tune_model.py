# Import necessary modules and packages
from datetime import timedelta
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.backend.dtos.create_request import CreateModelDTO, CreateTrainingRunDTO
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO, UpdateTrainingRunDTO
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
from backend.util.config import DATA_AUGMENTATION_METHODS as augmentation_methods
from app.backend.database.schema import FineTuningModelVersions
from backend.util import utility_functions as backend_uf
from backend.service.classes.api.openai_services import OpenAIService
from frontend.classes.datapoint_service import DataPointService

apply_global_style()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)
current_page = "fine_tune_model"

with logger:
    ToastManager.show_global_toasts()
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
        service, current_page)
    QueryParamsManager.set_query_params_from_page(current_page)

    def current_page_navigation_settings(current_step_counter):
        if current_step_counter == 0:
            update_current_project_data = UpdateCurrentProjectDataDTO(
                id=current_project_data.id, save_checkpoint_models=False)
            GlobalAppStateManager.update_current_project_data(
                service, update_current_project_data)
        if current_step_counter == 1:
            update_current_project_data = UpdateCurrentProjectDataDTO(
                id=current_project_data.id, selected_model_for_fine_tuning_id=None, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter-1, unfinished_progress=False)
            GlobalAppStateManager.update_current_project_data(
                service, update_current_project_data)
        if current_step_counter == 2:
            update_current_project_data = UpdateCurrentProjectDataDTO(
                id=current_project_data.id, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter-2, fine_tuning_augmentation_methods=None, fine_tuning_augmentation_method_percentages=None, currently_modified_dataset_id=None)
            GlobalAppStateManager.update_current_project_data(
                service, update_current_project_data)

    if current_project_data.fine_tuning_step_counter == 0:
        PageNavigator.set_navbar(
            "Go back", "home", "Return to the previous page", func=current_page_navigation_settings, args=[current_project_data.fine_tuning_step_counter])

    # Get the current training status every ten seconds

    @st.experimental_fragment(run_every=10)
    def fine_tuning_progress_bar(fine_tuning_job_id: str, save_checkpoint_models: bool, current_fine_tuning_model: ModelDTO, current_project_id: int):
        # Always need to go two steps back when the fine tuning progress bar is called
        PageNavigator.set_navbar("Previous step", current_page, nav_bar_cols_config=[
                                 2, 3, 2], help="Go back to previous step", func=current_page_navigation_settings, args=[current_project_data.fine_tuning_step_counter])

        st.write("")  # Extra space
        st.write("")  # Extra space
        frontend_uf.create_text_divider(
            f"##### Fine tuning model", [0.4, 1.5, 0.4])

        current_training_progress, status, progress_message, hyperparameters = service.get_current_fine_tuning_status(
            fine_tuning_job_id)

        if current_training_progress:
            progress_text = f"Fine tuning in progress. Please wait. - {
                current_training_progress}"
            my_bar = st.progress(
                current_training_progress, text=f"{progress_message} - {current_training_progress*100}%" or progress_text)
        elif status == "cancelled":
            progress_text = f"Fine tuning has been cancelled!"
            my_bar = st.progress(
                current_training_progress or 0.0, text=progress_text)
        elif status == "failed":
            progress_text = f"Fine tuning failed!"
            my_bar = st.progress(
                current_training_progress or 0.0, text=progress_text)
        elif status == "succeeded":
            progress_text = f"Finished!"
            my_bar = st.progress(
                current_training_progress or 1.0, text=progress_text)
        else:
            my_bar = st.progress(
                0.0, text=f"Fine tuning in progress.... {status}")

        # If fine tuning has been completed, advance to the next step
        if status == "succeeded":
            try:
                epochs = hyperparameters.n_epochs
                learning_rate_multiplier = hyperparameters.model_extra["learning_rate_multiplier"]
                batch_size = hyperparameters.model_extra["batch_size"]

                # Update current fine tuned models training run to latest hyperparameters in case some where set to auto
                service.update_training_run_dtos([UpdateTrainingRunDTO(id=current_fine_tuning_model.training_run_id, epochs=epochs,
                                                                       learning_rate_multiplier=float(learning_rate_multiplier), batch_size=batch_size)])
                # Save checkpoint models
                if save_checkpoint_models:
                    saved_checkpoint_models: list[ModelDTO] = service.save_checkpoint_models(
                        current_fine_tuning_model, current_project_id)

                # Update the current project state so that the user can proceed with model evaluation.
                GlobalAppStateManager.update_current_project_data(service,
                                                                  UpdateCurrentProjectDataDTO(id=current_project_data.id, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter + 1))
                st.rerun()
            except Exception as e:
                # TODO: Implement logic to reset model state (delete model in database and from openai)
                logger.ui_warning(
                    f"Something failed during fine tuning success: {e}")

        else:
            # if the user cancels the fine tuning run, go to the previous step
            cancel_fine_tuning = st.button(
                label="Cancel", help="Cancel the fine tuning process and return to the previous step", type="primary")

            if cancel_fine_tuning:
                service.cancel_fine_tuning_run(fine_tuning_job_id)
                GlobalAppStateManager.update_current_project_data(service,
                                                                  UpdateCurrentProjectDataDTO(id=current_project_data.id, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter - 1))
                st.rerun()

    def create_new_model(chosen_fine_tuning_base_model: str, parent_model: ComplexModelDTO, is_global: bool, save_checkpoint_models: bool, epochs: int | None, learning_rate_multiplier: float | None,  batch_size: int | None, seed: int | None):

        try:

            # Model attributes
            model_name: str = parent_model.model_name
            project_ids: list[int] = [current_project_data.current_project.id]
            training_dataset_ids: list[int] = parent_model.training_dataset_ids
            parent_model_id: int = parent_model.id
            is_global: bool = is_global

            # Training run attributes
            fine_tuning_model: str = chosen_fine_tuning_base_model

            # Create new model based on old model (parent model)
            model_dto: ModelDTO = service.create_models([CreateModelDTO(
                model_name=model_name, project_ids=project_ids, parent_model_id=parent_model_id, is_global=is_global, training_dataset_ids=training_dataset_ids)])[0]

            # Create new models associated training run
            training_run_dto: TrainingRunDTO = service.create_training_run_dtos([CreateTrainingRunDTO(
                model_id=model_dto.id, fine_tuning_model=fine_tuning_model, epochs=epochs, learning_rate_multiplier=learning_rate_multiplier, batch_size=batch_size, seed=seed)])[0]

            # If the parent / previous model is version 0 (untrained base model), the user may not add augmented data, since every model hierarchy should have at least one unaugmented base model trained.
            updated_model_dto = None
            if parent_model.version == "0":
                updated_model_dto: ModelDTO = service.create_fine_tuning_run(
                    model_dto.id, training_run_dto)[0]

            # Update model to set new parameters
            GlobalAppStateManager.update_current_project_data(service,
                                                              UpdateCurrentProjectDataDTO(id=current_project_data.id, unfinished_progress=True, current_fine_tuning_model_id=updated_model_dto.id if updated_model_dto else model_dto.id, save_checkpoint_models=save_checkpoint_models, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter + 1))

        except Exception as e:
            # Handle model deletion, state reset, training dto deleteion, openai job cancellation and other stuff when something fails during model and model fine tuning job creation
            logger.ui_warning(
                f"Something failed during fine tuning job creation: {e}")

    def load():
        current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
            service, current_page)

        st.title("Choose Or Create A Base Model")

        # TODO: REMOVE
        # current_project_data = GlobalAppStateManager.update_current_project_data(service, UpdateCurrentProjectDataDTO(
        #     id=current_project_data.id, selected_model_for_fine_tuning_id=None, fine_tuning_step_counter=0))

        # Fetch models using the potentially None `current_project_id`
        models: list[ModelDTO] = service.filter_models(
            GetModelsDTO(project_id=current_project_data.current_project.id))

        # Set the currently selected model if selected
        if current_project_data.selected_model_for_fine_tuning:
            # Must use this since index must be None to be able to delete the currently selected model
            st.session_state.model_selector = next(
                (model for model in models if model.id == current_project_data.selected_model_for_fine_tuning.id), None)

        selected_model = st.selectbox("Select one of the existing models assigned to this project",
                                      key="model_selector", options=models, index=None, placeholder="Choose a base model to train" if models else "No options available", label_visibility="hidden" if models else "visible", format_func=lambda dto: frontend_uf.display_dto(dto, formattings["MODELDTO_SIMPLE"]), disabled=current_project_data.fine_tuning_step_counter != 0, on_change=lambda: GlobalAppStateManager.update_current_project_data(service, UpdateCurrentProjectDataDTO(
                                          id=current_project_data.id, selected_model_for_fine_tuning_id=st.session_state.model_selector.id if st.session_state.get("model_selector") else None)))

        frontend_uf.create_text_divider("or")

        create_model_button = st.button(
            "Create Model +", type="primary", key="create_model_button", disabled=selected_model != None)

        if create_model_button:
            GlobalAppStateManager.clear_session_state()
            PageNavigator.navigate_to_page('create_model')

        if selected_model:
            # Update selected model in current app state if it has changed
            if selected_model.id != getattr(current_project_data.selected_model_for_fine_tuning, "id", None):
                current_project_data = GlobalAppStateManager.update_current_project_data(service, UpdateCurrentProjectDataDTO(
                    id=current_project_data.id, selected_model_for_fine_tuning_id=selected_model.id))

                GlobalAppStateManager.clear_session_state()

            # Always get the most recent current project state
            current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.get_current_project_data(
                service)

            # This is needed because openai the amount of datapoints must be >= the batch size. Meaning: batch_size = 32 -> available datapoints must be >= 32
            total_amount_of_datapoints: int = service.get_training_dataset_datapoint_amount(
                selected_model.training_dataset_ids)

            st.write("")  # Extra space
            st.write("")  # Extra space
            frontend_uf.create_text_divider(
                f"##### Choose a model fine tuning configuration", [0.4, 1, 0.4])

            # Only display if it is an untrained model
            if selected_model.version == "0":
                st.text(f"""Current model '{
                    selected_model.model_name}' has version 0 and is not fine tuned yet. To further fine tune this model with augmented data, it first needs to be fine tuned once with the current dataset to create a 'Base' model with version 1. Any further fine tuning run creates a new model with consecutively numbering like chapters in a book.""")

            # If no parent model exists because the model has not been trained yet, the model itself is used for setting default values
            parent_model: ComplexModelDTO = current_project_data.selected_model_for_fine_tuning

            fine_tuning_model = None
            if parent_model.training_run:
                fine_tuning_model = parent_model.training_run.fine_tuning_model

            init_values_set = GlobalAppStateManager.get_or_create_session_state(
                "init_values_set", False)

            # Only set the init values once to not overwrite set values on reload
            if not init_values_set:

                # Check if the parent model exists
                if parent_model:
                    st.session_state.is_global = parent_model.is_global

                    # Check if the training run exists for the parent model
                    if parent_model.training_run:
                        # Find the index in the list for the fine-tuning model version
                        st.session_state.chosen_fine_tuning_base_model_index = backend_uf.find_index_in_list(
                            FineTuningModelVersions.openai.value, parent_model.training_run.fine_tuning_model, default=0)
                        # Set values from the parent model's training run
                        st.session_state.epochs = parent_model.training_run.epochs
                        st.session_state.learning_rate_multiplier = parent_model.training_run.learning_rate_multiplier
                        st.session_state.batch_size = parent_model.training_run.batch_size

                st.session_state["init_values_set"] = True

            # # Set default values
            chosen_fine_tuning_base_model: str = st.session_state.get(
                "chosen_fine_tuning_base_model", None)
            # Filter training runs dtos which are used for seed selection by either selected model or preset model if no selected yet.,
            training_run_dtos: list[SimpleTrainingRunDTO] = service.filter_simple_training_runs(
                GetTrainingRunsDTO(fine_tuning_model=st.session_state.get("chosen_fine_tuning_base_model", fine_tuning_model)))
            chosen_fine_tuning_base_model_index: int = backend_uf.find_index_in_list(
                FineTuningModelVersions.openai.value, chosen_fine_tuning_base_model or fine_tuning_model, default=0)
            is_global: bool = st.session_state.get(
                "globalize_model_checkbox", False)
            save_checkpoint_models: bool = st.session_state.get(
                "save_checkpoint_models_checkbox", False)
            epochs: int | None = st.session_state.get("epochs", None)
            learning_rate_multiplier: float | None = st.session_state.get(
                "learning_rate_multiplier", None)
            batch_size: int | None = st.session_state.get(
                "batch_size", None)

            model_global_columns = st.columns(3)

            with model_global_columns[0]:
                chosen_fine_tuning_base_model: str = st.selectbox(label="Choose a model", options=FineTuningModelVersions.openai.value, index=chosen_fine_tuning_base_model_index, placeholder="Choose a fine tuning base model",
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
                st.button(
                    label="Train Model" if parent_model.version == "0" else "Save", key="submit_train_model", help="Submit the current fine tuning configuration", type="primary", disabled=current_project_data.fine_tuning_step_counter != 0, on_click=create_new_model, args=(chosen_fine_tuning_base_model, parent_model, is_global, save_checkpoint_models, epochs, learning_rate_multiplier, batch_size, seed))

            # Either train the model directly if the current parent model has not been trained or increase the step counter by one to go directly to the next step
            if current_project_data.fine_tuning_step_counter == 1 and parent_model.version == "0":
                fine_tuning_progress_bar(
                    current_project_data.current_fine_tuning_model.fine_tuning_job_id, save_checkpoint_models, current_project_data.current_fine_tuning_model, current_project_data.current_project.id)
            elif current_project_data.fine_tuning_step_counter == 1:
                GlobalAppStateManager.update_current_project_data(service,
                                                                  UpdateCurrentProjectDataDTO(id=current_project_data.id, fine_tuning_step_counter=current_project_data.fine_tuning_step_counter + 1))
                st.rerun()

            # Start augmentation process
            if current_project_data.fine_tuning_step_counter == 2:

                @st.experimental_fragment
                def data_augmentation_process():
                    PageNavigator.set_navbar("Previous step", current_page, nav_bar_cols_config=[
                                             2, 3, 2], help="Go back to previous step", func=current_page_navigation_settings, args=[current_project_data.fine_tuning_step_counter])
                    st.write("HELLO")

                data_augmentation_process()

            # if selected_model.version == 0 and current_step_counter == 2:  # TODO: Change version to > 0
            #     st.write("")  # Extra space
            #     st.write("")  # Extra space
            #      frontend_uf.create_text_divider(
            #           f"##### Choose a data augmentation configuration", [0.4, 1, 0.4])

            #       data_augmentation_cols = st.columns(2)

            #        with data_augmentation_cols[0]:
            #             first_data_augmentation_method_amount: int = st.number_input(label="Amount of augmented data in %", min_value=0.1, max_value=5000.0, step=0.1, value=None, key="first_data_augmentation_method_amount",
            #                                                                          help="Select the percentage of data you want to be augmented", placeholder="no augmentation", label_visibility="visible")

            #             second_data_augmentation_method_amount: int = st.number_input(label="Amount of augmented data in %", min_value=0.1, max_value=5000.0, step=0.1, value=None, key="second_data_augmentation_method_amount",
            #                                                                           help="Select the percentage of data you want to be augmented", placeholder="no augmentation", label_visibility="visible")

            #         with data_augmentation_cols[1]:
            #             first_data_augmentation_method = st.selectbox(label="Select data augmentation method", options=augmentation_methods, key="first_data_augmentation_method",
            #                                                           help="Select one of the provided data augmentation methods.", placeholder="Chose a data augmentation option", label_visibility="hidden")

            #             second_data_augmentation_method = st.selectbox(label="Select data augmentation method", options=augmentation_methods, key="second_data_augmentation_method",
            #                                                            help="Select one of the provided data augmentation methods.", placeholder="Chose a data augmentation option", label_visibility="hidden")

            #         if current_step_counter == 2:
            #             submit = st.button(
            #                 label="Submit", key="submit", help="Submit the current fine tuning configuration", type="primary")
            #             if submit:
            #                 current_step_counter: int = update_step_counter(3)

            #         if current_step_counter == 3:
            #             st.write("")  # Extra space
            #             st.write("")  # Extra space
            #             current_step_counter: int = update_step_counter(3)
            #             frontend_uf.create_text_divider(
            #                 f"##### Evaluate the currently augmented data", [0.4, 1, 0.4])

    load()
