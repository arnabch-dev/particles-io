from collections import defaultdict
from system.models import Player
from .projectile import ProjectileCache
from system.constant import RoomStatus, MAX_MEMBERS

class GameRoomCache:
    def __init__(self):
        self._cache = {}

    def create_room(self, room_id: str):
        if room_id not in self._cache:
            self._cache[room_id] = {
                "players": {},
                "projectiles": ProjectileCache(),
                "status":RoomStatus.idle
            }

    def set_player(self, room_id: str, user_id: str, player: Player):
        self.create_room(room_id)
        self._cache[room_id]["players"][user_id] = player
        if self.get_player_count(room_id) == MAX_MEMBERS:
            self.start_game(room_id)


    def remove_player(self, room_id: str, user_id: str):
        room = self._cache.get(room_id)
        if room and user_id in room["players"]:
            del room["players"][user_id]

    def get_player(self, room_id: str, user_id: str) -> Player | None:
        room = self._cache.get(room_id)
        if room:
            return room["players"].get(user_id)
        return None

    def get_players_batch(self,room_id:str):
        return self._cache.get(room_id, {}).get("players", {})

    def get_all_players(self, room_id: str):
        return list(self.get_players_batch(room_id).values())
    
    def get_projectile_cache(self, room_id: str) -> ProjectileCache:
        self.create_room(room_id)
        return self._cache[room_id]["projectiles"]

    def delete_room(self, room_id: str):
        if room_id in self._cache:
            del self._cache[room_id]

    def get_rooms(self):
        return list(self._cache.keys())
    
    def get_player_count(self,room_id):
        return len(self.get_all_players(room_id))
    
    def start_game(self,room_id):
        self._cache[room_id]['status'] = RoomStatus.started

    def is_game_started(self,room_id):
        return self._cache[room_id]['status'] == RoomStatus.started or self.get_player_count(room_id) == MAX_MEMBERS
    
    def is_game_completed(self,room_id):
        # TODO: need to consider the disconnection of the player as well
        return self._cache[room_id]['status'] == RoomStatus.started and self.get_player_count(room_id) < MAX_MEMBERS