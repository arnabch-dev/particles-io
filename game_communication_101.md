## Tick, fps , interpolation
tick -> one cycle of servers' simulation
fps -> rendering on the clients' screen

suppose server is having 20tick/s -> updates every 50ms
client is having 60FPS -> updates every 16ms

between each server update -> client updates 3.3 times

.3 means in middle and if we update client state from server
state it will lead to jitter(teleportation kind of effect)

Solution
1) Interpolation(estimating current)
Basically estimating the current position
Server update 1 -> x=100 t=0
Server update 2 -> x=200 t=50

Client at t = 25 which is inbetween
So client will determine if the source of truth is going from
100 to 200 in 50ms then at 25ms what should be the position
t=25 , x = 100 + (200-100) x (25/50) = 150

* glitch free

2) Extrapolation
Predicting the future instead of the current based on last.
If client is moving at 100m/s and it haven't heard anything from 
server it will continue moving at 100m/s

when true value from server comes it does a transition from current to
true position

Game engines store inputs hisitory as well and matches from where the mismatch happendtick -> one cycle of servers' simulation
fps -> rendering on the clients' screen

suppose
server is having 20tick/s -> updates every 50ms
client is having 60FPS -> updates every 16ms

between each server update -> client updates 3.3 times. Here .3 means in middle and if we update client state from server
state it will lead to jitter(teleportation kind of effect)

Solution
1) Interpolation(estimating current)
Basically estimating the current position
Server update 1 -> x=100 t=0
Server update 2 -> x=200 t=50

Client at t = 25 which is inbetween
So client will determine if the source of truth is going from
100 to 200 in 50ms then at 25ms what should be the position
t=25 , x = 100 + (200-100) x (25/50) = 150

* glitch free

2) Extrapolation
Predicting the future instead of the current based on last.
If client is moving at 100m/s and it haven't heard anything from 
server it will continue moving at 100m/s

when true value from server comes it does a transition from current to
true position

Game engines store inputs hisitory as well
and matches from where the mismatch happend

## Target shooting prediction on server
When client send event for shooting, other player also moving + lag + ping.
So we need to replicate what client sees on the screen

```bash
Current Server Time - Packet Latency - Interpolation Time
```

We can have a ping-pong mechanism to get the packet latency