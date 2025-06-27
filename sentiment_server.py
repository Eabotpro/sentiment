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
        try:
            if session_id is None:
                login_myfxbook()
            if session_id:
                r = requests.get("https://www.myfxbook.com/api/get-community-outlook.json", params={
                    "session": session_id
                })
                outlook = r.json()
                for sym in outlook["symbols"]:
                    if sym["symbol"] == "XAU/USD":
                        cached_sentiment["long"] = sym["longPercentage"]
                        cached_sentiment["short"] = sym["shortPercentage"]
                        print("Updated XAUUSD Sentiment:", cached_sentiment)
                        break
        except Exception as e:
            print("Update error:", e)
        time.sleep(300)  # كل 5 دقايق

# API endpoint
@app.route('/sentiment/XAUUSD')
def get_sentiment():
    return jsonify(cached_sentiment)

# تشغيل الـ background updater
@app.before_first_request
def start_background_thread():
    threading.Thread(target=update_sentiment, daemon=True).start()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
