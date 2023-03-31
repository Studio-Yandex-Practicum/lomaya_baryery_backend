import uvicorn

from src.application import create_app
from src.core.utils import setup_logging

app = create_app()

if __name__ == '__main__':
    setup_logging()
    uvicorn.run(app, host="127.0.0.1", port=8080)
