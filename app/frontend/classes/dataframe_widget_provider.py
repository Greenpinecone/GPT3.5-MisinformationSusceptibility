from uuid import uuid4
import streamlit as st
import pandas as pd
from app.backend.dtos.response import ComplexDataPointEvaluationDTO, ComplexModelEvaluationDTO, DataPointDTO, DataPointWithInitialDataPointDTO
from app.frontend.classes.dataframe_editor import DataFrameEditor
from app.backend.database.schema import DatasetCategory, EvaluationType, FineTuningCompany, MessageKeys
from app.frontend.custom_styles.individual_styles import custom_style_span
from app.frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from app.frontend.classes.datapoint_service import DataPointService
from app.backend.util.utility_functions import find_index_in_list

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
            if st.session_state[new_val_session_key] > 0:
                setattr(complex_datapoint_evaluation_dto, attribute,
                        st.session_state[new_val_session_key])
            else:
                setattr(complex_datapoint_evaluation_dto, attribute,
                        None)

            if updated_evalautions is not None:
                # Only add evaluations if they have actually changed - no duplicates in the set since the reference stays the same
                updated_evalautions.add(complex_datapoint_evaluation_dto.id)

        augmented_datapoint_dto: DataPointWithInitialDataPointDTO = complex_datapoint_evaluation_dto.datapoint
        initial_datapoint_dto: DataPointWithInitialDataPointDTO = augmented_datapoint_dto.initial_datapoint

        st.markdown("###### Original Datapoint")
        cls.create_simple_dataframe(initial_datapoint_dto)
        st.markdown("###### Augmented Datapoint")
        cls.create_simple_dataframe(augmented_datapoint_dto)

        st.slider(label="Coherence score", min_value=0, max_value=10, step=1, value=complex_datapoint_evaluation_dto.coherence_score or 0, help="This slider allows you to evaluate the internal consistency and logical flow of the augmented data. Coherence measures how well the augmented data maintains the structure, grammar, and logical sense of the original content. A higher coherence score indicates that the data is logically structured and easy to understand. Only values between 1-10 are considered for calculations.",
                  on_change=update_eval, args=(complex_datapoint_evaluation_dto, updated_evalautions, "coherence_score", "coherence_score"), key="coherence_score", label_visibility="visible", disabled=current_step_counter != activation_threshold)

        st.slider(label="Relevance score", min_value=0, max_value=10, step=1, value=complex_datapoint_evaluation_dto.relevance_score or 0, help="This slider allows you to evaluate the contextual appropriateness and pertinence of the augmented data. Relevance measures how well the augmented data aligns with the intended purpose or topic of the original content. A higher relevance score indicates that the data is contextually suitable and useful for its intended application. Only values between 1-10 are considered for calculations.",
                  key="relevance_score", on_change=update_eval, args=(complex_datapoint_evaluation_dto, updated_evalautions, "relevance_score", "relevance_score"), label_visibility="visible", disabled=current_step_counter != activation_threshold)

        st.markdown(f"""###### Semantic similarity score: {
            complex_datapoint_evaluation_dto.semantic_similarity_score}""")

    @classmethod
    def create_only_content_table(cls, model_evaluation):
        # Convert messages to a DataFrame
        df = pd.DataFrame(model_evaluation.messages["messages"])

        # Select only the 'role' and 'content' columns
        df = df[['role', 'content']]

        # Style the DataFrame
        def highlight_last_row(s):
            is_last = pd.Series(data=False, index=s.index)
            is_last.iloc[-1] = True
            return ["color: lightgray; background-color: green;" if is_last[i] else '' for i in range(len(s))]

        # Use a styled pd.DataFrame to apply colors / fonts / bold to the text custom
        styled_df = df.style.apply(
            highlight_last_row, axis=0)

        # TODO: Adapt the other dataframe functions (where possible) to take only a messages object so that we can reuse them anywhere without passing datapoints.
        st.dataframe(
            styled_df,
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
    def create_complex_model_evaluation_dataframe(cls, complex_model_evaluation_dto: ComplexModelEvaluationDTO, updated_evalautions: set[int] | None = None, current_step_counter: int | None = None, activation_threshold: int = -1):
        # Update the current attribute when the slider changes
        def update_eval(complex_model_evaluation_dto: ComplexDataPointEvaluationDTO, updated_evalautions: set[int], attribute: str, new_val_session_key: str):
            if st.session_state[new_val_session_key]:
                setattr(complex_model_evaluation_dto, attribute,
                        st.session_state[new_val_session_key])
            else:
                setattr(complex_model_evaluation_dto, attribute,
                        None)

            if updated_evalautions is not None:
                # Only add evaluations if they have actually changed - no duplicates in the set since the reference stays the same
                updated_evalautions.add(complex_model_evaluation_dto.id)

        # augmented_datapoint_dto: DataPointWithInitialDataPointDTO = complex_model_evaluation_dto.datapoint
        test_datapoint: DataPointDTO = complex_model_evaluation_dto.datapoint

        st.markdown("###### Original Test Datapoint")
        cls.create_simple_dataframe(test_datapoint)
        st.markdown("###### Model Generated Answer")
        cls.create_only_content_table(complex_model_evaluation_dto)

        enum_evaluation_types: list[EvaluationType] = list(
            EvaluationType)

        # reset selectbox kex when the displayed dto has no evaluation type set
        if not complex_model_evaluation_dto.evaluation_type:
            st.session_state.evaluation_type = None
        else:
            index: int = find_index_in_list(enum_evaluation_types, EvaluationType(
                complex_model_evaluation_dto.evaluation_type))
            st.session_state.evaluation_type = enum_evaluation_types[index]

        st.selectbox(label="Evaluation Types", options=enum_evaluation_types, index=None, help="""True Negative (TN): Instances where the model correctly identifies that the data does not belong to a certain category or does not possess a particular characteristic. This helps measure the model's ability to correctly reject irrelevant data, avoiding false positives.

        True Positive (TP): Instances where the model correctly identifies that the data belongs to a certain category or possesses a particular characteristic. This helps assess the model's accuracy in recognizing and classifying relevant data, identifying true positives.

        False Negative (FN): Instances where the model incorrectly identifies that the data does not belong to a certain category or does not possess a particular characteristic when it actually does. This helps understand the model's tendency to miss relevant data, avoiding false negatives.

        False Positive (FP): Instances where the model incorrectly identifies that the data belongs to a certain category or possesses a particular characteristic when it actually does not. This helps understand the model's tendency to incorrectly classify irrelevant data, avoiding false positives.""", format_func=lambda enum: enum.value,
                     on_change=update_eval, args=(complex_model_evaluation_dto, updated_evalautions, "evaluation_type", "evaluation_type"), key="evaluation_type", label_visibility="visible", disabled=current_step_counter != activation_threshold)

        st.slider(label="Helpfulness score", min_value=0, max_value=10, step=1, value=complex_model_evaluation_dto.helpful_score or 0, help="This slider allows you to evaluate how useful and relevant the model's responses are to the given prompts. A higher helpfulness score (ranging from 1 to 10) indicates that the model's output is more informative, actionable, and aligns well with the user's intent. Setting the slider to 0 means that helpfulness is not included in the evaluation.",
                  on_change=update_eval, args=(complex_model_evaluation_dto, updated_evalautions, "helpful_score", "helpful_score"), key="helpful_score", label_visibility="visible", disabled=current_step_counter != activation_threshold)

        st.slider(label="Honesty score", min_value=0, max_value=10, step=1, value=complex_model_evaluation_dto.honest_score or 0, help="This slider allows you to assess the truthfulness and accuracy of the model's responses. A higher honesty score (ranging from 1 to 10) reflects that the model's output is factually correct and free from misleading or false information. Setting the slider to 0 means that honesty is not included in the evaluation.",
                  key="honest_score", on_change=update_eval, args=(complex_model_evaluation_dto, updated_evalautions, "honest_score", "honest_score"), label_visibility="visible", disabled=current_step_counter != activation_threshold)

        st.slider(label="Harmlessness score", min_value=0, max_value=10, step=1, value=complex_model_evaluation_dto.harmless_score or 0, help="This slider allows you to measure the safety and non-harmful nature of the model's responses. A higher harmlessness score (ranging from 1 to 10) means that the model's output avoids harmful, offensive, or biased content, ensuring that it is safe for all users. Setting the slider to 0 means that harmlessness is not included in the evaluation.",
                  key="harmless_score", on_change=update_eval, args=(complex_model_evaluation_dto, updated_evalautions, "harmless_score", "harmless_score"), label_visibility="visible", disabled=current_step_counter != activation_threshold)

        if complex_model_evaluation_dto.semantic_similarity_score:
            st.markdown(f"""###### Semantic similarity score: {
                complex_model_evaluation_dto.semantic_similarity_score}""")
