import yt_dlp
import mp3_tag_editor
import os
import urllib.request
import json
import random

# easter egg
cat = ['котик', 'кися', 'котейка', 'кот', 'рыжик', 'рыжня', 'котэ', 'кисан', 'кисан кисан', 'кс кс', 'мяу', 'cэми']
async def save_json(a, j): #this method save json info
    try: # a: name of ID / j: json str
        with open(f"JSON_INFO_MP3/{a}.txt", "w") as json_file:
            # SAVE JSON FILE TO HAVE INFO ABOUT SOUND
            json_file.write(json.dumps(j))
    except Exception as e:
        print("ERROR JSON SAVE: ", e)

# commands for download video
commands_video = ['-video', '-v', 'видео', '-в']

# bot.send_message(chat_id='@your_channel_name', text='Hello, world!')

async def pars_command():
    pass
async def send_audio(message, bot):
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
        await bot.send_message(message.chat.id, "ERROR SENDING")
        print("ERROR SENDING: ", e)

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
        print("65", e)

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

async def download_video(message):
    print("NO IMPLEMENTATION YET")

async def show_cat(message, bot):
    try:
        with open(f'photo/Cats/cat{random.randint(1, 3)}.jpeg', 'rb') as photo:
            await bot.send_photo(message.chat.id, photo)
    except Exception as e:
        await bot.send_message(message.chat.id, "нима котика")