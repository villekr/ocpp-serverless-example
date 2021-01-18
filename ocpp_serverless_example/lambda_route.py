import asyncio

from ocpp_serverless_example.charging_station import ChargingStation
from ocpp_serverless_example.models import Context
from ocpp_serverless_example.context_aws import (
    AWSQueue,
    AWSConnection,
    AWSAfterHookStrategy,
    AWSResponseStrategy,
)


def lambda_handler(event, context):
    response = asyncio.get_event_loop().run_until_complete(
        async_lambda_hander(event, context)
    )
    return {"statusCode": 200, "body": response}


async def async_lambda_hander(event, context):
    print("------------")
    connection_id = event["requestContext"]["connectionId"]
    queue = AWSQueue(connection_id=connection_id)
    connection = AWSConnection(
        connection_id=connection_id,
        queue=queue,
    )
    response_strategy = AWSResponseStrategy()
    after_hook_strategy = AWSAfterHookStrategy(
        connection_id=connection_id,
        lambda_invocation_context=context,
    )
    context = Context(
        queue=queue,
        connection=connection,
        response_strategy=response_strategy,
        after_hook_strategy=after_hook_strategy,
    )
    charging_station = ChargingStation(id=None, context=context)
    if "afterHook" in event["requestContext"]:
        handler_name = event["requestContext"]["handlerName"]
        payload = event["body"]
        handler = getattr(charging_station, handler_name)
        print(f"handler: {handler}")
        await handler(**payload)
    else:
        response = await charging_station.route_message(event["body"])
        return response
