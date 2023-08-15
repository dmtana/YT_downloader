import yt_dlp
import mp3_tag_editor
import os
import urllib.request
import json
import random
import datetime
import time

# easter egg
cat = ['котик', 'кися', 'котейка', 'кот', 'рыжик', 'рыжня', 'котэ', 'кисан', 'кисан кисан', 'кс кс', 'мяу', 'cэми']
del_file = True

async def save_json(a, j): #this method save json info
    folder = 'JSON_INFO_MP3'
    if not os.path.exists(folder):
        os.makedirs(folder)
    try: # a: name of ID / j: json str
        with open(f"JSON_INFO_MP3/{a}.txt", "w") as json_file:
            # SAVE JSON FILE TO HAVE INFO ABOUT SOUND
            json_file.write(json.dumps(j))
            print('[+][JSON SAVE]')
    except Exception as e:
        print("[-][ERROR JSON SAVE]", e)

# commands for download video
commands_video = ['-video', 'video', '-v', 'видео', '-в', '-видео', 'v', 'в']

def str_buf_fix(s):
    trans_table = str.maketrans('$', 'S', '"<>:/\\|?*')
    s = s.translate(trans_table)
    # some bugfix
    # s.translate(str.maketrans("$", "S"))
    return s

def get_args(m):
    # dict pasrsing
    commands = {"link": '', "video": False, "group": ''}
    # trim and delete spaces between words
    list_str = " ".join(m.split()).split(" ")
    commands['link'] = list_str[0].replace('&feature=share', '')
    if len(list_str) > 1:
        # for chekinig #
        print('[Video command]', '[',list_str[1], ']')
        if list_str[1].lower() in commands_video:
            commands['video'] = True
        else:
            commands['video'] = False
            print("INVALID VIDEO COMMAND")
    if len(list_str) > 2:
        commands['group'] = list_str[2]
    print('[+][ARG]')    
    # print(commands)
    return commands

async def send_video(message, bot, file_id=''):
    file_name = ""

    with open(f"JSON_INFO_MP3/{file_id}.txt", "r") as file:
        json_info = json.loads(file.read())
        file_name += json_info['title']
    print('[+][START SENDING]')

    try:
        with open(f'video/{str_buf_fix(file_name)}.mp4', 'rb') as video:
            await bot.send_document(message.chat.id, video)
        print("[+][DONE SENDING]", datetime.datetime.now())
        try:
            if del_file:
                os.remove(f'video/{str_buf_fix(file_name)}.mp4')
                print('[+][VIDEO FILE DELETED]')
        except Exception as e:
            print('[ERR OF DEL]')
    except Exception as e:
        await bot.send_message(message.chat.id, "ERROR SENDING")
        await bot.send_message(message.chat.id, "WE ARE WORKING ON THIS PROBLEM. SORRY. =(")
        print("[-][ERROR SENDING]", e)

async def send_audio(message, bot, file_id, group=''):
    file_name = ""
    with open(f"JSON_INFO_MP3/{file_id}.txt", "r") as file:
        json_info = json.loads(file.read())
        file_name += json_info['title']
    print('[+][START SENDING]')
    try:
        with open(f'media_from_yt/{str_buf_fix(file_name)}.mp3', 'rb') as audio:
            await bot.send_audio(message.chat.id, audio)
            if group != '':
                try:
                    # Not working, err on telebot api
                    await bot.send_audio(chat_id=f'@{group}', audio=audio)
                except Exception as e:
                    print('[Ошибка отправки в группу!]', e)
        print("[+][DONE SENDING]", f'[{datetime.datetime.now()}]', sep='\n')
        try:
            if del_file:
                os.remove(f'media_from_yt/{str_buf_fix(file_name)}.mp3')
                print('[+][FILE DELETED]')
        except Exception as e:
            print('[-][ERR OF FILE DELETE]')
    except Exception as e:
        await bot.send_message(message.chat.id, "ERROR SENDING")
        await bot.send_message(message.chat.id, "WE ARE WORKING ON THIS PROBLEM. SORRY. =(")
        print("[-][ERROR SENDING]", e)

async def download_media(URL, is_video=False):
    # Folder for album covers, if not exist
    folder = 'photo/Thumbnails'
    if not os.path.exists(folder):
        os.makedirs(folder)
    # chat_id - folder
    file_name = ""
    file_id = ""
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
            os.system(f'yt-dlp -f mp4 -P video -o "{str_buf_fix(file_name)}.mp4" {URL}')
            print("[+][DOWNLOAD VIDEO COMPLETE]")
        except Exception as e:
            print("[-][ERR DOWNLOAD]")
    else:
        l = some_var['thumbnails'][5]['url']               # l is link to image of this sound
        print("[+][DOWNLOADING AUDIO]")
        try:
            # DOWNLOAD AND SAVE IMAGE
            resource = urllib.request.urlopen(l)
            with open(f'photo/Thumbnails/{file_id}.jpeg', 'wb') as file:
                file.write(resource.read())
        except:
            print("[ERR DOWNLOAD IMAGE]")
        try:
            os.system(f'yt-dlp -f ba -o "{str_buf_fix(file_name)}" -x --audio-quality 0 -x --audio-format mp3 ' # using ffmpeg.exe # 
                      f'-P media_from_yt '  # path
                      f'"{URL}"')  # link
            print("[+][DOWNLOAD AUDIO COMPLETE]")
        except Exception as e:
            print("[-][ERR DOWNLOAD]")
        await mp3_tag_editor.tag_edit(file_id)
    return file_id            

async def delete_file(max_day=3, folder_path = 'JSON_INFO_MP3'):
    now = time.time()
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                if os.stat(file_path).st_mtime < now - max_day * 86400:
                    os.remove(file_path)
                    print(f'[DELETE FILE]: {file_path}')
    except Exception as e:
        print('[NO DIR: JSON_INFO_MP3]')

async def show_cat(message, bot):
    try:
        with open(f'photo/Cats/cat{random.randint(1, 7)}.jpeg', 'rb') as photo:
            await bot.send_photo(message.chat.id, photo)
    except Exception as e:
        await bot.send_message(message.chat.id, "нима котика")