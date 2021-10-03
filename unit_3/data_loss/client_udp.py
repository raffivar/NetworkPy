import random
import socket

SERVER_IP = "127.0.0.1"
PORT = 8821
MAX_MSG_SIZE = 1024
TIMEOUT_IN_SECONDS = 3


def special_sendto(socket_object, response, client_address):
    fail = random.randint(1, 3)
    if not (fail == 1):
        socket_object.sendto(response.encode(), client_address)
    else:
        print("Oops")


my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    msg = input("Message to server: ")
    special_sendto(my_socket, msg, (SERVER_IP, PORT))
    if msg.lower() == "exit":
        break
    my_socket.settimeout(TIMEOUT_IN_SECONDS)
    try:
        (response, remote_address) = my_socket.recvfrom(MAX_MSG_SIZE)
        data = response.decode()
        print("{}: {}".format(remote_address, data))
    except:
        print("This code reached despite server not answering")

my_socket.close()
