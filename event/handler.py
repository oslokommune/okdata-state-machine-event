import json
from dataplatform.awslambda.logging import logging_wrapper, log_add
from dataplatform.status import Status, STATUS_OK, STATUS_FAILED, STATUS_FINISHED


@logging_wrapper("lambda-boilerplate")
def act_on_event(event, context):
    details = event.get("detail", None)
    if not details:
        return False
    id = details.get("name")
    event_status = details.get("status")

    # Each event that is still running is responsible to set status, we can
    # ignore them here
    if event_status == "RUNNING":
        return False

    statuses = {
        "ABORTED": STATUS_FAILED,
        "FAILED": STATUS_FAILED,
        "TIMED_OUT": STATUS_FAILED,
        "SUCCEEDED": STATUS_OK,
    }
    if event_status not in statuses:
        return False

    end_status = statuses[event_status]
    status = Status(id)
    status.add(status=end_status, run_status=STATUS_FINISHED)
    # TODO: we will look at the user/application here later on, once we have more experience
    # with the data coming into the system
    status.add(application="dataset", user="system")
    status.add(handler="pipeline-instance")
    status.add(body={})
    status.done()
    headers = {}
    log_add(status_payload=status.payload)
    body = {"message": "Acted on event"}
    return {"statusCode": 200, "headers": headers, "body": json.dumps(body)}
