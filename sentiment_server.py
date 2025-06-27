import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
import threading
import time

app = Flask(__name__)
cached_sentiment = {"symbol": "XAUUSD", "long": None, "short": None}

def fetch_fxssi_sentiment():
    try:
        response = requests.get("https://fxssi.com/tools/current-ratio")
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="ratio__table")
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2 and "XAUUSD" in cols[0].text:
                sentiment_text = cols[1].text.strip()
                long_pct, short_pct = sentiment_text.split("–")
                long_pct = float(long_pct.strip().replace("%", ""))
                short_pct = float(short_pct.strip().replace("%", ""))
                cached_sentiment["long"] = long_pct
                cached_sentiment["short"] = short_pct
                print("✅ Updated XAUUSD Sentiment:", cached_sentiment)
                break
    except Exception as e:
        print("💥 Sentiment fetch error:", e)

def update_sentiment_periodically():
    while True:
        fetch_fxssi_sentiment()
        time.sleep(300)  # كل 5 دقائق

@app.route("/sentiment/XAUUSD")
def get_sentiment():
    return jsonify(cached_sentiment)

if __name__ == "__main__":
    threading.Thread(target=update_sentiment_periodically, daemon=True).start()
    print("⚙️ Background sentiment updater started...")
    app.run(host="0.0.0.0", port=3000)
