import asyncio
import os

import boto3

from ocpp_serverless_example.charging_station import ChargingStation
from ocpp_serverless_example.connection_aws import AWSLambdaConnection

endpoint_url = os.getenv("APIGATEWAY_WEBSOCKET_ENDPOINT_URL")
apigateway_client = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)

# Problem: Charging Station identity, action handlers and connection are all bundled.
# Ideally we would build route map (create_route_map) only once and share that for
# different event invocations.
charging_station = ChargingStation(id=None, connection=None)


def lambda_handler(event, context):
    asyncio.get_event_loop().run_until_complete(async_lambda_hander(event, context))


async def async_lambda_hander(event, context):
    print(event)
    connection_id = event["requestContext"]["connectionId"]
    # Problem(?): In order to route messages we have to create instance of a class
    # that implements websocket send and recv interface. This is not likely a problem
    # but has to be part of the solution i.e. based on environment different adaptation
    # is needed in order to operate in event based fashion.
    connection = AWSLambdaConnection(
        apigateway_client=apigateway_client, connection_id=connection_id
    )
    # Problem: identity (id) should be passed somehow to route_message so that action
    # handlers will have id available to map message handling with correct charging
    # station identity.
    # (AWS Websockets API connection_id doesn't represent "id" but for here this can do)
    charging_station.id = connection_id
    # Problem: Connection is different based on event, patch to _connection here.
    # Possibly connection should be given as a parameter to route message, I don't know.
    charging_station._connection = connection
    # Problem: route_message invokes both on and after hooks. return value from on-hook
    # (CallResult/CallError) is send to websockets api within route_message handling.
    # More natural way in lambda would be to utilize lambda return value.
    #   return {"statusCode": 200, "body": on_hook_return_value}
    # But the problem then is how to execute after-hook? Perhaps invoke different lambda
    # function if after-hook is defined?
    await charging_station.route_message(event["body"])
    # Problem: Lambda return value is also delivered to websocket end so it'll receive
    # 2 responses (CallResult/CallError and None)
    return {"statusCode": 200}
