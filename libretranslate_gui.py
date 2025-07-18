import tkinter as tk
from tkinter import font
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading
import os
import sys
import socket

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class LibreTranslateGUI:
    def __init__(self, root):
        self.root = root        
        self.root.title("LibreTranslate Server Manager")
        self.root.iconbitmap(resource_path("Translate.ico"))
        self.root.geometry("700x500")
        self.root.configure(bg="#e6f0ff")  # Light background

        self.process = None

        self.button_font = font.Font(family="Helvetica", size=11, weight="bold")
        self.label_font = font.Font(family="Consolas", size=10)

        # Title
        title = tk.Label(root, text="LibreTranslate Server Manager", bg="#e6f0ff", fg="#000000", font=("Helvetica", 16, "bold"))
        title.pack(pady=(10, 5))

        # Button Frame
        button_frame = tk.Frame(root, bg="#e6f0ff")
        button_frame.pack(pady=5)

        self.start_button = tk.Button(button_frame, text="▶ Restart Server", command=self.restart_server,
                                      width=20, font=self.button_font, bg="#1565c0", fg="white", relief="flat")
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(button_frame, text="■ Stop Server", command=self.stop_server,
                                     width=20, font=self.button_font, bg="#b22222", fg="white", relief="flat")
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Server Access URL Label
        self.access_label = tk.Label(root, text="", bg="#e6f0ff", fg="#000000", font=self.label_font)
        self.access_label.pack(pady=(5, 10))

        # Log Area
        self.log_area = ScrolledText(root, height=20, width=85, state='disabled',
                                     bg="#ffffff", fg="#000000", font=("Consolas", 10))
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Auto start on launch
        self.start_server()

    def start_server(self):
        if self.process is None:
            self.append_log("[INFO] Starting LibreTranslate...\n", "info")
            threading.Thread(target=self.run_server, daemon=True).start()
        else:
            self.restart_server()

    def stop_server(self):
        self.append_log("[STOP] Stopping LibreTranslate...\n", "error")
        if self.process:
            self.process.terminate()
            self.process = None
        self.append_log("[STOP] LibreTranslate server stopped.\n", "error")
        self.access_label.config(text="")

    def restart_server(self):
        self.stop_server()
        self.start_server()

    def run_server(self):
        try:
            db_folder = os.path.join(os.getenv("TEMP"), "LibreTranslate")
            os.makedirs(db_folder, exist_ok=True)
            os.chdir(db_folder)

            command = [
                'libretranslate', '--host', '0.0.0.0', '--port', '8081', '--debug'
            ]

            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            ip = self.get_local_ip()
            self.access_label.config(text=f"Access at: http://{ip}:8081")

            for line in self.process.stdout:
                self.display_colored_log(line)

        except Exception as e:
            self.append_log(f"[ERROR] {str(e)}\n", "error")
            self.process = None

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "127.0.0.1"
        return ip

    def display_colored_log(self, line):
        lower_line = line.lower()
        if "[error" in lower_line or "error" in lower_line:
            tag = "error"
        elif "warn" in lower_line:
            tag = "warn"
        elif "[info" in lower_line or "info" in lower_line:
            tag = "info"
        else:
            tag = "normal"
        self.append_log(line, tag)

    def append_log(self, message, tag="normal"):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message, tag)
        self.log_area.configure(state='disabled')
        self.log_area.yview(tk.END)

    def on_close(self):
        self.append_log("[STOP] Closing app and stopping server...\n", "error")
        self.stop_server()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LibreTranslateGUI(root)

    # Color tags for log area
    app.log_area.tag_config("info", foreground="green")
    app.log_area.tag_config("warn", foreground="orange")
    app.log_area.tag_config("error", foreground="red")
    app.log_area.tag_config("normal", foreground="#1565c0")  # Normal operation: blue

    root.mainloop()
