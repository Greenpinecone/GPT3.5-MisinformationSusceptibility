import streamlit as st
from io import BytesIO
from app.frontend.classes.dataframe_editor import DataFrameEditor
from app.frontend.classes.dataset_editor import DatasetEditor
from app.frontend.classes.dataset_service import DatasetService
from app.frontend.classes.paginator import Paginator
from app.frontend.classes.toast_manager import ToastManager
from app.frontend.custom_styles.global_styles import apply_global_style
from app.frontend.classes.query_params_manager import QueryParamsManager
from app.frontend.classes.page_navigator import PageNavigator
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.backend.util.logger import StreamlitLogger
from app.backend.util import utility_functions as backend_uf
from app.backend.util.config import UPLOAD_FORMAT_FORMATTINGS
from app.backend.dtos.response import ComplexDatasetDTO, ProjectDTO, CurrentProjectDataDTO
from app.backend.database.schema import DatasetCategory, FineTuningCompany, FineTuningModelVersions, UploadFormats

apply_global_style()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)
current_page = "create_dataset"


def load_choose_file_format_form(dataset_editor: DatasetEditor, uploaded_dataset_file: BytesIO, all_dataset_editors: list[DatasetEditor]) -> None:
    """Loads the form to choose file format for the uploaded dataset."""
    create_formatting_examples_tabs()
    options = [company for company in FineTuningCompany]
    index = backend_uf.find_index_in_list(
        options, dataset_editor.chosen_company, default=0)

    formatting_cols = st.columns(3)

    # Select box for choosing company formatting style
    with formatting_cols[0]:
        chosen_company: FineTuningCompany = st.selectbox(
            label="Choose a company formatting style",
            options=options, index=index, format_func=lambda company: company.value,
            placeholder="Choose a company's formatting style", key="chosen_company_selectbox",
            help="Choose the formatting style for the file to upload based on company.",
            label_visibility="collapsed",
            disabled=DatasetService.check_if_dataset_editor_has_datapoints(
                all_dataset_editors) or uploaded_dataset_file is not None
        )
        DatasetService.update_dataset_editor_if_changed(
            "chosen_company", chosen_company, all_dataset_editors)

    options = FineTuningModelVersions[chosen_company.value].value if chosen_company else [
    ]
    index = backend_uf.find_index_in_list(
        options, dataset_editor.chosen_model, default=0)

    # Select box for choosing company model
    with formatting_cols[1]:
        chosen_model: str = st.selectbox(
            label="Choose a company model",
            options=options, index=index,
            placeholder="Choose a model", key="chosen_model_selectbox",
            help="Choose a model from the selected company you want to upload data for.",
            label_visibility="collapsed",
            disabled=DatasetService.check_if_dataset_editor_has_datapoints(
                all_dataset_editors) or uploaded_dataset_file is not None
        )
        DatasetService.update_dataset_editor_if_changed(
            "chosen_model", chosen_model, all_dataset_editors)

    options = UploadFormats[chosen_company.value].value[chosen_model] if chosen_model else [
    ]
    index = backend_uf.find_index_in_list(
        options, dataset_editor.chosen_file_format, default=0)

    # Select box for choosing upload file format
    with formatting_cols[2]:
        chosen_file_format: str = st.selectbox(
            label="Choose an upload file format",
            options=options, index=index,
            placeholder="Choose file format", key="chosen_file_format_selectbox",
            help="Choose the format of the file you want to upload and the datapoints you want to create",
            label_visibility="collapsed",
            disabled=DatasetService.check_if_dataset_editor_has_datapoints(
                all_dataset_editors) or uploaded_dataset_file is not None
        )
        formatting_changed = DatasetService.update_dataset_editor_if_changed(
            "chosen_file_format", chosen_file_format, all_dataset_editors)

    # Select box for choosing dataset category
    options = [dataset_category for dataset_category in DatasetCategory]
    index = 0
    selected_dataset: DatasetCategory = st.selectbox(
        label=" ",
        options=options,
        index=index, format_func=lambda x: x.value,
        key="dataset_category_selectbox", help="Select the dataset category the dataset falls into.",
        placeholder="Choose the dataset type", label_visibility="visible"
    )

    if formatting_changed:
        st.rerun()


def create_formatting_examples_tabs():
    """Creates tabs for formatting examples."""
    companies = list(UPLOAD_FORMAT_FORMATTINGS.keys())
    company_tabs = st.tabs(companies)

    for tab, company in zip(company_tabs, companies):
        with tab:
            format_dict = UPLOAD_FORMAT_FORMATTINGS.get(company)
            with st.expander(label=f"{company.capitalize()} formatting examples", expanded=False):
                format_tabs = st.tabs(list(format_dict.keys()))
                for format_key, format_tab in zip(format_dict.keys(), format_tabs):
                    with format_tab:
                        st.code(format_dict[format_key], line_numbers=True)


@st.experimental_fragment
def load_dataset_input_form():
    """Loads the dataset input form."""
    st.markdown("###### Set the dataset info")
    cols = st.columns(2)
    # Input for dataset name
    with cols[0]:
        st.text_input(label="The datasets name", value=None, max_chars=255, key="dataset_name_input",
                      help="Input the name of your dataset", placeholder="The dataset's name...", label_visibility="collapsed")
    # Checkbox for global availability
    with cols[1]:
        st.checkbox(label="Make the dataset globally available", value=False, key="globalize_dataset_checkbox",
                    help="Globalized datasets can be selected in the list of available datasets when creating a new project", label_visibility="visible")


