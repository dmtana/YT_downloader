import os
import yt_dlp
import time
import random
import asyncio
import json
import mp3_tag_editor
import urllib.request
from telebot.async_telebot import AsyncTeleBot

def get_token():
    try:
        with open("token.txt", "r") as token:
            return str(token.read())
    except:
        print("CAN'T READ TOKEN!!! BOT STOPPED!!!")

hello_str = "Я бот для скачивания музыки с YouTube, просто пришли мне ссылку и я отправлю тебе аудиофайл"

bot = AsyncTeleBot(get_token())

# easter egg
cat = ['котик', 'кися', 'котейка', 'кот', 'рыжик', 'рыжня', 'котэ', 'кисан', 'кисан кисан', 'кс кс', 'мяу', 'cэми']


async def save_json(a, j):
    '''
    this method save json info
    :param a: name of ID :
    :param j: json str
    :return: None
    '''
    try:
        with open(f"JSON_INFO_MP3/{a}.txt", "w") as json_file:
            # SAVE JSON FILE TO HAVE INFO ABOUT SOUND
            json_file.write(json.dumps(j))
    except Exception as e:
        print("ERROR JSON SAVE: ", e)

@bot.message_handler(commands=["start"])
async def start(message):
    str = f"Привет, {message.from_user.first_name}. \n"
    await bot.send_message(message.chat.id, str + hello_str)

@bot.message_handler(content_types=["text"])
async def echo(message):
    if "https://" in message.text:
        await bot.send_message(message.chat.id, "Downloading")
        await download_audio(message)
        await bot.send_message(message.chat.id, "Download complete")
        await send_audio(message)
    elif message.text.lower() in cat:
        await show_cat(message)
        print("мяу", end=" ")
    else:
        await bot.send_message(message.chat.id, "Введите пожалуйста ссылку в формате 'https://...'")

async def send_audio(message):
    file_name = ""
    file_id = ""
    with yt_dlp.YoutubeDL() as ydl:
        # EXTRACT FROM LINK JSON INFO
        s = ydl.sanitize_info(ydl.extract_info(message.text, download=False))
        # WE GET TITLE AND ID FROM LINK
        file_name += s['title']
        file_id += s['id']
    try:
        with open(f'media_from_yt/{message.chat.id}/{file_name} [{file_id}].mp3', 'rb') as audio:
            await bot.send_audio(message.chat.id, audio)
        print("done sending")
    except Exception as e:
        time.sleep(2)
        print("ERROR SENDING: ", e)
        await bot.send_message(message.chat.id, "ERROR SENDING")

async def download_audio(message):
    file_name = ""
    file_id = ""
    try:
        with yt_dlp.YoutubeDL() as ydl:
            some_var = ydl.sanitize_info(ydl.extract_info(message.text, download=False))
            # WE GET TITLE AND ID FROM LINK
            file_name += some_var['title']
            file_id += some_var['id']
            await save_json(file_id, some_var)
            l = some_var['thumbnails'][5]['url']               # l is link to image of this sound
            try:
                # DOWNLOAD AND SAVE IMAGE
                resource = urllib.request.urlopen(l)
                with open(f'photo/Thumbnails/{file_id}.jpeg', 'wb') as file:
                    file.write(resource.read())
            except:
                print(777, "ERR DOWNLOAD IMAGE")
    except Exception as e:
        print("1", e)

    URL = message.text
    '''
    :param URL: link in format 'https://...'
    :return: None
    '''
    try:
        os.system(f'yt-dlp -f ba -x --audio-format mp3 -P '  # using ffmpeg.exe
                  f'D:\Other\Projects\Python_TG_bot\src\python\media_from_yt\{message.chat.id} '  # path
                  f'{URL}"')  # link
        print("download complete")
    except Exception as e:
        print("ERR DOWNLOAD")

    await mp3_tag_editor.tag_edit(file_id, message.chat.id)

async def show_cat(message):
    try:
        with open(f'photo/Cats/cat{random.randint(1, 3)}.jpeg', 'rb') as photo:
            await bot.send_photo(message.chat.id, photo)
    except Exception as e:
        await bot.send_message(message.chat.id, "нима котика")

# BOT in multithread
# run non stop
asyncio.run(bot.polling(non_stop=True))