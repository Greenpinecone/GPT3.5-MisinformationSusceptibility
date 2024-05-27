import streamlit as st
import datetime
from enum import Enum


def sort_dicts(list_of_objects: list[object],
               *sort_keys: str,
               priority_enum: Enum | None = None,
               enum_key: str = '',
               descending: bool = True) -> list[object]:

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


def create_text_divider(text: str = None):
    if text:
        divider_cols = st.columns((5, 1, 5))
        divider_cols[0].divider()
        divider_cols[1].write(text)
        divider_cols[2].divider()
    else:
        st.divider()
