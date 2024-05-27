import streamlit as st
from backend.util.config import GLOBAL_SESSION_STATE_KEYS, PAGE_CONFIG


class QueryParamsManager:

    @classmethod
    def set_query_params_from_page(cls, page_name: str):
        if page_name not in PAGE_CONFIG:
            raise ValueError(
                f"Page name '{page_name}' not found in configuration.")

        params = PAGE_CONFIG[page_name]['query_params']
        cls._set_query_params_from_session(params)

    @staticmethod
    def _set_query_params_from_session(params: dict[str, list]):
        if GLOBAL_SESSION_STATE_KEYS['GLOBAL_STATES_KEY'] not in st.session_state:
            raise ValueError(f"""Global state '{
                             GLOBAL_SESSION_STATE_KEYS['GLOBAL_STATES_KEY']}' not found in session state.""")

        query_params = {}
        global_state = st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_STATES_KEY']]

        for query_key, session_info in params.items():
            session_key = session_info[0]
            if session_key in global_state:
                session_value = global_state[session_key]
                if len(session_info) > 1 and hasattr(session_value, session_info[1]):
                    attribute = session_info[1]
                    query_params[query_key] = getattr(
                        session_value, attribute, None)
                    if not query_params[query_key]:
                        raise ValueError(f"""Missing attribute '{
                                         attribute}' in session state for key '{session_key}'""")
                else:
                    query_params[query_key] = session_value
        if query_params:
            st.experimental_set_query_params(**query_params)

        missing_keys = [
            key for key in params.keys() if key not in query_params]
        if missing_keys:
            raise ValueError(f"Missing query parameters: {missing_keys}")
