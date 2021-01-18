import logging
import os
from dataclasses import asdict
from uuid import uuid4

import pytest
import websockets
from ocpp.charge_point import remove_nones, snake_to_camel_case
from ocpp.messages import Call, CallResult, unpack
from ocpp.v16 import call, call_result

FORMAT = "[%(asctime)s - %(funcName)s - %(lineno)s] %(message)s"
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel("DEBUG")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")


# Note! This test code looks quite mess as we build occp-j messages here by ourselves
# instead of using ocpp-library ChargePoint instance to send these.
# One problem with ocpp ChargePoint implementation is that it's quite hard to drive
# testing as ChargePoint.start() blocks the thread while listenin incoming messages
# from websocket.


def payload_to_ocppj_message(payload, *, class_type, unique_id: str) -> str:
    # Helper to convert ocpp payload class to ocpp-j message string
    camel_case_payload = snake_to_camel_case(asdict(payload))
    call = class_type(
        unique_id=unique_id,
        action=payload.__class__.__name__[:-7],
        payload=remove_nones(camel_case_payload),
    )
    message = call.to_json()
    return message


@pytest.mark.asyncio
async def test_send_receive():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
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
            boot_notification_payload, class_type=Call, unique_id=str(uuid4())
        )
        await websocket.send(ocppj_message)  # -> Call/BootNotificationPayload
        call_result_msg = (
            await websocket.recv()
        )  # <- CallResult/BootNotificationPayload
        call_result_obj = unpack(call_result_msg)
        log.info(call_result_obj)
        assert type(call_result_obj) == CallResult
        call_msg = await websocket.recv()  # <- Call/GetConfiguration
        call_obj = unpack(call_msg)
        log.info(call_obj)
        assert type(call_obj) == Call
        unique_id = call_obj.unique_id  # use Call's unique_id in CallResult
        ocppj_message = payload_to_ocppj_message(
            get_configuration_payload, class_type=CallResult, unique_id=unique_id
        )
        log.info(ocppj_message)
        await websocket.send(ocppj_message)  # -> CallResult/GetConfiguration

        # If exception happens in websocket integration we get message:
        # {
        #     "message": "Internal server error",
        #     "connectionId": "ZEqRad4HjoECIqg=",
        #     "requestId": "ZEqRuGA-joEF6QA=",
        # }
