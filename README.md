# YT_downloader

This is simple telegram bot for download music and small video (up to 50 Mb) from YouTube, Instagram, Tik-Tok etc. 

Based on <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> library.

<h2>How to create your own YT_downloader bot</h2>

Get a bot token from a <a href="https://t.me/BotFather">botfather</a>. And start the bot.

<h3>Creation script for docker:</h3>

1. First create a folder (for more convenient use)
<pre>
<code>mkdir bot_folder
cd bot_folder</code>
</pre>
    
2. Then copy the installation file from the repository
<pre>
<code>wget "https://raw.githubusercontent.com/dmtana/YT_downloader/master/src/scripts/creation.sh"</code>
</pre>  

3. And finally run the installation file with superuser <code>sudo</code> rights and follow the instructions
<pre>
<code>sudo bash creation.sh</code>
</pre>

Finished bot implementation -> <a href="https://t.me/yt_downloader_dmtana_bot">YT_downloader</a>
