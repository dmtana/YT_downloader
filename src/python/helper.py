import asyncio
import subprocess
import yt_dlp
import mp3_tag_editor
import os
import urllib.request
import json
import random
import datetime
import time

from aiogram import Bot
from aiogram.types import Message, FSInputFile
from aiogram.utils.chat_action import ChatActionSender

from config import SITE_1

# easter egg
cat = ['котик', 'кися', 'котейка', 'кот', 'рыжик', 'рыжня', 'котэ', 'кисан', 'кисан кисан', 'кс кс', 'мяу', 'cat', 'pusy']

# flag for deleting files after sending to bot
del_file = True

# fix for .venv py
curren_path = os.path.dirname(__file__)+'/'

# START BUGFIX
async def create_folders():
    if not os.path.exists(curren_path+'video'):
        os.makedirs(curren_path+'video')
    if not os.path.exists(curren_path+'media_from_yt'):
        os.makedirs(curren_path+'media_from_yt') 
    if not os.path.exists(curren_path+'photo/Thumbnails'):
        os.makedirs(curren_path+'photo/Thumbnails') 
    if not os.path.exists(curren_path+'JSON_INFO_MP3'):
        os.makedirs(curren_path+'JSON_INFO_MP3') 
    print('[+][Folder created!]')    
    
async def save_json(a, j): #this method save json info
    folder = curren_path+'JSON_INFO_MP3'
    if not os.path.exists(folder):
        os.makedirs(folder)
    try: # a: name of ID / j: json str
        with open(f"{curren_path}JSON_INFO_MP3/{a}.json", "w") as json_file:
            # SAVE JSON FILE TO HAVE INFO ABOUT SOUND
            json_file.write(json.dumps(j))
            print('[+][JSON SAVE]')
    except Exception as e:
        print("[-][ERROR JSON SAVE]", e)

# commands for download video
# @deprecated(reason="added video choice") 
commands_video = ['-video', 'video', '-v', 'видео', '-в', '-видео', 'v', 'в']

def str_buf_fix(s):
    trans_table = str.maketrans('$', 'S', '"<>:/\\|?*')
    s = s.translate(trans_table)
    # some bugfix
    # s.translate(str.maketrans("$", "S"))
    return s

def get_args(m : str):
    # dict pasrsing
    commands = {"link": '', "video": False, "group": ''}
    # trim and delete spaces between words
    list_str = " ".join(m.split()).split(" ")
    commands['link'] = list_str[0].replace('&feature=share', '')
    # @deprecated(reason="added video choice") 
    if len(list_str) > 1:
        # for chekinig #
        print('[Video command]', '[',list_str[1], ']')
        if list_str[1].lower() in commands_video:
            commands['video'] = True
        else:
            commands['video'] = False
            print("INVALID VIDEO COMMAND")
    # @deprecated(reason="added group choice")         
    if len(list_str) > 2:
        commands['group'] = list_str[2]
    print('[+][ARG]')    
    return commands

async def send_video(message, bot, file_id=''):
    duration = None
    file_name = ''
    thumbnail = None
    width = None
    height = None
    with open(f"{curren_path}JSON_INFO_MP3/{file_id}.json", "r") as file:
        json_info = json.loads(file.read())
        file_name += json_info['title']
        try:
            width = int(json_info['width'])
            height = int(json_info['height'])
            print('[+][RES]', end='')
        except Exception as e:
            print('[-][ERROR WIDTH AND HEIGHT]')
        try:
            if width > height:
                thumbnail = FSInputFile(f'{curren_path}photo/Thumbnails/{file_id}.jpeg')
            print('[+][THUMB]', end='')    
        except Exception as e:
            print('[-][VIDEO THUMBNAIL ERROR]', e)
        try:
            duration = int(json_info['duration'])
            print('[+][DUR]', end='')   
        except Exception as e:
            print('[-][ERROR DURATION VIDEO INFO]')    
    print('[+][START SENDING]')
    try:
        video_file = f'{curren_path}video/{str_buf_fix(file_name)}.mp4'    
        video = FSInputFile(video_file)
        # thumbnail = FSInputFile(f'{curren_path}киркоров.jpg')
        await bot.send_video(
            chat_id=message.chat.id, 
            video=video, 
            width=width, 
            height=height,
            duration=duration,
            thumbnail=thumbnail) 
        print("[+][DONE SENDING]", datetime.datetime.now())
        try:
            if del_file:
                os.remove(f'{curren_path}video/{str_buf_fix(file_name)}.mp4')
                print('[+][VIDEO FILE DELETED]')
        except Exception as e:
            print('[ERR OF DEL]')
    except Exception as e:
        await bot.send_message(message.chat.id, "ERROR SENDING")
        await bot.send_message(message.chat.id, "WE ARE WORKING ON THIS PROBLEM. SORRY. =(")
        print("[-][ERROR SENDING]", e)

