import pytest
from app.backend.persistence.implementations.data_manager import DataManager
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from .unit_tests.database_tests.test_database_setup import setup_test_data, teardown_test_data
from ..util.logger import Logger

logger = Logger(__name__)


@pytest.fixture(scope='session')
def test_manager() -> IDataManager:
    # Create and return a DataManager instance for the test database.
    data_manager: IDataManager = DataManager(
        db_filename='streamlit_app_test.db')
    return data_manager


@pytest.fixture(scope='function')
def db_session(test_manager):

    try:
        setup_test_data(test_manager)
        yield
    except:
        logger.exception("Test database setup failed.")
    finally:
        teardown_test_data(test_manager)
