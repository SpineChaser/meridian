# Day 1–2 Learning & Blocker Journal

## Tool
RabbitMQ

## Goal
Learn the basics of RabbitMQ by building a very small producer → queue → consumer prototype.

## Time-box
30 minutes

## Starting Point
RabbitMQ is unfamiliar to me.

## Blocker 1 — RabbitMQ command not found

### What I tried
```bash
rabbitmqctl status
Results: ``` bash: rabbitmqctl: command not found
### fix 
Tried normal command → command not found → verified installation → found executable → used its actual path.

### Resolution

RabbitMQ was already installed. The initial `rabbitmqctl` command failed because Git Bash could not find it through PATH.

### I verified the installation with:

```bash
where rabbitmqctl
where erl
###What I learned

RabbitMQ runs as a service/node and exposes AMQP connections on port 5672. The management interface is available on port 15672.
### Result

Resolved. RabbitMQ is running and ready for the prototype.

## Blocker 2 — Queue declaration rejected

### What I tried

I created a simple RabbitMQ producer using Python and Pika, then ran:

```bash
python producer.py
###Result

The connection reached RabbitMQ, but RabbitMQ rejected the queue declaration with: INTERNAL_ERROR - Feature `transient_nonexcl_queues` is deprecated.
By default, this feature is not permitted anymore.

### What I learned

The problem is not that RabbitMQ or Pika is missing. The producer is reaching the RabbitMQ server, but the queue declaration is incompatible with the current RabbitMQ 4.3.5 configuration.


### Now let's investigate instead of guessing

##used this command:

```bash
"/c/Program Files/RabbitMQ Server/rabbitmq_server-4.3.5/sbin/rabbitmqctl.bat" list_queues name durable auto_delete arguments

### Resolution

I checked the queues already available in RabbitMQ and found an existing
`inventory_queue` configured as a durable classic queue.

I changed the producer to use that queue and declare it as durable.

I ran:

```bash
python producer.py
### Result:

Sent LAPTOP-001 has 12 items in stock

### Next: Consumer

Now we'll complete the other half:

```text
Producer → RabbitMQ → Consumer

## Blocker 3 — Consumer exited immediately

### What I tried

I created `consumer.py` and ran:

```bash
python consumer.py

##Result

The program exited immediately without displaying a message or waiting for a message.

##Investigation

I checked the file with: cat consumer.py
I discovered that the file only connected to RabbitMQ and declared the queue. I had not yet added the consumer callback or start_consuming().

###What I learned

Connecting to a RabbitMQ queue does not automatically make a program consume messages. The consumer needs to register what it should do when a message arrives and then start consuming.

## Prototype Result

The RabbitMQ prototype is working.

The producer successfully published:

```text
LAPTOP-001 has 12 items in stock

The consumer received the message from inventory_queue:

Received: LAPTOP-001 has 12 items in stock

### What I learned

I learned the basic RabbitMQ message flow:

Producer → Queue → Consumer

I also learned how to troubleshoot a RabbitMQ connection, identify an existing queue, publish a message with Pika, and consume and acknowledge that message.

### Final Status

Complete — the Day 1–2 mini-prototype is functional.

## Day 3 — Original Specification

### Requirement

Individuals form and build toward the original specification:

- Poll a warehouse API every 5 minutes.
- Cache the latest stock information.
- Expose a query endpoint that allows clients to retrieve stock information.

### Initial Understanding

The Day 1–2 prototype established the RabbitMQ producer → queue → consumer workflow.

For Day 3, I need to extend the prototype toward the original inventory-sync specification. The main focus is understanding how to retrieve warehouse stock periodically, store the latest stock in a cache, and make that cached information available through an API endpoint.

### Planned Flow

Warehouse API → Poller → Stock Cache → Query Endpoint

RabbitMQ will remain part of the architecture where it provides value for the asynchronous inventory workflow.

### Day 3 Status

Started — requirement understood; implementation not yet complete.
