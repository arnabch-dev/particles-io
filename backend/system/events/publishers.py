from . import pub_sub


async def player_joined():
    await pub_sub.publish("players:*", "Message")
