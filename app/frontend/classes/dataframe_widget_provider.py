"""
This module provides various methods to create and manage different kinds of data editors and dataframes using Streamlit.
It includes functionalities to display and update dataframes for training data, test data, and model evaluations.

Classes:
    DataFrameWidgetProvider: Provides static methods to create and manage data editors and dataframes.

Methods:
    - create_training_data_editor_widget: Creates a data editor widget for training data.
    - create_test_data_editor_widget: Creates a data editor widget for test data.
    - create_dataframe_with_checkbox: Automatically updates the test datapoint when the training datapoint is checked.
    - create_simple_dataframe: Creates a simple dataframe.
    - create_only_content_dataframe: Creates a dataframe displaying only content.
    - create_complex_datapoint_evaluation_dataframe: Creates a dataframe for complex datapoint evaluation.
    - create_only_content_table: Creates a table displaying only content.
    - create_dataframe_with_augmentation_method: Creates a dataframe with augmentation method.
    - create_complex_model_evaluation_dataframe: Creates a dataframe for complex model evaluation.
    - display_models_data_editor: Displays models data editor.
    - general_dataframe: Displays a general dataframe.
"""


import streamlit as st
import pandas as pd
from dataclasses import asdict
from uuid import uuid4
from app.frontend.dtos.frontend_dtos import DataPointDTOWithDataFrameWrapper
from app.frontend.classes.services.datapoint_service import DataPointService
from app.frontend.classes.editors.dataframe_editor import DataFrameEditor
from app.backend.dtos.response import ComplexDataPointEvaluationDTO, ComplexModelEvaluationDTO, DataPointDTO, DataPointWithInitialDataPointDTO, ModelWithOriginalProjectDTO, SimpleDataPointDTO
from app.backend.dtos.update_request import UpdateModelDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.backend.database.schema import EvaluationType, FineTuningCompany, MessageKeys
from app.backend.util.utility_functions import find_index_in_list

# Returns different kinds of data_editors and dataframes


