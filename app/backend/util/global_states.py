import streamlit as st
from app.frontend.dataclasses.dataclasses import ToastMessage
from .utility_functions import get_or_create_session_state

global_toasts: list[ToastMessage] = get_or_create_session_state(
    "global_toasts", default_value=[])
