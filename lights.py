import board
import neopixel

import asyncio
import enum
import logging

from camera import Camera
from ikea_control import Ikea


class ACTIONS(enum.Enum):
    USER_INPUT = 'user_input'
    NO_ACTION = 'no_action'
    CAPTURE = 'capture'


class LIGHT_GROUPS(enum.Enum):
    TOP_RING = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    A_TOP = [16, 17, 18, 19]
    A_BOTTOM = [20, 21, 22, 23]
    B_TOP = [31, 30, 29, 28]
    B_BOTTOM = [24, 25, 26, 27]
    C_TOP = [32, 33, 34, 35]
    C_BOTTOM = [36, 37, 38, 39]
    D_TOP = [47, 46, 45, 44]
    D_BOTTOM = [40, 41, 42, 43]
    E_TOP = [48, 49, 50, 51]
    E_BOTTOM = [52, 53, 54, 55]
    F_TOP = [63, 62, 61, 60]
    F_BOTTOM = [56, 57, 58, 59]
    G_TOP = [64, 65, 66, 67]
    G_BOTTOM = [68, 69, 70, 71]
    H_TOP = [79, 78, 77, 76]
    H_BOTTOM = [72, 73, 74, 75]


class Lights:
    def __init__(self):
        self.sides = neopixel.NeoPixel(board.D10, 80, pixel_order=neopixel.RGBW)
        self.sides.fill((0, 0, 0, 0))  # Initialize all pixels

    def clear(self):
        self.sides.fill((0, 0, 0, 0))

    def set_sides(self, color, ids):
        for i in ids:
            if 0 <= i < len(self.sides):
                self.sides[i] = color
            else:
                raise ValueError(f"Index {i} is out of bounds for sides array.")


class BaseProgram:
    def __init__(self, lights: Lights, camera: Camera, ikea: Ikea):
        self.lights = lights
        self.camera = camera
        self.ikea = ikea
        self.stage = None  # Current stage of the program
        self.program = []

    async def reset(self):
        await self.ikea.change_light_state(False)
        self.lights.clear()
        self.stage = None

    async def step(self) -> int:
        stage_index = 0
        if self.stage is not None:
            self.lights.clear()
            stage_index = self.stage+1

        self.stage = stage_index
        try:
            stage = self.program[stage_index]
        except IndexError:
            self.stage = None
            self.lights.set_sides((0, 0, 0, 250), LIGHT_GROUPS.TOP_RING.value)
            return -2
        if 'color' in stage:
            self.lights.set_sides(stage['color'], stage.get('ids', []))

        if 'light' in stage:
            await self.ikea.change_light_state(stage['light'])
            await asyncio.sleep(1.5)

        if 'camera' in stage:
            for k in stage['camera']:
                self.camera.set_param(k, stage['camera'][k])

        if stage['action'] == ACTIONS.USER_INPUT:
            return -1
        elif stage['action'] == ACTIONS.CAPTURE:
            self.camera.capture_image()
        return 0

    async def top_ring(self, state: bool):
        if state:
            self.lights.set_sides((0, 0, 0, 250), LIGHT_GROUPS.TOP_RING.value)
        else:
            self.lights.set_sides((0, 0, 0, 0), LIGHT_GROUPS.TOP_RING.value)

    async def side_light(self, state: bool):
        if state:
            self.lights.set_sides((0, 0, 0, 250), LIGHT_GROUPS.C_BOTTOM.value)
        else:
            self.lights.set_sides((0, 0, 0, 0), LIGHT_GROUPS.C_BOTTOM.value)

    async def bottom_light(self, state: bool):
        await self.ikea.change_light_state(state)


class TopLightsProgram(BaseProgram):
    def __init__(self, lights, camera, ikea):
        super().__init__(lights, camera, ikea)
        self.program = [
            {'name': 'Focus', 'color': (0, 0, 0, 200), 'ids': LIGHT_GROUPS.TOP_RING.value, 'action': ACTIONS.USER_INPUT},
            {'name': 'Side', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.C_TOP.value, 'action': ACTIONS.USER_INPUT},
            {'name': 'Side', 'light': True, 'action': ACTIONS.USER_INPUT},
            {'name': 'Stage 0', 'light': False, 'color': (0, 0, 0, 200), 'ids': LIGHT_GROUPS.TOP_RING.value,  'action': ACTIONS.CAPTURE, 'camera': {
                'shutterspeed': '1.3', 'iso': '200', 'aperture': '7.1', 'whitebalance': 'Tungsten'}},
            {'name': 'Stage 1', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.C_TOP.value, 'action': ACTIONS.CAPTURE, 'camera': {
                'shutterspeed': '1.3', 'iso': '200', 'aperture': '7.1', 'whitebalance': 'Tungsten'}},
            {'name': 'Stage 2', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.B_TOP.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 3', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.A_TOP.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 4',  'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.H_TOP.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 5', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.G_TOP.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 6', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.F_TOP.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 7',  'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.E_TOP.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 8',  'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.D_TOP.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 9',  'light': True, 'action': ACTIONS.CAPTURE, 'camera': {
                'shutterspeed': '1/60', 'iso': '200', 'aperture': '7.1', 'whitebalance': 'Tungsten'}},
            {'name': 'Final',  'light': False, 'action': ACTIONS.NO_ACTION},
        ]


class BottomLightsProgram(BaseProgram):
    def __init__(self, lights, camera, ikea):
        super().__init__(lights, camera, ikea)
        self.program = [
            {'name': 'Stage 0', 'light': False, 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.TOP_RING.value,  'action': ACTIONS.CAPTURE, 'camera': {
                'shutterspeed': '2', 'iso': '200', 'aperture': '7.1', 'whitebalance': 'Tungsten'}},
            {'name': 'Stage 1', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.C_BOTTOM.value, 'action': ACTIONS.CAPTURE, 'camera': {
                'shutterspeed': '1.3', 'iso': '200', 'aperture': '7.1', 'whitebalance': 'Tungsten'}},
            {'name': 'Stage 2', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.B_BOTTOM.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 3', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.A_BOTTOM.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 4',  'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.H_BOTTOM.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 5', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.G_BOTTOM.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 6', 'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.F_BOTTOM.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 7',  'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.E_BOTTOM.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 8',  'color': (0, 0, 0, 250), 'ids': LIGHT_GROUPS.D_BOTTOM.value, 'action': ACTIONS.CAPTURE},
            {'name': 'Stage 9',  'light': True, 'action': ACTIONS.CAPTURE, 'camera': {
                'shutterspeed': '1/60', 'iso': '200', 'aperture': '7.1', 'whitebalance': 'Tungsten'}},
            {'name': 'Final',  'light': False, 'action': ACTIONS.NO_ACTION},
        ]
