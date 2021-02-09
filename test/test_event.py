import json
import pytest
import re

from okdata.aws.status import TraceStatus, TraceEventStatus
from okdata.aws.status.sdk import Status

from event.handler import act_on_queue

empty_context = {}


def make_event(message):
    return {
        "Records": [{"EventSource": "aws:sns", "Sns": {"Message": json.dumps(message)}}]
    }


class TestActOnQueue:
    def test_send_event_invalid_source(self):
        with pytest.raises(ValueError):
            act_on_queue({"Records": [{"EventSource": "unknown"}]}, empty_context)

    def test_send_empty_event(self):
        with pytest.raises(ValueError):
            act_on_queue({}, empty_context)

    def test_send_event_empty_message(self):
        result = act_on_queue(
            {"Records": [{"EventSource": "aws:sns", "Sns": {"Message": "{}"}}]},
            empty_context,
        )
        assert result is False

    def test_send_event_status_is_still_running(self):
        result = act_on_queue(
            make_event({"detail": {"status": "RUNNING"}}), empty_context
        )
        assert result is False

    def test_send_event_with_unknown_status(self):
        result = act_on_queue(
            make_event({"detail": {"status": "NOT_RECOGNIZED"}}), empty_context
        )
        assert result is False

    def test_send_event_with_succeeded_status(self, mocker):
        mocker.patch.object(Status, "done", return_value={})
        s = mocker.spy(Status, "add")

        trace_id = "trace-id-abc123-1a2b3c"
        result = act_on_queue(
            make_event({"detail": {"status": "SUCCEEDED", "name": trace_id}}),
            empty_context,
        )

        assert (
            mocker.call(
                mocker.ANY,
                trace_id=trace_id,
                domain="dataset",
                operation="set_finished_status",
                trace_event_status=TraceEventStatus.OK,
                trace_status=TraceStatus.FINISHED,
            )
            in s.call_args_list
        )

        Status.done.assert_called_once()
        assert result is True

    def test_send_event_with_aborted_status(self, mocker):
        mocker.patch.object(Status, "done", return_value={})
        s = mocker.spy(Status, "add")

        trace_id = "trace-id-abc123-1a2b3c"
        result = act_on_queue(
            make_event({"detail": {"status": "ABORTED", "name": trace_id}}),
            empty_context,
        )

        assert (
            mocker.call(
                mocker.ANY,
                trace_id=trace_id,
                domain="dataset",
                operation="set_finished_status",
                trace_event_status=TraceEventStatus.FAILED,
                trace_status=TraceStatus.FINISHED,
            )
            in s.call_args_list
        )

        Status.done.assert_called_once()
        assert result is True

    def test_send_event_with_unknown_trace_id(self, requests_mock):
        matcher = re.compile("status-api")
        requests_mock.register_uri("POST", matcher, status_code=404)

        trace_id = "trace-id-abc123-1a2b3c"
        result = act_on_queue(
            make_event({"detail": {"status": "SUCCEEDED", "name": trace_id}}),
            empty_context,
        )

        assert result is False
