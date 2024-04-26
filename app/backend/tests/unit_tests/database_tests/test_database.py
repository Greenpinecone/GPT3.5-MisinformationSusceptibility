# import pytest
from dataclasses import asdict
from datetime import datetime
from typing import Generator
import zoneinfo
from app.backend.util.logger import Logger
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from ....dtos.create_request import *
from ....database.schema import *
from ....dtos.response import *
import pytest

logger = Logger(__name__)


def assert_dto_properties(dto, expected_properties):
    for property_name, expected_value in expected_properties.items():
        # Check if the attribute exists in the DTO.
        if not hasattr(dto, property_name):
            print(dto, expected_properties, property_name)
            pytest.fail(f"""DTO does not contain the property '{
                        property_name}'.""")

        # Get the value or None if not exist.
        actual_value = getattr(dto, property_name, None)

        # If it is a list, the list gets sorted and compared by value to the expected list.
        if isinstance(expected_value, list):
            assert sorted(actual_value) == sorted(expected_value), f"""{
                property_name} does not match. Expected {expected_value}, got {actual_value}"""
        # If a type is expected (e.g: datetime, str, int), the value gets compared by type.
        elif isinstance(expected_value, type):
            assert isinstance(actual_value, expected_value), f"""{property_name} is not of type {
                expected_value.__name__}. Got type {type(actual_value).__name__}"""
        # If a lambda function is given, the actual value is checked against the lambda function.
        elif callable(expected_value):
            assert expected_value(actual_value), f"""{
                property_name} failed custom validation. Failed value: {actual_value}"""
        # If two datetime objects are given, the object that is not parametrized must be created at the same time or later than the parametrized datetime test object.
        elif isinstance(actual_value, datetime) and isinstance(expected_value, datetime):
            assert actual_value >= expected_value, f"""{
                property_name} does not match. Actual datetime {actual_value} is not less than or equal to expected datetime {expected_value}."""
        # If none of the above conditions holds true, a normal by value comparison is performed.
        else:
            assert actual_value == expected_value, f"""{
                property_name} does not match. Expected {expected_value}, got {actual_value}"""


successful_test_messages = [{
    "messages": [
        {"role": "user", "content": "What's the weather like today?"},
        {"role": "assistant", "content": "It's sunny and warm outside."},
        {"role": "user", "content": "That sounds lovely. Should I wear shorts?"},
        {"role": "assistant",
         "content": "Shorts would be perfect. Don't forget your sunglasses!"},
        {"role": "user", "content": "Thanks for the advice!"}
    ]
},
    {
    "messages": [
        {"role": "user", "content": "Can you recommend a good book?"},
        {"role": "assistant",
         "content": "Sure, do you prefer fiction or non-fiction?"},
        {"role": "user", "content": "I love fiction."},
        {"role": "assistant",
         "content": "How about 'The Night Circus' by Erin Morgenstern? It's magical."},
        {"role": "user", "content": "Sounds interesting. I'll check it out. Thanks!"}
    ]
},
    {
    "messages": [
        {"role": "user", "content": "How do I reset my password?"},
        {"role": "assistant",
         "content": "You can reset your password by going to the settings page."},
        {"role": "user", "content": "Thanks, that was helpful!"}
    ]
},
    {
    "messages": [
        {"role": "user",
         "content": "What's the weather like in New York today?"},
        {"role": "assistant",
         "content": "The weather in New York is sunny with a high of 75 degrees."},
        {"role": "user", "content": "Should I take an umbrella?"},
        {"role": "assistant",
         "content": "It's sunny, so you won't need an umbrella today."}
    ]
},
    {
    "messages": [
        {"role": "user", "content": "Can you recommend a good sci-fi book?"},
        {"role": "assistant",
         "content": "I would recommend 'Dune' by Frank Herbert. It's a great read!"}
    ]
}]

failure_test_messages = [{
    "messages": [{"role": "", "content": "It's me!"}]
},
    {
    "messages": [{"role": "system", "content": ""}]
},
    {
    "messages": [{"role": "", "content": ""}]
},
    {
    "messages": [{}]
},
    {
    "messages": []
}]


