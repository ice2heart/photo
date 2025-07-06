from fastapi import FastAPI
import gphoto2 as gp

import enum
from dataclasses import dataclass
from contextlib import asynccontextmanager


camera = None
camera_config = None


class Params(enum.Enum):
    CAPTURE_TARGET = 'capturetarget'
    CAPTURE_SETTINGS = 'capturesettings'
    APERTURE = 'aperture'
    SHUTTER_SPEED = 'shutterspeed'
    ISO = 'iso'
    WHITE_BALANCE = 'whitebalance'


@dataclass
class Param:
    name: str
    value: str
    options: list[str]
    address: gp.gphoto2.widget.CameraWidget


params: dict[Param] = {}


def update_params():
    global camera
    global params
    global camera_config
    camera_config = camera.get_config()
    apperture = camera_config.get_child_by_name('aperture')
    if apperture is not None:
        params[Params.APERTURE] = Param(
            name=Params.APERTURE.value,
            value=apperture.get_value(),
            options=list(apperture.get_choices()),
            address=apperture
        )
    shutter_speed = camera_config.get_child_by_name('shutterspeed')
    if shutter_speed is not None:
        params[Params.SHUTTER_SPEED] = Param(
            name=Params.SHUTTER_SPEED.value,
            value=shutter_speed.get_value(),
            options=list(shutter_speed.get_choices()),
            address=shutter_speed
        )
    iso = camera_config.get_child_by_name('iso')
    if iso is not None:
        params[Params.ISO] = Param(
            name=Params.ISO.value,
            value=iso.get_value(),
            options=list(iso.get_choices()),
            address=iso
        )
    white_balance = camera_config.get_child_by_name('whitebalance')
    if white_balance is not None:
        params[Params.WHITE_BALANCE] = Param(
            name=Params.WHITE_BALANCE.value,
            value=white_balance.get_value(),
            options=list(white_balance.get_choices()),
            address=white_balance
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global camera
    yield
    if camera is not None:
        camera.exit()

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/status")
async def get_status():
    global camera
    global params
    global camera_config
    result = {}
    if camera is None:
        result['camera'] = False
    else:
        result['camera'] = True
        update_params()
        result['params'] = {param.name: {'value': param.value,
                                         'options': param.options} for param in params.values()}
    return result


@app.post("/connect")
async def connect_camera():
    global camera
    global params
    global camera_config
    if camera is None:
        try:
            camera = gp.Camera()
            camera.init()
            camera_config = camera.get_config()
            # Set the capture target to memory card
            capture_target = camera_config.get_child_by_name('capturetarget')
            if capture_target:
                capture_target.set_value('Memory card')
                camera.set_config(camera_config)

            update_params()
            return {"status": "connected", "params": {param.name: {'value': param.value, 'options': param.options} for param in params.values()}}
        except Exception as e:
            camera = None
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "already connected"}


@app.post("/disconnect")
async def disconnect_camera():
    global camera
    global params
    if camera is not None:
        try:
            camera.exit()
            camera = None
            params.clear()
            return {"status": "disconnected"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "not connected"}


@app.post("/capture")
async def capture_image():
    global camera
    if camera is None:
        return {"status": "error", "message": "Camera not connected"}
    try:
        file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
        return {"status": "success", "file_path": f"{file_path.folder}/{file_path.name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/set_param")
async def set_param(param_name: str, value: str):
    global camera
    global params
    global camera_config
    param_name = Params(param_name)
    if camera is None:
        return {"status": "error", "message": "Camera not connected"}

    if param_name not in params:
        return {"status": "error", "message": f"Parameter {param_name} not found"}

    try:
        param = params[param_name]
        param.address.set_value(value)
        camera.set_config(camera_config)
        param.value = value
        return {"status": "success", "param": { param.name: param.value}}
    except Exception as e:
        return {"status": "error", "message": str(e)}
