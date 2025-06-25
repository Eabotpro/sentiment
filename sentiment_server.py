import requests
from flask import Flask, jsonify

app = Flask(__name__)

# حساب Myfxbook
email = "wifileb@gmail.com"
password = "Ilovechatgpt0214@"

# تسجيل الدخول
login_url = f"https://www.myfxbook.com/api/login.json?email={email}&password={password}"
login_response = requests.get(login_url).json()

# التأكد من الدخول
if not login_response["error"]:
    session_id = login_response["session"]

    # سحب بيانات المجتمع (Community Outlook)
    sentiment_url = f"https://www.myfxbook.com/api/get-community-outlook.json?session={session_id}"
    sentiment_response = requests.get(sentiment_url).json()

    # استخراج نسبة long/short لـ XAUUSD
    long_pct = None
    short_pct = None

    for item in sentiment_response["symbols"]:
        if item["symbol"] == "XAU/USD":
            long_pct = item["longPercentage"]
            short_pct = item["shortPercentage"]
            break
else:
    print("❌ فشل تسجيل الدخول:", login_response["message"])
    long_pct = 0
    short_pct = 0

@app.route('/sentiment/XAUUSD')
def get_sentiment():
    return jsonify({
        "symbol": "XAUUSD",
        "long": long_pct,
        "short": short_pct
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
