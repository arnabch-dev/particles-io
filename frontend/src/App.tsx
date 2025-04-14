import { BrowserRouter, Routes, Route } from "react-router";
import LandingPage from "./pages/landing-page";
import AuthProvider from "./context/AuthProvider";
import MultiplayerPage from "./pages/multiplayer";

function App() {
  const URI = `${window.location.origin}/multiplayer`
  return (
    <AuthProvider redirect_uri={URI}>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage/>}/>
        <Route path="/multiplayer" element={<MultiplayerPage />} />
      </Routes>
    </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
