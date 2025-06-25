from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/sentiment/XAUUSD')
def get_sentiment():
    return jsonify({
        "symbol": "XAUUSD",
        "long": 61.3,
        "short": 38.7
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
