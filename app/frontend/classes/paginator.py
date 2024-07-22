"""
A module to hanldle pagination of various items.

Classes:
    Paginator:
"""


import math
import streamlit as st
from typing import Any
from uuid import uuid4
from streamlit.delta_generator import DeltaGenerator


class Paginator:
    """
    A class to handle pagination for a list of items in a Streamlit application.

    Attributes:
        items_per_page (int): Number of items to display per page.
        current_page (int): The current page number.
        total_pages (int): The total number of pages.

    Methods:
        get_total_pages(num_items: int) -> int:
            Returns the total number of pages based on the number of items.
        get_paginated_items(items: list[Any]) -> list:
            Returns the items for the current page.
        set_page_num(page_num: int) -> None:
            Sets the current page number.
        create_pagination_buttons(pagination_buttons_container: DeltaGenerator, items: list, columns_partition: list[float] = [3, 1, 1.5, 1, 3]) -> None:
            Creates pagination buttons in the given container.
    """

    def __init__(self, items_per_page: int = 50) -> None:
        """
        Initializes the Paginator with the specified number of items per page.

        Parameters:
            items_per_page (int): Number of items to display per page. Default is 50.
        """

        self.items_per_page = items_per_page
        self.current_page = 1
        self.total_pages = 1

    def get_total_pages(self, num_items: int) -> int:
        """
        Returns the total number of pages based on the number of items.

        Parameters:
            num_items (int): The total number of items.

        Returns:
            int: The total number of pages.
        """

        return math.ceil(num_items / self.items_per_page)

    def get_paginated_items(self, items: list[Any]) -> list:
        """
        Returns the items for the current page.

        Parameters:
            items (list[Any]): The list of items to paginate.

        Returns:
            list: The items for the current page.
        """

        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        return items[start_index:end_index]

    def set_page_num(self, page_num: int):
        """
        Sets the current page number.

        Parameters:
            page_num (int): The page number to set.
        """

        self.current_page = page_num

    def create_pagination_buttons(self, pagination_buttons_container: DeltaGenerator, items: list, columns_partition: list[float] = [3, 1, 1.5, 1, 3]) -> None:
        """
        Creates pagination buttons in the given container.

        Parameters:
            pagination_buttons_container (DeltaGenerator): The container to place the buttons in.
            items (list): The list of items to paginate.
            columns_partition (list[float]): The column widths for the pagination buttons. Default is [3, 1, 1.5, 1, 3].
        """

        num_items = len(items)
        self.total_pages = self.get_total_pages(num_items)

        if self.total_pages > 1:
            with pagination_buttons_container:
                st.write(f"Page {self.current_page} of {self.total_pages}")

                # Adjust column widths as needed
                cols = st.columns(columns_partition)
                with cols[1]:
                    if self.current_page > 1:
                        prev_button_key = f"""prev_{
                            uuid4()}"""
                        st.button(label="Prev", key=prev_button_key, help="""Go to the previous page.
                                  
                                  INFO: Be sure to only press the button ONCE and let the page fully reload afterwards, else unintended side effects may occur""", on_click=lambda: self.set_page_num(
                            self.current_page - 1))

                with cols[2]:
                    page_input_key = f"page_input_{uuid4()}"
                    st.number_input(
                        label="Current page",
                        min_value=1,
                        max_value=self.total_pages,
                        value=self.current_page,
                        key=page_input_key,
                        label_visibility="collapsed",
                        on_change=lambda: self.set_page_num(
                            st.session_state[page_input_key]
                        ))

                with cols[3]:
                    if self.current_page < self.total_pages:
                        next_button_key = f"""next_{
                            uuid4()}"""
                        st.button(label="Next", key=next_button_key, on_click=lambda: self.set_page_num(
                            self.current_page + 1), help="""Go to the previous page.
                                  
                                  INFO: Be sure to only press the button ONCE and let the page fully reload afterwards, else unintended side effects may occur""")
