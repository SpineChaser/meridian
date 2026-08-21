from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import uuid

from stock_store import get_stock
from checkin_store import (
    initialize_database,
    create_pending_checkin,
    get_checkin,
    mark_printed,
)
from print_producer import publish_print_request

app = Flask(__name__, static_folder="frontend", static_url_path="")

initialize_database()

@app.route('/')
def home():
    return send_from_directory('frontend', 'index.html')

@app.route('/check-in', methods=['POST'])
def check_in():
    data = request.get_json()

    if not data or not data.get('attendee_id'):
        return {
            "message": "attendee_id is required"
        }, 400

    attendee_id = data["attendee_id"]
    job_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    created = create_pending_checkin(
        attendee_id,
        job_id,
        timestamp
    )

    if not created:
        existing = get_checkin(attendee_id)

        return {
            "message": "Attendee already has a check-in",
            "attendee": existing
        }, 409

    publish_print_request(attendee_id, job_id)

    return {
        "message": "Check-in pending",
        "attendee_id": attendee_id,
        "job_id": job_id,
        "status": "PENDING"
    }, 202


@app.route('/print-webhook', methods=['POST'])
def print_webhook():
    data = request.get_json()

    if not data:
        return {
            "message": "Webhook payload is required"
        }, 400

    attendee_id = data.get("attendee_id")
    job_id = data.get("job_id")
    status = data.get("status")

    if not attendee_id or not job_id or not status:
        return {
            "message": "attendee_id, job_id and status are required"
        }, 400

    if status != "PRINTED":
        return {
            "message": "Unsupported print status"
        }, 400

    updated = mark_printed(
        attendee_id,
        job_id,
        datetime.now().isoformat()
    )

    if not updated:
        return {
            "message": "Print job already completed or does not match"
        }, 409

    return {
        "message": "Print confirmed",
        "attendee_id": attendee_id,
        "job_id": job_id,
        "status": "PRINTED"
    }, 200

@app.route('/inventory/stock', methods=['GET'])
def inventory_stock():
    return jsonify(get_stock())


if __name__ == '__main__':
    app.run(debug=True)

