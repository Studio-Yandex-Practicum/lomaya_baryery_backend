import json
import sys


def main():
    """Скрипт проверки JSON ответа от ручки /healthcheck при деплое сервера.

    Возвращает в терминал 0, если все хорошо, иначе - 1.
    """
    JSON = json.load(sys.stdin)
    result = 0
    for value in JSON.values():
        if value != [
            True,
        ]:
            result += 1
    if result:
        print(1)
    else:
        print(0)


if __name__ == '__main__':
    main()
