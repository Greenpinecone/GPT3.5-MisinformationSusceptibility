"""
Provides a service class for interacting with OpenAI's API, specifically for
fine-tuning the GPT-3.5-Turbo model. It handles API requests and responses,
streamlining the model's fine-tuning process.

Classes:
    OpenAIService: Manages the API interactions with OpenAI, including fine-tuning and data retrieval.
"""

import os
import io
from uuid import uuid4
from openai import OpenAI
import json
from app.backend.custom_types.typedicts import Message, MessagesContainer
from app.backend.database.schema import Dataset, DatasetCategory, Model
from app.backend.dtos.response import ComplexDatasetDTO, ComplexModelDTO, DataPointDTO, TrainingRunDTO
from sqlalchemy.orm import Session
import requests
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from app.backend.service.classes.model.api.interfaces.i_fine_tuning_service import IFineTuningService


class OpenAIService(IFineTuningService):
    """
    Service class for interacting with OpenAI's API. Manages the process of
    fine-tuning GPT-3.5-Turbo, including request preparation and response handling.

    Attributes:
        api_key (str): API access key for openAI's API.
    """

    def __init__(self, api_key: str = "", organization: str = ""):
        self.organization = organization or os.getenv('OPENAI_ORGANIZATION')
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(
            organization=self.organization, api_key=self.api_key)

    def check_and_upload_file(self, file_content: io.BytesIO, file_name: str):
        try:
            files = self.client.files.list(purpose="fine-tune").data
            for file in files:
                if file.filename == file_name:
                    return file.id
            response = self.client.files.create(
                file=(file_name, file_content),
                purpose="fine-tune"
            )
            return response.id
        except Exception as e:
            raise Exception(f"Error while uploading files: {e}")

    def fine_tune_model(self, training_file_id: str, chosen_training_model: str, validation_file_id: str | None = None, hyperparameters: dict[str, str] | None = None, seed: int | None = None, suffix: str | None = None):
        try:
            params = {
                "training_file": training_file_id,
                "model": chosen_training_model,
            }
            if validation_file_id:
                params["validation_file"] = validation_file_id
            if hyperparameters:
                params["hyperparameters"] = hyperparameters
            if suffix:
                params["suffix"] = suffix
            if seed:
                params["seed"] = seed

            response = self.client.fine_tuning.jobs.create(**params)
            return response
        except Exception as e:
            raise Exception(f"Error creating fine tuning job: {e}")

    def get_fine_tuning_status(self, fine_tuning_job_id: str) -> str | float:
        response = self.client.fine_tuning.jobs.retrieve(fine_tuning_job_id)

        # else status == "running"
        events = self.client.fine_tuning.jobs.list_events(
            fine_tuning_job_id=fine_tuning_job_id, limit=1)

        progress_message = None
        current_training_progress = None
        if events.data:
            # Get the last event
            last_event = events.data[0]  # Use the latest event

            # Ensure model_extra["data"] is a dictionary
            data = last_event.model_extra.get("data", {})
            if isinstance(data, dict):
                # Get current steps
                current_step = data.get("step", None)
                total_steps = data.get("total_steps", None)

                if current_step is not None and total_steps is not None:

                    current_training_progress = (current_step / total_steps)

            progress_message = last_event.message

        # TODO: Return other params + metrics file later for stats:
            """  "train_loss": 0.478,
    "train_mean_token_accuracy": 0.924,
    "valid_loss": 10.112,
    "valid_mean_token_accuracy": 0.145,
    "full_valid_loss": 0.567,
    "full_valid_mean_token_accuracy": 0.944"""

        # response.seed, response.fine_tuned_model, response.trained_tokens
        # response.result_files -> [] -> [0] -> metrics for the graph?

        # Return the current status if there is no progress information
        return current_training_progress, response.status, progress_message, response.hyperparameters, response.seed, response.fine_tuned_model

    def get_checkpoints(self, fine_tuning_job_id):
        url = f"""https://api.openai.com/v1/fine_tuning/jobs/{
            fine_tuning_job_id}/checkpoints"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response = response.json()
        return response.get("data")

    def cancel_fine_tuning_job(self, fine_tuning_job_id: str):
        try:
            # Step 1: Get the details of the cancelled fine-tuning job
            job_details = self.client.fine_tuning.jobs.retrieve(
                fine_tuning_job_id)

            # Extract the file IDs from the job details
            training_file_id = job_details.training_file
            validation_file_id = job_details.validation_file

            response = None
            # The job itself cannot be deleted from openai only cancelled and the model can be deleted if it exists.
            # Delete the current fine tuning job if the job has already finished,
            if job_details.status not in ['succeeded', 'failed', 'cancelled']:
                # Proceed to cancel the job if it is still running
                response = self.client.fine_tuning.jobs.cancel(
                    fine_tuning_job_id)
            else:
                # Delete the fine tuned model if it already exists
                if job_details.fine_tuned_model:
                    response = self.delete_fine_tuned_model(
                        job_details.fine_tuned_model)

             # Step 3: Delete the training and validation files
            if training_file_id:
                self.delete_file(training_file_id)
            if validation_file_id:
                self.delete_file(validation_file_id)

            return response

        except Exception as e:
            raise Exception(
                f"Fine tuning job could not be cancelled properly: {e}") from e

    def delete_file(self, file_id: str):
        try:
            response = self.client.files.delete(file_id)
            return response
        except Exception as e:
            # Files have already been deleted - Can happen due to streamlit reload functionality if an error occurs the first time
            if e.status_code == 404:
                pass
            else:
                raise Exception(f"Error deleting file {file_id}: {str(e)}")

    def delete_fine_tuned_model(self, fine_tuned_model_id: str):
        try:
            response = self.client.models.delete(fine_tuned_model_id)
            return response
        except Exception as e:
            # Model has already been deleted
            if e.status_code == 404:
                pass
            else:
                raise Exception(
                    f"Fine tuned model could not be deleted properly: {e}")

    def create_jsonl_string(self, datasets: list[ComplexDatasetDTO]):
        jsonl_lines: list[str] = []
        for dataset in datasets:
            for datapoint in dataset.datapoints:
                messages = datapoint.messages.get('messages')
                if messages:
                    jsonl_lines.append(json.dumps({"messages": messages}))
        jsonl_string = "\n".join(jsonl_lines)
        return jsonl_string

    def convert_string_to_bytes(self, file_content: str) -> io.BytesIO:
        # Convert file_content to bytes and create a BytesIO object
        return io.BytesIO(file_content.encode('utf-8'))

    def shorten_uuid(self, uuid: str, length: int = 18) -> str:

        # Use shortuuid to generate a shorter unique ID
        short_id = uuid[:length]

        return short_id

    def sort_datasets(self, dataset_dtos: list[ComplexDatasetDTO]) -> tuple[list[ComplexDatasetDTO], list[ComplexDatasetDTO]]:
        all_training_datasets: list[ComplexDatasetDTO] = []
        all_test_datasets: list[ComplexDatasetDTO] = []
        seen_test_ids: set[int] = set()

        for dataset in dataset_dtos:
            # No duplicates here
            if dataset.category == DatasetCategory.training:
                all_training_datasets.append(dataset)
                # Add all test datasets that have test datapoints since test datasets are not mandatory
                # For the same model, all datasets reference the same test dataset
                if dataset.test_dataset and dataset.test_dataset.datapoints:
                    if dataset.test_dataset.id not in seen_test_ids:
                        all_test_datasets.append(dataset.test_dataset)
                        seen_test_ids.add(dataset.test_dataset.id)

        return all_training_datasets, all_test_datasets

    def count_datapoints_in_dataset_list(self, datasets: list[ComplexDatasetDTO]) -> int:
        count = 0
        for dataset in datasets:
            count += len(dataset.datapoints)

        return count

    def generate_model_chat(self, chat: MessagesContainer, model_id: str) -> str:
        """
        This function takes a chat history and a model ID, finds the last empty assistant message,
        gets a response for it from the OpenAI API, appends the response to the chat, and returns
        the full chat history.

        Parameters:
            chat (list[dict]): The conversation chat history.
            model_id (str): The custom model ID to be used for generating the response.

        Returns:
            list[dict]: The updated chat history with the new response.
        """
        try:

            # Generate a response for the empty assistant message
            response = self.client.chat.completions.create(
                model=model_id,
                messages=chat
            )

            # Get the content of the response
            answer = response.choices[0].message.content

            # Append the response to the chat history
            return answer

        except Exception as e:
            raise Exception(f"Error while answering the last message: {e}")
