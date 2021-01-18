import asyncio
import json

from ocpp_router_example.ocpp.router import Router
from ocpp_router_example.routers.provisioning import router as provisioning_router
from ocpp_serverless_example.models import Context
from ocpp_serverless_example.context_aws import (
    AWSQueue,
    AWSConnection,
    AWSAfterHookStrategy,
    AWSResponseStrategy,
)

# Router and routemap is created only once
router = Router()
router.include_router(provisioning_router)


def create_context(lambda_event: dict, lambda_context) -> Context:
    connection_id = lambda_event["requestContext"]["connectionId"]
    queue = AWSQueue(connection_id=connection_id)
    connection = AWSConnection(
        connection_id=connection_id,
        queue=queue,
    )
    response_strategy = AWSResponseStrategy()
    after_hook_strategy = AWSAfterHookStrategy(
        connection_id=connection_id,
        lambda_invocation_context=lambda_context,
    )
    context = Context(
        queue=queue,
        connection=connection,
        response_strategy=response_strategy,
        after_hook_strategy=after_hook_strategy,
    )
    return context


async def handler(event: dict, context: object) -> dict:
    # Context is invocation specific
    context = create_context(event, context)
    ocppj_message = event["body"]
    response = router.route(ocppj_message, context)
    return {"statusCode": 200, "body": response}


if __name__ == "__main__":
    ocpp_message = [
        2,
        "5e11b71c-d87d-4824-8eb9-4e9918bfbd37",
        "BootNotification",
        {"chargePointModel": "Test", "chargePointVendor": "Test"},
    ]
    payload = json.dumps(ocpp_message)
    event = {"requestContext": {"connectionId": "123"}, "body": payload}
    asyncio.run(handler(event))
