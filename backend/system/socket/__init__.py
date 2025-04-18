import socketio
from .game import GameNamespace
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
game_namespace = GameNamespace("/game")
sio.register_namespace(game_namespace)
socket_app = socketio.ASGIApp(sio, socketio_path="/socket/")