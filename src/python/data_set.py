from aiogram.filters.callback_data import CallbackData

# KOSTYL 
class TemporaryCache:
    def __init__(self):
        self.cache = {}

    async def add_to_cache(self, key, value):
        self.cache[key] = value

    async def get_from_cache(self, key):
        return self.cache.get(key, None)

class SelecMediaDownloader(CallbackData, prefix=''):
    media_type: str
    key: str
