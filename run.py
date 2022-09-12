import uvicorn

from src.core.settings import DATABASE_URL
from src.main import app

if __name__ == '__main__':
    print(DATABASE_URL)
    uvicorn.run(app, host="0.0.0.0")
