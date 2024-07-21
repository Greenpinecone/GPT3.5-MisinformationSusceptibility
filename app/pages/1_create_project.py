import streamlit as st
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from app.frontend.classes.page_navigator import PageNavigator
from app.frontend.classes.toast_manager import ToastManager
from app.frontend.custom_styles.global_styles import apply_global_style
from app.frontend.util import utility_functions as frontend_uf
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.backend.util.logger import StreamlitLogger
from app.backend.dtos.get_request import GetDatasetsDTO, GetModelsDTO
from app.backend.dtos.response import CurrentProjectDataDTO, DatasetDTO, ModelDTO, ProjectDTO
from app.backend.dtos.create_request import CreateProjectDTO
from app.backend.database.schema import DatasetCategory
from app.backend.util.config import DTO_LIST_FORMATTING_PRESETS as formattings

apply_global_style()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)
current_page = "create_project"

with logger:
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
        service, current_page)
    ToastManager.show_global_toasts()
    PageNavigator.set_navbar(
        "Go back", "home", "Return to the previous page")

    def load_page():
        st.title("Create Project")

        # Get all goobal datasets and models.
        models: list[ModelDTO] = service.filter_models(
            GetModelsDTO(is_global=True))
        datasets: list[DatasetDTO] = service.filter_datasets(
            GetDatasetsDTO(category=DatasetCategory.training, is_global=True))

        form_container = st.container(border=True)

        with form_container:
            @st.experimental_fragment
            def form_fragment():
                project_name: str = st.text_input(label="Project Name",
                                                  label_visibility="hidden", key="project_name_input", value=None, placeholder="Your project name...", max_chars=255)
                project_description: str = st.text_area(label="Project Description",
                                                        label_visibility="hidden", key="project_description_input",  value=None, placeholder="Your project description...", max_chars=4000)

                chosen_datasets: list[DatasetDTO] = st.multiselect(
                    label="Select datasets to associate with this project", label_visibility="hidden" if datasets else "visible", key="dataset_multi_selector", placeholder="Choose datasets to associate with this project",
                    options=datasets, format_func=lambda dto: frontend_uf.display_dto(dto, formattings["DATASETDTO_SIMPLE"]))

                chosen_models: list[ModelDTO] = st.multiselect(
                    label="Select models to associate with this project", label_visibility="hidden" if models else "visible", key="model_multi_selector", placeholder="Choose models to associate with this project",
                    options=models, format_func=lambda dto: frontend_uf.display_dto(dto, formattings["MODELDTO_SIMPLE"]))

                submitted = st.button(
                    "Submit", help="Click me to submit the form", type="primary", disabled=not project_name)

                if submitted:
                    chosen_model_ids = [model.id for model in chosen_models]
                    chosen_dataset_ids = [
                        dataset.id for dataset in chosen_datasets]
                    project_to_save = CreateProjectDTO(
                        project_name=project_name, description=project_description, model_ids=chosen_model_ids, dataset_ids=chosen_dataset_ids)

                    saved_project_dto: ProjectDTO = service.create_projects(
                        [project_to_save])
                    if saved_project_dto:
                        GlobalAppStateManager.clear_session_state()
                        ToastManager.add_global_toasts(
                            "Successfully created project.", "success")
                        PageNavigator.navigate_to_page('home')

            form_fragment()

    load_page()
