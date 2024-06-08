import asyncio
import os
import time

# fix for .venv py
curren_path = os.path.dirname(__file__)+'/'


async def create_folders():
    try:
        if not os.path.exists(curren_path+'video'):
            os.makedirs(curren_path+'video')
        if not os.path.exists(curren_path+'media_from_yt'):
            os.makedirs(curren_path+'media_from_yt') 
        if not os.path.exists(curren_path+'photo/Thumbnails'):
            os.makedirs(curren_path+'photo/Thumbnails') 
        if not os.path.exists(curren_path+'JSON_INFO_MP3'):
            os.makedirs(curren_path+'JSON_INFO_MP3') 
        print('[bot][+][Folder created!]')  
    except Exception as e:
        print(f'[ERROR CREATING FOLDERS] - {str(e)}')


async def clear_cache(seconds=86400):
    '''
        Clear cache every 24 hours 
    '''
    while True:
        try:
            await delete_file()
            await delete_file(1, 'photo/Thumbnails')
            await delete_file(1, 'video')
        except Exception as e:
            print(f'[ERROR CLEANING CACHE] - {str(e)}')
        await asyncio.sleep(seconds)


async def delete_file(max_day=3, folder_path='JSON_INFO_MP3'):
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
        print(f'[bot][NO DIR: {folder_path}]', e)        