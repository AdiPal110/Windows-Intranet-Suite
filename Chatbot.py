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
  <title>Dum Bot</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
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
      font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center;
    }
    .container {
      max-width: 960px; width: 100%; padding: 20px; position: relative;
    }
    .chat-box {
      background: var(--bg); border-radius: 16px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.1); padding: 20px;
    }
    .model-info {
      text-align: center; margin-bottom: 15px;
    }
    .model-info h2 { margin: 0; font-size: 1.5rem; }
    .model-details {
      display: flex; justify-content: center; flex-wrap: wrap; gap: 12px;
      font-size: 0.95rem; margin-top: 6px;
    }
    .model-details span {
      background-color: rgba(0, 0, 0, 0.05); padding: 6px 12px;
      border-radius: 12px; color: var(--text);
    }
    [data-theme='dark'] .model-details span {
      background-color: rgba(255, 255, 255, 0.08);
    }
    #messages {
      max-height: 60vh; overflow-y: auto; margin-bottom: 1rem;
    }
    .message { display: flex; margin: 12px 0; }
    .user .bubble {
      margin-left: auto; background-color: var(--bubble-user); color: white;
    }
    .bot .bubble {
      margin-right: auto; background-color: var(--bubble-bot);
      color: var(--text); position: relative;
    }
    .bubble {
      padding: 12px 16px; border-radius: 20px; max-width: 75%; line-height: 1.5;
    }
    textarea {
      width: 100%; padding: 12px; font-size: 1rem;
      border: 1px solid #ccc; border-radius: 10px; resize: none;
    }
    .controls {
      display: flex; gap: 10px; flex-wrap: wrap; justify-content: space-between; margin-top: 10px;
    }
    button {
      font-size: 1rem; padding: 10px 16px; border-radius: 10px;
      border: none; background-color: var(--highlight); color: white; cursor: pointer;
    }
    button:hover { background-color: #0056b3; }
    .icon-button {
      background-color: var(--icon-bg); color: var(--text); font-size: 18px;
      padding: 10px 14px; border: none; border-radius: 10px; cursor: pointer;
    }
    .icon-button:hover { background-color: var(--icon-hover); }
    .floating-controls {
      position: absolute; top: 10px; width: 100%;
      display: flex; justify-content: space-between; padding: 0 10px;
    }
    .menu-dropdown {
      position: absolute; left: 10px; top: 40px;
      background: var(--bg); border: 1px solid #ccc;
      border-radius: 8px; display: none; flex-direction: column;
      min-width: 160px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); padding: 10px; z-index: 100;
    }
    .menu-dropdown.show { display: flex; }
    #history {
      max-height: 150px; overflow-y: auto; margin-top: 10px; font-size: 0.9rem;
    }
    .bot-tools {
      display: flex; gap: 8px; justify-content: flex-end; margin-top: 6px;
      visibility: hidden;
    }
    .bot.complete .bot-tools { visibility: visible; }
    @media screen and (max-width: 600px) {
      .chat-box { padding: 10px; }
      .bubble { max-width: 90%; }
    }
  </style>
</head>
<body data-theme="light">
  <div class="container">
    <div class="floating-controls">
      <button class="icon-button" onclick="toggleMenu()">☰</button>
      <button class="icon-button" onclick="toggleTheme()">🌓</button>
    </div>
    <div class="menu-dropdown" id="menu">
      <button onclick="confirmClear()">🗑️ Clear Chat</button>
      <div id="history"></div>
    </div>
    <div class="chat-box">
      <div class="model-info">
        <h2>🤖 Qwen2.5:0.5b</h2>
        <div class="model-details">
          <span>🧠 <strong>Arch:</strong> Qwen2</span>
          <span>📊 <strong>Parameters:</strong> 494M</span>
          <span>⚙️ <strong>Quantization:</strong> Q4_K_M</span>
          <span>💾 <strong>Size:</strong> 398MB</span>
        </div>
      </div>
      <div id="messages"></div>
      <textarea id="user-input" rows="3" placeholder="Type a message..."></textarea>
      <div class="controls">
        <button onclick="sendMessage()">Send</button>
        <button class="icon-button" onclick="stopSpeaking()">⏹️ Stop Voice</button>
        <button class="icon-button" onclick="stopStream()">🛑 Stop Generation</button>
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
        ? `<div class='bot-tools'><button class='icon-button' onclick='readAloud("${id}-content")'>🔊</button><button class='icon-button' onclick='regenerate("${id}")'>🔁</button></div>`
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
        if (!finished) updateContent(botId, " ⚠️ Error.");
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
          if (!finished) updateContent(newBotId, " ⚠️ Error.");
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
      if (confirm("Clear entire chat?")) clearChat();
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
