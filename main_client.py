import argparse
import requests
from threading import Thread
from server import server
import time

def main():
    # get server ip from args
    parser = argparse.ArgumentParser()
    parser.add_argument("server_ip", help="Enter the server IP")
    args = parser.parse_args()

    app = server.start_server()
    thread = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8000, 'debug': True})
    thread.start()
    time.sleep(1)

    requests.post(f"http://{args.server_ip}:8000/join")

    thread.join()


if __name__ == '__main__':
    main()
