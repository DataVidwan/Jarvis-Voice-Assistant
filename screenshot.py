import os
import datetime
import pyautogui
from speak import speak

def take_screenshot():
    # Find the user's Desktop folder
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desktop_path):
        os.makedirs(desktop_path)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(desktop_path, filename)
    
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        speak(f"Screenshot saved to Desktop as {filename}")
    except Exception as e:
        print("Screenshot Error:", e)
        speak("Failed to capture screenshot.")