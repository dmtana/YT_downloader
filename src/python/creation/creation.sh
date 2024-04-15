#!/bin/bash

# manual mod
# touch script.sh

# runnable 
# chmod +x script.sh

# docker
# sudo apt install docker.io

# run
# ./script.sh

echo "Enter bot TOKEN:"
read TOKEN

echo "Run bot after install? (yes/no or y/n)"
read answer

if [[ "$answer" == "yes" || "$answer" == "y" ]]; then
    echo "Ok, the bot will be launched automatically"
else
    echo "Ok, run the bot in manual mode after installation"    
fi

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
#YT_downloader
TOKEN       = '$TOKEN'
ADMINS_ID   = [0]
MODERATORS_ID = [0]
START_TEXT  = {'RUS':'I am a simple bot designed to download videos and audio from various popular sources, such as YouTube, Instagram, TikTok, and many others. Just send me the link of what you want to download, and I will try to fetch it for you.'}
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

DOCKER_IMAGE_BOT_NAME=bot_image

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
    echo "[+][PERMISSION chmod 777 /var/run/docker.sock]"
else
    echo "[X][FAILED TO GRANT PERMISSIONS]"
fi

if [[ "$answer" == "yes" || "$answer" == "y" ]]; then
    if docker run -d bot_image; then
        echo "[+][BOT RUN]"
    else
        echo "[X][FAILED TO RUN BOT]"
    fi
fi