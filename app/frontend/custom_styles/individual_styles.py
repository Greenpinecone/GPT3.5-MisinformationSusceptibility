
import streamlit as st


def center_elements_with_custom_span_in_column(custom_style: str):
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
    st.markdown(f"""
    <span class='{custom_style}'></span>
    """, unsafe_allow_html=True)
