from event.handler import act_on_event
from dataplatform.status import Status

empty_context = {}


class TestActOnEvent:
    def test_send_event_empty_event(self):
        result = act_on_event({}, empty_context)
        assert result is False

    def test_send_event_status_is_still_running(self):
        result = act_on_event({"detail": {"status": "RUNNING"}}, empty_context)
        assert result is False

    def test_send_event_with_unknown_status(self):
        result = act_on_event({"detail": {"status": "NOT_RECOGNIZED"}}, empty_context)
        assert result is False

    def test_send_event_with_correct_status(self, mocker):
        mocker.patch.object(Status, "done", return_value={})
        result = act_on_event({"detail": {"status": "SUCCEEDED"}}, empty_context)
        assert result["statusCode"] == 200
