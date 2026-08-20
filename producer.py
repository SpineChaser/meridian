import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters("localhost")
)

channel = connection.channel()

channel.queue_declare(
    queue="inventory_queue",
    durable=True
)

message = "LAPTOP-001 has 12 items in stock"

channel.basic_publish(
    exchange="",
    routing_key="inventory_queue",
    body=message
)

print(f"Sent: {message}")

connection.close()