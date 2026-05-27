import re
import datetime
import threading
import time
import winsound
from speak import speak

# Global list of alarms and reminders
# Format: {'type': 'alarm'/'reminder', 'time': datetime, 'message': str, 'triggered': bool}
alarms = []
alarms_lock = threading.Lock()

def parse_absolute_time(time_str):
    time_str = time_str.lower().strip()
    match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str)
    if not match:
        return None
        
    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    meridiem = match.group(3)
    
    if meridiem:
        if meridiem == 'pm' and hour < 12:
            hour += 12
        elif meridiem == 'am' and hour == 12:
            hour = 0
            
    now = datetime.datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Smart fallback for 12-hour format if meridiem is not specified
    if not meridiem and hour < 12 and target_time < now:
        alternative_time = target_time + datetime.timedelta(hours=12)
        if alternative_time > now:
            target_time = alternative_time
            
    if target_time < now:
        target_time += datetime.timedelta(days=1)
        
    return target_time

def parse_alarm_reminder(command):
    """
    Parses a command for alarm or reminder scheduling.
    Returns a tuple (type, target_time, message) or None.
    """
    command = command.lower().strip()
    
    # 1. Reminders
    # "remind me to [message] in [X] [minutes]"
    # "remind me to [message] at [time]"
    reminder_match = re.search(r'(?:remind me to|set a reminder to|reminder to)\s+(.+)', command)
    if reminder_match:
        content = reminder_match.group(1).strip()
        
        # Check relative: "in 10 minutes"
        rel_match = re.search(r'\s+in\s+(\d+)\s+(second|seconds|minute|minutes|hour|hours|min|mins|hr|hrs|sec|secs)', content)
        if rel_match:
            message = content[:rel_match.start()].strip()
            amount = int(rel_match.group(1))
            unit = rel_match.group(2)
            
            delta = datetime.timedelta()
            if 'min' in unit:
                delta = datetime.timedelta(minutes=amount)
            elif 'hour' in unit or 'hr' in unit:
                delta = datetime.timedelta(hours=amount)
            elif 'sec' in unit:
                delta = datetime.timedelta(seconds=amount)
                
            trigger_time = datetime.datetime.now() + delta
            return ('reminder', trigger_time, message)
            
        # Check absolute: "at 5:30 pm"
        abs_match = re.search(r'\s+at\s+(.+)', content)
        if abs_match:
            message = content[:abs_match.start()].strip()
            time_str = abs_match.group(1).strip()
            trigger_time = parse_absolute_time(time_str)
            if trigger_time:
                return ('reminder', trigger_time, message)

    # 2. Alarms
    # "set alarm for 6:30 pm"
    # "set alarm at 6:30 pm"
    # "set alarm in 10 minutes"
    alarm_match = re.search(r'(?:set\s+)?(?:an\s+)?alarm\s+(?:for|at|in)?\s*(.+)', command)
    if alarm_match:
        time_str = alarm_match.group(1).strip()
        
        # Check if relative inside alarm
        rel_match = re.search(r'^(\d+)\s+(second|seconds|minute|minutes|hour|hours|min|mins|hr|hrs|sec|secs)', time_str)
        if rel_match:
            amount = int(rel_match.group(1))
            unit = rel_match.group(2)
            delta = datetime.timedelta()
            if 'min' in unit:
                delta = datetime.timedelta(minutes=amount)
            elif 'hour' in unit or 'hr' in unit:
                delta = datetime.timedelta(hours=amount)
            elif 'sec' in unit:
                delta = datetime.timedelta(seconds=amount)
            trigger_time = datetime.datetime.now() + delta
            return ('alarm', trigger_time, 'Alarm')
            
        trigger_time = parse_absolute_time(time_str)
        if trigger_time:
            return ('alarm', trigger_time, 'Alarm')
            
    return None

def add_alarm(alarm_type, target_time, message):
    with alarms_lock:
        alarms.append({
            'type': alarm_type,
            'time': target_time,
            'message': message,
            'triggered': False
        })
    time_str = target_time.strftime("%I:%M %p")
    if alarm_type == 'alarm':
        speak(f"Alarm set for {time_str}.")
    else:
        speak(f"Reminder set for {time_str} to: {message}.")

def check_and_trigger_alarms():
    global alarms
    now = datetime.datetime.now()
    to_trigger = []
    
    with alarms_lock:
        # Keep non-triggered or future alarms
        new_alarms = []
        for item in alarms:
            if not item['triggered'] and now >= item['time']:
                item['triggered'] = True
                to_trigger.append(item)
            else:
                new_alarms.append(item)
        alarms = new_alarms
        
    for item in to_trigger:
        # Play beep in a separate thread so it doesn't block speech
        threading.Thread(target=play_alarm_sound, daemon=True).start()
        # Speak the reminder/alarm
        if item['type'] == 'alarm':
            speak("Alarm is ringing! It is time!")
        else:
            speak(f"Reminder alert: {item['message']}")

def play_alarm_sound():
    for _ in range(3):
        try:
            winsound.Beep(1000, 600)  # 1000 Hz for 600 ms
        except Exception:
            pass
        time.sleep(0.1)

def list_active_items():
    with alarms_lock:
        if not alarms:
            speak("There are no active alarms or reminders.")
            return
            
        speak("Here are your active items:")
        for idx, item in enumerate(alarms, 1):
            time_str = item['time'].strftime("%I:%M %p")
            if item['type'] == 'alarm':
                speak(f"Alarm number {idx} at {time_str}.")
            else:
                speak(f"Reminder number {idx} at {time_str} to {item['message']}.")

def clear_all_items():
    with alarms_lock:
        count = len(alarms)
        alarms.clear()
        speak(f"Cleared all {count} active alarms and reminders.")
