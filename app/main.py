import socket
from enum import Enum

HOST = "localhost"
PORT = 4221


class Status(Enum):
    OK = "200 OK"
    NOT_FOUND = "404 Not Found"


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
                        data = connection.recv(4096).decode()
                        if data is None or data == "":
                            break
                        Server.handle_request(connection, data)

    @staticmethod
    def handle_request(connection: socket.socket, data: str):
        headers, body = Server.get_headers_and_body(data)
        _, path, _ = Server.get_method_path_protocol(headers)
        if path.startswith("/echo/"):
            body_response = path[len("/echo/"):]
            headers_response = ["Content-Type: text/plain"]
            Server.response(connection, Status.OK, headers_response, body_response)
        elif path == "/user-agent":
            user_agent_header = [header for header in headers if header.startswith("User-Agent: ")][0]
            body_response = user_agent_header[len("User-Agent: "):]
            headers_response = ["Content-Type: text/plain"]
            Server.response(connection, Status.OK, headers_response, body_response)
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
    def response(connection: socket.socket, status: Status, headers: list[str], body: str):
        str_builder = [f"HTTP/1.1 {status.value}"]
        for header in headers:
            str_builder.append(header)
        str_builder.append(f"Content-Length: {len(body.encode())}")
        str_builder.append(f"\r\n{body}")
        connection.sendall("\r\n".join(str_builder).encode())

def main():
    server = Server(HOST, PORT)
    server.run()


if __name__ == "__main__":
    main()
