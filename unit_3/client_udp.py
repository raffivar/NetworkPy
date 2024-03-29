import socket

SERVER_IP = "127.0.0.1"
PORT = 8821
MAX_MSG_SIZE = 1024

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    msg = input("Message to server: ")
    my_socket.sendto(msg.encode(), (SERVER_IP, PORT))
    if msg.lower() == "exit":
        break
    (response, remote_address) = my_socket.recvfrom(MAX_MSG_SIZE)
    data = response.decode()
    print("{}: {}".format(remote_address, data))

my_socket.close()
