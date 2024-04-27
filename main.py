from hardware.hardware import Hardware
from server.server import start_server


def main():
    hardware = Hardware()
    app = start_server(hardware)
    app.run(host='0.0.0.0', port=8000, debug=True)


if __name__ == "__main__":
    main()
