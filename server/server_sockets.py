from flask import Flask, request
from flask_socketio import SocketIO, emit, send

from model.mesh import Mesh

mesh: Mesh = Mesh(devices={})
app = Flask('TurnTrackerPrototypeSockets')
socketio = SocketIO(app)


def start():
    socketio.run(app, host='0.0.0.0', port=5000)


@socketio.on('connect')
def connect(auth):
    print(request)
    mesh.add_device(request.sid)

    emit('device_update', mesh.get_by_id(request.sid).model_dump())


@socketio.on('disconnect')
def disconnect():
    mesh.remove_device(request.sid)


@socketio.on('end_turn')
def end_turn(message):
    if mesh.get_by_ip(request.sid).on:
        mesh.end_turn()
    for id, device in mesh.devices.items():
        send('device_update', device.model_dump(), to=id)
