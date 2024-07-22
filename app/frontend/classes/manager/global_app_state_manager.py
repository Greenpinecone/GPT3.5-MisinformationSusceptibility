"""
This module provides the `GlobalAppStateManager` class for managing global application states in a Streamlit application.
It includes functionality for managing session states, services, and current project data.

Classes:
    GlobalAppStateManager: Manages global application states and services.
"""

import streamlit as st
from typing import Any, Callable
from app.frontend.classes.page_navigator import PageNavigator
from app.backend.dtos.response import CurrentProjectDataDTO
from app.backend.dtos.update_request import UpdateCurrentProjectDataDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.backend.util.config import GLOBAL_SESSION_STATE_KEYS as global_keys


class GlobalAppStateManager:
    """
    Manages global application states and services.

    This class handles the initialization, retrieval, and updating of global application states,
    including the service manager and current project data.

    Methods:
        _ensure_global_states: Ensures the global states dictionary is initialized.
        _initialize_service: Initializes the service manager facade.
        reset_service: Resets the service manager with a new or default service.
        get_service: Retrieves the service manager facade from session state.
        set_service: Sets a new service manager facade in session state.
        get_current_project_data: Retrieves or initializes the current project data.
        update_current_project_data: Updates the current project data.
        get_global_states: Retrieves the global states dictionary.
        set_global_states: Sets the global states dictionary.
        get_or_create_session_state: Retrieves or creates a session state entry.
        clear_session_state: Clears session state entries except specified global keys.
        initialize_current_project_state: Initializes current project state and handles page navigation if needed.
    """

    @classmethod
    def _ensure_global_states(cls) -> None:
        if not st.session_state.get(global_keys["GLOBAL_STATES_KEY"]):
            st.session_state[global_keys["GLOBAL_STATES_KEY"]] = {}

    @staticmethod
    def _initialize_service() -> ServiceManagerFacade:
        return ServiceManagerFacade()

    @classmethod
    def reset_service(cls, new_service: ServiceManagerFacade | None = None) -> None:
        """
        Resets the service manager with a new or default service.

        Args:
            new_service (ServiceManagerFacade, optional): The new service manager facade. Defaults to None.
        """

        cls.service = new_service or cls._initialize_service()

    @classmethod
    def get_service(cls) -> ServiceManagerFacade:
        """
        Retrieves the service manager facade from session state.

        Returns:
            ServiceManagerFacade: The service manager facade.
        """

        cls._ensure_global_states()
        if global_keys["SERVICE_KEY"] not in st.session_state[global_keys["GLOBAL_STATES_KEY"]]:
            st.session_state[global_keys["GLOBAL_STATES_KEY"]][global_keys["SERVICE_KEY"]] = cls._initialize_service(
            )
        return st.session_state[global_keys["GLOBAL_STATES_KEY"]][global_keys["SERVICE_KEY"]]

    @classmethod
    def set_service(cls, new_service: ServiceManagerFacade) -> None:
        """
        Sets a new service manager facade in session state.

        Args:
            new_service (ServiceManagerFacade): The new service manager facade.
        """

        cls._ensure_global_states()
        st.session_state[global_keys["GLOBAL_STATES_KEY"]
                         ][global_keys["SERVICE_KEY"]] = new_service

    @classmethod
    def get_current_project_data(cls, service: ServiceManagerFacade) -> ServiceManagerFacade:
        """
        Retrieves or initializes the current project data.

        Args:
            service (ServiceManagerFacade): The service manager facade.

        Returns:
            CurrentProjectDataDTO: The current project data.
        """

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
        """
        Updates the current project data.

        Args:
            service (ServiceManagerFacade): The service manager facade.
            new_current_project_data (UpdateCurrentProjectDataDTO): The new current project data.

        Returns:
            CurrentProjectDataDTO: The updated current project data.
        """

        cls._ensure_global_states()
        updated_current_project_data: CurrentProjectDataDTO = service.update_current_project_data(
            new_current_project_data)[0]
        st.session_state[global_keys["GLOBAL_STATES_KEY"]
                         ][global_keys["CURRENT_PROJECT_DATA_KEY"]] = updated_current_project_data
        return updated_current_project_data

    @classmethod
    def get_global_states(cls) -> dict[str, Any]:
        """
        Retrieves the global states dictionary from session state.

        Returns:
            dict[str, Any]: The global states dictionary.
        """

        cls._ensure_global_states()
        return st.session_state[global_keys["GLOBAL_STATES_KEY"]]

    @classmethod
    def set_global_states(cls, new_global_states: dict[str, Any]) -> None:
        """
        Sets the global states dictionary in session state.

        Args:
            new_global_states (dict[str, Any]): The new global states dictionary.
        """

        st.session_state[global_keys["GLOBAL_STATES_KEY"]
                         ] = new_global_states

    @staticmethod
    def get_or_create_session_state(key: str, *args: Any, default_value: Any | Callable[..., Any] = None, **kwargs: Any) -> Any:
        """
        Retrieves or creates a session state entry.

        Args:
            key (str): The key for the session state entry.
            default_value (Any | Callable[..., Any], optional): The default value or callable to create the default value. Defaults to None.
            *args (Any): Additional arguments for the callable default value.
            **kwargs (Any): Additional keyword arguments for the callable default value.

        Returns:
            Any: The session state entry.
        """

        if not key in st.session_state:
            if callable(default_value):
                st.session_state[key] = default_value(*args, **kwargs)
            else:
                st.session_state[key] = default_value
        return st.session_state.get(key)

    @classmethod
    def clear_session_state(cls, clear_global_keys: list[str] = None) -> None:
        """
        Clears session state entries except specified global keys.

        Args:
            clear_global_keys (list[str], optional): List of global keys to clear. Defaults to None.
        """

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
        """
        Initializes current project state and handles page navigation if needed.

        Args:
            service (ServiceManagerFacade): The service manager facade.
            current_page (str): The current page identifier.

        Returns:
            CurrentProjectDataDTO: The current project data.
        """

        current_project_data: CurrentProjectDataDTO = cls.get_current_project_data(
            service)
        if current_project_data.unfinished_progress and current_project_data.current_page != current_page:
            PageNavigator.navigate_to_page(current_project_data.current_page)
        elif current_project_data.current_page != current_page:
            # Update data if page has changed
            current_project_data = cls.update_current_project_data(
                service, UpdateCurrentProjectDataDTO(id=current_project_data.id, current_page=current_page))

        return current_project_data
