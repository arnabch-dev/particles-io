import {
  createContext,
  useContext,
  useEffect,
  useState,
  PropsWithChildren,
} from "react";
import { io, Socket } from "socket.io-client";
import { type Coordinate } from "./core/core";
interface Player {
  color: string;
  player_id: string;
  position: Coordinate;
}

interface Projectile {
  color: string;
  position: Coordinate;
  angle: number;
  projectile_id: string;
}

type Movement = "up" | "down" | "left" | "right";
interface ShootingCoordinates {
  angle: number;
  position: {
    x: number;
    y: number;
  };
}

interface Game {
  isConnected: boolean;
  player: Player[];
  projectiles: Projectile[];
  socket: Socket | null;
  token: string;
  playerId: string;
  resetProjetiles: () => void;
  emitMovement: (movement: Movement) => void;
  emitShoot: (coordinates: ShootingCoordinates) => void;
}

const SocketContext = createContext<Game | null>(null);

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context)
    throw new Error("useSocket must be used within a SocketProvider");
  return context;
};

const token = prompt("token")!;
export default function SocketProvider({ children }: PropsWithChildren) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [playerData, setPlayerData] = useState<Player[]>([]);
  const [projectiles, setProjectiles] = useState<Projectile[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  // TODO:Making token and playerid same for ease
  // TODO: change this to auth endpont
  // const [token, setToken] = useState(
  //   "8fa071ed-8d80-4d6c-a482-dd9cba652207"
  // );
  const [playerId, setPlayerId] = useState(token);

  function resetProjetiles() {
    setProjectiles([]);
  }

  useEffect(() => {
    const newSocket = io(import.meta.env.VITE_SOCKET_URL!, {
      path: "/socket/",
      withCredentials: true,
      transports: ["websocket"], // Using WebSockets only
      auth: { token },
    });

    setSocket(newSocket);

    // Handle connection
    newSocket.on("connect", () => {
      console.log("✅ Connected to socket:", newSocket.id);
      setIsConnected(true);
    });

    // Handle disconnection
    newSocket.on("disconnect", (reason) => {
      console.log("❌ Disconnected:", reason);
      setIsConnected(false);
    });

    newSocket.on("connect_error", (reason) => {
      alert("invalid auth");
      console.log("❌ Disconnected:", reason);
      setIsConnected(false);
    });

    newSocket.on("joined", (players: Player[]) => {
      setPlayerData(players);
    });

    newSocket.on("update-players", (players: Player[]) => {
      setPlayerData(players);
    });

    newSocket.on("update-projectiles", (newProjectiles: Projectile[]) => {
      setProjectiles(newProjectiles);
    });

    return () => {
      newSocket.disconnect();
    };
  }, []);

  function emitMovement(movement: Movement) {
    if (!socket) return;
    socket.emit("move", movement);
  }

  async function emitShoot(coordinate: ShootingCoordinates) {
    if (!socket) return;
    socket.emit("shoot", coordinate);
  }

  const game: Game = {
    isConnected,
    player: playerData,
    projectiles,
    socket,
    token,
    playerId,
    emitMovement,
    emitShoot,
    resetProjetiles,
  };

  return (
    <SocketContext.Provider value={game}>{children}</SocketContext.Provider>
  );
}
