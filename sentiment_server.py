from flask import Flask, jsonify
import requests, threading, time

app = Flask(__name__)

session_id = None
cached_sentiment = {
    "symbol": "XAUUSD",
    "long": None,
    "short": None
}

email = "wifileb@gmail.com"
password = "Ilovechatgpt0214@"

def login_myfxbook():
    global session_id
    try:
        print("🔐 Logging in to Myfxbook...")
        r = requests.get("https://www.myfxbook.com/api/login.json", params={
            "email": email,
            "password": password
        })
        data = r.json()
        if data["error"]:
            print("❌ Login failed:", data["message"])
        else:
            session_id = data["session"]
            print("✅ Logged in! Session ID:", session_id)
    except Exception as e:
        print("💥 Login error:", e)

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
                    if "XAUUSD" in sym["symbol"]:
                        cached_sentiment["long"] = sym["longPercentage"]
                        cached_sentiment["short"] = sym["shortPercentage"]
                        print("✅ Updated XAUUSD Sentiment:", cached_sentiment)
                        break
                else:
                    print("❗ XAUUSD not found in symbols.")
        except Exception as e:
            print("💥 Update error:", e)
        time.sleep(300)

@app.route('/sentiment/<symbol>')
def get_sentiment(symbol):
    if symbol.upper() == "XAUUSD":
        return jsonify(cached_sentiment)
    return jsonify({"error": "Symbol not supported"}), 404

def start_background_thread():
    print("⚙️ Starting background thread from main")
    t = threading.Thread(target=update_sentiment)
    t.daemon = True
    t.start()
    print("🔁 Background thread started.")

if __name__ == '__main__':
    start_background_thread()
    app.run(host="0.0.0.0", port=3000)
