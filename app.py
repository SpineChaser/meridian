from flask import Flask, request

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


if __name__ == '__main__':
    app.run(debug=True)