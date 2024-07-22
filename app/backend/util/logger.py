"""
This module sets up logging for the application, providing a standardized way
to log messages and errors across different modules.
"""

import logging
from logging.handlers import RotatingFileHandler
import streamlit as st
from pathlib import Path
from sqlalchemy.exc import MultipleResultsFound, NoResultFound, SQLAlchemyError
from marshmallow import ValidationError
from app.backend.custom_types.exceptions import CustomValidationError
from app.frontend.classes.manager.toast_manager import ToastManager


class Logger:
    """
    Sets up and manages logging for the application.

    This class configures application-wide logging which can output to both
    console and file. It supports log rotation to prevent log files from
    consuming too much disk space.

    Attributes:
        logger (logging.Logger): Configured logger instance.
    """

    def __init__(self, name: str, log_dir: str = 'backend/logs', log_file: str = 'app.log', root_marker: str = "app", level: int = logging.DEBUG) -> None:
        """
        Configures a logger with the given name, log level, and log file.
        This method ensures that each logger is only configured once.
        """

        # Get the path to the directory where this script runs
        current_path = Path(__file__).resolve()

        # Find the project root
        project_root = self.find_project_root(current_path, root_marker)

        # Construct the full path to the log file
        log_path = project_root / log_dir / log_file

        # Ensure the log directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

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

    def find_project_root(self, start_path: Path, root_marker: str) -> Path:
        """
        Traverse up from start_path to find the directory marked by a marker.

        Args:
            start_path (Path): The starting path to begin the search.
            root_marker (str): The marker indicating the project root directory.

        Returns:
            Path: The path to the project root directory.

        Raises:
            FileNotFoundError: If the project root is not found starting from start_path.
        """

        for parent in start_path.parents:
            # Check if the parent directory or a marker file exists
            if (parent / root_marker).exists() or (parent.name == root_marker):
                return parent
        raise FileNotFoundError(
            f"Project root not found starting from {start_path}")

    def __getattr__(self, name):
        """
        Forward attribute access to the underlying logging.Logger object.

        Args:
            name (str): The attribute name to access.

        Returns:
            Any: The attribute from the underlying logging.Logger object.
        """
        return getattr(self.logger, name)


class StreamlitLogger(Logger):
    """
    Initialize the StreamlitLogger with a logger name and error container.

    Args:
        name (str): The name of the logger.
        errors_container (st.container): The Streamlit container for displaying errors.
        log_dir (str): The directory where log files are stored.
        log_file (str): The name of the log file.
        root_marker (str): The marker indicating the project root directory.
        level (int): The logging level (default is logging.DEBUG).
    """

    def __init__(self, name: str, errors_container: st.container, log_dir: str = 'backend/logs', log_file: str = 'app.log', root_marker: str = "app", level: int = logging.DEBUG) -> None:
        self.errors_container = errors_container
        # Call the parent class's __init__ method
        super().__init__(name, log_dir, log_file, root_marker, level)

    def __getattr__(self, name):
        """
        Forward attribute access to the Logger class and then to the underlying logging.Logger object if not found.

        Args:
            name (str): The attribute name to access.

        Returns:
            Any: The attribute from the Logger class or the underlying logging.Logger object.
        """
        return super().__getattr__(name)

    def __enter__(self):
        """
        Enter the runtime context related to this object.

        Returns:
            StreamlitLogger: The StreamlitLogger instance itself.
        """

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context related to this object.

        Args:
            exc_type (Type[BaseException]): The exception type.
            exc_value (BaseException): The exception instance.
            traceback (TracebackType): The traceback object.

        Returns:
            bool: True if the exception is handled, otherwise False.
        """

        # We need to check if exc_type is an instance of Exception to avoid catching "non error" exception which are directly derived from the BaseException class like streamlits "RerunException" (or KeyboardInterrupt) to avoid issues with page reload / page reloads after navigating to another page, when using the context manager for error handling.
        if exc_type is not None and issubclass(exc_type, Exception):
            self.handle_exception(exc_type, exc_value)
            # Suppresses the exception unless it needs to propagate.
            return True
        else:
            # Lets BaseExceptions propagate furhter to avoid streamlit page reload issues.
            return False

    def handle_exception(self, exc_type, exc_value):
        """
        Handle exceptions by logging them and displaying them in the Streamlit UI.

        Args:
            exc_type (Type[BaseException]): The exception type.
            exc_value (BaseException): The exception instance.
        """

        with self.errors_container:
            if issubclass(exc_type, NoResultFound):
                self.ui_error(
                    f"Check the database an inconsistency might have occurred:\n{exc_value}")
            elif issubclass(exc_type, MultipleResultsFound):
                self.ui_error(
                    f"Check the database, an id duplication might have occurred:\n{exc_value}")
            elif issubclass(exc_type, ValidationError):
                self.ui_error(
                    f"An unchecked validation error has been thrown:\n{exc_value}")
            elif issubclass(exc_type, CustomValidationError):
                self.handle_validation_error(exc_value)
            elif issubclass(exc_type, SQLAlchemyError):
                self.ui_error(
                    f"Something went wrong with the database:\n{exc_value}")
            elif issubclass(exc_type, Exception):
                self.ui_error(f"An unexpected error occurred:\n{exc_value}")

    def handle_validation_error(self, e):
        """
        Handle validation errors by displaying them in the Streamlit UI.

        Args:
            e (CustomValidationError): The validation error instance.
        """

        if hasattr(e, 'errors') and hasattr(e, 'operation_type'):
            # Handles dictionaries with lists, single values or None.
            error_messages = self._process_errors(e.errors)
            message = e.message if e.message else "Validation errors occurred during operaion"
            ToastManager.show_toast(f"{message} '{e.operation_type}':\n" +
                                    "\n".join(error_messages), "error")
        else:
            ToastManager.show_toast(
                f"Validation errors occurred:\n{e}", "error")

    def _format_error_message(self, idx, field, msgs):
        if isinstance(msgs, dict):
            # Format messages from a dictionary
            return f"{idx+1}. {field}: {', '.join(f'{key}={value}' for key, value in msgs.items())}"
        elif isinstance(msgs, list):
            # Join list items into a single string
            return f"{idx+1}. {field}: {', '.join(msgs)}"
        else:
            # Handle other cases or malformed messages
            return f"{idx+1}. {field}: (Invalid message format)"

    def _process_errors(self, errors):
        if isinstance(errors, dict):
            # Process errors assuming it is a dictionary of messages
            return [self._format_error_message(idx, field, msgs) for idx, (field, msgs) in enumerate(errors.items())]
        elif isinstance(errors, list):
            # Process errors assuming it is a list of generic error messages
            return [f"{idx+1}. Error: {error}" for idx, error in enumerate(errors)]
        else:
            # Return a generic error if the format is unexpected
            return ["Unexpected error format"]

    def ui_error(self, message: str) -> None:
        """
        Displays an error message in the Streamlit UI.
        """
        st.error(message)

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
