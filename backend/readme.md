### dependency management
* Managed using poetry
* for the postgres using asyncpg and psycopg2
* if getting error add the below in the dependencies in the pyproject.toml
    ```
        "psycopg2-binary (>=2.9.10,<3.0.0)",
        "asyncpg (>=0.29.0,<1.0.0)"
    ```
* run poetry update
* run poetry install --no-root

# Player payload
```
players:{
    uuid:{
        sid:"",
        x:"",
        y:"",
        colors:"",
        joined_timestamp:"",
        status:{online,ttl 5mins}
    }
}

projectiles:[
    {x:"",y:"",playerUUID:""}
]
```
* uuid from jwt token

https://www.reddit.com/r/gamedev/comments/50a4ej/my_naive_multiplayer_game_sync_algorithm_and/
https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking

# Player Lobby Management and Assigning rooms
> May be we can use another field in the player details to make sure one player does not block the whole queue.
```python
# lobby caches
players_queue : set of player_id  which will be popped by the consumer
rooms:avaiable = redis_sorted_set(member-> roomId, score-> players) # heap
room:room_id = metadata with ttl 10mins
```
```python
# gameplay related cache
player:player_id : player_details with TTL 5mins # kv -> a centralised store for assigning room, player state, connected seeing, disconnected seeing,etc
projectile:room_id : queue
rooms:room_id:set() # players
leaderboard: sorted_set # heap
```
* One game at a time per client
* Lobby and room under same namespace -> /lobby
* Game under a separate namespace -> /game
* Lobby = Room
* Each lobby will be having max 5 members and min 3 members to start the game
* Technically a queuing and assinging in some priority basis
* Player joins a player-queue and it publishes an event.
    * Subscriber will listen
    * Search for the room -> rooms with max players to compelete the room fast
    * Pop the player
    * Ideally adding player and popping player should be 
    * Also add a shadow key(actually ttl). For getting the value
* When a room:room_id timesout
    * Listen to it and check the number of players
    * Take the decision of what to do with the room

* Maintaing race conditon for player joining flows
    * Player switching from lobby to room to game. Solved it by playing lobby and room under same namespace
    * Game joining when a player leaves a match in between. So at the start player makes a http call for lobby queueing. If he is a part of a prev match then no continuing.
    Plus the server takes care of room joining

> In a prod and at scale -> may be two or three rooms should be emulated in a single server node.

# Game tick server
* Problem of redis is we need to make a network roundtrip -> every 15ms making a network roundtrip is costly
* Challenge -> syncing between local cache , redis distributed cache and the database
    * Local cache -> for game ticker should be always fast
    * what if the server crash?

* Solution
    * DB is the source of truth
    * Redis is the layer for syncing -> Getting initial states or where the player was last time or a snapshot
    * Local cache is for the fast changing data. Coordinates changing at every 15ms. Also the projectiles
    * At every 15ms -> Local cache is updated
    * At every 30s -> the redis cache is updated
    * Not saving player movements to the database as we dont need replay for later on. May be added with a queue with aggregation doing batch updates
    * Some necessary parts like leaderboard and removal of players are done in the cache + db directly along with the local cache

* Failover strategy
    * We don't need to projectiles anywhere. Cause they simply can be fired again by the users
    * But player movements are necessary. We don't that to be again generated at random.
    * Redis -> snapshot of the last stored state of the player coordinates
    * If redis is also not having data -> lets load it from the db to the redis cause redis is also getting used as a session manager and checker
    * Replicate redis state to the room
    * DB is the ultimate source of truth
    * Plus redis cache is also getting used for tracking online of the player in the room so we need to update at some seconds

### Deployment plan
* Deploy with docker. Nginx on top of the server -> 
    * /app will go to the frontend hosted on the netlify
    * /feedback should go to the feedback page
    * / should go to the backend (ws support needed here)