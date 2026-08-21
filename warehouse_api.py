from flask import Flask, jsonify

app = Flask(__name__)

stock = {
    "LAPTOP-001": 12,
    "MOUSE-002": 50,
    "KEYBOARD-003": 30,
    "PHONE-004": 25,
    "TABLET-005": 8
}

@app.route("/warehouse/stock", methods=["GET"])
def get_stock():
    return jsonify(stock)

if __name__ == "__main__":
    app.run(port=5001, debug=True)

