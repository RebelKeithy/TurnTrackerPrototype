import argparse
import requests

from hardware.hardware import Hardware
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
    requests.post(f"http://{args.server_ip}:8000/join")
    app = server.start_server(hardware, own_ip)
    app.run(host='0.0.0.0', port=8000, debug=True)


if __name__ == '__main__':
    main()
