import SingleBoard from "./components/SingleBoard";
import MultiplayerBoard from "./components/MultiplayerBoard";
import AuthProvider from "./components/AuthProvider";

interface BoardProps {
  mode: "single" | "multiplayer";
}

export default function Board({ mode }: BoardProps) {
  return (
    <div>
      {mode === "single" ? (
        <SingleBoard />
      ) : (
        <AuthProvider redirect_uri={window.location.origin}>
          <MultiplayerBoard />
        </AuthProvider>
      )}
    </div>
  );
}
