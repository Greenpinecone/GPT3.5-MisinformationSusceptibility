from uuid import uuid4
import streamlit as st
import pandas as pd
from app.backend.dtos.response import DataPointDTO
from app.frontend.classes.dataframe_editor import DataFrameEditor
from app.backend.database.schema import DatasetCategory, FineTuningCompany, MessageKeys
from app.frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from app.frontend.classes.datapoint_service import DataPointService


# Returns different kinds of data_editors and dataframes
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
                "content": st.column_config.TextColumn("Content", help="Set the content for the current role", default="", width="large"),
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
    def create_test_data_editor_widget(simple_datapoint_dto: DataPointDTOWithDataFrameWrapper, chosen_company: FineTuningCompany, default_role: str, dataframe_editor: DataFrameEditor):
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
                "content": st.column_config.TextColumn("Content", help="Set the content for the current role", default="", width="large"),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key=simple_datapoint_dto.data_editor_key,
            on_change=dataframe_editor.update_df,
            args=(simple_datapoint_dto,)
        )

    @staticmethod
    def create_dataframe_with_checkbox(datapoint_dto: DataPointDTO, current_test_datapoint: DataPointDTO):

        @st.experimental_fragment
        def editor_fragment():
            st.dataframe(
                datapoint_dto.messages["messages"],
                column_config={
                    "role": st.column_config.TextColumn(
                        "Role",
                        help="The role of the current prompt",
                        required=True,
                        width="small"
                    ),
                    "content": st.column_config.TextColumn("Content", help="The content for the current role", required=True, width="large"),
                },
                hide_index=True,
                use_container_width=True,
            )

            def on_checkbox_change():
                DataPointService.add_or_remove(
                    current_test_datapoint, datapoint_dto)

            value = DataPointService.is_present(
                current_test_datapoint.related_datapoints, datapoint_dto)

            st.checkbox(label="Select the current datapoint",
                        help="Select the current datapoint", value=value, label_visibility="collapsed", key=uuid4(), on_change=on_checkbox_change)
        editor_fragment()

    @staticmethod
    def create_simple_dataframe(datapoint_dto: DataPointDTO):

        st.dataframe(
            datapoint_dto.messages["messages"],
            column_config={
                "role": st.column_config.TextColumn(
                    "Role",
                    help="The role of the current prompt",
                    required=True,
                    width="small"
                ),
                "content": st.column_config.TextColumn("Content", help="The content for the current role", required=True, width="large"),
            },
            hide_index=True,
            use_container_width=True,
        )
