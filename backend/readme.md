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
