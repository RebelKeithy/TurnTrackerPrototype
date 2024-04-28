import requests
from gpiozero import Button, LED
from model.device import Device
from resources.constants import EMULATE_HARDWARE


class Hardware:
    def __init__(self, server_ip):
        self.device: Device = None
        if not EMULATE_HARDWARE:
            self.led_turn = LED(17)
            self.button_end_turn = Button(2)
            self.button_end_turn.when_pressed = self.next_turn
        self.server_ip = server_ip

    def set_server_ip(self, server_ip):
        self.server_ip = server_ip

    def next_turn(self):
        if self.device.on:
            self.device.on = False
            if not EMULATE_HARDWARE:
                self.led_turn.off()
            if self.server_ip:
                requests.post(f'http://{self.server_ip}:8000/end_turn')

    def set_hardware_state(self, in_device: Device):
        self.device = in_device
        if EMULATE_HARDWARE:
            return
        if self.device.on:
            self.led_turn.on()
        else:
            self.led_turn.off()

