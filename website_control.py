import webbrowser
import win32gui
import win32con
import urllib.request
import urllib.parse
import json
import re
from speak import speak

def get_real_website_url(site_name):
    """Resolves arbitrary site name queries to their official URLs using multiple fallbacks."""
    site_name = site_name.strip()
    
    # If the site name already looks like a domain or URL, use it directly
    if "." in site_name or site_name.startswith("http"):
        return site_name if site_name.startswith("http") else "https://" + site_name
        
    # Dictionary of known websites with specific domains
    site_map = {
        "wikipedia": "https://www.wikipedia.org",
        "github": "https://github.com",
        "stackoverflow": "https://stackoverflow.com",
        "reddit": "https://www.reddit.com",
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "outlook": "https://outlook.live.com",
        "chatgpt": "https://chatgpt.com",
        "spotify": "https://open.spotify.com"
    }
    
    name_lower = site_name.lower().strip()
    if name_lower in site_map:
        return site_map[name_lower]
        
    # 1. Try DDG Instant Answer JSON API
    try:
        api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(site_name)}&format=json&no_html=1"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=3)
        data = json.loads(res.read().decode('utf-8'))
        
        results = data.get('Results', [])
        if results and results[0].get('FirstURL'):
            url = results[0]['FirstURL']
            print(f"DDG API Success for '{site_name}': {url}")
            return url
    except Exception as e:
        print("DDG API error:", e)
        
    # 2. Try Yahoo Search redirect scraping (No captchas, embeds target URLs)
    try:
        print(f"Resolving '{site_name}' official URL via Yahoo Search...")
        query = urllib.parse.quote(site_name + " official website")
        yahoo_url = f"https://search.yahoo.com/search?p={query}"
        req = urllib.request.Request(yahoo_url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=4).read().decode('utf-8', errors='ignore')
        
        ru_matches = re.findall(r'RU=(https?%3[aA]%2[fF][a-zA-Z0-9\-\.\/\?\&\=\%\_\+]+)', html)
        for match in ru_matches:
            decoded_url = urllib.parse.unquote(match)
            if "yahoo.com" not in decoded_url and "yahoo.co" not in decoded_url and "yimg.com" not in decoded_url:
                if "/RK=" in decoded_url:
                    decoded_url = decoded_url.split("/RK=")[0]
                # Clean trailing double slashes
                if decoded_url.endswith("//"):
                    decoded_url = decoded_url[:-1]
                print(f"Yahoo Search Success for '{site_name}': {decoded_url}")
                return decoded_url
    except Exception as e:
        print("Yahoo Search error:", e)
        
    # Default fallback
    return f"https://www.{site_name}.com"

def open_website(site_name):
    """Opens a website in the default browser based on its resolved domain."""
    url = get_real_website_url(site_name)
    speak(f"Opening website {site_name}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Error opening website {url}: {e}")
        speak(f"Failed to open website {site_name}.")

def close_website(site_name):
    """Attempts to find and close a single browser window matching the site name."""
    site_name_lower = site_name.lower().strip()
    closed = False
    
    # Common browser window title suffix keywords
    browsers = ["chrome", "firefox", "edge", "opera", "brave", "explorer"]
    
    def win_enum_handler(hwnd, ctx):
        nonlocal closed
        if closed:
            return False
            
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd).lower()
            # Match if the site name is in the window title, and it is a browser
            if site_name_lower in title and any(browser in title for browser in browsers):
                print(f"Closing website window: {win32gui.GetWindowText(hwnd)}")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                closed = True
                return False # Stop enumeration
        return True
                
    try:
        # First check the foreground window
        fg_hwnd = win32gui.GetForegroundWindow()
        if fg_hwnd:
            win_enum_handler(fg_hwnd, None)
            
        if not closed:
            win32gui.EnumWindows(win_enum_handler, None)
    except Exception as e:
        print("Error enumerating windows:", e)
        
    if closed:
        speak(f"Closed website window for {site_name}")
        return
        
    # Fallback: search for any visible window containing the site name, browser or not
    def fallback_enum_handler(hwnd, ctx):
        nonlocal closed
        if closed:
            return False
            
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd).lower()
            if site_name_lower in title:
                print(f"Closing window (fallback): {win32gui.GetWindowText(hwnd)}")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                closed = True
                return False # Stop enumeration
        return True
        
    try:
        if not closed:
            win32gui.EnumWindows(fallback_enum_handler, None)
    except Exception:
        pass
        
    if closed:
        speak(f"Closed window matching {site_name}")
    else:
        speak(f"Could not find any open website window for {site_name}")