from flask import Flask, jsonify
import requests, threading, time

app = Flask(__name__)

# بيانات حساب Myfxbook
MYFXBOOK_EMAIL = "wifileb@gmail.com"
MYFXBOOK_PASSWORD = "Ilovechatgpt0214@"

# بيانات global
cached_sentiment = {"symbol": "XAUUSD", "long": None, "short": None}
session_id = None

# دالة تسجيل الدخول إلى Myfxbook
def login_myfxbook():
    global session_id
    try:
        r = requests.get("https://www.myfxbook.com/api/login.json", params={
            "email": MYFXBOOK_EMAIL,
            "password": MYFXBOOK_PASSWORD
        })
        data = r.json()
        if data["error"]:
            print("Login failed:", data["message"])
            return None
        session_id = data["session"]
        print("Logged in to Myfxbook.")
    except Exception as e:
        print("Login error:", e)

# دالة لتحديث البيانات كل 5 دقائق
def update_sentiment():
    global cached_sentiment, session_id
    while True:
        print("🔁 Background thread started.")
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

# API endpoint
@app.route('/sentiment/XAUUSD')
def get_sentiment():
    return jsonify(cached_sentiment)

# تشغيل الـ background updater
if __name__ == '__main__':
    print("⚙️ Starting background thread from main")
    threading.Thread(target=update_sentiment, daemon=True).start()
    app.run(host="0.0.0.0", port=3000)
