"""
This is the main entry point for the application. It orchestrates the workflow
of the project, calling functions from other modules and handling the overall process flow.
"""

# Import necessary modules and packages

import streamlit as st
import numpy as np
import pandas as pd
import plotly
from util.logger import StreamlitLogger  # pylint: disable=import-error


def main():
    st.write("Test - I am running in streamlit!")
    logger = StreamlitLogger()


if __name__ == "__main__":
    # This condition ensures that main() is called only when this script is executed directly (not imported)
    main()
