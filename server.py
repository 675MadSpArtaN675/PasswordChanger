import password_changer as pc

import os, sys, re
import argparse as ap
import random as r
import string as s
import socket as st
import hashlib as h
import time as t

import cryptography.fernet as ctf
import dotenv as de

de.load_dotenv()


class PasswordGenerator:
    __need_symbols: bool
    __keywords_list: list[str]

    def __init__(self, is_symbols_need: bool, keywords: list[str]):
        self.__keywords_list = keywords
        self.__need_symbols = is_symbols_need

    def readKey(self, filename: str):
        if os.path.exists(filename):
            with open(filename, "rb") as key_file:
                return key_file.read()

        raise FileNotFoundError("Key file not found!")

    def generateKey(self, filename: str):
        if not os.path.exists(filename):
            key = ctf.Fernet.generate_key()

            with open(filename, "wb") as key_file:
                key_file.write(key)

    def generate_password(self, password_len: int):
        if password_len < 8:
            raise Exception("Пароль должен быть 8 и больше символов!")

        chars = list(
            s.ascii_letters
            + s.digits
            + ("!@#$:;%^&*-_=+" if self.__need_symbols else "")
        )
        chars.extend(self.__keywords_list)

        chars_count = len(chars)

        remains_symbols = password_len
        result_password = ""
        for _ in range(0, password_len):
            word_or_letter = chars[r.randint(0, chars_count - 1)]
            word_or_letter_len = len(word_or_letter)

            if word_or_letter_len <= remains_symbols:
                result_password += word_or_letter
                remains_symbols -= word_or_letter_len

        return result_password


class PasswordServer:
    __ip: str
    __port: int

    __server: st.socket
    __client: st.socket

    encryptKey: bytes = None

    __is_block_errors: bool

    def __init__(self, ip: str, port: int, block_errors: bool):
        self.__ip, self.__port = ip, port

        self.__server = st.socket(st.AF_INET, st.SOCK_STREAM)
        self.__server.bind((self.__ip, self.__port))
        self.__client = None

        self.__is_block_errors = block_errors

    def get_pin_code(self):
        pin_code = os.getenv("PCH_PIN_CODE").encode()

        pin = self.__client.recv(4096)

        if pin == h.sha512(pin_code).digest():
            return True

        return False

    def send_password(self, password):
        fernet_obj = ctf.Fernet(self.encryptKey)

        self.__client.sendall(fernet_obj.encrypt(password.encode()))

    def close(self):
        if self.__client is not None:
            self.__client.close()

        self.__server.close()

    def __enter__(self):
        print("Сервер запущен!")
        print("Привязка к IP и порту")
        self.__server.listen(2)

        print("Ожидание подключений...")
        connection, address = self.__server.accept()

        print("Подключен клиент: " + str(address))
        self.__client = connection

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

        return self.__is_block_errors


def main():
    args = ConfigureArgParser()

    p_user = os.getenv("PCH_USER")
    wait_time = int(os.getenv("WAIT_TIME"))
    p_max_len = int(os.getenv("MAX_PASSWORD_LEN"))
    key_words = list(
        map(lambda x: x.strip(), re.split(r",?\s*", os.getenv("KEYWORDS")))
    )

    p_generator = PasswordGenerator(True, key_words)

    key = None
    key_file_name = os.getenv("KEY_FILE_NAME") + ".key"

    if args.generate_key:
        key = p_generator.generateKey(key_file_name)
        return

    else:
        key = p_generator.readKey(key_file_name)

    while True:
        password = p_generator.generate_password(r.randint(8, p_max_len))
        changePassword(p_user, password)

        with PasswordServer("", 8080, True) as client:
            client.encryptKey = key

            if client.get_pin_code():
                client.send_password(password)
            else:
                client.sendall("i_pc".encode())

        t.sleep(wait_time)


def ConfigureArgParser():
    parser = ap.ArgumentParser("password_changer")
    parser.add_argument("-gk", "--generate_key", action="store_true")

    args = parser.parse_args()

    return args


def changePassword(p_user, password):
    if sys.platform == "win32":
        pc.ChangePasswordWindows(p_user, password)

    else:
        pc.ChangePasswordLinux(p_user, password)


if __name__ == "__main__":
    main()
