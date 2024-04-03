# import pytest
from datetime import datetime
from app.backend.util.logger import Logger
from app.backend.persistence.interfaces.i_data_manager import IDataManager

logger = Logger(__name__)


class TestDatabaseOperations:

    def test_project_creation(self, db_session: None, test_manager: IDataManager):
        # Example of creating and testing a project
        # project_data = {"project_name": "Test Project",
        #                 "timestamp": datetime.now()}
        # created_project = test_manager.save_projects(project_data)
        # assert created_project[0].project_name == "Test Project"
        # More assertions or operations
        print("RUNNING FIRST TEST", __name__)