with logger:

    ToastManager.show_global_toasts()
    PageNavigator.set_navbar(
        "Go back", "create_model", "Return to the previous page")
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
        service, current_page)
    current_project: ProjectDTO = current_project_data.current_project
    QueryParamsManager.set_query_params_from_page(
        current_page)

    # Initialize DatasetEditor for training and test datasets with corresponding paginator
    trainings_dataset_paginator = GlobalAppStateManager.get_or_create_session_state(
        "trainings_dataset_paginator", default_value=Paginator
    )
    training_dataset_editor: DatasetEditor = GlobalAppStateManager.get_or_create_session_state(
        "training_dataset_editor", DatasetCategory.training, DataFrameEditor, trainings_dataset_paginator, default_value=DatasetEditor
    )
    test_dataset_paginator = GlobalAppStateManager.get_or_create_session_state(
        "test_dataset_paginator", default_value=Paginator
    )
    test_dataset_editor: DatasetEditor = GlobalAppStateManager.get_or_create_session_state(
        "test_dataset_editor", DatasetCategory.test, DataFrameEditor, test_dataset_paginator, default_value=DatasetEditor
    )

    # Determine the current dataset editor based on the chosen upload dataset type
    dataset_editor = training_dataset_editor if GlobalAppStateManager.get_or_create_session_state(
        "dataset_category_selectbox", default_value=DatasetCategory.training) == DatasetCategory.training else test_dataset_editor
    all_dataset_editors = [training_dataset_editor, test_dataset_editor]

    def load_page(dataset_editor: DatasetEditor, all_dataset_editors: list[DatasetEditor]):
        st.title("Create Dataset")
        # Container for file format selection
        chosen_file_format_container = st.container()
        # File uploader widget
        uploaded_dataset_file: BytesIO = st.file_uploader(
            label="Upload a new dataset",
            type=dataset_editor.chosen_file_format,
            key=dataset_editor.file_uploader_key,
            accept_multiple_files=False,
            help="Upload a file formatted in the format chosen. Uploaded datasets will be directly available to select within your project after submitting.",
            disabled=False if dataset_editor.chosen_file_format else True,
            on_change=dataset_editor.clear_current_datapoints
        )

        with chosen_file_format_container:
            load_choose_file_format_form(
                dataset_editor, uploaded_dataset_file, all_dataset_editors)

        load_dataset_input_form()

        # Display label and delete button for the uploaded dataset file
        label = dataset_editor.currently_uploaded_file.name if dataset_editor.currently_uploaded_file else uploaded_dataset_file.name if uploaded_dataset_file else None
        if label:
            delete_dataset_button = st.button(
                label=label + "✖️",
                help="Remove the uploaded dataset with all datapoints",
                type="secondary"
            )
            if delete_dataset_button:
                ToastManager.add_global_toasts(
                    "Successfully removed dataset.", "success")
                dataset_editor.reset_editor_states()

        pagination_buttons_container_above = st.container()
        datapoints_container = st.container()
        pagination_buttons_container_below = st.container()

        dataset_editor.manage_datapoints_flow(
            uploaded_dataset_file, datapoints_container
        )

        # Display pagination buttons only when more items than fit on one page
        if len(dataset_editor.datapoints) > dataset_editor.paginator.items_per_page:
            # dataset_editor.paginator.get_paginated_items(
            #     dataset_editor.datapoints)
            dataset_editor.paginator.create_pagination_buttons(
                pagination_buttons_container_above, dataset_editor.datapoints)
            dataset_editor.paginator.create_pagination_buttons(
                pagination_buttons_container_below, dataset_editor.datapoints)

        cols = st.columns((2, 5, 1))
        # Button to add a new datapoint
        with cols[0]:
            add_new_datapoint_button = st.button(
                label="Add New Datapoint", key="add_new_datapoint_button",
                help="Add a new datapoint to the current dataset", type="secondary",
                disabled=not dataset_editor.chosen_file_format
            )
            if add_new_datapoint_button:
                dataset_editor.open_add_datapoint_dialog(datapoints_container)

        # Submit button to submit the datasets and datapoints
        with cols[2]:
            submit_button = st.button(
                label="Submit", key="submit_dataset",
                help="Submit both datasets with all their datapoints", type="primary",
                disabled=not all_dataset_editors[0].datapoints
            )
            if submit_button:
                saved_dataset_dto: ComplexDatasetDTO = DatasetService.process_and_create_dataset(
                    all_dataset_editors, GlobalAppStateManager.get_or_create_session_state("globalize_dataset_checkbox", None), GlobalAppStateManager.get_or_create_session_state("dataset_name_input", None), current_project.id, service)[0]
                if saved_dataset_dto:
                    ToastManager.add_global_toasts(
                        "Dataset has been successfully created.", "success")
                    # Match training and test datapoints if a test dataset has been uploaded
                    if saved_dataset_dto.test_dataset:
                        GlobalAppStateManager.update_current_project_data(service,
                                                                          UpdateCurrentProjectDataDTO(id=current_project_data.id, currently_modified_dataset_id=saved_dataset_dto.id))
                        GlobalAppStateManager.clear_session_state()
                        PageNavigator.navigate_to_page("match_datapoint")
                    else:
                        GlobalAppStateManager.update_current_project_data(service,
                                                                          UpdateCurrentProjectDataDTO(id=current_project_data.id, currently_modified_dataset_id=None))
                        PageNavigator.navigate_to_page("create_model")

    load_page(dataset_editor, all_dataset_editors)
