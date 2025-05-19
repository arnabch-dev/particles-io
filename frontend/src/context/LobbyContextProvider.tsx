import {
  createContext,
  useContext,
  useEffect,
  useState,
  PropsWithChildren,
} from "react";
import { io, Socket } from "socket.io-client";
import { useAuth0 } from "@auth0/auth0-react";
import Loader from "../components/Loader";
import { Outlet, useNavigate } from "react-router";
import axios from "axios";
import AuthProtect from "../components/AuthProctect";

const SocketContext = createContext<null>(null);

export const useLobbySocket = () => {
  const context = useContext(SocketContext);
  if (!context)
    throw new Error(
      "useLobbySocket must be used within a LobbyContextProvider"
    );
  return context;
};
// @ts-ignore
export default function LobbyContextProvider({ children }: PropsWithChildren) {
  const [socket, setSocket] = useState<Socket | null>(null);
  // @ts-ignore
  const [isConnected, setIsConnected] = useState(false);

  const { getAccessTokenSilently, isAuthenticated, user } = useAuth0();
  const [token, setToken] = useState<string | null>(null);
  // @ts-ignore
  const [playerId, setPlayerId] = useState<string | null>(null);

  const navigate = useNavigate();

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

  // Initialize socket connection after HTTP handshake
  useEffect(() => {
    if (!token || !user) return;
    async function connectToLobby() {
      try {
        await axios.post(
          `${import.meta.env.VITE_BACKEND_URL}/lobby/`,
          {},
          {
            headers: { token },
            withCredentials: true,
          }
        );

        // ✅ If allowed — connect to /lobby socket
        const newSocket = io(`${import.meta.env.VITE_SOCKET_URL}/lobby`, {
          path: "/socket",
          withCredentials: true,
          transports: ["websocket"],
          auth: { token },
        });

        setSocket(newSocket);

        newSocket.on("connect", () => {
          console.log("✅ Connected to lobby socket:", newSocket.id);
          setIsConnected(true);
        });

        newSocket.on("disconnect", (reason) => {
          console.log("❌ Disconnected from lobby:", reason);
          setIsConnected(false);
        });

        newSocket.on("connect_error", (reason) => {
          console.error("❌ Socket connect error", reason);
          alert("Socket connection failed — check auth");
          setIsConnected(false);
        });

        newSocket.on("game:room-added", ({ room_id }) => {
          navigate(`/multiplayer/${room_id}`);
        });

        newSocket.on("game:start", ({ room_id }) => {
          navigate(`/multiplayer/game/${room_id}`);
        });
      } catch (err: any) {
        if (err.response?.status === 400) {
          const room = err.response.data.room;
          console.warn("Already in a match, redirecting to game:", room);
          navigate(`/multiplayer/game/${room}`);
        } else {
          console.error("Failed to join lobby", err);
        }
      }
    }

    connectToLobby();

    // Clean up
    return () => {
      socket?.disconnect();
    };
  }, [token, user]);
  return (
    <AuthProtect>
      <SocketContext.Provider value={null}>
        {socket?.connected ? <Outlet /> : <Loader text="Connecting....." />}
      </SocketContext.Provider>
    </AuthProtect>
  );
}
