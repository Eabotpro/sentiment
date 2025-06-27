# At the top of the file
import os
from threading import Lock

# Replace hardcoded credentials with environment variables
EMAIL = os.getenv('MYFXBOOK_EMAIL')
PASSWORD = os.getenv('MYFXBOOK_PASSWORD')

# Add a lock for thread safety
sentiment_lock = Lock()

# In login_myfxbook()
def login_myfxbook():
    global session_id
    try:
        r = requests.post("https://www.myfxbook.com/api/login.json", data={
            "email": EMAIL,
            "password": PASSWORD
        })
        r.raise_for_status()  # Raises exception for HTTP errors
        if r.json().get("error"):
            print("❌ Login failed:", r.json().get("message"))
            return False
        session_id = r.json().get("session")
        print("✅ Logged in! Session ID:", session_id)
        return True
    except Exception as e:
        print("💥 Login error:", e)
        return False

# In update_sentiment() when updating cached_sentiment
with sentiment_lock:
    cached_sentiment["long"] = sym["longPercentage"]
    cached_sentiment["short"] = sym["shortPercentage"]
