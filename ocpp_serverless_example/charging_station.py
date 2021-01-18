from datetime import datetime

from ocpp.routing import after, on
from ocpp.v16 import call, call_result  # , ChargePoint not used but overriden version
from ocpp.v16.enums import Action

from ocpp_serverless_example.charge_point import ChargePoint  # import overriden version
from ocpp_serverless_example.models import (
    Context,
    Queue,
    Connection,
    ResponseStrategy,
    AfterHookStrategy,
)


class ChargingStation(ChargePoint):
    def __init__(self, id, context: Context):
        super().__init__(id=id, connection=context.connection)
        self._response_queue: Queue = context.queue
        self._connection: Connection = context.connection
        self._response_strategy: ResponseStrategy = context.response_strategy
        self._after_hook_strategy: AfterHookStrategy = context.after_hook_strategy

    # Action handlers

    @on(Action.BootNotification)
    async def on_boot_notification(self, **kwargs):
        print("on_boot_notification")
        payload = call.BootNotificationPayload(**kwargs)
        await self.register_charging_station(self.id, payload)  # make internal call
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status="Accepted",
        )

    @after(Action.BootNotification)
    async def after_boot_notification(self, **kwargs):
        print("after_boot_notification")
        payload = call.GetConfigurationPayload()
        response = await self.call(payload)
        print(response)

    # Utilities

    async def register_charging_station(
        self, id: str, payload: call.BootNotificationPayload
    ):
        print("register_charging_station")
        pass
