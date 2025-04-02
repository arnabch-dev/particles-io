import Board from "./Board";
import SocketProvider from "./SocketProvider";

function App() {
  return (
    <SocketProvider>
      <Board mode="multiplayer"/>
    </SocketProvider>
  );
}

export default App;
