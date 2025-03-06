import os
import logging
from flask import Flask, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the API!", "status": "running"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logging.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)
