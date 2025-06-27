from flask import Flask, jsonify
import requests, threading, time

app = Flask(__name__)

# بيانات الدخول إلى Myfxbook
MYFXBOOK_EMAIL = "wifileb@gmail.com"
MYFXBOOK_PASSWORD = "Ilovechatgpt0214@"

session_id = None
cached_sentiment = {"symbol": "XAUUSD", "long": None, "short": None}

def login_myfxbook():
    global session_id
    try:
        print("🔐 Trying to login to Myfxbook...")
        r = requests.get("https://www.myfxbook.com/api/login.json", params={
            "email": MYFXBOOK_EMAIL,
            "password": MYFXBOOK_PASSWORD
        })
        res = r.json()
        if res["error"] is False:
            session_id = res["session"]
            print("✅ Logged in! Session ID:", session_id)
        else:
            print("❌ Login failed:", res["message"])
    except Exception as e:
        print("💥 Login error:", str(e))

def update_sentiment():
    global cached_sentiment, session_id
    print("⚙️ Starting background thread from main")
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
                    if sym["symbol"] == "XAU/USD":
                        cached_sentiment["long"] = sym["longPercentage"]
                        cached_sentiment["short"] = sym["shortPercentage"]
                        print("✅ Updated XAUUSD Sentiment:", cached_sentiment)
                        break
                else:
                    print("❗ XAU/USD not found in symbols.")
        except Exception as e:
            print("💥 Update error:", str(e))
        time.sleep(300)

@app.route("/sentiment/XAUUSD")
def get_sentiment():
    return jsonify(cached_sentiment)

if __name__ == "__main__":
    threading.Thread(target=update_sentiment, daemon=True).start()
    print("🔁 Background thread started.")
    app.run(host="0.0.0.0", port=3000)
