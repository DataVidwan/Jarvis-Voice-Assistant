import os
import re
import urllib.request
import urllib.parse
import webbrowser
import pyautogui
from speak import speak
from voice import take_command

def play_music(command):
    """
    Parses the command to identify the song and platform, then plays it.
    Supported inputs: "play lofi", "play lofi on youtube", "play shape of you on spotify", "play music"
    """
    command = command.lower().strip()
    
    # Check if user just said "play music" without specifying a song
    if command == "play music" or command == "play some music" or command == "play music player":
        speak("What song or artist would you like to play?")
        song_name = take_command()
        if not song_name:
            speak("I didn't catch that. Music playback cancelled.")
            return
            
        speak("Would you like to play it on Spotify or YouTube?")
        platform = take_command()
        if "spotify" in platform:
            preferred_platform = "spotify"
        else:
            preferred_platform = "youtube"
    else:
        # Extract song name and platform from command
        # e.g., "play bohemian rhapsody on youtube"
        # strip "play" prefix
        search_term = command
        if search_term.startswith("play "):
            search_term = search_term.replace("play ", "", 1).strip()
            
        preferred_platform = "youtube" # Default platform
        
        if " on spotify" in search_term:
            preferred_platform = "spotify"
            song_name = search_term.replace(" on spotify", "").strip()
        elif " on youtube" in search_term:
            preferred_platform = "youtube"
            song_name = search_term.replace(" on youtube", "").strip()
        else:
            song_name = search_term.strip()
            
    if not song_name:
        speak("I couldn't identify the song name.")
        return

    if preferred_platform == "youtube":
        play_on_youtube(song_name)
    else:
        play_on_spotify(song_name)

def play_on_youtube(song_name):
    speak(f"Playing {song_name} on YouTube.")
    try:
        query = urllib.parse.quote(song_name)
        url = f"https://www.youtube.com/results?search_query={query}"
        
        # Make a request with User-Agent to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8', errors='ignore')
        
        # Regex to find video links: watch?v=...
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        if video_ids:
            # We open the first video directly to autostart playing it!
            play_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            print(f"Auto-playing YouTube URL: {play_url}")
            webbrowser.open(play_url)
        else:
            # Fallback to search results page if scraping failed
            print("No video IDs found, opening search results page.")
            webbrowser.open(url)
    except Exception as e:
        print("YouTube Search Error:", e)
        # Simple browser fallback
        webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(song_name)}")

def play_on_spotify(song_name):
    speak(f"Searching for {song_name} on Spotify.")
    query = urllib.parse.quote(song_name)
    
    # Try Spotify URI first (opens desktop app search if installed)
    try:
        spotify_uri = f"spotify:search:{query}"
        print(f"Opening Spotify URI: {spotify_uri}")
        os.startfile(spotify_uri)
    except Exception as e:
        print("Spotify URI launch failed, falling back to web browser:", e)
        # Fallback to web search
        webbrowser.open(f"https://open.spotify.com/search/{query}")

def next_song():
    speak("Skipping to the next track.")
    pyautogui.press('nexttrack')
