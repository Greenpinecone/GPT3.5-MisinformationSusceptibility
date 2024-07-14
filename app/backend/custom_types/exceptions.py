class CustomValidationError(Exception):
    def __init__(self, message="", operation_type="Unknown Operation", errors="Unknown Errors"):
        self.message = message
        self.operation_type = operation_type
        self.errors = errors
