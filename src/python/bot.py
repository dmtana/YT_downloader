import asyncio
import helper
from telebot.async_telebot import AsyncTeleBot

def get_token():
    try:
        with open("token.txt", "r") as token:
            return str(token.read())
    except:
        print("CAN'T READ TOKEN!!! BOT STOPPED!!!")

hello_str = "Я бот для скачивания музыки с YouTube, просто пришли мне ссылку и я отправлю тебе аудиофайл"

bot = AsyncTeleBot(get_token())

@bot.message_handler(commands=["start"])
async def start(message):
    str = f"Привет, {message.from_user.first_name}. \n"
    await bot.send_message(message.chat.id, str + hello_str)

@bot.message_handler(content_types=["text"])
async def echo(message):
    message_info = None
    args = helper.get_args(message.text)
    print(message.text)
    try:
        if "https://" in args['link']:
            message_info = await bot.send_message(message.chat.id, "Downloading")
            if args['video'] is False:
                file_id = await helper.download_audio(args['link'])
                await bot.delete_message(message.chat.id, message_info.message_id)
                message_info = await bot.send_message(message.chat.id, "Download complete")
                await helper.send_audio(message=message, bot=bot, file_id=file_id, group=args['group'])
            elif args['video'] is True:
                await helper.download_video(args['link'])
                await bot.delete_message(message.chat.id, message_info.message_id)
                message_info = await bot.send_message(message.chat.id, "Download complete")
                await helper.send_video(message, bot)
            await bot.delete_message(message.chat.id, message_info.message_id)
        elif message.text.lower() in helper.cat:
            await helper.show_cat(message, bot)
            print("мяу", end=" ")
        else:
            await bot.send_message(message.chat.id, "Введите пожалуйста ссылку в формате 'https://...'")
            print(message.chat.type)
            print("ERROR INPUT")
    except Exception as e:
        await bot.delete_message(message.chat.id, message_info.message_id)
        await bot.send_message(message.chat.id, "ERROR INPUT, WRONG LINK")
        print("ERROR IN MAIN PACKAGE", e)

# BOT in multithread
# run non-stop
print("BOT STARTED")
asyncio.run(bot.polling(non_stop=True))
