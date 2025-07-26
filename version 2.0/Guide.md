🖥️ Offline Intranet Suite Setup (Windows)
By Adity — July 26, 2025

A beginner-friendly guide to create your own fully offline, self-hosted intranet on a Windows PC using free tools. Access movies, Wikipedia, music, comics, translation, voice calls, AI chat, and more — all without internet.

🧠 What You’ll Get
Feature	Tool(s) Used
Offline Wiki	Kiwix Server + ZIM Files
Movies/TV Shows	Jellyfin
Comics	Komga
Music	Navidrome
Language Translation	LibreTranslate
VoIP Calling/Texting	MiniSIPServer + Linphone
File Sharing	Python Local File Server / Samba
AI Chatbot (ChatGPT)	Ollama + Qwen + Msty UI
Voice Chat (VOIP)	Mumble
Remote Access	Sunshine + Moonlight
Custom Domain Access	Technitium DNS + NGINX
Search Engine / Home	YaCy / Status_Server.py
LAN Games	LAN Game Server

🔧 System Requirements
OS: Windows 10 (Version 22H2 or higher)

RAM: At least 8 GB (Tested on 12 GB DDR3)

CPU: Works even on Intel i3-2120 (2nd Gen)

Internet needed only once (for setup)

🛠️ Step-by-Step Setup Instructions
1. 📚 Kiwix Server (Offline Wikipedia)
What is it? A local Wikipedia-style encyclopedia using .zim files.
How to set up:

Download: https://kiwix.org/en/applications/

Get ZIM files: https://library.kiwix.org/#lang=eng

2. 🎬 Jellyfin (Media Server)
What is it? A personal Netflix-like server for movies and TV.
How to set up:

Download: https://jellyfin.org/

Install and add your media files.

3. 🌐 LibreTranslate (Offline Translation)
What is it? A translation tool like Google Translate, fully offline.
How to set up:

bash
Copy
Edit
pip install libretranslate
libretranslate --load-only en,es,fr
Use libretranslate_gui.py for a GUI interface.

4. 🎵 Navidrome (Music Server)
What is it? A self-hosted Spotify alternative.
How to set up:

Download: https://www.navidrome.org/docs/installation/

It auto-detects music from your Music folder.

Use Mp3tag or MusicBrainz Picard to fix metadata.

5. 📖 Komga (Comic Server)
What is it? A comic/manga reader over LAN.
How to set up:

Download: https://komga.org/docs/installation/desktop

Add .cbz or .cbr files to the library.

6. 🤖 Ollama + Qwen + Msty UI (ChatGPT Alternative)
What is it? An offline AI chatbot.
How to set up:

Download: https://ollama.com

Run in CMD:

bash
Copy
Edit
ollama run qwen2.5:0.5b
Use chatbot.exe for the web UI.

7. 🌐 Technitium DNS + NGINX (LAN Domains)
What is it? Lets you use friendly .lan URLs instead of IPs.
How to set up:

Technitium DNS: https://technitium.com/dns/

Add Zone → e.g., lan

Add Records like kiwix = 192.168.1.x

NGINX: https://nginx.org/en/download.html

Use nginx.conf and run:

nginx -s reload
8. 🧑‍💻 Sunshine + Moonlight (Remote PC Streaming)
What is it? Remote desktop streaming over LAN.

Server: https://github.com/moonlight-stream/moonlight-qt/releases

Client (Phone): https://f-droid.org/packages/com.limelight/

9. ☎️ MiniSIPServer + Linphone (VoIP Calling)
What is it? LAN-based calling and messaging.

MiniSIPServer: https://www.myvoipapp.com/download/

Linphone (Client): https://www.linphone.org

10. 💾 File Sharing (FTP/HTTP)
What is it? Share files over LAN using a simple server.

Script: local_file_server.py

Access from browser: http://your-ip:5050

11. 🗣️ Mumble (Voice Chat)
What is it? Low-latency VOIP over LAN.

Install Mumble Server and Client (e.g., Mumla on phone).

12. 🔍 Offline Search or Homepage (YaCy / Status_Server.py)
What is it? LAN homepage or full offline search engine.

Use status_server.py for a simple dashboard.

Install YaCy for a Google-style search engine.

13. 🕹️ LAN Game Server
What is it? Lightweight local game hosting.

Use lan_game_server.py or .exe

Access: http://your-ip:7815

🌐 Example LAN URLs
Service	URL	Port
Movies	http://jellyfin.lan	8096
Wiki	http://kiwix.lan	8088
Music	http://navidrome.lan	8091
Comics	http://komga.lan	1111
Translate	http://translate.lan	8081
Chatbot	http://dumbot.lan	1090
Search/Home	http://search.lan	5050
Games	http://games.lan	7815

⚠️ Important Notes
If you are using my Python scrypty, change its icon path in the .py file to where your .ico or icon file is located.

All services work fully offline after setup.

RAM usage is lightweight (~6.9 GB), works fine on 8 GB systems.

