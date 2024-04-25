import socket

HOST = "localhost"
PORT = 4221


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        connection, address = server_socket.accept()
        request_data = connection.recv(1024)
        lines = request_data.decode().split("\r\n")
        header = lines[0]
        path = header.split(" ")[1]
        if path == "/":
            connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        else:
            connection.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
        connection.close()


if __name__ == "__main__":
    main()
