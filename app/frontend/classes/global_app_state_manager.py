import streamlit as st
from typing import Any, Callable
from app.frontend.classes.page_navigator import PageNavigator
from app.backend.dtos.response import CurrentProjectDataDTO
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.backend.util.config import GLOBAL_SESSION_STATE_KEYS as global_keys


class GlobalAppStateManager:

    @classmethod
    def _ensure_global_states(cls) -> None:
        if not st.session_state.get(global_keys["GLOBAL_STATES_KEY"]):
            st.session_state[global_keys["GLOBAL_STATES_KEY"]] = {}

    @staticmethod
    def _initialize_service() -> ServiceManagerFacade:
        return ServiceManagerFacade()

    @classmethod
    def reset_service(cls, new_service: ServiceManagerFacade | None = None) -> None:
        cls.service = new_service or cls._initialize_service()

    @classmethod
    def get_service(cls) -> ServiceManagerFacade:
        cls._ensure_global_states()
        if global_keys["SERVICE_KEY"] not in st.session_state[global_keys["GLOBAL_STATES_KEY"]]:
            st.session_state[global_keys["GLOBAL_STATES_KEY"]][global_keys["SERVICE_KEY"]] = cls._initialize_service(
            )
        return st.session_state[global_keys["GLOBAL_STATES_KEY"]][global_keys["SERVICE_KEY"]]

    @classmethod
    def set_service(cls, new_service: ServiceManagerFacade) -> None:
        cls._ensure_global_states()
        st.session_state[global_keys["GLOBAL_STATES_KEY"]
                         ][global_keys["SERVICE_KEY"]] = new_service

    @classmethod
    def get_current_project_data(cls, service: ServiceManagerFacade) -> ServiceManagerFacade:
        cls._ensure_global_states()
        if global_keys["CURRENT_PROJECT_DATA_KEY"] not in st.session_state[global_keys["GLOBAL_STATES_KEY"]]:
            current_project_data: CurrentProjectDataDTO = service.get_or_create_current_project_data()[
                0]
            st.session_state[global_keys["GLOBAL_STATES_KEY"]
                             ][global_keys["CURRENT_PROJECT_DATA_KEY"]] = current_project_data
        else:
            current_project_data = st.session_state[global_keys["GLOBAL_STATES_KEY"]
                                                    ][global_keys["CURRENT_PROJECT_DATA_KEY"]]
        return current_project_data

    @classmethod
    def update_current_project_data(cls, service: ServiceManagerFacade, new_current_project_data: UpdateCurrentProjectDataDTO) -> None:
        cls._ensure_global_states()
        updated_current_project_data: CurrentProjectDataDTO = service.update_current_project_data(
            new_current_project_data)[0]
        st.session_state[global_keys["GLOBAL_STATES_KEY"]
                         ][global_keys["CURRENT_PROJECT_DATA_KEY"]] = updated_current_project_data
        return updated_current_project_data

    @classmethod
    def get_global_states(cls) -> dict[str, Any]:
        cls._ensure_global_states()
        return st.session_state[global_keys["GLOBAL_STATES_KEY"]]

    @classmethod
    def set_global_states(cls, new_global_states: dict[str, Any]) -> None:
        st.session_state[global_keys["GLOBAL_STATES_KEY"]
                         ] = new_global_states

    @staticmethod
    def get_or_create_session_state(key: str, *args: Any, default_value: Any | Callable[..., Any] = None, **kwargs: Any) -> Any:
        if not key in st.session_state:
            if callable(default_value):
                st.session_state[key] = default_value(*args, **kwargs)
            else:
                st.session_state[key] = default_value
        return st.session_state.get(key)

    @classmethod
    def clear_session_state(cls, clear_global_keys: list[str] = None) -> None:
        # Clears all session states except globals
        global_exceptions = [global_keys['GLOBAL_STATES_KEY']]
        keys_to_delete = [
            key for key in st.session_state.keys() if key not in global_exceptions]
        for key in keys_to_delete:
            del st.session_state[key]

        # Set global states None to avoid
        if clear_global_keys:
            for key in clear_global_keys:
                if key in st.session_state[global_keys['GLOBAL_STATES_KEY']]:
                    del st.session_state[global_keys['GLOBAL_STATES_KEY']][key]

    # Sets the current project data and updates / navigates if needed
    @classmethod
    def initialize_current_project_state(cls, service: ServiceManagerFacade, current_page: str) -> CurrentProjectDataDTO:
        current_project_data: CurrentProjectDataDTO = cls.get_current_project_data(
            service)
        if current_project_data.unfinished_progress and current_project_data.current_page != current_page:
            PageNavigator.navigate_to_page(current_project_data.current_page)
        elif current_project_data.current_page != current_page:
            # Update data if page has changed
            current_project_data = cls.update_current_project_data(
                service, UpdateCurrentProjectDataDTO(id=current_project_data.id, current_page=current_page))

        # print("\n\n\n\n\n\nCURRENT PROJECT STATE:",
        #       current_project_data, "\n\n\n\n\n\n")
        return current_project_data
