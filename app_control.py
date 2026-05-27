import os
import subprocess
import psutil
import win32gui
import win32process
import win32con
from speak import speak

# Cache of shortcuts
_shortcuts_cache = None

def get_all_shortcuts():
    """Scans Windows Start Menu and Desktop locations for app shortcuts."""
    global _shortcuts_cache
    if _shortcuts_cache is not None:
        return _shortcuts_cache
        
    shortcuts = {}
    user_profile = os.path.expanduser("~")
    search_paths = [
        os.path.join(user_profile, "Desktop"),
        r"C:\Users\Public\Desktop",
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.join(user_profile, r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs")
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(".lnk"):
                        name = os.path.splitext(file)[0].lower()
                        full_path = os.path.join(root, file)
                        # We don't overwrite user shortcuts with system shortcuts
                        if name not in shortcuts:
                            shortcuts[name] = full_path
    _shortcuts_cache = shortcuts
    return shortcuts

def find_app_path(app_name):
    """
    Finds the path to the application shortcut or executable.
    Supports basic system app names directly.
    """
    system_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "command prompt": "cmd.exe",
        "cmd": "cmd.exe",
        "paint": "mspaint.exe",
        "mspaint": "mspaint.exe",
        "task manager": "taskmgr.exe",
        "file explorer": "explorer.exe",
        "explorer": "explorer.exe"
    }
    
    app_name_lower = app_name.lower().strip()
    if app_name_lower in system_apps:
        return system_apps[app_name_lower]
        
    shortcuts = get_all_shortcuts()
    
    # 1. Exact match
    if app_name_lower in shortcuts:
        return shortcuts[app_name_lower]
        
    # 2. Key phrase match (e.g. "chrome" matches "google chrome")
    for name, path in shortcuts.items():
        if app_name_lower in name:
            return path
            
    # 3. Word-by-word match
    words = app_name_lower.split()
    for name, path in shortcuts.items():
        if all(word in name for word in words):
            return path
            
    return None

def open_app(app_name):
    """Attempts to find and open the specified application."""
    app_path = find_app_path(app_name)
    if app_path:
        speak(f"Opening {app_name}")
        try:
            os.startfile(app_path)
        except Exception as e:
            print(f"Error starting {app_name}: {e}")
            speak(f"Failed to launch {app_name}.")
    else:
        speak(f"Sorry, I could not find {app_name} on your system.")

def close_app(app_name):
    """Attempts to find and close a single window of the specified application. Falls back to terminating processes."""
    app_name_lower = app_name.lower().strip()
    
    # Map common application names to executable names
    process_map = {
        "chrome": ["chrome.exe"],
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe", "calculatorapp.exe", "calculator.exe"],
        "word": ["winword.exe"],
        "excel": ["excel.exe"],
        "powerpoint": ["powerpnt.exe"],
        "edge": ["msedge.exe"],
        "firefox": ["firefox.exe"],
        "spotify": ["spotify.exe"],
        "discord": ["discord.exe"],
        "teams": ["teams.exe", "ms-teams.exe"],
        "skype": ["skype.exe"],
        "zoom": ["zoom.exe"]
    }
    
    target_names = process_map.get(app_name_lower, [app_name_lower + ".exe", app_name_lower])
    closed = False
    
    def win_enum_handler(hwnd, ctx):
        nonlocal closed
        if closed:
            return False
            
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd).lower()
            
            # Check title match
            title_match = (app_name_lower in title)
            
            # Check process name match
            proc_match = False
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc = psutil.Process(pid)
                proc_name = proc.name().lower()
                if any(t in proc_name for t in target_names) or app_name_lower in proc_name:
                    proc_match = True
            except Exception:
                pass
                
            if title_match or proc_match:
                print(f"Closing window: {win32gui.GetWindowText(hwnd)}")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                closed = True
                return False # Stop enum
        return True
        
    try:
        # First check the foreground window
        fg_hwnd = win32gui.GetForegroundWindow()
        if fg_hwnd:
            win_enum_handler(fg_hwnd, None)
            
        if not closed:
            win32gui.EnumWindows(win_enum_handler, None)
    except Exception as e:
        print("Error during window enumeration:", e)
        
    if closed:
        speak(f"Closed {app_name}.")
        return

    # Fallback to terminating processes
    killed = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            if any(t in proc_name for t in target_names) or app_name_lower in proc_name:
                proc.terminate()
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    if killed:
        speak(f"Terminated background processes for {app_name}.")
    else:
        speak(f"Could not find any running processes or windows for {app_name}.")