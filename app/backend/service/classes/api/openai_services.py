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
from app.backend.database.schema import Dataset, DatasetCategory, Model
from app.backend.dtos.response import DataPointDTO, TrainingRunDTO
from sqlalchemy.orm import Session
import requests
from app.backend.persistence.interfaces.i_data_manager import IDataManager


class OpenAIService:
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
        files = self.client.files.list(purpose="fine-tune").data
        for file in files:
            if file.filename == file_name:
                # If a file with the same name already exists, delete the existing file to avoid overwriting issues. E.g. What if the user decides to delete the database file. The model ids start again by 1 and overwrite the xisting files.
                self.delete_file(file.id)
        response = self.client.files.create(
            file=(file_name, file_content),
            purpose="fine-tune"
        )
        return response.id

    def fine_tune_model(self, training_file_id, chosen_training_model: str, validation_file_id=None, hyperparameters=None, suffix=None):
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

        response = self.client.fine_tuning.jobs.create(**params)
        return response

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

            # TODO: Add other params to Training Run DTO like train_loss, valid_loss, full_valid_loss, train_mean_token_accuracy, valid_mean_token_accuracy, full_valid_mean_token_accuracy

        # Return the current status if there is no progress information
        return current_training_progress, response.status, progress_message, response.hyperparameters

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
        # Step 1: Cancel the fine-tuning job
        response = self.client.fine_tuning.jobs.cancel(fine_tuning_job_id)

        # Step 2: Get the details of the cancelled fine-tuning job
        job_details = self.client.fine_tuning.jobs.retrieve(fine_tuning_job_id)

        # Extract the file IDs from the job details
        training_file_id = job_details.training_file
        validation_file_id = job_details.validation_file

        # Step 3: Delete the training and validation files
        if training_file_id:
            self.delete_file(training_file_id)
        if validation_file_id:
            self.delete_file(validation_file_id)

        return response

    def delete_file(self, file_id: str):
        try:
            self.client.files.delete(file_id)
            print(f"File {file_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting file {file_id}: {str(e)}")

    def delete_fine_tuning_job(self, fine_tuning_job_id: str):
        response = self.client.models.delete(fine_tuning_job_id)
        return response

    def create_jsonl_string(self, datasets: list[Dataset]):
        jsonl_lines = []
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

    def generate_uuid_suffix(self, length: int = 18) -> str:
        # Generate a UUID
        generated_uuid = str(uuid4())

        # Ensure the length of the generated UUID suffix is at most the specified length
        if length < 1 or length > len(generated_uuid):
            raise ValueError(
                "Length must be between 1 and the length of the UUID string.")

        # Truncate the UUID to the desired length
        return generated_uuid[:length]

    def sort_datasets(self, model: Model) -> tuple[list[Dataset], list[Dataset]]:
        training_datasets: list[Dataset] = []
        test_datasets: list[Dataset] = []
        for dataset in model.training_datasets:
            if dataset.category == DatasetCategory.training:
                training_datasets.append(dataset)
                # Add all test datasets that have test datapoints since test datasets are not mandatory
                if dataset.test_dataset and dataset.test_dataset.datapoints:
                    test_datasets.append(dataset)

        return training_datasets, test_datasets

    def count_datapoints_in_dataset_list(self, datasets: list[Dataset]) -> int:
        count = 0
        for dataset in datasets:
            count += len(dataset.datapoints)

        return count

    def create_fine_tuning_run(self, model: Model, training_run_dto: TrainingRunDTO):

        # Sort datasets into training and test datasets. Each training dataset can have 0-1 test datasets.
        training_datasets, test_datasets = self.sort_datasets(model)

        # Combine all training datasets into one dataset
        training_dataset_content = self.create_jsonl_string(
            training_datasets)
        training_dataset_bytes = self.convert_string_to_bytes(
            training_dataset_content)
        # Upload the combined dataset
        training_file_id = self.check_and_upload_file(
            training_dataset_bytes, f"training_{model.id}.jsonl")

        # Combine all test datasets into one dataset
        validation_file_id = None
        if test_datasets:
            test_dataset_content = self.create_jsonl_string(test_datasets)
            test_dataset_bytes = self.convert_string_to_bytes(
                test_dataset_content)
            # Upload the combined dataset
            validation_file_id = self.check_and_upload_file(
                test_dataset_bytes, f"test_{model.id}.jsonl")

        # Create and start the fine-tuning job
        suffix = self.generate_uuid_suffix()

        # set hyperparameters
        hyperparameters = {
            key: value for key, value in {
                "n_epochs": training_run_dto.epochs,
                "learning_rate_multiplier": training_run_dto.learning_rate_multiplier,
                "batch_size": training_run_dto.batch_size,
                "seed": training_run_dto.seed
            }.items() if value is not None
        }

        fine_tuning_job = self.fine_tune_model(
            training_file_id=training_file_id,
            chosen_training_model=training_run_dto.fine_tuning_model,
            validation_file_id=validation_file_id,
            hyperparameters=hyperparameters,
            suffix=suffix
        )

        return fine_tuning_job.id
