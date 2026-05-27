import datetime
import re
import os
import random
import ctypes

from speak import speak
from screenshot import take_screenshot
from app_control import open_app, close_app
from website_control import open_website, close_website
from alarm_manager import parse_alarm_reminder, add_alarm, list_active_items, clear_all_items
from voice import take_command

def confirm_action(action_name):
    """Asks the user for verbal confirmation before performing critical/system actions."""
    phrases = [
        f"Are you sure you want to {action_name}?",
        f"Do you really want me to {action_name}?",
        f"Confirming: should I proceed to {action_name}?",
        f"Please confirm: do you want to {action_name}?"
    ]
    speak(random.choice(phrases))
    speak("Please say yes or no.")
    
    response = take_command().lower().strip()
    print(f"Confirmation response: {response}")
    if any(word in response for word in ["yes", "yeah", "sure", "ok", "do it", "confirm", "yep"]):
        return True
    
    speak(f"Action cancelled. I will not {action_name}.")
    return False

# Popular websites to help differentiate websites from applications
COMMON_WEBSITES = [
    "google", "youtube", "github", "facebook", "wikipedia", 
    "amazon", "reddit", "twitter", "instagram", "linkedin", 
    "netflix", "stackoverflow", "gmail", "outlook", "chatgpt"
]

