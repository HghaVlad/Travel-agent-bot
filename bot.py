import os
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.redis import RedisStorage2

bot_token = "6614384039:AAHkX2KbEebFXGaHNqkDp51jbGEzAENiUBQ"

bot = Bot(bot_token, parse_mode="HTML")
dp = Dispatcher(bot, storage=RedisStorage2(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0))

from filters import *
from handlers import *

async def starting(message):
    from models.DBSM import Base, engine
    Base.metadata.create_all(engine)
    await bot.send_message(578081663, "Started")

if __name__ == '__main__':
    print("Started")
    import filters
    import handlers

    executor.start_polling(dp, on_startup=starting)