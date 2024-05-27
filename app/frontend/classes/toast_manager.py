import streamlit as st
from app.frontend.dataclasses.dataclasses import ToastMessage
from backend.util.global_states import global_toasts


class ToastManager:
    @classmethod
    def add_global_toasts(message: str, message_type: str = 'info'):
        """Add a toast message to the global toasts."""
        icon = ToastManager.get_icon_for_message_type(message_type)
        global_toasts.append(ToastMessage(message, icon))

    @staticmethod
    def show_global_toasts():
        """Show all toasts from the global state."""
        if global_toasts:
            for toast in global_toasts:
                st.toast(body=toast.message, icon=toast.icon)
            # Clear toasts after showing
            global_toasts.clear()

    @classmethod
    def show_toast(message: str, message_type: str = 'info'):
        """Show a toast."""
        icon = ToastManager.get_icon_for_message_type(message_type)
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
