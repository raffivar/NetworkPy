# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages 
# In this dictionary we will have all the client and server command names
PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT"
}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR"
}  # ..  Add more commands if needed

# Other constants
ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
    """
    Gets command name (str) and data field (str) and creates a valid protocol message
    Returns: str, or None if error occured
    """
    if not 0 < len(cmd) <= CMD_FIELD_LENGTH:
        return None
    padded_cmd = "{}{}".format(cmd, ' ' * (CMD_FIELD_LENGTH - len(cmd)))
    content_len = len(data)
    if content_len > MAX_DATA_LENGTH:
        return None
    data_len_as_str = str(content_len)
    padded_data_len = "{}{}".format('0' * (LENGTH_FIELD_LENGTH - len(data_len_as_str)), data_len_as_str)
    return "{}{}{}{}{}".format(padded_cmd, DELIMITER, padded_data_len, DELIMITER, data)


def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    parsed_data = data.split(DELIMITER)
    if len(parsed_data) != 3:
        return None, None
    cmd = parsed_data[0].strip()
    data_len_as_str = parsed_data[1].strip()
    if not data_len_as_str.isnumeric():
        return None, None
    expected_content_len = int(parsed_data[1])
    if not 0 < expected_content_len < MAX_DATA_LENGTH:
        return None, None
    content = parsed_data[2]
    if len(content) != expected_content_len:
        return None, None
    return cmd, content


def split_data(msg, expected_fields):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's data field delimiter (|#) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    res = msg.split(DATA_DELIMITER)
    num_of_hashtags = msg.count(DATA_DELIMITER)
    return res if num_of_hashtags == expected_fields else None


def join_data(msg_fields):
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter.
    Returns: string that looks like cell1#cell2#cell3
    """
    return DELIMITER.join(msg_fields)
