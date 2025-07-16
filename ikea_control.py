import asyncio

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.device import Device
from pytradfri.resource import ApiResource


class Ikea:
    def __init__(self, host: str, identity: str, psk:str, light_id: int):
        self.host = host
        self.identity = identity
        self.psk = psk
        self.light_id = light_id

    async def get_devices(self):
        self.api_factory = await APIFactory.init(host=self.host, psk_id=self.identity, psk=self.psk)
        self.api = self.api_factory.request

        self.gateway = Gateway()

        devices_command = self.gateway.get_devices()
        devices_commands = await self.api(devices_command)
        devices = await self.api(devices_commands)

        self.lights = [dev for dev in devices if dev.has_light_control]

        def observe_callback(updated_device: ApiResource) -> None:
            assert isinstance(updated_device, Device)
            assert updated_device.light_control is not None
            light = updated_device.light_control.lights[0]
            print(f"Received message for: {light}")

        def observe_err_callback(err: Exception) -> None:
            print("observe error:", err)

        for light in self.lights:
            observe_command = light.observe(
                observe_callback, observe_err_callback, duration=0
            )
            asyncio.create_task(self.api(observe_command))
            await asyncio.sleep(0)

        self.light = [light for light in self.lights if light.id == self.light_id][0]

    async def change_light_state(self, state):
        on_command = self.light.light_control.set_state(state)
        await self.api(on_command)

    async def shutdown(self):
        await self.api_factory.shutdown()
