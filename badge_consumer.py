import json
import pika
import requests


def handle_print_request(ch, method, properties, body):
    message = json.loads(body.decode())

    attendee_id = message["attendee_id"]
    job_id = message["job_id"]

    print(f"Print request received for {attendee_id}")
    print(f"Job ID: {job_id}")

    webhook_data = {
        "attendee_id": attendee_id,
        "job_id": job_id,
        "status": "PRINTED"
    }

    response = requests.post(
        "http://127.0.0.1:5000/print-webhook",
        json=webhook_data
    )

    print(f"Webhook response: {response.status_code}")

    if response.status_code == 200:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Print confirmed and message acknowledged.")

    elif response.status_code == 409:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Print job was already completed. Message acknowledged.")

    else:
        print("Print confirmation failed. Message was not acknowledged.")


def start_badge_consumer():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost")
    )

    channel = connection.channel()

    channel.queue_declare(
        queue="print_requests",
        durable=True
    )

    print("Waiting for print requests...")

    channel.basic_consume(
        queue="print_requests",
        on_message_callback=handle_print_request
    )

    channel.start_consuming()


if __name__ == "__main__":
    start_badge_consumer()