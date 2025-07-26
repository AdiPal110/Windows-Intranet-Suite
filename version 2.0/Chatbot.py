import subprocess
import socket
import requests
import time
import os
import json
import sys
import threading
import tkinter as tk
from tkinter import font, ttk
from tkinter.scrolledtext import ScrolledText
from flask import Flask, request, Response, render_template_string, session
from uuid import uuid4
import psutil
from werkzeug.serving import make_server
import logging
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# === Flask Setup ===
flask_app = Flask(__name__)
flask_app.secret_key = os.urandom(24)
OLLAMA_MODEL = "qwen2.5:0.5b"
OLLAMA_API_URL = "http://localhost:11434/api/chat"
chat_histories = {}

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <title>Qwen2.5 Chat</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <style>
    :root {
      --bg: #f4f4f9; --text: #111; --bubble-user: #007bff;
      --bubble-bot: #e9ecef; --highlight: #007bff;
      --icon-bg: #eee; --icon-hover: #ddd;
    }
    [data-theme='dark'] {
      --bg: #1f1f1f; --text: #f0f0f0;
      --bubble-user: #0056b3; --bubble-bot: #2d2d2d;
      --icon-bg: #333; --icon-hover: #444;
    }
    body {
      margin: 0; background: var(--bg); color: var(--text);
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; 
      display: flex; justify-content: center;
      -webkit-tap-highlight-color: transparent;
    }
    .container {
      max-width: 960px; width: 100%; padding: 15px; position: relative;
    }
    .chat-box {
      background: var(--bg); border-radius: 16px;
      box-shadow: 0 6px 24px rgba(0,0,0,0.08); padding: 20px;
      position: relative;
    }
    .model-info {
      text-align: center; margin-bottom: 15px;
      padding-top: 10px; /* Add space for floating buttons */
    }
    .model-info h2 { 
      margin: 0 0 8px 0; 
      font-size: 1.6rem;
    }
    .model-details {
      display: flex; justify-content: center; flex-wrap: wrap; gap: 12px;
      font-size: 0.95rem; margin-top: 5px;
    }
    .model-details span {
      background-color: rgba(0, 0, 0, 0.05); padding: 7px 14px;
      border-radius: 14px; color: var(--text); 
    }
    [data-theme='dark'] .model-details span {
      background-color: rgba(255, 255, 255, 0.08);
    }
    #messages {
      max-height: 60vh; min-height: 50vh; overflow-y: auto; 
      margin-bottom: 15px; -webkit-overflow-scrolling: touch;
      scrollbar-width: thin;
    }
    .message { 
      display: flex; margin: 14px 0; 
    }
    .user .bubble {
      margin-left: auto; background-color: var(--bubble-user); color: white;
      border-bottom-right-radius: 5px;
    }
    .bot .bubble {
      margin-right: auto; background-color: var(--bubble-bot);
      color: var(--text); border-bottom-left-radius: 5px;
    }
    .bubble {
      padding: 14px 18px; border-radius: 20px; 
      max-width: 80%; line-height: 1.5;
      font-size: 1.05rem;
      word-break: break-word;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    textarea {
      width: 100%; padding: 14px; 
      font-size: 1.05rem;
      border: 1px solid #ccc; border-radius: 14px; 
      resize: none; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }
    .controls {
      display: flex; gap: 12px; flex-wrap: wrap; 
      justify-content: space-between; margin-top: 15px;
    }
    button {
      font-size: 1.05rem; padding: 12px 20px; 
      border-radius: 14px; min-height: 48px;
      border: none; background-color: var(--highlight); 
      color: white; cursor: pointer; flex: 1;
      min-width: 140px;
      transition: background-color 0.2s ease;
    }
    button:hover { 
      background-color: #0069d9; 
    }
    
    /* Floating controls - fixed size */
    .floating-controls {
      position: absolute; 
      top: 10px; 
      width: calc(100% - 30px); /* Account for container padding */
      display: flex; 
      justify-content: space-between; 
      z-index: 10;
    }
    .icon-button {
      background-color: var(--icon-bg); color: var(--text); 
      font-size: 1.2rem;
      padding: 8px; border: none; border-radius: 14px; 
      cursor: pointer;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background-color 0.2s ease;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      flex: 0 0 auto;
    }
    .icon-button:hover { 
      background-color: var(--icon-hover); 
    }
    
    .menu-dropdown {
      position: absolute; left: 15px; top: 45px;
      background: var(--bg); border: 1px solid #ccc;
      border-radius: 14px; display: none; flex-direction: column;
      min-width: 200px; box-shadow: 0 8px 24px rgba(0,0,0,0.15); 
      padding: 15px; z-index: 100;
    }
    .menu-dropdown.show { display: flex; }
    #history {
      max-height: 150px; overflow-y: auto; margin-top: 10px; 
      font-size: 0.95rem; padding: 10px;
      background: rgba(0,0,0,0.03); border-radius: 10px;
    }
    .bot-tools {
      display: flex; gap: 8px; justify-content: flex-end; margin-top: 8px;
      visibility: hidden;
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    .bot.complete .bot-tools { 
      visibility: visible;
      opacity: 1;
    }
    
    /* Mobile-specific enhancements */
    @media (max-width: 768px) {
      .container { 
        padding: 10px;
        max-width: 100%;
      }
      
      .chat-box { 
        padding: 15px; 
        border-radius: 20px;
      }
      
      .model-info h2 { 
        font-size: 1.4rem;
      }
      
      .model-details {
        gap: 8px;
        font-size: 0.9rem;
        justify-content: center;
      }
      
      .model-details span { 
        padding: 6px 10px; 
        border-radius: 12px;
        font-size: 0.85rem;
      }
      
      .bubble { 
        max-width: 85%; 
        padding: 12px 16px;
        font-size: 1rem;
      }
      
      textarea {
        font-size: 1rem;
        padding: 12px;
        border-radius: 12px;
      }
      
      button {
        min-height: 44px;
        border-radius: 12px;
        font-size: 1rem;
        padding: 10px 15px; /* Reduced padding for mobile */
      }
      
      .floating-controls {
        top: 5px;
        width: calc(100% - 20px); /* Account for container padding */
      }
      
      .icon-button {
        width: 36px;
        height: 36px;
        font-size: 1rem;
        padding: 6px;
      }
      
      .menu-dropdown { 
        left: 8px;
        top: 42px;
        min-width: 180px;
      }
    }
    
    /* Small mobile optimization */
    @media (max-width: 480px) {
      .model-details {
        flex-wrap: nowrap;
        overflow-x: auto;
        justify-content: flex-start;
        padding-bottom: 5px;
        -webkit-overflow-scrolling: touch;
      }
      
      .model-details span {
        flex-shrink: 0;
        white-space: nowrap;
      }
      
      .bubble { 
        max-width: 90%; 
      }
      
      .controls {
        gap: 8px;
      }
      
      button {
        min-width: auto;
        flex: 1;
        font-size: 0.95rem;
        padding: 8px 12px; /* More compact on small screens */
        min-height: 40px; /* Reduced height */
      }
      
      .icon-button {
        width: 34px;
        height: 34px;
        font-size: 0.95rem;
      }
    }
    
    /* Animation enhancements */
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .message {
      animation: fadeIn 0.3s ease-out;
    }
    
    /* Scrollbar styling */
    #messages::-webkit-scrollbar {
      width: 6px;
    }
    
    #messages::-webkit-scrollbar-track {
      background: rgba(0,0,0,0.05);
      border-radius: 10px;
    }
    
    #messages::-webkit-scrollbar-thumb {
      background: rgba(0,0,0,0.2);
      border-radius: 10px;
    }
    
    [data-theme='dark'] #messages::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,0.2);
    }
  </style>
