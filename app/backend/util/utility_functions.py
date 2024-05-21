"""
A summary of utility functions used throughout the project.
"""

from enum import Enum
from typing import Any, Tuple
from marshmallow import ValidationError
import streamlit as st
from datetime import datetime
import streamlit as st
from pathlib import Path

from app.frontend.dataclasses.dataclasses import ToastMessage
from .config import Config
from ..service.implementations.service_manager_facade import ServiceManagerFacade
from ..custom_types.exceptions import CustomValidationError


def get_or_create_session_state(key: str, *args: Any, default_value: Any = None, **kwargs: Any) -> Any:
    """
    Retrieves an object from the Streamlit session state, creating it with default_value
    or a constructor with args and kwargs if it does not exist.

    Args:
        key (str): The key in the session state dictionary.
        default_value (Union[T, Callable[..., T]]): The default value to set if the key doesn't exist.
                                                    Can be a value or a callable that returns a value of type T.
        *args (Any): Arguments to pass to the default_value callable if it's a constructor.
        **kwargs (Any): Keyword arguments to pass to the default_value callable if it's a constructor.

    Returns:
        T: The value from the session state corresponding to the key, or the newly created value.
    """
    if not st.session_state.get(key):
        if callable(default_value):
            st.session_state[key] = default_value(*args, **kwargs)
        else:
            st.session_state[key] = default_value
    return st.session_state.get(key)


def get_current_date_time_formatted() -> str:
    """
    Gets the current date and time, formatted as a string.

    The format for the output string is "YYYY_MM_DD:HH_MM_SS", 
    where YYYY is the year, MM is the month, DD is the day, 
    HH is the hour (24-hour clock), MM is the minute, and SS is the second.

    Returns:
        str: The current date and time formatted as a string.
    """
    return datetime.now().strftime("%Y_%m_%d:%H_%M_%S")


def validate_iso_datetime(value: str):
    try:
        # Attempt to parse the string as ISO 8601
        datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        # Raise a validation error if the format is incorrect
        raise ValidationError("Invalid datetime format, must be ISO 8601.")


def initialize_global_states(serviceInstance: ServiceManagerFacade, configInstance: Config) -> tuple[ServiceManagerFacade, Config]:

    service: serviceInstance
    config: configInstance

    if not st.session_state.get("service"):
        service = get_or_create_session_state(
            "service", default_value=serviceInstance)
    else:
        service = st.session_state.get("service")

    if not st.session_state.get("config"):
        config = get_or_create_session_state(
            "config", default_value=configInstance)
    else:
        config = st.session_state.get("config")

    return service, config


# Shows all stored toast messages once. Useful for occasions where you need to reload the page which would swollow the toast message if shown immediately.
def show_one_time_toast_messages(toast_messages: list[ToastMessage]):
    for toast_message in toast_messages:
        show_toast(toast_message.message, toast_message.type)
    toast_messages.clear()


def cleanup_and_navigate(page: str, keys: list[str]):
    clear_session_state_except(keys)
    navigate_to_page(page)


# Initial extra styles for buttons
    """ Override secondary button style */
    button[data-testid="baseButton-secondary"] {
        background-color: #22c55e; /* Green color */
        border: none;
        color: white;
    }
    /* Custom style for tertiary button by reusing old secondary style */
    button[data-testid="baseButton-tertiary"] {
        background-color: #e0e0e0; /* Light grey color */
        border: 1px solid #ced4da; /* Light grey border */
        color: black;
    }"""


def apply_global_style():
    st.markdown("""
    <style>
    /* General styles for all widgets inside #root */
    #root, #root .stButton, #root .stTextInput, #root .stDataFrame, #root .stPlotlyChart, #root .stAlert {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        justify-content: center;
        width: 100%;
    }
    
    /* Make the Checkbox centered to the height and width of the outer container - TODO: Center vertically! */
    #root .stCheckbox, #root .checkbox {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        justify-content: center;
        width: 100%;
        height: 100%
    }
    
    /* Additional specific style for .stJson */
    #root .object-key-val, #root .object-content, #root .stCodeBlock {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        text-align: left;
        justify-content: flex-start;
        width: 100%;
    }
    
    #root .stCodeBlock, #root .stExpanderDetails .stMarkdown pre {
            overflow-x: auto;  /* Activates horizontal scrolling */
            white-space: pre;  /* Ensures whitespace is preserved */
        }
    
    /* Style separators */
    hr {
        height: 2px;
        margin-top: 14px;
    }
    </style>
    """, unsafe_allow_html=True)


