from flask import Flask, request

app = Flask(__name__)
@app.route('/')
def home():
    return "Meridian is running!"

@app.route('/check-in', methods=['POST'])
def check_in():
    data = request.get_json()
    return {
        "message": "Check-in received!",
        "attendee": data
    }


if __name__ == '__main__':
    app.run(debug=True)