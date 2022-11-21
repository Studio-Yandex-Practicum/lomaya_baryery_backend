import uvicorn

from src.application import create_app

app = create_app()

if __name__ == '__main__':
    # TODO подумать как можно реализовать другими средствами
    # ssl_keyfile и ssl_certfile для того чтобы работала форма регистрации бота на тесте
    # Ссылка на описание проблемы https://www.notion.so/WebApp-Telegram-API-eee8bf6ebcbe492e835bf166ead50fd7
    uvicorn.run(app, host="0.0.0.0", port=8080, ssl_keyfile="localhost.key", ssl_certfile="localhost.crt")
