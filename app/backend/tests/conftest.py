from typing import Generator
import pytest
from app.backend.persistence.implementations.data_manager import DataManager
from app.backend.persistence.interfaces.i_data_manager import IDataManager
from app.backend.tests.unit_tests.database_tests.test_database_setup import setup_test_data, teardown_test_data
from sqlalchemy.orm import Session
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
