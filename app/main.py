import socket

HOST = "localhost"
PORT = 4221


class Server:
    slots = ("host", "port")

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def run(self):
        with socket.create_server(
            (self.host, self.port), reuse_port=True
        ) as server_socket:
            while True:
                connection, address = server_socket.accept()
                with connection:
                    while True:
                        data = connection.recv(1024).decode()
                        if data is None or data == "":
                            break
                        path = data.split("\r\n")[0].split(" ")[1]
                        if path.startswith("/echo/"):
                            message = path[6:]
                            print(f"Received message: {message}")
                            connection.sendall(
                                b"HTTP/1.1 200 OK\r\n"
                                + b"Content-Type: text/plain\r\n"
                                + b"Content-Length: "
                                + str(len(message.encode())).encode()
                                + b"\r\n\r\n"
                                + message.encode()
                            )
                        elif path == "/":
                            connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
                        else:
                            connection.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


def main():
    server = Server(HOST, PORT)
    server.run()


if __name__ == "__main__":
    main()
