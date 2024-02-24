"""
This module sets up logging for the application, providing a standardized way
to log messages and errors across different modules.
"""

import logging
from logging.handlers import RotatingFileHandler
import streamlit as st


class Logger:
    """Sets up and manages logging for the application.

    This class configures application-wide logging which can output to both
    console and file. It supports log rotation to prevent log files from
    consuming too much disk space.

    Attributes:
        logger (logging.Logger): Configured logger instance.
    """

    def __init__(self, name="global", log_file='app.log', level=logging.INFO):
        """Initializes the logger with specified name, log file, and level.

        Args:
            name (str): Name of the logger, typically __name__ to reflect the
                module name. Defaults to __name__.
            log_file (str): Name of the file where logs will be written. 
                Defaults to 'app.log'.
            level (int): Logging level, e.g., logging.INFO, logging.DEBUG.
                Defaults to logging.INFO.
        """
        self.logger = logging.getLogger(name)

        if not self.logger.handlers:  # Check if the logger already has handlers

            self.logger.setLevel(level)

            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # Create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

            # Create file handler for logging to a file
            # 1MB per file, with backup up to 5 files.
            fh = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=1)
            fh.setLevel(level)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

        # This is a Streamlit-specific setting. Streamlit writes its logs to stdout, and adding a StreamHandler without
        # checking if the logger already has handlers can result in duplicate logs if Streamlit's re-run mechanism triggers.
        # The above setup ensures custom logs are also outputted correctly while avoiding duplication.

    def get_logger(self):
        """Returns the configured logger instance.

        Returns:
            logging.Logger: The configured logger.
        """
        return self.logger

    def info(self, message):
        """
        Logs an informational message.

        Args:
            message: The message to be logged.
        """
        self.logger.info(message)

    def warning(self, message):
        """
        Logs a warning message.

        Args:
            message: The message to be logged.
        """
        self.logger.warning(message)

    def error(self, message):
        """
        Logs an error message.

        Args:
            message: The message to be logged.
        """
        self.logger.error(message)


class StreamlitLogger(Logger):
    """
    Extends Logger to add functionality for logging messages to the Streamlit UI.
    """

    def ui_info(self, message):
        """
        Displays an informational message in the Streamlit UI.

        Args:
            message: The message to be logged.
        """
        st.info(message)

    def ui_warning(self, message):
        """
        Displays a warning message in the Streamlit UI.

        Args:
            message: The message to be logged.
        """
        st.warning(message)

    def ui_error(self, message):
        """
        Displays an error message in the Streamlit UI.

        Args:
            message: The message to be logged.
        """
        st.error(message)
