import socket as s
import hashlib as h

import cryptography.fernet as ctf
import pyinputplus as pyip


def main():
    password = None
    pin_code = pyip.inputRegex(r"\d{4}", prompt="PIN: ").strip()

    with s.create_connection(("192.168.0.100", 8080)) as server:
        server.settimeout(10)

        server.send(h.sha512(pin_code.encode()).digest())
        key = server.recv(4096)

        if key:
            message = server.recv(4096)
            password = ctf.Fernet(key).decrypt(message).decode()

    print_password(password)


def print_password(password):
    if password is not None:
        input("Нажмите ENTER для продолжения...")
        print(f"Ваш пароль: {password}")

    else:
        print("Неправильный PIN код!")


if __name__ == "__main__":
    main()


# vs9s!d8%h=nv-
