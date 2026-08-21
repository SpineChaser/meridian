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

### Milestone 3 — Continuous Warehouse Polling

I updated the warehouse poller to run continuously instead of executing only once.

The poller now runs `poll_warehouse()` and waits 300 seconds before performing the next poll.

I verified that `POLL_INTERVAL` is set to 300 seconds and tested the repeated polling behavior using a temporary two-second interval.

The poller successfully retrieved the warehouse stock twice and updated the shared SQLite stock store each time.

### What I learned

A polling loop allows the inventory system to keep the shared stock store synchronized with the warehouse API over time.

The five-minute interval is represented as a configurable constant rather than being hard-coded into the polling logic.

The next step is to verify that the Flask query endpoint can continuously read the latest inventory while the poller updates the shared SQLite store.

## Day 3 — Final Status

### Completion

Day 3 is complete.

The warehouse polling workflow was extended from a one-time poll into a continuous polling process. The poller retrieves warehouse stock every five minutes and stores the latest inventory in the shared SQLite stock store.

The implementation was verified using a temporary two-second polling interval. Two consecutive polls successfully retrieved the warehouse stock and updated the SQLite store.

The project now has the following verified flow:

Warehouse API → Continuous Poller → SQLite Stock Store → Query Endpoint

### What I learned

Day 3 taught me that an inventory synchronization service needs more than a working API call. The system must continuously retrieve changing warehouse data, store it somewhere that can be shared between processes, and expose the latest stored data to clients.

I also learned why an in-memory Python dictionary is insufficient when the poller and Flask API run as separate processes. SQLite provides a shared persistence layer between them.

### Day 3 Status

Complete — continuous warehouse polling and shared inventory storage have been implemented and verified.

## Day 4 — Asynchronous Check-In & Frontend

### Day 4 Objective

The Day 4 requirement introduced a deliberate architectural pivot.

Instead of continuing to focus on the warehouse polling workflow, the project was extended toward an asynchronous event-driven check-in system. RabbitMQ became the central message queue for handling print requests asynchronously.

The goal was to connect the Flask check-in API, persistent check-in state, RabbitMQ, a background consumer, and a print webhook into one working workflow.

### Starting Point

Before making changes, I inspected the existing repository structure and verified that the working tree was clean.

The existing project contained:

- Flask application
- RabbitMQ producer and consumer
- SQLite stock store
- Warehouse API and poller
- Existing learning documentation
- Frontend/API components

Git verification showed that the repository was up to date with the remote branch and had no uncommitted changes.

### Architecture Pivot

The original Day 3 architecture was:

```text
Warehouse API
      ↓
Continuous Poller
      ↓
SQLite Stock Store
      ↓
Query Endpoint

For Day 4, the focus shifted to an asynchronous check-in workflow:

Frontend
    ↓
Flask /check-in
    ↓
SQLite Check-In State
    ↓
RabbitMQ print_requests
    ↓
Badge Consumer
    ↓
/print-webhook
    ↓
SQLite → PRINTED

RabbitMQ remained at the center of the architecture because the print operation does not need to block the initial check-in request.

### What I Changed

I extended the existing Flask application to support attendee check-ins.

The check-in workflow stores the attendee state in SQLite and initially marks a successful check-in as:PENDING

A print request is then published to RabbitMQ for asynchronous processing.

The RabbitMQ producer was reused and adapted for the print-request workflow, while the consumer was extended to process the print request and communicate with the print webhook.

### Asynchronous Processing

The consumer receives the print request from RabbitMQ and processes it independently from the original check-in request.

### The workflow is:
Check-in received
        ↓
Record stored as PENDING
        ↓
Print request published
        ↓
RabbitMQ queue
        ↓
Consumer receives message
        ↓
Print webhook called
        ↓
Successful processing
        ↓
Record updated to PRINTED
        ↓
RabbitMQ message acknowledged

This demonstrated the difference between a synchronous request and an asynchronous message-driven workflow.

### Duplicate Check-In Discovery

I verified that duplicate attendee IDs are rejected.

This prevents the same attendee from being registered repeatedly and ensures that an existing check-in is not accidentally processed as a new event.

### Print State Discovery

A new check-in initially remains in the PENDING state while the print request is waiting to be processed.

After the consumer successfully processes the print request and the webhook succeeds, the record changes to:PRINTED

This provides a persistent representation of the progress of the asynchronous operation.

### RabbitMQ Acknowledgement Behavior

The consumer was designed to acknowledge the RabbitMQ message only after successful processing.

This means that a message is not considered successfully completed simply because the consumer received it.

### The processing sequence is:

Receive message
      ↓
Process print request
      ↓
Call print webhook
      ↓
Successful result
      ↓
Update database
      ↓
Acknowledge RabbitMQ message

This helped demonstrate why acknowledgement timing matters in asynchronous systems.

### Completed Print Jobs

I also verified the behavior of an already-completed print job.

If a print request has already been completed, the system returns:409

The message is acknowledged rather than repeatedly processed.

This prevents an already-completed print job from being retried indefinitely.

### Frontend Integration

A frontend was added to provide a user-facing check-in flow.

Flask serves the frontend through its configured static directory, allowing the frontend and backend API to operate as part of the same application.

The frontend sends the check-in request to the Flask API, while the asynchronous print workflow continues through RabbitMQ and the consumer.

### Verification

The complete workflow was tested successfully:

Frontend
    ↓
Flask /check-in
    ↓
SQLite
    ↓
RabbitMQ
    ↓
Consumer
    ↓
Print webhook
    ↓
SQLite PRINTED state

### The verification confirmed that:

A valid attendee can check in.
The check-in is persisted in SQLite.
A new check-in starts in the PENDING state.
A print request is published to RabbitMQ.
The consumer receives the message asynchronously.
The consumer calls the print webhook.
Successful processing changes the record to PRINTED.
The RabbitMQ message is acknowledged after successful processing.
Duplicate attendee IDs are rejected.
Completed print jobs are not repeatedly processed.
The frontend can communicate with the Flask API.
The complete asynchronous workflow operates successfully.

### What I Learned

Day 4 showed me that RabbitMQ is not just another component added to an application. It changes how the application handles work.

The check-in request can complete without waiting for the physical printing process to finish. RabbitMQ acts as the boundary between the immediate API operation and the background print operation.

I also learned that persistent state is important in an asynchronous workflow. The PENDING and PRINTED states allow the system to track progress even though different processes are responsible for different parts of the workflow.

The consumer's acknowledgement behavior also demonstrated an important reliability principle: a message should only be acknowledged after the work it represents has successfully completed.

### Day 4 Final Status

Complete — the Meridian check-in workflow has been extended into an asynchronous RabbitMQ-based system with a Flask frontend, SQLite state persistence, a print producer, a background consumer, and a print webhook.

### The verified Day 4 architecture is:
Frontend
    ↓
Flask Check-In API
    ↓
SQLite — PENDING
    ↓
RabbitMQ print_requests
    ↓
Print Consumer
    ↓
Print Webhook
    ↓
SQLite — PRINTED

RabbitMQ is now the central asynchronous message path connecting the check-in system to the background printing workflow.
