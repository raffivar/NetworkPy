import socket

SERVER_IP = "127.0.0.1"
PORT = 8821
MAX_MSG_SIZE = 1024

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.sendto("geeks".encode(), (SERVER_IP, PORT))
(response, remote_address) = my_socket.recvfrom(MAX_MSG_SIZE)
data = response.decode()
print("[{}]:\n{}\n".format(remote_address, data))
my_socket.close()
