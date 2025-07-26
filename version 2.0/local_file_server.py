import http.server
import socketserver
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import socket
import os
import time
import sys
import json
import re
from io import StringIO
import base64
import hashlib
import secrets

PORT = 8000
server_thread = None
FOLDER_SELECTED = None
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "password"  # Default password
SESSION_TOKENS = {}

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, text):
        self.widget.after(0, lambda: self.widget.insert(tk.END, text))
        self.widget.after(0, lambda: self.widget.see(tk.END))

    def flush(self):
        pass

def get_ip():
    return socket.gethostbyname(socket.gethostname())

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
    def authenticate(self):
        """Check if user is authenticated via session token"""
        cookie = self.headers.get('Cookie', '')
        cookies = {}
        for c in cookie.split(';'):
            parts = c.strip().split('=')
            if len(parts) == 2:
                cookies[parts[0]] = parts[1]
                
        token = cookies.get('session_token')
        return token and token in SESSION_TOKENS

    def log_message(self, format, *args):
        print(self.address_string(), "-", self.log_date_time_string(), "-", format % args)

    def do_POST(self):
        # Handle login requests
        if self.path == "/login":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return
                
            username = data.get('username', '')
            password = data.get('password', '')
            
            if username == AUTH_USERNAME and password == AUTH_PASSWORD:
                # Generate session token
                token = secrets.token_urlsafe(32)
                SESSION_TOKENS[token] = time.time() + 3600  # 1 hour expiration
                
                self.send_response(200)
                self.send_header('Set-Cookie', f'session_token={token}; Path=/; HttpOnly')
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'Invalid credentials')
            return
        
        # Handle logout
        if self.path == "/logout":
            token = self.headers.get('Cookie', '').split('session_token=')[-1].split(';')[0]
            if token in SESSION_TOKENS:
                del SESSION_TOKENS[token]
            self.send_response(200)
            self.send_header('Set-Cookie', 'session_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
            self.end_headers()
            self.wfile.write(b'Logged out')
            return
        
        # Protected operations
        if self.path in ["/delete", "/rename"]:
            if not self.authenticate():
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'Authentication required')
                return
        
        # Original file operations
        if self.path == "/delete":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            filename = data.get("filename")
            filepath = os.path.join(os.getcwd(), os.path.basename(filename))
            if os.path.exists(filepath):
                os.remove(filepath)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Deleted")
            else:
                self.send_error(404, "File not found")
            return

        if self.path == "/rename":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            old = os.path.basename(data.get("oldName"))
            new = os.path.basename(data.get("newName"))
            if not old or not new:
                self.send_error(400, "Missing name(s)")
                return
            old_path = os.path.join(os.getcwd(), old)
            new_path = os.path.join(os.getcwd(), new)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Renamed")
            else:
                self.send_error(404, "File not found")
            return

        # File upload handling
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            self.send_error(400, "Bad Request: Expected multipart/form-data")
            return

        boundary = content_type.split("boundary=")[-1].encode()
        remainbytes = int(self.headers['Content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)

        if boundary not in line:
            self.send_error(400, "Content does not begin with boundary")
            return

        line = self.rfile.readline()
        remainbytes -= len(line)
        filename = None
        while line and line.strip():
            if b'Content-Disposition' in line and b'filename="' in line:
                filename = line.decode().split('filename="')[-1].split('"')[0]
            line = self.rfile.readline()
            remainbytes -= len(line)

        if not filename:
            self.send_error(400, "No file uploaded")
            return

        filename = re.sub(r'[\\/*?:"<>|]', "_", os.path.basename(filename))
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, 'wb') as out:
            preline = self.rfile.readline()
            remainbytes -= len(preline)
            while remainbytes > 0:
                line = self.rfile.readline()
                remainbytes -= len(line)
                if boundary in line:
                    out.write(preline.rstrip(b'\r\n'))
                    break
                else:
                    out.write(preline)
                    preline = line

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def list_directory(self, path):
        try:
            file_list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None

        file_list.sort(key=lambda a: a.lower())
        rel_path = os.path.relpath(path, os.getcwd())
        is_ajax = self.headers.get('X-Requested-With') == 'XMLHttpRequest'
        is_authenticated = self.authenticate()

        # Generate auth button HTML
        if is_authenticated:
            auth_button = '<button onclick="logout()" style="position:absolute;top:10px;right:100px;">Logout</button>'
        else:
            auth_button = '<button onclick="showLoginModal()" style="position:absolute;top:10px;right:100px;">Login</button>'

        rows = []
        for name in file_list:
            full_path = os.path.join(path, name)
            displayname = name + "/" if os.path.isdir(full_path) else name
            linkname = name + "/" if os.path.isdir(full_path) else name
            stat = os.stat(full_path)
            size = "-" if os.path.isdir(full_path) else f"{stat.st_size / (1024*1024):.2f} MB"
            preview_html = ""

            if name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                preview_html = f'<img src="{linkname}">'
            elif name.lower().endswith(('.mp3', '.wav', '.ogg')):
                preview_html = f'<audio controls src="{linkname}"></audio>'
            elif name.lower().endswith(('.mp4', '.webm', '.ogg')):
                preview_html = f'<video controls src="{linkname}"></video>'
                
            # Only show action buttons if authenticated
            action_buttons = ""
            if is_authenticated:
                action_buttons = (
                    f'<td><button onclick="deleteFile(\'{linkname}\')">🗑 Delete</button> '
                    f'<button onclick="renameFile(\'{linkname}\')">✏ Rename</button></td>'
                )
            else:
                action_buttons = '<td>Login required</td>'

            rows.append(
                f'<tr><td><a href="{linkname}">{displayname}</a></td>'
                f'<td>{size}</td><td>{preview_html}</td>'
                f'{action_buttons}</tr>'
            )

        if is_ajax:
            # Return JSON with both file list and auth button
            response_data = {
                "table": "\n".join(rows),
                "authButton": auth_button
            }
            encoded = json.dumps(response_data).encode('utf-8', 'surrogateescape')
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return None

        # HTML for the full page
        html = f"""<!DOCTYPE html>
<html lang='en' data-theme='light'>
<head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>LAN File Share</title>
<style>
:root {{
  --blue:#2196F3;
  --bg:#fff;
  --text:#212529;
  --border:#dee2e6;
  --accent:#0d6efd;
  --form-bg:#fff;
  --input-bg:#f8f9fa;
  --input-text:#212529;
}}
[data-theme=dark] {{
  --bg:#121212;
  --text:#f1f1f1;
  --border:#333;
  --accent:#0dcaf0;
  --form-bg:#1e1e1e;
  --input-bg:#2a2a2a;
  --input-text:#f1f1f1;
}}

a {{
  color: var(--accent);
  text-decoration: none;
}}
a:hover {{
  text-decoration: underline;
}}

body {{
  background:var(--bg);
  color:var(--text);
  font-family:sans-serif;
  margin:0;
  padding:1rem;
}}
button, input {{
  font-size:1rem;
}}
.upload-form {{
  max-width:500px;
  margin:auto;
  background:var(--form-bg);
  padding:1em;
  border-radius:8px;
  border:1px solid var(--border);
}}
input[type='file'] {{
  background:var(--input-bg);
  color:var(--input-text);
  border:1px solid var(--border);
  padding:0.4em;
  width:100%;
  border-radius:4px;
  margin-bottom:0.5em;
}}
input[type='submit'] {{
  background:var(--accent);
  color:white;
  padding:0.5em 1em;
  border:none;
  cursor:pointer;
  border-radius:4px;
}}
.toggle {{
  position:absolute;
  top:10px;
  right:10px;
  border:1px solid var(--border);
  padding:0.3em 0.6em;
  background:transparent;
  color:var(--text);
  cursor:pointer;
  border-radius:4px;
}}
table {{
  width:100%;
  border-collapse:collapse;
  margin-top:1em;
}}
th, td {{
  padding:0.5em;
  border-bottom:1px solid var(--border);
}}
img, video, audio {{
  max-height:100px;
  max-width:100%;
  display:block;
  margin:auto;
}}
#toast {{
  position:fixed;
  bottom:20px;
  left:50%;
  transform:translateX(-50%);
  background:var(--accent);
  color:white;
  padding:10px 20px;
  border-radius:8px;
  display:none;
}}
.modal {{
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  z-index: 1000;
}}
.modal-content {{
  background: var(--form-bg);
  width: 300px;
  margin: 100px auto;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}}
</style></head>
<body>
<button class='toggle' onclick='toggleTheme()'>🌗</button>
<div id="authButtonContainer">{auth_button}</div>
<h2>📂 Folder: /{rel_path}</h2>
<div class='upload-form'>
  <form id='uploadForm' onsubmit='return uploadFile(event)'>
    <input id='fileInput' name='file' type='file' required><br>
    <input type='submit' value='Upload'>
    <div id='progressBarContainer'><div id='progressBar'></div></div>
  </form>
</div>
<div id='loader' style='display:none;text-align:center;'>🔄 Refreshing...</div>
<table id='fileTable'><tr><th>Name</th><th>Size</th><th>Preview</th><th>Action</th></tr>
""" + '\n'.join(rows) + """</table>
<div id='toast'>Upload successful!</div>

<div id="loginModal" class="modal">
  <div class="modal-content">
    <h3>Login Required</h3>
    <form id="loginForm">
      <input type="text" id="username" placeholder="Username" required style="width:100%;padding:8px;margin-bottom:10px">
      <input type="password" id="password" placeholder="Password" required style="width:100%;padding:8px;margin-bottom:10px">
      <button type="submit" style="background:#2196F3;color:white;border:none;padding:8px;width:100%;border-radius:4px">Login</button>
    </form>
    <button onclick="document.getElementById('loginModal').style.display='none'" style="background:#f44336;color:white;border:none;padding:8px;width:100%;margin-top:10px;border-radius:4px">Cancel</button>
  </div>
</div>

<script>
let pendingOperation = null;

function toggleTheme() {
  const html = document.documentElement;
  const theme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}
(function () {
  const saved = localStorage.getItem('theme');
  const system = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', saved || system);
})();
function uploadFile(event) {
  event.preventDefault();
  const form = document.getElementById('uploadForm');
  const formData = new FormData(form);
  fetch('/', { method: 'POST', body: formData }).then(res => {
    if (res.ok) {
      showToast('✅ Upload successful');
      form.reset();
      refreshFileList();
    } else showToast('❌ Upload failed');
  }).catch(() => showToast('⚠️ Upload error'));
  return false;
}
function refreshFileList() {
  document.getElementById('loader').style.display = 'block';
  fetch(window.location.href, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(res => res.json())
    .then(data => {
      document.getElementById('fileTable').innerHTML = data.table;
      document.getElementById('authButtonContainer').innerHTML = data.authButton;
      document.getElementById('loader').style.display = 'none';
    })
    .catch(err => {
      console.error('Error refreshing file list:', err);
      document.getElementById('loader').style.display = 'none';
    });
}
function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.style.display = 'block';
  setTimeout(() => toast.style.display = 'none', 3000);
}
function deleteFile(filename) {
  if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;
  
  const operation = () => {
    fetch('/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename })
    }).then(res => {
      if (res.ok) {
        showToast('🗑 File deleted');
        refreshFileList();
      } else if (res.status === 401) {
        showLoginModal(() => deleteFile(filename));
      } else {
        showToast('❌ Delete failed');
      }
    });
  };
  
  operation();
}
function renameFile(oldName) {
  const newName = prompt("Enter new filename:", oldName);
  if (!newName || newName === oldName) return;
  
  const operation = () => {
    fetch('/rename', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ oldName, newName })
    }).then(res => {
      if (res.ok) {
        showToast('✏ File renamed');
        refreshFileList();
      } else if (res.status === 401) {
        showLoginModal(() => renameFile(oldName));
      } else {
        showToast('❌ Rename failed');
      }
    });
  };
  
  operation();
}
function showLoginModal(operation) {
  pendingOperation = operation;
  document.getElementById('loginModal').style.display = 'block';
}
document.getElementById('loginForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  }).then(res => {
    if (res.ok) {
      document.getElementById('loginModal').style.display = 'none';
      showToast('🔓 Login successful');
      if (pendingOperation) pendingOperation();
      refreshFileList();  // Update button state
    } else {
      showToast('❌ Login failed');
    }
  });
});
function logout() {
  fetch('/logout', { method: 'POST' })
    .then(res => {
      if (res.ok) {
        showToast('👋 Logged out');
        refreshFileList();  // Update button state
      }
    });
}
</script></body></html>"""

        encoded = html.encode('utf-8', 'surrogateescape')
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

def stop_server(httpd):
    if httpd:
        httpd.shutdown()
        httpd.server_close()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple LAN File Share")
        self.httpd = None
        self.countdown = 60
        self.timer_label = None
        self.timer_thread = None

        self.setup_ui()

        self.log_output = tk.Text(self.container, height=15, bg="#111", fg="#0f0", font=("Courier", 10))
        self.log_output.pack(pady=10, fill=tk.BOTH, expand=True)

        sys.stdout = TextRedirector(self.log_output, "stdout")
        sys.stderr = TextRedirector(self.log_output, "stderr")

        self.start_countdown()

    def setup_ui(self):
        self.container = tk.Frame(self.root, bg="#f4f4f4", padx=20, pady=20)
        self.container.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        self.title_label = tk.Label(self.container, text="Choose a folder to share:", font=("Arial", 16), bg="#f4f4f4")
        self.title_label.pack(pady=10)

        self.btn_choose = tk.Button(self.container, text="Browse Folder", command=self.choose_folder, font=("Arial", 14), bg="#2196F3", fg="white", relief="solid")
        self.btn_choose.pack(pady=10, fill=tk.X)

        self.timer_label = tk.Label(self.container, text=f"Time left: {self.countdown}s", font=("Arial", 14), bg="#f4f4f4", fg="red")
        self.timer_label.pack(pady=10)

        self.label_link = tk.Label(self.container, text="", font=("Arial", 14), bg="#f4f4f4")
        self.label_link.pack(pady=10)

        # Authentication configuration
        auth_frame = tk.LabelFrame(self.container, text="Authentication Settings", padx=10, pady=10, bg="#f4f4f4")
        auth_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(auth_frame, text="Username:", bg="#f4f4f4").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.username_var = tk.StringVar(value=AUTH_USERNAME)
        tk.Entry(auth_frame, textvariable=self.username_var).grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(auth_frame, text="Password:", bg="#f4f4f4").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.password_var = tk.StringVar(value=AUTH_PASSWORD)
        tk.Entry(auth_frame, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=5, pady=2)
        
        tk.Button(auth_frame, text="Apply Credentials", command=self.update_credentials, 
                 bg="#4CAF50", fg="white").grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        
        self.btn_stop = tk.Button(self.container, text="Stop Server", command=self.stop_server, font=("Arial", 14), bg="#FF6347", fg="white", state=tk.DISABLED)
        self.btn_stop.pack(pady=10, fill=tk.X)

        # Try to set icon (ignore if file doesn't exist)
        try:
            root.iconbitmap(r'C:\Users\Aditya\Desktop\pyton try\file_host.ico')
        except:
            pass

    def update_credentials(self):
        """Update global credentials from UI"""
        global AUTH_USERNAME, AUTH_PASSWORD
        AUTH_USERNAME = self.username_var.get()
        AUTH_PASSWORD = self.password_var.get()
        
        # Clear existing sessions
        global SESSION_TOKENS
        SESSION_TOKENS = {}
        
        messagebox.showinfo("Credentials Updated", 
                          f"Authentication credentials updated\nUsername: {AUTH_USERNAME}\n"
                          "All existing sessions have been invalidated")

    def start_countdown(self):
        def countdown():
            while self.countdown > 0:
                if FOLDER_SELECTED is not None:
                    break
                self.countdown -= 1
                self.timer_label.config(text=f"Time left: {self.countdown}s")
                self.root.update()
                time.sleep(1)

            if self.countdown == 0 and FOLDER_SELECTED is None:
                self.use_current_directory()

        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            global FOLDER_SELECTED
            FOLDER_SELECTED = folder
            self.httpd = start_server(folder)
            ip = get_ip()
            link = f"http://{ip}:{PORT}"
            self.label_link.config(text=f"Now Sharing:\n{link}")
            self.btn_stop.config(state=tk.NORMAL)
            self.countdown = 0
            self.timer_label.config(text="Folder selected, starting server...")
            self.timer_label.pack_forget()

    def use_current_directory(self):
        global FOLDER_SELECTED
        if FOLDER_SELECTED is None:
            FOLDER_SELECTED = os.getcwd()
            self.httpd = start_server(FOLDER_SELECTED)
            ip = get_ip()
            link = f"http://{ip}:{PORT}"
            self.label_link.config(text=f"Now Sharing:\n{link}")
            self.btn_stop.config(state=tk.NORMAL)
            self.timer_label.pack_forget()

    def stop_server(self):
        stop_server(self.httpd)
        self.label_link.config(text="Server stopped.")
        self.btn_stop.config(state=tk.DISABLED)

if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except Exception as e:
        import traceback
        import tkinter.messagebox as msg
        msg.showerror("Error", f"An error occurred:\n{traceback.format_exc()}")
