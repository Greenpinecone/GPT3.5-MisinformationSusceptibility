import pytest
from app.backend.persistence.daos.data_manager import DataManager
from database.schema import Base
from backend.service.classes.util.logger import Logger

"""
@pytest.fixture(scope='function')
def db_session():
    logger = Logger()
    # Create a DataManager instance for test database
    test_manager = DataManager(
        logger=logger, db_filename='streamlit_app_test.db')

    # Setup the database schema
    Base.metadata.create_all(test_manager.engine)

    # Setup test data
    setup_test_data(test_manager.Session())

    yield test_manager.Session()

    # Teardown test data and drop all tables
    Base.metadata.drop_all(test_manager.engine)
    test_manager.engine.dispose()


class TestDatabaseOperations:

    def test_project_creation(self, test_data_manager):
        # Example of creating and testing a project
        project_data = {"project_name": "Test Project",
                        "timestamp": datetime.datetime.now()}
        created_project = test_data_manager.save_project(project_data)
        assert created_project[0].project_name == "Test Project"
        # More assertions or operations

"""
