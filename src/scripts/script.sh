#!/bin/bash
cd /app/YT_downloader/src/python/ 
pip install yt-dlp -U
pip install aiogram -U
git pull 
python3 bot.py