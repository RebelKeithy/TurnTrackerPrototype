import socketio

from hardware.hardware import Hardware
from model.device import Device
from model.mesh import Mesh

hardware = Hardware(0)
mesh: Mesh = Mesh(devices=[])
sio = socketio.Client()


hardware.button_callback(lambda: sio.emit('end_turn'))


def start():
    sio.connect('http://192.168.1.108:5000', namespaces=['/'])
    sio.wait()


@sio.event
def connect():
    print('[INFO] Successfully connected to server.')


@sio.event
def connect_error():
    print('[INFO] Failed to connect to server.')


@sio.on('device_update')
def device_update(message):
    print(message)
    device = Device.parse_obj(message)
    hardware.set_hardware_state(device)

