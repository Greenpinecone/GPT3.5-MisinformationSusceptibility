
import streamlit as st


def center_elements_with_custom_span_in_column():
    # Styles any column that has a <span> with the class "custom-style" inside in the following way.
    st.write("""
        <style>
            div[data-testid="column"]:has(span):has(.custom-style)
    {
        display: flex;
        flex-direction: column;
        justify-content: center;
        width: 100%;
        align-items: center; /* Added to center horizontally */
    }
        </style>
        """, unsafe_allow_html=True)
