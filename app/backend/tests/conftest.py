from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Generator
import pytest
from app.backend.persistence.implementations.data_manager import DataManager
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.backend.service.interfaces.i_service_manager import IServiceManager
from app.backend.tests.test_database_setup import setup_test_data, teardown_test_data
from sqlalchemy.orm import Session
from app.backend.database.schema import Base
from app.backend.util.logger import Logger
# from app.backend.mapper.implementations.mappers_facade import MapperFacade

logger = Logger(__name__)


# Data manager and database engine are only created once per session
@pytest.fixture(scope='session')
def test_manager() -> Generator[IDataManager, None, None]:
    try:
        # Create and return a DataManager instance for the test database.
        data_manager: IDataManager = DataManager(
            db_filename='streamlit_app_test.db')

        try:
            # Setup the database once per session
            setup_test_data(data_manager)
        except Exception as e:
            pytest.fail(
                "Database data manager setup failed, stopping setup.", pytrace=False)

        yield data_manager

    finally:
        teardown_test_data(data_manager)
        data_manager.engine.dispose()


# Session is created once per session
@pytest.fixture(scope='session')
def db_session(test_manager: IDataManager) -> Generator[Session, None, None]:
    with test_manager.get_session() as session:
        yield session


# Use a transaction and rollback after each test
@pytest.fixture(scope='function')
def db_setup_manager(test_manager: IDataManager, db_session: Session) -> Generator[tuple[IDataManager, Session], None, None]:
    try:
        yield test_manager, db_session
        db_session.rollback()  # Rollback the transaction after each test
    except:
        db_session.rollback()  # Ensure rollback on exception


# IServiceManager is created once per session
@pytest.fixture(scope='session')
def service(test_manager: IDataManager) -> Generator[IServiceManager, None, None]:
    service: IServiceManager = ServiceManagerFacade(data_manager=test_manager)
    yield service


def assert_properties(entity, expected_properties):
    if isinstance(expected_properties, dict):
        for property_name, expected_value in expected_properties.items():
            # Check if the attribute exists in the entity.
            if isinstance(entity, dict):
                if property_name not in entity:
                    print(entity, expected_properties, property_name)
                    pytest.fail(f"""Entity does not contain the property '{
                        property_name}'.""")

                # Get the value or None if not exist.
                actual_value = entity.get(property_name)
            elif isinstance(entity, Base) and not hasattr(entity, property_name):
                print(entity, expected_properties, property_name)
                pytest.fail(f"""Entity does not contain the property '{
                            property_name}'.""")

            else:
                # Get the value or None if not exist.
                actual_value = getattr(entity, property_name, None)

            if isinstance(expected_value, list) and len(expected_value) > 0 and all(isinstance(i, dict) for i in expected_value):
                # Ensure both lists have the same length
                assert len(actual_value) == len(expected_value), f"{
                    property_name} length does not match. Expected {len(expected_value)}, got {len(actual_value)}"

                # Sort by the first key in the dictionaries for comparison
                first_key = next(iter(expected_value[0].keys()))
                sorted_actual = sorted(
                    actual_value, key=lambda x: x[first_key])
                sorted_expected = sorted(
                    expected_value, key=lambda x: x[first_key])

                # Get all keys from the expected_value dictionaries
                expected_keys = set(expected_value[0].keys())

                for expected_dict, actual_dict in zip(sorted_expected, sorted_actual):
                    for key in expected_keys:
                        assert key in actual_dict, f"{property_name} key '{
                            key}' missing in actual value"
                        if isinstance(expected_dict[key], type):
                            if issubclass(expected_dict[key], datetime):
                                assert isinstance(actual_dict[key], expected_dict[key]), f"""{property_name} is not of type {
                                    expected_dict[key].__name__}. Got type {type(actual_dict[key]).__name__}"""
                            else:
                                assert isinstance(actual_dict[key], expected_dict[key]), f"""{property_name} is not of type {
                                    expected_dict[key].__name__}. Got type {type(actual_dict[key]).__name__}"""
                        else:
                            assert expected_dict[key] == actual_dict[key], f"{property_name} key '{
                                key}' does not match. Expected {expected_dict[key]}, got {actual_dict[key]}"
            # If it is a list, the list gets sorted and compared by value to the expected list.
            elif isinstance(expected_value, list):
                if len(actual_value) > 0 and isinstance(actual_value[0], Base):
                    # If it is a list of entities, check if their ids are correct
                    actual_value = [val.id for val in actual_value]

                if len(actual_value) > 0 and isinstance(actual_value[0], dict):
                    # If it is a list of dicts, check if their ids are correct
                    actual_value = [val["id"] for val in actual_value]

                assert sorted(actual_value) == sorted(expected_value), f"""{
                    property_name} does not match. Expected {expected_value}, got {actual_value}"""
            # If a type is expected (e.g: datetime, str, int), the value gets compared by type.
            elif isinstance(expected_value, type):
                if issubclass(expected_value, datetime):
                    assert isinstance(actual_value, expected_value), f"""{property_name} is not of type {
                        expected_value.__name__}. Got type {type(actual_value).__name__}"""
                else:
                    assert isinstance(actual_value, expected_value), f"""{property_name} is not of type {
                        expected_value.__name__}. Got type {type(actual_value).__name__}"""
            # If a lambda function is given, the actual value is checked against the lambda function.
            elif callable(expected_value):
                assert expected_value(actual_value), f"""{
                    property_name} failed custom validation. Failed value: {actual_value}"""
            # If two datetime objects are given, the object that is not parametrized must be created at the same time or later than the parametrized datetime test object.
            elif isinstance(actual_value, datetime) and isinstance(expected_value, datetime):
                assert actual_value >= expected_value, f"""{property_name} does not match. Actual datetime {
                    actual_value} is not less than or equal to expected datetime {expected_value}."""
            elif isinstance(expected_value, dict) and isinstance(actual_value, Base):
                # For relationships that are dictionaries (e.g., one-to-one or many-to-one relationships)
                assert actual_value.id == expected_value["id"], f"""{
                    property_name}.id does not match. Expected {expected_value['id']}, got {actual_value.id}"""
            elif isinstance(expected_value, int) and isinstance(actual_value, Base):
                assert expected_value == actual_value.id, f"""{
                    property_name}.id does not match. Expected {expected_value}, got {actual_value.id}"""
            # If the expected value is a dictionary, recursively call assert_properties
            elif isinstance(expected_value, dict) and isinstance(actual_value, dict):
                assert_properties(actual_value, expected_value)
            # If the expected value is JSON, compare the loaded JSON
            elif isinstance(expected_value, str) and isinstance(actual_value, str):
                assert actual_value == expected_value, f"""{
                    property_name} does not match. Expected {expected_value}, got {actual_value}"""
            # If none of the above conditions holds true, a normal by value comparison is performed.
            else:
                assert actual_value == expected_value, f"""{
                    property_name} does not match. Expected {expected_value}, got {actual_value}"""
    else:
        assert entity == expected_properties, f"""Expected {
            expected_properties}, got {entity}"""
