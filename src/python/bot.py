import asyncio
import threading
import handlers
import logging
import cache_maestro

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties

from config.config import TOKEN

async def start():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s) .%(funcName)s(%(lineno)d) - %(message)s")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

    dp = Dispatcher()
    await handlers.handlers_reg(dp)
   
    try:  # create folders
        await cache_maestro.create_folders()
        # clear cache more than 3 days default every 24h
        threading.Thread(target=lambda: asyncio.run(cache_maestro.clear_cache())).start()
    except Exception as e:
        print('[X][ERROR creating/deleting in main bot.py]', e)

    # BOT STARTED
    try:
        await dp.start_polling(bot)
    except Exception as ex:
        print(f'[ERROR IN START FILE] {ex}')
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())