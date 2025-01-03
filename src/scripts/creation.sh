#!/bin/bash

TOKENS=()

database=true

# DATABASE CONFIG
host='localhost'
user='admin'
passwd='postgres'
db='bot_data'
port='5432'
port_pgadmin='2345'

# PGADMIN CONFIG
user_pg_admin='admin@admin.com'
passwd_pg_admin='admin'

# NETWORK TYPE
network_mode_host=''
ports_locker='#'

read -p "Enter TOKEN: " TOKEN
IFS=',' read -ra TOKENS <<< "$TOKEN"

echo "Run bot after install? Y/n"
read answer

# TODO edit config creating separately database docker-compose file
# for use external database
if $database ; then
    echo "[+][database creating]"
fi    

echo "Use default network:
1. Default (will block your host ports [$port],[$port_pgadmin] with virtual network ports) 
(RECOMMENDED)
2. Localhost (will use your host's ports [$port],[$port_pgadmin])
Enter your choice: "

read network_type

if [[ "$network_type" != "2" ]]; then
    network_mode_host='#'
    host='database'
    ports_locker=''
    echo "You selected Default network from Docker!"
fi

num_of_bots=${#TOKENS[@]}

read -p "Use default database setting? 
(NOT RECOMMENDED, PLEASE ENTER YOUR OWN CONFIG (type NO)) Y/n: " yesno

if [[ "$yesno" != "yes" && "$yesno" != "y" || "$yesno" == "Y" ]]; then
    while true; do
        read -p "Enter database user name: " _user
        read -p "Enter database password: " _passwd
        read -p "Enter database name: " _db

        read -p "Enter database pgadmin login mail: " user_pg_admin
        read -p "Enter database pgadmin password: " passwd_pg_admin

        echo -e "Your database config: \n\tuser - $_user\n\tpass - $_passwd\n\tdatabase - $_db\n\n\tpgadmin login - $user_pg_admin\n\tpgadmin pass - $passwd_pg_admin"
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
$ports_locker    ports:
$ports_locker      - "$port:5432" # there will always be 5432 in the container
    volumes:
      - ./db_data:/var/lib/postgresql/data
$network_mode_host    network_mode: host
EOL

# Add pgadmin4 service
cat <<EOL >> docker-compose.yml
  pg-admin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=$user_pg_admin
      - PGADMIN_DEFAULT_PASSWORD=$passwd_pg_admin
      - PGADMIN_LISTEN_PORT=$port_pgadmin
$ports_locker    ports:
$ports_locker      - "$port_pgadmin:$port_pgadmin"
$network_mode_host    network_mode: host
EOL

# Add bot images
for ((c=0; c<num_of_bots; c++)); do
    cat <<EOL >> docker-compose.yml
  yt_downloader_$c:
    image: bot_image_$c
    volumes:
      - ./config_$c:/app/YT_downloader/src/python/config
$network_mode_host    network_mode: host
EOL
done

# # trim()
# Print tokens
for ((i=0; i<num_of_bots; i++)); do
    trimmed_TOKEN=$(echo ${TOKENS[$i]} | sed 's/^[   ]*//;s/[    ]*$//')

    mkdir bot_$i

    cd bot_$i

    echo "
FROM python:latest
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN git clone https://github.com/dmtana/YT_downloader
RUN pip install --no-cache-dir -r /app/YT_downloader/requirements.txt
RUN chmod +x /app/YT_downloader/src/scripts/script.sh
RUN mv /app/config.py /app/YT_downloader/src/python/config/
RUN apt-get update
RUN apt-get install -y ffmpeg
CMD [\"./YT_downloader/src/scripts/script.sh\"]" > Dockerfile

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

    cd .. 

    echo "Token $((i+1)): [${trimmed_TOKEN}] DONE"
done

for ((i=0; i<num_of_bots; i++)); do
    mkdir config_$i
    cp bot_$i/config.py config_$i/config.py
done

if [[ "$answer" == "yes" || "$answer" == "y" || "$answer" == "Y" ]]; then
    if docker-compose up -d; then
        echo "[+][docker-compose up -d]"
    else
        echo "[X][FAILED docker-compose up]"
    fi   
fi 