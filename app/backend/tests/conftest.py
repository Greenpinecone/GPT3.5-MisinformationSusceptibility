import pytest
from app.backend.persistence.implementations.data_manager import DataManager
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from .unit_tests.database_tests.test_database_setup import setup_test_data, teardown_test_data


@pytest.fixture(scope='session')
def test_manager() -> IDataManager:
    # Create and return a DataManager instance for the test database.
    data_manager: IDataManager = DataManager(
        db_filename='streamlit_app_test.db')
    return data_manager


@pytest.fixture(scope='function')
def db_session(test_manager):

    setup_test_data(test_manager)

    yield

    teardown_test_data(test_manager)
