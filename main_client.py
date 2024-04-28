import argparse
import requests

from hardware.hardware import Hardware
from model.mesh import Mesh
from resources.constants import EMULATE_HARDWARE
from server import server

from utils.network import get_ip


def main():
    # get server ip from args
    parser = argparse.ArgumentParser()
    parser.add_argument("server_ip", help="Enter the server IP")
    args = parser.parse_args()

    hardware = Hardware(args.server_ip)
    own_ip = get_ip()
    print(f"http://{args.server_ip}:8000/join")
    response = requests.post(f"http://{args.server_ip}:8000/join")
    response.raise_for_status()
    data = response.json()['data']
    mesh = Mesh.model_validate_json(data)
    app = server.start_server(hardware, own_ip, mesh)
    app.run(host='0.0.0.0', port=8000, debug=EMULATE_HARDWARE)


if __name__ == '__main__':
    main()
