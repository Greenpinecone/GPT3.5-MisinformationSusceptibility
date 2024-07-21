

import os
import copy
from dotenv import load_dotenv
from google.cloud import translate
from app.backend.custom_types.typedicts import GoogleBTParams
from app.backend.database.schema import AugmentationType
from app.backend.dtos.create_request import CreateDataPointDTO
from app.backend.dtos.response import DataPointDTO
from app.backend.service.classes.data_augmentation.augmentation_methods.interfaces.i_augmentation_methods import IAugmentationMethod


class GoogleBackTranslation(IAugmentationMethod):

    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv()

        # Set the path to the Google authentication key file from the environment variable
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        else:
            raise EnvironmentError(
                "GOOGLE_APPLICATION_CREDENTIALS environment variable not set")

        # Set the project ID from the environment variable
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        if not self.project_id:
            raise EnvironmentError(
                "GOOGLE_CLOUD_PROJECT_ID environment variable not set")

        # Initialize the Google Translate client for v3
        self.translate_client = translate.TranslationServiceClient()
        self.location = 'global'  # You can set this to a specific region if needed

    def translate_text(self, text, target_language):
        try:
            parent = f"projects/{self.project_id}/locations/{self.location}"

            # Google translate reliably recognizes the language provided
            response = self.translate_client.translate_text(
                contents=[text],
                target_language_code=target_language,
                parent=parent
            )

            return response.translations[0].translated_text
        except Exception as e:
            raise Exception(f"Error during translation: {e}") from e

    def augment_datapoints(self, datapoints: list[DataPointDTO], datapoint_indices: list[int], configuration: GoogleBTParams) -> list[CreateDataPointDTO]:
        augmented_datapoints: list[CreateDataPointDTO] = []

        for idx in datapoint_indices:
            original_dp = datapoints[idx]

            # Deep copy the messages to avoid mutating the original
            copied_messages = copy.deepcopy(original_dp.messages)

            # Create a new CreateDataPointDTO
            new_dp = CreateDataPointDTO(
                messages=copied_messages,
                dataset_id=None,
                related_datapoint_ids=None,
                augmentation_type=AugmentationType.BT,
                initial_datapoint_id=original_dp.id
            )

            # Extract and augment messages
            for message in new_dp.messages['messages']:
                content = message['content']
                # Sequentially translate through the specified languages
                for lang in configuration['translate_languages']:
                    content = self.translate_text(content, lang['code'])
                message['content'] = content

            augmented_datapoints.append(new_dp)

        return augmented_datapoints
