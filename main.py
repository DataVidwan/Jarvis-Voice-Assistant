import random
from voice import take_command, init_voice
from speak import speak
from commands import process_command
from alarm_manager import check_and_trigger_alarms

WAKE_WORDS = ["hey jarvis", "hello jarvis", "hi jarvis", "jarvis"]

def main():
    print("Starting Jarvis...")
    speak("Jarvis is starting up.")
    
    # Calibrate microphone once at startup
    init_voice()
    speak("Jarvis is now online.")
    
    print("Main loop started. Say 'exit', 'stop', or 'bye' to quit.")
    print("Wake words: 'Jarvis', 'Hey Jarvis', 'hello jarvis', 'hi Jarvis'")
    
    active_session = False

    while True:
        # Check and trigger any pending alarms or reminders
        check_and_trigger_alarms()
        
        # Listen for a command (non-blocking, returns empty string on timeout)
        speech_input = take_command()
        
        if speech_input:
            print(f"Captured speech: {speech_input}")
            
            if "exit" in speech_input or "stop" in speech_input or "bye" in speech_input:
                speak("Goodbye, Boss.")
                break
                
            # Check if any wake word was spoken
            wake_word_detected = False
            matched_wake_word = ""
            for word in WAKE_WORDS:
                if word in speech_input:
                    wake_word_detected = True
                    matched_wake_word = word
                    break
                    
            if wake_word_detected:
                # Extract command content after/around the wake word
                command_content = speech_input.replace(matched_wake_word, "", 1).strip()
                # Clean up punctuation like commas (e.g. "Jarvis, open notepad")
                command_content = command_content.lstrip(",.?! ").strip()
                
                if command_content:
                    # User spoke the wake word and a command together
                    process_command(command_content)
                else:
                    # User only spoke the wake word, start an active session
                    greetings = [
                        "Yes, Boss?",
                        "At your service. What can I do for you?",
                        "I'm listening, Boss.",
                        "Yes? How can I help you today?"
                    ]
                    speak(random.choice(greetings))
                    active_session = True
            elif active_session:
                # In active session, process direct input as command
                process_command(speech_input)
                active_session = False
            else:
                # No wake word detected, and assistant is idle
                print("Idle. Ignoring speech (no wake word detected).")
        else:
            # If nothing was heard and we were waiting for a follow-up command, return to sleep
            if active_session:
                active_session = False
                print("Active session timed out. Returning to idle state.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
        input("Press Enter to close...")