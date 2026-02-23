import os
import shutil
from datetime import datetime, timedelta

def setup_folder(folder_name):
    """Creates a folder if it doesn't exist. Overwrites if it does."""
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)

def save_content(folder_name, subject, sender, date_str, body_text):
    """Saves email content to content.txt in the specified folder."""
    file_path = os.path.join(folder_name, "content.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"Subject: {subject}\n")
        f.write(f"Sender: {sender}\n")
        f.write(f"Date: {date_str}\n")
        f.write("\nBody:\n")
        f.write(body_text)

def is_within_24_hours(date_str):
    """
    Checks if a date string is within the last 24 hours.
    Gmail date formats in 'title' attribute: "Sat, 21 Feb 2026, 21:38"
    Relative formats: "2:15 PM", "Yesterday"
    """
    now = datetime.now()
    
    # Clean string
    date_str = date_str.strip()
    
    # 1. Handle common relative strings
    if "PM" in date_str.upper() or "AM" in date_str.upper():
        # If it only contains time, it's today
        if "," not in date_str and ":" in date_str:
            return True
        
    if "Yesterday" in date_str:
        return True
    
    # 2. Try parsing the full format seen in the logs: "Sat, 21 Feb 2026, 21:38"
    # Format: %a, %d %b %Y, %H:%M
    fmts = [
        "%a, %d %b %Y, %H:%M",   # Sat, 21 Feb 2026, 21:38
        "%a, %b %d, %Y, %I:%M %p", # Sat, Feb 21, 2026, 9:38 PM
        "%b %d",                   # Feb 21
        "%m/%d/%y",                # 02/21/26
        "%Y-%m-%dT%H:%M:%S%z"      # ISO format occasionally
    ]
    
    for fmt in fmts:
        try:
            dt = datetime.strptime(date_str, fmt)
            # Handle cases where year is missing (e.g., "Feb 21")
            if dt.year == 1900:
                dt = dt.replace(year=now.year)
            
            # Check if within 24 hours
            # Use absolute difference to handle slight clock skews
            if abs((now - dt).total_seconds()) <= 24 * 3600:
                return True
        except ValueError:
            continue
            
    # Final fallback for simple time strings like "21:38" 
    if ":" in date_str and len(date_str) <= 5:
        return True

    return False
