from config.config import *

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, F

from data_set import SelecMediaDownloader, TemporaryCache, FeedbackForm
from key_gen import generate_random_key
from side_menu import set_commands

from database.database import start_db
from uptime import Uptime

from collections import defaultdict
from datetime import datetime, timedelta

# from cache_maestro import CookieChecker
from supportedsites import *

import os

import asyncio
import bot_sender
import threading
import helper
import keyboards

uptime = Uptime()
cache = TemporaryCache()

WHITELIST = USERS['white_list']
downloads = defaultdict(list)
downloads_lock = asyncio.Lock()


# cookies = CookieChecker()

# HANDLER REGISTRATION 
async def handlers_reg(dp: Dispatcher):

    # command handler registration 
    dp.message.register(get_start, Command(commands=['start']))
    dp.message.register(get_feedback, Command(commands=['feedback']))
    dp.message.register(settings, Command(commands=['settings']))
    dp.message.register(get_version, Command(commands=['version']))

    # FEEDBACK 
    dp.message.register(feedback_from_user, FeedbackForm.RECEIVING_FEEDBACK)

    # TEXT HANDLER
    dp.message.register(text_handler, F.text)

    # DOCUMENTS HANDLER
    dp.message.register(document_handler, F.document)

    # SELECTORS MEDIA DOWNLOADER
    dp.callback_query.register(download_and_send_audio, SelecMediaDownloader.filter(F.media_type == 'audio'))
    dp.callback_query.register(download_and_send_video, SelecMediaDownloader.filter(F.media_type == 'video'))
    # dp.callback_query.register(download_and_send_voice, SelecMediaDownloader.filter(F.media_type == 'voice'))

    # ADDITIONAL MEDIA HANDLER
    dp.callback_query.register(send_audio_to_group, SelecMediaDownloader.filter(F.media_type == 'music'))
    dp.callback_query.register(send_audio_to_group, SelecMediaDownloader.filter(F.media_type == 'relax'))
    dp.callback_query.register(send_audio_to_group, SelecMediaDownloader.filter(F.media_type == 'rock'))

    # AFTER START BOT COMMANDS
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

#################################
'''
Side menu command handlers
'''
# START COMMAND HANDLER
async def get_start(message: Message):
    await message.answer(f'Hello there, <b>{message.from_user.full_name}</b>. {START_TEXT["EN"]}')
    
# FEEDBACK COMMAND HANDLER
async def get_feedback(message: Message, state: FSMContext):
    await message.answer('Напиши отзыв автору: \n\n'+
                         'Write a feedback to the author: \n\n')
    await state.set_state(FeedbackForm.RECEIVING_FEEDBACK)
    print('состояние установлено')

# SETTING COMMAND HANDLER
async def settings(message: Message):
    await message.answer(f'Settings is coming soon\nWe working on it')

# VERSION COMMAND HANDLER
async def get_version(message: Message):
    chat_id = message.chat.id
    try:
        threading.Thread(target=lambda: asyncio.run(bot_sender.send_version(TOKEN=TOKEN, CHAT_ID=chat_id, uptime=uptime))).start()
    except Exception as e:
        print(e)    


#################################


# DOCUMENTS HANDLER
async def document_handler(message: Message, bot: Bot):
# For updating cookies file 

    if message.from_user.id in ADMINS_ID:

        document = message.document
        file_id = document.file_id
        file = await bot.get_file(file_id)

        curren_path = os.path.dirname(__file__)+'/'
        filename = document.file_name
        os.makedirs(f"{curren_path}config/cookies", exist_ok=True)

        file_path = f"{curren_path}config/cookies/{filename}"

        await bot.download_file(file.file_path, file_path)

        await message.answer(f"File '{filename}' saved!")

        # await message.answer_document(FSInputFile(file_path))


