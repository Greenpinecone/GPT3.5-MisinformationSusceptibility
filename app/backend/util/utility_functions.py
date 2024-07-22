"""
A summary of utility functions used throughout the project.
"""

from typing import Any
from marshmallow import ValidationError
from datetime import datetime


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
    """
    Validate that a string is in ISO 8601 datetime format.

    Args:
        value (str): The string to validate.

    Raises:
        ValidationError: If the string is not in ISO 8601 format.
    """

    try:
        # Attempt to parse the string as ISO 8601
        datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        # Raise a validation error if the format is incorrect
        raise ValidationError("Invalid datetime format, must be ISO 8601.")

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


def find_index_in_list(values_list: list[Any], specific_value: Any, default: Any | None = None) -> Any:
    """
    Returns the index of the specific_value in values_list, or None if not found.

    Args:
        values_list (list): The list of values to search.
        specific_value: The specific value to find in the list.

    Returns:
        int or None: The index of the specific value in the list, or None if not found.
    """

    try:
        return values_list.index(specific_value)
    except ValueError:
        return default
