import streamlit as st
import pandas as pd
from app.frontend.classes.dataframe_editor import DataFrameEditor
from app.backend.database.schema import DatasetCategory, FineTuningCompany, MessageKeys
from app.frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper


# Retruns different kinds of data_editors and dataframes
class DataFrameWidgetProvider:

    @staticmethod
    def create_training_data_editor_widget(simple_datapoint_dto: DataPointDTOWithDataFrameWrapper, chosen_company: FineTuningCompany, default_role: str, dataframe_editor: DataFrameEditor):
        st.data_editor(
            simple_datapoint_dto.messages,
            column_config={
                "role": st.column_config.SelectboxColumn(
                    "Role",
                    help="The role of the current prompt",
                    options=MessageKeys[chosen_company.value].value[0],
                    required=True,
                    default=default_role,
                    width="small"
                ),
                "content": st.column_config.TextColumn("Content", help="Set the content for the current role", default=""),
                "category": st.column_config.TextColumn("Category", help="You can only set one category per datapoint", default=""),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key=simple_datapoint_dto.data_editor_key,
            on_change=dataframe_editor.update_df,
            # Must be an iterable
            args=(simple_datapoint_dto,)
        )

    @staticmethod
    def create_test_data_editor_widget(simple_datapoint_dto: DataPointDTOWithDataFrameWrapper, chosen_company: FineTuningCompany, default_role: str, dataframe_editor: DataFrameEditor, used_categories: list[str]):
        st.data_editor(
            simple_datapoint_dto.messages,
            column_config={
                "role": st.column_config.SelectboxColumn(
                    "Role",
                    help="The role of the current prompt",
                    options=MessageKeys[chosen_company.value].value[0],
                    required=True,
                    default=default_role,
                    width="small"
                ),
                "content": st.column_config.TextColumn("Content", help="Set the content for the current role", default=""),
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    help="The category the test datapoint belongs to from the trainings dataset",
                    options=set(sorted(used_categories)),
                    default=None,
                ),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key=simple_datapoint_dto.data_editor_key,
            on_change=dataframe_editor.update_df,
            args=(simple_datapoint_dto,)
        )
