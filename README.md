# YT_downloader
Simple bot for download music

This is simple telegram bot for download music from YouTube. Also you can download short video. 

Based on <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> library.

<h2>How to create your own YT_downloader bot</h2>

Fisrt off all you need to install <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> on youre computer PC or Linux or Mac. 
Then you need download <a href="https://github.com/aiogram/aiogram">aiogram</a> and <a href="https://ffmpeg.org/" class="link">ffmpeg</a>. 
You need to place ffmpeg.exe in the root of the project with the executable code if You have Windows. 
For Linux or Mac just install using terminal or <a href="https://brew.sh/">homebrew</a>. 

Get a bot token from a botfather. And start the bot.

<h3>Creation script for docker:</h3>

<pre >
#!/bin/bash

# create this script
# touch script.sh

# make it runneble
# chmod +x script.sh

# run script
# ./script.sh

echo "# Commands before start polling
# cd /app/YT_downloader/src/python/ && git pull && python3 bot.py

# Используем официальный образ Python
FROM python:3.8

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы из текущего каталога (где находится Dockerfile) в контейнер
COPY . /app

# Устанавливаем зависимости, если они есть
RUN pip install --no-cache-dir -r requirements.txt

# Копирование entrypoint.sh в контейнер
# COPY script.sh /app

# Делаем entrypoint.sh исполняемым
RUN chmod +x /app/script.sh

# Загрузите проект из репозитория GitHub
RUN git clone https://github.com/dmtana/YT_downloader

# Переместить config.py файл в рабочую деректорию 
RUN mv /app/config.py /app/YT_downloader/src/python

# Устанавливаем ffmpeg
RUN apt-get update
RUN apt-get install -y ffmpeg

# Установите рабочую директорию в /app/YT_downloader/src/python
WORKDIR /app

# Опционально: устанавливаем переменную окружения
# ENV NAME World

# Опционально: указываем порт, который будет слушать приложение
# EXPOSE 8080

# Команда, которая будет выполнена при запуске контейнера
# Использую backslash для экранирования кавычек для bash скрипта
CMD [\"./script.sh\"]" > Dockerfile

echo "yt-dlp
aiofiles
aiogram
aiohttp
ffmpeg-python" > requirements.txt

echo "
# 			    @my_new_bot:
TOKEN       = 'TOKEN'

ADMIN_ID    = 0
ADMIN_ID2   = 0
ADMIN_ID3   = 0
ADMIN_ID4   = 0

MODERATOR   = 0
MODERATOR2  = 0
MODERATOR3  = 0
MODERATOR4  = 0

START_TEXT  = {'RUS':'Я простой бот что бы скачивать видео и аудио с различных популярных ресурсов, таких как YouTube, Instagram, TikTok и многих других. Просто отправь ссылку на то что хочешь скачать и я попытаюсь это скачать.',
               'EN':'I am a simple bot designed to download videos and audio from various popular sources, such as YouTube, Instagram, TikTok, and many others. Just send me the link of what you want to download, and I will try to fetch it for you. '}

GROUP1      = 'group1'
GROUP2      = 'group2'
GROUP3      = 'group3'

GROUP4      = ''
GROUP5      = ''
GROUP6      = ''

SITE_1      = 'site1.com'
SITE_2      = ''
SITE_3      = ''

VAR_1       = None
VAR_2       = None
VAR_3       = None

VERSION     = 'version'
" > config.py

echo "#!/bin/bash
cd /app/YT_downloader/src/python/ 
git pull 
python3 bot.py" > script.sh

docker build -t new_docker_bot .
docker run new_docker_bot
  </pre>  

Finished bot implementation -> <a href="https://t.me/TestTelegramBot001_bot">YT_downloader</a>
