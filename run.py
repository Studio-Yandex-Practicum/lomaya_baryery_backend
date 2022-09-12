import uvicorn as uvicorn

from src.main import app

if __name__ == '__main__':
    # bot.polling()
    uvicorn.run(app, host="0.0.0.0", port=8000)
