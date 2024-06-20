import requests
import version
import helper

from aiogram.utils.chat_action import ChatActionSender
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties

from database.database import write_to_db
from get_version_new import get_version_new


async def download_and_send_video(TOKEN, URL, CHAT_ID, user_name, parse_mode='HTML'):
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=parse_mode))
    bot_name = ''
    async with ChatActionSender.upload_video(chat_id=CHAT_ID, bot=bot):
        try:
            msg = await bot.send_message(chat_id=CHAT_ID, text='Downloading...')
            bot_name = str(msg.from_user.first_name)
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
    try:
        await write_to_db(information=URL, id=str(CHAT_ID), media_type='video', user_name=user_name, bot_name=bot_name)
    except Exception as e:
        print('[X][ERROR DATABASE CONNECTION][bot_sender]', e)
    print('[bot][+][DONE SENDING IN THREAD]')    

async def download_and_send_audio(TOKEN, URL, CHAT_ID, user_name, group='', voice=False, parse_mode='HTML'):
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=parse_mode))
    bot_name = ''
    media_type='audio'
    async with ChatActionSender.upload_voice(chat_id=CHAT_ID, bot=bot):
        try:    
            msg = await bot.send_message(chat_id=CHAT_ID, text='Downloading...')
            file_id, error_message = await helper.download_media(URL)
            await helper.send_audio(chat_id=CHAT_ID, bot=bot, file_id=file_id, group=group)
            if error_message:
                await bot.send_message(chat_id=CHAT_ID, text=error_message)               
        except Exception as e:
            try:
                await bot.send_message(chat_id=CHAT_ID, text='ERROR INPUT, WRONG LINK')
            except Exception as e:
                print(e)    
            print('[X][ERROR SENDING AUDIO in download_and_send_audio()]', error_message, e)
        finally:
            try:
                await bot.delete_message(CHAT_ID, msg.message_id)
            except Exception as e:
                print(e)
            await bot.session.close()   
    try:
        if voice:
            media_type = 'voice'
        await write_to_db(information=URL, id=str(CHAT_ID), media_type=media_type, user_name=user_name, bot_name=bot_name)
    except Exception as e:
        print('[X][ERROR DATABASE CONNECTION][bot_sender]', e) 
    print('[bot][+][DONE SENDING IN THREAD]')               


async def send_version(TOKEN, CHAT_ID, uptime, parse_mode='HTML'):
    ver_of_lib = ''
    uptime_str = ''
    try:
        ver_of_lib = await get_version_new()
        uptime_str = uptime.get_uptime()
    except Exception as e:
        print(e)
    check_version = ''
    try: # check for latest version on github
        url = 'https://raw.githubusercontent.com/dmtana/YT_downloader/master/src/python/version.py'
        response = requests.get(url)
        response.raise_for_status()
        config_content = response.text
        config = {}
        exec(config_content, config)
        if version.VERSION == config.get('VERSION'):
            check_version += '(Latest)'
        else:
            check_version += f"A new version is available {config.get('VERSION')}, please reboot the server to update."
            pass    
    except Exception as e:
        print(e)   
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=parse_mode))
    msg = f'Version: <b>{version.VERSION}</b> <i>{check_version}</i>\n{version.description}\n{ver_of_lib}\n\nUptime: {uptime_str}'
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print(e)
    finally:
        await bot.session.close()    
