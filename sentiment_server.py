from flask import Flask, jsonify
import requests, threading, time

app = Flask(__name__)
session_id = None
cached_sentiment = {"symbol": "XAU/USD", "long": None, "short": None}

def login_myfxbook():
    global session_id
    r = requests.post("https://www.myfxbook.com/api/login.json", data={
        "email": "wifileb@gmail.com",
        "password": "Ilovechatgpt0214@"
    })
    if r.json().get("error"):
        print("❌ Login failed:", r.json().get("message"))
        return
    session_id = r.json().get("session")
    print("✅ Logged in! Session ID:", session_id)

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
                for sym in outlook.get("symbols", []):
                    if sym["symbol"].lower() == "xau/usd":
                        cached_sentiment["long"] = sym["longPercentage"]
                        cached_sentiment["short"] = sym["shortPercentage"]
                        print("✅ Updated XAU/USD Sentiment:", cached_sentiment)
                        break
                else:
                    print("❗ Symbol not found in Myfxbook data.")
        except Exception as e:
            print("💥 Update error:", e)
        time.sleep(300)

@app.route('/sentiment/XAU/USD')
def get_sentiment():
    return jsonify(cached_sentiment)

if __name__ == '__main__':
    print("⚙️ Starting background thread from main")
    threading.Thread(target=update_sentiment, daemon=True).start()
    print("🔁 Background thread started.")
    app.run(host="0.0.0.0", port=3000)
