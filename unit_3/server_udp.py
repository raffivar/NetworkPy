import socket

SERVER_IP = "0.0.0.0"
PORT = 8821
MAX_MSG_SIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, PORT))
(client_message, client_address) = server_socket.recvfrom(MAX_MSG_SIZE)
data = client_message.decode()
response = "Super{}".format(data)
server_socket.sendto(response.encode(), client_address)
server_socket.close()
