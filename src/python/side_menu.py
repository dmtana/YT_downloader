from config import VERSION

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start', 
            description="Bot start"
        ),
        BotCommand(
            command='help', 
            description="How to use"
        ),
        BotCommand(
            command='feedback',
            description='Leave feedback to the author'
        ),
        BotCommand(
            command='version',
            description=VERSION
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())