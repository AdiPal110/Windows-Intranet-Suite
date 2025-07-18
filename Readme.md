Wintranet: A Self-Hosted Intranet for Windows
# Windows Intranet Suite

A lightweight, fully offline intranet setup for Windows using:

- ✅ Technitium DNS Server for `.lan` routing
- ✅ Nginx reverse proxy for clean URLs
- ✅ Jellyfin, Kiwix, Navidrome for media
- ✅ Local chatbot and translation tools
- ✅ Python-based file server and tools

> All running on a modest Windows PC (even on an i3 2nd gen!)

---

## 🔧 Features

- LAN-only `.lan` domain resolution
- Reverse proxy setup via Nginx
- Portable, open-source components
- Minimal RAM/CPU requirements
- Fully offline: no Internet needed after setup
- GUI chatbots, offline media, calling, wiki, and translation

---

## 🚀 Getting Started

1. Install [Technitium DNS Server](https://technitium.com/dns/)
2. Configure `.lan` domains (e.g., `kiwix.lan`, `jellyfin.lan`, etc.)
3. Run Nginx with the provided `nginx.conf` config
4. Launch:
    - `Jellyfin` for movies
    - `Kiwix` for offline Wikipedia
    - `Navidrome` for music
    - `LibreTranslate` for language translation
    - `Komga` for comics
    - Your local Python chatbot + file server
5. Access services via browser using `.lan` URLs on the same Wi-Fi

---

## 💻 Components Used

- **Technitium DNS** – Custom DNS server for `.lan` routing
- **Nginx** – High-performance reverse proxy
- **Jellyfin** – Media server for movies/anime
- **Kiwix** – Offline Wikipedia and ZIM file reader
- **Navidrome** – Music streaming from your own collection
- **Komga** – Manga/Comic reader server
- **LibreTranslate** – Offline translation server
- **MiniSIPServer + Linphone** – VoIP calling and messaging
- **Python chatbot (Qwen 2.5:0.5B)** – AI assistant
- **Samba/FTP/Explorer** – File sharing

---

## 📂 Example LAN Services

| App           | URL Example         | Port  |
|----------------|---------------------|-------|
| Jellyfin       | `http://jellyfin.lan`   | 8096 |
| Kiwix          | `http://kiwix.lan`      | 8088 |
| Chatbot (Qwen) | `http://dumbot.lan`     | 1090 |
| Komga          | `http://komga.lan`      | 1111 |
| Translate      | `http://translate.lan`  | 8081 |
| Navidrome      | `http://navidrome.lan`  | 8091 |

---

## 🤝 Contribute

Pull requests welcome! Share improvements, new apps, better automation, or alternate UIs for the intranet.

---

## 📄 License

This project is open-source and available under the **MIT License**.  

