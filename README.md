# YT_downloader

This is simple telegram bot for download music and video (up to 50 Mb) from YouTube, Instagram, Tik-Tok, Facebook etc. 

Based on <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> library.

<h2>How to create your own YT_downloader bot</h2>

Receive a token from the <a href="https://t.me/BotFather">botfather</a>. And start the bot using this simple instruction.

<h3>Creation script (docker based):</h3>

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

<h3>YouTube antibot system fix:</h3>
For YouTube You will need to add cookies for anti bot system. Download your account cookies from youtube in format <code><a href="https://docs.cyotek.com/cyowcopy/1.10/netscapecookieformat.html">Netscape</a></code>, this can be obtained using a browser extension like <a href="https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc">Get cookies.txt LOCALLY</a>. After that copy this file to the config folder in the bot project and rename it to <code>www.youtube.com_cookies.txt</code>. 


<h3>Instagram antibot system fix:</h3>
The same thing like with yotube fix, just pull instagram cookies in format <code><a href="https://docs.cyotek.com/cyowcopy/1.10/netscapecookieformat.html">Netscape</a></code>, and create file in config folder <code>www.instagram.com_cookies.txt</code>
