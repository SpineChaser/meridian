import json
import pika

def publish_print_request(attendee_id, job_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost")
    )
    channel = connection.channel()

    channel.queue_declare(
        queue="print_requests",
        durable=True
    )
    message = json.dumps({
            "attendee_id": attendee_id,
            "job_id": job_id
        })

    channel.basic_publish(
        exchange="",
        routing_key="print_requests",
        body=message.encode(),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        )
    )

    connection.close()


if __name__ == "__main__":
    publish_print_request("ATT-TEST-001", "job-test-001")
    print("Test print request published.")