class DataFrameWidgetProvider:
    """Provides various data editors and dataframes for displaying and editing data."""

    @classmethod
    def create_training_data_editor_widget(cls, simple_datapoint_dto: DataPointDTOWithDataFrameWrapper, chosen_company: FineTuningCompany, default_role: str, dataframe_editor: DataFrameEditor):
        """
        Create a data editor widget for training data.

        Args:
            simple_datapoint_dto (DataPointDTOWithDataFrameWrapper): The simple datapoint DTO with dataframe wrapper.
            chosen_company (FineTuningCompany): The chosen company.
            default_role (str): The default role.
            dataframe_editor (DataFrameEditor): The dataframe editor.
        """

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
        """
        Create a data editor widget for test data.

        Args:
            simple_datapoint_dto (DataPointDTOWithDataFrameWrapper): The simple datapoint DTO with dataframe wrapper.
            chosen_company (FineTuningCompany): The chosen company.
            default_role (str): The default role.
            dataframe_editor (DataFrameEditor): The dataframe editor.
        """

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
        """
        Automatically update the test datapoint when the training datapoint is checked.

        Args:
            datapoint_dto (DataPointDTO): The datapoint DTO.
            current_test_datapoint (DataPointDTO): The current test datapoint.
        """

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

            def on_checkbox_change(current_test_datapoint, datapoint_dto):
                DataPointService.add_or_remove(
                    current_test_datapoint, datapoint_dto)

            # Check if datapoint exists in list of test related datapoints and if so, set the "checked" value to True.
            value = DataPointService.is_present(
                current_test_datapoint.related_datapoints, datapoint_dto)

            st.checkbox(label="Select the current datapoint",
                        help="Select the current datapoint", value=value, label_visibility="collapsed", key=uuid4(), on_change=on_checkbox_change, args=(current_test_datapoint, datapoint_dto))
        editor_fragment()

    @classmethod
    def create_simple_dataframe(cls, datapoint_dto: DataPointDTO):
        """
        Create a simple dataframe.

        Args:
            datapoint_dto (DataPointDTO): The datapoint DTO.
        """

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
        """
        Create a dataframe displaying only content.

        Args:
            datapoint_dto (DataPointWithInitialDataPointDTO): The datapoint with initial datapoint DTO.
        """

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
        """
        Create a dataframe for complex datapoint evaluation.

        Args:
            complex_datapoint_evaluation_dto (ComplexDataPointEvaluationDTO): The complex datapoint evaluation DTO.
            updated_evalautions (set[int] | None): Set of updated evaluations.
            current_step_counter (int | None): The current step counter.
            activation_threshold (int): The activation threshold.
        """

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
        """
        Create a table displaying only content.

        Args:
            model_evaluation: The model evaluation.
        """

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
    def create_dataframe_with_augmentation_method(cls, datapoint_dto: DataPointDTO | SimpleDataPointDTO):
        """
        Create a dataframe with augmentation method.

        Args:
            datapoint_dto (DataPointDTO | SimpleDataPointDTO): The datapoint DTO or simple datapoint DTO.
        """

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

        st.write(datapoint_dto.augmentation_type or None)

    @classmethod
    def create_complex_model_evaluation_dataframe(cls, complex_model_evaluation_dto: ComplexModelEvaluationDTO, all_training_datapoints: list[SimpleDataPointDTO], updated_evalautions: set[int] | None = None, current_step_counter: int | None = None, activation_threshold: int = -1):
        """
        Create a dataframe for complex model evaluation.

        Args:
            complex_model_evaluation_dto (ComplexModelEvaluationDTO): The complex model evaluation DTO.
            all_training_datapoints (list[SimpleDataPointDTO]): List of all training datapoints.
            updated_evalautions (set[int] | None): Set of updated evaluations.
            current_step_counter (int | None): The current step counter.
            activation_threshold (int): The activation threshold.
        """

        # Update the current attribute when the slider changes
        def update_eval(complex_model_evaluation_dto: ComplexDataPointEvaluationDTO, updated_evalautions: set[int], attribute: str, new_val_session_key: str):
            if st.session_state[new_val_session_key]:
                setattr(complex_model_evaluation_dto, attribute,
                        st.session_state[new_val_session_key])
            else:
                setattr(complex_model_evaluation_dto, attribute,
                        None)

            if updated_evalautions is not None:
                # Only add evaluations if they have actually changed - no duplicates in the set since the reference stays the same. Add test datapoint for model eval, since model evals are fetched and updated via their test datapoint and model id
                updated_evalautions.add(
                    complex_model_evaluation_dto.datapoint.id)

        # augmented_datapoint_dto: DataPointWithInitialDataPointDTO = complex_model_evaluation_dto.datapoint
        test_datapoint: DataPointDTO = complex_model_evaluation_dto.datapoint

        tabs = st.tabs(
            ["Original Test DataPoint", "Related Training Datapoints", "All Training Datapoints"])
        with tabs[0]:
            st.markdown(
                f"###### *Ground label: {getattr(test_datapoint.evaluation_type, 'value', 'N/A')}*")
            cls.create_simple_dataframe(test_datapoint)

        with tabs[1]:
            if test_datapoint.related_datapoints:
                datapoints_container = st.container(height=333)
                with datapoints_container:
                    for datapoint in test_datapoint.related_datapoints:
                        cls.create_dataframe_with_augmentation_method(
                            datapoint)
            else:
                st.write("No related datapoints available. If you want to see related datapoints here, match those datapoints in the datapoint matcher on dataset creation.")
        with tabs[2]:
            datapoints_container = st.container(height=333)
            with datapoints_container:
                for datapoint in all_training_datapoints:
                    cls.create_dataframe_with_augmentation_method(datapoint)

            # TODO: Optimize this by using HTML with Javascript and make a lazy loading infinity scroll
            # # HTML and JavaScript for lazy loading dataframes
            # html_content = """
            # <div id="container" style="height: 333px; overflow-y: scroll; border: 1px solid black;">
            # </div>
            # <script>
            # const container = document.getElementById('container');
            # let index = 0;
            # const totalDataframes = 1000;

            # function loadMoreDataframes() {
            #     if (index >= totalDataframes) return;
            #     for (let i = 0; i < 20; i++) {
            #     if (index >= totalDataframes) break;
            #     const div = document.createElement('div');
            #     div.innerHTML = `
            #         <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ddd;">
            #         ${dataframesHTML[index]}
            #         </div>`;
            #     container.appendChild(div);
            #     index++;
            #     }
            # }

            # container.addEventListener('scroll', () => {
            #     if (container.scrollTop + container.clientHeight >= container.scrollHeight) {
            #     loadMoreDataframes();
            #     }
            # });

            # // Initial load
            # loadMoreDataframes();
            # </script>
            # """

            # def create_dataframe(index):
            #     return pd.DataFrame({
            #         'Column1': range(index * 10, (index + 1) * 10),
            #         'Column2': range(index * 10, (index + 1) * 10)
            #     })

            # # Generate sample data
            # dataframes = [create_dataframe(i) for i in range(1000)]

            # # Convert dataframes to HTML
            # dataframes_html = []
            # for df in dataframes:
            #     df_html = df.to_html(index=False, classes='dataframe')
            #     dataframes_html.append(df_html)

            # # Pass the dataframe HTML to JavaScript
            # html_content = html_content.replace(
            #     'dataframesHTML = []', f'dataframesHTML = {dataframes_html}')

            # # Display the HTML content in Streamlit
            # st.markdown(html_content, unsafe_allow_html=True)

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

        st.experimental_fragment

        def evaluation_fragment():
            if getattr(test_datapoint.evaluation_type, 'value', None):
                st.selectbox(label="Evaluation Types", options=enum_evaluation_types, index=None, help="""
                            
                Truth (T): The model answered as expected from the original test datapoint.

                Falsehood (F): The model answered with an unexpected output.
                
                INFO: False Negative: F, F - True Positive: T, T

                """, format_func=lambda enum: enum.value,
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
        evaluation_fragment()

    @classmethod
    def display_models_data_editor(cls, service: ServiceManagerFacade, models: list[ModelWithOriginalProjectDTO], selected_models: list[int]):
        """
        Display models data editor.

        Args:
            service (ServiceManagerFacade): The service manager facade.
            models (list[ModelWithOriginalProjectDTO]): List of models with original project DTO.
            selected_models (list[int]): List of selected models.
        """

        # Convert models to a list of dictionaries
        model_dicts = [asdict(model) for model in models]
        # Add the "add to statistics" field manually since it will not be displyaed without being present in the dict
        for model_dict in model_dicts:
            model_dict['select_for_statistics'] = model_dict['id'] in selected_models
            model_dict['created_at'] = model_dict['created_at'].strftime(
                '%Y-%m-%d %H:%M:%S %Z')

        # Define column configuration
        column_config = {
            "model_name": st.column_config.TextColumn("Model Name", help="Model name", width="medium", disabled=True),
            "version": st.column_config.TextColumn("Version", help="Version", width="small", disabled=True),
            "is_checkpoint_model": st.column_config.CheckboxColumn("Checkpoint", help="Is it a checkpoint model?", width="small", disabled=True),
            "checkpoint_step": st.column_config.NumberColumn("Step", help="Checkpoint step", width="small", disabled=True),
            "is_global": st.column_config.CheckboxColumn("Global", help="Is the model global?", width="small"),
            "created_at": st.column_config.TextColumn("Creation Date", help="Model creation date", width="small", disabled=True),
            "select_for_statistics": st.column_config.CheckboxColumn("Select for statistics", help="Select model for statistical analysis", width="small")
        }

        def update_model_data(service: ServiceManagerFacade, models: list[ModelWithOriginalProjectDTO], data_editor_key: str, selected_models: list[int]):
            edited_rows = st.session_state[data_editor_key].get(
                'edited_rows', {})

            updated_models: list[UpdateModelDTO] = []
            for idx, changes in edited_rows.items():
                original_model: ModelWithOriginalProjectDTO = models[idx]
                # Look up the model ID using the row index
                model_id: int = original_model.id

                # Only update the model if there are actually fields to update, "selected_for_statistics" does not require a model update
                if changes.get('is_global') is not None:
                    model_dto = UpdateModelDTO(
                        id=model_id,
                        is_global=changes.get(
                            'is_global', original_model.is_global)
                    )
                    updated_models.append(model_dto)

                if changes.get("select_for_statistics") is not None:
                    if model_id not in selected_models:
                        selected_models.append(model_id)
                    else:
                        selected_models.remove(model_id)

            if updated_models:
                service.update_models(updated_models)

            # Removes all prject model associations that do not belong to the originals projects model, since it is not global anymore. Only do this if the fields has been set from True to False
            for model_dto in updated_models:
                if original_model.is_global and model_dto.is_global is False:
                    service.remove_model_global_status(model_dto.id)

        # Data editor key
        data_editor_key = f"model_data_editor_{models[0].original_project.id}"

        # Data editor configuration
        data_editor = st.data_editor(
            model_dicts,
            column_config=column_config,
            hide_index=True,
            # height=800,
            column_order=("model_name", "version", "is_checkpoint_model",
                          "checkpoint_step", "is_global", "created_at", "select_for_statistics"),
            use_container_width=True,
            num_rows="fixed",
            key=data_editor_key,
            on_change=update_model_data,
            args=(service, models, data_editor_key, selected_models)
        )

    @classmethod
    def general_dataframe(cls, data: list | dict | pd.DataFrame):
        """
        Display a general dataframe.

        Args:
            data (list | dict | pd.DataFrame): The data to be displayed.
        """

        column_order: tuple = None
        if isinstance(data, dict):
            column_order = tuple(data.keys())

        st.dataframe(
            data,
            hide_index=True,
            height=400,
            column_order=column_order,
            use_container_width=True
        )
