# Import necessary modules and packages
from datetime import timedelta
from io import BytesIO
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
from backend.dtos.create_request import *
from backend.database.schema import DatasetCategory
from app.frontend.classes.file_uploader import FileUploader
from app.frontend.classes.dataframe_editor import DataFrameEditor
import math
from uuid import uuid4

errors_container = st.container()
logger: StreamlitLogger = StreamlitLogger(__name__, errors_container)

with logger:
    uf.apply_global_style()
    # Can be easily adapted in case of multiple users at the same time
    service, config = uf.initialize_global_states(ServiceManagerFacade, Config)
    # uf.set_query_params_from_session(
    #     {"projectId": ["current_project", "id"]}, config)

    editor_key_base = "datapoint_editor_"
    df_key_base = "datapoint_df_"
    editor_delete_key_base = "datapoint_delete_"

    def add_all_datapoints(message_containers: list[MessagesContainer]) -> list[int]:
        """_summary_ Saves all message containers passed with a corresponding id and returns a list of generated ids.

        Args:
            message_containers (list[MessagesContainer]): _description_

        Returns:
            list[int]: _description_
        """
        id_list = []
        for message_container in message_containers:
            datapoint_id = st.session_state.next_datapoint_id
            id_list.append(datapoint_id)
            st.session_state.datapoints.append(
                (datapoint_id, message_container))
            st.session_state.next_datapoint_id += 1
        return id_list

    @st.experimental_dialog(title="New Datapoint", width="large")
    def open_add_datapoint_dialog(datapoints_ui_container: st.container):
        """_summary_
        Adds a new datapoint via a dialog window. How  it works: it first checks if "temp_new_datapoint_id" exists. This session state is used to store a a uuid generated as id for a temporary datapoint, since a normal id would have the potential to conflict with an existing one (In theory somewhere - its just safer). This datapoint (with its df_key and editor_key and id) is needed for generating a temporary streamlit data_editor which is displayed inside the dialog window. This is necessary because you cannot display the same widget with the same data twice and deleting a widget after submitting is basically impossible without an extra button for checking. So what I do is, 1. I create a temporary widget inside the dialog window with the generated uuid id keys 2. The user can edit the temp datapoint in the dialog window as he likes, since it has a valida dataframe object and therefore the same methods to update the dataframe. Then the user can A: close the window without submitting, which would just do nothing since the the widget is cleared upon rerun if not displayed and the df just exists in memory and will be just reused by fetching "temp_new_datapoint_id" and recalculating the df_key and editor_key. Therefore when the user does not submit the dialog and want to add another datapoint afterwards, the previous dataframe state is still persisted, which can be useful. B: Submit the dialog window, which causes the creation of an ACTUAL datapoint data editor object in the datapoints list with the df data of the temporary dialog data editor, so no data is lost. The temporary df data object will be deleted after copying to avoid data leaks and the temp id will be reset to avoid any saved states that should not be.
        Args:
            datapoints_ui_container (st.container): _description_
        """
        # TODO: Depening on the current selected format, choose the correct datapoint instantiation
        df_key = None
        editor_key = None
        # Check if a temp id exists in the session state (as long as the user has not submitted a new datapoint the old one should be reused. The id defines the df_key and editor_key which are fetched through generate_datapoint_data_editor_ids(id))
        if st.session_state.get("temp_new_datapoint_id"):
            editor_key, df_key = generate_datapoint_data_editor_ids(
                st.session_state.temp_new_datapoint_id)
        # If no id exists and therefore no key, a new one is generated.
        if not df_key:
            # Generate a new key pair with a uuid for an inter mediate data editor and save the generated random uuid
            editor_key, df_key = generate_datapoint_data_editor_ids()

        # Create new message container
        message_container = MessagesContainer(messages=[])

        # Creates a new intermediate data editor with a random id INSIDE the dialog that is automatically removed later on rerun (because you cannot display the same widget in two different positions), but the changes made to this container are saved inside the df which has the regular id based key, which is then used (if submitted) to create a new data editor inside the datapoints list with the edited information.
        create_new_data_editor(message_container, df_key, editor_key)

        # The user can submit the datapoint created
        submit_button = st.button(label="Submit", key="submit_adding_new_datapoint",
                                  help="This will add a new datapoint at the end of the list", type="primary")

        # If the user has submitted the datapoint created, a new datapoint with the same data will be created at the end of the datapoints list. The message container is needed to generate the next id in the st.session_state.datapoints list and because it is needed. Can be rewritten but not for know.
        if submit_button:
            add_datapoint_data_editor_to_ui(
                datapoints_ui_container, message_container=MessagesContainer(messages=[]), is_new_datapoint=True)

    def add_datapoint_data_editor_to_ui(datapoints_ui_container: st.container, message_container: MessagesContainer | None = None, id: int | None = None, is_new_datapoint: bool | None = False) -> None:

        # The keys used to create the streamlit data_editor.
        new_datapoint_editor_key = None
        new_datapoint_df_key = None

        # Checks if it is a "new" datapoint added via the UI.
        if is_new_datapoint:
            # Saves the an arbitrary "message_container" to create a new "real" (for datapoints in the actual datapoint list) id and add it to st.session_state.datapoints. This is needed since only datapoints within this list od datapoint id, message tuples are rendered during page rerun.
            saved_ids = add_all_datapoints([message_container])
            # Fetches the saved id.
            id = saved_ids[0]
            # Retrieve saved random uuid / id used for dialog data editor key, df_key generation
            temp_data_editor_id = st.session_state.temp_new_datapoint_id
            # Generate access data for in dialog edited data editor and dataframe based on random id - only df_key is needed
            _, df_key = generate_datapoint_data_editor_ids(
                temp_data_editor_id)
            # Get in dialog modified dataframe to then copy it into the "real" datapoints session state (copy df data for new datapoint)
            stored_df = st.session_state[df_key]
            # Generate access keys for the "real" datapoint id which will be added to the datapoint list with the copied data of the modified dataframe
            new_datapoint_editor_key, new_datapoint_df_key = generate_datapoint_data_editor_ids(
                id)
            # Set modified temp id dataframe for new "real" datapoint so it will not be overwritten on creation. New df session entries are only created if a df for a specific key does not already exist in the session state. And since we created the session key (df_key, editor_key) the data editor creation function will use, a df entry will already exist and the df data set here will be used. Otherwise a new df would be created.
            st.session_state[new_datapoint_df_key] = stored_df
        else:
            # If it is just a regular already existing datapoint that should be rendered again on reload, this just generated the data editor keys for the given id.
            new_datapoint_editor_key, new_datapoint_df_key = generate_datapoint_data_editor_ids(
                id)

        # Places the datapoints inside the UI container element defined prior.
        with datapoints_ui_container:

            # Creates the "delete" key for the delete button of each datapoint.
            delete_key = f'{editor_delete_key_base}{id}'

            # Creates a new data editor with the given df_key (and its data) and editor_key. In case it is a new datapoint, the message_container is always passed, and the id is optional, because it is used to generate the UI markdown heading for the respective datapoint which is not needed for the temp datapoint.
            create_new_data_editor(
                message_container, new_datapoint_df_key, new_datapoint_editor_key, id=id)

            st.button(label="Delete", key=delete_key,
                      help="Delete the whole datapoint", type="secondary", on_click=lambda datapoint_id=id: delete_datapoint(datapoint_id))

        # If a new (via the UI) datapoint has been created, this cleans up all the states and remaining data and reruns the program once for full rerender (just in case).
        if is_new_datapoint:
            # Delete old dataframe
            del st.session_state[df_key]
            # Reset temo datapoint id
            st.session_state.temp_new_datapoint_id = 0
            # Rerun the program for everything to take effect (might not even be necessary)
            st.rerun()

    def create_new_data_editor(message_container: MessagesContainer, df_key: str, editor_key: str, id: int | None = None) -> None:
        """INFO 1: Cannot check if "key not in" because it implicitly tries to convert the possibly resulting dataframe to a boolean but you cannot check for a dataframe with true or false "if exists" because that is ambiguous because it could mean the dataframe is empty or it is None.
        # INFO 2: We have to check for the updated and persisted dataframe via "df_key" which is stored in the session state, because when switching pages, the "editor_key" is None because the widget has not been reinstantiated or something changed and streamlit could not retrieve the same session state (bit unclear as of now but also makes sense)
        # 
        # To this function a "message_container" is passed which can can be empty, a df_key which is used to access the saved dataframe from the session state, an editor_key which is used for the streamlit data_editor widget and since they follow a fixed schema based on the id, it can always be retrieved, and an optional id in case the datapoint needs a markdown heading (only necessary if it is really added to the UI list of datapoints)."""

        # If dataframe already exists, jus repopulate new editor with existing data.
        # Creates a editable dataframe for each datapoint
        if st.session_state.get(df_key) is None:
            # TODO: offer multiple different datapoint edit tables / formats based on the AI model chosen.
            st.session_state[df_key] = FileUploader.messages_to_df(
                message_container['messages'])

        # Add a heading for datapoints that should populate the UI list.
        if id:
            st.markdown(f"###### Datapoint {id}")

        # Create a streamlit data editor with the currently passed dataframe data, the current config roles as role options, the current default role based on the config roles / company schema chosen. The data editor updated the underlying dataframe object in all cases (add, edit delete) as soon as something changes -> dataframe_editor.py
        st.data_editor(
            st.session_state[df_key],
            column_config={
                "role": st.column_config.SelectboxColumn(
                    "Role",
                    help="The role of the current prompt.",
                    options=config.roles.openai,
                    required=True,
                    default=st.session_state.default_role
                ),
                "content": st.column_config.TextColumn("Content", help="Set the content for the current role.", default=""),
                "category": st.column_config.TextColumn("Category", help="You can only set one category per datapoint.", default=""),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key=editor_key,
            on_change=DataFrameEditor.update_df,
            args=(editor_key, df_key)
        )

    def generate_datapoint_data_editor_ids(id: int | None = None):
        """_summary_ This function takes in an optional id and generates the standardized datapoint data editor keys for it. If no id is provided, a "temp" unstandardized set of keys is generated where the id (generated through a uuid) is saved in st.session_state.temp_new_datapoint_id to retrieve and regenerate the corresponding keys later on. (Used for dialog datapoint data editor)

        Args:
            id (int | None, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        uuid = None
        editor_key = None
        df_key = None

        if not id:
            uuid = uuid4()
            editor_key = f"{editor_key_base}{uuid}"
            df_key = f'{df_key_base}{uuid}'
            st.session_state.temp_new_datapoint_id = uuid
        else:
            editor_key = f"{editor_key_base}{id}"
            df_key = f'{df_key_base}{id}'

        return editor_key, df_key

    def delete_datapoint(datapoint_id: int) -> None:
        """
        Removes a datapoint from the session state and deletes its associated session keys.
        """
        # Find the tuple in the list where the first element (the ID) matches datapoint_id
        print("DELETING:", datapoint_id)
        tuple_to_remove = find_datapoint_by_id(datapoint_id)
        if tuple_to_remove:
            st.session_state.datapoints.remove(tuple_to_remove)
            editor_key = f"{editor_key_base}{datapoint_id}"
            df_key = f"{df_key_base}{datapoint_id}"
            # Deleting the session keys related to this datapoint
            if editor_key in st.session_state:
                del st.session_state[editor_key]
            if df_key in st.session_state:
                del st.session_state[df_key]
        else:
            st.error("Datapoint not found or already removed.")

    def clear_current_datapoints() -> None:
        """
        Clears all current datapoints and resets counters.
        """
        # Iterate over a copy of the list to avoid modifying the list while iterating
        for datapoint_id, _ in st.session_state.datapoints[:]:
            delete_datapoint(datapoint_id)
        reset_datapoints_counter()

    def reset_datapoints_counter():
        # Set the datapoint counter back to 1
        st.session_state.next_datapoint_id = 1

    def update_page_number(page: int) -> None:
        st.session_state.current_page = page

    def calculate_pagination_indices() -> tuple[int, int]:
        start_index = (st.session_state.current_page - 1) * \
            st.session_state.datapoints_per_page
        end_index = start_index + st.session_state.datapoints_per_page

        return start_index, end_index

    def create_pagination_buttons(pagination_buttons_container_above: st.container, pagination_buttons_container_below: st.container) -> None:
        """Function to create pagination buttons with left alignment."""
        num_datapoints = len(
            st.session_state.datapoints)  # Assuming this is correctly updated elsewhere
        pages = math.ceil(
            num_datapoints / st.session_state.datapoints_per_page)
        buttons_per_row = 10  # Defines the maximum number of buttons per row

        # Handling more than 10 pages by creating multiple rows of buttons
        rows_needed = math.ceil(pages / buttons_per_row)
        for row in range(rows_needed):
            start_page = row * buttons_per_row + 1
            end_page = min(start_page + buttons_per_row, pages + 1)

            with pagination_buttons_container_above:
                cols = st.columns(buttons_per_row)  # Always create 10 columns
                for i in range(start_page, end_page):
                    with cols[i - start_page]:  # Place buttons from left to right
                        st.button(label=str(i), key=f"""page_{
                                  i}""", on_click=lambda i=i: update_page_number(i))

            with pagination_buttons_container_below:
                cols = st.columns(buttons_per_row)  # Always create 10 columns
                for i in range(start_page, end_page):
                    with cols[i - start_page]:  # Place buttons from left to right
                        # Quick fix (multiplication by large int) to avoid key duplication
                        st.button(label=str(i), key=f"""page_{
                                  i*9999999}""", on_click=lambda i=i: update_page_number(i))

    # Define a function to display paginated datapoints
    def display_paginated_datapoints(datapoints_container: st.container):
        """_summary_ This method receives a streamlit UI container to contain the datapoints rendered in a specific place.

        Args:
            datapoints_container (st.container): _description_
        """
        start_index, end_index = calculate_pagination_indices()
        # Access the sliced part of datapoints for the current page
        # Display only the slice of datapoint ids for the current pagination page (Add a streamlit data editor for each datapoint id with its underlying dataframe data).
        for id, message_container in st.session_state.datapoints[start_index:end_index]:
            add_datapoint_data_editor_to_ui(
                datapoints_container, message_container=message_container, id=id)

    def find_datapoint_by_id(datapoint_id: int) -> Optional[tuple[int, MessagesContainer]]:
        """
        Searches for a datapoint by ID within the provided list of datapoints.

        Args:
        datapoint_id (int): The ID of the datapoint to find.
        datapoints (List[Tuple[int, MessagesContainer]]): The list of datapoints to search through.

        Returns:
        Optional[Tuple[int, MessagesContainer]]: The found datapoint tuple if present, None otherwise.
        """
        return next((item for item in st.session_state.datapoints if item[0] == datapoint_id), None)

    def handle_new_file_upload(training_dataset_file: BytesIO, datapoints_container: st.container) -> None:
        """
        Processes a new file upload, initializes pagination, adds all new datapoints,
        and displays them in the specified container.

        Args:
            training_dataset_file (UploadedFile): The newly uploaded dataset file.
            datapoints_container (Container): Streamlit container to display datapoints.
        """
        print("HANDLING FILE UPLOAD")
        message_containers = FileUploader.process_uploads(
            training_dataset_file)
        if message_containers:
            st.session_state.currently_uploaded_file = training_dataset_file
            update_page_number(1)
            add_all_datapoints(message_containers)
            display_paginated_datapoints(datapoints_container)

    def reset_datapoint_states_if_all_datapoints_deleted() -> None:
        """
        Increments the file uploader key to force a widget update, clears current datapoints,
        and triggers a rerun of the Streamlit app.
        """
        st.session_state.file_uploader_key += 1
        clear_current_datapoints()
        st.rerun()

    def clear_datapoint_states_if_none_exist() -> None:
        """
        Clears all datapoint states when no datapoints exist to clean up the session state.
        """
        clear_current_datapoints()

    def handle_existing_datapoints(datapoints_container: st.container) -> None:
        """
        Displays existing datapoints in the specified container.

        Args:
            datapoints_container (Container): Streamlit container to display datapoints.
        """
        display_paginated_datapoints(datapoints_container)

    # Encapsulates logic to only rerun this fragment on change - similar to a form but without a submit button or limitations
    @st.experimental_fragment
    def load_dataset_input_form():
        st.markdown("###### Set the dataset info")
        st.text_input(label="The datasets name", value=None, max_chars=255, key="dataset_name_input",
                      help="Input the name of your dataset", placeholder="The datasets name...", disabled=True, label_visibility="collapsed")
        cols = st.columns(2)
        with cols[0]:
            st.selectbox(label="Select the dataset category",
                         options=[dataset_category for dataset_category in DatasetCategory], index=None, format_func=lambda x: x.value, key="dataset_category_selectbox", help="Select the category the dataset falls into", placeholder="Choose a dataset category", disabled=True, label_visibility="collapsed")
        with cols[1]:
            st.checkbox(label="Make the dataset globally available", value=False, key="globalize_dataset_checkbox",
                        help="Globalized datasets can be selected in the list of available datasets when creating a new project", disabled=False, label_visibility="visible")

    def load_choose_file_format_form(uploaded_dataset_file: BytesIO) -> None:
        # TODO: Make this dynamic (adapt to Enums etc.)
        tab1, tab2 = st.tabs(
            list(vars(config.upload_format_formattings).keys()))

        # TODO: Add google formattings and others.
        with tab1:
            openai_formatting_expander = st.expander(
                label="Openai formatting examples", expanded=False)

            with openai_formatting_expander:
                st.code(config.upload_format_formattings.openai,
                        line_numbers=True)

        with tab2:
            google_formatting_expander = st.expander(
                label="Google formatting examples", expanded=False)

            with google_formatting_expander:
                st.code("Nothing to see here",
                        line_numbers=True)

        formatting_cols = st.columns(2)

        print("LENGTH", len(st.session_state.datapoints))
        # Only changeable if no datapoints exist at the moment
        with formatting_cols[0]:
            st.selectbox(label="Choose a company formatting style",
                         options=config.fine_tuning_companies.companies, index=None, placeholder="Choose a companies formatting style", help="Chose the formatting style for the file to upload based on company.", label_visibility="collapsed", key="chosen_company", disabled=len(st.session_state.datapoints) or uploaded_dataset_file is not None)

        # Only changeable if a company has been chosen and no datapoints exist at the moment
        with formatting_cols[1]:
            st.selectbox(label="Choose an upload file format",
                         options=getattr(config.upload_formats, st.session_state.chosen_company) if st.session_state.chosen_company else [], index=None, placeholder="Choose file format", help="Choose the format of the file you want to upload and the datapoints you want to create", label_visibility="collapsed", key="chosen_file_format", disabled=not st.session_state.chosen_company or len(st.session_state.datapoints) or uploaded_dataset_file is not None)

            # Set default role for datapoint messages (e.g. role = "system")
            st.session_state.default_role = getattr(config.roles, st.session_state.chosen_company)[
                0] if st.session_state.chosen_company else None

    def manage_datapoints_flow(uploaded_dataset_file: BytesIO, datapoints_container: st.container, pagination_buttons_container_above: st.container, pagination_buttons_container_below: st.container) -> None:
        """
        Manages the flow of datapoints based on their current state and file changes.
        Updates the UI components according to the file and datapoints state.

        Args:
            uploaded_dataset_file (UploadedFile): The file uploaded by the user.
            pagination_buttons_container (Container): Streamlit container for pagination buttons.
            datapoints_container (Container): Streamlit container for displaying datapoints.
        """
        # If a new file has been uploaded
        if uploaded_dataset_file and not st.session_state.datapoints and st.session_state.currently_uploaded_file != uploaded_dataset_file:
            handle_new_file_upload(uploaded_dataset_file, datapoints_container)
        # If all datapoints have been deleted from the UI
        elif uploaded_dataset_file and not st.session_state.datapoints and st.session_state.currently_uploaded_file == uploaded_dataset_file:
            reset_datapoint_states_if_all_datapoints_deleted()
        # If there are no datapoints -> Is somewhat redundant and can be potentially changed but carefully!
        elif not st.session_state.datapoints:
            clear_datapoint_states_if_none_exist()
        # Rerender all currently displayed datapoints
        else:
            handle_existing_datapoints(datapoints_container)

        # Always create pagination buttons
        create_pagination_buttons(
            pagination_buttons_container_above, pagination_buttons_container_below)

    def load_page():
        # Checks whether datapoints and next datapoint id already exist and if not initializes them.
        # Current tuples of (dattapoint_id: id, datapoint_message_container: MessageContainer) -> The messagecontainer saved here is only relevant for the first render without an underlying dataframe and could be deleted afterwards theoretically (I guess).
        if not st.session_state.get('datapoints'):
            st.session_state.datapoints = []
        # The datapoint id counter. Whenever a new datapoint is added, this counter goes up.
        if not st.session_state.get('next_datapoint_id'):
            st.session_state.next_datapoint_id = 1
        # Current default role based on selected datapoint formatting schema.
        if not st.session_state.get('default_role'):
            st.session_state.default_role = None
        # Currently uploaded file in BytesIO (I think).
        if not st.session_state.get("currently_uploaded_file"):
            st.session_state.currently_uploaded_file = None
        # Session state key of the file uploader widget. This is necessary to properly programatically reset the file uploader when all datapoints are deleted. Else the file uploaded will still be displayed (I think).
        if not st.session_state.get('file_uploader_key'):
            st.session_state.file_uploader_key = 0
        # The current pagination page.
        if not st.session_state.get("current_page"):
            st.session_state.current_page = 1  # current page
        # The amount of datapoints displayed per page.
        if not st.session_state.get("datapoints_per_page"):
            # Number of datapoints per page. Less means faster reload speed.
            st.session_state.datapoints_per_page = 50
        # Current temporary (dialog datapoint) datapoint uuid.
        if not st.session_state.get("temp_new_datapoint_id"):
            st.session_state.temp_new_datapoint_id = 0
        if not st.session_state.get("chosen_file_format"):
            st.session_state.chosen_file_format = None
        if not st.session_state.get("chosen_company"):
            st.session_state.chosen_company = None

        chosen_file_format_container = st.container()

        # The datapoints are cleared when a new file is uploaded or the current file is deleted
        # The file uploader is only available if no datapoints exist, a file format is chosen and no dataset is currently uploaded.
        uploaded_dataset_file = st.file_uploader(
            label="Upload new datasets", type=st.session_state.get("chosen_file_format"), key=st.session_state.file_uploader_key, accept_multiple_files=False, help="Upload a file formatted in the format chosen. Uploaded datasets will be directly available to select within your project after submitting.", disabled=False if st.session_state.chosen_file_format else True, on_change=clear_current_datapoints)

        with chosen_file_format_container:
            # Insert chose file format form
            load_choose_file_format_form(uploaded_dataset_file)

        # Insert the dataset input form
        load_dataset_input_form()

        # Create container for pagination buttons and datapoint data editors to populate later.
        pagination_buttons_container_above = st.container(border=False)
        datapoints_container = st.container(border=False)
        pagination_buttons_container_below = st.container(border=False)

        # Runs the page depending on the current input
        manage_datapoints_flow(
            uploaded_dataset_file, datapoints_container, pagination_buttons_container_above, pagination_buttons_container_below)

        print("DATAPOINT IDS", [x[0] for x in st.session_state.datapoints])

        cols = st.columns((1, 5, 1))

        with cols[1]:
            # Add a new datapoint via the UI.
            add_new_datapoint_buton = st.button(label="Add New Datapoint", key="add_new_datapoint_button",
                                                help="Add a new datapoint to the current dataset", type="secondary", disabled=not st.session_state.chosen_file_format)
            if add_new_datapoint_buton:
                # Need to be called outside of a callback or else a "RuntimeError: Could not find fragment with id <> will occure!"
                open_add_datapoint_dialog(datapoints_container)

            print("hallo")

        with cols[2]:
            # Submit all datapoint dataframes, convert them to datapoint objects and save them in the database as dataset. TODO: Implement the functionality.
            st.button(label="Submit", key="submit_dataset",
                      help="Submit the dataset with all its datapoints", type="primary", disabled=not st.session_state.get('datapoints'))

    load_page()
