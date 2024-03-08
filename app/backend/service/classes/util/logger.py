"""
This module sets up logging for the application, providing a standardized way
to log messages and errors across different modules.
"""

from typing import Any
import logging
from logging.handlers import RotatingFileHandler
import streamlit as st


class Logger:
    """
    Sets up and manages logging for the application.

    This class configures application-wide logging which can output to both
    console and file. It supports log rotation to prevent log files from
    consuming too much disk space.

    Attributes:
        logger (logging.Logger): Configured logger instance.
    """

    def __init__(self, name: str = "global", log_file: str = 'logs/app.log', level: int = logging.INFO) -> None:
        """
        Initializes the logger with specified name, log file, and level.

        Args:
            name (str): Name of the logger, typically __name__ to reflect the module name. Defaults to 'global'.
            log_file (str): Name of the file where logs will be written. Defaults to 'app.log'.
            level (int): Logging level, e.g., logging.INFO, logging.DEBUG. Defaults to logging.INFO.
        """
        self.logger: logging.Logger = logging.getLogger(name)

        self.logger.setLevel(level)

        # Create formatter
        formatter: logging.Formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Create console handler and set level to debug
        ch: logging.StreamHandler = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        # Create file handler for logging to a file
        fh: RotatingFileHandler = RotatingFileHandler(
            log_file, maxBytes=1048576, backupCount=1)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def get_logger(self) -> logging.Logger:
        """
        Returns the configured logger instance.

        Returns:
            logging.Logger: The configured logger.
        """
        return self.logger

    def info(self, message: str) -> None:
        """
        Logs an informational message.

        Args:
            message (str): The message to be logged.
        """
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """
        Logs a warning message.

        Args:
            message (str): The message to be logged.
        """
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """
        Logs an error message.

        Args:
            message (str): The message to be logged.
        """
        self.logger.error(message)


class StreamlitLogger(Logger):
    """
    Extends Logger to add functionality for logging messages to the Streamlit UI.
    """

    def ui_info(self, message: str) -> None:
        """
        Displays an informational message in the Streamlit UI.

        Args:
            message (str): The message to be displayed.
        """
        st.info(message)

    def ui_warning(self, message: str) -> None:
        """
        Displays a warning message in the Streamlit UI.

        Args:
            message (str): The message to be displayed.
        """
        st.warning(message)

    def ui_error(self, message: str) -> None:
        """
        Displays an error message in the Streamlit UI.

        Args:
            message (str): The message to be displayed.
        """
        st.error(message)
