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
import cv2
import random

from PIL import Image
from aiogram import Bot
from aiogram.types import Message, FSInputFile
from aiogram.utils.chat_action import ChatActionSender

from config.config import SITE_1

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
    print('[bot][+][Folder created!]')    
    
async def save_json(a, j): #this method save json info
    folder = curren_path+'JSON_INFO_MP3'
    if not os.path.exists(folder):
        os.makedirs(folder)
    try: # a: name of ID / j: json str
        with open(f"{curren_path}JSON_INFO_MP3/{a}.json", "w") as json_file:
            # SAVE JSON FILE TO HAVE INFO ABOUT SOUND
            json_file.write(json.dumps(j))
            print('[bot][+][JSON SAVE]')
            return True
    except Exception as e:
        print("[bot][-][ERROR JSON SAVE]", e)

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
    print('[bot][+][ARG]')    
    return commands

async def send_video(message, bot, file_id='', group=''):
    duration = None
    file_name = ''
    thumbnail = None
    width = None
    height = None
    with open(f"{curren_path}JSON_INFO_MP3/{file_id}.json", "r") as file:
        json_info = json.loads(file.read())
        file_name += json_info['id']
        try:
            width = int(json_info['width'])
            height = int(json_info['height'])
            print('[bot][+][RES]', end='')
        except Exception as e:
            print('[bot][-][ERROR WIDTH AND HEIGHT]')
        try:
            thumbnail = FSInputFile(f'{curren_path}photo/Thumbnails/{file_id}.jpeg')
            print('[bot][+][THUMB]', end='')
            try:
                if os.path.getsize(f'{curren_path}photo/Thumbnails/{file_id}.jpeg') / 1024 > 200: # tg limit for thumbnail
                    await compress_image(f'{curren_path}photo/Thumbnails/{file_id}.jpeg', f'{curren_path}photo/Thumbnails/{file_id}_edited.jpeg')
                    thumbnail = FSInputFile(f'{curren_path}photo/Thumbnails/{file_id}_edited.jpeg')
            except Exception as e:
                print('[helper][X][ERROR CONVERTER ON SEND_VIDEO]', e)
        except Exception as e:
            print('[bot][-][VIDEO THUMBNAIL ERROR]', e)
        try:
            duration = int(json_info['duration'])
            print('[bot][+][DUR]', end='')   
        except Exception as e:
            print('[bot][-][ERROR DURATION VIDEO INFO]')    
    print('[bot][+][START SENDING]')
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
        print("[bot][+][DONE SENDING AS VIDEO]", datetime.datetime.now())
    except Exception as e:
        print("[bot][X][ERROR SENDING AS VIDEO FILE]", e)
        try:
            video_file = f'{curren_path}video/{str_buf_fix(file_name)}.mp4'    
            video = FSInputFile(video_file)
            await bot.send_document(chat_id=message.chat.id, document=video)
            print("[bot][+][DONE SENDING AS DOCUMENT]", datetime.datetime.now())
        except Exception as e:
            pass
            await bot.send_message(message.chat.id, f"ERROR SENDING\nWE ARE WORKING ON THIS PROBLEM. SORRY. =(\n{str(e)}")
            print("[bot][X][ERROR SENDING AS DOCUMENT]", e)
    try:
        if del_file:
            os.remove(f'{curren_path}video/{str_buf_fix(file_name)}.mp4')
            print('[bot][+][VIDEO FILE DELETED]')
    except Exception as e:
        print('[bot][X][ERR OF DEL]')

async def send_voice(message, bot, file_id, group=''):
    send_audio_status = 0
    file_name = ""
    duration = None
    with open(f"{curren_path}JSON_INFO_MP3/{file_id}.json", "r") as file:
        json_info = json.loads(file.read())
        file_name += json_info['title']
        try:
            duration = json_info['duration']
        except Exception as e:
            print('[bot][X][DURATION GETING ERROR FOR VOICE]')
    print('[bot][+][START SENDING VOICE]')
    try:
        cmd = str(f'ffmpeg -i "{curren_path}media_from_yt/{str_buf_fix(file_name)}.mp3" -c:a libopus -b:a 32k -vbr on -compression_level 10 -frame_duration 60 -application voip "{curren_path}media_from_yt/{str_buf_fix(file_name)}.opus"')
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        print(f'[cmd][+][STDOUT]'+'\n'+f'{stdout.decode("utf-8")}'+
                f'[cmd][!][ERRORS]'+'\n'+f'{stderr.decode("utf-8")}')
        print('[cmd][+][DONE CONVERTING]')
    except Exception as e:
        print('[cmd][X][ERR CONVERTING]', e)    
    try:
        audio_file = f'{curren_path}media_from_yt/{str_buf_fix(file_name)}.opus'
        audio = FSInputFile(audio_file)
        try:
            await bot.send_voice(message.chat.id, voice=audio, duration=duration)
        except Exception as e:
            print('[bot][X][ERROR AUDIO SENDING]', e)
            if 'VOICE_MESSAGES_FORBIDDEN' in str(e):
                await bot.send_message(chat_id=message.chat.id, text=f'This users privacy settings forbid you from sending voice messages. {str(e)}')
            try:
                await bot.send_document(message.chat.id, audio)
            except Exception as e:
                print("[bot][X][ERROR SENDING VOICE AS DOCUMENT]", e)
        if group != '':
            try:
                await bot.send_voice(chat_id=f'@{group}', voice=audio, duration=duration)
                send_audio_status = 6
            except Exception as e:
                print('[bot][X][ERROR GROUP VOICE SENDING]', e)
                await bot.send_message(chat_id=message.chat.id, text=str(e))
                print('[Ошибка отправки в группу!]', e)
                try:
                    await bot.send_document(chat_id=f'@{group}', document=audio)
                except Exception as e:
                    print('[bot][X][ERROR GROUP VOICE SENDING AS DOCUMENT]', e)
        try:
            if del_file:
                os.remove(f'{curren_path}media_from_yt/{str_buf_fix(file_name)}.mp3')
                os.remove(f'{curren_path}media_from_yt/{str_buf_fix(file_name)}.opus')
                print('[bot][+][FILE DELETED]')
        except Exception as e:
            print('[bot][X][ERR OF FILE DELETE]')
    except Exception as e:
        await bot.send_message(message.chat.id, f"ERROR SENDING\nWE ARE WORKING ON THIS PROBLEM. SORRY. =(\nTRY AGAIN LATER\n{str(e)}")
        print("[bot][X][ERROR SENDING]", e)
    return send_audio_status   

