from app.backend.service.implementations.service_manager_facade import ServiceManagerFacade
from app.frontend.classes.evaluators.model_metrics_evaluator import ModelMetricsEvaluator


class FineTuningJobMonitor:
    def __init__(self, service: ServiceManagerFacade, limit: int = 20):
        self._service = service
        self._last_event_id = None  # Track the last event ID fetched
        self._limit = limit  # How many events to fetch with one request
        self._fetched_events: list[object] = []  # Store fetched events
        self._request_running: bool = False

    def fetch_new_events(self, fine_tuning_job_id: str) -> list[object]:
        new_events = self._service.fetch_new_events(
            fine_tuning_job_id, limit=self._limit, last_event_id=self._last_event_id)

        if new_events:
            # Prepend new events to maintain chronological order
            self._fetched_events = new_events + self._fetched_events
            # The newest / latest event produced
            self._last_event_id = self._fetched_events[0].id

    def draw_current_fine_tuning_graph(self, fine_tuning_job_id: str):
        if not self._request_running and not self.check_if_last_step_event():
            self._request_running = True
            self.fetch_new_events(fine_tuning_job_id)
            self._request_running = False

        ModelMetricsEvaluator.show_current_fine_tuning_event_progress(
            self._fetched_events)

    def check_if_last_step_event(self):
        if self._fetched_events:
            events_with_data: list[object] = self.filter_events_with_data_and_step(
            )
            if events_with_data:
                return events_with_data[0].model_extra.get('data').get('step') == events_with_data[0].model_extra.get('data').get('total_steps')
        return False

    def filter_events_with_data_and_step(self):
        filtered_events: list[object] = [
            event for event in self._fetched_events if event.model_extra.get('data') and event.model_extra.get('data').get('step')
        ]
        return filtered_events
