import uvicorn as uvicorn

from bot.views import bot
from server.main import app

if __name__ == '__main__':
    bot.polling()
    uvicorn.run(app, host="0.0.0.0", port=8000)
