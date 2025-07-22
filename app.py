from fastapi import FastAPI

from functools import lru_cache
from contextlib import asynccontextmanager

from camera import Camera, Params
from lights import Lights, TopLightsProgram, BottomLightsProgram, BaseProgram

from config import Settings
from ikea_control import Ikea

camera: Camera = None
program: BaseProgram = None
ikea: Ikea = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global camera
    global ikea
    settings = get_settings()
    ikea = Ikea(settings.host, settings.identity, settings.psk, 65546 )
    await ikea.get_devices()
    yield
    if camera is not None:
        camera.exit()
        camera = None


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/status")
async def get_status():
    global camera
    result = {}
    if camera is None:
        result['camera'] = False
    else:
        result['camera'] = True
        result['params'] = camera.read_params()
    return result


@app.post("/connect")
async def connect_camera():
    global camera
    global program
    global ikea
    if camera is None:
        try:
            camera = Camera()
            params = camera.read_params()
            program = TopLightsProgram(Lights(), camera, ikea)
            return {"status": "connected", "camera": True, "params": params}
        except Exception as e:
            camera = None
            return {"status": "error", "camera": False, "message": str(e)}


@app.post("/disconnect")
async def disconnect_camera():
    global camera
    if camera is not None:
        try:
            camera.exit()
            camera = None
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
        file_path = camera.capture_image()
        return {"status": "success", "file_path": f"{file_path.folder}/{file_path.name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/set_param")
async def set_param(param_name: str, value: str):
    global camera
    if camera is None:
        return {"status": "error", "message": "Camera not connected"}

    # ._value2member_map_  required for older python then 3.12
    if param_name not in Params._value2member_map_:
        return {"status": "error", "message": f"Parameter {param_name} not found"}

    try:
        param = camera.set_param(param_name, value)
        return {"status": "success", "param": param}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/run")
async def run_program():
    global program
    if program is None:
        return {"status": "error", "message": "Program not initialized"}
    while (await program.step() != -1):
        pass
    return {"status": "success"}

@app.post("/reset")
async def reset_program():
    global program
    if program is None:
        return {"status": "error", "message": "Program not initialized"}
    await program.reset()
    return {"status": "success"}