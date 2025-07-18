import http.server
import socketserver
import threading
import tkinter as tk
from tkinter import filedialog
import socket
import os
import time
import sys
from io import StringIO

PORT = 8000
server_thread = None
FOLDER_SELECTED = None

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, text):
        self.widget.after(0, lambda: self.widget.insert(tk.END, text))
        self.widget.after(0, lambda: self.widget.see(tk.END))

    def flush(self):
        pass


# Get the local IP address
def get_ip():
    return socket.gethostbyname(socket.gethostname())

# Start the HTTP server with the selected folder
class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_server(path):
    global server_thread
    os.chdir(path)
    handler = CustomHandler
    httpd = ReusableTCPServer(("", PORT), handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return httpd

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        print(self.address_string(), "-", self.log_date_time_string(), "-", format % args)
    def list_directory(self, path):
        try:
            file_list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None

        file_list.sort(key=lambda a: a.lower())
        rel_path = os.path.relpath(path, os.getcwd())

        html = [f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>📂 LAN Share - {rel_path}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
            transition: background-color 0.3s, color 0.3s;
        }}
        .dark-mode {{
            background-color: #1e1e1e;
            color: #ddd;
        }}
        h2 {{
            text-align: center;
            font-size: 24px;
        }}
        .toggle {{
            position: absolute;
            top: 20px;
            right: 20px;
            cursor: pointer;
            font-size: 18px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .dark-mode table {{
            background: #2c2c2c;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .dark-mode th, .dark-mode td {{
            border-color: #444;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        .dark-mode tr:hover {{
            background-color: #333;
        }}
        a {{
            text-decoration: none;
            color: #2196F3;
        }}
        img.preview {{
            max-height: 100px;
        }}
        audio, video {{
            max-width: 200px;
            display: block;
            margin-top: 5px;
        }}
    </style>
    <script>
        function toggleMode() {{
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
        }}
        window.onload = () => {{
            if (localStorage.getItem('theme') === 'dark') {{
                document.body.classList.add('dark-mode');
            }}
        }}
    </script>
</head>
<body>
    <div class="toggle" onclick="toggleMode()">🌓</div>
    <h2>📂 Sharing: /{rel_path}</h2>
    <table>
        <tr><th>Name</th><th>Size</th><th>Preview</th></tr>
"""]

        for name in file_list:
            full_path = os.path.join(path, name)
            displayname = name + "/" if os.path.isdir(full_path) else name
            linkname = name + "/" if os.path.isdir(full_path) else name
            stat = os.stat(full_path)
            size = "-" if os.path.isdir(full_path) else f"{stat.st_size / (1024*1024):.2f} MB"
            preview_html = ""

            # Image preview
            if name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                preview_html = f'<img src="{linkname}" class="preview">'
            # Audio preview
            elif name.lower().endswith(('.mp3', '.wav', '.ogg')):
                preview_html = f'<audio controls src="{linkname}"></audio>'
            # Video preview
            elif name.lower().endswith(('.mp4', '.webm', '.ogg')):
                preview_html = f'<video controls src="{linkname}"></video>'

            html.append(
                f'<tr><td><a href="{linkname}">{displayname}</a></td>'
                f'<td>{size}</td><td>{preview_html}</td></tr>\n'
            )

        html.append("</table></body></html>")
        encoded = '\n'.join(html).encode('utf-8', 'surrogateescape')

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

# Stop the server
def stop_server(httpd):
    if httpd:
        httpd.shutdown()
        httpd.server_close()
# UI App Class
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple LAN File Share")
        self.httpd = None
        self.countdown = 60  # 60 seconds countdown timer
        self.timer_label = None
        self.timer_thread = None

        # UI Elements
        self.setup_ui()
        # Add a Text widget for logs
        self.log_output = tk.Text(self.container, height=15, bg="#111", fg="#0f0", font=("Courier", 10))
        self.log_output.pack(pady=10, fill=tk.BOTH, expand=True)

        # Redirect stdout and stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        sys.stdout = TextRedirector(self.log_output, "stdout")
        sys.stderr = TextRedirector(self.log_output, "stderr")


        # Start countdown
        self.start_countdown()

    def setup_ui(self):
        # Container
        self.container = tk.Frame(self.root, bg="#f4f4f4", padx=20, pady=20)
        self.container.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Title Label
        self.title_label = tk.Label(self.container, text="Choose a folder to share:", font=("Arial", 16), bg="#f4f4f4")
        self.title_label.pack(pady=10)

        # Browse Button
        self.btn_choose = tk.Button(self.container, text="Browse Folder", command=self.choose_folder, font=("Arial", 14), bg="#2196F3", fg="white", relief="solid")
        self.btn_choose.pack(pady=10, fill=tk.X)

        # Countdown Timer Label
        self.timer_label = tk.Label(self.container, text=f"Time left: {self.countdown}s", font=("Arial", 14), bg="#f4f4f4", fg="red")
        self.timer_label.pack(pady=10)

        # Display link after folder is chosen
        self.label_link = tk.Label(self.container, text="", font=("Arial", 14), bg="#f4f4f4")
        self.label_link.pack(pady=10)

        # Stop Server Button
        self.btn_stop = tk.Button(self.container, text="Stop Server", command=self.stop_server, font=("Arial", 14), bg="#FF6347", fg="white", state=tk.DISABLED)
        self.btn_stop.pack(pady=10, fill=tk.X)

    def start_countdown(self):
        """Start the countdown timer for 60 seconds."""
        def countdown():
            while self.countdown > 0:
                if FOLDER_SELECTED is not None:
                    break  # If a folder is selected, stop the countdown
                self.countdown -= 1
                self.timer_label.config(text=f"Time left: {self.countdown}s")
                self.root.update()
                time.sleep(1)
            
            if self.countdown == 0 and FOLDER_SELECTED is None:
                self.use_current_directory()

        # Start the countdown in a separate thread
        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()

    def choose_folder(self):
        """Allow user to select a folder using the file dialog."""
        folder = filedialog.askdirectory()
        if folder:
            global FOLDER_SELECTED
            FOLDER_SELECTED = folder
            self.httpd = start_server(folder)
            ip = get_ip()
            link = f"http://{ip}:{PORT}"
            self.label_link.config(text=f"Now Sharing:\n{link}")
            self.btn_stop.config(state=tk.NORMAL)

            # Stop the countdown and hide the timer label once a folder is selected
            self.countdown = 0  # Prevent further countdown
            self.timer_label.config(text="Folder selected, starting server...")  # Update timer text
            self.timer_label.pack_forget()  # Remove timer label

    def use_current_directory(self):
        """Default to the current directory if no folder is selected within 60 seconds."""
        global FOLDER_SELECTED
        if FOLDER_SELECTED is None:
            FOLDER_SELECTED = os.getcwd()
            self.httpd = start_server(FOLDER_SELECTED)
            ip = get_ip()
            link = f"http://{ip}:{PORT}"
            self.label_link.config(text=f"Now Sharing:\n{link}")
            self.btn_stop.config(state=tk.NORMAL)

            # Hide the countdown timer once the server starts
            self.timer_label.pack_forget()

    def stop_server(self):
        """Stop the file server."""
        stop_server(self.httpd)
        self.label_link.config(text="Server stopped.")
        self.btn_stop.config(state=tk.DISABLED)

# Start the app
if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except Exception as e:
        import traceback
        import tkinter.messagebox as msg
        msg.showerror("Error", f"An error occurred:\n{traceback.format_exc()}")

