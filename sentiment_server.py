from flask import Flask, jsonify
import requests
import threading
import time

app = Flask(__name__)

# بيانات الدخول لحساب Myfxbook
MYFXBOOK_EMAIL = "wifileb@gmail.com"
MYFXBOOK_PASSWORD = "Ilovechatgpt0214@"

# كاش البيانات وجلسة الدخول
cached_sentiment = {"symbol": "XAUUSD", "long": None, "short": None}
session_id = None

def login_myfxbook():
    global session_id
    try:
        print("🔐 Trying to login to Myfxbook...")
        r = requests.get("https://www.myfxbook.com/api/login.json", params={
            "email": MYFXBOOK_EMAIL,
            "password": MYFXBOOK_PASSWORD
        })
        data = r.json()
        if data["error"] is False:
            session_id = data["session"]
            print("✅ Logged in! Session ID:", session_id)
        else:
            print("❌ Login failed:", data["message"])
    except Exception as e:
        print("💥 Login error:", e)

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
                print("📋 Available symbols:")
                for sym in outlook.get("symbols", []):
                    print("➡️", sym["symbol"])  # نطبع كل الرموز

                    # عدّل هيدا السطر حسب الاسم الحقيقي اللي بشوفو
                    if sym["symbol"].lower() == "xauusd":
                        cached_sentiment["long"] = sym["longPercentage"]
                        cached_sentiment["short"] = sym["shortPercentage"]
                        print("✅ Updated XAUUSD Sentiment:", cached_sentiment)
                        break
                else:
                    print("❗ XAUUSD not found in returned symbols.")
        except Exception as e:
            print("💥 Update error:", e)
        time.sleep(300)  # كل 5 دقايق

@app.route("/sentiment/<symbol>", methods=["GET"])
def get_sentiment(symbol):
    if symbol.upper() == cached_sentiment["symbol"]:
        return jsonify(cached_sentiment)
    return jsonify({"error": "Symbol not found"}), 404

if __name__ == '__main__':
    print("⚙️ Starting background thread from main")
    threading.Thread(target=update_sentiment, daemon=True).start()
    print("🔁 Background thread started.")
    app.run(host='0.0.0.0', port=3000)
