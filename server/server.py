import json

import requests
from flask import Flask, request

from hardware.hardware import Hardware
from model.device import Device
from model.mesh import Mesh

hardware = Hardware()
own_ip: str = None
mesh: Mesh = None

def start_server():
    app = Flask('TurnTrackerServer')

    @app.route('/')
    def root():
        print(request.remote_addr)
        return "Hello World!"

    @app.route('/join', methods=['POST'])
    def join():
        global mesh
        if mesh is None:
            own_ip = request.host.split(':')[0]
            mesh = Mesh(
                devices=[
                    Device(
                        ip = own_ip,
                        on = True,
                    )
                ]
            )
        mesh.devices.append(
            Device(
                ip = request.remote_addr,
                turn_order=len(mesh.devices)
            )
        )
        update_clients()

    @app.route('/end_turn', methods=['POST'])
    def end_turn():
        global mesh
        if mesh is None:
            print("error: Mesh is not setup yet")
            return "error: Mesh is not setup yet"

        device = mesh.get_by_ip(request.remote_addr)
        if device is None:
            print("error: Device is not connected")
            return "error: Device is not connected"

        device.on = False
        next_device_updated = False
        index = device.turn_order
        while not next_device_updated:
            index = (index + 1) % len(mesh.devices)
            next_device = mesh.get_by_turn(index)
            if next_device is None:
                print("error: Could not get next device")
                return "error: Could not get next device"
            if not next_device.passed:
                next_device.on = True
                next_device_updated = True
        update_clients()

    @app.route('/increment_turn_order', methods=['POST'])
    def increment_turn_order():
        global mesh
        device = mesh.get_by_ip(request.remote_addr)
        next_device = mesh.get_by_turn((device.turn_order + 1) % len(mesh.devices))
        (device.turn_order, next_device.turn_order) = (next_device.turn_order, next_device.turn_order)
        (device.on, next_device.on) = (next_device.on, next_device.on)
        update_clients()

    @app.route('/decrement_turn_order', methods=['POST'])
    def decrement_turn_order():
        global mesh
        device = mesh.get_by_ip(request.remote_addr)
        next_device = mesh.get_by_turn((device.turn_order - 1) % len(mesh.devices))
        (device.turn_order, next_device.turn_order) = (next_device.turn_order, next_device.turn_order)
        (device.on, next_device.on) = (next_device.on, next_device.on)
        update_clients()

    @app.route('/pass', methods=['POST'])
    def pass_turn():
        global mesh
        device = mesh.get_by_ip(request.remote_addr)
        device.passed = True
        device.on = False
        next_device_updated = False
        index = device.turn_order
        while not next_device_updated:
            index = (index + 1) % len(mesh.devices)
            if index == device.turn_order:
                for device in mesh.devices:
                    device.passed = False
                mesh.get_by_turn(0).on = True
            next_device = mesh.get_by_turn(index)
            if next_device is None:
                print("error: Could not get next device")
                return "error: Could not get next device"
            if not next_device.passed:
                next_device.on = True
                next_device_updated = True
        update_clients()

    @app.route('/mesh', methods=['POST'])
    def set_mesh():
        global mesh, own_ip
        if own_ip is None:
            own_ip = request.host.split(':')[0]
        mesh = Mesh.model_validate_json(request.data.decode())
        hardware.set_hardware_state(mesh.get_by_ip(own_ip))
        print('Mesh Updated')
        print(f'{mesh=}')

    def update_clients():
        hardware.set_hardware_state(mesh.get_by_ip(own_ip))
        for device in mesh.devices:
            if device.ip != request.remote_addr:
                requests.post(f'http://{device.ip}/mesh', data=mesh.model_dump_json())

    return app

