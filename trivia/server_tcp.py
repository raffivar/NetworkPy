##############################################################################
# server.py
##############################################################################
import select
import socket
import random

import chatlib

# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
client_sockets = []
messages_to_send = []

MAX_MSG_LENGTH = 1024
ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
    full_msg = chatlib.build_message(code, msg)
    messages_to_send.append((conn, full_msg))  # add to messages_to_send
    # print("[SERVER] ", full_msg)  # Debug print -> Moved to "send_all_saves_messages"


def recv_message_and_parse(conn):
    full_msg = conn.recv(1024).decode()
    cmd, data = chatlib.parse_message(full_msg)
    print("[CLIENT] ", full_msg)  # Debug print
    return cmd, data


def send_saved_messages(ready_to_write):
    global messages_to_send
    for message in messages_to_send:
        current_socket, data = message
        if current_socket in ready_to_write:
            print("[SERVER] ", data)  # Debug print
            current_socket.send(data.encode())
            messages_to_send.remove(message)


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

def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global client_sockets
    client_sockets.remove(conn)
    global logged_users
    logged_users.pop(conn.getpeername())
    conn.close()
    print("{} has disconnected".format(conn))


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

    logged_users[conn.getpeername()] = username
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"], "Login successful!")


def handle_getscore_message(conn, username):
    global users

    if username not in users:
        send_error(conn, "User does not exist")
        return

    user = users[username]
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["your_score_msg"], str(user["score"]))


def handle_highscore_message(conn):
    global users

    high_score_list = []
    for username in users:
        name = username
        score = users[username]["score"]
        high_score_list.append((name, score))

    high_score_list.sort(key=lambda user: user[1], reverse=True)
    high_score_string = '\n'.join("\t{}: {}".format(user[0], str(user[1])) for user in high_score_list)
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["all_score_msg"], high_score_string)


def handle_logged_message(conn):
    global logged_users
    high_score_string = '\n'.join("\t{}".format(logged_users[user]) for user in logged_users)
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["logged_answer_msg"], high_score_string)


def create_random_question():
    global questions
    if len(questions) == 0:
        return None
    random_question = random.choice(list(questions.items()))
    question_id = random_question[0]
    question_txt = random_question[1]["question"]
    question_possible_answers = random_question[1]["answers"]
    question = list()
    question.append(str(question_id))
    question.append(question_txt)
    question += question_possible_answers
    return chatlib.join_data(question)


def handle_question_message(conn):
    question = create_random_question()
    if question is None:
        send_error(conn, "No more questions")
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["your_question_msg"], question)


def handle_answer_message(conn, data):
    question_id = int(data[0])
    user_answer = int(data[1])

    if question_id not in questions.keys():
        send_error(conn, "Question no longer exists")
        return

    question = questions[question_id]
    correct_answer = question["correct"]

    if user_answer == correct_answer:
        username = logged_users[conn.getpeername()]
        user = users[username]
        user["score"] += 5
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["correct_answer_msg"], "")
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["wrong_answer_msg"], str(correct_answer))


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users  # To be used later

    if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
        handle_login_message(conn, data)
        return

    if conn.getpeername() not in logged_users:
        send_error(conn, "You're not logged in, buddy")
        return

    if cmd == chatlib.PROTOCOL_CLIENT["score_msg"]:
        handle_getscore_message(conn, logged_users[conn.getpeername()])
        return
    if cmd == chatlib.PROTOCOL_CLIENT["highscore_msg"]:
        handle_highscore_message(conn)
        return

    if cmd == chatlib.PROTOCOL_CLIENT["logged_msg"]:
        handle_logged_message(conn)
        return

    if cmd == chatlib.PROTOCOL_CLIENT["play_question_msg"]:
        handle_question_message(conn)
        return

    if cmd == chatlib.PROTOCOL_CLIENT["send_answer_msg"]:
        handle_answer_message(conn, data)
        return


def print_client_sockets(client_sockets):
    print("All connected sockets:")
    if len(client_sockets) == 0:
        print("\t<No sockets connected>")
    for cs in client_sockets:
        print("\t", cs.getpeername())


def main():
    # Initializes global users and questions dicionaries using load functions, will be used later
    global client_sockets
    global messages_to_send
    global users
    global questions
    users = load_user_database()
    questions = load_questions()

    print("Welcome to Trivia Server!")
    server_socket = setup_socket()

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
                    if cmd is None:
                        print("Connection closed (on purpose)")
                        handle_logout_message(current_socket)
                        print_client_sockets(client_sockets)
                    else:
                        handle_client_message(current_socket, cmd, data)
                        send_saved_messages(ready_to_write)
                except Exception as e:
                    print("Connection closed (due to exception - {})".format(e))
                    handle_logout_message(current_socket)
                    print_client_sockets(client_sockets)


if __name__ == '__main__':
    main()
