from typing import Generator
import pytest
from app.backend.persistence.implementations.data_manager import DataManager
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from .unit_tests.database_tests.test_database_setup import setup_test_data, teardown_test_data
from ..util.logger import Logger
from ..mapper.implementations.mappers_facade import MapperFacade

logger = Logger(__name__)


# data_manager and database engine are only created once per session
@pytest.fixture(scope='session')
def test_manager() -> Generator[IDataManager, None, None]:
    # Create and return a DataManager instance for the test database.
    mapper_facade = MapperFacade()
    data_manager: IDataManager = DataManager(mapper=mapper_facade,
                                             db_filename='streamlit_app_test.db')
    yield data_manager

    data_manager.engine.dispose()


# Database tables are setup and cleared for each individual test
@pytest.fixture(scope='function')
def db_setup_manager(test_manager) -> Generator[None, None, None]:

    try:
        setup_test_data(test_manager)
        yield
    except:
        logger.exception("Test database setup failed.")
        pytest.fail("Database setup failed, stopping tests.", pytrace=False)
    finally:
        teardown_test_data(test_manager)