</head>
<body data-theme="light">
  <div class="container">
    <div class="chat-box">
      <div class="floating-controls">
        <button class="icon-button" onclick="toggleMenu()">☰</button>
        <button class="icon-button" onclick="toggleTheme()">🌓</button>
      </div>
      <div class="menu-dropdown" id="menu">
        <button onclick="confirmClear()" style="margin-bottom: 12px;">🗑️ Clear Chat</button>
        <div id="history"></div>
      </div>
      <div class="model-info">
        <h2>🤖 Qwen2.5:0.5b</h2>
        <div class="model-details">
          <span>🧠 Arch: Qwen2</span>
          <span>📊 Params: 494M</span>
          <span>⚙️ Quant: Q4_K_M</span>
          <span>💾 Size: 398MB</span>
        </div>
      </div>
      <div id="messages"></div>
      <textarea id="user-input" rows="3" placeholder="Type your message..."></textarea>
      <div class="controls">
        <button onclick="sendMessage()">Send</button>
        <button class="icon-button" onclick="stopSpeaking()" title="Stop voice">⏹️</button>
        <button class="icon-button" onclick="stopStream()" title="Stop generation">🛑</button>
      </div>
    </div>
  </div>
  <script>
    let currentUtterance = null;
    let currentEventSource = null;

    function addMessage(role, text) {
      const id = "msg-" + Date.now();
      const div = document.createElement("div");
      div.className = "message " + role;
      div.id = id;
      const speaker = role === "bot"
        ? `<div class='bot-tools'><button class='icon-button' onclick='readAloud("${id}-content")' title="Read aloud">🔊</button><button class='icon-button' onclick='regenerate("${id}")' title="Regenerate">🔁</button></div>`
        : "";
      div.innerHTML = `<div class="bubble"><span id="${id}-content">${text}</span>${speaker}</div>`;
      document.getElementById("messages").appendChild(div);
      scrollToBottom();
      return id;
    }

    function updateContent(id, text) {
      const el = document.getElementById(id + "-content");
      if (el) el.textContent += text;
      scrollToBottom();
    }

    function finishMessage(id) {
      const msg = document.getElementById(id);
      if (msg) msg.classList.add("complete");
    }

    function sendMessage() {
      const input = document.getElementById("user-input");
      const message = input.value.trim();
      if (!message) return;
      input.value = "";
      addToHistory(message);
      addMessage("user", message);
      const botId = addMessage("bot", "");

      if (currentEventSource) currentEventSource.close();
      currentEventSource = new EventSource("/stream?prompt=" + encodeURIComponent(message));
      let finished = false;

      currentEventSource.onmessage = function(event) {
        if (event.data === "[DONE]") {
          finished = true;
          finishMessage(botId);
          currentEventSource.close();
        } else {
          updateContent(botId, event.data);
        }
      };

      currentEventSource.onerror = function() {
        if (!finished) updateContent(botId, " ⚠️ Connection error");
        finishMessage(botId);
        currentEventSource.close();
      };
    }

    function regenerate(botId) {
      const el = document.getElementById(botId + "-content");
      if (el) {
        const text = el.textContent;
        addMessage("user", text);
        const newBotId = addMessage("bot", "");
        if (currentEventSource) currentEventSource.close();
        currentEventSource = new EventSource("/stream?prompt=" + encodeURIComponent(text));
        let finished = false;

        currentEventSource.onmessage = function(event) {
          if (event.data === "[DONE]") {
            finished = true;
            finishMessage(newBotId);
            currentEventSource.close();
          } else {
            updateContent(newBotId, event.data);
          }
        };

        currentEventSource.onerror = function() {
          if (!finished) updateContent(newBotId, " ⚠️ Connection error");
          finishMessage(newBotId);
          currentEventSource.close();
        };
      }
    }

    function stopSpeaking() {
      if (speechSynthesis.speaking) speechSynthesis.cancel();
    }

    function stopStream() {
      if (currentEventSource) currentEventSource.close();
    }

    function readAloud(id) {
      stopSpeaking();
      const el = document.getElementById(id);
      if (!el) return;
      const utter = new SpeechSynthesisUtterance(el.textContent);
      currentUtterance = utter;
      speechSynthesis.speak(utter);
    }

    function toggleTheme() {
      const body = document.body;
      const current = body.getAttribute("data-theme");
      body.setAttribute("data-theme", current === "dark" ? "light" : "dark");
    }

    function toggleMenu() {
      document.getElementById("menu").classList.toggle("show");
    }

    function addToHistory(text) {
      const entry = document.createElement("div");
      entry.textContent = "• " + text;
      document.getElementById("history").appendChild(entry);
    }

    function confirmClear() {
      if (confirm("Clear entire chat history?")) clearChat();
    }

    function clearChat() {
      document.getElementById("messages").innerHTML = "";
      document.getElementById("history").innerHTML = "";
      fetch("/clear", { method: "POST" });
    }

    function scrollToBottom() {
      const messages = document.getElementById("messages");
      messages.scrollTop = messages.scrollHeight;
    }

    document.addEventListener("click", function(e) {
      const menu = document.getElementById("menu");
      const burger = document.querySelector(".icon-button[onclick='toggleMenu()']");
      if (!menu.contains(e.target) && e.target !== burger) {
        menu.classList.remove("show");
      }
    });
    
    // Mobile enhancements
    document.getElementById('user-input').addEventListener('focus', function() {
      setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      }, 300);
    });
    
    // Enter key to send
    document.getElementById('user-input').addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  </script>