def process_command(command):
    command = command.lower().strip()
    
    # ------------------------
    # SYSTEM CONTROLS (WITH CONFIRMATION)
    # ------------------------
    if "shutdown pc" in command or "shut down pc" in command or "shutdown computer" in command:
        if confirm_action("shutdown the computer"):
            speak("Shutting down the system. Goodbye, Boss.")
            os.system("shutdown /s /t 5")
        return

    if "restart pc" in command or "restart computer" in command:
        if confirm_action("restart the computer"):
            speak("Initiating system restart now.")
            os.system("shutdown /r /t 5")
        return

    if "sleep mode" in command or "put pc to sleep" in command or "put computer to sleep" in command or "go to sleep" in command:
        if confirm_action("put the computer to sleep"):
            speak("Entering sleep mode. See you later, Boss.")
            try:
                ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            except Exception as e:
                print("Sleep Error:", e)
                speak("I was unable to trigger sleep mode.")
        return

    if "volume up" in command or "increase volume" in command:
        if confirm_action("increase the system volume"):
            speak("Raising the volume.")
            import pyautogui
            for _ in range(5):
                pyautogui.press('volumeup')
        return

    if "volume down" in command or "decrease volume" in command:
        if confirm_action("decrease the system volume"):
            speak("Lowering the volume.")
            import pyautogui
            for _ in range(5):
                pyautogui.press('volumedown')
        return

    if "mute system" in command or "mute volume" in command or "unmute system" in command or "mute" in command:
        if confirm_action("toggle the volume mute status"):
            speak("Toggling mute.")
            import pyautogui
            pyautogui.press('volumemute')
        return

    # ------------------------
    # NOTES SYSTEM
    # ------------------------
    if "take note" in command or "take a note" in command or "write note" in command:
        from notes_control import take_note
        take_note()
        return

    if "show note" in command or "show notes" in command or "read notes" in command or "open notes" in command or "view notes" in command:
        from notes_control import show_notes
        show_notes()
        return

    # ------------------------
    # MUSIC PLAYER
    # ------------------------
    if "next song" in command or "next track" in command or "skip song" in command or "skip track" in command:
        from music_control import next_song
        next_song()
        return

    if command.startswith("play ") or "play music" in command:
        from music_control import play_music
        play_music(command)
        return

    # ------------------------
    # ALARMS & REMINDERS
    # ------------------------
    if "list alarm" in command or "show alarm" in command or "list reminder" in command or "show reminder" in command:
        list_active_items()
        return
        
    if "clear alarm" in command or "clear reminder" in command or "delete alarm" in command or "delete reminder" in command:
        clear_all_items()
        return

    parsed = parse_alarm_reminder(command)
    if parsed:
        alarm_type, target_time, message = parsed
        add_alarm(alarm_type, target_time, message)
        return

    # ------------------------
    # OPEN APPLICATIONS / WEBSITES
    # ------------------------
    if command.startswith("open ") or command.startswith("go to "):
        target = command.replace("open ", "", 1).replace("go to ", "", 1).strip()
        
        is_website = False
        if "." in target or target.startswith("http"):
            is_website = True
        elif target in COMMON_WEBSITES or "website" in command:
            is_website = True
            
        clean_target = target.replace("website", "").strip()
        
        if is_website:
            open_website(clean_target)
        else:
            from app_control import find_app_path
            app_path = find_app_path(clean_target)
            if app_path:
                open_app(clean_target)
            else:
                open_website(clean_target)
        return

    # ------------------------
    # CLOSE APPLICATIONS / WEBSITES
    # ------------------------
    if command.startswith("close "):
        target = command.replace("close ", "", 1).strip()
        
        is_website = False
        if "." in target or target in COMMON_WEBSITES or "website" in command:
            is_website = True
            
        clean_target = target.replace("website", "").strip()
        
        if is_website:
            close_website(clean_target)
        else:
            from app_control import close_app
            close_app(clean_target)
        return

    # ------------------------
    # SCREENSHOT
    # ------------------------
    if "take screenshot" in command or "take a screenshot" in command or "capture screen" in command:
        take_screenshot()
        return

    # ------------------------
    # TIME & DATE
    # ------------------------
    if "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
        return

    if "date" in command:
        today = datetime.datetime.now().strftime("%d %B %Y")
        speak(f"Today's date is {today}")
        return

    # ------------------------
    # BASIC CONVERSATION & INTERACTIVITY
    # ------------------------
    if "hello" in command or "hi jarvis" in command or "hey jarvis" in command:
        greetings = [
            "Hello, Boss! How can I help you today?",
            "Hi there! Ready for your commands.",
            "Hello! How is your day going? What can I do for you?",
            "Hey! At your service. What's on your mind?"
        ]
        speak(random.choice(greetings))
        return

    if "how are you" in command:
        status_phrases = [
            "I am doing great, thank you! I'm fully online and ready to assist.",
            "I'm functioning perfectly, Boss. Ready to get some work done!",
            "All systems are green. I'm feeling excellent. How are you doing today?",
            "I'm fine and happy to help you. What can I do for you?"
        ]
        speak(random.choice(status_phrases))
        return

    if "your name" in command or "who are you" in command:
        speak("I am Jarvis, your digital voice assistant. I am here to help manage your PC, play music, take notes, and make life easier.")
        return

    if "thank you" in command or "thanks" in command:
        thanks_phrases = [
            "You're very welcome, Boss!",
            "Anytime! I'm always here to help.",
            "Happy to assist you. Let me know if you need anything else.",
            "It is my absolute pleasure!"
        ]
        speak(random.choice(thanks_phrases))
        return

    if "what can you do" in command or "help" in command or "what are your features" in command:
        speak("I can help you with a variety of tasks! Here are some things you can ask me to do:")
        speak("You can open applications or websites by saying: Open Notepad, or: Open Wikipedia.")
        speak("You can close them by saying: Close Notepad, or: Close Wikipedia.")
        speak("I can manage notes for you. Try saying: Take note, or: Show notes.")
        speak("I can play music for you. Try saying: Play lofi music on YouTube, or: Play Shape of You on Spotify, or simply skip tracks with: Next song.")
        speak("I can control system settings. Try saying: Mute system, Volume up, Sleep mode, or Shutdown PC. I will always ask for confirmation first.")
        speak("I can also set alarms, take screenshots, check the time, or just chat. What can I do for you right now?")
        return

    # ------------------------
    # UNKNOWN COMMAND
    # ------------------------
    speak("Sorry, I did not understand that command. You can say 'help' to hear what I can do.")