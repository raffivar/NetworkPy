import socket

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = "127.0.0.1"

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((SERVER_IP, SERVER_PORT))

while True:
    data = input("Please enter your message:\n")
    len_msg = len(data)
    my_socket.send(data.encode())
    if len_msg == 0:
        break
    data = my_socket.recv(MAX_MSG_LENGTH).decode()
    print("The server sent", data)