# TEXT HANDLER
async def text_handler(message: Message, bot: Bot):
    message_info = None
    args = helper.get_args(message.text)
    print(message.text)
    if await can_download(message.chat.id, args['link']):
        try:
            if "https://" in args['link'] and (youtube):
                if message.from_user.id not in WHITELIST:
                    await bot.send_message(
                        message.chat.id,
                        "⚠️ Скачивание с YouTube сейчас сильно ограничено.\nВедутся работы что бы это исправить.\n"
                        "⚠️ Downloading from YouTube is currently heavily restricted.\nWork is underway to fix this." \
                    )
                    return 

            if 'https://' in args['link'] and 'youtube' in args['link'] and '&list=' in args['link']:
                await bot.send_message(message.chat.id, "Бот не может качать весь плейлист, введите ссылку на отдедельную песню в формате 'https://...'\n\n"+
                                    "The bot cannot download the entire playlist, enter a link to an individual song in the format 'https://...")
            elif '//' and 'joyreactor.cc' in args['link']:
                threading.Thread(target=lambda: asyncio.run(helper.send_from_joyreactor(LINK=args['link'],
                                                                                        CHAT_ID=message.chat.id,
                                                                                        TOKEN=TOKEN))).start()
            elif "https://" in args['link'] and any(site in args['link'] for site in ELIGIBLE_SITES):
                # message_info need for delete message after sending file
                try:
                    if args['video'] or args['audio']:
                        if args['video']:
                            threading.Thread(target=lambda: asyncio.run(bot_sender.download_and_send_video(TOKEN=TOKEN,
                                                                                            URL=args['link'],
                                                                                            CHAT_ID=message.chat.id,
                                                                                            user_name=message.from_user.full_name))).start()
                        if args['audio']:
                            group = ''
                            if args['group'] != '':
                                group = args['group']
                            threading.Thread(target=lambda: asyncio.run(bot_sender.download_and_send_audio(TOKEN=TOKEN,
                                                                                            URL=args['link'],
                                                                                            CHAT_ID=message.chat.id,
                                                                                            group=group,
                                                                                            user_name=message.from_user.full_name))).start()
                    else:
                        key = generate_random_key() # 45-44 from 64 bytes for call_back data - 19 left 
                        key = key[0:38] # short coz callback_data is ***** -_- gavno ebanoe, 64 simvola ya togo rot ebal
                        message_info = await message.reply("<b>DOWNLOAD</b>", 
                                                    reply_markup=await keyboards.select_media_type(key, message.from_user.id)) # reply looks much better 
                        await cache.add_to_cache(key, [message_info, args, message.from_user.full_name])
                    if args['del_msg']:
                        try:
                            await bot.delete_message(message.chat.id, message.message_id)
                        except Exception as e:
                            print(e)
                except Exception as e: 
                    print(f"ERROR in text_handler - {str(e)}")
            elif "https://" in args['link'] and not any(site in args['link'] for site in ELIGIBLE_SITES):
                await bot.send_message(message.chat.id, "THE SITE IS NOT SUPPORTED!!!")
                print("[-][ERROR INPUT, NOT SUPPORTED SITE]")    
            elif message.text.lower() in helper.cat:
                await helper.show_cat(message, bot)
                print("мяу", end=" ")
            else:
                await bot.send_message(message.chat.id, "Введите пожалуйста ссылку в формате 'https://...'\n"+
                                    "Please enter the link in the format 'https://...")
                print(message.chat.type)
                print("[-][ERROR INPUT]")
        except Exception as e:
            try:
                await bot.delete_message(message.chat.id, message_info.message_id)
            except Exception as e:
                print('ERROR DELETING MESSAGE', e)
                await bot.send_message(message.chat.id, "ERROR INPUT, CALL TO ADMIN")    
            await bot.send_message(message.chat.id, "ERROR INPUT, WRONG LINK")
            print("[bot][-][ERROR IN MAIN PACKAGE]", e)
    else:
        await bot.send_message(message.chat.id, "PLS WAIT, BOT IS OVERLOADED. TRY AGAIN LATER!\nПОЖАЛУЙСТА ПОДОЖДИТЕ БОТ ПЕРЕГРУЖЕН, ПОВТОРИТЕ ПОПЫТКУ ПОЗЖЕ!")        


# DOWNLOAD AND SEND VIDEO
async def download_and_send_video(call: CallbackQuery, bot: Bot, callback_data: SelecMediaDownloader):
    arr = await cache.get_from_cache(callback_data.key) # kostyl
    message = arr[0]
    await bot.delete_message(message.chat.id, message.message_id)
    args = arr[1]
    user_name = arr[2]
    await cache.remove_from_cache(callback_data.key) # kostyl
    threading.Thread(target=lambda: asyncio.run(bot_sender.download_and_send_video(TOKEN=TOKEN,
                                                                                    URL=args['link'],
                                                                                    CHAT_ID=message.chat.id,
                                                                                    user_name=user_name))).start()
  
# DOWNLOAD AND SEND AUDIO
async def download_and_send_audio(call: CallbackQuery, bot: Bot, callback_data: SelecMediaDownloader, group='', voice=False):
    arr = await cache.get_from_cache(callback_data.key) # kostyl
    message = arr[0]
    await bot.delete_message(message.chat.id, message.message_id)
    args = arr[1]
    user_name = arr[2]
    await cache.remove_from_cache(callback_data.key) # kostyl
    threading.Thread(target=lambda: asyncio.run(bot_sender.download_and_send_audio(TOKEN=TOKEN,
                                                                                    URL=args['link'],
                                                                                    CHAT_ID=message.chat.id,
                                                                                    group=group,
                                                                                    user_name=user_name))).start()
                  

# DOWNLOAD AND SEND VOICE
async def download_and_send_voice(call: CallbackQuery, bot: Bot, callback_data: SelecMediaDownloader, group=''):
    await download_and_send_audio(call=call, bot=bot, callback_data=callback_data, group=group, voice=True)

