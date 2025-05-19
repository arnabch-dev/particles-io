import { BrowserRouter, Routes, Route } from "react-router";
import LandingPage from "./pages/landing-page";
import AuthProvider from "./context/AuthProvider";
import MultiplayerPage from "./pages/multiplayer";
import LobbyConnectingPage from "./pages/lobby";
import LobbyRoomPage from "./pages/game-room";
import LobbyContextProvider from "./context/LobbyContextProvider";
import GameSocketProvider from "./context/GameSocketProvider";
import Leaderboard from "./pages/leaderboard";

function App() {
  const URI = `${window.location.origin}/multiplayer`;
  return (
    <AuthProvider redirect_uri={URI}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          
          <Route path="single" element={<h1>Some fixes going on</h1>} />

          {/* Routing based on namespace for having a discrete namespace websocket connection to the server */}
          {/* Lobby Routes */}
          <Route path="multiplayer" element={<LobbyContextProvider />}>
            <Route index element={<LobbyConnectingPage />} />
            <Route path=":room" element={<LobbyRoomPage />} />
          </Route>

          {/*Actual Game Routes */}
          <Route path="multiplayer/game" element={<GameSocketProvider/>}>
            <Route path=":room" element={<MultiplayerPage />} />
          </Route>

          <Route path="leaderboard/:room" element={<Leaderboard />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
