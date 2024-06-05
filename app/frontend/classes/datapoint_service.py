from __future__ import annotations
from typing import TYPE_CHECKING
import streamlit as st
from app.backend.dtos.response import DataPointDTO
from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.mappers.frontend_mappers import DataPointDTOToUpdateDataPointDTO


class DataPointService:

    @staticmethod
    def add_or_remove(current_test_datapoint: DataPointDTO, datapoint: DataPointDTO) -> None:
        """Add or remove a datapoint from the related datapoints list."""
        if any(dp.id == datapoint.id for dp in current_test_datapoint.related_datapoints):
            current_test_datapoint.related_datapoints = [
                dp for dp in current_test_datapoint.related_datapoints if dp.id != datapoint.id
            ]
        else:
            current_test_datapoint.related_datapoints.append(datapoint)

    @staticmethod
    def is_present(current_test_datapoint: DataPointDTO, datapoint: DataPointDTO) -> None:
        """Check if datapoint exists."""
        if any(dp.id == datapoint.id for dp in current_test_datapoint.related_datapoints):
            return True
        else:
            return False

    def update_datapoints(service: ServiceManagerFacade, datapoints: list[DataPointDTO]) -> list[DataPointDTO]:
        update_datapoint_dtos = DataPointDTOToUpdateDataPointDTO(
            many=True).dump(datapoints)
        return service.update_datapoints(update_datapoint_dtos)
