from typing import Optional

import requests
from flask import Flask, request

from hardware.hardware import Hardware
from model.device import Device
from model.mesh import Mesh


class AppServer(Flask):
    def __init__(self, import_name: str, hardware: Hardware, own_ip: str, mesh: Optional[Mesh]) -> None:
        super().__init__(import_name)
        self.hardware = hardware
        self.own_ip: str = own_ip
        self.mesh: Mesh = mesh or Mesh(
            devices=[
                Device(
                    ip=own_ip,
                    on=True,
                )
            ]
        )


def start_server(hardware: Hardware, own_ip: str, mesh: Optional[Mesh] = None):
    app = AppServer('TurnTrackerServer', hardware, own_ip, mesh)

    @app.route('/')
    def root():
        print(request.remote_addr)
        return "Hello World!"

    @app.route('/join', methods=['POST'])
    def join():
        print("/join")
        if app.mesh.get_by_ip(request.remote_addr) is None:
            app.mesh.devices.append(
                Device(
                    ip = request.remote_addr,
                    turn_order=len(app.mesh.devices)
                )
            )
            update_clients()
        print(f'{app.mesh=}')
        return {
            'data': app.mesh.model_dump_json()
        }

    @app.route('/end_turn', methods=['POST'])
    def end_turn():
        if app.mesh is None:
            print("error: Mesh is not setup yet")
            return "error: Mesh is not setup yet"

        device = app.mesh.get_by_ip(request.remote_addr)
        if device is None:
            print("error: Device is not connected")
            return "error: Device is not connected"

        device.on = False
        next_device_updated = False
        index = device.turn_order
        while not next_device_updated:
            index = (index + 1) % len(app.mesh.devices)
            next_device = app.mesh.get_by_turn(index)
            if next_device is None:
                print("error: Could not get next device")
                return "error: Could not get next device"
            if not next_device.passed:
                next_device.on = True
                next_device_updated = True
        print(f'{app.mesh=}')
        update_clients()
        return 'Success', 200

    @app.route('/increment_turn_order', methods=['POST'])
    def increment_turn_order():
        device = app.mesh.get_by_ip(request.remote_addr)
        next_device = app.mesh.get_by_turn((device.turn_order + 1) % len(app.mesh.devices))
        (device.turn_order, next_device.turn_order) = (next_device.turn_order, next_device.turn_order)
        (device.on, next_device.on) = (next_device.on, next_device.on)
        print(f'{app.mesh=}')
        update_clients()
        return 'Success', 200

    @app.route('/decrement_turn_order', methods=['POST'])
    def decrement_turn_order():
        device = app.mesh.get_by_ip(request.remote_addr)
        next_device = app.mesh.get_by_turn((device.turn_order - 1) % len(app.mesh.devices))
        (device.turn_order, next_device.turn_order) = (next_device.turn_order, next_device.turn_order)
        (device.on, next_device.on) = (next_device.on, next_device.on)
        print(f'{app.mesh=}')
        update_clients()
        return 'Success', 200

    @app.route('/pass', methods=['POST'])
    def pass_turn():
        device = app.mesh.get_by_ip(request.remote_addr)
        device.passed = True
        device.on = False
        next_device_updated = False
        index = device.turn_order
        while not next_device_updated:
            index = (index + 1) % len(app.mesh.devices)
            if index == device.turn_order:
                for device in app.mesh.devices:
                    device.passed = False
                app.mesh.get_by_turn(0).on = True
            next_device = app.mesh.get_by_turn(index)
            if next_device is None:
                print("error: Could not get next device")
                return "error: Could not get next device"
            if not next_device.passed:
                next_device.on = True
                next_device_updated = True
        print(f'{app.mesh=}')
        update_clients()
        return 'Success', 200

    @app.route('/mesh', methods=['POST'])
    def set_mesh():
        if app.own_ip is None:
            app.own_ip = request.host.split(':')[0]
        app.mesh = Mesh.model_validate_json(request.data.decode())
        if app.hardware:
            app.hardware.set_hardware_state(app.mesh.get_by_ip(app.own_ip))
        print('Mesh Updated')
        print(f'{app.mesh=}')
        return 'Success', 200

    def update_clients(excluded_ip=[]):
        if app.hardware:
            app.hardware.set_hardware_state(app.mesh.get_by_ip(app.own_ip))
        for device in app.mesh.devices:
            if device.ip != request.remote_addr and device.ip not in excluded_ip and device.ip != own_ip:
                requests.post(f'http://{device.ip}:8000/mesh', data=app.mesh.model_dump_json())

    return app

