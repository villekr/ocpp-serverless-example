# Override ChargePoint methods
# These should be moved to ocpp.charge_point

import inspect
from dataclasses import asdict

from ocpp.charge_point import (
    camel_to_snake_case,
    LOGGER,
    remove_nones,
    snake_to_camel_case,
)
from ocpp.exceptions import OCPPError
from ocpp.messages import unpack, MessageType, validate_payload
from ocpp.v16 import ChargePoint as CP


class ChargePoint(CP):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def route_message(self, raw_msg):
        """
        Route a message received from a CP.

        If the message is a of type Call the corresponding hooks are executed.
        If the message is of type CallResult or CallError the message is passed
        to the call() function via the response_queue.
        """
        try:
            msg = unpack(raw_msg)
        except OCPPError as e:
            LOGGER.exception(
                "Unable to parse message: '%s', it doesn't seem "
                "to be valid OCPP: %s",
                raw_msg,
                e,
            )
            return

        if msg.message_type_id == MessageType.Call:
            # await self._handle_call(msg)
            response = await self._handle_call(msg)
            return response

        elif msg.message_type_id in [MessageType.CallResult, MessageType.CallError]:
            self._response_queue.put_nowait(msg)

    async def _handle_call(self, msg):
        """
        Execute all hooks installed for based on the Action of the message.

        First the '_on_action' hook is executed and its response is returned to
        the client. If there is no '_on_action' hook for Action in the message
        a CallError with a NotImplemtendError is returned.

        Next the '_after_action' hook is executed.

        """
        try:
            handlers = self.route_map[msg.action]
        except KeyError:
            raise NotImplementedError(f"No handler for '{msg.action}' " "registered.")

        if not handlers.get("_skip_schema_validation", False):
            validate_payload(msg, self._ocpp_version)

        # OCPP uses camelCase for the keys in the payload. It's more pythonic
        # to use snake_case for keyword arguments. Therefore the keys must be
        # 'translated'. Some examples:
        #
        # * chargePointVendor becomes charge_point_vendor
        # * firmwareVersion becomes firmwareVersion
        snake_case_payload = camel_to_snake_case(msg.payload)

        try:
            handler = handlers["_on_action"]
        except KeyError:
            raise NotImplementedError(f"No handler for '{msg.action}' " "registered.")

        try:
            response = handler(**snake_case_payload)
            if inspect.isawaitable(response):
                response = await response
        except Exception as e:
            LOGGER.exception("Error while handling request '%s'", msg)
            response = msg.create_call_error(e).to_json()
            await self._send(response)

            return

        temp_response_payload = asdict(response)

        # Remove nones ensures that we strip out optional arguments
        # which were not set and have a default value of None
        response_payload = remove_nones(temp_response_payload)

        # The response payload must be 'translated' from snake_case to
        # camelCase. So:
        #
        # * charge_point_vendor becomes chargePointVendor
        # * firmware_version becomes firmwareVersion
        camel_case_payload = snake_to_camel_case(response_payload)

        response = msg.create_call_result(camel_case_payload)

        if not handlers.get("_skip_schema_validation", False):
            validate_payload(response, self._ocpp_version)

        response = await self._response_strategy.run(response.to_json())

        try:
            handler = handlers["_after_action"]
            await self._after_hook_strategy.run(handler, snake_case_payload)
        except KeyError:
            # '_on_after' hooks are not required. Therefore ignore exception
            # when no '_on_after' hook is installed.
            pass
        return response
