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

### Implementation Decision

The existing Flask application and RabbitMQ prototype will be extended rather than replaced.

For development, I will use a local mock warehouse API to simulate the external warehouse service. This allows me to build and test the polling and caching workflow without depending on an external service.

The first implementation milestone is:

Warehouse API → Poller → Stock Cache

The five-minute scheduling and query endpoint will be added after the basic polling and caching flow is verified.

### Milestone 1 — Mock Warehouse API

I created a local Flask service to simulate the external warehouse API.

The service exposes:

GET /warehouse/stock

The endpoint successfully returned the current warehouse stock as JSON.

Example result:

- LAPTOP-001: 12
- MOUSE-002: 50
- KEYBOARD-003: 30
- PHONE-004: 25
- TABLET-005: 8

### What I learned

A local mock API allows me to develop and test the inventory synchronization workflow without depending on an external warehouse service.

The next step is to build a poller that retrieves this data and updates the stock cache.

### Dependency Discovery

While building the warehouse poller, I discovered that the Python environment did not have the requests package installed.

I verified this with the command:

python -m pip show requests

The package was not found, so I installed it and verified version 2.34.2.

I then added requests==2.34.2 to requirements.txt so the dependency is reproducible for the project.

### What I learned

A working local environment is not enough. Dependencies used by the application must also be recorded in requirements.txt so another developer can recreate the environment.

### Milestone 2 — Warehouse Poller

I created a poller that retrieves stock from the mock warehouse API using the requests library.

The poller successfully retrieved the warehouse stock and passed it to the stock cache.

Test result:

Updated stock cache: {'KEYBOARD-003': 30, 'LAPTOP-001': 12, 'MOUSE-002': 50, 'PHONE-004': 25, 'TABLET-005': 8}

### Cache Behavior Discovery

The current stock cache is an in-memory Python dictionary.

When the poller process exits, the cached data is lost. Starting another Python process creates a new empty cache.

This showed me that the current cache implementation works for demonstrating the data flow, but it is not yet suitable for a continuously running inventory service.

### Next Step

The next milestone is to keep the poller running continuously and introduce the five-minute polling interval. After that, the query endpoint will read from the cache while the poller continues updating it.

### Query Endpoint Discovery

I added a GET /inventory/stock endpoint that reads from the shared SQLite stock store.

Initially, the endpoint returned an empty object because the poller and Flask application were using separate in-memory Python processes.

This exposed an important limitation of the original in-memory cache: each Python process has its own copy of the cache.

### Architecture Decision

I replaced the in-memory cache as the shared storage layer with SQLite.

The resulting architecture is:

Warehouse API → Poller → SQLite Stock Store → Query Endpoint

The poller writes the latest warehouse inventory to SQLite, while the Flask API reads the latest stored inventory from the same database.

I verified the design by running the poller and then reading the inventory from a separate Python process. The Flask query endpoint also returned the stored warehouse inventory successfully.
