from io import BytesIO
import json
from typing import Any, Iterator
from backend.custom_types.typedicts import *
from backend.util.utility_functions import show_toast
import pandas as pd

# TODO: Implement different data validators and handlers for different data formats so that user can upload and edit their data for different AI models that do not support the same format (jsonl) and structure as google.


class FileUploader:

    def __init__(self):
        pass

    @staticmethod
    def validate_jsonl(file_iterator: Iterator[str]) -> bool:
        """ Validates that each line in the file is proper JSON. """
        for line_number, line in enumerate(file_iterator, start=1):
            try:
                json.loads(line)  # Try parsing each line as JSON
            except json.JSONDecodeError as e:
                show_toast(message=f"""Invalid JSON on line {
                           line_number}: {e}", message_type="error""")
                # raise ValueError(f"Invalid JSON on line {line_number}: {e}")
        return True

    @staticmethod
    def convert_to_messages_container(file_iterator: Iterator[str]) -> list[MessagesContainer]:
        """ Converts valid JSONL data to list of MessagesContainer typed dicts. """
        containers = []
        for line in file_iterator:
            record = json.loads(line)
            if "messages" in record:
                container = MessagesContainer(messages=record["messages"])
                containers.append(container)
            else:
                show_toast(
                    message="JSONL does not conform to expected 'messages' format", message_type="error")
                # raise ValueError("JSON does not conform to expected 'messages' format")
        return containers

    @staticmethod
    def process_uploads(uploaded_files: list[BytesIO]) -> list[MessagesContainer]:
        """ Processes an uploaded file. """
        validated_message_containers = []
        for file_buffer in uploaded_files:
            # file_buffer = file
            file_text = file_buffer.decode(
                "utf-8").splitlines()  # Decode and split lines
            if FileUploader.validate_jsonl(file_text):
                message_container: MessagesContainer = FileUploader.convert_to_messages_container(
                    file_text)
                validated_message_containers.extend(message_container)

        return validated_message_containers

    @staticmethod
    def messages_to_df(messages: MessagesContainer | None = None, default_role: str | None = None) -> pd.DataFrame:
        if messages:
            return pd.DataFrame([
                {"role": msg["role"],
                 "content": msg["content"], "category": ""}
                for msg in messages
            ])
        else:  # default for creating a new datapoint
            return pd.DataFrame({
                "role": [default_role or ""],
                "content": [""],
                "category": [""]
            })
