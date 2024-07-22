"""
A module containing functions to set individual styles where needed.
"""


import streamlit as st


def center_elements_with_custom_span_in_column(custom_style: str):
    """
    Applies custom CSS styling to center elements with a specific class inside Streamlit columns.

    This function injects CSS to style any column that contains a `<span>` with the specified class name.
    The styling centers the content of the column and adjusts text properties to avoid overflow issues.

    Args:
        custom_style (str): The class name to target for custom styling.
    """

    # Styles any column that has a <span> with the class "custom-style" inside in the following way.
    # Keep in mind that every time you use a st.markdown(<span id="my_tag"></span>) as a css-tag you will trigger the gab attribute of the parent container. This will give you a 1rem empty space. To counteract this I did gap: 0rem:
    st.write(f"""
        <style>
        div[data-testid="column"]:has(span.{custom_style}) div.stTextLabelWrapper {{
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        justify-content: center;
        height: 100%;
        overflow: hidden;  /* Disable overflow */
        white-space: normal;  /* Enable text wrapping */
        word-wrap: break-word;  /* Ensure long words are broken */
        gap: 0rem;
    }}
        </style>
        """, unsafe_allow_html=True)


def center_checkboxes():
    """
    Applies custom CSS styling to center checkboxes in Streamlit.

    This function injects CSS to style checkboxes so that they are centered within their container.
    """

    st.write("""
        <style>
        div[data-testid="stCheckbox"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        justify-content: center;
        height: 100%;
    }
        </style>
        """, unsafe_allow_html=True)


def custom_style_span(custom_style: str):
    """
    Injects a span element with a specific class name into Streamlit's HTML.

    This function uses Streamlit's markdown capability to insert a span with a given class name.
    This can be used to apply custom CSS styles to specific elements.

    Args:
        custom_style (str): The class name to apply to the span element.
    """

    st.markdown(f"""
    <span class='{custom_style}'></span>
    """, unsafe_allow_html=True)
