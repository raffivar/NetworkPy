import random
import socket

SERIAL_NUMBER_FIELD_SIZE = 4
MAX_SERIAL_NUM = 10000

SERVER_IP = "0.0.0.0"
PORT = 8821
MAX_MSG_SIZE = 1024


def special_sendto(socket_object, response, client_address):
    fail = random.randint(1, 3)
    if not (fail == 1):
        socket_object.sendto(response.encode(), client_address)
    else:
        print("Oops")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, PORT))
request_serial_number = 0

while True:
    (client_message, client_address) = server_socket.recvfrom(MAX_MSG_SIZE)
    data = client_message.decode()
    if data.lower() == "exit":
        break
    response = "echo '{}'".format(data)
    special_sendto(server_socket, response, client_address)
    serial_number_field = str(request_serial_number).zfill(SERIAL_NUMBER_FIELD_SIZE)
    # Here is where you would enter code checking if the request already existed
    request_serial_number += 1
    if request_serial_number == MAX_SERIAL_NUM:
        request_serial_number = 0

server_socket.close()
