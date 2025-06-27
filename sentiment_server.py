from flask import Flask, jsonify
import requests
import threading
import time
import os
from threading import Lock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
SESSION_REFRESH_INTERVAL = 1800  # 30 minutes
SENTIMENT_UPDATE_INTERVAL = 300  # 5 minutes
MAX_LOGIN_ATTEMPTS = 3

# Thread-safe storage
sentiment_lock = Lock()
cached_sentiment = {
    "symbol": "XAUUSD",
    "long": 0.0,
    "short": 0.0,
    "last_updated": None,
    "error": None
}
session_id = None
running = True

def login_myfxbook():
    global session_id
    attempts = 0
    
    while attempts < MAX_LOGIN_ATTEMPTS:
        try:
            response = requests.post(
                "https://www.myfxbook.com/api/login.json",
                data={
                    "email": os.getenv('MYFXBOOK_EMAIL'),
                    "password": os.getenv('MYFXBOOK_PASSWORD')
                },
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("error"):
                print(f"❌ Login failed (attempt {attempts + 1}):", data.get("message"))
                attempts += 1
                time.sleep(5)
                continue
                
            session_id = data.get("session")
            print("✅ Login successful")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"💥 Network error during login (attempt {attempts + 1}):", str(e))
            attempts += 1
            time.sleep(10)
    
    print("❌ Max login attempts reached")
    return False

def update_sentiment():
    global cached_sentiment, session_id, running
    last_session_refresh = 0
    
    while running:
        try:
            current_time = time.time()
            
            # Refresh session if needed
            if session_id is None or (current_time - last_session_refresh) > SESSION_REFRESH_INTERVAL:
                if not login_myfxbook():
                    time.sleep(SENTIMENT_UPDATE_INTERVAL)
                    continue
                last_session_refresh = current_time
            
            # Fetch sentiment data
            print("📡 Fetching sentiment data...")
            response = requests.get(
                "https://www.myfxbook.com/api/get-community-outlook.json",
                params={"session": session_id},
                timeout=10
            )
            response.raise_for_status()
            
            outlook = response.json()
            found = False
            
            for sym in outlook.get("symbols", []):
                if sym["symbol"].lower() == "xauusd":
                    with sentiment_lock:
                        cached_sentiment = {
                            "symbol": "XAUUSD",
                            "long": float(sym["longPercentage"]),
                            "short": float(sym["shortPercentage"]),
                            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "error": None
                        }
                    print(f"✅ Updated XAUUSD Sentiment: Long {sym['longPercentage']}% | Short {sym['shortPercentage']}%")
                    found = True
                    break
            
            if not found:
                with sentiment_lock:
                    cached_sentiment["error"] = "Symbol not found in Myfxbook data"
                print("❗ XAUUSD symbol not found in response")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            with sentiment_lock:
                cached_sentiment["error"] = error_msg
            print(f"💥 {error_msg}")
            session_id = None  # Force re-login on next attempt
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            with sentiment_lock:
                cached_sentiment["error"] = error_msg
            print(f"💥 {error_msg}")
            
        time.sleep(SENTIMENT_UPDATE_INTERVAL)

@app.route('/sentiment/XAUUSD')
def get_sentiment():
    with sentiment_lock:
        return jsonify(cached_sentiment)

@app.route('/health')
def health_check():
    with sentiment_lock:
        is_healthy = cached_sentiment['error'] is None and cached_sentiment['last_updated'] is not None
        status = {
            "status": "healthy" if is_healthy else "unhealthy",
            "last_updated": cached_sentiment['last_updated'],
            "error": cached_sentiment['error']
        }
        return jsonify(status), 200 if is_healthy else 503

def shutdown_handler():
    global running
    running = False
    print("🛑 Shutting down background threads...")

if __name__ == '__main__':
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write('MYFXBOOK_EMAIL=your_email@example.com\n')
            f.write('MYFXBOOK_PASSWORD=your_password\n')
        print("⚠️ Created .env file. Please update with your credentials.")
        exit(1)
    
    print("⚙️ Starting sentiment service...")
    sentiment_thread = threading.Thread(target=update_sentiment, daemon=True)
    sentiment_thread.start()
    
    try:
        app.run(host="0.0.0.0", port=3000)
    except KeyboardInterrupt:
        shutdown_handler()
    finally:
        sentiment_thread.join()
        print("👋 Service stopped")
