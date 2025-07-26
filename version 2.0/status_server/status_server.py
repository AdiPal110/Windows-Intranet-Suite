from flask import Flask, jsonify, send_from_directory
import socket
import os
import time
import concurrent.futures
from threading import Lock

app = Flask(__name__)

ICON_FILE = "search.ico"

# Configurable services with additional metadata
SERVICES = {
    "jellyfin": {"port": 8096, "emoji": "🎬", "domain": "jellyfin.lan"},
    "kiwix": {"port": 8088, "emoji": "📚", "domain": "kiwix.lan"},
    "navidrome": {"port": 8091, "emoji": "🎵", "domain": "navidrome.lan"},
    "translate": {"port": 8081, "emoji": "🌐", "domain": "translate.lan"},
    "dumbot": {"port": 1090, "emoji": "🤖", "domain": "dumbot.lan"},
    "drive": {"port": 8000, "emoji": "💾", "domain": "drive.lan"},
    "clock": {"port": 1224, "emoji": "⏰", "domain": "clock.lan"},
    "komga": {"port": 1111, "emoji": "📖", "domain": "komga.lan"},
    "games": {"port": 7815, "emoji": "🎮", "domain": "games.lan"},
}

# Configuration
STATUS_SERVER_PORT = 5050
STATUS_CHECK_TIMEOUT = 0.3  # seconds
CACHE_DURATION = 2  # seconds
OFFLINE_THRESHOLD = 5  # seconds to hide offline services

# Cache lock for thread safety
cache_lock = Lock()
last_status_cache = None
last_cache_time = 0

# Track offline durations
offline_durations = {name: 0 for name in SERVICES}

