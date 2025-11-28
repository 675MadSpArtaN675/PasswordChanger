### Настройка программы.

Для правильной работы сервера подменщика паролей, нужно в файл ".env" написать параметры и вставить значения.

PCH_USER=<Имя пользователя>

PCH_PIN_CODE=<Пин-код>

MAX_PASSWORD_LEN=<Макс. кол-во символов>

WAIT_TIME=<Ожидание между перегенерацией паролей в секундах>

KEY_FILE_NAME=<Название файла без формата>

KEYWORDS=... <Список слов, которые разделены пробелами или запятой>

Пример настроек:
'''
PCH_USER=IVAN
PCH_PIN_CODE=0913
MAX_PASSWORD_LEN=16
WAIT_TIME=5
KEY_FILE_NAME=password_key
KEYWORDS=Lodik, Kirill, Asshole, Artyom, DoggyStyle, Fick, Fuck, MADARA
'''
