from mutagen.id3 import ID3, TIT2, TALB, TPE1, TCON, TDRC, APIC
import os
import json
import ssl

# fix for .venv python
curren_path = os.path.dirname(__file__)+'/'

# crutch for MacOS BADYLLLLL =D
ssl._create_default_https_context = ssl._create_unverified_context

def str_buf_fix(s):
    trans_table = str.maketrans('', '', '"<>:/\\|?*')
    s = s.translate(trans_table)
    return s

async def tag_edit(id):
    folder_name = 'JSON_INFO_MP3'
    try:
        if not os.path.exists(curren_path+folder_name):
            os.makedirs(curren_path+folder_name)
        # read tag from json info
        with open(f"{curren_path+folder_name}/{id}.txt", "r") as file:
            ###   GET INFO FROM JSON   ###
            json_info = json.loads(file.read())
            title = json_info['title']
            # EDIT TAG
            audiofile = ID3(f"{curren_path}media_from_yt/{str_buf_fix(title)}.mp3")

            try:
                artist = json_info['artist']
                album = json_info['album']
                track = json_info['track']
                release_year = json_info['release_year']

                audiofile.add(TIT2(encoding=3, text=track))
                audiofile.add(TALB(encoding=3, text=album))
                audiofile.add(TPE1(encoding=3, text=artist))
                audiofile.add(TCON(encoding=3, text=""))  # genre
                audiofile.add(TDRC(encoding=3, text=str(release_year)))
                # EDIT IMAGE
                with open(f"{curren_path}photo/Thumbnails/{id}.jpeg", "rb") as album_art:
                    audiofile.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=album_art.read()))
            except Exception as e:
                print("[BAD ATTRIBUTES]", e)
                try:
                    audiofile.add(TIT2(encoding=3, text=str_buf_fix(title)))
                except Exception as e:
                    print("[BAD ATTRIBUTES: 2]", e)
            # SAVE TAG
            audiofile.save()

    except Exception as e:
        print('[NO MP3 TAG]', e)