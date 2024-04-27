from server.server import start_server


def main():
    app = start_server()
    app.run(host='0.0.0.0', port=8000, debug=True)


if __name__ == "__main__":
    main()
