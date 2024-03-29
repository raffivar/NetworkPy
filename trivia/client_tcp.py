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
    return recv_message_and_parse(conn)


def play_question(conn):
    """
    Gets question from server
    Gets high score from the server
    Returns: Nothing
    """
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["play_question_msg"], "")
    if data is None:
        print("No more questions left for you")
        return
    question_code = data[0]
    question = data[1]
    print("Q: {}:".format(question))
    print("\t1. {}\n\t2. {}\n\t3. {}\n\t4. {}".format(data[2], data[3], data[4], data[5]))
    answer_code = input("Please choose an answer [1-4]: ")
    while answer_code not in ['1', '2', '3', '4']:
        answer_code = input("Invalid answer, please try again [1-4]: ")
    data_to_send = chatlib.join_data([question_code, answer_code])
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["send_answer_msg"], data_to_send)
    if cmd == chatlib.PROTOCOL_SERVER["error_msg"]:
        print(data[0])
    if cmd == chatlib.PROTOCOL_SERVER["correct_answer_msg"]:
        print("YES!!!!")
    elif cmd == chatlib.PROTOCOL_SERVER["wrong_answer_msg"]:
        correct_answer = data[0]
        print("Nope, correct answer is #{}".format(correct_answer))


def get_logged_users(conn):
    """
    Gets list oc connected users from the server
    Parameters: conn (socket object)
    Returns: Nothing
    """
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["logged_msg"], "")
    logged_users = data[0]
    print("Logged users:\n{}".format(logged_users))


def get_score(conn):
    """
    Gets score from the server
    Parameters: conn (socket object)
    Returns: Nothing
    """
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["score_msg"], "")
    score = data[0]
    print("your score is: {}".format(score))


def get_highscore(conn):
    """
    Gets high score from the server
    Parameters: conn (socket object)
    Returns: Nothing
    """
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["highscore_msg"], "")
    highscore = data[0]
    print("High-Score:\n{}".format(highscore))


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
    data_to_send = chatlib.join_data([username, password])
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], data_to_send)
    cmd, data = recv_message_and_parse(conn)
    if cmd == 'LOGIN_OK':
        print("Logged in!")
    else:
        print("Login failed [{}] - please try again:".format(data[0]))
        login(conn)


def logout(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")


def print_choices():
    print("p\t\tPlay a trivia question")
    print("s\t\tScore")
    print("h\t\tHigh score")
    print("l\t\tGet logged users")
    print("q\t\tQuit")


def main():
    conn = connect()
    login(conn)

    while True:
        print_choices()
        choice = input("Please enter your choice: ").lower()
        if choice == "p":
            play_question(conn)
        elif choice == "s":
            get_score(conn)
        elif choice == "h":
            get_highscore(conn)
        elif choice == "l":
            get_logged_users(conn)
        elif choice == "q":
            logout(conn)
            break
        else:
            print("command {} not found".format(choice))

    exit()


if __name__ == '__main__':
    main()
