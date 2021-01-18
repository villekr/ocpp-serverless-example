# This should be part of ocpp library

from __future__ import annotations

from ocpp_serverless_example.models import Context


class Router:
    def __init__(self):
        self.routes = {}
        self.routers: Router = []

    def on(self, action, *, skip_schema_validation=False):
        # TODO: decorator
        pass

    def after(self, action):
        # TODO: decorator
        pass

    def include_router(self, router: Router):
        self.routers.append(router)

    async def route(message: str, context: Context):
        # TODO: ...
        # One thing to solve is how to pass ChargingStation.id to action handler
        # Currently as action handlers are part of ChargePoint subclass they have
        # handler to id as self.id.
        pass