async def send_audio(message, bot, file_id, group=''):
    file_name = ""
    thumbnail = None
    with open(f"{curren_path}JSON_INFO_MP3/{file_id}.json", "r") as file:
        json_info = json.loads(file.read())
        file_name += json_info['title']
    print('[+][START SENDING]')
    try:
        audio_file = f'{curren_path}media_from_yt/{str_buf_fix(file_name)}.mp3'
        audio = FSInputFile(audio_file)
        try:
            thumbnail = FSInputFile(f'{curren_path}photo/Thumbnails/{file_id}.jpeg')
        except Exception as e:
            print('[-][TRHUMBNAIL AUDIO MESSAGE ERROR]')    
        await bot.send_audio(message.chat.id, audio, thumbnail=thumbnail)
        if group != '':
            try:
                # Not working, err on telebot api, IN AIOGRAM IT WORKING
                await bot.send_audio(chat_id=f'@{group}', audio=audio, thumbnail=thumbnail)
            except Exception as e:
                await bot.send_message(chat_id=message.chat.id, text=str(e))
                print('[Ошибка отправки в группу!]', e)
        try:
            if del_file:
                os.remove(f'{curren_path}media_from_yt/{str_buf_fix(file_name)}.mp3')
                print('[+][FILE DELETED]')
        except Exception as e:
            print('[-][ERR OF FILE DELETE]')
    except Exception as e:
        await bot.send_message(message.chat.id, "ERROR SENDING")
        await bot.send_message(message.chat.id, "WE ARE WORKING ON THIS PROBLEM. SORRY. =(\nTRY AGAIN LATER")
        print("[-][ERROR SENDING]", e)

