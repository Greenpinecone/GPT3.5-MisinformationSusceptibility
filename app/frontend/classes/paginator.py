import math
import streamlit as st
from typing import Any
from streamlit.delta_generator import DeltaGenerator
from uuid import uuid4


class Paginator:
    def __init__(self, items_per_page: int = 50) -> None:
        self.items_per_page = items_per_page
        self.current_page = 1

    def get_paginated_items(self, items: list[Any]) -> list[Any]:
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        return items[start_index:end_index]

    def create_pagination_buttons(self, pagination_buttons_container: DeltaGenerator, items: list[Any]) -> None:
        num_items = len(items)
        total_pages = math.ceil(num_items / self.items_per_page)
        buttons_per_row = 10

        for row_start in range(1, total_pages + 1, buttons_per_row):
            row_end = min(row_start + buttons_per_row, total_pages + 1)
            with pagination_buttons_container:
                cols = st.columns(buttons_per_row)
                for page_num, col in zip(range(row_start, row_end), cols):
                    with col:
                        st.button(label=str(page_num), key=f"""page_{page_num}_{
                                  uuid4()}""", on_click=lambda page=page_num: self.set_page_num(page))

    def set_page_num(self, page_num: int):
        self.current_page = page_num
        print(self.current_page)
        print("HALLO")
