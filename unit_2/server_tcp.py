import random
import socket
from datetime import datetime

COMMAND_NAME = "NAME"
COMMAND_TIME = "TIME"
COMMAND_RAND = "RAND"

SERVER_NAME = "Raffi\'s Server"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 8820))
server_socket.listen()
print("Server is up and running")
(client_socket, client_address) = server_socket.accept()
print("Client connected")
data = ""
while True:
    data = client_socket.recv(1024).decode()
    print("Client sent: " + data)
    if data == COMMAND_NAME:
        data = SERVER_NAME
    elif data == COMMAND_TIME:
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    elif data == COMMAND_RAND:
        # Includes both ends (1 and 10!!)
        data = str(random.randint(1, 10))
    elif data == "Bye":
        data = " "
    elif data == "Quit":
        print("closing client socket now...")
        client_socket.send("Bye".encode())
        break
    else:
        data = "Command <{}> unknown".format(data)
    client_socket.send(data.encode())

client_socket.close()
server_socket.close()
