"""
A summary of utility functions used throughout the project.
"""

from typing import Any
import streamlit as st
from datetime import datetime


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
    if key not in st.session_state:
        if callable(default_value):
            st.session_state[key] = default_value(*args, **kwargs)
        else:
            st.session_state[key] = default_value
    return st.session_state[key]


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
