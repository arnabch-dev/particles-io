import {
  createContext,
  useContext,
  useEffect,
  useState,
  PropsWithChildren,
} from "react";
import { io, Socket } from "socket.io-client";
import { type Coordinate } from "../core/core";
import { useAuth0 } from "@auth0/auth0-react";
import Loader from "../components/Loader";

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
  token: string | null;
  playerId: string | null;
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

export default function SocketProvider({ children }: PropsWithChildren) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [playerData, setPlayerData] = useState<Player[]>([]);
  const [projectiles, setProjectiles] = useState<Projectile[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  const { getIdTokenClaims, getAccessTokenSilently, isAuthenticated, user } =
    useAuth0();

  const [token, setToken] = useState<string | null>(null);
  const [playerId, setPlayerId] = useState<string | null>(null);

  function resetProjetiles() {
    setProjectiles([]);
  }

  // Get Auth0 token and player ID after login
  useEffect(() => {
    if (!isAuthenticated || !user) return;

    async function fetchToken() {
      const claims = await getAccessTokenSilently();
      if (!claims || !user) return;
      setPlayerId(user?.sub as string);
      setToken(claims as string);
    }

    fetchToken();
  }, [isAuthenticated, getAccessTokenSilently, user]);

  // Initialize socket connection after token is set
  useEffect(() => {
    if (!token || !user) return;
    const newSocket = io(import.meta.env.VITE_SOCKET_URL!, {
      path: "/socket/",
      withCredentials: true,
      transports: ["websocket"],
      auth: { token },
    });

    setSocket(newSocket);

    newSocket.on("connect", () => {
      console.log("✅ Connected to socket:", newSocket.id);
      setIsConnected(true);
    });

    newSocket.on("disconnect", (reason) => {
      console.log("❌ Disconnected:", reason);
      setIsConnected(false);
    });

    newSocket.on("connect_error", (reason) => {
      alert("❌ Socket connect error: Invalid auth");
      console.error(reason);
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
  }, [token, user]);

  function emitMovement(movement: Movement) {
    if (!socket || !socket.connected) return;
    socket.emit("move", movement);
  }

  function emitShoot(coordinate: ShootingCoordinates) {
    if (!socket || !socket.connected) return;
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
    <SocketContext.Provider value={game}>
      {socket?.connected ? children : <Loader text="Connecting to lobby...." />}
    </SocketContext.Provider>
  );
}
