import gphoto2 as gp


import enum


class Params(enum.Enum):
    CAPTURE_TARGET = 'capturetarget'
    CAPTURE_SETTINGS = 'capturesettings'
    APERTURE = 'aperture'
    SHUTTER_SPEED = 'shutterspeed'
    ISO = 'iso'
    WHITE_BALANCE = 'whitebalance'

class Camera:
    def __init__(self):
        self.camera = gp.Camera()
        self.camera.init()
        self.camera_config = self.camera.get_config()

        # Set the capture target to memory card
        capture_target = self.camera_config.get_child_by_name(Params.CAPTURE_TARGET.value)
        capture_target.set_value('Memory card')
        self.camera.set_config(self.camera_config)

    def get_camera(self):
        return self.camera

    def get_camera_config(self):
        return self.camera_config
    
    def capture_image(self):
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        print(f'Camera file path: {file_path.folder}/{file_path.name}')
        return file_path
    
    def set_param(self, param_name, value):
        param = self.camera_config.get_child_by_name(param_name)
        if param is None:
            raise ValueError(f"Parameter {param_name} not found in camera configuration.")
        
        param.set_value(value)
        self.camera.set_config(self.camera_config)
        return {param_name: value}

    def exit(self):
        self.camera.exit()
        self.camera = None
        self.camera_config = None
        print("Camera exited successfully.")
    
    def read_param(self, param_name):
        self.camera_config = self.camera.get_config()
        param = self.camera_config.get_child_by_name(param_name)
        if param is None:
            raise ValueError(f"Parameter {param_name} not found in camera configuration.")
        
        return param.get_value()

    def read_params(self):
        self.camera_config = self.camera.get_config()
        params = {}
        for param_name in Params:
            param = self.camera_config.get_child_by_name(param_name.value)
            if param:
                params[param_name.value] = {'value': param.get_value(), 'options': list(param.get_choices())}
        self.params = params
        return params