async def download_media(URL, is_video=False):
    some_var = ''
    error_message = ''    
    file_name = ''
    file_id = ''
    try:
        with yt_dlp.YoutubeDL() as ydl:
            some_var = ydl.sanitize_info(ydl.extract_info(URL, download=False))
            # WE GET TITLE AND ID FROM LINK
            file_name += some_var['title']
            file_id += some_var['id']
            await save_json(file_id, some_var)
    except Exception as e:
            print("[CAN'T GET JSON FROM LINK]", e)        
    if is_video:
        print("[+][DOWNLOADING VIDEO]")
        try:
            quality = 'b' # best
            if SITE_1 in URL:
                quality = 'w' # worst
            cmd = str(f'yt-dlp -f {quality} '+
                      # f'-S "filesize:50M" '+ #max file size around 50 Mb
                      f'--max-filesize 50M '+ # KOSTYL for tg
                      f'-P "{curren_path}video" '+
                      f'-o "{str_buf_fix(file_name)}.mp4" '+ 
                      f'"{URL}"')
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            print(cmd)
            print("[+][DOWNLOAD VIDEO COMPLETE]")
            print(f'[+][STDOUT] - {stdout.decode("utf-8")}, \n[!][ERRORS] - {stderr.decode("utf-8")}')
            try:
                l = some_var['thumbnails'][10]['url']               # l is link to image of this sound
                print('[_][DOWNLOADING VIDEO THUMBNAIL]')
                # DOWNLOAD AND SAVE IMAGE
                resource = urllib.request.urlopen(l)
                with open(f'{curren_path}photo/Thumbnails/{file_id}.jpeg', 'wb') as file:
                    file.write(resource.read())
                print("[+][DOWNLOAD THUMBNAIL VIDEO IMAGE COMPLETE]")    
            except Exception as e:
                print("[-][ERR DOWNLOAD THUMBNAIL VIDEO IMAGE]", e)
            if 'File is larger than max-filesize' in str(stdout):
                error_message = str(f'<pre>File is larger than 50 Mb\n'+
               'Боты в настоящее время могут отправлять файлы любого типа размером до 50 МБ, '+
               'поэтому да, очень большие файлы пока не будут работать. Извини. '+
               'Этот лимит может быть изменен в будущем.</pre>')
                try:
                    os.remove(f'{curren_path}video/{str_buf_fix(file_name)}.mp4.part')
                    print('[+][VIDEO PART-FILE DELETED]')
                except Exception as e:
                    print('[ERROR PART FILE DELETING]', e)
                print(error_message)
        except Exception as e:
            print("[-][ERROR DOWNLOAD VIDEO FILE ON async def download_media()]", e)
    else:
        l = some_var['thumbnails'][5]['url']               # l is link to image of this sound
        print("[+][DOWNLOADING AUDIO]")
        try:
            print('[_][DOWNLOADING AUDIO THUMBNAIL]')
            # DOWNLOAD AND SAVE IMAGE
            resource = urllib.request.urlopen(l)
            with open(f'{curren_path}photo/Thumbnails/{file_id}.jpeg', 'wb') as file:
                file.write(resource.read())
            print("[+][DOWNLOAD THUMBNAIL IMAGE COMPLETE]")    
        except Exception as e:
            print("[-][ERR DOWNLOAD IMAGE]", e)
        try:
            cmd = str(f'yt-dlp -f ba '+
                      f'-o "{str_buf_fix(file_name)}" '+
                      f'--max-filesize 50.0M '+ # KOSTYL
                      f'-x --audio-quality 0 '+
                      f'-x --audio-format mp3 '+# using ffmpeg.exe for Windows# 
                      f'-P {curren_path}media_from_yt '+ # path
                      f'"{URL}"')  # link
            # os.system(cmd)  
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            print("[+][DOWNLOAD AUDIO COMPLETE]")
            print(f'[+][STDOUT] - {stdout.decode("utf-8")}, \n[!][ERRORS] - {stderr.decode("utf-8")}')
            if 'File is larger than max-filesize' in str(stdout):
                error_message = str(f'<pre>File is larger than 50 Mb\n'+
               'Боты в настоящее время могут отправлять файлы любого типа размером до 50 МБ, '+
               'поэтому да, очень большие файлы пока не будут работать. Извини. '+
               'Этот лимит может быть изменен в будущем.</pre>')
                print(error_message)
        except Exception as e:
            print("[-][ERROR DOWNLOAD AUDIO FILE ON async def download_media()]", e)
        await mp3_tag_editor.tag_edit(file_id)
    return file_id, error_message            

async def delete_file(max_day=3, folder_path = 'JSON_INFO_MP3'):
    folder_path = curren_path+folder_path
    print(folder_path)
    now = time.time()
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                if os.stat(file_path).st_mtime < now - max_day * 86400:
                    os.remove(file_path)
                    print(f'[DELETE FILE]: {file_path}')
    except Exception as e:
        print(f'[NO DIR: {folder_path}]')

async def show_cat(message: Message, bot: Bot):
    async with ChatActionSender.upload_photo(chat_id=message.chat.id, bot=bot):
        try:
            cat_image_path = curren_path+f'photo/Cats/cat{random.randint(1, 7)}.jpeg'
            image = FSInputFile(cat_image_path)
            await bot.send_photo(message.chat.id, image)
        except Exception as e:
            print('[CAT IMAGE ERROR]')
            await bot.send_message(message.chat.id, "нима котика")