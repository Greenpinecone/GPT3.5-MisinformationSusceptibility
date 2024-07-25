"""
This module provides the `QueryParamsManager` class for managing query parameters in a Streamlit application.
It includes functionality for setting and clearing query parameters based on session state and page configurations.

Classes:
    QueryParamsManager: Manages query parameters for Streamlit pages.
"""


import streamlit as st
from typing import Any
from dataclasses import is_dataclass, asdict
from app.frontend.classes.manager.toast_manager import ToastManager
from app.frontend.classes.manager.global_app_state_manager import GlobalAppStateManager
from app.backend.util.config import PAGE_CONFIG


class QueryParamsManager:
    """
    Manages query parameters for Streamlit pages.

    This class provides methods to clear query parameters, set query parameters based on page configurations,
    and fetch nested attributes from session state.

    Methods:
        clear_query_params: Clears all query parameters.
        set_query_params_from_page: Sets query parameters based on the page configuration.
        _set_query_params_from_session: Helper method to set query parameters from session state.
        fetch_nested_attribute: Retrieves nested attributes from an object.
    """

    @staticmethod
    def clear_query_params() -> None:
        """
        Clears all query parameters.
        """
        st.query_params.clear()

    @classmethod
    def set_query_params_from_page(cls, page_name: str) -> None:
        """
        Sets query parameters based on the page configuration.

        Args:
            page_name (str): The name of the page for which to set query parameters.

        Raises:
            ValueError: If the page name is not found in the configuration.
        """

        if not PAGE_CONFIG.get(page_name):
            raise ValueError(
                f"Page name '{page_name}' not found in configuration.")

        cls._set_query_params_from_session(page_name)

    @classmethod
    def _set_query_params_from_session(cls, page_name: str) -> None:
        """
        Helper method to set query parameters from session state.

        Args:
            page_name (str): The name of the page for which to set query parameters.

        Raises:
            ValueError: If the page name is not found in PAGE_CONFIG or if required session keys or attributes are missing.
        """

        missing_keys: list[str] = []

        # Ensure the page configuration exists for the given page name
        if not PAGE_CONFIG.get(page_name):
            raise ValueError(f"Page '{page_name}' not found in PAGE_CONFIG.")

        # Get the query parameters configuration for the specified page
        page_config = PAGE_CONFIG[page_name]
        params = page_config.get('query_params', {})

        # Initialize query parameters dictionary
        query_params = {}
        global_state = GlobalAppStateManager.get_global_states()

        # Build query parameters from session state
        for query_key, session_info in params.items():
            session_key = session_info[0]
            attributes = session_info[1]

            if session_key in global_state:
                session_value = global_state[session_key]
                attribute_value = cls.fetch_nested_attribute(
                    session_value, attributes)
                if attribute_value:
                    query_params[query_key] = attribute_value
                else:
                    # There should be a value but there is none
                    missing_keys.append(query_key)
            else:
                raise ValueError(
                    f"Session key '{session_key}' not found in global state")

        # Check for empty keys and raise an error if any
        if missing_keys:
            ToastManager.add_global_toasts(f"""Invalid session state has been detected, redirecting to home page and resetting invalid states. Invalid states: {
                missing_keys}""", "error")
            raise ValueError(f"""Invalid session state has been detected, redirecting to home page and resetting invalid states. Invalid states: {
                             missing_keys}""")
        else:
            # Set the query parameters using Streamlit's st.query_params.from_dict()
            st.query_params.from_dict(query_params)

    @staticmethod
    def fetch_nested_attribute(obj: Any, attrs: list[str]) -> Any:
        """
        Retrieves nested attributes from an object.

        Args:
            obj (Any): The object from which to fetch attributes.
            attrs (list[str]): A list of attribute names or indices to navigate through the object.

        Returns:
            Any: The value of the nested attribute.

        Raises:
            ValueError: If an attribute or index is not found or is invalid.
        """

        for idx, attr in enumerate(attrs):
            if isinstance(obj, dict):
                obj = obj.get(attr)
            elif isinstance(obj, list):
                try:
                    index = int(attr)
                    obj = obj[index]
                except (ValueError, IndexError):
                    raise ValueError(
                        f"List index '{attr}' is invalid for object '{obj}'")
            elif is_dataclass(obj):
                obj = asdict(obj).get(attr)
            elif hasattr(obj, attr):
                obj = getattr(obj, attr)
            elif idx == 0:
                raise ValueError(f"""Attribute '{attr}' not found in object of type '{
                                 type(obj).__name__}'""")
        return obj