# DOWNLOAD AND SEND AUDIO TO GROUP
async def send_audio_to_group(call: CallbackQuery, bot: Bot, callback_data: SelecMediaDownloader, group=None):
    group=''
    if callback_data.media_type == 'music':
        group=GROUP1
    if callback_data.media_type == 'relax':
        group=GROUP2
    if callback_data.media_type == 'rock':
        group=GROUP3
    await download_and_send_audio(call=call, bot=bot, callback_data=callback_data, group=group)

#################################
# GETTING FEEDBACK
async def feedback_from_user(message: Message, bot: Bot, state: FSMContext):
    # FEEDBACK TO ADMINS
    ms = []
    try:
        if len(ADMINS_ID) > 0:
            for admin_id in ADMINS_ID:
                ms.append(await bot.send_message(chat_id=admin_id, text=f"<pre>FEEDBACK\nBOT ID:\n{TOKEN}\n<b>{message.from_user.full_name}, ID-{message.from_user.id}:\n</b>{message.text}</pre>")) 
    except Exception as e:
        print('[ERROR FEEDBACK TO ADMINS]', e)
        await message.reply('ERROR FEEDBACK, SEND MESSAGE TO ADMINS')
    # FEEDBACK TO MODERATORS
    try:
        if len(MODERATORS_ID) > 0:
            for mod_id in MODERATORS_ID:
                ms.append(await bot.send_message(chat_id=mod_id, text=f"<pre>FEEDBACK\n<b>{message.from_user.full_name}, ID-{message.from_user.id}:\n</b>{message.text}</pre>"))
    except Exception as e:
        print('[ERROR FEEDBACK]', e)
        await message.reply('ERROR FEEDBACK, SEND MESSAGE TO MODERATORS')
    # TRY TO PIN    
    try:
        for rem_ms in ms:
            await bot.pin_chat_message(chat_id=rem_ms.chat.id, message_id=rem_ms.message_id)
            ms.remove(rem_ms)   
        await message.reply(f"Я отправил твой отзыв автору бота.\n"+
                            "I sent your feedback to the bot author.")    
    except Exception as e:  
        await message.reply('ERROR FEEDBACK, CAN\'T PIN MESSAGE')      
    await state.clear()

#################################
# LIMITS DOWNLOAD
async def can_download(user_id: int, link: str) -> bool:
    async with downloads_lock:
        now = datetime.now()

        if user_id in WHITELIST:
            return True

        if user_id in USERS['blocked']:
            return False

        is_youtube = any(yt in link for yt in youtube)
        limits_type = 'youtube' if is_youtube else 'other'
        limits = BOT_SETINGS['LIMITS'][limits_type]

        # создаём хранилище отдельно по типам
        if user_id not in downloads:
            downloads[user_id] = {
                'youtube': [],
                'other': []
            }

        user_downloads = downloads[user_id][limits_type]

        # чистим старые записи по окну days_delay_limit
        downloads[user_id][limits_type] = [
            t for t in user_downloads
            if now - t < timedelta(days=limits['days_delay_limit'])
        ]

        user_downloads = downloads[user_id][limits_type]

        # лимит по кулдауну в днях
        if user_downloads:
            last_download = max(user_downloads)
            if now - last_download < timedelta(days=limits['days_delay_limit']):
                print(f'[!][OVER LIMITS {limits_type.upper()} DAYS DELAY]')
                return False

        # лимит за день
        per_day = [
            t for t in user_downloads
            if now - t < timedelta(days=1)
        ]
        if len(per_day) >= limits['per_day']:
            print(f'[!][OVER LIMITS {limits_type.upper()} DAY]')
            return False

        # лимит за условный "hour" — у тебя тут раньше было 10 минут
        recent = [
            t for t in user_downloads
            if now - t < timedelta(minutes=10)
        ]
        if len(recent) >= limits['per_hour']:
            print(f'[!][OVER LIMITS {limits_type.upper()} 10 MIN]')
            return False

        downloads[user_id][limits_type].append(now)
        return True


#################################
# FIRST ACTION AFTER LAUNCH BOT
async def start_bot(bot: Bot):
    await set_commands(bot)
    try:
        await start_db()
    except Exception as e:    
        print('[err 8989898]', e)
    try:
        for admin_id in ADMINS_ID:
            await bot.send_message(admin_id, "<b>BOT STARTED</b>")
    except Exception as e:
        print('[-][ERROR SEND MESSAGE TO ADMIN]', e)
# LAST ACTION OF BOT 
async def stop_bot(bot: Bot):
    # ALWAYS SILENT =) 
    try: 
        for admin_id in ADMINS_ID:    
            await bot.send_message(admin_id, "<b>BOT STOPPED</b>") 
    except Exception as e:
        print('[-][ERROR SEND MESSAGE TO ADMIN]', e)