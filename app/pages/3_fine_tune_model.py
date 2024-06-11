# Import necessary modules and packages
from datetime import timedelta
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from app.backend.dtos.create_request import CreateModelDTO, CreateTrainingRunDTO
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO
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

apply_global_style()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)
current_page = "fine_tune_model"

with logger:
    ToastManager.show_global_toasts()
    PageNavigator.set_navbar(
        "Go back", "home", "Return to the previous page")
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
        service, current_page)
    QueryParamsManager.set_query_params_from_page(current_page)

    # def go_to_previous_step():
    #     GlobalAppStateManager.update_current_project_data(
    #         UpdateCurrentProjectDataDTO(fine_tuning_step_counter=current_project_data.fine_tuning_step_counter - 1))

    def start_fine_tuning_process():
        pass

    def create_new_model(chosen_fine_tuning_base_model: str, parent_model: ComplexModelDTO, is_global: bool, save_checkpoint_models: bool, epochs: int | None, learning_rate_multiplier: float | None,  batch_size: int | None, seed: int | None):

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
            model_name=model_name, project_ids=project_ids, parent_model_id=parent_model_id, is_global=is_global, training_dataset_ids=training_dataset_ids)])

        # Create new models associated training run
        service.create_training_run_dtos([CreateTrainingRunDTO(
            model_id=model_dto.id, fine_tuning_model=fine_tuning_model, epochs=epochs, learning_rate_multiplier=learning_rate_multiplier, batch_size=batch_size, seed=seed)])

        # Update project state to unfinished progress
        GlobalAppStateManager.update_current_project_data(
            UpdateCurrentProjectDataDTO(fine_tuning_step_counter=2, unfinished_progress=True, current_fine_tuning_model_id=model_dto.id, save_checkpoint_models=save_checkpoint_models))

        # If the parent / previous model is version 0 (untrained base model), the user may not add augmented data, since every model hierarchy should have at least one unaugmented base model trained.
        if parent_model.version == 0:
            start_fine_tuning_process()

        # TODO: Implement a service function to update training runs in case of openai setting the default values

    def load():
        current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
            service, current_page)

        st.title("Choose Or Create A Base Model")

        # Fetch models using the potentially None `current_project_id`
        models: list[ModelDTO] = service.filter_models(
            GetModelsDTO(project_id=current_project_data.current_project.id))

        selected_model = st.selectbox("Select one of the existing models assigned to this project",
                                      key="model_selector", options=models, index=None, placeholder="Choose a base model to train" if models else "No options available", label_visibility="hidden" if models else "visible", format_func=lambda dto: frontend_uf.display_dto(dto, formattings["MODELDTO_SIMPLE"]))

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
                    id=current_project_data.id, selected_model_for_fine_tuning_id=selected_model.id, fine_tuning_step_counter=1))

            @st.experimental_fragment
            def load_model_configuration_inputs():

                st.write("")  # Extra space
                st.write("")  # Extra space
                frontend_uf.create_text_divider(
                    f"##### Choose a model fine tuning configuration", [0.4, 1, 0.4])

                st.text(f"""Current model '{
                    selected_model.model_name}' has version 0 and is not fine tuned yet. To further fine tune this model with augmented data, it first needs to be fine tuned once with the current dataset to create a 'Base' model with version 1. Any further fine tuning run creates a new model with consecutively numbering.""")

                init_values_set = GlobalAppStateManager.get_or_create_session_state(
                    "init_values_set", False)

                # If no parent model exists because the model has not been trained yet, the model itself is used for setting default values
                parent_model: ComplexModelDTO = current_project_data.selected_model_for_fine_tuning.parent_model or current_project_data.selected_model_for_fine_tuning

                fine_tuning_model = None
                if parent_model.training_run:
                    fine_tuning_model = parent_model.training_run.fine_tuning_model

                # Filter training runs dtos which are used for seed selection by either selected model or preset model if no selected yet.,
                training_run_dtos: list[SimpleTrainingRunDTO] = service.filter_simple_training_runs(
                    GetTrainingRunsDTO(fine_tuning_model=st.session_state.get("chosen_fine_tuning_base_model") or fine_tuning_model))

                # Only set the init values once to not overwrite set values on reload
                if not init_values_set:

                    # Set default values
                    chosen_fine_tuning_base_model_index: int = 0
                    is_global: bool = False
                    epochs: int | None = None
                    learning_rate_multiplier: float | None = None
                    batch_size: int | None = None
                    seed_index: int | None = None

                    # Check if the parent model exists
                    if parent_model:
                        is_global = parent_model.is_global

                        # Check if the training run exists for the parent model
                        if parent_model.training_run:
                            # Find the index in the list for the fine-tuning model version
                            chosen_fine_tuning_base_model_index = backend_uf.find_index_in_list(
                                FineTuningModelVersions.openai.value, parent_model.training_run.fine_tuning_model, default=0)
                            # Set values from the parent model's training run
                            epochs = parent_model.training_run.epochs
                            learning_rate_multiplier = parent_model.training_run.learning_rate_multiplier
                            batch_size = parent_model.training_run.batch_size

                            # Create a list of seed values from the available training runs
                            seed_list: list[int] = [
                                training_run_dto.seed for training_run_dto in training_run_dtos if training_run_dto]
                            seed_index = backend_uf.find_index_in_list(
                                seed_list, parent_model.training_run.seed)

                    st.session_state["init_values_set"] = True

                model_global_columns = st.columns(3)

                with model_global_columns[0]:
                    chosen_fine_tuning_base_model: str = st.selectbox(label="Choose a model", options=FineTuningModelVersions.openai.value, index=chosen_fine_tuning_base_model_index, placeholder="Choose a fine tuning base model",
                                                                      key="chosen_fine_tuning_base_model", help="Choose a base model for this fine tuning run", label_visibility="collapsed", disabled=current_project_data.fine_tuning_step_counter != 1)

                with model_global_columns[1]:
                    is_global = st.checkbox(label="Make model global", value=is_global, key="globalize_model_checkbox",
                                            help="Globalized models can be selected in the list of available models when creating a new project", label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 1)

                with model_global_columns[2]:
                    save_checkpoint_models = st.checkbox(label="Save checkpoint models", value=current_project_data.save_checkpoint_models, key="save_checkpoint_models_checkbox",
                                                         help="In addition to creating a final fine-tuned model at the end of each fine-tuning job, some fine tuning companies will create one full model checkpoint for you at the end of each training epoch. These checkpoints are themselves full models that can be used as regular models. Checkpoints are useful as they potentially provide a version of your fine-tuned model from before it experienced overfitting.", label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 1)

                fine_tuning_config_columns = st.columns(3)

                with fine_tuning_config_columns[0]:
                    epochs: int = st.number_input(label="Amount of epochs", min_value=1, max_value=10, step=1, value=epochs, key="epochs",
                                                  help="The number of epochs to train the model for. An epoch refers to one full cycle through the training dataset. Defaults to auto. 1-10.", placeholder="auto", label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 1)
                with fine_tuning_config_columns[1]:
                    learning_rate_multiplier: float = st.number_input(label="Learning rate multiplier", min_value=0.1, max_value=10.0, step=0.1, value=learning_rate_multiplier, key="learning_rate_multiplier",
                                                                      help="Scaling factor for the learning rate. A smaller learning rate may be useful to avoid overfitting. Defaults to auto. 0.1-10.0", placeholder="auto", label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 1)
                with fine_tuning_config_columns[2]:
                    batch_size: int = st.number_input(label="Batch size", min_value=1, max_value=32, step=1, value=batch_size, key="batch_sizer",
                                                      help="Number of examples in each batch. A larger batch size means that model parameters are updated less frequently, but with lower variance. Defaults to auto. 1-32.", placeholder="auto", label_visibility="visible", disabled=current_project_data.fine_tuning_step_counter != 1)

                training_run_dto: SimpleTrainingRunDTO = st.selectbox(label="Seed", options=training_run_dtos, index=seed_index, placeholder="auto", help="The seed controls the reproducibility of the job. Passing in the same seed and job parameters for the same model should produce the same results, but may differ in rare cases. If a seed is not specified (or no other seeds exist), one will be generated for you.",
                                                                      label_visibility="visible", format_func=lambda dto: frontend_uf.display_dto(dto, formattings["TRAINING_RUN_DTO_SIMPLE"]), disabled=current_project_data.fine_tuning_step_counter != 1)

                seed = None
                if training_run_dto:
                    seed = training_run_dto.seed

                if current_project_data.fine_tuning_step_counter == 1:
                    st.button(
                        label="Train Model" if parent_model.version == 0 else "Save", key="submit_train_model", help="Submit the current fine tuning configuration", type="primary", on_click=create_new_model, args=(chosen_fine_tuning_base_model, parent_model, is_global, save_checkpoint_models, epochs, learning_rate_multiplier, batch_size, seed))

            load_model_configuration_inputs()

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
