import board
import neopixel

import enum

from camera import Camera


class TYPE(enum.Enum):
    TOP = 'top'
    SIDES = 'sides'


class ACTIONS(enum.Enum):
    USER_INPUT = 'user_input'
    NO_ACTION = 'no_action'
    CAPTURE = 'capture'


class Lights:
    def __init__(self):
        self.top = neopixel.NeoPixel(pin=board.D18, num_pixels=8)
        self.top.fill((0, 0, 0))  # Initialize all pixels to off
        self.sides = neopixel.NeoPixel(pin=board.D10, num_pixels=64, pixel_order=neopixel.RGBW)
        self.sides.fill((0, 0, 0, 0))  # Initialize all pixels

    def clear(self):
        self.top.fill((0, 0, 0))  # Turn off all pixels
        self.sides.fill((0, 0, 0, 0))

    def set_top(self, color):
        self.top.fill(color)

    def set_sides(self, color, ids):
        for i in ids:
            if 0 <= i < len(self.sides):
                self.sides[i] = color
            else:
                raise ValueError(f"Index {i} is out of bounds for sides array.")


class Program:
    def __init__(self, lights: Lights, camera: Camera):
        self.lights = lights
        self.camera = camera
        self.program = [
            {'name': 'Focus', 'type': TYPE.TOP, 'color': (250, 250, 250), 'action': ACTIONS.USER_INPUT},
            {'name': 'Stage 0', 'type': TYPE.TOP, 'color': (250, 250, 250), 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 1', 'type': TYPE.SIDES, 'color': (0, 0, 0, 250), 'ids': [0, 1, 2, 3], 'action': ACTIONS.CAPTURE},
        ]

    async def run(self):
        for stage in self.program:
            if stage['type'] == TYPE.TOP:
                self.lights.set_top(stage['color'])
            elif stage['type'] == TYPE.SIDES:
                self.lights.set_sides(stage['color'], stage.get('ids', []))
            if stage['action'] == ACTIONS.USER_INPUT:
                yield
            elif stage['action'] == ACTIONS.CAPTURE:
                self.camera.capture_image()
        self.lights.clear()
