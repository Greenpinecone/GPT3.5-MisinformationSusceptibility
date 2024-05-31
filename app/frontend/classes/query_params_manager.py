from typing import Any
import streamlit as st
from backend.util.config import GLOBAL_SESSION_STATE_KEYS, PAGE_CONFIG
from dataclasses import is_dataclass, asdict


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

    @staticmethod
    def _set_query_params_from_session(page_name: str) -> None:
        # Ensure the page configuration exists for the given page name
        if not PAGE_CONFIG.get(page_name):
            raise ValueError(f"Page '{page_name}' not found in PAGE_CONFIG.")

        # Get the query parameters configuration for the specified page
        page_config = PAGE_CONFIG[page_name]
        params = page_config.get('query_params', {})

        global_states_key = GLOBAL_SESSION_STATE_KEYS['GLOBAL_STATES_KEY']

        # Check if global states key exists in session state
        if not st.session_state.get(global_states_key):
            raise ValueError(f"""Global state '{
                             global_states_key}' not found in session state.""")

        # Initialize query parameters dictionary
        query_params = {}
        global_state = st.session_state[global_states_key]

        # Helper function to fetch attribute based on type
        def fetch_attribute(obj: Any, attr: str) -> Any:
            if isinstance(obj, dict):
                return obj.get(attr)
            elif isinstance(obj, list):
                try:
                    index = int(attr)
                    return obj[index]
                except (ValueError, IndexError):
                    raise ValueError(
                        f"List index '{attr}' is invalid for object '{obj}'")
            elif is_dataclass(obj):
                return asdict(obj).get(attr)
            elif hasattr(obj, attr):
                return getattr(obj, attr)
            else:
                raise ValueError(f"""Attribute '{attr}' not found in object of type '{
                                 type(obj).__name__}'""")

        # Build query parameters from session state
        for query_key, session_info in params.items():
            session_key = session_info[0]
            attribute = session_info[1]

            if session_key in global_state:
                session_value = global_state[session_key]
                attribute_value = fetch_attribute(session_value, attribute)
                if attribute_value is not None:
                    query_params[query_key] = attribute_value
                else:
                    raise ValueError(f"""Missing attribute '{
                                     attribute}' in session state for key '{session_key}'""")
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