async def send_audio(message, bot, file_id, group=''):
    send_audio_status = 0
    file_name = ""
    duration = None
    thumbnail = None
    with open(f"{curren_path}JSON_INFO_MP3/{file_id}.json", "r") as file:
        json_info = json.loads(file.read())
        file_name += json_info['title']
        try:
            duration = json_info['duration']
        except Exception as e:
            print('[bot][X][DURATION GETING ERROR]')
    print('[bot][+][START SENDING]')
    try:
        audio_file = f'{curren_path}media_from_yt/{str_buf_fix(file_name)}.mp3'
        audio = FSInputFile(audio_file)
        try:
            thumbnail = FSInputFile(f'{curren_path}photo/Thumbnails/{file_id}.jpeg')
        except Exception as e:
            print('[bot][X][TRHUMBNAIL AUDIO MESSAGE ERROR]')
        try:
            await bot.send_audio(message.chat.id, audio=audio, thumbnail=thumbnail, duration=duration)
        except Exception as e:
            print('[bot][X][ERROR AUDIO SENDING]', e)
            try:
                await bot.send_document(message.chat.id, audio)
            except Exception as e:
                print("[bot][X][ERROR SENDING AUDIO AS DOCUMENT]", e)
        if group != '':
            try:
                await bot.send_audio(chat_id=f'@{group}', audio=audio, thumbnail=thumbnail, duration=duration)
                send_audio_status = 6
            except Exception as e:
                print('[bot][X][ERROR GROUP AUDIO SENDING]', e)
                await bot.send_message(chat_id=message.chat.id, text=str(e))
                print('[Ошибка отправки в группу!]', e)
                try:
                    await bot.send_document(chat_id=f'@{group}', document=audio, thumbnail=thumbnail)
                except Exception as e:
                    print('[bot][X][ERROR GROUP AUDIO SENDING AS DOCUMENT]', e)
        try:
            if del_file:
                os.remove(f'{curren_path}media_from_yt/{str_buf_fix(file_name)}.mp3')
                print('[bot][+][FILE DELETED]')
        except Exception as e:
            print('[bot][X][ERR OF FILE DELETE]')
    except Exception as e:
        await bot.send_message(message.chat.id, f"ERROR SENDING\nWE ARE WORKING ON THIS PROBLEM. SORRY. =(\nTRY AGAIN LATER\n{str(e)}")
        print("[bot][X][ERROR SENDING]", e)
    return send_audio_status

