from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

import asyncio
from functools import lru_cache
from contextlib import asynccontextmanager

from camera import Camera, Params
from lights import Lights, TopLightsProgram, BottomLightsProgram, BaseProgram

from config import Settings
from ikea_control import Ikea

camera: Camera = None
program: BaseProgram = None
ikea: Ikea = None

step_lock: asyncio.Event = asyncio.Event()
program_lock: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global camera
    global ikea
    settings = get_settings()
    ikea = Ikea(settings.host, settings.identity, settings.psk, 65546)
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
            program = BottomLightsProgram(Lights(), camera, ikea)
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


async def program_exec(program: BaseProgram):
    global step_lock
    global program_lock
    while (program_lock):
        result = await program.step()
        yield f'event: StepUpdate\ndata: {result}\n\n'
        if result == -1:
            step_lock.clear()
            await step_lock.wait()
        if result == -2:
            return


@app.post("/run")
async def run_program():
    global program
    global program_lock
    global step_lock
    if program is None:
        raise HTTPException(status_code=500, detail="Program not initialized")
    program_lock = True
    step_lock.clear()
    return StreamingResponse(program_exec(program), media_type="text/event-stream")


@app.post("/continue")
async def continue_exec():
    global step_lock
    step_lock.clear()
    return {"status": "success"}


@app.post("/reset")
async def reset_program():
    global program
    global program_lock
    global step_lock
    if program is None:
        return {"status": "error", "message": "Program not initialized"}
    program_lock = False
    step_lock.set()
    await program.reset()
    return {"status": "success"}


@app.post("/light")
async def set_light(name: str, value: str):
    global program
    if name == "TOP":
        await program.top_ring(bool(value))
    if name == "SIDE":
        await program.side_light(bool(value))
    if name == "BOTTOM":
        await program.bottom_light(bool(value))
    return {"status": "success"}
