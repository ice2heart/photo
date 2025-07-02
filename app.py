from fastapi import FastAPI
import gphoto2 as gp

import enum

app = FastAPI()
camera =  None



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
    return result


@app.post("/connect")
async def connect_camera():
    global camera
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
            return {"status": "connected"}
        except Exception as e:
            camera = None
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "already connected"}

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
        file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
        return {"status": "success", "file_path": f"{file_path.folder}/{file_path.name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}