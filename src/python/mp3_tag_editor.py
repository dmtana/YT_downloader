from mutagen.id3 import ID3, TIT2, TALB, TPE1, TCON, TDRC, APIC
import json


async def tag_edit(id, media_folder):
    '''
    :param id: like 'Qk1ymCm0tLI'
    :param media_folder: like '390352383'
    :return: None
    '''
    try:
        # read tag from json info
        with open(f"JSON_INFO_MP3/{id}.txt", "r") as file:
            ###   GET INFO FROM JSON   ###
            json_info = json.loads(file.read())
            title = json_info['title']
            # EDIT TAG
            audiofile = ID3(f"media_from_yt/{media_folder}/{title} [{id}].mp3")

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
                with open(f"photo/Thumbnails/{id}.jpeg", "rb") as album_art:
                    audiofile.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=album_art.read()))
            except Exception as e:

                print("881", e)
            try:
                audiofile.add(TIT2(encoding=3, text=title))
            except Exception as e:
                print("882", e)
            # SAVE TAG
            audiofile.save()

    except Exception as e:
        print(997, e)