import asyncio
import json
import subprocess
import version
import helper

from aiogram.utils.chat_action import ChatActionSender
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties

from get_version_new import get_version_new


async def download_and_send_video(TOKEN, URL, CHAT_ID, parse_mode='HTML'):
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=parse_mode))
    async with ChatActionSender.upload_video(chat_id=CHAT_ID, bot=bot):
        try:
            msg = await bot.send_message(chat_id=CHAT_ID, text='Downloading...')
            file_id, error_message = await helper.download_media(URL, is_video=True)
            await helper.send_video(message=CHAT_ID, bot=bot, file_id=file_id)
        except Exception as e:
            try:
                await bot.send_message(chat_id=CHAT_ID, text='ERROR INPUT, WRONG LINK')
            except Exception as e:
                print(e)    
            print('[X][ERROR SENDING VIDEO in download_and_send_video()]', error_message, e)
        finally:
            try:
                await bot.delete_message(CHAT_ID, msg.message_id)
            except Exception as e:
                print(e)        
            await bot.session.close()   


async def send_version(TOKEN, CHAT_ID, uptime, parse_mode='HTML'):
    ver_of_lib = ''
    try:
        ver_of_lib = await get_version_new()
        uptime_str = uptime.get_uptime()
    except Exception as e:
        print(e)

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=parse_mode))
    msg = f'Version: <b>{version.VERSION}</b>\n{version.description}\n{ver_of_lib}\n\nUptime: {uptime_str}'

    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print(e)
    finally:
        await bot.session.close()    
