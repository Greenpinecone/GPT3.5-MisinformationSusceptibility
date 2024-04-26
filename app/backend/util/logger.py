"""
This module sets up logging for the application, providing a standardized way
to log messages and errors across different modules.
"""

from typing import Any
import logging
from logging.handlers import RotatingFileHandler
import streamlit as st
from sqlalchemy.exc import MultipleResultsFound, NoResultFound, SQLAlchemyError
from marshmallow import ValidationError
import os


class Logger:
    """
    Sets up and manages logging for the application.

    This class configures application-wide logging which can output to both
    console and file. It supports log rotation to prevent log files from
    consuming too much disk space.

    Attributes:
        logger (logging.Logger): Configured logger instance.
    """

    def __init__(self, name: str, log_dir: str = 'backend/logs', log_file: str = 'app.log', level: int = logging.DEBUG) -> None:
        """
        Configures a logger with the given name, log level, and log file.
        This method ensures that each logger is only configured once.
        """

        # Ensure the log directory path is correctly formed
        log_path = os.path.join(log_dir, log_file)

        # Ensure the directory exists (not the file path)
        log_directory = os.path.dirname(log_path)
        os.makedirs(log_directory, exist_ok=True)

        self.logger = logging.getLogger(name)
        if not self.logger.handlers:  # Check if the logger already has handlers
            self.logger.setLevel(level)
            formatter = logging.Formatter(
                "[%(asctime)s] [%(filename)s:%(lineno)s - %(funcName)20s() ]%(levelname)s: %(message)s",
                datefmt='%Y-%m-%d %H:%M:%S')

            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

            # File handler
            fh = RotatingFileHandler(log_path, maxBytes=1048576, backupCount=1)
            fh.setLevel(level)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def __getattr__(self, name):
        """
        Forward attribute access to the underlying logging.Logger object.
        This allows direct use of logging methods on instances of this class.
        """
        return getattr(self.logger, name)


class StreamlitLogger(Logger):
    """
    Extends Logger to add functionality for logging messages to the Streamlit UI.
    """

    def __init__(self, name: str, log_dir: str = 'backend/logs', log_file: str = 'app.log', level: int = logging.DEBUG) -> None:
        # Call the parent class's __init__ method
        super().__init__(name, log_dir, log_file, level)

    def __getattr__(self, name):
        """
        This ensures that if an attribute is not found in StreamlitLogger,
        it's looked up in the Logger class, which then forwards it to
        the underlying logging.Logger object if not found.
        """
        return super().__getattr__(name)

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

    def display_errors(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)  # Or handle successful result
        except NoResultFound as e:
            self.ui_error(
                str(f"Check the database an inconsistency might have occured: {e}"))
        except MultipleResultsFound as e:
            self.ui_error(
                str(f"Check the database, an id duplication might have occured: {e}"))
        except ValidationError as e:
            self.ui_error(str(e))
        except SQLAlchemyError as e:
            self.ui_error(str(f"Something went wrong with the database: {e}"))
        except Exception as e:
            self.ui_error("An unexpected error occurred, check the logs.")
