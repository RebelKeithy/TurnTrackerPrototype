import socketio

from hardware.hardware import Hardware
from model.device import Device

sio = socketio.Client()


hardware = Hardware(0)
hardware.button_callback(lambda: sio.emit('end_turn'))


def start():
    sio.connect('http://192.168.1.108:5000', namespaces=['/'])
    sio.wait()


@sio.event
def connect():
    print('[INFO] Successfully connected to server.')


@sio.event
def connect_error(message):
    print(f'[INFO] Failed to connect to server. {message=}')


@sio.on('device_update')
def device_update(message):
    print(message)
    device = Device.parse_obj(message)
    hardware.set_hardware_state(device)

