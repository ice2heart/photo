import board
import neopixel

import enum

from camera import Camera
from ikea_control import Ikea


class ACTIONS(enum.Enum):
    USER_INPUT = 'user_input'
    NO_ACTION = 'no_action'
    CAPTURE = 'capture'


class Lights:
    def __init__(self):
        self.sides = neopixel.NeoPixel(board.D10, 72, pixel_order=neopixel.RGBW)
        self.sides.fill((0, 0, 0, 0))  # Initialize all pixels

    def clear(self):
        self.sides.fill((0, 0, 0, 0))

    def set_sides(self, color, ids):
        for i in ids:
            if 0 <= i < len(self.sides):
                self.sides[i] = color
            else:
                raise ValueError(f"Index {i} is out of bounds for sides array.")


class Program:
    def __init__(self, lights: Lights, camera: Camera, ikea: Ikea):
        self.lights = lights
        self.camera = camera
        self.ikea = ikea
        self.stage = None  # Current stage of the program
        self.program = [
            {'name': 'Focus', 'color': (0, 0, 0, 250), 'ids': [0, 1, 2, 3, 4, 5, 6, 7], 'action': ACTIONS.USER_INPUT},
            {'name': 'Side', 'color': (0, 0, 0, 250), 'ids': [8, 9, 10, 11], 'action': ACTIONS.USER_INPUT},
            {'name': 'Side', 'light': True, 'action': ACTIONS.USER_INPUT},
            {'name': 'Stage 0', 'light': False, 'color': (0, 0, 0, 250), 'ids': [0, 1, 2, 3, 4, 5, 6, 7],  'action': ACTIONS.CAPTURE, 'camera': {
                'shutterspeed': '1/5', 'iso': '400', 'aperture': '7.1', 'whitebalance': 'Flash'}},
            {'name': 'Stage 1', 'color': (0, 0, 0, 250), 'ids': [8, 9, 10, 11], 'action': ACTIONS.CAPTURE, 'camera': {
                'shutterspeed': '0.5', 'iso': '400', 'aperture': '7.1', 'whitebalance': 'Tungsten'}},
            {'name': 'Stage 2', 'color': (0, 0, 0, 250), 'ids': [20, 21, 22, 23], 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 3', 'color': (0, 0, 0, 250), 'ids': [24, 25, 26, 27], 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 4',  'color': (0, 0, 0, 250), 'ids': [36, 37, 38, 39], 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 5', 'color': (0, 0, 0, 250), 'ids': [40, 41, 42, 43], 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 6', 'color': (0, 0, 0, 250), 'ids': [52, 53, 54, 55], 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 7',  'color': (0, 0, 0, 250), 'ids': [56, 57, 58, 59], 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 8',  'color': (0, 0, 0, 250), 'ids': [68, 69, 70, 71], 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 9',  'light': True, 'action': ACTIONS.CAPTURE},
            {'name': 'Final',  'light': False, 'action': ACTIONS.NO_ACTION},
        ]

    async def step(self) -> int:
        stage_index = 0
        if self.stage is not None:
            # previous_stage = self.stage[self.stage]
            self.lights.clear()
            stage_index = self.stage+1
            # if 'light' in self.program[self.stage]:
            #     self.ikea.change_light_state( not self.program[self.stage]['light']);

        self.stage = stage_index
        try:
            stage = self.program[stage_index]
        except IndexError:
            self.stage = None
            return -1
        if 'color' in stage:
            self.lights.set_sides(stage['color'], stage.get('ids', []))

        if 'light' in stage:
            await self.ikea.change_light_state(stage['light'])

        if 'camera' in stage:
            for k in stage['camera']:
                self.camera.set_param(k, stage['camera'][k])

        if stage['action'] == ACTIONS.USER_INPUT:
            return -1
        elif stage['action'] == ACTIONS.CAPTURE:
            self.camera.capture_image()
        return 0
