import uvicorn

from src.application import create_app

app = create_app()

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8080)
