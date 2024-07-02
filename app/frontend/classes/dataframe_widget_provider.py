from uuid import uuid4
import streamlit as st
import pandas as pd
from app.backend.dtos.response import ComplexDataPointEvaluationDTO, DataPointDTO, DataPointWithInitialDataPointDTO
from app.frontend.classes.dataframe_editor import DataFrameEditor
from app.backend.database.schema import DatasetCategory, FineTuningCompany, MessageKeys
from app.frontend.custom_styles.individual_styles import custom_style_span
from app.frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from app.frontend.classes.datapoint_service import DataPointService


# Returns different kinds of data_editors and dataframes
class DataFrameWidgetProvider:

    @classmethod
    def create_training_data_editor_widget(cls, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper, chosen_company: FineTuningCompany, default_role: str, dataframe_editor: DataFrameEditor):
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

    @classmethod
    def create_test_data_editor_widget(cls, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper, chosen_company: FineTuningCompany, default_role: str, dataframe_editor: DataFrameEditor):
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

    # Automatically updates the test datapoint when the training datapoint is checked
    @classmethod
    def create_dataframe_with_checkbox(cls, datapoint_dto: DataPointDTO, current_test_datapoint: DataPointDTO):

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

            # Check if datapoint exists in list of test related datapoints and if so, set the "checked" value to True.
            value = DataPointService.is_present(
                current_test_datapoint.related_datapoints, datapoint_dto)

            st.checkbox(label="Select the current datapoint",
                        help="Select the current datapoint", value=value, label_visibility="collapsed", key=uuid4(), on_change=on_checkbox_change)
        editor_fragment()

    @classmethod
    def create_simple_dataframe(cls, datapoint_dto: DataPointDTO):

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

    @classmethod
    def create_only_content_dataframe(cls, datapoint_dto: DataPointWithInitialDataPointDTO):
        st.dataframe(
            datapoint_dto.messages["messages"],
            column_config={
                "content": st.column_config.TextColumn("Content", help="The content for the current role", required=True),
            },
            hide_index=True,
            use_container_width=True,
        )

    @classmethod
    def create_complex_datapoint_evaluation_dataframe(cls, complex_datapoint_evaluation_dto: ComplexDataPointEvaluationDTO, updated_evalautions: set[int] | None = None, current_step_counter: int | None = None, activation_threshold: int = -1):
        # Update the current attribute when the slider changes
        def update_eval(complex_datapoint_evaluation_dto: ComplexDataPointEvaluationDTO, updated_evalautions: set[int], attribute: str, new_val_session_key: str):
            setattr(complex_datapoint_evaluation_dto, attribute,
                    st.session_state[new_val_session_key])

            if updated_evalautions is not None:
                # Only add evaluations if they have actually changed - no duplicates in the set since the reference stays the same
                updated_evalautions.add(complex_datapoint_evaluation_dto.id)

        augmented_datapoint_dto: DataPointWithInitialDataPointDTO = complex_datapoint_evaluation_dto.datapoint
        initial_datapoint_dto: DataPointWithInitialDataPointDTO = augmented_datapoint_dto.initial_datapoint

        st.markdown("###### Original Datapoint")
        cls.create_simple_dataframe(initial_datapoint_dto)
        st.markdown("###### Augmented Datapoint")
        cls.create_simple_dataframe(augmented_datapoint_dto)

        st.slider(label="Coherence score", min_value=0, max_value=10, step=1, value=complex_datapoint_evaluation_dto.coherence_score, help="This slider allows you to evaluate the internal consistency and logical flow of the augmented data. Coherence measures how well the augmented data maintains the structure, grammar, and logical sense of the original content. A higher coherence score indicates that the data is logically structured and easy to understand",
                  on_change=update_eval, args=(complex_datapoint_evaluation_dto, updated_evalautions, "coherence_score", "coherence_score"), key="coherence_score", label_visibility="visible", disabled=current_step_counter != activation_threshold)

        st.slider(label="Relevance score", min_value=0, max_value=10, step=1, value=complex_datapoint_evaluation_dto.relevance_score, help="This slider allows you to evaluate the contextual appropriateness and pertinence of the augmented data. Relevance measures how well the augmented data aligns with the intended purpose or topic of the original content. A higher relevance score indicates that the data is contextually suitable and useful for its intended application",
                  key="relevance_score", on_change=update_eval, args=(complex_datapoint_evaluation_dto, updated_evalautions, "relevance_score", "relevance_score"), label_visibility="visible", disabled=current_step_counter != activation_threshold)

        st.markdown(f"""###### Semantic similarity score: {
            complex_datapoint_evaluation_dto.semantic_similarity_score}""")
