"""
This is the main entry point for the application. It orchestrates the workflow
of the project, calling functions from other modules and handling the overall process flow.
"""

# Import necessary modules and packages

import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from ..backend.util.logger import StreamlitLogger
from ..backend.persistence.classes.data_manager import DataManager
from ..backend.util import utility_functions as uf
from ..backend.util.config import Config


def main():
    logger: StreamlitLogger = uf.get_or_create_session_state(
        "logger", default_value=StreamlitLogger)
    data_manager: DataManager = uf.get_or_create_session_state(
        "data_manager", logger, default_value=DataManager)
    config: Config = uf.get_or_create_session_state(
        "config", default_value=Config)

    logger.ui_error("HALLO1")
    logger.warning("HALLO 2")


"""
    # Dummy lists for existing models and projects. Replace these with actual data.
    existing_models = ["Model A", "Model B", "Model C"]
    existing_projects = ["Project X", "Project Y", "Project Z"]
    existing_datasets = ["Dataset 1", "Dataset 2",
                         "Dataset 3"]  # Dummy datasets

    st.header("Setup Your Project")
    with st.form("choose_a_project_form"):

        tab1, tab2 = st.tabs(["Existing Project", "New Project"])

        with tab1:
            st.write(
                "The generated data will be added to the existing project folder.")
            selected_project = st.selectbox("Choose an existing project:", [""] + existing_projects,
                                            key="choose_existing_project", label_visibility='visible')
            if selected_project:
                st.write("YOU HAVE SELECTED THIS MODEL")

        with tab2:
            new_model_name = st.text_input(
                "Create a new project:", key="set_new_project_name", label_visibility='visible')

        project_submitted = st.form_submit_button("Choose Project")

    with st.form("choose_model_form"):

        tab1, tab2 = st.tabs(["Existing Model", "New Model"])

        with tab1:
            st.selectbox("Choose an existing model:", [""] + existing_models,
                         key="choose_existing_model", label_visibility='visible')
        with tab2:
            new_model_name = st.text_input(
                "Create a new model:", key="set_new_model_name", label_visibility='visible')

        model_submitted = st.form_submit_button("Choose Model")

        # Project Name
        project_choice = st.selectbox("Choose an existing project or input a new name below:", [
                                      ""] + existing_projects, key="project_choice")
        new_project_name = st.text_input(
            "Or specify a new project name:", key="new_project_name", label_visibility=None)

        # Initial Trainings Data
        trainings_data_choice = st.selectbox("Choose existing training data or upload a new file below:", [
                                             ""] + existing_datasets, key="trainings_data_choice")
        new_trainings_data = st.file_uploader(
            "Or upload new training data:", key="new_trainings_data")

        # Initial Test Data
        test_data_choice = st.selectbox("Choose existing test data or upload a new file below:", [
                                        ""] + existing_datasets, key="test_data_choice")
        new_test_data = st.file_uploader(
            "Or upload new test data:", key="new_test_data")

        # Submit button
        submitted = st.form_submit_button("Submit")

    if submitted:
        model_name = new_model_name if new_model_name else model_choice
        project_name = new_project_name if new_project_name else project_choice
        trainings_data_name = "Uploaded File" if new_trainings_data else trainings_data_choice
        test_data_name = "Uploaded File" if new_test_data else test_data_choice

        st.write(f"Model Name: {model_name}")
        st.write(f"Project Name: {project_name}")
        st.write(f"Initial Trainings Data: {trainings_data_name}")
        st.write(f"Initial Test Data: {test_data_name}")

        # Process the uploaded files or selected options as needed
        if new_trainings_data:
            # Process the uploaded training data file
            pass
        if new_test_data:
            # Process the uploaded test data file
            pass
"""


if __name__ == "__main__":
    # This condition ensures that main() is called only when this script is executed directly (not imported)
    main()
