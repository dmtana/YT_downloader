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

1. First create a folder (for more convenient use)
<pre>
<code>mkdir bot_folder</code>
</pre>
    
2. Then go to the folder you created <code>cd bot_folder</code> and copy the installation file from the repository
<pre>
<code>wget "https://raw.githubusercontent.com/dmtana/YT_downloader/master/src/scripts/creation.sh"</code>
</pre>  

3. And finally run the installation file with superuser <code>sudo</code> rights and follow the instructions
<pre>
<code>sudo bash creation.sh</code>
</pre>

Finished bot implementation -> <a href="https://t.me/yt_downloader_dmtana_bot">YT_downloader</a>
