from typing import Any
from uuid import uuid4
import pandas as pd
import streamlit as st
from app.frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from app.frontend.classes.toast_manager import ToastManager
from app.backend.custom_types.typedicts import MessagesContainer, Message


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
    def add_new_rows(df: pd.DataFrame, new_rows: list[dict[str, Any]]) -> pd.DataFrame:
        """Add new rows to the DataFrame,"""

        for row in new_rows:
            for key, value in row.items():
                if isinstance(value, list):
                    row[key] = ', '.join(map(str, value))

        new_df = pd.DataFrame(new_rows)
        return pd.concat([df, new_df], ignore_index=True)

    @staticmethod
    def delete_rows(df: pd.DataFrame, indices: list[int]) -> pd.DataFrame:
        """Remove rows by indices and reset index."""

        # Drop the rows
        df = df.drop(indices, errors='ignore').reset_index(drop=True)

        return df

    @staticmethod
    def check_edits(df: pd.DataFrame, edits: dict[int, dict[str, Any]]) -> bool:
        """Check edits to ensure 'system' role is only in the first row."""
        for idx, changes in edits.items():
            if 'role' in changes and changes['role'] == 'system' and idx != 0:
                ToastManager.add_global_toasts(
                    "'System' role can only be placed at the beginning of a datapoint", "info")
                return False
        return True

    @classmethod
    def update_df(cls, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper) -> None:
        """Main method to update DataFrame based on editor changes."""
        data_editor: dict = st.session_state[simple_datapoint_dto.data_editor_key]
        df: pd.DataFrame = simple_datapoint_dto.messages

        # Apply edits if there are edited rows
        if data_editor.get('edited_rows'):
            # Check if the edits are valid
            # TODO: Adapt this for different companies / roles / models and change the data_editor key reset to avoid multiple failure points when copying code
            if not cls.check_edits(df, data_editor['edited_rows']):
                # Reset data editor key to force rerender, to avoid showing the currently data_editor stored changes which ar enot applied and would reset on page reload.
                simple_datapoint_dto.data_editor_key = f"data_editor_{uuid4()}"
                return
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
        Convert a DataFrames to a MessagesContainer.

        Args:
            df (pd.DataFrame): DataFrame to convert.

        Returns:
            MessagesContainer: MessagesContainer.
        """

        messages = []

        for index, row in df.iterrows():
            # Create a Message object for each row
            message = Message(role=row['role'], content=row['content'])
            messages.append(message)

        # Create a MessagesContainer with the list of messages
        messages_container = MessagesContainer(messages=messages)

        # MessagesContainer
        return messages_container
