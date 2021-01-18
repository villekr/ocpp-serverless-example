from ocpp.v16.enums import Action

from ocpp_router_example.ocpp import Router

router = Router()


@router.on(Action.BootNotification)
async def on_boot_notification(self, **kwargs):
    pass


@router.after(Action.BootNotification)
async def after_boot_notification(self, **kwargs):
    pass
