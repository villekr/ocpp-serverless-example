from datetime import datetime

from ocpp.v16 import ChargePoint
from ocpp.v16 import call, call_result
from ocpp.routing import on, after
from ocpp.v16.enums import (
    Action,
)

class ChargingStation(ChargePoint):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Action handlers

    @on(Action.BootNotification)
    async def on_boot_notification(self, **kwargs):
        print("on_boot_notification")
        payload = call.BootNotificationPayload(**kwargs)
        await self.register_charging_station(self.id, payload)
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status="Accepted",
        )

    @after(Action.BootNotification)
    async def after_boot_notification(self, **kwargs):
        print("after_boot_notification")
        payload = call.GetConfigurationPayload()
        # Problem: CallResult/CallError will invoke another Lambda i.e. we never
        # get response here.
        # One possible solution:
        # - CallResult/CallError messages are put to some queue (e.g. SQS/Redis)
        # - AWSConnection.call polls that queue for specific message and return it as
        # response here. Basically SQS/Redis would be used instead of asyncio.Queue()
        response = await self.call(payload)
        print(response)

    @on(Action.GetConfiguration)
    async def on_get_configuration(self, **kwargs):
        print("on_get_configuration")
        payload = call.GetConfigurationPayload(**kwargs)
        # do something

    # Utilities

    async def register_charging_station(self, id: str, payload: call.BootNotificationPayload):
        print("register_charging_station")
        pass
