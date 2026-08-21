from flask import Flask, request, jsonify

from stock_store import get_stock

app = Flask(__name__)
attendees = {}

@app.route('/')
def home():
    return "Meridian is running!"

@app.route('/check-in', methods=['POST'])
def check_in():
    data = request.get_json()
    attendee_id = data.get('attendee_id')

    if attendee_id in attendees:
        return {
            "message": "Attendee already checked in!",
            "attendee": data
        }, 409

    attendees[attendee_id] = "checked_in"

    return {
        "message": "Check-in received!",
        "attendee": data
    }

@app.route('/inventory/stock', methods=['GET'])
def inventory_stock():
    return jsonify(get_stock())


if __name__ == '__main__':
    app.run(debug=True)

