from fastapi import FastAPI


from contextlib import asynccontextmanager

from camera import Camera, Params
from lights import Lights, Program

camera: Camera = None
program: Program = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global camera
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
    if camera is None:
        try:
            camera = Camera()
            params = camera.read_params()
            program = Program(Lights(), camera)
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
        file_path = camera.capture()
        return {"status": "success", "file_path": f"{file_path.folder}/{file_path.name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/set_param")
async def set_param(param_name: str, value: str):
    global camera
    if camera is None:
        return {"status": "error", "message": "Camera not connected"}

    if param_name not in Params:
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