import asyncio
import json
import os

import boto3
from redis import Redis
from ocpp.messages import pack, unpack

from ocpp_serverless_example.models import (
    Queue,
    Connection,
    AfterHookStrategy,
    ResponseStrategy,
)

REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT")
REDIS_PORT = os.getenv("REDIS_PORT")
APIGATEAY_ENDPOINT = os.getenv("APIGATEWAY_WEBSOCKET_ENDPOINT_URL")

apigateway_client = boto3.client(
    "apigatewaymanagementapi", endpoint_url=APIGATEAY_ENDPOINT
)
lambda_client = boto3.client("lambda")


class AWSQueue(Queue):
    def __init__(self, connection_id: str):
        self.redis: Redis = Redis(host=REDIS_ENDPOINT, port=REDIS_PORT)
        self.connection_id: str = connection_id

    async def get(self) -> str:
        print(f"get: {self.connection_id}")
        # What is optimal sleep time while waiting response?
        # Here we have gradually increasing sleep time up to 1s max
        sleep_duration = 0.2
        sleep_duration_max = 1
        while True:
            msg = self.redis.rpop(self.connection_id)
            if msg is None or type(msg) is not bytes:
                print(f"sleep. type(msg): {type(msg)} msg: {msg}")
                await asyncio.sleep(sleep_duration)
                if sleep_duration_max < sleep_duration_max:
                    sleep_duration_max += 0.2
            else:
                print(f"get (result): {msg}")
                return unpack(msg)

    def put_nowait(self, msg):
        msg_str = pack(msg)
        print(f"put_nowait: {self.connection_id}, {msg_str}")
        self.redis.rpush(self.connection_id, msg_str)


class AWSConnection(Connection):
    def __init__(self, *, connection_id: str, queue: AWSQueue):
        self.apigateway_client = apigateway_client
        self.connection_id: str = connection_id
        self.queue: AWSQueue = queue

    async def send(self, message: str):
        print(f"send: {self.connection_id} {message}")
        self.apigateway_client.post_to_connection(
            Data=message, ConnectionId=self.connection_id
        )

    async def recv(self) -> str:
        # recv is not utilized in event based handling within ChargePoint class
        # i.e. ChargePoint.start() should not be called at all
        raise NotImplementedError


class AWSResponseStrategy(ResponseStrategy):
    def __init__(self):
        pass

    async def run(self, response):
        # In AWS Lambda we wan't to return response as lambda function return value
        return response


class AWSAfterHookStrategy(AfterHookStrategy):
    def __init__(self, *, connection_id, lambda_invocation_context):
        self.connection_id = connection_id
        self.lambda_client = lambda_client
        self.lambda_invocation_context = lambda_invocation_context

    async def run(self, handler, payload):
        # Lambda strategy is to invoke another lambda for after-hook processing
        event = {
            "requestContext": {
                "connectionId": self.connection_id,
                "afterHook": True,
                "handlerName": handler.__name__,
            },
            "body": payload,
        }
        self.lambda_client.invoke(
            FunctionName=self.lambda_invocation_context.invoked_function_arn,
            InvocationType="Event",
            Payload=json.dumps(event),
        )
