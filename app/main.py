"""
This is the main entry point for the application. It orchestrates the workflow
of the project, calling functions from other modules and handling the overall process flow.
"""

# Import necessary modules and packages
from datetime import timedelta
import streamlit as st
import numpy as np
import pandas as pd
import plotly as pl
from backend.util.logger import StreamlitLogger
from backend.util import utility_functions as uf
from backend.util.config import Config
from backend.service.implementations.service_manager_facade import ServiceManagerFacade
from backend.dtos.get_request import *
from backend.dtos.response import *


errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:

    uf.apply_global_style()
    # Can be easily adapted in case of multiple users at the same time
    service, config = uf.initialize_global_states(ServiceManagerFacade, Config)

    def load_page():
        uf.clear_query_params()

        update_button_base_key = "update_project_button_"
        delete_button_base_key = "delete_project_button_"
        choose_button_base_key = "choose_project_button_"
        project_update_state_key = "update_project"
        project_delete_state_key = "delete_project"
        project_choose_state_key = "choose_project"

        search_name = st.session_state.get("search_name")
        search_date = st.session_state.get("search_date")

        projects: list[ProjectDTO] = service.filter_projects(GetProjectsDTO(
            project_name=search_name, created_at=search_date))

        sorted_projects: list[ProjectDTO] = uf.sort_dicts(
            projects, "created_at",  "project_name")

        st.title("Project Overview")

        @st.experimental_fragment
        def switch_to_create_project():
            create_project_button = st.button(
                "Create Project +", help="Click me to create a new project", type="primary", key="create_project_button")

            if create_project_button:
                uf.cleanup_and_navigate(
                    "pages/1_create_project.py", config.global_states)
        switch_to_create_project()

        search_cols = st.columns((2, 1))

        with search_cols[0]:
            search_name = st.text_input("Search a project by name:",
                                        placeholder="Search projects by name", label_visibility="hidden", max_chars=255, key="search_name", disabled=False if not sorted_projects else False)

        search_date = search_cols[1].date_input(
            "Search projects created after this date:", value=None,  key="search_date", disabled=False if not sorted_projects else False, min_value=sorted_projects[-1].created_at if sorted_projects else None, max_value=sorted_projects[0].created_at if sorted_projects else None, label_visibility="hidden")

        if sorted_projects:
            header_cols = st.columns((1, 2, 1))
            header_cols[0].header("Name")
            header_cols[1].header("Description")
            header_cols[2].header("Created at")

            for i, project in enumerate(sorted_projects):
                project_details_row_cols = st.columns((1, 2, 1))
                with project_details_row_cols[0]:
                    st.container(height=100).write(project.project_name)
                with project_details_row_cols[1]:
                    st.container(height=100).write(project.description)
                with project_details_row_cols[2]:
                    st.container(height=100).write(project.created_at)

                button_container = st.container()

                with button_container:
                    project_button_row_cols = st.columns(5)
                    update_button_key = update_button_base_key + str(i)
                    delete_button_key = delete_button_base_key + str(i)
                    choose_button_key = choose_button_base_key + str(i)

                    with project_button_row_cols[1]:
                        @st.experimental_fragment
                        def switch_to_update_project():
                            if st.session_state.get(project_update_state_key):
                                set_clicked_project_data(
                                    sorted_projects, update_button_base_key)
                                uf.cleanup_and_navigate(config.pages.update_project,
                                                        config.global_states + ['current_project'])

                            st.button(
                                "Update Project", help="Click me to update this project", type="secondary", key=update_button_key, on_click=lambda: setattr(st.session_state, project_update_state_key, True))
                        switch_to_update_project()
                    with project_button_row_cols[2]:
                        @st.experimental_fragment
                        def switch_to_fine_tune_model():
                            if st.session_state.get(project_choose_state_key):
                                set_clicked_project_data(
                                    sorted_projects, choose_button_base_key)
                                uf.cleanup_and_navigate(config.pages.fine_tune_model,
                                                        config.global_states + ['current_project'])

                            st.button(
                                "Choose Project", help="Click me to choose this project", type="primary", key=choose_button_key, on_click=lambda: setattr(st.session_state, project_choose_state_key, True))
                        switch_to_fine_tune_model()
                    with project_button_row_cols[3]:
                        @st.experimental_fragment
                        def delete_project():
                            if st.session_state.get(project_delete_state_key):
                                set_clicked_project_data(
                                    sorted_projects, delete_button_base_key)
                                # TODO: add delete project method

                            st.button(
                                "Delete Project", help="Click me to delete this project", type="secondary", key=delete_button_key, on_click=lambda: setattr(st.session_state, project_delete_state_key, True))
                        delete_project()
        else:
            st.write("You currently have no projects.")

    def set_clicked_project_data(sorted_projects: list[ProjectDTO], base_key: str):
        for i, project in enumerate(sorted_projects):
            key = base_key + str(i)
            if st.session_state.get(key):
                st.session_state.current_project = project

    load_page()
