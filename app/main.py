import argparse
import os
import socket
import threading
from enum import Enum

HOST = "localhost"
PORT = 4221


class Status(Enum):
    OK = "200 OK"
    NOT_FOUND = "404 Not Found"


class Server:
    slots = ("host", "port", "directory")

    def __init__(self, host: str, port: int, directory: str):
        self.host = host
        self.port = port
        self.directory = directory

    def run(self):
        with socket.create_server(
            (self.host, self.port), reuse_port=True
        ) as server_socket:
            while True:
                connection, _ = server_socket.accept()
                thread = threading.Thread(
                    target=self.handle_connection, args=(connection,)
                )
                thread.start()

    def handle_connection(self, connection: socket.socket):
        with connection:
            while True:
                data = connection.recv(4096).decode()
                if data is None or data == "":
                    break
                self.handle_request(connection, data)

    def handle_request(self, connection: socket.socket, data: str):
        headers, body = Server.get_headers_and_body(data)
        _, path, _ = Server.get_method_path_protocol(headers)
        if path.startswith("/echo/"):
            body_response = path[len("/echo/") :]
            headers_response = ["Content-Type: text/plain"]
            Server.response(connection, Status.OK, headers_response, body_response)
        elif path == "/user-agent":
            user_agent_header = [
                header for header in headers if header.startswith("User-Agent: ")
            ][0]
            body_response = user_agent_header[len("User-Agent: "):]
            headers_response = ["Content-Type: text/plain"]
            Server.response(connection, Status.OK, headers_response, body_response)
        elif path.startswith("/files/"):
            file_path = os.path.join(self.directory, path[len("/files/"):])
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "rb") as file:
                    body_response = file.read().decode()
                    headers_response = ["Content-Type: application/octet-stream"]
                    Server.response(
                        connection, Status.OK, headers_response, body_response
                    )
            else:
                Server.response(connection, Status.NOT_FOUND, [], "")
        elif path == "/":
            Server.response(connection, Status.OK, [], "")
        else:
            Server.response(connection, Status.NOT_FOUND, [], "")

    @staticmethod
    def get_headers_and_body(data: str) -> (list[str], str):
        header_body = data.split("\r\n\r\n")
        if len(header_body) != 2:
            raise ValueError("Invalid request")
        header, body = header_body
        headers = header.split("\r\n")
        return headers, body

    @staticmethod
    def get_method_path_protocol(headers: list[str]) -> (str, str, str):
        if len(headers) == 0:
            raise ValueError("Invalid request")
        result = headers[0].split(" ")
        if len(result) != 3:
            raise ValueError("Invalid request")

        return result

    @staticmethod
    def response(
        connection: socket.socket, status: Status, headers: list[str], body: str
    ):
        str_builder = [f"HTTP/1.1 {status.value}"]
        for header in headers:
            str_builder.append(header)
        str_builder.append(f"Content-Length: {len(body.encode())}")
        str_builder.append(f"\r\n{body}")
        message = "\r\n".join(str_builder)
        connection.sendall(message.encode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default="")
    args = parser.parse_args()
    server = Server(HOST, PORT, args.directory)
    server.run()


if __name__ == "__main__":
    main()
