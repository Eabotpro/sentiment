from flask import Flask, jsonify
import threading
import requests
import time

app = Flask(__name__)

cached_sentiment = {"symbol": "XAUUSD", "long": None, "short": None}
session_id = None

def login_myfxbook():
    global session_id
    try:
        r = requests.post("https://www.myfxbook.com/api/login.json", data={
            "email": "wifileb@gmail.com",
            "password": "Ilovechatgpt0214@"
        })
        result = r.json()
        if result.get("error"):
            print("❌ Login error:", result["message"])
        else:
            session_id = result.get("session")
            print("✅ Logged in! Session ID:", session_id)
    except Exception as e:
        print("💥 Login exception:", e)

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
                print("📋 Available symbols:")
                for sym in outlook.get("symbols", []):
                    print("➡️", sym["symbol"])  # Debug print to check real symbol names
                    if sym["symbol"].lower() == "xauusd.sd":  # <-- غيرها حسب ما يطلعلك
                        cached_sentiment["long"] = sym["longPercentage"]
                        cached_sentiment["short"] = sym["shortPercentage"]
                        print("✅ Updated Sentiment:", cached_sentiment)
                        break
                else:
                    print("❗ Symbol not found.")
        except Exception as e:
            print("💥 Update error:", e)
        time.sleep(300)

@app.route("/sentiment/<symbol>")
def get_sentiment(symbol):
    if symbol.upper() == "XAUUSD":
        return jsonify(cached_sentiment)
    else:
        return jsonify({"symbol": symbol.upper(), "long": None, "short": None})

if __name__ == "__main__":
    print("⚙️ Starting background thread from main")
    threading.Thread(target=update_sentiment, daemon=True).start()
    print("🔁 Background thread started.")
    app.run(host="0.0.0.0", port=3000)
