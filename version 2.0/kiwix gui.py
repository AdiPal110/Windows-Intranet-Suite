import os
import socket
import subprocess
import glob
import threading
import tkinter as tk
from tkinter import scrolledtext
import psutil
import sys
import ctypes

# === CONFIG ===
KIWIX_PATH = r"B:\Kiwix Windows\kiwix-tools_win-i686\kiwix-serve.exe"
ZIM_FOLDER = r"B:\Wiki"
PORT = 8088

# === DEFINE ICONS WITH TAGS ===
ICON_SUCCESS = ("[✔] ", "success")
ICON_ERROR = ("[✖] ", "error")
ICON_WARNING = ("[!] ", "warning")
ICON_INFO = ("[i] ", "info")
ICON_STOPPED = ("[x] ", "stopped")

# === FUNCTION TO HANDLE RESOURCES IN .EXE ===
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# === GET LOCAL IP ===
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# === STOP ALL EXISTING INSTANCES OF KIWIX SERVER ===
def kill_existing_kiwix():
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            if proc.info['name'] == 'kiwix-serve.exe' or (
                proc.info['exe'] and os.path.basename(proc.info['exe']) == 'kiwix-serve.exe'
            ):
                proc.terminate()
                append_log(f"Stopped existing instance: {proc.info['name']}", ICON_WARNING)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

# === CHECK IF SERVER IS RUNNING ===
def is_server_running():
    if server_process is None:
        return False
    return server_process.poll() is None

# === START SERVER ===
def start_server():
    global server_process
    if is_server_running():
        append_log("Server already running!", ICON_INFO)
        return

    zim_files = glob.glob(os.path.join(ZIM_FOLDER, "*.zim"))
    if not zim_files:
        update_status_label("No ZIM files found!", "error")
        append_log("No ZIM files found in the specified folder.", ICON_ERROR)
        return

    kill_existing_kiwix()

    command = [KIWIX_PATH, "--port", str(PORT)] + zim_files

    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        server_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            startupinfo=startupinfo
        )
        ip = get_ip()
        update_status_label(f"Running on http://{ip}:{PORT}", "success")
        append_log(f"Server started successfully on http://{ip}:{PORT}", ICON_SUCCESS)
        threading.Thread(target=stream_output, daemon=True).start()
    except Exception as e:
        update_status_label(f"Error: {e}", "error")
        append_log(f"Error starting server: {e}", ICON_ERROR)

# === STREAM KIWIX OUTPUT TO UI ===
def stream_output():
    for line in server_process.stdout:
        append_log(line.strip())

# === STOP SERVER ===
def stop_server():
    global server_process
    kill_existing_kiwix()
    server_process = None
    update_status_label("Server stopped.", "error")
    append_log("Server stopped manually.", ICON_STOPPED)

# === APPEND LOG TO UI WITH OPTIONAL ICON ===
def append_log(message, icon=None):
    if icon:
        icon_text, tag = icon
        log_area.insert(tk.END, icon_text, tag)
    log_area.insert(tk.END, message + "\n")
    log_area.see(tk.END)

# === COLORED STATUS LABEL FUNCTION ===
def update_status_label(message, tag="info"):
    colors = {
        "success": "green",
        "error": "red",
        "warning": "orange",
        "info": "blue",
        "stopped": "gray"
    }
    emoji_map = {
        "success": "✔",
        "error": "✖",
        "warning": "!",
        "info": "i",
        "stopped": "⛔"
    }
    emoji = emoji_map.get(tag, "")
    color = colors.get(tag, "#333")
    status_label.config(text=f"{emoji} {message}", fg=color)

# === CLOSE WINDOW ===
def close_app():
    stop_server()
    root.destroy()

# === GUI SETUP ===
root = tk.Tk()
root.title("Kiwix Server GUI")
root.geometry("700x500")
root.configure(bg="#e6f2ff")

ico_path = resource_path("Kiwix.ico")
if os.path.exists(ico_path):
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("kiwix.server.gui")
    root.iconbitmap(ico_path)

root.protocol("WM_DELETE_WINDOW", close_app)

# === Title Label ===
title_label = tk.Label(root, text="Kiwix Server Manager", font=("Helvetica", 16, "bold"), bg="#e6f2ff", fg="#1f3a93")
title_label.pack(pady=(15, 5))

# === Buttons ===
btn_frame = tk.Frame(root, bg="#e6f2ff")
btn_frame.pack()

start_btn = tk.Button(btn_frame, text="🚀 Start Server", command=start_server, font=("Arial", 12), bg="#90ee90", width=15, relief="flat")
start_btn.grid(row=0, column=0, padx=10)

stop_btn = tk.Button(btn_frame, text="⛔ Stop Server", command=stop_server, font=("Arial", 12), bg="#ff8b94", width=15, relief="flat")
stop_btn.grid(row=0, column=1, padx=10)

# === Hover effects ===
def on_enter_start(e):
    start_btn.config(bg="#77dd77")  # brighter green

def on_leave_start(e):
    start_btn.config(bg="#90ee90")  # original green

def on_enter_stop(e):
    stop_btn.config(bg="#ff6f61")  # brighter red

def on_leave_stop(e):
    stop_btn.config(bg="#ff8b94")  # original red

start_btn.bind("<Enter>", on_enter_start)
start_btn.bind("<Leave>", on_leave_start)
stop_btn.bind("<Enter>", on_enter_stop)
stop_btn.bind("<Leave>", on_leave_stop)


# === Status Label BELOW buttons ===
status_label = tk.Label(root, text="", font=("Helvetica", 14), bg="#e6f2ff", fg="#333")
status_label.pack(pady=(5, 10))

# === Log Viewer ===
log_area = scrolledtext.ScrolledText(root, width=80, height=20, font=("Courier New", 10), bg="#f9f9f9", wrap=tk.WORD)
log_area.pack(padx=15, pady=5)

# === Define text color tags ===
log_area.tag_config("success", foreground="green")
log_area.tag_config("error", foreground="red")
log_area.tag_config("warning", foreground="orange")
log_area.tag_config("info", foreground="blue")
log_area.tag_config("stopped", foreground="gray")

# === AUTO START SERVER ===
server_process = None
if not is_server_running():
    start_server()

root.mainloop()
