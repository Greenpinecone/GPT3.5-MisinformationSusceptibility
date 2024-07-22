"""
This module provides services for managing datapoints.

Classes:
    DataPointService: Provides methods for manipulating datapoint objects.
"""


from app.frontend.mappers.frontend_mappers import DataPointDTOToUpdateDataPointDTO
from app.backend.dtos.response import DataPointDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade


class DataPointService:
    """
    Provides methods for manipulating datapoint objects.

    This service offers various static methods to handle operations such as adding or removing a datapoint from a related list, checking for the presence of a datapoint, replacing or removing a datapoint in a list, and updating datapoints.

    Methods:
        add_or_remove: Add or remove a datapoint from the related datapoints list.
        is_present: Check if a datapoint exists in a list.
        replace_datapoint_in_list: Replace a datapoint in the list if it exists, or add it if it does not.
        remove_datapoint_from_list: Remove a datapoint from the list by its ID if it exists.
        find_datapoint_in_list: Find a datapoint in the list by its ID.
        update_datapoints: Update a list of datapoints using the service manager.
    """

    @staticmethod
    def add_or_remove(current_test_datapoint: DataPointDTO, datapoint: DataPointDTO) -> None:
        """
        Add or remove a datapoint from the related datapoints list.

        Args:
            current_test_datapoint (DataPointDTO): The current test datapoint to modify.
            datapoint (DataPointDTO): The datapoint to add or remove.
        """

        if any(dp.id == datapoint.id for dp in current_test_datapoint.related_datapoints):
            current_test_datapoint.related_datapoints = [
                dp for dp in current_test_datapoint.related_datapoints if dp.id != datapoint.id
            ]
        else:
            current_test_datapoint.related_datapoints.append(datapoint)

    @staticmethod
    def is_present(datapoint_list: list[DataPointDTO], datapoint: DataPointDTO) -> None:
        """
        Check if a datapoint exists in a list.

        Args:
            datapoint_list (list[DataPointDTO]): The list of datapoints.
            datapoint (DataPointDTO): The datapoint to check for presence.

        Returns:
            bool: True if the datapoint is present, False otherwise.
        """

        if any(dp.id == datapoint.id for dp in datapoint_list):
            return True
        else:
            return False

    def replace_datapoint_in_list(datapoint: DataPointDTO, datapoint_list: list[DataPointDTO]) -> list[DataPointDTO]:
        """
        Replace a datapoint in the list if it exists, or add it if it does not.

        Args:
            datapoint (DataPointDTO): The datapoint to replace or add.
            datapoint_list (list[DataPointDTO]): The list of datapoints.

        Returns:
            list[DataPointDTO]: The updated list of datapoints.
        """

        for i, dp in enumerate(datapoint_list):
            if dp.id == datapoint.id:
                datapoint_list[i] = datapoint
                return datapoint_list
        datapoint_list.append(datapoint)
        return datapoint_list

    def remove_datapoint_from_list(datapoint_id: int, datapoint_list: list[DataPointDTO]) -> bool:
        """Remove a datapoint from the list by its ID if it exists.

        Args:
            datapoint_id (int): The ID of the datapoint to remove.
            datapoint_list (list[DataPointDTO]): The list of datapoints.

        Returns:
            bool: True if the datapoint was removed, False if it was not found.
        """

        for i, dp in enumerate(datapoint_list):
            if dp.id == datapoint_id:
                del datapoint_list[i]
                return True
        return False

    @staticmethod
    def find_datapoint_in_list(datapoint_id: int, datapoint_list: list[DataPointDTO]) -> DataPointDTO | None:
        """
        Find a datapoint in the list by its ID.

        Args:
            datapoint_id (int): The ID of the datapoint to find.
            datapoint_list (list[DataPointDTO]): The list of datapoints.

        Returns:
            DataPointDTO | None: The found datapoint, or None if not found.
        """

        return next((dp for dp in datapoint_list if dp.id == datapoint_id), None)

    def update_datapoints(service: ServiceManagerFacade, datapoints: list[DataPointDTO]) -> list[DataPointDTO]:
        """
        Update a list of datapoints using the service manager.

        Args:
            service (ServiceManagerFacade): The service manager to handle the update.
            datapoints (list[DataPointDTO]): The list of datapoints to update.

        Returns:
            list[DataPointDTO]: The updated list of datapoints.
        """

        update_datapoint_dtos = DataPointDTOToUpdateDataPointDTO(
            many=True).dump(datapoints)
        return service.update_datapoints(update_datapoint_dtos)
