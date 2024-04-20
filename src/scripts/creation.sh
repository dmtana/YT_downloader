#!/bin/bash

TOKENS=()
# DATABASE CONFIG
host='database'
user='admin'
passwd='postgres'
db='bot_data'
port='5432'

user_pg_admin=admin@admin.com
passwd_pg_admin=admin

read -p "Enter TOKEN: " TOKEN
IFS=',' read -ra TOKENS <<< "$TOKEN"

echo "Run bot after install? Y/n"
read answer

num_of_bots=${#TOKENS[@]}

read -p "Use default database setting? Y/n: " yesno

if [[ "$yesno" != "yes" && "$yesno" != "y" || "$yesno" == "Y" ]]; then
    while true; do
        read -p "Enter database user name: " _user
        read -p "Enter database password: " _passwd
        read -p "Enter database name: " _db

        echo -e "Your database config: \n\tuser - $_user\n\tpass - $_passwd\n\tdatabase - $_db"
        read -p "Is it correct? Y/n: " answ

        if [[ "$answ" == "yes" || "$answ" == "y" || "$answ" == "Y" ]]; then
            user=$_user
            passwd=$_passwd
            db=$_db
            break
        else
            continue
        fi
    done
fi

if apt install docker.io -y; then
    echo "[+][sudo apt install docker.io -y]"
else
    echo "[X][FAILED apt install docker.io -y]"
fi
if apt install docker-compose -y; then
    echo "[+][apt install docker-compose -y]"
else
    echo "[X][FAILED apt install docker-compose -y]"
fi

# Create docker-compose file
cat <<EOL > docker-compose.yml
version: '3.9'
services:
EOL

# Add database service
cat <<EOL >> docker-compose.yml
  database:
    image: postgres
    environment:
      - POSTGRES_USER=$user
      - POSTGRES_PASSWORD=$passwd
      - POSTGRES_DB=$db
    ports:
      - "$port:5432" # в контейнере будет всегда 5432 он залочен
    volumes:
      - ./db_data:/var/lib/postgresql/data
EOL

# Add pgadmin4 service
cat <<EOL >> docker-compose.yml
  pg-admin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=$user_pg_admin
      - PGADMIN_DEFAULT_PASSWORD=$passwd_pg_admin
      - PGADMIN_LISTEN_PORT=80
    ports:
      - "2345:80"
EOL

# Add bot images
for ((x=0; x<num_of_bots; x++)); do
    cat <<EOL >> docker-compose.yml
  yt_downloader_$x:
    image: bot_image_$x
    volumes:
      - ./config_$x:/app/YT_downloader/src/python/config
EOL
done

# # trim()
# Print tokens
for ((i=0; i<num_of_bots; i++)); do
    trimmed_TOKEN=$(echo ${TOKENS[$i]} | sed 's/^[   ]*//;s/[    ]*$//')

    mkdir bot_$i

    cd bot_$i

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
asyncpg
ffmpeg-python
opencv-python" > requirements.txt

echo "
#YT_downloader
TOKEN       = '$trimmed_TOKEN'
ADMINS_ID   = [0]
MODERATORS_ID = [0]
START_TEXT  = {'EN':'I am a simple bot designed to download videos and audio from various popular sources, such as YouTube, Instagram, TikTok, and many others. Just send me the link of what you want to download, and I will try to fetch it for you.'}
INFO        = {}
GROUP1      = ''
GROUP2      = ''
GROUP3      = ''
SITE_1      = 'site1'
DATABASE = {'pass':'$passwd', 'user':'$user', 'host':'$host', 'port':'$port', 'database':'$db'}
" > config.py

    DOCKER_IMAGE_BOT_NAME=bot_image_$i

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

    if rm -r requirements.txt script.sh Dockerfile; then
        echo "[+][rm -r requirements.txt script.sh Dockerfile]"
    else
        echo "[X][FAILED rm -r requirements.txt script.sh]"
    fi    

    cd .. 

    echo "Token $((i+1)): [${trimmed_TOKEN}] DONE"
done

for ((i=0; i<num_of_bots; i++)); do
    mkdir config_$i
    mv bot_$i/config.py config_$i/config.py
done

if [[ "$answer" == "yes" || "$answer" == "y" || "$answer" == "Y" ]]; then
    if docker-compose up -d; then
        echo "[+][docker-compose up -d]"
    else
        echo "[X][FAILED docker-compose up]"
    fi   
fi 