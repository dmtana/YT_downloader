# YT_downloader

This is simple telegram bot for download music and small video (up to 50 Mb) from YouTube, Instagram, Tik-Tok etc. 

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

# make it runnable
# chmod +x script.sh

# run script
# ./script.sh

echo "# Commands before start polling
# cd /app/YT_downloader/src/python/ && git pull && python3 bot.py
  
FROM python:3.8
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /app/script.sh
RUN git clone https://github.com/dmtana/YT_downloader
RUN mv /app/config.py /app/YT_downloader/src/python
RUN apt-get update
RUN apt-get install -y ffmpeg
WORKDIR /app
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

START_TEXT  = {'RUS':'text'}

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
