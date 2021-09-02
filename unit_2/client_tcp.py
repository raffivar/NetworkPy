import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect(("127.0.0.1", 8820))
my_socket.send("hello".encode())
data = my_socket.recv(1024).decode()
print("The server sent " + data)
my_socket.close()
