from config.config import ADMINS_ID, MODERATORS_ID, TOKEN, START_TEXT, GROUP1, GROUP2, GROUP3

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
from aiogram import Bot, Dispatcher, F

from data_set import SelecMediaDownloader, TemporaryCache, FeedbackForm
from key_gen import generate_random_key
from side_menu import set_commands

from database.database import write_to_db, start_db
from uptime import Uptime

import asyncio
import bot_sender
import threading
import helper
import keyboards

uptime = Uptime()
cache = TemporaryCache()

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

    # SELECTORS MEDIA DOWNLOADER
    dp.callback_query.register(download_and_send_audio, SelecMediaDownloader.filter(F.media_type == 'audio'))
    dp.callback_query.register(download_and_send_video, SelecMediaDownloader.filter(F.media_type == 'video'))
    dp.callback_query.register(download_and_send_voice, SelecMediaDownloader.filter(F.media_type == 'voice'))

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
    await message.answer('Напиши отзыв автору: \n<i>(если хотите получить обратную связь укажите как с вами связаться)</i>\n\n'+
                         'Write a feedback to the author: \n<i>(if you want to receive feedback, please indicate how to contact you)</i>\n\n'+
                         'or write me <b>@dmtana</b>')
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

# TEXT HANDLER
async def text_handler(message: Message, bot: Bot):

    message_info = None
    args = helper.get_args(message.text)
    print(message.text)
    try:
        if 'https://' and 'youtube' and '&list=' in args['link']:
            await bot.send_message(message.chat.id, "Бот не может качать весь плейлист, введите ссылку на отдедельную песню в формате 'https://...'\n\n"+
                                   "The bot cannot download the entire playlist, enter a link to an individual song in the format 'https://...")
        elif "https://" in args['link']:
            # message_info need for delete message after sending file
            try:
                key = generate_random_key()
                # 45-44 from 64 bytes for call_back data - 19 left 
                key = key[0:38] # short coz callback_data is ***** -_- gavno ebanoe, 64 simvola ya togo rot ebal
                message_info = await message.reply("<b>DOWNLOAD</b>", 
                                               reply_markup=await keyboards.select_media_type(key, message.from_user.id)) # reply looks much better 
                
                await cache.add_to_cache(key, [message_info, args, message.from_user.full_name])

            except Exception as e: 
                print(f"ERROR in text_handler - {str(e)}")
          
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


# DOWNLOAD AND SEND VIDEO
async def download_and_send_video(call: CallbackQuery, bot: Bot, callback_data: SelecMediaDownloader):
    arr = await cache.get_from_cache(callback_data.key) # kostyl
    message = arr[0]
    await bot.delete_message(message.chat.id, message.message_id)
    args = arr[1]
    user_name = arr[2]
    await cache.remove_from_cache(callback_data.key) # kostyl
    ############################### testing
    try:
        await write_to_db(information=args['link'], id=str(message.chat.id), media_type='video', user_name=user_name, bot_name=message.from_user.full_name)
    except Exception as e:
        print('[X][ERROR DATABASE CONNECTION]', e)
    ############################### testing
    threading.Thread(target=lambda: asyncio.run(bot_sender.download_and_send_video(TOKEN=TOKEN,
                                                                                    URL=args['link'],
                                                                                    CHAT_ID=message.chat.id,
                                                                                    ))).start()
  
# DOWNLOAD AND SEND AUDIO
async def download_and_send_audio(call: CallbackQuery, bot: Bot, callback_data: SelecMediaDownloader, group='', voice=False):
    arr = await cache.get_from_cache(callback_data.key) # kostyl
    message = arr[0]
    await bot.delete_message(message.chat.id, message.message_id)
    args = arr[1]
    user_name = arr[2]
    await cache.remove_from_cache(callback_data.key) # kostyl

    media_type='audio'
    download_and_send_audio_status = 0
    ms = None
    ############################## testing
    try:
        if voice:
            media_type='voice'
        await write_to_db(information=args['link'], id=str(message.chat.id), media_type=media_type, user_name=user_name, bot_name=message.from_user.full_name)
    except Exception as e:
        print('[X][ERROR DATABASE CONNECTION]', e)
    ############################### testing
    async with ChatActionSender.upload_voice(chat_id=call.message.chat.id, bot=bot):
        try:    
            ms = await call.message.answer('Downloading...')
            file_id, err_msg = await helper.download_media(args['link'])
            if voice:
                download_and_send_audio_status = await helper.send_voice(message=message, bot=bot, file_id=file_id, group=group)
            else:    
                download_and_send_audio_status = await helper.send_audio(message=message, bot=bot, file_id=file_id, group=group)
            if err_msg:
                await call.message.answer(err_msg)                
        except Exception as e:
            await call.message.answer('ERROR INPUT, WRONG LINK')
            print('ERROR AUDIO - ', e)
        finally:
            print('[bot][+][DONE DOWNLOADING]')
            if ms:
                await bot.delete_message(message.chat.id, ms.message_id) 
    if download_and_send_audio_status > 5:
        await call.message.answer(f'<b>Sent in {group} +</b>')                       

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
                ms.append(await bot.send_message(chat_id=admin_id, text=f"<pre>FEEDBACK\n<b>{message.from_user.full_name}, ID-{message.from_user.id}:\n</b>{message.text}</pre>")) 
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