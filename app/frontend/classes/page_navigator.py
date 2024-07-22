"""
A module to handle page navigation.

Classes:
    PageNavigator:
"""


import streamlit as st
from typing import Any, Callable, Literal
from app.backend.util.config import PAGE_CONFIG


class PageNavigator:
    """
    A class to manage page navigation and navigation bar setup within a Streamlit app.

    Methods:
        set_navbar(label: str, previous_page: str, help: str, icon: str = "◀️", is_left: bool = True, nav_bar_cols_config: list[int] = [1.5, 4.5, 1.5], gap: str = "large", func: Callable[..., None] = None, args: list[Any] = None, disabled: bool = False, type: str | Literal["secondary", "primary"] = "secondary", **kwargs) -> None:
            Sets up a navigation bar with customizable button.
        navigate_to_page(page: str) -> None:
            Navigates to the specified page based on the configuration.
    """

    @classmethod
    def set_navbar(cls, label: str, previous_page: str, help: str, icon: str = "◀️", is_left: bool = True, nav_bar_cols_config: list[int] = [1.5, 4.5, 1.5], gap: str = "large", func: Callable[..., None] = None, args: list[Any] = None, disabled: bool = False, type: str | Literal["secondary", "primary"] = "secondary", **kwargs) -> None:
        """
        Sets up a navigation bar with customizable button.

        Parameters:
            label (str): The label for the button.
            previous_page (str): The page name to navigate to.
            help (str): Help text for the button.
            icon (str): Icon to display on the button. Default is "◀️".
            is_left (bool): If True, the button is placed on the left side of the navbar. Default is True.
            nav_bar_cols_config (list[int]): Configuration for the navbar columns. Default is [1.5, 4.5, 1.5].
            gap (str): Gap between the columns. Default is "large".
            func (Callable[..., None]): Optional function to call when the button is clicked.
            args (list[Any]): Arguments to pass to the function. Default is an empty list.
            disabled (bool): If True, the button is disabled. Default is False.
            type (str | Literal["secondary", "primary"]): Button type. Default is "secondary".
            **kwargs: Additional keyword arguments to pass to the function.

        Raises:
            ValueError: If the previous_page is not found in the configuration.
        """

        if args is None:
            args = []

        nav_bar_cols = st.columns(nav_bar_cols_config, gap=gap)
        if not PAGE_CONFIG.get(previous_page):
            raise ValueError(
                f"Page name '{previous_page}' not found in configuration.")

        if is_left:
            with nav_bar_cols[0]:
                if st.button(label=f"{icon} {label}", help=help, disabled=disabled, type=type):
                    if func:
                        func(*args, **kwargs)
                    cls.navigate_to_page(previous_page)
        else:
            with nav_bar_cols[-1]:
                if st.button(label=f"{label} {icon}", help=help, disabled=disabled, type=type):
                    if func:
                        func(*args, **kwargs)
                    cls.navigate_to_page(previous_page)

    @staticmethod
    def navigate_to_page(page: str) -> None:
        """
        Navigates to the specified page based on the configuration.

        Parameters:
            page (str): The name of the page to navigate to.

        Raises:
            ValueError: If the page is not found in the configuration.
        """

        if not PAGE_CONFIG.get(page):
            raise ValueError(f"Page name '{page}' not found in configuration.")
        else:
            page_path = PAGE_CONFIG[page]['path']
            st.switch_page(page_path)