async def download_media(URL, is_video=False):
    some_var = '' # JSON info from yt-dlp lib
    error_message = ''    
    file_name = ''
    file_id = ''
    done = 0
    while done < 15: # kostyl for facebook reels etc
        try:
            with yt_dlp.YoutubeDL() as ydl:
                print('yt-dlp 1')
                some_var = ydl.sanitize_info(ydl.extract_info(URL, download=False))
                # WE GET TITLE AND ID FROM LINK
                file_name = some_var['title']
                file_id = some_var['id']
                if await save_json(file_id, some_var):
                    done = 15
                print('yt-dlp 2')    
        except Exception as e:
                print("[bot][X][CAN'T GET JSON FROM LINK]", e)
        done += 1
    if is_video:
        done = 0
        while done < 15: # kostyl for facebook reels and tiktok
            print("[bot][DOWNLOADING VIDEO]")
            try:
                quality = 'b' # best
                if 'tiktok' in URL:
                    quality = '0'
                elif SITE_1 in URL:
                    quality = 'w' # worst
                cmd = str(f'yt-dlp -f {quality} '+
                        f'--max-filesize 50M '+ # KOSTYL for tg
                        f'-P "{curren_path}video" '+
                        f'-o "{str_buf_fix(file_id)}.mp4" '+
                        f'"{URL}"')
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                print(cmd)
                print("[bot][+][DOWNLOAD VIDEO COMPLETE]")
                print(f'[cmd][+][STDOUT]'+'\n'+f'{stdout.decode("utf-8")}'+
                      f'[cmd][!][ERRORS]'+'\n'+f'{stderr.decode("utf-8")}')
                if 'already been downloaded' in stdout.decode("utf-8"):
                    done = 15
                try:
                    video_path = f'{curren_path}video/{str_buf_fix(file_id)}.mp4'
                    cap = cv2.VideoCapture(video_path)
                    if not cap.isOpened():
                        print("err open file")
                    frame_number = random.choice([random.randint(0, 45), 0, 0]) # 0 will fall out 3 times more often, 0 means first frame
                    for i in range(frame_number + 1):
                        ret, frame = cap.read()
                        if not ret:
                            print(f"err reading frame {i+1}")
                    cap.release()
                    cv2.imwrite(f'{curren_path}photo/Thumbnails/{file_id}.jpeg', frame)
                    print("[bot][+][DOWNLOAD THUMBNAIL VIDEO IMAGE COMPLETE]")    
                except Exception as e:
                    print("[bot][X][ERR DOWNLOAD THUMBNAIL VIDEO IMAGE]", e)
                if 'File is larger than max-filesize' in str(stdout):
                    error_message = str(f'<pre>File is larger than 50 Mb\n'+
                'Боты в настоящее время могут отправлять файлы любого типа размером до 50 МБ, '+
                'поэтому да, очень большие файлы пока не будут работать. Извини. '+
                'Этот лимит может быть изменен в будущем.</pre>')
                    try:
                        os.remove(f'{curren_path}video/{str_buf_fix(file_id)}.mp4.part')
                        print('[bot][+][VIDEO PART-FILE DELETED]')
                    except Exception as e:
                        print('[bot][X][ERROR PART FILE DELETING]', e)
                    print(error_message)
            except Exception as e:
                print("[bot][X][ERROR DOWNLOAD VIDEO FILE ON async def download_media()]", e)
            done += 1
    else:
        link_thumbnail = some_var['thumbnails'][5]['url'] # link_thumbnail is link to image of this sound
        print("[bot][+][DOWNLOADING AUDIO]")
        try:
            # DOWNLOAD AND SAVE IMAGE
            resource = urllib.request.urlopen(link_thumbnail)
            with open(f'{curren_path}photo/Thumbnails/{file_id}.jpeg', 'wb') as file:
                file.write(resource.read())
            print("[bot][+][DOWNLOAD THUMBNAIL IMAGE COMPLETE]")    
        except Exception as e:
            print("[bot][X][ERR DOWNLOAD IMAGE]", e)
        try:
            cmd = str(f'yt-dlp -f ba '+
                      f'-o "{str_buf_fix(file_name)}" '+
                      f'--max-filesize 50.0M '+ # KOSTYL tg size 
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
            print("[bot][+][DOWNLOAD AUDIO COMPLETE]")
            print(f'[cmd][+][STDOUT]'+'\n'+f'{stdout.decode("utf-8")}'+
                  f'[cmd][!][ERRORS]'+'\n'+f'{stderr.decode("utf-8")}')
            if 'File is larger than max-filesize' in str(stdout):
                error_message = str(f'<pre>File is larger than 50 Mb\n'+
               'Боты в настоящее время могут отправлять файлы любого типа размером до 50 МБ, '+
               'поэтому да, очень большие файлы пока не будут работать. Извини. '+
               'Этот лимит может быть изменен в будущем.</pre>')
                print(error_message)
        except Exception as e:
            print("[bot][X][ERROR DOWNLOAD AUDIO FILE ON async def download_media()]", e)
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
                    print(f'[bot][DELETE FILE]: {file_path}')
    except Exception as e:
        print(f'[bot][NO DIR: {folder_path}]')

async def compress_image(input_path, output_path, target_size_kb = 200):
    try:
        with Image.open(input_path) as img:
            quality = 100
            while True:
                img.save(output_path, optimize=True, quality=quality)
                if os.path.getsize(output_path) / 1024 <= target_size_kb:
                    break
                quality -= 5
                if quality < 10:
                    break
    except Exception as e:
        print('[helper][X][CONVERT ERROR]', e)                     

async def show_cat(message: Message, bot: Bot):
    async with ChatActionSender.upload_photo(chat_id=message.chat.id, bot=bot):
        try:
            cat_image_path = curren_path+f'photo/Cats/cat{random.randint(1, 7)}.jpeg'
            image = FSInputFile(cat_image_path)
            await bot.send_photo(message.chat.id, image)
        except Exception as e:
            print('[bot][CAT IMAGE ERROR]')
            await bot.send_message(message.chat.id, "нима котика")