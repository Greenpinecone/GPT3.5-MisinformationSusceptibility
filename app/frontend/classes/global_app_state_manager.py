import streamlit as st
from app.backend.dtos.response import ProjectDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from typing import Any, Callable
from backend.util.config import GLOBAL_SESSION_STATE_KEYS


class GlobalAppStateManager:

    @classmethod
    def _ensure_global_states(cls) -> None:
        if not st.session_state.get(GLOBAL_SESSION_STATE_KEYS["GLOBAL_STATES_KEY"]):
            st.session_state[GLOBAL_SESSION_STATE_KEYS["GLOBAL_STATES_KEY"]] = {}

    @staticmethod
    def _initialize_service() -> ServiceManagerFacade:
        return ServiceManagerFacade()

    @classmethod
    def reset_service(cls, new_service: ServiceManagerFacade | None = None) -> None:
        cls.service = new_service or cls._initialize_service()

    @classmethod
    def get_service(cls) -> ServiceManagerFacade:
        cls._ensure_global_states()
        if GLOBAL_SESSION_STATE_KEYS["SERVICE_KEY"] not in st.session_state[GLOBAL_SESSION_STATE_KEYS["GLOBAL_STATES_KEY"]]:
            st.session_state[GLOBAL_SESSION_STATE_KEYS["GLOBAL_STATES_KEY"]][GLOBAL_SESSION_STATE_KEYS["SERVICE_KEY"]] = cls._initialize_service(
            )
        return st.session_state[GLOBAL_SESSION_STATE_KEYS["GLOBAL_STATES_KEY"]][GLOBAL_SESSION_STATE_KEYS["SERVICE_KEY"]]

    @classmethod
    def set_service(cls, new_service: ServiceManagerFacade) -> None:
        cls._ensure_global_states()
        st.session_state[GLOBAL_SESSION_STATE_KEYS["GLOBAL_STATES_KEY"]
                         ][GLOBAL_SESSION_STATE_KEYS["SERVICE_KEY"]] = new_service

    @classmethod
    def get_current_project(cls) -> ProjectDTO:
        cls._ensure_global_states()
        return st.session_state[GLOBAL_SESSION_STATE_KEYS["GLOBAL_STATES_KEY"]][GLOBAL_SESSION_STATE_KEYS["CURRENT_PROJECT_KEY"]]

    @classmethod
    def set_current_project(cls, new_current_project: ProjectDTO) -> None:
        cls._ensure_global_states()
        st.session_state[GLOBAL_SESSION_STATE_KEYS["GLOBAL_STATES_KEY"]
                         ][GLOBAL_SESSION_STATE_KEYS["CURRENT_PROJECT_KEY"]] = new_current_project

    @classmethod
    def get_global_states(cls) -> dict[str, Any]:
        cls._ensure_global_states()
        return st.session_state[GLOBAL_SESSION_STATE_KEYS["GLOBAL_STATES_KEY"]]

    @classmethod
    def set_global_states(cls, new_global_states: dict[str, Any]) -> None:
        st.session_state[GLOBAL_SESSION_STATE_KEYS["GLOBAL_STATES_KEY"]
                         ] = new_global_states

    @staticmethod
    def get_or_create_session_state(key: str, *args: Any, default_value: Any | Callable[..., Any] = None, **kwargs: Any) -> Any:
        print(st.session_state.get(key), key)
        if st.session_state.get(key) is not False and not st.session_state.get(key):
            if callable(default_value):
                st.session_state[key] = default_value(*args, **kwargs)
            else:
                st.session_state[key] = default_value
        return st.session_state.get(key)

    @classmethod
    def clear_session_state_except(cls, exceptions: list[str] = None) -> None:
        if exceptions is None:
            exceptions = [GLOBAL_SESSION_STATE_KEYS['GLOBAL_STATES_KEY']]
        keys_to_delete = [
            key for key in st.session_state.keys() if key not in exceptions]
        for key in keys_to_delete:
            del st.session_state[key]
