import subprocess

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
        yt_dlp_ver += '\n'
        res = subprocess.run('pip show aiogram', shell=True, capture_output=True, text=True)
        var = res.stdout.split('\n')
        aiogram_ver = ''
        for _ in var:
            if 'Version' in _ or 'Name' in _ :
                aiogram_ver += _+' '
        aiogram_ver = aiogram_ver.replace('Version: ', '')
        aiogram_ver = aiogram_ver.replace('Name: ', '')        
        version=yt_dlp_ver+aiogram_ver
    except Exception as e:
        print(e)    
    return version