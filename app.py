# app.py
from flask import Flask, jsonify
from datetime import datetime, timezone

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Hello from PyPulse",
        "time": datetime.now(timezone.utc).isoformat()
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)