def is_port_open(host, port, timeout=STATUS_CHECK_TIMEOUT):
    """Check if a port is open with connection timeout."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def check_all_services():
    """Check all services concurrently with thread pooling."""
    global last_status_cache, last_cache_time
    
    with cache_lock:
        # Return cached result if still valid
        if time.time() - last_cache_time < CACHE_DURATION:
            return last_status_cache
        
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    is_port_open, 
                    "127.0.0.1", 
                    info["port"]
                ): name for name, info in SERVICES.items()
            }
            
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                results[name] = future.result()
        
        # Update offline durations
        current_time = time.time()
        for name in SERVICES:
            if results.get(name, False):
                offline_durations[name] = 0  # Reset if online
            else:
                # Increment duration if service is offline
                offline_durations[name] += current_time - last_cache_time if last_cache_time > 0 else 0
        
        # Update cache
        last_status_cache = results
        last_cache_time = current_time
        return results

# Routes
@app.route("/about.html")
def serve_about():
    return send_from_directory("icons/pages", "about.html")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("icons", "search.ico", mimetype='image/vnd.microsoft.icon')

@app.route("/api/status")
def api_status():
    # Add cache control headers
    response = jsonify({
        "status": check_all_services(),
        "offline_durations": offline_durations
    })
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/icons/<path:filename>")
def serve_icon(filename):
    icon_dir = os.path.join(os.path.dirname(__file__), "icons")
    return send_from_directory(icon_dir, filename)

@app.route("/")
def status_dashboard():
    # HTML template with improved structure and accessibility
    return f"""
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LanScout</title>
  <link rel="icon" href="/search.ico" type="image/x-icon">
  <style>
    :root {{
      --bg: #f5f5f5; --text: #111; --box: #ffffff;
      --online: #4caf50; --offline: #f44336; --border: #ccc;
      --hover: #e9e9e9; --active: #d9d9d9; --selected: #e0f7fa;
    }}
    [data-theme="dark"] {{
      --bg: #1e1e1e; --text: #eee; --box: #2c2c2c; 
      --border: #555; --hover: #383838; --active: #484848;
      --selected: #004d40;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; 
      font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
      background: var(--bg); color: var(--text);
      transition: background 0.3s, color 0.3s;
      line-height: 1.5;
    }}
    .top-bar {{
      display: flex; justify-content: space-between; 
      padding: 12px 16px; align-items: center;
      background: var(--box); border-bottom: 1px solid var(--border);
    }}
    .icon-btn {{
      width: 42px; height: 42px; background: none; border: none;
      font-size: 1.4rem; cursor: pointer; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      transition: background 0.2s;
    }}
    .icon-btn:hover {{ background: var(--hover); }}
    .icon-btn:active {{ background: var(--active); }}
    .search-bar {{
      margin: 20px auto 10px; 
      max-width: min(90%, 500px);
    }}
    .search-form {{
      display: flex; background: var(--box); 
      border: 2px solid var(--border); border-radius: 16px; 
      padding: 8px 16px;
    }}
    .search-form input {{
      border: none; background: transparent; outline: none;
      font-size: 1rem; flex-grow: 1; color: var(--text);
      padding: 0 8px;
    }}
    .search-form span {{ font-weight: bold; opacity: 0.8; }}
    .suggestions {{
      width: 100%; margin-top: 4px;
      background: var(--box); border: 1px solid var(--border);
      border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      max-height: 300px; overflow-y: auto; z-index: 10;
    }}
    .suggestions div {{
      padding: 10px 14px; cursor: pointer;
      border-bottom: 1px solid var(--border);
      transition: background 0.2s;
    }}
    .suggestions div.selected {{ 
      background: var(--selected); 
      border-left: 3px solid var(--online);
    }}
    .suggestions div:last-child {{ border-bottom: none; }}
    .suggestions div:hover {{ background: var(--hover); }}
    .grid {{
      display: grid; 
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 20px; padding: 20px; max-width: 900px; margin: 0 auto;
    }}
    .tile {{
      background: var(--box); border: 2px solid var(--border);
      border-radius: 12px; text-align: center; padding: 16px 10px;
      position: relative; cursor: pointer; transition: all 0.2s;
      aspect-ratio: 1/1; display: flex; flex-direction: column;
      justify-content: center; align-items: center;
      min-width: 0; /* Prevent overflow */
    }}
    .tile.hidden {{
      display: none; /* Changed to display:none for proper collapsing */
    }}
    .tile:hover {{ 
      transform: translateY(-3px); 
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
      border-color: var(--text);
    }}
    .tile:active {{ transform: translateY(0); }}
    .tile img {{
      width: 52px; height: 52px; object-fit: contain;
      margin-bottom: 8px;
    }}
    .name {{
      font-weight: bold; margin: 5px 0 0;
      font-size: 0.95rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }}
    .status-label {{
      position: absolute; right: 8px; top: 8px;
      font-size: 0.7rem; font-weight: bold; padding: 4px 8px;
      border-radius: 6px; color: white; text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .online {{ background: var(--online); }}
    .offline {{ background: var(--offline); }}
    
    /* Mobile responsiveness - 2 columns */
    @media (max-width: 600px) {{
      .grid {{
        grid-template-columns: repeat(2, minmax(120px, 1fr)); /* 2 columns */
        gap: 15px;
        padding: 15px;
      }}
      .tile {{
        padding: 14px 8px;
        border-width: 1px;
        border-radius: 10px;
      }}
      .tile img {{
        width: 48px;
        height: 48px;
      }}
      .name {{
        font-size: 0.95rem; /* Slightly larger text */
      }}
      .status-label {{
        font-size: 0.7rem;
        padding: 3px 6px;
        right: 6px;
        top: 6px;
      }}
      .search-bar {{
        margin: 15px auto 8px;
      }}
      .search-form {{
        padding: 6px 12px;
        font-size: 0.9rem;
      }}
    }}
    
    /* Very small screens - still 2 columns */
    @media (max-width: 400px) {{
      .grid {{
        grid-template-columns: repeat(2, minmax(100px, 1fr)); /* 2 columns */
        gap: 10px;
      }}
      .tile {{
        padding: 12px 5px;
      }}
      .tile img {{
        width: 42px;
        height: 42px;
      }}
      .name {{
        font-size: 0.85rem;
      }}
      .status-label {{
        font-size: 0.6rem;
        padding: 2px 4px;
      }}
      .search-form {{
        padding: 4px 8px;
      }}
      .search-form span {{
        font-size: 0.8rem;
      }}
    }}
    
    .sr-only {{
      position: absolute; width: 1px; height: 1px; 
      padding: 0; margin: -1px; overflow: hidden; 
      clip: rect(0, 0, 0, 0); border: 0;
    }}
  </style>
</head>
<body>
  <header class="top-bar">
    <a href="about.html" class="icon-btn" aria-label="About">
      <span aria-hidden="true">ℹ️</span>
    </a>
    <button class="icon-btn" id="themeToggle" aria-label="Toggle theme">
      <span aria-hidden="true">🌔</span>
    </button>
  </header>

  <main>
    <div class="search-bar">
      <form class="search-form" id="searchForm">
        <span>http://</span>
        <input 
          type="text" 
          id="searchInput" 
          placeholder="Search services..." 
          aria-label="Service search"
          autocomplete="off"
        >
        <span>.lan</span>
      </form>
      <div id="suggestions" class="suggestions" hidden></div>
    </div>

    <div class="grid">
      {''.join([
        f'''
        <div class="tile" tabindex="0" role="button" aria-label="{name} service"
             data-service="{name}" data-domain="{info['domain']}">
          <img src="/icons/{name}.png" alt="" onerror="this.replaceWith(document.createTextNode('{info['emoji']}'))">
          <div class="name">{name.capitalize()}</div>
          <div class="status-label">Checking...</div>
        </div>
        ''' for name, info in SERVICES.items()
      ])}
    </div>
  </main>

  <script>
    const SERVICES = {{
      {','.join([
        f'"{name}": {{"domain": "{info["domain"]}", "emoji": "{info["emoji"]}"}}' 
        for name, info in SERVICES.items()
      ])}
    }};

    const SEARCH_LINKS = [
      {{ name: "Jellyfin Search", match: ["jellyfin", "movies"], url: "http://jellyfin.lan/web/#/search.html" }},
      {{ name: "Kiwix – Wikipedia", match: ["wiki", "wikipedia"], url: "http://kiwix.lan/viewer#wikipedia_en_simple_all_2024-06/A/Main_Page" }},
      {{ name: "Kiwix – Wiktionary", match: ["dict", "wiktionary"], url: "http://kiwix.lan/viewer#wiktionary_en_all_maxi_2024-05/A/Wiktionary%3AMain_Page" }},
      {{ name: "Kiwix – Books", match: ["Book", "book"], url: "http://kiwix.lan/viewer#wikibooks_en_all_maxi_2021-03/A/Main_Page" }},
      {{ name: "Games – Games", match: ["Game", "game"], url: "http://games.lan/" }},
      {{ name: "Komga – Comics", match: ["Comics", "comics", "CH", "ch"], url: "http://games.lan/" }},
      {{ name: "Navidrome Search", match: ["music", "songs", "navidrome"], url: "http://navidrome.lan/app/#/search?q={{search}}" }}
    ];

    // DOM elements
    const searchInput = document.getElementById('searchInput');
    const suggestions = document.getElementById('suggestions');
    const tiles = document.querySelectorAll('.tile');
    const OFFLINE_THRESHOLD = 5;  // seconds to hide offline services
    
    // Track offline durations
    let offlineDurations = {{
      {','.join([f'"{name}": 0' for name in SERVICES])}
    }};

    // Keyboard navigation state
    let selectedSuggestionIndex = -1;

    // Initialize service tiles
    tiles.forEach(tile => {{
      const service = tile.dataset.service;
      tile.addEventListener('click', () => {{
        window.open(`http://${{SERVICES[service].domain}}`, '_blank');
      }});
      tile.addEventListener('keydown', (e) => {{
        if (e.key === 'Enter' || e.key === ' ') {{
          window.open(`http://${{SERVICES[service].domain}}`, '_blank');
        }}
      }});
    }});

    // Search functionality
    function updateSuggestions() {{
      const input = searchInput.value.trim().toLowerCase();
      suggestions.hidden = !input;
      
      if (!input) {{
        selectedSuggestionIndex = -1;
        return;
      }}
      
      const results = SEARCH_LINKS.filter(entry => 
        entry.match.some(keyword => keyword.toLowerCase().includes(input))
      );
      
      suggestions.innerHTML = results.length 
        ? results.map(entry => `
            <div tabindex="0" role="button" data-url="${{entry.url}}">
              ${{entry.name}}
            </div>
          `).join('')
        : '<div class="no-result">No matching services found</div>';
      
      // Reset selection
      selectedSuggestionIndex = -1;
      
      // Add click/keyboard handlers to suggestions
      suggestions.querySelectorAll('div').forEach((div, index) => {{
        div.addEventListener('click', () => openSuggestion(index));
        div.addEventListener('keydown', e => {{
          if (e.key === 'Enter') openSuggestion(index);
        }});
      }});
    }}

    function openSuggestion(index) {{
      const suggestionDivs = suggestions.querySelectorAll('div');
      if (index >= 0 && index < suggestionDivs.length) {{
        const url = suggestionDivs[index].dataset.url;
        if (url) {{
          window.open(
            url.replace('{{search}}', encodeURIComponent(searchInput.value.trim())),
            '_blank'
          );
          searchInput.value = '';
          suggestions.hidden = true;
        }}
      }}
    }}

    // Keyboard navigation for suggestions
    function handleSuggestionNavigation(e) {{
      const suggestionDivs = suggestions.querySelectorAll('div');
      if (!suggestionDivs.length) return;
      
      switch(e.key) {{
        case 'ArrowDown':
          e.preventDefault();
          selectedSuggestionIndex = 
            selectedSuggestionIndex >= suggestionDivs.length - 1 
              ? 0 
              : selectedSuggestionIndex + 1;
          break;
          
        case 'ArrowUp':
          e.preventDefault();
          selectedSuggestionIndex = 
            selectedSuggestionIndex <= 0 
              ? suggestionDivs.length - 1 
              : selectedSuggestionIndex - 1;
          break;
          
        case 'Enter':
          e.preventDefault();
          if (selectedSuggestionIndex !== -1) {{
            openSuggestion(selectedSuggestionIndex);
          }}
          return;  // Skip the highlight update
          
        case 'Escape':
          suggestions.hidden = true;
          return;
          
        default:
          return;  // Don't prevent default for other keys
      }}
      
      // Update highlight
      suggestionDivs.forEach((div, i) => {{
        div.classList.toggle('selected', i === selectedSuggestionIndex);
        if (i === selectedSuggestionIndex) {{
          div.scrollIntoView({{ block: 'nearest' }});
        }}
      }});
    }}

    // Theme toggle
    function initTheme() {{
      const themeToggle = document.getElementById('themeToggle');
      const savedTheme = localStorage.getItem('theme');
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      
      const currentTheme = savedTheme || (systemDark ? 'dark' : 'light');
      document.documentElement.setAttribute('data-theme', currentTheme);
      themeToggle.innerHTML = currentTheme === 'dark' ? '🌒' : '🌔';
      
      themeToggle.addEventListener('click', () => {{
        const html = document.documentElement;
        const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        themeToggle.innerHTML = newTheme === 'dark' ? '🌒' : '🌔';
      }});
    }}

    // Robust status polling with timeout
    function pollServiceStatus() {{
      // Create a timeout controller
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 4000);
      
      // Add cache busting parameter
      const cacheBuster = 't=' + new Date().getTime();
      
      fetch(`/api/status?${{cacheBuster}}`, {{
        signal: controller.signal
      }})
        .then(response => {{
          clearTimeout(timeout);
          if (!response.ok) throw new Error(`HTTP error! status: ${{response.status}}`);
          return response.json();
        }})
        .then(data => {{
          const status = data.status;
          offlineDurations = data.offline_durations;
          
          for (const name in SERVICES) {{
            const isOnline = status[name];
            const tile = document.querySelector(`.tile[data-service="${{name}}"]`);
            if (!tile) continue;
            
            const label = tile.querySelector('.status-label');
            label.textContent = isOnline ? 'ONLINE' : 'OFFLINE';
            label.className = `status-label ${{isOnline ? 'online' : 'offline'}}`;
            
            // Update ARIA status
            tile.setAttribute(
              'aria-label', 
              `${{name}} service - ${{isOnline ? 'online' : 'offline'}}`
            );
            
            // Hide if offline for more than threshold
            if (!isOnline && offlineDurations[name] > OFFLINE_THRESHOLD) {{
              tile.classList.add('hidden');
            }} else {{
              tile.classList.remove('hidden');
            }}
          }}
        }})
        .catch(err => {{
          clearTimeout(timeout);
          console.error('Status check failed:', err);
          
          // Show error state for all tiles
          document.querySelectorAll('.tile').forEach(tile => {{
            const label = tile.querySelector('.status-label');
            if (label.textContent === 'Checking...') {{
              label.textContent = 'ERROR';
              label.className = 'status-label offline';
            }}
          }});
        }});
    }}

    // Initialize
    document.addEventListener('DOMContentLoaded', () => {{
      initTheme();
      
      // Initial poll with retry mechanism
      function safePoll() {{
        try {{
          pollServiceStatus();
        }} catch (e) {{
          console.error('Polling error:', e);
        }}
      }}
      
      safePoll();
      setInterval(safePoll, 5000);
      
      searchInput.addEventListener('input', updateSuggestions);
      searchInput.addEventListener('keydown', handleSuggestionNavigation);
      
      document.addEventListener('click', (e) => {{
        if (!e.target.closest('.search-bar')) suggestions.hidden = true;
      }});
    }});
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    print(f"Serving status dashboard on http://0.0.0.0:{STATUS_SERVER_PORT}")
    app.run(host="0.0.0.0", port=STATUS_SERVER_PORT)
