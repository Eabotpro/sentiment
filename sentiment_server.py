from flask import Flask, jsonify
import requests
import threading
import time

app = Flask(__name__)

# 📦 تخزين الجلسة والبيانات
session_id = None
cached_sentiment = {"symbol": "XAUUSD", "long": None, "short": None}

# 📥 بيانات الدخول لـ Myfxbook – غيرهم حسب حسابك
MYFXBOOK_EMAIL = "wifileb@gmail.com"
MYFXBOOK_PASSWORD = "Ilovechatgpt0214@"

# 🔐 تسجيل الدخول
def login_myfxbook():
    global session_id
    try:
        print("🔐 Trying to login to Myfxbook...")
        r = requests.post("https://www.myfxbook.com/api/login.json", params={
            "email": MYFXBOOK_EMAIL,
            "password": MYFXBOOK_PASSWORD
        })
        response = r.json()
        if response.get("error") == False:
            session_id = response.get("session")
            print("✅ Logged in! Session ID:", session_id)
        else:
            print("❌ Login failed:", response.get("message"))
    except Exception as e:
        print("💥 Login error:", e)

# 🔁 تحديث البيانات كل فترة
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
                    if sym["symbol"] in ["XAUUSD", "XAU/USD", "xauusd.sd"]:
                        cached_sentiment["long"] = sym["longPercentage"]
                        cached_sentiment["short"] = sym["shortPercentage"]
                        print("✅ Updated XAUUSD Sentiment:", cached_sentiment)
                        break
                else:
                    print("❗ XAUUSD not found in symbols.")
        except Exception as e:
            print("💥 Update error:", e)
        time.sleep(300)  # كل 5 دقايق

# 🌐 Endpoint للقراءة
@app.route('/sentiment/XAUUSD')
def get_sentiment():
    return jsonify(cached_sentiment)

# 🚀 تشغيل الخادم والخيط بالخلفية
if __name__ == '__main__':
    print("⚙️ Starting background thread from main")
    threading.Thread(target=update_sentiment, daemon=True).start()
    print("🔁 Background thread started.")
    app.run(host='0.0.0.0', port=3000)
