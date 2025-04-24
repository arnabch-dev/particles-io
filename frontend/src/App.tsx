import { BrowserRouter, Routes, Route } from "react-router";
import LandingPage from "./pages/landing-page";
import AuthProvider from "./context/AuthProvider";
import MultiplayerPage from "./pages/multiplayer";
import LobbyConnectingPage from "./pages/lobby";
import LobbyRoomPage from "./pages/game-room";
import LobbyContextProvider from "./context/LobbyContextProvider";

function App() {
  const URI = `${window.location.origin}/multiplayer`;
  return (
    <AuthProvider redirect_uri={URI}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />

          {/* Lobby Routes */}
          <Route path="multiplayer" element={<LobbyContextProvider />}>
            <Route index element={<LobbyConnectingPage />} />
            <Route path=":room" element={<LobbyRoomPage />} />
          </Route>

          {/*Actual Game Routes */}
          <Route
            path="multiplayer/game/:room"
            element={<MultiplayerPage />}
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
