"""
This module handles the fine-tuning process of different fine tuning models. It includes
functionality for applying different fine-tuning strategies and settings.

Classes:
    FineTuner: Handles model fine tuning.
"""


from app.backend.dtos.response import ComplexDatasetDTO, ComplexModelDTO
from app.backend.service.classes.model.api.openai_services import OpenAIService
from app.backend.database.schema import FineTuningModelVersions, FineTuningCompany
from app.backend.service.classes.model.api.interfaces.i_fine_tuning_service import IFineTuningService


class FineTuner:
    """
    Manages the fine-tuning process of different fine tuning models, including (potentially various)
    fine-tuning strategies and settings.
    """

    def __init__(self):
        pass

    @staticmethod
    def find_parent_company(model_string: str) -> str:
        """
        Finds the parent company of a given model string.

        Args:
            model_string (str): The model string to find the parent company for.

        Returns:
            str: The name of the parent company.
        """

        for company in FineTuningModelVersions:
            if model_string in company.value:
                return company.name

    @classmethod
    def select_fine_tuning_class(cls, fine_tuning_company: str, model_dto: ComplexModelDTO, model_dataset_dtos: list[ComplexDatasetDTO]):
        """
        Selects the appropriate fine-tuning class based on the fine-tuning company.

        Args:
            fine_tuning_company (str): The name of the fine-tuning company.
            model_dto (ComplexModelDTO): The model DTO.
            model_dataset_dtos (list[ComplexDatasetDTO]): The list of model dataset DTOs.

        Returns:
            object: The fine-tuning job object.
        """

        fine_tuner: IFineTuningService = None
        if fine_tuning_company == FineTuningCompany.openai.value:
            fine_tuner: OpenAIService = OpenAIService()
            return cls.create_openai_fine_tuning_run(
                fine_tuner, model_dto, model_dataset_dtos)
        if fine_tuning_company == FineTuningCompany.google.value:
            raise Exception("Google fine tuning is not yet implemented")

    # TODO: Sort some fine_tuner functions into separate modeules if they are not vital for the service that provides the api access to encapsulate all vital api service methods into the IFineTuntingService interface, right now, just put all of them into the interface
    @classmethod
    def create_fine_tuning_run(cls, model_dto: ComplexModelDTO, model_dataset_dtos: list[ComplexDatasetDTO], fine_tuning_model: str):
        """
        Creates a fine-tuning run for a given model and dataset DTOs.

        Args:
            model_dto (ComplexModelDTO): The model DTO.
            model_dataset_dtos (list[ComplexDatasetDTO]): The list of model dataset DTOs.
            fine_tuning_model (str): The fine-tuning model to use.

        Returns:
            object: The fine-tuning job object.
        """

        fine_tuning_company: str = cls.find_parent_company(fine_tuning_model)
        return cls.select_fine_tuning_class(
            fine_tuning_company, model_dto, model_dataset_dtos)

    @classmethod
    def create_openai_fine_tuning_run(cls, fine_tuner: IFineTuningService, model_dto: ComplexModelDTO, model_dataset_dtos: list[ComplexDatasetDTO]) -> object:
        """
        Creates and starts a fine-tuning run using OpenAI's fine-tuning service.

        Args:
            fine_tuner (IFineTuningService): The fine-tuning service instance.
            model_dto (ComplexModelDTO): The model DTO.
            model_dataset_dtos (list[ComplexDatasetDTO]): The list of model dataset DTOs.

        Returns:
            object: The fine-tuning job ID.
        """

        try:
            # Fetch available models
            available_models = fine_tuner.get_available_models()

            # Check if the model_used_for_fine_tuning exists
            if model_dto.training_run.fine_tuning_model not in available_models:
                raise ValueError(f"""Model used for fine-tuning '{
                                 model_dto.training_run.fine_tuning_model}' does not exist or is no longer available. Please choose a different model.""")

            # Sort datasets into training and test datasets. Each training dataset can have 0-1 test datasets.
            training_datasets, test_datasets = fine_tuner.sort_datasets(
                model_dataset_dtos)

            # Combine all training datasets into one dataset
            training_dataset_content = fine_tuner.create_jsonl_string(
                training_datasets)
            training_dataset_bytes = fine_tuner.convert_string_to_bytes(
                training_dataset_content)
            # Upload the combined dataset
            training_file_id = fine_tuner.check_and_upload_file(
                training_dataset_bytes, f"training_{model_dto.uuid}.jsonl")

            # Combine all test datasets into one dataset
            validation_file_id = None
            if test_datasets:
                test_dataset_content = fine_tuner.create_jsonl_string(
                    test_datasets)
                test_dataset_bytes = fine_tuner.convert_string_to_bytes(
                    test_dataset_content)
                # Upload the combined dataset
                validation_file_id = fine_tuner.check_and_upload_file(
                    test_dataset_bytes, f"test_{model_dto.uuid}.jsonl")

            # set hyperparameters
            hyperparameters = {
                key: value for key, value in {
                    "n_epochs": model_dto.training_run.epochs,
                    "learning_rate_multiplier": model_dto.training_run.learning_rate_multiplier,
                    "batch_size": model_dto.training_run.batch_size,
                }.items() if value is not None
            }

            # Create and start the fine-tuning job
            suffix = fine_tuner.shorten_uuid(model_dto.uuid)

            fine_tuning_job = fine_tuner.fine_tune_model(
                training_file_id=training_file_id,
                chosen_training_model=model_dto.training_run.fine_tuning_model,
                validation_file_id=validation_file_id,
                hyperparameters=hyperparameters,
                seed=model_dto.training_run.seed,
                suffix=suffix
            )

            return fine_tuning_job.id

            # You can get the error code via "response.error.code / message / param"
        except Exception as e:
            raise Exception(
                f"Error during fine tuning run creation: {e}") from e
