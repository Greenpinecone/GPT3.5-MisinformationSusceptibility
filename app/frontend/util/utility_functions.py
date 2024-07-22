"""
A module containing utility functions explicitly created for the frontend.
"""


import streamlit as st
from datetime import datetime
from enum import Enum


def sort_dicts(list_of_objects: list[object],
               *sort_keys: str,
               priority_enum: Enum | None = None,
               enum_key: str = '',
               descending: bool = True) -> list[object]:
    """
    Sorts a list of objects based on multiple sorting keys in the specified order.

    Args:
        list_of_objects (List[object]): List of objects to be sorted.
        sort_keys (str): Keys used for sorting.
        priority_enum (Enum, optional): Enum to prioritize certain values.
        enum_key (str, optional): Key to identify the enum attribute in the objects.
        descending (bool, optional): Flag to sort datetime objects in descending order.

    Returns:
        List[object]: Sorted list of objects.
    """

    def sort_key(x: object) -> tuple:
        """
        Sorts a list of objects based on multiple sorting keys in specified order. Datetime object are sorted descending, everything else, ascending.
        """
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


def create_text_divider(text: str = None, column_partitions: list[int] = [5, 1, 5]):
    """
    Creates a text divider with optional text centered between dividers.

    Args:
        text (str, optional): Text to display in the center of the divider.
        column_partitions (List[int], optional): List of column widths for the divider.
    """

    if text:
        divider_cols = st.columns(column_partitions)
        divider_cols[0].divider()
        divider_cols[1].markdown(text)
        divider_cols[2].divider()
    else:
        st.divider()


def display_dto(dto, attributes):
    """
    Displays attributes of a DTO or dictionary as a formatted string.

    Args:
        dto (Any): The data transfer object (DTO) or dictionary to retrieve values from.
        attributes (List[tuple[str, str]]): List of attribute name-key tuples.

    Returns:
        str: Concatenated string of attribute values.

    Raises:
        ValueError: If the DTO does not have the specified attribute.
    """

    # Initialize a list to hold the formatted attribute values
    attribute_values = []

    # Check if the input is a dictionary
    is_dict = isinstance(dto, dict)

    # Iterate through the list of attribute name-key tuples
    for name, key in attributes:
        # Retrieve the value of the attribute from the dictionary
        if is_dict:
            value = dto.get(key, None)
        # Retrieve the value of the attribute from the DTO
        else:
            if hasattr(dto, key):
                value = getattr(dto, key)
            else:
                raise ValueError(f"DTO does not have attribute '{key}'.")

        if value or value is False or value == 0:
            # Format the value with the name if provided
            if name:
                formatted_value = f"{name}: {value}"
            else:
                formatted_value = str(value)
            # Append the formatted value to the list
            attribute_values.append(formatted_value)

    # Form the concatenated string with spaces between values
    concatenated_string = " - ".join(attribute_values)

    # Return the concatenated string
    return concatenated_string


def scroll_to_bottom():
    """
    Placeholder function to scroll to the bottom of the page.
    """

    pass
    # TODO: Implement
    # # JavaScript to scroll to the bottom of the page
    # scroll_script = """
    # <script>
    # window.onload = function() {
    #     window.scrollTo(0, document.body.scrollHeight);
    # }
    # </script>
    # """
    # st.markdown(scroll_script, unsafe_allow_html=True)
