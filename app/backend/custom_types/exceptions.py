"""
This module contains custom exception classes for the application.

Classes:
    CustomValidationError: Custom exception raised for validation errors.
"""


class CustomValidationError(Exception):
    """
    Custom exception raised for validation errors.

    Attributes:
        message (str): Description of the validation error.
        operation_type (str): Type of operation during which the error occurred.
        errors (str): Specific errors that caused the validation to fail.
    """

    def __init__(self, message="", operation_type="Unknown Operation", errors="Unknown Errors"):
        """
        Initializes the CustomValidationError instance.

        Args:
            message (str): Description of the validation error.
            operation_type (str): Type of operation during which the error occurred.
            errors (str): Specific errors that caused the validation to fail.
        """
        self.message = message
        self.operation_type = operation_type
        self.errors = errors
