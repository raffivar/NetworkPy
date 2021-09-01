import chatlib


def main():
    print(chatlib.build_message("LOGIN", "user#pass"))
    print(chatlib.parse_message("LOGIN           |  -8|use#pass"))


if __name__ == '__main__':
    main()

