import tkinter as tk
from tkinter import font
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading
import socket
import os
import psutil
import sys

def resource_path(relative_path):
    """Get absolute path to resource (for dev and PyInstaller EXE)"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class NavidromeGUI:
    def __init__(self, root):
        self.root = root        
        self.root.title("Navidrome Server GUI")
        # Set the window icon
        self.root.iconbitmap(resource_path("Navidrom.ico"))
        self.root.geometry("700x450")
        self.root.configure(bg="#1e1e1e")

        self.process = None

        self.button_font = font.Font(family="Helvetica", size=11, weight="bold")
        self.label_font = font.Font(family="Consolas", size=10)

        title = tk.Label(root, text="Navidrome Server Manager", bg="#1e1e1e", fg="#00ffcc", font=("Helvetica", 16, "bold"))
        title.pack(pady=(10, 5))

        button_frame = tk.Frame(root, bg="#1e1e1e")
        button_frame.pack(pady=5)

        # Start Button
        self.start_button = tk.Button(button_frame, text="▶ Start Server", command=self.start_server,
                                      width=20, font=self.button_font, bg="#2e8b57", fg="white", relief="flat")
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Stop Button
        self.stop_button = tk.Button(button_frame, text="■ Stop Server", command=self.stop_all_navidrome,
                                     width=20, font=self.button_font, bg="#b22222", fg="white", relief="flat")
        self.stop_button.pack(side=tk.LEFT, padx=10)

        self.access_label = tk.Label(root, text="", bg="#1e1e1e", fg="#dddddd", font=self.label_font)
        self.access_label.pack(pady=(5, 10))

        self.log_area = ScrolledText(root, height=20, width=85, state='disabled',
                                     bg="#121212", fg="#00ff00", font=("Consolas", 10))
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Handle window close
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.after(100, self.start_server)  # Start the server a bit after the window is ready

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def start_server(self):
        if self.process is None:
            self.append_log("Starting Navidrome...\n")
            ip = self.get_local_ip()
            self.access_label.config(text=f"🔗 Access at: http://{ip}:8091")
            threading.Thread(target=self.run_server, daemon=True).start()
            self.start_button.config(text="▶ Restart Server")
        else:
            self.restart_server()

    def stop_all_navidrome(self):
        self.append_log("Stopping all Navidrome instances...\n")
        count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and 'navidrome' in proc.info['name'].lower():
                    proc.kill()
                    count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        self.process = None
        self.access_label.config(text="")
        self.append_log(f"Killed {count} Navidrome process(es).\n")
        self.start_button.config(text="▶ Start Server")  # Change button text back to 'Start'

    def restart_server(self):
        self.append_log("Restarting Navidrome...\n")
        self.stop_all_navidrome()
        self.start_server()

    def run_server(self):
        try:
            navidrome_path = "B:/Navidrome/navidrome.exe"
            self.process = subprocess.Popen(
                [navidrome_path],
                cwd="B:/Navidrome",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            for line in self.process.stdout:
                self.append_log(line)
        except Exception as e:
            self.append_log(f"Error: {str(e)}\n")
            self.process = None

    def append_log(self, message):
        try:
            self.log_area.configure(state='normal')
            self.log_area.insert(tk.END, message)
            self.log_area.configure(state='disabled')
            self.log_area.yview(tk.END)
        except:
            pass

    def on_close(self):
        self.append_log("Closing app and stopping Navidrome...\n")
        self.stop_all_navidrome()
        self.root.destroy()

    # Mouse hover effect functions
    def on_enter_start(self, event):
        self.start_button.config(bg="#3cb371")

    def on_leave_start(self, event):
        self.start_button.config(bg="#2e8b57")

    def on_enter_stop(self, event):
        self.stop_button.config(bg="#dc143c")

    def on_leave_stop(self, event):
        self.stop_button.config(bg="#b22222")

if __name__ == "__main__":
    root = tk.Tk()
    app = NavidromeGUI(root)

    # Bind mouse hover events to buttons
    app.start_button.bind("<Enter>", app.on_enter_start)
    app.start_button.bind("<Leave>", app.on_leave_start)
    app.stop_button.bind("<Enter>", app.on_enter_stop)
    app.stop_button.bind("<Leave>", app.on_leave_stop)

    root.mainloop()
