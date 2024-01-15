from config import ADMIN_ID, ADMIN_ID2, MODERATOR
from config import START_TEXT
from config import GROUP1, GROUP2, GROUP3

from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender

from aiogram import Bot, Dispatcher, F

from data_set import SelecMediaDownloader, TemporaryCache, FeedbackForm
from key_gen import generate_random_key
from side_menu import set_commands

from version import VERSION

import helper
import keyboards

my_cache = TemporaryCache()

# HANDLER REGISTRATION 
async def handlers_reg(dp: Dispatcher):

    # command handler registration 
    dp.message.register(get_start, Command(commands=['start']))
    dp.message.register(get_help, Command(commands=['help']))
    dp.message.register(get_feedback, Command(commands=['feedback']))
    dp.message.register(get_version, Command(commands=['version']))

    # FEEDBACK 
    dp.message.register(feedback_from_user, FeedbackForm.RECEIVING_FEEDBACK)

    # TEXT HANDLER
    dp.message.register(text_handler, F.text)

    # SELECTORS MEDIA DOWNLOADER
    dp.callback_query.register(download_and_send_audio, SelecMediaDownloader.filter(F.media_type == 'audio'))
    dp.callback_query.register(download_and_send_video, SelecMediaDownloader.filter(F.media_type == 'video'))
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
async def get_start(message: Message, bot: Bot):
    await message.answer(f'Здравствуй <b>{message.from_user.full_name}</b>. {START_TEXT["RUS"]}')

# HELP COMMAND HANDLER
async def get_help(message: Message, bot: Bot):
    await message.answer('Помощи пока нет, но вы держитесь =)')
    
# FEEDBACK COMMAND HANDLER
async def get_feedback(message: Message, state: FSMContext):
    await message.answer('Напиши отзыв автору: ')
    await state.set_state(FeedbackForm.RECEIVING_FEEDBACK)
    print('состояние установлено')

# VERSION COMMAND HANDLER
async def get_version(message: Message, bot: Bot):
    await message.answer(f'Version: {VERSION}')


#################################

# TEXT HANDLER
async def text_handler(message: Message, bot: Bot):

    message_info = None
    args = helper.get_args(message.text)
    print(message.text)
    try:
        if "https://" in args['link']:
            # variable [message_info] need for delete message after sending file
            try:
                key = generate_random_key()
                key = key[0:38] # short coz callback_data is ***** -_-

                message_info = await message.reply("Скачать\Download ->", 
                                               reply_markup=await keyboards.select_media_type(key, message.from_user.id)) # reply looks much better 
                
                await my_cache.add_to_cache(key, [message_info, args])

            except Exception as e: 
                print(f"ERROR in text_handler - {str(e)}")
          
        elif message.text.lower() in helper.cat:
            await helper.show_cat(message, bot)
            print("мяу", end=" ")
        else:
            await bot.send_message(message.chat.id, "Введите пожалуйста ссылку в формате 'https://...'")
            print(message.chat.type)
            print("[-][ERROR INPUT]")
    except Exception as e:
        try:
            await bot.delete_message(message.chat.id, message_info.message_id)
        except Exception as e:
            print('ERROR DELETING MESSAGE', e)
            await bot.send_message(message.chat.id, "ERROR INPUT, CALL TO ADMIN")    
        await bot.send_message(message.chat.id, "ERROR INPUT, WRONG LINK")
        print("[-][ERROR IN MAIN PACKAGE]", e)


# DOWNLOAD AND SEND VIDEO
async def download_and_send_video(call: CallbackQuery, bot: Bot, callback_data: SelecMediaDownloader):
    arr = await my_cache.get_from_cache(callback_data.key)
    message = arr[0]
    args = arr[1]
    await bot.delete_message(message.chat.id, message.message_id)        
    async with ChatActionSender.upload_video(chat_id=call.message.chat.id, bot=bot):
        try:
            ms = await call.message.answer(f'Downloading...')
            file_id, err_msg = await helper.download_media(args['link'], is_video=True)
            await helper.send_video(message=message, bot=bot, file_id=file_id)
            if err_msg:
                await call.message.answer(err_msg)
        except Exception as e:
            await call.message.answer('ERROR INPUT, WRONG LINK')
            print('ERROR VIDEO - ', e)
        finally: 
            await bot.delete_message(message.chat.id, ms.message_id)      

# DOWNLOAD AND SEND AUDIO
async def download_and_send_audio(call: CallbackQuery, bot: Bot, callback_data: SelecMediaDownloader, group=''):
    arr = await my_cache.get_from_cache(callback_data.key)
    message = arr[0]
    args = arr[1]
    await bot.delete_message(message.chat.id, message.message_id)
    async with ChatActionSender.upload_voice(chat_id=call.message.chat.id, bot=bot):
        try:
            ms = None
            if call.message.chat.id == MODERATOR:
                ms = await call.message.answer('Downloading...', 
                                           reply_markup=ReplyKeyboardMarkup(
                                               keyboard=[[
                                                   KeyboardButton(text='кисан кисан')
                                                   ]], resize_keyboard=True, 
                                                   one_time_keyboard=True, 
                                                   selective=True))
            else:
                ms = await call.message.answer('Downloading...')    
            file_id, err_msg = await helper.download_media(args['link'])
            await helper.send_audio(message=message, bot=bot, file_id=file_id, group=group)
            if err_msg:
                await call.message.answer(err_msg)                
        except Exception as e:
            await call.message.answer('ERROR INPUT, WRONG LINK')
            print('ERROR AUDIO - ', e)
        finally:
            await bot.delete_message(message.chat.id, ms.message_id) 

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
    await call.message.answer(f'<b>In the group {group} +</b>')

async def feedback_from_user(message: Message, bot: Bot, state: FSMContext):
    # FEEDBACK TO ADMIN
    try:
        await message.reply(f"Я отправил твой отзыв автору бота.")
        ms1 = await bot.send_message(chat_id=ADMIN_ID, text=f"<pre>Отзыв от пользователя с ID \n<b>{message.from_user.id},\nИмя пользователя:\n{message.from_user.full_name}</b>: \n{message.text}</pre>")
        ms2 = await bot.send_message(chat_id=ADMIN_ID2, text=f"<pre>Отзыв от пользователя с ID \n<b>{message.from_user.id},\nИмя пользователя:\n{message.from_user.full_name}</b>: \n{message.text}</pre>")
        await bot.pin_chat_message(chat_id=ms1.chat.id, message_id=ms1.message_id)
        await bot.pin_chat_message(chat_id=ms2.chat.id, message_id=ms2.message_id)
    except Exception as e:
        print('[ERROR FEEDBACK]', e)
        await message.reply('ERROR FEEDBACK, SEND MESSAGE TO ADMIN')
    await state.clear()

#################################
# FIRST ACTION AFTER LAUNCH BOT
async def start_bot(bot: Bot):
    await set_commands(bot)
    try:
        await bot.send_message(ADMIN_ID, "<b>BOT STARTED</b>")
        await bot.send_message(ADMIN_ID2, "<b>BOT STARTED</b>")
    except Exception as e:
        print('[-][ERROR SEND MESSAGE TO ADMIN]', e)
# LAST ACTION OF BOT 
async def stop_bot(bot: Bot):
    # ALWAYS SILENT =) 
    try:    
        await bot.send_message(ADMIN_ID, "<b>BOT STOPPED</b>")  
        await bot.send_message(ADMIN_ID2, "<b>BOT STOPPED</b>")
    except Exception as e:
        print('[-][ERROR SEND MESSAGE TO ADMIN]', e)