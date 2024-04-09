# YT_downloader

This is simple telegram bot for download music and small video (up to 50 Mb) from YouTube, Instagram, Tik-Tok etc. 

Based on <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> library.

<h2>How to create your own YT_downloader bot</h2>

Fisrt off all you need to install <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> on youre PC or Linux or Mac. 
Then you need download <a href="https://github.com/aiogram/aiogram">aiogram</a> and <a href="https://ffmpeg.org/" class="link">ffmpeg</a>. 
You need to place ffmpeg.exe in the root of the project with the executable code if You have Windows. 
For Linux or Mac just install using terminal or <a href="https://brew.sh/">homebrew</a>. 

Get a bot token from a botfather. And start the bot.

<h3>Creation script for docker:</h3>

<pre >
#!/bin/bash

# [ create this script ]
# touch creator.sh

# [ make it runnable ] 
# chmod +x creator.sh

# [ install docker ]
# sudo apt  install docker.io

# [ run script ]
# sudo bash creator.sh

echo "
FROM python:3.8
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /app/script.sh
RUN git clone https://github.com/dmtana/YT_downloader
RUN mv /app/config.py /app/YT_downloader/src/python/config/
RUN apt-get update
RUN apt-get install -y ffmpeg
CMD [\"./script.sh\"]" > Dockerfile

echo "#!/bin/bash
cd /app/YT_downloader/src/python/ 
git pull 
python3 bot.py" > script.sh
    
echo "yt-dlp
aiofiles
aiogram
aiohttp
ffmpeg-python" > requirements.txt

echo "
#@NameTelegramBot_bot:
TOKEN       = 'TOKEN'
ADMINS_ID   = [0, 0]
MODERATORS_ID = [0]
START_TEXT  = {'RUS':'start text', 'ENG':'start text'}
GROUP1      = ''
GROUP2      = ''
GROUP3      = ''
GROUP4      = ''
GROUP5      = ''
GROUP6      = ''
SITE_1      = 'site1'
SITE_2      = ''
SITE_3      = ''
VAR_1       = None
VAR_2       = None
VAR_3       = None
" > config.py

DOCKER_IMAGE_BOT_NAME=new_docker_bot

if docker build -t $DOCKER_IMAGE_BOT_NAME .; then
    echo "[+][BUILD COMPLETE image name=$DOCKER_IMAGE_BOT_NAME]"
else
    echo "[X][BUILD FAILED]"
fi
if usermod -aG docker $USER; then
    echo "[+][PERMISSION usermod -aG docker $USER]"
else
    echo "[X][FAILED TO GRANT PERMISSIONS]"
fi
if chmod 777 /var/run/docker.sock; then
    echo "[+][PERMISSION /var/run/docker.sock]"
else
    echo "[X][FAILED TO GRANT PERMISSIONS]"
fi
# if docker run -d bot_image; then
#    echo "[+][BOT RUN]"
# else
#    echo "[X][FAILED TO RUN BOT]"
# fi
  </pre>  

Finished bot implementation -> <a href="https://t.me/TestTelegramBot001_bot">YT_downloader</a>
