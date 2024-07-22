"""
This module provides the `ToastManager` class for managing toast notifications in a Streamlit application.
It includes functionality for adding, displaying, and managing global toast messages.

Classes:
    ToastManager: Manages toast notifications for Streamlit pages.
"""


import streamlit as st
from app.frontend.dataclasses.dataclasses import ToastMessage
from app.backend.util.config import GLOBAL_SESSION_STATE_KEYS


class ToastManager:
    """
    Manages toast notifications for Streamlit pages.

    This class provides methods to add, display, and manage global toast messages.
    It ensures the toast messages are stored in the session state and can be displayed or cleared as needed.

    Methods:
        _initialize_global_toasts: Ensure the global toasts session state is initialized.
        add_global_toasts: Add a toast message to the global toasts.
        show_global_toasts: Show all toasts from the global state.
        show_toast: Show a single toast message.
        get_icon_for_message_type: Get the icon for the given message type.
    """

    @staticmethod
    def _initialize_global_toasts() -> None:
        """
        Ensure the global toasts session state is initialized.
        """
        if not st.session_state.get(GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']):
            st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']] = []

    @classmethod
    def add_global_toasts(cls, message: str, message_type: str = 'info') -> None:
        """
        Add a toast message to the global toasts.

        Args:
            message (str): The message to be displayed.
            message_type (str): The type of the message (e.g., 'info', 'warning', 'success', 'error'). Defaults to 'info'.
        """

        cls._initialize_global_toasts()
        icon = cls.get_icon_for_message_type(message_type)
        st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']].append(
            ToastMessage(message, icon))

    @staticmethod
    def show_global_toasts() -> None:
        """
        Show all toasts from the global state.

        This method retrieves all toast messages stored in the session state and displays them.
        After displaying the messages, it clears the toasts from the session state.
        """

        if GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY'] in st.session_state and st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']]:
            for toast in st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']]:
                st.toast(toast.message, icon=toast.icon)
            # Clear toasts after showing
            st.session_state[GLOBAL_SESSION_STATE_KEYS['GLOBAL_TOASTS_KEY']].clear()

    @classmethod
    def show_toast(cls, message: str, message_type: str = 'info') -> None:
        """
        Show a toast message.

        Args:
            message (str): The message to be displayed.
            message_type (str): The type of the message (e.g., 'info', 'warning', 'success', 'error'). Defaults to 'info'.
        """

        icon = cls.get_icon_for_message_type(message_type)
        st.toast(message, icon=icon)

    @staticmethod
    def get_icon_for_message_type(message_type: str) -> str:
        """
        Get the icon for the given message type.

        Args:
            message_type (str): The type of the message (e.g., 'info', 'warning', 'success', 'error').

        Returns:
            str: The icon corresponding to the message type.
        """

        return {
            'info': "ℹ️",
            'warning': "❕",
            'success': "✅",
            'error': "❌"
        }.get(message_type, "ℹ️")
