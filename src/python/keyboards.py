from aiogram.utils.keyboard import InlineKeyboardBuilder
from data_set import SelecMediaDownloader
from config.config import ADMINS_ID

async def select_media_type(key: str, user_id=None):
    kb = InlineKeyboardBuilder()

    kb.button(text="AUDIO", callback_data=SelecMediaDownloader(media_type='audio', key=key))
    kb.button(text="VIDEO", callback_data=SelecMediaDownloader(media_type='video', key=key))
    
    if user_id in ADMINS_ID:
        kb.button(text="MUSIC", callback_data=SelecMediaDownloader(media_type='music', key=key))
        kb.button(text="RELAX", callback_data=SelecMediaDownloader(media_type='relax', key=key))
        kb.button(text="ROCK", callback_data=SelecMediaDownloader(media_type='rock', key=key))

        kb.adjust(2,3)
        return kb.as_markup()
    else:    
        kb.adjust(2)
        return kb.as_markup()