import gphoto2 as gp

import enum
import logging


class Params(enum.Enum):
    CAPTURE_TARGET = 'capturetarget'
    CAPTURE_SETTINGS = 'capturesettings'
    APERTURE = 'aperture'
    SHUTTER_SPEED = 'shutterspeed'
    ISO = 'iso'
    WHITE_BALANCE = 'whitebalance'


class BaseCamera:
    def capture_image(self):
        logging.info('capture_image')

    def set_param(self, param_name, value):
        logging.info(f'set_param {param_name} = {value}')

    def exit(self):
        logging.info('exit')

    def read_param(self, param_name):
        logging.info(f'read_param {param_name}')
        return "mock"

    def read_params(self):
        logging.info('read_params')
        return {'aperture': {'value': 'test', 'options': ['test', 'test2']},
                'shutterspeed': {'value': 'test', 'options': ['test', 'test2']},
                'iso': {'value': 'test', 'options': ['test', 'test2']},
                'whitebalance': {'value': 'test', 'options': ['test', 'test2']}}

class Camera(BaseCamera):
    def __init__(self):
        self.camera = gp.Camera()
        self.camera.init()
        self.camera_config = self.camera.get_config()

        # Set the capture target to memory card
        capture_target = self.camera_config.get_child_by_name(Params.CAPTURE_TARGET.value)
        capture_target.set_value('Memory card')
        self.camera.set_config(self.camera_config)

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
                try:
                    params[param_name.value] = {'value': param.get_value(), 'options': list(param.get_choices())}
                except gp.GPhoto2Error:
                    pass
        self.params = params
        return params
