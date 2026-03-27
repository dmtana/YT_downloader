#!/bin/bash

set -e

TOKENS=()

# ===== DEFAULT SETTINGS =====
use_external_db=false
install_pgadmin=true

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
use_host_network=false

# LIMITS
per_day=99
per_hour=99

# IMAGE
DOCKER_IMAGE_BOT_NAME='bot_image'

# ===== HELPERS =====
ask_yes_no() {
    local prompt="$1"
    local default="${2:-yes}"
    local answer

    while true; do
        read -r -p "$prompt" answer

        if [[ -z "$answer" ]]; then
            answer="$default"
        fi

        case "${answer,,}" in
            y|yes) return 0 ;;
            n|no) return 1 ;;
            *) echo "Please answer: y/yes or n/no" ;;
        esac
    done
}

echo "Enter TOKEN (if several, separate by commas):"
read -r TOKEN
IFS=',' read -ra TOKENS <<< "$TOKEN"

if ask_yes_no "Run bot after install? Y/n: " "yes"; then
    answer="yes"
else
    answer="no"
fi

echo
echo "Database mode:"
echo "1. Local PostgreSQL in Docker"
echo "2. External PostgreSQL"
read -r -p "Enter your choice [1/2]: " db_mode

if [[ "$db_mode" == "2" ]]; then
    use_external_db=true
    echo "You selected external database."
else
    use_external_db=false
    echo "You selected local database in Docker."
fi

echo
if ask_yes_no "Install pgAdmin? Y/n: " "yes"; then
    install_pgadmin=true
else
    install_pgadmin=false
fi

echo
echo "Use default network:"
echo "1. Default Docker bridge network"
echo "2. Host network"
read -r -p "Enter your choice [1/2]: " network_type

if [[ "$network_type" == "2" ]]; then
    use_host_network=true
    echo "You selected Host network from Docker."
else
    use_host_network=false
    echo "You selected Default bridge network from Docker."
fi

