from typing import Any
import pandas as pd
import streamlit as st
from frontend.dtos.frontend_dtos import *
from backend.custom_types.typedicts import *


class DataFrameEditor:

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
            old_category = df.at[int(key), "category"]
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

        # Drop the rows
        df = df.drop(indices, errors='ignore').reset_index(drop=True)

        return df

    @classmethod
    def update_df(cls, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper) -> None:
        """Main method to update DataFrame based on editor changes."""
        print("DATAFRAME EDITOR - HALLO 1 !!!")
        data_editor: dict = st.session_state[simple_datapoint_dto.data_editor_key]
        df: pd.DataFrame = simple_datapoint_dto.messages

        # Apply edits if there are edited rows
        if data_editor.get('edited_rows'):
            # Update the whole category column if one category field has been changed
            cls.apply_category_changes(
                df, data_editor['edited_rows'])
            # Apply all other edits if any have taken place
            cls.apply_edits(df, data_editor['edited_rows'])

        # Add new rows if they exist
        if data_editor.get("added_rows"):
            df = cls.add_new_rows(df, data_editor['added_rows'])

        # Handle deletions
        if data_editor.get("deleted_rows"):
            df = cls.delete_rows(
                df, data_editor['deleted_rows'])

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

    @staticmethod
    def set_default_category_if_not_in_list(df: pd.DataFrame, categories: list[str], default_value: str | None = None) -> None:
        """
        Check the first row's category and set the default value for the entire column if the category is not in the list.

        Args:
            df (pd.DataFrame): DataFrame to check and update.
            categories (List[str]): List of valid categories.
            default_value (str): Default value to set if the category is not in the list.
        """
        if df.shape[0] > 0:  # Ensure there are rows in the DataFrame
            first_category: str | pd.NA = df['category'].iloc[0]
            print("TYPE", type(first_category))
            if first_category and isinstance(first_category, str):  # could be nan
                first_category = first_category.strip()
            if first_category not in categories:
                df['category'] = default_value
