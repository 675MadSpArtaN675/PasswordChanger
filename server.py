import password_changer as pc

import os, sys
import threading as th
import argparse as ap
import random as r
import string as s
import socket as st
import hashlib as h
import time as t

import cryptography.fernet as ctf

from config import *


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

            return key

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
        pin_code = PCH_PIN_CODE.encode()

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


class ChangerService:
    __password: str = None
    __is_service_launch: bool = False

    def __del__(self):
        self.SetStandartPassword()

    def Launch(self):
        args = self.__ConfigureArgParser()

        p_user = PCH_USER
        key_words = list(map(lambda x: x.strip(), KEYWORDS))

        p_generator = PasswordGenerator(True, key_words)

        key = None
        key_file_name = PCH_PATH_TO_KEY + "\\" + KEY_FILE_NAME + ".key"

        if args.generate_key or not os.path.exists(key_file_name):
            key = p_generator.generateKey(key_file_name)
            return

        else:
            key = p_generator.readKey(key_file_name)

        self._program_cycle(p_user, p_generator, key)

    def SetStandartPassword(self):
        self.__changePassword(PCH_USER, "1234qwer", self.__password)

        return

    def Stop(self):
        self.__is_service_launch = False

    def _replacePassword(
        self, username: str, p_generator: PasswordGenerator, lock: th.Lock
    ):
        p_max_len = int(MAX_PASSWORD_LEN)
        wait_time = int(WAIT_TIME)

        while self.__is_service_launch:
            lock.acquire()
            global YOUR_LAST_PASSWORD
            self.__password = p_generator.generate_password(r.randint(8, p_max_len))
            self.__changePassword(username, self.__password, YOUR_LAST_PASSWORD)

            YOUR_LAST_PASSWORD = self.__password
            lock.release()

            t.sleep(wait_time)

    def _program_cycle(
        self,
        username: str,
        p_generator: PasswordGenerator,
        key: bytes,
    ):
        self.__is_service_launch = True

        lock = th.Lock()

        changer_thread = th.Thread(
            target=self._replacePassword, args=(username, p_generator, lock)
        )
        changer_thread.start()

        while self.__is_service_launch:
            with PasswordServer("0.0.0.0", 8080, True) as client:
                client.encryptKey = key

                if client.get_pin_code():
                    lock.acquire()
                    if self.__password is not None:
                        client.send_password(self.__password)
                    lock.release()
                else:
                    client.sendall("i_pc".encode())

        changer_thread.join()

    def __ConfigureArgParser(self):
        parser = ap.ArgumentParser("password_changer")
        parser.add_argument("-gk", "--generate_key", action="store_true")

        args = parser.parse_args()

        return args

    def __changePassword(self, p_user, password, old_password):
        if sys.platform == "win32":
            pc.ChangePasswordWindows(p_user, password, old_password)

        else:
            pc.ChangePasswordLinux(p_user, password)


if __name__ == "__main__":
    ChangerService().Launch()
