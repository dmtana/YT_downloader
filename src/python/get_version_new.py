import subprocess
import requests
from aiogram import __version__ as aio_ver

async def get_version_new():
    version = ''
    try:
        res = subprocess.run('pip show yt_dlp', shell=True, capture_output=True, text=True)
        var = res.stdout.split('\n')
        yt_dlp_ver = ''
        for _ in var:
            if 'Version' in _ or 'Name' in _ :
                yt_dlp_ver += _+' '
        yt_dlp_ver = yt_dlp_ver.replace('Version: ', '')
        yt_dlp_ver = yt_dlp_ver.replace('Name: ', '')
        is_latest = ''
        try:
            is_latest += await version_of_yt_dlp('please update the libraries')
        except Exception as e:
            print(e)
        yt_dlp_ver += is_latest+'\n'
        is_latest = ''
        res = subprocess.run('pip show aiogram', shell=True, capture_output=True, text=True)
        var = res.stdout.split('\n')
        aiogram_ver = ''
        for _ in var:
            if 'Version' in _ or 'Name' in _ :
                aiogram_ver += _+' '
        aiogram_ver = aiogram_ver.replace('Version: ', '')
        aiogram_ver = aiogram_ver.replace('Name: ', '')
        try:
            is_latest += await version_of_aiogram('please update the libraries')
        except Exception as e:
            print(e)      
        version=yt_dlp_ver+aiogram_ver+is_latest
    except Exception as e:
        print(e)   
    print('[+][get_version]')     
    return version

async def version_of_aiogram(msg : str):
    version = aio_ver
    url = 'https://github.com/aiogram/aiogram/releases/latest'
    response = requests.get(url)
    final_url = response.url
    new_line = ''
    for _ in final_url[::-1]:
        if _ == '/':
            break
        else:
            new_line += _
    latest_version = new_line[::-1].replace('v','')
    if latest_version == version:
        return '<i>(Latest)</i>'
    else: 
        return f'<i>(A new version is available: {latest_version}\n{msg})</i>'

async def version_of_yt_dlp(msg : str):
    # url of yt-dlp lib on github
    version = subprocess.run('yt-dlp --version', shell=True, capture_output=True, text=True)
    url = 'https://github.com/yt-dlp/yt-dlp/releases/latest'
    response = requests.get(url)
    final_url = response.url
    new_line = ''
    for _ in final_url[::-1]:
        if _ == '/':
            break
        else:
            new_line += _
    latest_version = new_line[::-1]
    if latest_version == version.stdout.replace('\n', ''):
        return '<i>(Latest)</i>'
    else: 
        return f'<i>(A new version is available: {latest_version}\n{msg})</i>'