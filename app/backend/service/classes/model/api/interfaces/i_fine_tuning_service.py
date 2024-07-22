"""
This module defines the interface for the Fine Tuning Service. 
It sets the ground functionality for various fine-tuning providers, managing the process of fine-tuning models, 
including request preparation and response handling.
"""

import io
from datetime import datetime
from abc import ABC, abstractmethod
from app.backend.custom_types.typedicts import MessagesContainer
from app.backend.dtos.response import ComplexDatasetDTO


class IFineTuningService(ABC):
    """
    Interface for the Fine Tuning Service, which interacts with different fine-tuning providers.
    Manages the process of fine-tuning models, including request preparation and response handling.
    """

    @abstractmethod
    def check_and_upload_file(self, file_content: io.BytesIO, file_name: str) -> str:
        """
        Checks if a file with the same name exists on OpenAI, uploads the file if it doesn't, and returns the file ID.

        Args:
            file_content (io.BytesIO): The content of the file to be uploaded.
            file_name (str): The name of the file to be uploaded.

        Returns:
            str: The ID of the uploaded file.
        """
        pass

    @abstractmethod
    def parse_csv_content(self, decoded_content: str) -> dict:
        """
        Parses the CSV content into a dictionary with headers and data rows.

        Args:
            decoded_content (str): The decoded content of the CSV file.

        Returns:
            dict: A dictionary with headers and data rows.
        """
        pass

    @abstractmethod
    def retrieve_training_data(self, file_id: str, as_jsonl: bool = True) -> bytes | str:
        """
        Retrieves the training data file content.

        Args:
            file_id (str): The ID of the file to be retrieved.
            as_jsonl (bool): Flag to determine if the content should be returned as JSONL.

        Returns:
            bytes | str: The content of the file.
        """
        pass

    @abstractmethod
    def retrieve_file_content(self, file_id: str) -> bytes | dict:
        """
        Retrieves the content of the file, decoding it if necessary.

        Args:
            file_id (str): The ID of the file to be retrieved.

        Returns:
            bytes | dict: The content of the file.
        """
        pass

    @abstractmethod
    def combine_result_files(self, result_files_contents: list) -> dict:
        """
        Combines the contents of multiple result files into a single dictionary.

        Args:
            result_files_contents (list): A list of dictionaries containing file contents.

        Returns:
            dict: A combined dictionary with headers and data rows.
        """
        pass

    @abstractmethod
    def fine_tune_model(self, training_file_id: str, chosen_training_model: str, validation_file_id: str | None = None, hyperparameters: dict[str, str] | None = None, seed: int | None = None, suffix: str | None = None) -> dict:
        """
        Initiates the fine-tuning of a model with the provided parameters.

        Args:
            training_file_id (str): The ID of the training file.
            chosen_training_model (str): The base model to be fine-tuned.
            validation_file_id (str | None): The ID of the validation file.
            hyperparameters (dict[str, str] | None): Hyperparameters for fine-tuning.
            seed (int | None): Seed for reproducibility.
            suffix (str | None): Suffix for the fine-tuning job.

        Returns:
            dict: The response from the OpenAI API.
        """
        pass

    @abstractmethod
    def get_fine_funing_job_object(self, fine_tuning_job_id: str | None = None) -> dict:
        """
        Retrieves the fine-tuning job object for the specified job ID.

        Args:
            fine_tuning_job_id (str | None): The ID of the fine-tuning job.

        Returns:
            dict: The fine-tuning job object.
        """
        pass

    @abstractmethod
    def fetch_all_events(self, fine_tuning_job_id: str, limit: int = 20, last_event_id: str = None) -> list[object]:
        """
        Fetches all events related to a fine-tuning job.

        Args:
            fine_tuning_job_id (str): The ID of the fine-tuning job.
            limit (int): The maximum number of events to fetch per request.
            last_event_id (str | None): The ID of the last event fetched.

        Returns:
            list[object]: A list of events related to the fine-tuning job.
        """
        pass

    @abstractmethod
    def fetch_new_events(self, fine_tuning_job_id: str, limit: int = 20, last_event_id: str | None = None) -> tuple[list[object], str]:
        """
        Fetches new events related to a fine-tuning job.

        Args:
            fine_tuning_job_id (str): The ID of the fine-tuning job.
            limit (int): The maximum number of events to fetch per request.
            last_event_id (str | None): The ID of the last event fetched.

        Returns:
            tuple[list[object], str]: A tuple containing a list of new events and the last event ID.
        """
        pass

    @abstractmethod
    def get_fine_tuning_status(self, fine_tuning_job_id: str) -> str | float:
        """
        Retrieves the current status of a fine-tuning job.

        Args:
            fine_tuning_job_id (str): The ID of the fine-tuning job.

        Returns:
            str | float: The current status or progress of the fine-tuning job.
        """
        pass

    @abstractmethod
    def convert_unix_to_local_time(self, unix_timestamp: int) -> datetime:
        """
        Converts a Unix timestamp to local time.

        Args:
            unix_timestamp (int): The Unix timestamp to be converted.

        Returns:
            datetime: The corresponding local time.
        """
        pass

    @abstractmethod
    def get_fine_tuning_job_metrics(self, fine_tuning_job_id: str, step: int | None = None) -> dict:
        """
        Retrieves the metrics of a fine-tuning job.

        Args:
            fine_tuning_job_id (str): The ID of the fine-tuning job.
            step (int | None): The specific step number for which metrics are to be retrieved.

        Returns:
            dict: The metrics of the fine-tuning job.
        """
        pass

    @abstractmethod
    def get_checkpoints(self, fine_tuning_job_id: str) -> list[dict]:
        """
        Retrieves the checkpoints of a fine-tuning job.

        Args:
            fine_tuning_job_id (str): The ID of the fine-tuning job.

        Returns:
            list[dict]: A list of checkpoints related to the fine-tuning job.
        """
        pass

    @abstractmethod
    def cancel_fine_tuning_job(self, fine_tuning_job_id: str) -> dict:
        """
        Cancels a fine-tuning job and deletes associated files.

        Args:
            fine_tuning_job_id (str): The ID of the fine-tuning job to be cancelled.

        Returns:
            dict: The response from the OpenAI API.
        """
        pass

    @abstractmethod
    def delete_checkpoint_models_by_original_fine_tuning_job_id(self, fine_tuning_job_id: str) -> None:
        """
        Deletes checkpoint models associated with a fine-tuning job.

        Args:
            fine_tuning_job_id (str): The ID of the original fine-tuning job.

        Returns:
            None
        """
        pass

    @abstractmethod
    def delete_file(self, file_id: str) -> dict:
        """
        Deletes a file from OpenAI.

        Args:
            file_id (str): The ID of the file to be deleted.

        Returns:
            dict: The response from the OpenAI API.
        """
        pass

    @abstractmethod
    def delete_fine_tuned_model(self, fine_tuned_model_id: str) -> dict:
        """
        Deletes a fine-tuned model.

        Args:
            fine_tuned_model_id (str): The ID of the fine-tuned model to be deleted.

        Returns:
            dict: The response from the OpenAI API.
        """
        pass

    @abstractmethod
    def create_jsonl_string(self, datasets: list[ComplexDatasetDTO]) -> str:
        """
        Creates a JSONL string from a list of datasets.

        Args:
            datasets (list[ComplexDatasetDTO]): A list of datasets.

        Returns:
            str: A JSONL string representing the datasets.
        """
        pass

    @abstractmethod
    def convert_string_to_bytes(self, file_content: str) -> io.BytesIO:
        """
        Converts a string to a BytesIO object.

        Args:
            file_content (str): The string content to be converted.

        Returns:
            io.BytesIO: A BytesIO object containing the converted content.
        """
        pass

    @abstractmethod
    def shorten_uuid(self, uuid: str, length: int = 18) -> str:
        """
        Shortens a UUID to a specified length.

        Args:
            uuid (str): The UUID to be shortened.
            length (int): The desired length of the shortened UUID.

        Returns:
            str: The shortened UUID.
        """
        pass

    @abstractmethod
    def sort_datasets(self, dataset_dtos: list[ComplexDatasetDTO]) -> tuple[list[ComplexDatasetDTO], list[ComplexDatasetDTO]]:
        """
        Sorts datasets into training and test categories.

        Args:
            dataset_dtos (list[ComplexDatasetDTO]): A list of dataset DTOs.

        Returns:
            tuple[list[ComplexDatasetDTO], list[ComplexDatasetDTO]]: A tuple containing lists of training and test datasets.
        """
        pass

    @abstractmethod
    def count_datapoints_in_dataset_list(self, datasets: list[ComplexDatasetDTO]) -> int:
        """
        Counts the number of datapoints in a list of datasets.

        Args:
            datasets (list[ComplexDatasetDTO]): A list of datasets.

        Returns:
            int: The total number of datapoints in the datasets.
        """
        pass

    @abstractmethod
    def generate_model_chat(self, chat: MessagesContainer, model_id: str) -> str:
        """
        Generates a response from a model based on a chat history.

        Args:
            chat (MessagesContainer): The conversation chat history.
            model_id (str): The custom model ID to be used for generating the response.

        Returns:
            str: The assistant's response.
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """
        Fetches the list of available models from OpenAI.

        Returns:
            list[str]: A list of available model IDs.
        """
        pass
