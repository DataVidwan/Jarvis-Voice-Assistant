import speech_recognition as sr

recognizer = sr.Recognizer()
microphone = None

def init_voice():
    """Initializes the microphone and calibrates for ambient noise once at startup."""
    global microphone
    print("Initializing microphone...")
    microphone = sr.Microphone()
    with microphone as source:
        print("Calibrating microphone for ambient noise (1 second)...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Microphone calibration complete.")

def take_command():
    """Listens for a voice command. Uses a short timeout to keep the loop responsive."""
    global microphone
    if microphone is None:
        init_voice()
        
    try:
        with microphone as source:
            print("Listening...")
            # timeout=2: waits 2s for speech to begin
            # phrase_time_limit=8: limits command length to 8s
            audio = recognizer.listen(source, timeout=2, phrase_time_limit=8)
            print("Recognizing...")
            command = recognizer.recognize_google(audio)
            command = command.lower()
            return command
    except sr.WaitTimeoutError:
        # Expected when the user does not speak during the listening window
        return ""
    except Exception as e:
        # Return empty string for errors/silence to keep the loop going
        return ""