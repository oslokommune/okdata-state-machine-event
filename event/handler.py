import json

from okdata.aws.logging import logging_wrapper
from okdata.aws.status import status_wrapper, status_add, TraceStatus, TraceEventStatus


finished_statuses = {
    "ABORTED": TraceEventStatus.FAILED,
    "FAILED": TraceEventStatus.FAILED,
    "TIMED_OUT": TraceEventStatus.FAILED,
    "SUCCEEDED": TraceEventStatus.OK,
}


@logging_wrapper
def act_on_event(event, context):
    return True


@logging_wrapper
def act_on_queue(event, context):
    records = event.get("Records", None)

    if not records:
        raise ValueError("Event does not contain Records")

    record = records[0]
    source = record["EventSource"]

    if source != "aws:sns":
        raise ValueError(
            f"Unsuported 'EventSource' {source}. Supported types: 'aws:sns'"
        )

    event = json.loads(record["Sns"]["Message"])

    try:
        event_status = event["detail"]["status"]
    except KeyError:
        return False

    # Ignore statuses where pipeline is not finished
    if event_status not in finished_statuses:
        return False

    return set_finished_status(event, context)


@status_wrapper
def set_finished_status(event, context):
    trace_id = event["detail"].get("name")
    trace_event_status = finished_statuses[event["detail"]["status"]]

    status_add(
        trace_id=trace_id,
        domain="dataset",
        operation="set_finished_status",
        trace_event_status=trace_event_status,
        trace_status=TraceStatus.FINISHED,
    )

    headers = {}
    body = {"message": "Acted on event"}
    return {"statusCode": 200, "headers": headers, "body": json.dumps(body)}
