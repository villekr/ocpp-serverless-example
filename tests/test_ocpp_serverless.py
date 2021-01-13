import os
from dataclasses import asdict
from uuid import uuid4

import pytest
import websockets
from ocpp.charge_point import remove_nones, snake_to_camel_case
from ocpp.messages import Call, CallResult
from ocpp.v16 import call, call_result

WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")


def payload_to_ocppj_message(payload, *, class_type) -> str:
    # Helper to convert ocpp payload class to ocpp-j message string
    camel_case_payload = snake_to_camel_case(asdict(payload))
    call = class_type(
        unique_id=str(uuid4()),
        action=payload.__class__.__name__[:-7],
        payload=remove_nones(camel_case_payload),
    )
    message = call.to_json()
    return message


@pytest.mark.asyncio
async def test_send_receive():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        try:
            boot_notification_payload = call.BootNotificationPayload(
                charge_point_model="Test", charge_point_vendor="Test"
            )
            get_configuration_payload = call_result.GetConfigurationPayload(
                configuration_key=[
                    {
                        "key": "GetConfigurationMaxKeys",
                        "readonly": True,
                        "value": "10",
                    }
                ]
            )
            ocppj_message = payload_to_ocppj_message(
                boot_notification_payload, class_type=Call
            )
            await websocket.send(ocppj_message)  # -> Call/BootNotificationPayload
            response = await websocket.recv()  # <- CallResult/BootNotificationPayload
            print(response)
            response = await websocket.recv()  # <- Call/GetConfiguration
            print(response)
            ocppj_message = payload_to_ocppj_message(
                get_configuration_payload, class_type=CallResult
            )

            await websocket.send(ocppj_message)  # -> CallResult/GetConfiguration
            response = await websocket.recv()  # <- None
            print(response)
            response = await websocket.recv()  # <- None
            print(response)
            response = await websocket.recv()  # <- None
            print(response)
        except Exception as e:
            print(f"Exception: {e}")

        # If exception happens in websocket integration we get message:
        # {
        #     "message": "Internal server error",
        #     "connectionId": "ZEqRad4HjoECIqg=",
        #     "requestId": "ZEqRuGA-joEF6QA=",
        # }
