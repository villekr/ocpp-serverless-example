# Example how current ChargePoint would use strategies and create context

import asyncio
import inspect

from ocpp_serverless_example.models import (
    # Context,
    # Queue,
    Connection,
    AfterHookStrategy,
    ResponseStrategy,
)


class DefaultResponseStrategy(ResponseStrategy):
    def __init__(self, connection: Connection):
        self.connection = connection

    async def run(self, response):
        await self.connection.send(response)


class DefaultAfterHookStrategy(AfterHookStrategy):
    async def run(self, handler, payload):
        # Create task to avoid blocking when making a call inside the
        # after handler
        response = handler(**payload)
        if inspect.isawaitable(response):
            asyncio.ensure_future(response)


# Example how to create default ChargingStation
# def initiate_charging_station(id: str, websocket: WebSocketServerProtocol):
#     context = Context(
#         queue=asyncio.Queue(),
#         connection=websocket,
#         response_strategy=DefaultResponseStrategy(websocket),
#         after_hook_strategy=DefaultAfterHookStrategy()
#     )
#     charging_station = ChargePoint(id, context)
