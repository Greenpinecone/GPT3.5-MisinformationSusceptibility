import streamlit as st


def apply_global_style() -> None:
    st.markdown("""
    <style>
    /* General styles for all widgets inside #root */
    #root, #root .stButton, #root .stTextInput, #root .stDataFrame, #root .stPlotlyChart, #root .stAlert {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        justify-content: center;
        width: 100%;
    }
    
    /* Make the Checkbox centered to the height and width of the outer container - TODO: Center vertically! */
    #root .stCheckbox, #root .checkbox {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        justify-content: center;
        width: 100%;
        height: 100%
    }
    
    /* Additional specific style for .stJson */
    #root .object-key-val, #root .object-content, #root .stCodeBlock {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        text-align: left;
        justify-content: flex-start;
        width: 100%;
    }
    
    #root .stCodeBlock, #root .stExpanderDetails .stMarkdown pre {
            overflow-x: auto;  /* Activates horizontal scrolling */
            white-space: pre;  /* Ensures whitespace is preserved */
        }
    
    /* Style separators */
    hr {
        height: 2px;
        margin-top: 14px;
    }
    
    </style>
    """, unsafe_allow_html=True)
