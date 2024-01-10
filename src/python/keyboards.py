from aiogram.utils.keyboard import InlineKeyboardBuilder
from data_set import User, SelecMediaDownloader
from config import ADMIN_ID, ADMIN_ID2

async def select_media_type(key: str, user_id=None):
    kb = InlineKeyboardBuilder()

    kb.button(text="Audio", callback_data=SelecMediaDownloader(media_type='audio', key=key))
    kb.button(text="Video", callback_data=SelecMediaDownloader(media_type='video', key=key))
    
    if user_id in [ADMIN_ID,ADMIN_ID2]:
        kb.button(text="MUSIC", callback_data=SelecMediaDownloader(media_type='music', key=key))
        kb.button(text="RELAX", callback_data=SelecMediaDownloader(media_type='relax', key=key))
        kb.button(text="ROCK", callback_data=SelecMediaDownloader(media_type='rock', key=key))

        kb.adjust(2,3)
        return kb.as_markup()
    else:    
        kb.adjust(2)
        return kb.as_markup()

async def language_select_start_command():
    kb = InlineKeyboardBuilder()

    kb.button(text="English", callback_data=User(USER_NAME='name', LANGUAGE="english"))
    kb.button(text="Русский", callback_data=User(USER_NAME='name', LANGUAGE="russian"))

    kb.adjust(2)
    return kb.as_markup()