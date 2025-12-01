import socket as s
import hashlib as h
import os

import cryptography.fernet as ctf
import pyinputplus as pyip


def main():
    password = None
    key = read_key("password_key.key")

    pin_code = pyip.inputRegex(r"\d{4}", prompt="PIN: ", limit=4).strip()

    for i in range(1, 50):
        try:
            ip_address = f"192.168.0.{i + 100}"
            print(f"Проверка ip: {ip_address}")

            is_errored = False
            with s.create_connection((ip_address, 8080)) as server:
                server.settimeout(10)

                server.send(h.sha512(pin_code.encode()).digest())
                message = server.recv(4096)

                if message == "i_pc":
                    is_errored = True

                if not is_errored and bool(key) and bool(message):
                    password = ctf.Fernet(key).decrypt(message).decode()

            print_password(password, is_errored)

        except ConnectionRefusedError | TimeoutError:
            if password is not None:
                return


def print_password(password, error):
    if password is not None:
        input("Нажмите ENTER для продолжения...")
        print(f"Ваш пароль: {password}")

    elif error:
        print("Неправильный PIN код!")


def read_key(filename: str):
    if os.path.exists(filename):
        with open(filename, "rb") as key_file:
            return key_file.read()

    raise FileNotFoundError("Key file is not found!")


if __name__ == "__main__":
    main()
