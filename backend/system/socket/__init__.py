from system.sio import sio
import socketio
from .game import GameNamespace
from .lobby import LobbyNamespace


game_namespace = GameNamespace("/game")
lobby_namespace = LobbyNamespace("/lobby")
sio.register_namespace(game_namespace)
sio.register_namespace(lobby_namespace)
socket_app = socketio.ASGIApp(sio, socketio_path="/socket")
