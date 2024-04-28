from hardware.hardware import Hardware
from resources.constants import EMULATE_HARDWARE
from server.server import start_server
from utils.network import get_ip


def main():
    own_ip = get_ip()
    hardware = Hardware(own_ip)
    app = start_server(hardware, own_ip)
    app.run(host='0.0.0.0', port=8000, debug=EMULATE_HARDWARE)


if __name__ == "__main__":
    main()
