from typing import List, Dict

import pydantic

from model.device import Device


class Mesh(pydantic.BaseModel):
    devices: Dict[str, Device]

    def add_device(self, id):
        self.devices[id] = Device(
            on=len(self.devices) == 0,
            turn_order=len(self.devices)
        )

    def remove_device(self, id):
        del self.devices[id]


    def get_by_id(self, id: str) -> Device:
        return self.devices[id]

    def get_by_turn(self, turn: int) -> Device:
        for device in self.devices.values():
            if device.turn_order == turn:
                return device

    def get_next_device(self, turn: int, skip_passed: bool = False) -> Device:
        next_turn = (turn + 1) % len(self.devices)
        while next_turn != turn:
            device = self.get_by_turn(next_turn)
            if not skip_passed or not device.passed:
                return device

    def get_previous_device(self, turn: int, skip_passed: bool = False) -> Device:
        next_turn = (turn - 1) % len(self.devices)
        while next_turn != turn:
            device = self.get_by_turn(next_turn)
            if not skip_passed or not device.passed:
                return device

    def end_turn(self):
        for device in self.devices.values():
            if device.on:
                device.on = False
                self.get_next_device(device.turn_order, skip_passed=True).on = True

    def pass_turn(self, turn: int):
        device = self.get_by_turn(turn)
        device.passed = True
        if all(device.passed for device in self.devices.values()):
            for device in self.devices.values():
                device.passed = True
                if device.turn_order == 0:
                    device.on = True
        elif device.on:
            self.end_turn()

    def increment_turn(self, turn: int):
        device = self.get_by_turn(turn)
        next_device = self.get_next_device(turn, skip_passed=False)
        device.turn_order += 1
        next_device.turn_order -= 1
        device.on, next_device.on = next_device.on, device.on

    def decrement_turn(self, turn: int):
        device = self.get_by_turn(turn)
        next_device = self.get_previous_device(turn, skip_passed=False)
        device.turn_order -= 1
        next_device.turn_order += 1
        device.on, next_device.on = next_device.on, device.on
