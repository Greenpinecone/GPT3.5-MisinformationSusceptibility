import streamlit as st
from app.frontend.classes.manager.toast_manager import ToastManager
from app.frontend.custom_styles.global_styles import apply_global_style
from app.frontend.custom_styles.individual_styles import center_checkboxes
from app.frontend.classes.manager.query_params_manager import QueryParamsManager
from app.frontend.classes.page_navigator import PageNavigator
from app.frontend.classes.manager.global_app_state_manager import GlobalAppStateManager
from app.frontend.util import utility_functions as frontend_uf
from app.frontend.classes.dataframe_widget_provider import DataFrameWidgetProvider
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.backend.util.logger import StreamlitLogger
from app.backend.dtos.get_request import GetModelsDTO, GetProjectsDTO
from app.backend.dtos.response import CurrentProjectDataDTO, ModelWithOriginalProjectDTO, SimpleProjectDTO
from app.backend.util.config import DTO_LIST_FORMATTING_PRESETS as formattings

# Set the page configuration to wide
st.set_page_config(layout="wide")
apply_global_style()
center_checkboxes()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)
current_page = "model_overview"

with logger:

    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project_data, prev_page = GlobalAppStateManager.initialize_current_project_state(
        service, current_page)
    try:
        QueryParamsManager.set_query_params_from_page(current_page)
    except ValueError:
        GlobalAppStateManager.update_current_project_data(service, new_current_project_data=UpdateCurrentProjectDataDTO(
            id=current_project_data.id, current_project_id=None))
        PageNavigator.navigate_to_page("home")
    ToastManager.show_global_toasts()
    # Reset the selected statistic models on page change
    PageNavigator.set_navbar(
        "Go back", "home", "Return to the previous page", func=GlobalAppStateManager.update_current_project_data, args=(service, UpdateCurrentProjectDataDTO(id=current_project_data.id, selected_statistic_models=[])))

    def load_page():

        st.title("Model Overview")

        columns = st.columns([6.0, 1.5, 1.4])

        with columns[2]:
            PageNavigator.set_navbar(
                "Show statistics", "model_statistic", "Show the statistical analysis of the selected models", icon="▶️", is_left=False, func=GlobalAppStateManager.update_current_project_data, args=(service, UpdateCurrentProjectDataDTO(id=current_project_data.id, selected_statistic_models=st.session_state.get("selected_models") or [])), nav_bar_cols_config=[1], disabled=not st.session_state.get("selected_models"), type="primary")

            model_hierarchy_button = st.button(label="Model hierarchy ▶️", help="Shows the full model hierarchy statistics for the selected model. Only works with ONE selected model", disabled=len(
                st.session_state.get("selected_models", [])) != 1)

            if model_hierarchy_button:
                st.session_state.selected_models = service.get_model_hierarchy_ids(
                    st.session_state.get("selected_models")[0])
                GlobalAppStateManager.update_current_project_data(service, UpdateCurrentProjectDataDTO(
                    id=current_project_data.id, selected_statistic_models=st.session_state.selected_models))
                PageNavigator.navigate_to_page("model_statistic")

        text_input_cols = st.columns(3)

        with text_input_cols[0]:
            model_name: str = st.text_input(label="Input the desired models name", max_chars=255, placeholder="Search for a model by its name",
                                            label_visibility="hidden", help="Input the name of a model you like to search for", on_change=lambda: delattr(st.session_state, "all_models"))
        with text_input_cols[1]:
            model_version: str = st.text_input(label="Input the desired models version", max_chars=255, placeholder="Search for a model by its version",
                                               label_visibility="hidden", help="Input the version of a model you like to search for", on_change=lambda: delattr(st.session_state, "all_models"))

        projects: list[SimpleProjectDTO] = []
        with text_input_cols[2]:
            if not st.session_state.get("all_projects"):
                projects: list[SimpleProjectDTO] = service.filter_simple_projects(
                    GetProjectsDTO())

            all_projects: list[SimpleProjectDTO] = GlobalAppStateManager.get_or_create_session_state(
                "all_projects", default_value=projects)

            selected_project: SimpleProjectDTO = st.selectbox(label="Select a project", options=all_projects, index=None, placeholder="Chose a project",
                                                              label_visibility="hidden", format_func=lambda dto: frontend_uf.display_dto(dto, formattings["PROJECT_DTO_SIMPLE"]), on_change=lambda: delattr(st.session_state, "all_models"))

        models: list[ModelWithOriginalProjectDTO] = []
        if not st.session_state.get("all_models"):
            if not (model_name or model_version or selected_project):
                # Fetch all models to show all models selected for statistical analysis
                get_models: GetModelsDTO = GetModelsDTO()
            else:
                # Fetch all models for display based on the filter params
                get_models: GetModelsDTO = GetModelsDTO(
                    model_name=model_name or None, version=model_version or None, project_id=selected_project.id if selected_project else None)
            models: list[ModelWithOriginalProjectDTO] = service.filter_models_with_original_project(
                get_models)

        all_models: list[ModelWithOriginalProjectDTO] = GlobalAppStateManager.get_or_create_session_state(
            "all_models", default_value=models)
        selected_models: list[int] = GlobalAppStateManager.get_or_create_session_state(
            "selected_models", default_value=list())

        if all_models:
            # Create Models list with project headings
            current_project_id: int = None
            models_with_same_project: list[ModelWithOriginalProjectDTO] = []
            # Iterate through the sorted list of models
            for idx, model in enumerate(all_models, 1):

                # Check if the current model's project ID is different from the current_project_id
                if current_project_id != model.original_project.id:
                    # If current_project_id is not None, it means we're switching to a new project group
                    if current_project_id is not None:
                        # Display the models for the previous project
                        DataFrameWidgetProvider.display_models_data_editor(
                            service, models_with_same_project, selected_models)
                        # Clear the list for the new project group
                        models_with_same_project = []

                    # Update the current project ID
                    current_project_id = model.original_project.id

                    # Display the new project's name and description
                    st.markdown(f"#### {model.original_project.project_name}")
                    st.write(f'{model.original_project.description}')

                # Append the current model to the list of models with the same project
                models_with_same_project.append(model)

                # If it's the last model, ensure to display the remaining models
                if idx == len(all_models):
                    DataFrameWidgetProvider.display_models_data_editor(
                        service, models_with_same_project, selected_models)
        else:
            # extra space
            st.write("")
            st.write("")

            st.write("No models created yet")

    load_page()
