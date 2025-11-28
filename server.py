import password_changer as pc

import os, sys
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

    def generateKey(self):
        if os.path.exists("test_key.dat"):
            with open("test_key.dat", "wb") as key_file:
                key_file.write(ctf.Fernet.generate_key())

        return

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

        pin = self.__client.recv(1024)

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
    p_generator = PasswordGenerator(True, ["fuck", "you", "anakin"])
    p_generator.generateKey()

    p_user = os.getenv("PCH_USER")
    wait_time = int(os.getenv("WAIT_TIME"))
    p_max_len = int(os.getenv("MAX_PASSWORD_LEN"))

    while True:
        password = p_generator.generate_password(r.randint(8, p_max_len))
        changePassword(p_user, password)

        with PasswordServer("", 8080, True) as client:
            if client.get_pin_code():
                client.send_password(password)

        t.sleep(wait_time)


def changePassword(p_user, password):
    if sys.platform == "win32":
        pc.ChangePasswordWindows(p_user, password)

    else:
        pc.ChangePasswordLinux(p_user, password)


if __name__ == "__main__":
    main()