def navigate_to_page(page: str):
    st.switch_page(page)


def clear_session_state_except(exceptions):
    """
    Clears all keys in the streamlit session state except those specified.

    Args:
    exceptions (list of str): Keys that should not be deleted from the session state.
    """
    keys_to_delete = [key for key in st.session_state.keys()
                      if key not in exceptions]
    for key in keys_to_delete:
        del st.session_state[key]


def sort_dicts(list_of_objects: list[object],
               *sort_keys: str,
               priority_enum: Enum | None = None,
               enum_key: str = '',  # Default enum_key to 'type'
               descending: bool = True) -> list[object]:
    """
    Sorts a list of objects based on multiple sorting keys in specified order. Datetime object are sorted descending, everything else, ascending.
    """

    def sort_key(x: object) -> tuple:
        # Initialize the tuple for sorting
        sort_tuple = []

        # Handle priority enum if specified
        if enum_key:
            enum_value = getattr(x, enum_key, None)
            is_priority = (enum_value == priority_enum) if isinstance(
                enum_value, Enum) else False
            # Priority is handled inversely; true priorities come first
            sort_tuple.append(not is_priority)

        # Append other sorting keys to the tuple
        for key in sort_keys:
            value = getattr(x, key, None)
            if isinstance(value, datetime):
                # Apply descending order if the key is a datetime type
                sort_tuple.append((-value.timestamp())
                                  if descending else value.timestamp())
            else:
                # For other types, use ascending order by default
                sort_tuple.append(value)

        return tuple(sort_tuple)

    # Sort using the constructed key, respect the 'descending' for the first key only
    sorted_list = sorted(list_of_objects, key=sort_key)
    return sorted_list


def clear_query_params():
    st.query_params.clear()


def set_query_params_from_session(params: dict, config: Config):
    """
    Sets query parameters based on the session state keys provided in the params dictionary. The value in params
    should be a list where the first element is the key in st.session_state, and the optional second element is an
    attribute of the object to fetch from the session state.

    Args:
    params (dict): A dictionary where keys are the query parameter names and the values are lists. The first element
                   of the list is the session state key, and the optional second element is the attribute of the object
                   from the session state to use as the value.
    """
    query_params = {}
    for query_key, session_info in params.items():
        session_key = session_info[0]
        if session_key in st.session_state:
            session_value = st.session_state[session_key]
            if len(session_info) > 1 and hasattr(session_value, session_info[1]):
                # If an attribute is specified and it exists, fetch it
                attribute = session_info[1]
                query_params[query_key] = getattr(
                    session_value, attribute, None)

                if not query_params[query_key]:
                    raise CustomValidationError(
                        message="A query parameter is missing during operation", operation_type="Setting query params", errors=query_params)
            else:
                # Otherwise, use the whole session value
                query_params[query_key] = session_value
    if query_params:
        st.query_params.from_dict(query_params)

    missing_keys = [key for key in params.keys() if key not in query_params]
    if missing_keys:
        raise CustomValidationError(
            message=f"Missing query parameters:",
            operation_type="Setting query params",
            errors=missing_keys)


def set_navbar(label: str, previous_page: str, help: str, icon: Any = "◀️"):
    nav_bar_cols = st.columns(10)
    nav_bar_cols[0].page_link(
        previous_page, label=label, icon=icon, help=help)


def create_text_divider(text: str = None):
    if text:
        divider_cols = st.columns((5, 1, 5))
        divider_cols[0].divider()
        divider_cols[1].write(text)
        divider_cols[2].divider()
    else:
        st.divider()


def show_toast(message, message_type='info'):
    """Show custom toast messages in Streamlit.

    Args:
    message (str): The message to display.
    message_type (str): Type of the message (info, warning, success, error).
    """
    icon = ""
    if message_type == 'info':
        icon = "ℹ️"
    elif message_type == 'warning':
        icon = "⚠️"
    elif message_type == 'success':
        icon = "✅"
    elif message_type == 'error':
        icon = "❌"
    else:
        # Default to info if something else is provided
        icon = "ℹ️"

    st.toast(body=message, icon=icon)
