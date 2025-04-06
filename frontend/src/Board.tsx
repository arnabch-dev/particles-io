import SingleBoard from "./components/SingleBoard";
import MultiplayerBoard from "./components/MultiplayerBoard";

interface BoardProps {
  mode: "single" | "multiplayer";
}

export default function Board({ mode }: BoardProps) {
  return (
    <div>{mode === "single" ? <SingleBoard /> : <MultiplayerBoard />}</div>
  );
}
