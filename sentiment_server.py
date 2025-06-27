import requests
import threading
import time
from flask import Flask, jsonify

app = Flask(__name__)

cached_sentiment = {"symbol": "XAUUSD", "long": None, "short": None}
session_id = None

def login_myfxbook():
    global session_id
    try:
        r = requests.get("https://www.myfxbook.com/api/login.json", params={
            "email": "wifileb@gmail.com",
            "password": "Ilovechatgpt0214@"
        })
        session_id = r.json().get("session")
        print("🔐 Logged in with session ID:", session_id)
    except Exception as e:
        print("💥 Login error:", e)
        session_id = None

def update_sentiment():
    global cached_sentiment, session_id
    while True:
        try:
            if session_id is None:
                login_myfxbook()
            if session_id:
                print("📡 Fetching sentiment...")
                r = requests.get("https://www.myfxbook.com/api/get-community-outlook.json", params={
                    "session": session_id
                })
                outlook = r.json()
                print("🔍 Outlook keys:", outlook.keys())
                for sym in outlook.get("symbols", []):
                    if sym["symbol"] == "XAU/USD":
                        cached_sentiment["long"] = sym["longPercentage"]
                        cached_sentiment["short"] = sym["shortPercentage"]
                        print("✅ Updated XAUUSD Sentiment:", cached_sentiment)
                        break
                else:
                    print("❗ XAU/USD not found in symbols.")
        except Exception as e:
            print("💥 Update error:", e)
        time.sleep(300)

@app.route("/sentiment/<symbol>")
def get_sentiment(symbol):
    if symbol.upper() == "XAUUSD":
        return jsonify(cached_sentiment)
    return jsonify({"error": "Symbol not found"}), 404

if __name__ == "__main__":
    print("⚙️ Starting background thread from main")
    thread = threading.Thread(target=update_sentiment)
    thread.daemon = True
    thread.start()
    print("🔁 Background thread started.")
    app.run(host="0.0.0.0", port=3000)
