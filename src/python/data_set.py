from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup

# KOSTYL 
class TemporaryCache:
    def __init__(self):
        self.cache = {}

    async def add_to_cache(self, key, value):
        self.cache[key] = value

    async def get_from_cache(self, key):
        return self.cache.get(key, None)
    
    async def remove_from_cache(self, key):
        if key in self.cache:
            del self.cache[key]

class SelecMediaDownloader(CallbackData, prefix=''):
    media_type: str
    key: str

class FeedbackForm(StatesGroup):
    RECEIVING_FEEDBACK = State()