import streamlit as st
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.classes.dataframe_widget_provider import DataFrameWidgetProvider
from backend.util.logger import StreamlitLogger
from app.backend.dtos.get_request import *
from app.backend.dtos.response import *
from app.backend.dtos.create_request import *
from frontend.classes.toast_manager import ToastManager
from frontend.custom_styles.global_styles import apply_global_style
from frontend.custom_styles.individual_styles import center_checkboxes
from frontend.classes.query_params_manager import QueryParamsManager
from frontend.classes.page_navigator import PageNavigator
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from app.frontend.classes.datapoint_matcher import DataPointMatcher
from app.frontend.classes.datapoint_service import DataPointService

apply_global_style()
center_checkboxes()
errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)
current_page = "match_datapoint"


def save_intermediate_dataset_state(datapoint_matcher: DataPointMatcher, datapoints_to_update: list[DataPointDTO]) -> None:

    # If a test datapoint is selected and it has related datapoints added
    if datapoint_matcher.current_test_datapoint:
        if datapoint_matcher.current_test_datapoint.related_datapoints:
            DataPointService.replace_datapoint_in_list(
                datapoint_matcher.current_test_datapoint, datapoints_to_update)
        # if the related datapoints are empty and the datapoint still has not been updated, remove it again, since there is nothing to update
        elif DataPointService.is_present(datapoints_to_update, datapoint_matcher.current_test_datapoint):
            DataPointService.remove_datapoint_from_list(
                datapoint_matcher.current_test_datapoint, datapoints_to_update)

        # Save the intermediate update to the database and clear the current datapoints that have already been updated
        if len(datapoints_to_update) >= 3:
            DataPointService.update_datapoints(
                service, datapoints_to_update)
            datapoints_to_update.clear()


with logger:

    ToastManager.show_global_toasts()
    service: ServiceManagerFacade = GlobalAppStateManager.get_service()
    current_project_data: CurrentProjectDataDTO = GlobalAppStateManager.initialize_current_project_state(
        service, current_page)
    GlobalAppStateManager.update_current_project_data(service,
                                                      UpdateCurrentProjectDataDTO(id=current_project_data.id, unfinished_progress=True))
    current_dataset: ComplexDatasetDTO = current_project_data.currently_modified_dataset
    QueryParamsManager.set_query_params_from_page(
        current_page)
    datapoint_matcher: DataPointMatcher = GlobalAppStateManager.get_or_create_session_state(
        "datapoint_matcher", current_dataset.datapoints, current_dataset.test_dataset.datapoints, default_value=DataPointMatcher
    )
    # To stroe all updated test datapoints until a certain threshold is reached to save it to the database and retrieve it via the current_project_data.currently_modified_dataset again to restore states in case needed
    datapoints_to_update: list[DataPointDTO] = GlobalAppStateManager.get_or_create_session_state(
        "datapoints_to_update", default_value=list())

    save_intermediate_dataset_state(datapoint_matcher, datapoints_to_update)

    def load_page(datapoint_matcher: DataPointMatcher):
        st.title("Match Datapoints")

        datapoint_matcher.load()

        submit_button_cols = st.columns((2, 5, 1))
        with submit_button_cols[2]:
            submit_button = st.button(
                label="Submit", key="submit_datapoints",
                help="Submit matched datapoint configurations", type="primary"
            )
            if submit_button:
                if datapoints_to_update:
                    # Update only the not yet updated datapoints
                    updated_datapoints: list[DataPointDTO] = DataPointService.update_datapoints(
                        service, datapoints_to_update)

                GlobalAppStateManager.clear_session_state()
                GlobalAppStateManager.update_current_project_data(service,
                                                                  UpdateCurrentProjectDataDTO(id=current_project_data.id, currently_modified_dataset_id=None, unfinished_progress=False))
                ToastManager.add_global_toasts(
                    "Datapoints have been successfully matched.", "success")
                PageNavigator.navigate_to_page("create_model")
    load_page(datapoint_matcher)
