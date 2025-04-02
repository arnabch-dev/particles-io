import {
  createContext,
  useContext,
  useEffect,
  useState,
  PropsWithChildren,
} from "react";
import { io, Socket } from "socket.io-client";


interface Player{
    color:string
}

interface Game {
  isConnected: boolean;
  player:Player | null
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
  const [playerData,setPlayerData] = useState<Player|null>(null)
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const newSocket = io(import.meta.env.VITE_SOCKET_URL!, {
      path: "/socket/",
      withCredentials: true,
      transports: ["websocket"], // Using WebSockets only
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

    newSocket.on("joined", (value:Player) => {
        setPlayerData(value)
      });

    return () => {
      newSocket.disconnect();
    };
  }, []);

  const game: Game = {
    isConnected,
    player:playerData
  };

  return (
    <SocketContext.Provider value={game}>{children}</SocketContext.Provider>
  );
}
