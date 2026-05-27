import os
import datetime
import subprocess
from speak import speak
from voice import take_command

NOTES_FILE = "notes.txt"

def take_note():
    speak("What would you like me to write down?")
    
    note_content = take_command()
    if not note_content:
        speak("I didn't hear anything. Note taking cancelled.")
        return
        
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_note = f"[{timestamp}] {note_content}\n"
    
    try:
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(formatted_note)
        speak("I've saved that note.")
        
        # Interactive followup
        speak("Would you like me to open your notes file?")
        response = take_command()
        if any(word in response for word in ["yes", "yeah", "sure", "ok", "open"]):
            speak("Opening notes file.")
            os.startfile(NOTES_FILE)
    except Exception as e:
        print("Notes Error:", e)
        speak("I ran into an error trying to save your note.")

def show_notes():
    if not os.path.exists(NOTES_FILE) or os.path.getsize(NOTES_FILE) == 0:
        speak("You don't have any notes saved yet.")
        return
        
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        if not lines:
            speak("Your notes file is empty.")
            return
            
        speak(f"You have {len(lines)} notes.")
        
        # Read the last 3 notes for brevity
        recent_count = min(3, len(lines))
        speak(f"Here are the {recent_count} most recent notes.")
        for line in lines[-recent_count:]:
            # Clean up the timestamp for reading (e.g. "[2026-05-27 11:15:30] note text")
            clean_line = line
            if line.startswith("[") and "]" in line:
                clean_line = line.split("]", 1)[1].strip()
            speak(clean_line)
            
        # Open notes file automatically so they can see all of them
        speak("Opening your notes file so you can see all of them.")
        os.startfile(NOTES_FILE)
    except Exception as e:
        print("Show Notes Error:", e)
        speak("I couldn't open or read your notes file.")
