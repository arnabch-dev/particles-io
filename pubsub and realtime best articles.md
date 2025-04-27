[] https://redis.io/blog/what-to-choose-for-your-synchronous-and-asynchronous-communication-needs-redis-streams-redis-pub-sub-kafka-etc-best-approaches-synchronous-asynchronous-communication/
[] http://blog.radiant3.ca/2013/01/03/reliable-delivery-message-queues-with-redis/ 
[] https://www.figma.com/blog/how-figmas-multiplayer-technology-works/
[] https://rxdb.info/replication.html
[] https://medium.com/@sayed.cse01/managing-redis-pub-sub-in-a-containerized-world-970f4a8c72a4
Pub/Sub -> push based
Streams -> pull based
[] https://stackoverflow.com/questions/63206036/is-there-a-way-to-subscribe-to-redis-streams-similar-to-redis-pub-sub
[] https://redis.io/learn/howtos/solutions/microservices/interservice-communication

### Persistent pub sub
```
MULTI
XADD logs:service1 * level error req-id 42 stack-trace "..."
LPUSH actions-queue "RESTART=service1"
PUBLISH live-notifs "New error event in service1!"
EXEC
```
* Now setup a consumer listening to the event of pub just as a signal
* Source of truth -> streams
Publisher
  │
  ├── XADD to stream:chat
  │
  └── PUBLISH "New message available" on channel:chat

Consumers:
  ├── Subscribed to Pub/Sub (channel:chat)
  │     └── On message: Wake up, fetch from stream (XREADGROUP)
  │
  └── Offline? No problem. Messages stay in stream.
        └── When back online: Resume XREADGROUP from last id.

* For streams, Consumer groups can independently track what they've read/acknowledged.
