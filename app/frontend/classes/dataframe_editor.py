from typing import Any
import pandas as pd
import streamlit as st
from frontend.dtos.frontend_dtos import *
from app.backend.custom_types.typedicts import *


class DataFrameEditor:
    def __init__(self):
        pass

    @staticmethod
    def apply_edits(df: pd.DataFrame, edits: dict[int, dict[str, Any]]) -> None:
        """Apply edits to the DataFrame using the changes dictionary."""
        for idx, changes in edits.items():
            for key, value in changes.items():
                if isinstance(value, list):  # Convert lists to strings
                    value = ', '.join(map(str, value))
                df.at[int(idx), key] = value

    @staticmethod
    def apply_category_changes(df: pd.DataFrame, edits: dict[int, dict[str, Any]]) -> None:
        key = list(edits.keys())[0]
        if "category" in edits[key]:
            updated_category = edits[key]["category"]
            df['category'] = updated_category

    @staticmethod
    def add_new_rows(df: pd.DataFrame, new_rows: list[dict[str, Any]]) -> pd.DataFrame:
        """Add new rows to the DataFrame, inheriting category if present."""
        # Check if there's an existing non-empty category
        existing_categories = df['category'].unique()
        existing_categories = [cat for cat in existing_categories if cat]

        # Set the default category
        default_category = existing_categories[0] if existing_categories else ""

        for row in new_rows:
            for key, value in row.items():
                if isinstance(value, list):
                    row[key] = ', '.join(map(str, value))

            # Apply the default category if one exists
            if default_category:
                row['category'] = default_category

        new_df = pd.DataFrame(new_rows)
        return pd.concat([df, new_df], ignore_index=True)

    @staticmethod
    def delete_rows(df: pd.DataFrame, indices: list[int]) -> pd.DataFrame:
        """Remove rows by indices and reset index."""
        return df.drop(indices, errors='ignore').reset_index(drop=True)

    @staticmethod
    def update_df(simple_datapoint_dto: DataPointDTOWithDataFrameWrapper) -> None:
        """Main method to update DataFrame based on editor changes."""

        data_editor = st.session_state[simple_datapoint_dto.data_editor_key]
        df = simple_datapoint_dto.messages

        # Apply edits if there are edited rows
        if 'edited_rows' in data_editor:
            DataFrameEditor.apply_edits(df, data_editor['edited_rows'])
            # If actual edits have taken place
            if data_editor['edited_rows']:
                DataFrameEditor.apply_category_changes(
                    df, data_editor['edited_rows'])

        # Add new rows if they exist
        if 'added_rows' in data_editor:
            df = DataFrameEditor.add_new_rows(df, data_editor['added_rows'])

        # Handle deletions
        if 'deleted_rows' in data_editor:
            df = DataFrameEditor.delete_rows(df, data_editor['deleted_rows'])

        simple_datapoint_dto.messages = df

    @staticmethod
    def convert_df_to_messages_container(df: pd.DataFrame) -> tuple[MessagesContainer, str]:
        """
        Convert a list of DataFrames to a list of tuples of MessagesContainer and category string.

        Args:
            dfs (List[pd.DataFrame]): List of DataFrames to convert.

        Returns:
            List[Tuple[MessagesContainer, str]]: List of tuples, each containing a MessagesContainer and a category string.
        """

        messages = []
        category = "general"  # Default category

        for index, row in df.iterrows():
            # Create a Message object for each row
            message = Message(role=row['role'], content=row['content'])
            messages.append(message)

            # Extract the category, defaulting to "general" if not present or empty
            row_category = row.get('category', None)
            if row_category:
                category = row_category

        # Create a MessagesContainer with the list of messages
        messages_container = MessagesContainer(messages=messages)

        # Append the tuple (MessagesContainer, category) to the result list
        return (messages_container, category)
