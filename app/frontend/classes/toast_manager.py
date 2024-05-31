import streamlit as st
from app.frontend.dataclasses.dataclasses import ToastMessage
from backend.util.config import GLOBAL_SESSION_STATE_KEYS


class ToastManager:

    @staticmethod
    def _initialize_global_toasts() -> None:
        """Ensure the global toasts session state is initialized."""
        if not st.session_state.get(GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']):
            st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']] = []

    @classmethod
    def add_global_toasts(cls, message: str, message_type: str = 'info') -> None:
        """Add a toast message to the global toasts."""
        cls._initialize_global_toasts()
        icon = cls.get_icon_for_message_type(message_type)
        st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']].append(
            ToastMessage(message, icon))

    @staticmethod
    def show_global_toasts() -> None:
        """Show all toasts from the global state."""
        if GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY'] in st.session_state and st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']]:
            for toast in st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']]:
                st.toast(body=toast.message, icon=toast.icon)
            # Clear toasts after showing
            st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']].clear()

    @classmethod
    def show_toast(cls, message: str, message_type: str = 'info') -> None:
        """Show a toast."""
        icon = cls.get_icon_for_message_type(message_type)
        st.toast(message, icon)

    @staticmethod
    def get_icon_for_message_type(message_type: str) -> str:
        """Get the icon for the given message type."""
        return {
            'info': "ℹ️",
            'warning': "❕",
            'success': "✅",
            'error': "❌"
        }.get(message_type, "ℹ️")