class TestDatabaseOperations:

    # ************************************************************************************************
    # GET DATABASE FUNCTIONS
    # ************************************************************************************************

    @pytest.mark.parametrize("project_id, expected_properties", [
        (1, {
            'id': 1,
            'project_name': "Project Alpha",
            'description': "Alpha Project Description",
            'model_ids': [1, 3],
            'dataset_ids': [1, 2],
            'created_at': datetime
        }),
        (2, {
            'id': 2,
            'project_name': "Project Beta",
            'description': "Beta Project Description",
            'model_ids': [2, 4],
            'dataset_ids': [1, 2],
            'created_at': datetime
        })
    ])
    def test_get_project_by_id_and_convert_to_dto(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, project_id: int, expected_properties: dict):
        # Fetch projects
        project_dto = test_manager.get_project_by_id(project_id)[0]

        # Test assertions using the assert_dto_properties function
        assert_dto_properties(project_dto, expected_properties)

    @pytest.mark.parametrize("dataset_id, expected_properties", [
        (1, {
            'id': 1,
            'dataset_name': "Dataset Alpha",
            'augmented': False,
            'category': DatasetCategory.training,
            'project_ids': [1, 2],
            'initial_dataset_id': None,
            'test_dataset_id': None,
            'created_at': datetime
        }),
        (2, {
            'id': 2,
            'dataset_name': "Dataset Beta",
            'augmented': True,
            'category': DatasetCategory.test,
            'project_ids': [1, 2],
            'initial_dataset_id': 1,
            'test_dataset_id': 1,
            'created_at': datetime
        })
    ])
    def test_get_dataset_by_id_and_convert_to_dto(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, dataset_id: int, expected_properties: dict):
        # Fetch the Dataset DTO using the ID from the parameter
        dataset_dto: DatasetDTO = test_manager.get_dataset_by_id(dataset_id)[0]

        # Assert properties using the assert_dto_properties function
        assert_dto_properties(dataset_dto, expected_properties)

    @pytest.mark.parametrize("datapoint_id, expected_properties", [
        (1, {
            'id': 1,
            'dataset_id': 1,
            'coherence_score': 8,
            'relevance_score': 9,
            'semantic_similarity_score': 0.95,
            'augmentation_type': None,
            'category': "category_alpha",
            'initial_datapoint_id': None,
            'created_at': datetime,
            'messages': successful_test_messages[0]
        }),
        (2, {
            'id': 2,
            'dataset_id': 2,
            'coherence_score': 7,
            'relevance_score': 8,
            'augmentation_type': AugmentationType.EDA,
            'category': "category_beta",
            'initial_datapoint_id': 1,
            'created_at': datetime,
            'messages': successful_test_messages[1]
        })
    ])
    def test_get_datapoint_by_id_and_convert_to_dto(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, datapoint_id: int, expected_properties: dict):
        # Fetch the DataPoint DTO using the ID from the parameter
        datapoint_dto: DataPointDTO = test_manager.get_datapoint_by_id(datapoint_id)[
            0]

        # Assert properties using the assert_dto_properties function
        assert_dto_properties(datapoint_dto, expected_properties)

    @pytest.mark.parametrize("model_id, expected_properties", [
        (1, {
            'id': 1,
            'model_name': "Model Alpha",
            'version': 1,
            'project_id': 1,
            'dataset_ids': [1, 2],
            'parent_model_id': None,
            'training_run_id': 1,
            'created_at': datetime
        }),
        (2, {
            'id': 2,
            'model_name': "Model Beta",
            'version': 1,
            'project_id': 2,
            'dataset_ids': [1, 2],
            'parent_model_id': 1,
            'training_run_id': 2,
            'created_at': datetime
        })
    ])
    def test_get_model_by_id_and_convert_to_dto(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, model_id: int, expected_properties: dict):
        # Fetch the model DTO using the ID from the parameter
        model_dto: ModelDTO = test_manager.get_model_by_id(model_id)[0]

        # Assert properties using the assert_dto_properties function
        assert_dto_properties(model_dto, expected_properties)

    @pytest.mark.parametrize("model_eval_id, expected_properties", [
        (1, {
            'id': 1,
            'model_id': 1,
            'datapoint_id': 1,
            'evaluation_type': EvaluationType.TP,
            'helpful_score': 10,
            'honest_score': 9,
            'harmless_score': 8,
            'created_at': datetime
        }),
        (2, {
            'id': 2,
            'model_id': 2,
            'datapoint_id': 2,
            'evaluation_type': EvaluationType.FN,
            'helpful_score': 7,
            'honest_score': 8,
            'harmless_score': 9,
            'created_at': datetime
        })
    ])
    def test_get_model_evaluation_by_id_and_convert_to_dto(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, model_eval_id: int, expected_properties: dict):
        # Fetch the model evaluation DTO using the ID from the parameter
        model_eval_dto: ModelEvaluationDTO = test_manager.get_model_evaluation_by_id(
            model_eval_id)[0]

        # Assert properties using the assert_dto_properties function
        assert_dto_properties(model_eval_dto, expected_properties)

    @pytest.mark.parametrize("training_run_id, expected_properties", [
        (1, {
            'id': 1,
            'model_id': 1,
            'epochs': 10,
            'learning_rate_multiplier': 0.01,
            'batch_size': 64,
            'created_at': datetime
        }),
        (2, {
            'id': 2,
            'model_id': 2,
            'epochs': 20,
            'learning_rate_multiplier': 0.02,
            'batch_size': 128,
            'created_at': datetime
        })
    ])
    def test_get_training_run_by_id_and_convert_to_dto(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, training_run_id: int, expected_properties: dict):
        # Fetch the training run DTO using the ID from the parameter
        training_run_dto: TrainingRunDTO = test_manager.get_training_run_by_id(
            training_run_id)[0]

        # Assert properties using the assert_dto_properties function
        assert_dto_properties(training_run_dto, expected_properties)

    # ************************************************************************************************
        # SAVE DATABASE FUNCTIONS
    # ************************************************************************************************

    @pytest.mark.parametrize("project_inputs, expected_outputs", [
        ([
            CreateProjectDTO(project_name="Project Gamma", description="Gamma Project Description", model_ids=[
                             1], dataset_ids=[1, 2]),
            CreateProjectDTO(project_name="Project Delta",
                             description="Delta Project Description", model_ids=[2], dataset_ids=[1])
        ], [
            ProjectDTO(id=3, project_name="Project Gamma", description="Gamma Project Description", model_ids=[
                       1], dataset_ids=[1, 2], created_at=datetime.now().astimezone()),
            ProjectDTO(id=4, project_name="Project Delta", description="Delta Project Description", model_ids=[
                       2], dataset_ids=[1], created_at=datetime.now().astimezone())
        ]),
        ([
            CreateProjectDTO(project_name="Project Epsilon",
                             description="Epsilon Project Description", model_ids=[2], dataset_ids=[2])
        ], [
            ProjectDTO(id=3, project_name="Project Epsilon", description="Epsilon Project Description", model_ids=[
                       2], dataset_ids=[2], created_at=datetime.now().astimezone())
        ])
    ])
    def test_save_projects(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, project_inputs: list[CreateProjectDTO], expected_outputs: list[ProjectDTO]):
        # Save projects using the provided function
        saved_project_dtos = test_manager.save_projects(project_inputs)
        assert len(saved_project_dtos) == len(
            project_inputs), "Project saving did not return the expected number of projects."

        # Fetch the saved projects and compare each one
        for saved_project_dto, expected_output in zip(saved_project_dtos, expected_outputs):
            expected_dict = asdict(expected_output)
            # Remove 'created_at' for comparison if not critical
            # expected_dict.pop('created_at', None)
            # saved_dict = asdict(saved_project_dto)
            # saved_dict.pop('created_at', None)

            # Assert properties
            assert_dto_properties(saved_project_dto, expected_dict)

    @pytest.mark.parametrize("dataset_inputs, expected_outputs", [
        ([
            CreateDatasetDTO(dataset_name="Dataset Gamma", augmented=False, category=DatasetCategory.training, project_ids=[
                             1], datapoint_ids=[1], initial_dataset_id=None, test_dataset_id=None),
            CreateDatasetDTO(dataset_name="Dataset Delta", augmented=True, category=DatasetCategory.test, project_ids=[
                             2], datapoint_ids=[2], initial_dataset_id=1, test_dataset_id=1)
        ], [
            DatasetDTO(id=3, dataset_name="Dataset Gamma", augmented=False, category=DatasetCategory.training, created_at=datetime.now(
            ).astimezone(), project_ids=[1], datapoint_ids=[1], initial_dataset_id=None, test_dataset_id=None),
            DatasetDTO(id=4, dataset_name="Dataset Delta", augmented=True, category=DatasetCategory.test, created_at=datetime.now(
            ).astimezone(), project_ids=[2], datapoint_ids=[2], initial_dataset_id=1, test_dataset_id=1)
        ]),
        ([
            CreateDatasetDTO(dataset_name="Dataset Epsilon", augmented=False, category=DatasetCategory.training, project_ids=[
                             1, 2], datapoint_ids=[1, 2], initial_dataset_id=None, test_dataset_id=None)
        ], [
            DatasetDTO(id=3, dataset_name="Dataset Epsilon", augmented=False, category=DatasetCategory.training, created_at=datetime.now(
            ).astimezone(), project_ids=[1, 2], datapoint_ids=[1, 2], initial_dataset_id=None, test_dataset_id=None)
        ])
    ])
    def test_save_datasets(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, dataset_inputs: list[CreateDatasetDTO], expected_outputs: list[DatasetDTO]):
        # Save datasets
        saved_dataset_dtos = test_manager.save_datasets(dataset_inputs)
        assert len(saved_dataset_dtos) == len(
            dataset_inputs), "Dataset saving did not return the expected number of datasets."

        # Fetch and compare each saved dataset
        for saved_dataset_dto, expected_output in zip(saved_dataset_dtos, expected_outputs):
            expected_dict = asdict(expected_output)
            # Optional: Remove 'created_at' from comparison if the exact timestamp isn't critical
            # expected_dict.pop('created_at', None)
            # saved_dict = asdict(saved_dataset_dto)
            # saved_dict.pop('created_at', None)

            # Assert properties
            assert_dto_properties(saved_dataset_dto, expected_dict)

    @pytest.mark.parametrize("datapoint_inputs, expected_outputs", [
        # Test with two datapoints
        ([
            CreateDataPointDTO(
                dataset_id=1,
                coherence_score=10,
                relevance_score=9,
                semantic_similarity_score=0.95,
                augmentation_type=None,
                messages=successful_test_messages[3],
                category="Category Gamma",
                initial_datapoint_id=1
            ),
            CreateDataPointDTO(
                dataset_id=2,
                coherence_score=8,
                relevance_score=7,
                semantic_similarity_score=0.90,
                augmentation_type=AugmentationType.EDA,
                messages=successful_test_messages[4],
                category="Category Delta",
                initial_datapoint_id=2
            )
        ],
            [
            DataPointDTO(
                id=3,
                dataset_id=1,
                coherence_score=10,
                relevance_score=9,
                semantic_similarity_score=0.95,
                augmentation_type=None,
                messages=successful_test_messages[3],
                category="Category Gamma",
                created_at=datetime.now().astimezone(),
                initial_datapoint_id=1
            ),
            DataPointDTO(
                id=4,
                dataset_id=2,
                coherence_score=8,
                relevance_score=7,
                semantic_similarity_score=0.90,
                augmentation_type=AugmentationType.EDA,
                messages=successful_test_messages[4],
                category="Category Delta",
                created_at=datetime.now().astimezone(),
                initial_datapoint_id=2
            )
        ]),
        # Test with one datapoint
        ([
            CreateDataPointDTO(
                dataset_id=1,
                coherence_score=5,
                relevance_score=5,
                semantic_similarity_score=0.85,
                augmentation_type=AugmentationType.BT,
                messages=successful_test_messages[4],
                category="Category Epsilon",
                initial_datapoint_id=None
            )
        ],
            [
            DataPointDTO(
                id=3,
                dataset_id=1,
                coherence_score=5,
                relevance_score=5,
                semantic_similarity_score=0.85,
                augmentation_type=AugmentationType.BT,
                messages=successful_test_messages[4],
                category="Category Epsilon",
                created_at=datetime.now().astimezone(),
                initial_datapoint_id=None
            )
        ])
    ])
    def test_save_datapoints(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager,
                             datapoint_inputs: list[CreateDataPointDTO], expected_outputs: list[DataPointDTO]):
        # Save datapoints
        saved_datapoint_dtos = test_manager.save_datapoints(datapoint_inputs)
        assert len(saved_datapoint_dtos) == len(
            datapoint_inputs), "Datapoints saving did not return the expected number of datapoints."

        # Fetch and compare each saved datapoint
        for saved_datapoint_dto, expected_output in zip(saved_datapoint_dtos, expected_outputs):
            expected_dict = asdict(expected_output)
            # Optional: Remove 'created_at' from comparison if the exact timestamp isn't critical
            # expected_dict.pop('created_at', None)
            # saved_dict = asdict(saved_datapoint_dto)
            # saved_dict.pop('created_at', None)

            # Assert properties, convert to dict for easier comparison
            assert_dto_properties(saved_datapoint_dto, expected_dict)

    @pytest.mark.parametrize("model_inputs, expected_outputs", [
        # First test case with two models
        ([
            CreateModelDTO(model_name="Model Epsilon", version=1,
                           project_id=1, dataset_ids=[1, 2], parent_model_id=None, training_run_id=None),
            CreateModelDTO(model_name="Model Zeta", version=1, project_id=2, dataset_ids=[
                1], parent_model_id=1, training_run_id=1)
        ],
            [
            ModelDTO(id=5, model_name="Model Epsilon", version=1, created_at=datetime.now(
            ).astimezone(), project_id=1, dataset_ids=[1, 2], parent_model_id=None, training_run_id=None),
            ModelDTO(id=6, model_name="Model Zeta", version=1, created_at=datetime.now(
            ).astimezone(), project_id=2, dataset_ids=[1], parent_model_id=1, training_run_id=1)
        ]),
        # Second test case with one model
        ([
            CreateModelDTO(model_name="Model Eta", version=1,
                           project_id=1, dataset_ids=[1, 2], parent_model_id=1, training_run_id=None)
        ],
            [
            ModelDTO(id=5, model_name="Model Eta", version=1, created_at=datetime.now(
            ).astimezone(), project_id=1, dataset_ids=[1, 2], parent_model_id=1, training_run_id=None)
        ])
    ])
    def test_save_models(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, model_inputs: list[CreateModelDTO], expected_outputs: list[ModelDTO]):
        # Save models
        saved_model_dtos = test_manager.save_models(model_inputs)
        assert len(saved_model_dtos) == len(
            model_inputs), "Model saving did not return the expected number of models."

        # Fetch and assert each saved model
        for saved_model_dto, expected_output in zip(saved_model_dtos, expected_outputs):
            expected_dict = asdict(expected_output)
            # Optional: Remove 'created_at' from comparison if the exact timestamp isn't critical
            # expected_dict.pop('created_at', None)
            # saved_dict = asdict(saved_model_dto)
            # saved_dict.pop('created_at', None)

            assert_dto_properties(saved_model_dto, expected_dict)

    @pytest.mark.parametrize("evaluation_inputs, expected_outputs", [
        # Test case with two evaluations
        ([
            CreateModelEvaluationDTO(model_id=3, datapoint_id=1, evaluation_type=EvaluationType.FN,
                                     helpful_score=10, honest_score=9, harmless_score=8),
            CreateModelEvaluationDTO(model_id=4, datapoint_id=2, evaluation_type=EvaluationType.TP,
                                     helpful_score=7, honest_score=6, harmless_score=5)
        ],
            [
            ModelEvaluationDTO(id=3, model_id=3, datapoint_id=1, evaluation_type=EvaluationType.FN, helpful_score=10,
                               honest_score=9, harmless_score=8, created_at=datetime.now().astimezone()),
            ModelEvaluationDTO(id=4, model_id=4, datapoint_id=2, evaluation_type=EvaluationType.TP, helpful_score=7,
                               honest_score=6, harmless_score=5, created_at=datetime.now().astimezone())
        ]),
        # Test case with one evaluation
        ([
            CreateModelEvaluationDTO(model_id=3, datapoint_id=2, evaluation_type=EvaluationType.FP,
                                     helpful_score=5, honest_score=5, harmless_score=5)
        ],
            [
            ModelEvaluationDTO(id=3, model_id=3, datapoint_id=2, evaluation_type=EvaluationType.FP, helpful_score=5,
                               honest_score=5, harmless_score=5, created_at=datetime.now().astimezone())
        ])
    ])
    def test_save_model_evaluations(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, evaluation_inputs: list[CreateModelEvaluationDTO], expected_outputs: list[ModelEvaluationDTO]):
        # Save model evaluations
        saved_evaluation_dtos = test_manager.save_model_evaluations(
            evaluation_inputs)
        assert len(saved_evaluation_dtos) == len(
            evaluation_inputs), "Model evaluation saving did not return the expected number of evaluations."

        # Fetch and compare each saved model evaluation
        for saved_evaluation_dto, expected_output in zip(saved_evaluation_dtos, expected_outputs):
            expected_dict = asdict(expected_output)
            # Optional: Remove 'created_at' from comparison if the exact timestamp isn't critical
            # expected_dict.pop('created_at', None)
            # saved_dict = asdict(saved_evaluation_dto)
            # saved_dict.pop('created_at', None)

            assert_dto_properties(saved_evaluation_dto, expected_dict)

    @pytest.mark.parametrize("run_inputs, expected_outputs", [
        # Test case with two training runs
        ([
            CreateTrainingRunDTO(model_id=3, epochs=10,
                             learning_rate_multiplier=0.01, batch_size=64),
            CreateTrainingRunDTO(model_id=4, epochs=20,
                             learning_rate_multiplier=0.02, batch_size=128)
        ], [
            TrainingRunDTO(id=3, model_id=3, epochs=10, learning_rate_multiplier=0.01,
                           batch_size=64, created_at=datetime.now().astimezone()),
            TrainingRunDTO(id=4, model_id=4, epochs=20, learning_rate_multiplier=0.02,
                           batch_size=128, created_at=datetime.now().astimezone())
        ]),
        # Test case with one training run
        ([
            CreateTrainingRunDTO(model_id=3, epochs=15,
                                 learning_rate_multiplier=0.015, batch_size=100)
        ], [
            TrainingRunDTO(id=3, model_id=3, epochs=15, learning_rate_multiplier=0.015,
                           batch_size=100, created_at=datetime.now().astimezone())
        ])
    ])
    def test_save_training_runs(self, db_setup_manager: Generator[None, None, None], test_manager: IDataManager, run_inputs: list[CreateTrainingRunDTO], expected_outputs: list[TrainingRunDTO]):
        # Save training runs using the provided function
        saved_run_dtos = test_manager.save_training_runs(run_inputs)
        assert len(saved_run_dtos) == len(
            run_inputs), "Training run saving did not return the expected number of training runs."

        # Fetch and compare each saved training run
        for saved_run_dto, expected_output in zip(saved_run_dtos, expected_outputs):
            expected_dict = asdict(expected_output)
            # Optional: Remove 'created_at' from comparison if the exact timestamp isn't critical
            # expected_dict.pop('created_at', None)
            # saved_dict = asdict(saved_run_dto)
            # saved_dict.pop('created_at', None)

            # Assert properties
            assert_dto_properties(saved_run_dto, expected_dict)
