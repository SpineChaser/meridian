import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(
    queue="inventory_queue",
    durable=True
    )
def receive_message(ch, method, properties, body):
    print(f"Received: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(
    queue="inventory_queue",
    on_message_callback=receive_message
)
print("Waiting for inventory messages...")
channel.start_consuming()