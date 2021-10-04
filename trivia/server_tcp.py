##############################################################################
# server.py
##############################################################################
import select
import socket
import chatlib

# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later

MAX_MSG_LENGTH = 1024
ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
    full_msg = chatlib.build_message(code, msg)
    print("[SERVER] ", full_msg)  # Debug print
    conn.send(full_msg.encode())


def recv_message_and_parse(conn):
    full_msg = conn.recv(1024).decode()
    cmd, data = chatlib.parse_message(full_msg)
    print("[CLIENT] ", full_msg)  # Debug print
    return cmd, data


# DATA LOADERS #

def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    questions = {
        2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2},
        4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
               "correct": 3}
    }

    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    users = {
        "test": {"password": "test", "score": 0, "questions_asked": []},
        "yossi": {"password": "123", "score": 50, "questions_asked": []},
        "master": {"password": "master", "score": 200, "questions_asked": []}
    }
    return users


# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """
    print("Setting up server...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen()
    print("Listening to clients...")
    return sock


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], error_msg)


##### MESSAGE HANDLING


def handle_getscore_message(conn, username):
    global users


# Implement this in later chapters


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users
    print("{} has been disconnected".format(conn))
    conn.close()


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users  # To be used later

    username = data[0]
    password = data[1]

    if username not in users:
        send_error(conn, "User does not exist")
        return

    user = users[username]
    if password != user["password"]:
        send_error(conn, "Incorrect password")
        return

    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"], "Login successful!")


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users  # To be used later

    if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
        handle_login_message(conn, data)


def print_client_sockets(client_sockets):
    for cs in client_sockets:
        print("\t", cs.getpeername())


def main():
    # Initializes global users and questions dicionaries using load functions, will be used later
    global users
    global questions

    print("Welcome to Trivia Server!")
    server_socket = setup_socket()
    client_sockets = []
    messages_to_send = []

    while True:
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                (client_socket, client_address) = current_socket.accept()
                print("New client joined!", client_address)
                client_sockets.append(client_socket)
                print_client_sockets(client_sockets)
            else:
                try:
                    cmd, data = recv_message_and_parse(current_socket)
                    if cmd == "":
                        print("Connection closed (on purpose)")
                        client_sockets.remove(current_socket)
                        handle_logout_message(current_socket)
                        print_client_sockets(client_sockets)
                    else:
                        print(cmd, data)
                        handle_client_message(current_socket, cmd, data)
                        # messages_to_send.append((current_socket, data))
                        # for message in messages_to_send:
                        #     current_socket, data = message
                        #     if current_socket in ready_to_write:
                        #         current_socket.send(data.encode())
                        #         messages_to_send.remove(message)
                except Exception as e:
                    print("Connection closed (due to exception {}".format(e))
                    client_sockets.remove(current_socket)
                    handle_logout_message(current_socket)
                    print_client_sockets(client_sockets)


if __name__ == '__main__':
    main()
