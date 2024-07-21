import streamlit as st
from typing import Any
from dataclasses import is_dataclass, asdict
from app.frontend.classes.global_app_state_manager import GlobalAppStateManager
from app.backend.util.config import PAGE_CONFIG


class QueryParamsManager:

    @staticmethod
    def clear_query_params() -> None:
        st.query_params.clear()

    @classmethod
    def set_query_params_from_page(cls, page_name: str) -> None:
        if not PAGE_CONFIG.get(page_name):
            raise ValueError(
                f"Page name '{page_name}' not found in configuration.")

        cls._set_query_params_from_session(page_name)

    @classmethod
    def _set_query_params_from_session(cls, page_name: str) -> None:
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
                if attribute_value is not None:
                    query_params[query_key] = attribute_value
                else:
                    raise ValueError(f"""Missing attribute '{
                                     attributes}' in session state for key '{session_key}'""")
            else:
                raise ValueError(
                    f"Session key '{session_key}' not found in global state")

        # Set the query parameters using Streamlit's st.query_params.from_dict()
        if query_params:
            st.query_params.from_dict(query_params)

        # Check for missing keys and raise an error if any
        missing_keys = [
            key for key in params.keys() if not query_params.get(key)]
        if missing_keys:
            raise ValueError(f"Missing query parameters: {missing_keys}")

    @staticmethod
    def fetch_nested_attribute(obj: Any, attrs: list[str]) -> Any:
        for attr in attrs:
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
            else:
                raise ValueError(f"""Attribute '{attr}' not found in object of type '{
                                 type(obj).__name__}'""")
        return obj
