import subprocess
import sys
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from threading import Thread
import os
import platform
import signal

flask_process = None
log_thread = None

def stop_flask():
    global flask_process
    killed_any = False

    if flask_process and flask_process.poll() is None:
        flask_process.terminate()
        flask_process.wait()
        killed_any = True

    port = "1224"
    if platform.system() == "Windows":
        try:
            result = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
            pids = set()
            for line in result.strip().splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.add(pid)
            for pid in pids:
                subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                killed_any = True
        except Exception as e:
            log_text.insert(tk.END, f"[ERROR] Failed to kill process: {e}\n")
    else:
        try:
            result = subprocess.check_output(f'lsof -i :{port} -t', shell=True).decode()
            pids = result.strip().splitlines()
            for pid in pids:
                os.kill(int(pid), signal.SIGTERM)
                killed_any = True
        except Exception as e:
            log_text.insert(tk.END, f"[ERROR] Failed to kill process: {e}\n")

    if killed_any:
        status_label.config(text="❌ Server Stopped", fg="#ff4444")
        log_text.insert(tk.END, "[INFO] Server process(es) terminated.\n")
        log_text.see(tk.END)
        start_button.config(state=tk.NORMAL, bg="#444", fg="white")
        stop_button.config(state=tk.DISABLED, bg="#222", fg="#999")

def start_flask():
    global flask_process, log_thread

    if flask_process is None or flask_process.poll() is not None:
        flask_process = subprocess.Popen(
            [sys.executable, __file__, '--child'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        status_label.config(text="✅ Server Running", fg="#00ff00")
        log_text.insert(tk.END, "[INFO] Flask server started...\n")
        log_text.see(tk.END)
        start_button.config(state=tk.DISABLED, bg="#444", fg="white")
        stop_button.config(state=tk.NORMAL, bg="#222", fg="white")

        def read_logs():
            while True:
                if flask_process.poll() is not None:
                    break
                line = flask_process.stdout.readline()
                if line:
                    log_text.insert(tk.END, line)
                    log_text.see(tk.END)
                else:
                    break

        log_thread = Thread(target=read_logs, daemon=True)
        log_thread.start()

def launch_ui():
    global status_label, log_text, start_button, stop_button, root

    root = tk.Tk()
    root.title("Clock Server Manager")
    root.iconbitmap(r'C:\Users\Aditya\Desktop\pyton try\clock.ico')
    root.geometry("700x450")
    root.configure(bg="#1e1e1e")

    tk.Label(root, text="🕒 Time Server Controller", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg="#1e1e1e").pack(pady=10)

    status_label = tk.Label(root, text="Status: Idle", font=("Segoe UI", 12), fg="orange", bg="#1e1e1e")
    status_label.pack()

    button_frame = tk.Frame(root, bg="#1e1e1e")
    button_frame.pack(pady=10)

    start_button = tk.Button(button_frame, text="▶️ Start Server", command=start_flask, font=("Segoe UI", 11),
                             width=15, bg="#444", fg="white", activebackground="#666")
    start_button.grid(row=0, column=0, padx=10)

    stop_button = tk.Button(button_frame, text="⏹ Stop Server", command=stop_flask, font=("Segoe UI", 11),
                            width=15, bg="#222", fg="#999", state=tk.DISABLED)
    stop_button.grid(row=0, column=1, padx=10)

    def on_enter_start(e):
        if start_button.cget('state') == 'normal':
            start_button.config(bg="#555")

    def on_leave_start(e):
        if start_button.cget('state') == 'normal':
            start_button.config(bg="#444")

    def on_enter_stop(e):
        if stop_button.cget('state') == 'normal':
            stop_button.config(bg="#444")

    def on_leave_stop(e):
        if stop_button.cget('state') == 'normal':
            stop_button.config(bg="#222")

    start_button.bind("<Enter>", on_enter_start)
    start_button.bind("<Leave>", on_leave_start)
    stop_button.bind("<Enter>", on_enter_stop)
    stop_button.bind("<Leave>", on_leave_stop)

    log_text = ScrolledText(root, width=80, height=15, bg="#111", fg="#0f0", insertbackground="white", font=("Consolas", 10))
    log_text.pack(pady=5)

    def on_close():
        stop_flask()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    start_flask()
    root.mainloop()

# Flask Server Code
if __name__ == '__main__':
    if '--child' in sys.argv:
        from flask import Flask, jsonify
        from datetime import datetime

        app = Flask(__name__)

        @app.route('/')
        def index():
            now = datetime.now()
            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Server Time</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0 5vw;
            min-height: 100vh;
            background-color: #111;
            color: #eee;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: background 0.3s, color 0.3s;
            text-align: center;
        }}
        h1 {{
            font-size: 5vw;
            margin: 10px 0;
        }}
        #time {{
            font-size: 6vw;
            margin: 10px 0;
            word-wrap: break-word;
        }}
        .switch {{
            margin: 10px;
            font-size: 4vw;
        }}
        #modeButton {{
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 6vw;
            background: none;
            border: none;
            cursor: pointer;
            color: inherit;
        }}
        @media (min-width: 600px) {{
            h1 {{ font-size: 2.2em; }}
            #time {{ font-size: 2em; }}
            .switch {{ font-size: 1.2em; }}
            #modeButton {{ font-size: 1.5em; }}
        }}
    </style>
</head>
<body>
    <button id="modeButton" onclick="toggleTheme()">🌑</button>
    <h1 id="clockIcon">⏲️ 24-Hour Format</h1>
    <div id="time">{now.strftime('%Y-%m-%d %H:%M:%S')}</div>
    <div class="switch">
        <label>
            <input type="checkbox" id="formatSwitch" onchange="toggleFormat()"> 12-Hour Format
        </label>
    </div>

    <script>
        let isDark = true;
        let format12h = false;

        function toggleTheme() {{
            isDark = !isDark;
            document.body.style.backgroundColor = isDark ? "#111" : "#fff";
            document.body.style.color = isDark ? "#eee" : "#000";
            document.getElementById("modeButton").textContent = isDark ? "🌒" : "🌔";
        }}

        function toggleFormat() {{
            format12h = document.getElementById("formatSwitch").checked;
            document.getElementById("clockIcon").textContent = format12h ? "🕒 12-Hour Format" : "⏲️ 24-Hour Format";
            updateTime();
        }}

        function updateTime() {{
            fetch('/time')
                .then(res => res.json())
                .then(data => {{
                    const timeStr = format12h ? data.time12 : data.time24;
                    document.getElementById("time").textContent = timeStr;
                }});
        }}

        setInterval(updateTime, 1000);
        updateTime();
    </script>
</body>
</html>"""

        @app.route('/time')
        def get_time():
            now = datetime.now()
            return {
                'time24': now.strftime('%Y-%m-%d %H:%M:%S'),
                'time12': now.strftime('%I:%M:%S %p')
            }

        app.run(host='0.0.0.0', port=1224)
    else:
        launch_ui()