num_of_bots=${#TOKENS[@]}

echo
if ask_yes_no "Use default database settings? y/N: " "no"; then
    echo "[+] Using default database config."
else
    while true; do
        read -r -p "Enter database      USER: " _user
        read -r -p "Enter database      PASSWORD: " _passwd
        read -r -p "Enter name          DATABASE: " _db

        if $use_external_db; then
            read -r -p "Enter external database host/IP: " _host
            read -r -p "Enter external database port [5432]: " _port
            _port=${_port:-5432}
        fi

        if $install_pgadmin; then
            read -r -p "Enter pgAdmin login email: " _user_pg_admin
            read -r -p "Enter pgAdmin password: " _passwd_pg_admin
        fi

        echo
        echo "Your database config:"
        echo "  user      - $_user"
        echo "  password  - $_passwd"
        echo "  database  - $_db"

        if $use_external_db; then
            echo "  db host   - $_host"
            echo "  db port   - $_port"
        fi

        if $install_pgadmin; then
            echo "  pgadmin login - ${_user_pg_admin:-$user_pg_admin}"
            echo "  pgadmin pass  - ${_passwd_pg_admin:-$passwd_pg_admin}"
        fi

        if ask_yes_no "Is it correct? Y/n: " "yes"; then
            user="$_user"
            passwd="$_passwd"
            db="$_db"

            if $use_external_db; then
                host="$_host"
                port="$_port"
            fi

            if $install_pgadmin; then
                user_pg_admin="${_user_pg_admin:-$user_pg_admin}"
                passwd_pg_admin="${_passwd_pg_admin:-$passwd_pg_admin}"
            fi
            break
        fi
    done
fi

# external db extra prompt if still default localhost
if $use_external_db; then
    if [[ -z "$host" || "$host" == "localhost" ]]; then
        read -r -p "Enter external database host/IP: " ext_host
        host="${ext_host:-localhost}"
    fi

    read -r -p "Enter external database port [${port}]: " ext_port
    port="${ext_port:-$port}"
fi

# local db host depends on network mode
if ! $use_external_db; then
    if $use_host_network; then
        host='localhost'
    else
        host='database'
    fi
fi

echo
echo "[+] Installing Docker..."
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

# better than building per-bot
mkdir -p bot_image_context
cat <<EOL > bot_image_context/Dockerfile
FROM python:3.13
WORKDIR /app
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y git ffmpeg
RUN git clone https://github.com/dmtana/YT_downloader
RUN pip install --no-cache-dir -r /app/YT_downloader/requirements.txt
RUN chmod +x /app/YT_downloader/src/scripts/script.sh
CMD bash ./YT_downloader/src/scripts/script.sh
EOL

if docker build -t "$DOCKER_IMAGE_BOT_NAME" ./bot_image_context; then
    echo "[+][BUILD COMPLETE image name=$DOCKER_IMAGE_BOT_NAME]"
else
    echo "[X][BUILD FAILED]"
fi

if usermod -aG docker "$USER"; then
    echo "[+][PERMISSION usermod -aG docker $USER]"
else
    echo "[X][FAILED TO GRANT PERMISSIONS]"
fi

# intentionally not using chmod 777 /var/run/docker.sock

# ===== CREATE CONFIG FILES =====
if (( num_of_bots == 1 )); then
    mkdir -p config
else
    for ((i=0; i<num_of_bots; i++)); do
        mkdir -p "config_$i"
    done
fi

for ((i=0; i<num_of_bots; i++)); do
    trimmed_TOKEN=$(echo "${TOKENS[$i]}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    if (( num_of_bots == 1 )); then
        config_path="config/config.py"
    else
        config_path="config_$i/config.py"
    fi

    cat <<EOL > "$config_path"
# YT_downloader
TOKEN = '$trimmed_TOKEN'
ADMINS_ID = [0]
MODERATORS_ID = [0]
START_TEXT = {
    'EN': 'I am a simple bot designed to download videos and audio from various popular sources, such as YouTube, Instagram, TikTok, and many others. Just send me the link of what you want to download, and I will try to fetch it for you.'
}
INFO = {}
GROUP1 = ''
GROUP2 = ''
GROUP3 = ''

LIMITS = {
    'per_day': $per_day,
    'per_hour': $per_hour
}

USERS = {
    'blocked': [],
    'admins': [],
    'moderators': [],
    'white_list': []
}

BOT_SETINGS={
    'cookies':{
        'youtube':False,
        'instagram':True,
        'facebook':False,
        'tiktok':False
    },
    'LIMITS':{
        'youtube':{   
            'per_day': 1,
            'per_hour': 1,
            'days_delay_limit': 3
            },
        'other':{
            'per_day': 5,
            'per_hour': 2,
            'days_delay_limit': 1
        }    
    }
}

DATABASE = {
    'pass':         '$passwd',
    'user':         '$user',
    'host':         '$host',
    'port':         '$port',
    'database':     '$db'
} 
INFO = {"time_adjustment" : 0}
EOL

    echo "Token $((i+1)): [${trimmed_TOKEN}] config created"
done

# ===== CREATE docker-compose.yml =====
cat <<EOL > docker-compose.yml
version: '3.9'
services:
EOL

# DATABASE SERVICE
if ! $use_external_db; then
    cat <<EOL >> docker-compose.yml
  database:
    image: postgres
    container_name: yt_database
    environment:
      - POSTGRES_USER=$user
      - POSTGRES_PASSWORD=$passwd
      - POSTGRES_DB=$db
EOL

    if ! $use_host_network; then
        cat <<EOL >> docker-compose.yml
    ports:
      - "$port:5432"
EOL
    fi

    cat <<EOL >> docker-compose.yml
    volumes:
      - ./db_data:/var/lib/postgresql/data
EOL

    if $use_host_network; then
        cat <<EOL >> docker-compose.yml
    network_mode: host
EOL
    fi
fi

# PGADMIN SERVICE
if $install_pgadmin; then
    cat <<EOL >> docker-compose.yml
  pg-admin:
    image: dpage/pgadmin4
    container_name: yt_pgadmin
    environment:
      - PGADMIN_DEFAULT_EMAIL=$user_pg_admin
      - PGADMIN_DEFAULT_PASSWORD=$passwd_pg_admin
      - PGADMIN_LISTEN_PORT=80
EOL

    if ! $use_host_network; then
        cat <<EOL >> docker-compose.yml
    ports:
      - "$port_pgadmin:80"
EOL
    fi

    cat <<EOL >> docker-compose.yml
    volumes:
      - ./pgadmin_data:/var/lib/pgadmin
EOL

    if $use_host_network; then
        cat <<EOL >> docker-compose.yml
    network_mode: host
EOL
    fi
fi

# BOT SERVICES
if (( num_of_bots == 1 )); then
    cat <<EOL >> docker-compose.yml
  yt_downloader:
    image: $DOCKER_IMAGE_BOT_NAME
    container_name: yt_downloader
    volumes:
      - ./config/config.py:/app/YT_downloader/src/python/config/config.py
EOL

    if $use_host_network; then
        cat <<EOL >> docker-compose.yml
    network_mode: host
EOL
    fi
else
    for ((c=0; c<num_of_bots; c++)); do
        cat <<EOL >> docker-compose.yml
  yt_downloader_$c:
    image: $DOCKER_IMAGE_BOT_NAME
    container_name: yt_downloader_$c
    volumes:
      - ./config_$c/config.py:/app/YT_downloader/src/python/config/config.py
EOL

        if $use_host_network; then
            cat <<EOL >> docker-compose.yml
    network_mode: host
EOL
        fi
    done
fi

mkdir -p db_data
mkdir -p pgadmin_data

echo
echo "[+] Project created."
echo "Database mode: $([[ "$use_external_db" == true ]] && echo 'External DB' || echo 'Local PostgreSQL in Docker')"
echo "pgAdmin: $([[ "$install_pgadmin" == true ]] && echo 'Enabled' || echo 'Disabled')"
echo "Bots count: $num_of_bots"
echo "DB host for bot config: $host"
echo "DB port for bot config: $port"
echo "Docker image: $DOCKER_IMAGE_BOT_NAME"

if [[ "$answer" == "yes" ]]; then
    if docker-compose up -d; then
        echo "[+][docker-compose up -d]"
    else
        echo "[X][FAILED docker-compose up]"
    fi
fi