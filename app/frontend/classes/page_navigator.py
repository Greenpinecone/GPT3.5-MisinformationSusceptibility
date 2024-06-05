import streamlit as st
from backend.util.config import PAGE_CONFIG


class PageNavigator:

    @classmethod
    def set_navbar(cls, label: str, previous_page: str, help: str, icon: str = "◀️", is_left: bool = True, nav_bar_cols_config: list[int] = [1.5, 4.5, 1.5], gap: str = "large") -> None:
        nav_bar_cols = st.columns(nav_bar_cols_config, gap)
        if not PAGE_CONFIG.get(previous_page):
            raise ValueError(
                f"Page name '{previous_page}' not found in configuration.")

        if is_left:
            with nav_bar_cols[0]:
                if st.button(f"{icon} {label}", help=help):
                    cls.navigate_to_page(previous_page)
        else:
            with nav_bar_cols[2]:
                if st.button(f"{label} {icon}", help=help):
                    cls.navigate_to_page(previous_page)

    @staticmethod
    def navigate_to_page(page: str) -> None:
        if not PAGE_CONFIG.get(page):
            raise ValueError(f"Page name '{page}' not found in configuration.")
        else:
            page_path = PAGE_CONFIG[page]['path']
            st.switch_page(page_path)
