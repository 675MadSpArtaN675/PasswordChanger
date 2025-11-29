### Настройка программы.

Для правильной работы сервера подменщика паролей, нужно в файл ".env" написать параметры и вставить значения.

PCH_USER="<Имя пользователя>"<br/>
PCH_PATH_TO_KEY="<Путь до ключа>"
PCH_PIN_CODE="\<PIN>", где PIN - пин-код длиной 4 символа<br/>
MAX_PASSWORD_LEN=<Макс. кол-во символов><br/>
WAIT_TIME=<Ожидание между перегенерацией паролей в секундах><br/>
KEY_FILE_NAME="<Название файла без формата>"<br/>
KEYWORDS=[...] <Список слов, которые разделены пробелами или запятой><br/>

#### Пример настроек:

```
PCH_USER = "IVAN"
PCH_PATH_TO_KEY = "C:\\Users\\Public\\Documents"
PCH_PIN_CODE = "7524"
MAX_PASSWORD_LEN = 16
WAIT_TIME = 60
KEY_FILE_NAME = "password_key"
KEYWORDS = ["Boy", "Girl", "Man", "Spider", "Horse", "Computer"]
```