</body>
</html>
"""

@flask_app.route("/")
def index():
    if "session_id" not in session:
        session["session_id"] = str(uuid4())
    return render_template_string(HTML_TEMPLATE)

@flask_app.route("/stream")
def stream():
    prompt = request.args.get("prompt", "")
    session_id = session.get("session_id")
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    chat_histories[session_id].append({"role": "user", "content": prompt})

    def generate():
        payload = {
            "model": OLLAMA_MODEL,
            "messages": chat_histories[session_id],
            "stream": True
        }
        try:
            with requests.post(OLLAMA_API_URL, json=payload, stream=True) as resp:
                full_bot_reply = ""
                for line in resp.iter_lines():
                    if line:
                        data = json.loads(line.decode("utf-8"))
                        token = data.get("message", {}).get("content", "")
                        if token:
                            full_bot_reply += token
                            yield f"data: {token}\n\n"
                chat_histories[session_id].append({"role": "assistant", "content": full_bot_reply})
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: ⚠️ Error: {str(e)}\n\n"

    return Response(generate(), content_type="text/event-stream")

@flask_app.route("/clear", methods=["POST"])
def clear():
    session_id = session.get("session_id")
    if session_id in chat_histories:
        chat_histories[session_id] = []
    return ("", 204)

# === Utility ===
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def start_ollama():
    print("🚀 Starting Ollama silently...")
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(
            ["ollama", "run", OLLAMA_MODEL],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    else:
        subprocess.Popen(["ollama", "run", OLLAMA_MODEL])

    for _ in range(30):
        try:
            if requests.get("http://localhost:11434").status_code == 200:
                print("✅ qwen2.5:0.5b is ready.")
                return
        except:
            pass
        time.sleep(1)
    raise RuntimeError("❌ Ollama didn't start.")

def stop_ollama():
    count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and "ollama" in proc.info['name'].lower():
                proc.kill()
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return count

# === Flask Thread Handler ===
class FlaskThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = make_server("0.0.0.0", 1090, flask_app)
        self.ctx = flask_app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

# === GUI ===
class QwenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Qwen2.5 Bot Server")
        self.root.iconbitmap(r'C:\Users\Aditya\Desktop\pyton try\qwenm.ico')
        self.root.geometry("780x520")
        self.root.configure(bg="#2a2a2a")
        self.flask_server = None

        # Fonts
        self.button_font = font.Font(family="Segoe UI", size=11, weight="bold")
        self.label_font = font.Font(family="Consolas", size=10)

        # Apply ttk style for rounded buttons
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Rounded.TButton",
                        font=self.button_font,
                        foreground="white",
                        background="#3a3a3a",
                        padding=10,
                        relief="flat")
        style.map("Rounded.TButton",
                  background=[('active', '#505050')],
                  foreground=[('active', 'white')])

        # Title Label
        tk.Label(root, text="🤖 Qwen2.5 Server Manager", bg="#2a2a2a", fg="#00d4ff",
                 font=("Segoe UI", 17, "bold")).pack(pady=(12, 8))

        # Button Frame
        button_frame = tk.Frame(root, bg="#2a2a2a")
        button_frame.pack(pady=5)

        self.start_button = ttk.Button(
            button_frame, text="▶ Start Server", command=self.start_server, style="Rounded.TButton", width=22
        )
        self.start_button.pack(side=tk.LEFT, padx=12)

        self.stop_button = ttk.Button(
            button_frame, text="■ Stop Server", command=self.stop_server, style="Rounded.TButton", width=22
        )
        self.stop_button.pack(side=tk.LEFT, padx=12)

        # Access Label
        self.access_label = tk.Label(root, text="", bg="#2a2a2a", fg="#cccccc", font=self.label_font)
        self.access_label.pack(pady=(5, 10))

        # Log Area
        self.log_area = ScrolledText(
            root, height=20, width=90, state='disabled',
            bg="#1e1e1e", fg="#7CFC00", insertbackground="white",
            font=self.label_font, borderwidth=0, relief="flat", padx=10, pady=8
        )
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.setup_flask_logging()
        self.start_server()

    def setup_flask_logging(self):
        class GuiLogHandler(logging.Handler):
            def emit(inner_self, record):
                log_entry = inner_self.format(record)
                self.append_log(f"📄 {log_entry}")

        gui_handler = GuiLogHandler()
        gui_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

        flask_logger = logging.getLogger('werkzeug')
        flask_logger.setLevel(logging.INFO)
        flask_logger.addHandler(gui_handler)

    def append_log(self, msg):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.configure(state='disabled')
        self.log_area.yview(tk.END)

    def start_server(self):
        if self.flask_server:
            self.append_log("⚠️ Server is already running.")
            return
        self.append_log("🚀 Starting Ollama & Flask server...")
        threading.Thread(target=self._run_backend, daemon=True).start()

    def _run_backend(self):
        try:
            start_ollama()
            ip = get_local_ip()
            self.access_label.config(text=f"🔗 Access at: http://{ip}:1090")
            self.append_log(f"🌐 Server running at http://{ip}:1090")
            self.flask_server = FlaskThread()
            self.flask_server.start()
        except Exception as e:
            self.append_log(f"❌ Error: {str(e)}")

    def stop_server(self):
        self.append_log("🛑 Stopping Ollama and Flask...")
        count = stop_ollama()
        self.access_label.config(text="🔌 Server stopped.")
        self.append_log(f"🛑 Stopped {count} Ollama instance(s).")
        if self.flask_server:
            self.flask_server.shutdown()
            self.append_log("🛑 Flask server stopped.")
            self.flask_server = None

    def on_close(self):
        self.append_log("💤 Closing... stopping servers.")
        self.stop_server()
        self.root.destroy()

# === Entry Point ===
if __name__ == "__main__":
    root = tk.Tk()
    app = QwenGUI(root)
    root.mainloop()
