"""
A module to monitor fine-tuning jobs by fetching and displaying fine-tuning events.

Classes:
    FineTuningMonitor:
"""


from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.classes.evaluators.model_metrics_evaluator import ModelMetricsEvaluator


class FineTuningJobMonitor:
    """
    A class to monitor fine-tuning jobs by fetching and displaying fine-tuning events.

    Attributes:
        _service (ServiceManagerFacade): An instance of the service manager to interact with backend services.
        _last_event_id (str | None): The ID of the last event fetched.
        _limit (int): The number of events to fetch per request.
        _fetched_events (list[object]): A list to store fetched events.
        _request_running (bool): A flag to indicate if a request is currently running.
    """

    def __init__(self, service: ServiceManagerFacade, limit: int = 20):
        """
        Initializes the FineTuningJobMonitor with the given service and event fetch limit.

        Parameters:
            service (ServiceManagerFacade): An instance of the service manager to interact with backend services.
            limit (int): The number of events to fetch per request. Default is 20.
        """

        self._service = service
        self._last_event_id = None  # Track the last event ID fetched
        self._limit = limit  # How many events to fetch with one request
        self._fetched_events: list[object] = []  # Store fetched events
        self._request_running: bool = False

    def fetch_new_events(self, fine_tuning_job_id: str) -> list[object]:
        """
        Fetches new events for a given fine-tuning job ID.

        Parameters:
            fine_tuning_job_id (str): The ID of the fine-tuning job to fetch events for.

        Returns:
            list[object]: A list of new events fetched.
        """

        new_events = self._service.fetch_new_events(
            fine_tuning_job_id, limit=self._limit, last_event_id=self._last_event_id)

        if new_events:
            # Prepend new events to maintain chronological order
            self._fetched_events = new_events + self._fetched_events
            # The newest / latest event produced
            self._last_event_id = self._fetched_events[0].id

    def draw_current_fine_tuning_graph(self, fine_tuning_job_id: str):
        """
        Draws the current fine-tuning graph for a given fine-tuning job ID.

        Parameters:
            fine_tuning_job_id (str): The ID of the fine-tuning job to draw the graph for.
        """

        if not self._request_running and not self.check_if_last_step_event():
            self._request_running = True
            self.fetch_new_events(fine_tuning_job_id)
            self._request_running = False

        ModelMetricsEvaluator.show_current_fine_tuning_event_progress(
            self._fetched_events)

    def check_if_last_step_event(self):
        """
        Checks if the last fetched event corresponds to the final step of the fine-tuning job.

        Returns:
            bool: True if the last event is the final step, False otherwise.
        """

        if self._fetched_events:
            events_with_data: list[object] = self.filter_events_with_data_and_step(
            )
            if events_with_data:
                return events_with_data[0].model_extra.get('data').get('step') == events_with_data[0].model_extra.get('data').get('total_steps')
        return False

    def filter_events_with_data_and_step(self):
        """
        Filters the fetched events to only include those with data and step information.

        Returns:
            list[object]: A list of filtered events with data and step information.
        """

        filtered_events: list[object] = [
            event for event in self._fetched_events if event.model_extra.get('data') and event.model_extra.get('data').get('step')
        ]
        return filtered_events
