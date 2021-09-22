import socket
import chatlib

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


def build_and_send_message(conn, code, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Parameters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    msg = chatlib.build_message(code, data)
    conn.send(msg.encode())


def recv_message_and_parse(conn):
    """
    Receives a new message from given socket,
    then parses the message using chatlib.
    Parameters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occurred, will return None, None
    """
    full_msg = conn.recv(1024).decode()
    cmd, data = chatlib.parse_message(full_msg)
    return cmd, data


def build_send_recv_parse(conn, code, data):
    """
    Sends a request  to + Receives response from server
    Parameters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    build_and_send_message(conn, code, data)
    cmd, data = recv_message_and_parse(conn)
    print("cmd:\n{}".format(cmd))
    print("data:\n{}".format(data))


def get_score(conn):
    """
    Gets score from the server
    Gets high score from the server
    Returns: Nothing
    """
    build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["score_msg"], "")


def get_highscore(conn):
    """
    Gets high score from the server
    Parameters: conn (socket object)
    Returns: Nothing
    """
    build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["highscore_msg"], "")


def connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    return sock


def error_and_exit(error_msg):
    print(error_msg)
    exit()


def login(conn):
    username = input("Please enter username: \n")
    password = input("Please enter password: \n")
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], "{}#{}".format(username, password))
    login_response = recv_message_and_parse(conn)
    if login_response[0] == 'LOGIN_OK':
        print("Login successful")
    else:
        print("Login failed, please try again:")
        login(conn)


def logout(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")


def print_choices():
    print("s - Score")
    print("h - High score")
    print("q - Quit")


def main():
    conn = connect()
    login(conn)

    while True:
        print_choices()
        choice = input("Please enter your choice: ").lower()
        if choice == "s":
            get_score(conn)
        elif choice == "h":
            get_highscore(conn)
        elif choice == "q":
            break
        else:
            print("command {} not found".format(choice))

    logout(conn)
    conn.close()
    exit()


if __name__ == '__main__':
    main()
