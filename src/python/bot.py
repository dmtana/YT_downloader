import asyncio
import helper
import handlers
import logging

from aiogram import Bot, Dispatcher

from config.config import TOKEN

# подготовка к запуску бота
async def start():
    # Logging to console
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s) .%(funcName)s(%(lineno)d) - %(message)s")

    # get token and set html parsing
    bot = Bot(token=TOKEN, parse_mode='HTML')

    dp = Dispatcher()

    # handler registration
    await handlers.handlers_reg(dp)
  
    # clear cache more than 3 days default
    try:
        await helper.create_folders()
        await helper.delete_file()
        await helper.delete_file(1, 'photo/Thumbnails')
        await helper.delete_file(1, 'video')
    except Exception as e:
        print(f'[ERROR CLEANING CACHE] - {str(e)}')

    # BOT STARTED
    try:
        await dp.start_polling(bot)
    except Exception as ex:
        print(f'[ERROR IN START FILE] {ex}')
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())