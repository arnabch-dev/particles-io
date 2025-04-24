import hashlib, random, math, uuid
from ..models import Player, GameElement, PlayerResponse


def get_unique_color_by_sid(sid):
    hash_value = int(hashlib.md5((sid.encode())).hexdigest(), 16)
    hue = hash_value % 360
    return f"hsl({hue}, 50%, 50%)"


def calculate_ping():
    return


def dump_player_details(sid, id, room_id, username="", prev_color=""):
    color = prev_color if prev_color else get_unique_color_by_sid(sid)
    x = random.random() * 500
    y = random.random() * 500
    # TODO: calculate ping
    ping = calculate_ping()
    player_details = Player(
        player_id=id,
        sid=sid,
        room_id=room_id,
        username="",
        color=color,
        position={"x": x, "y": y},
    )
    return player_details


def get_velocity(angle, speed=1):
    y_direction = math.sin(angle) * speed
    x_direction = math.cos(angle) * speed
    return x_direction, y_direction


def get_random_id():
    return uuid.uuid4().hex


def check_collision(obj1: GameElement, obj2: GameElement):
    dist = math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)
    return dist - obj1.radius - obj2.radius < 1



async def get_all_player_details(players_cache, room) -> list:
    players = []
    all_players_ids = await room.get_all_players()
    for pid in all_players_ids:
        player = await players_cache.get_player(pid)
        if player:
            player = player.model_dump()
            players.append(PlayerResponse(**player).model_dump())
    return players