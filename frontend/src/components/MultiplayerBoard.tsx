import { useEffect, useRef, useState, useCallback } from "react";
import { GameEngine } from "../core/gameEngine";
import { useFocus } from "../hooks/Focus";
import { Circle } from "../core/core";
import { useSocket } from "../SocketProvider";

export default function MultiplayerBoard() {
  // All hooks must be called before any conditional returns
  const { player: playerDetails, isConnected, socket, playerId } = useSocket();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [gameEngine, setGameEngine] = useState<GameEngine | null>(null);

  // Stable reference to handle shooting
  const handleShoot = useCallback(
    (e: MouseEvent, focusValue: number) => {
      if (!playerDetails) return;
      const player = gameEngine?.getPlayer(playerId);
      if (!player) return;

      const currentPos = { x: player.x, y: player.y };
      const targetPos = { x: e.clientX, y: e.clientY };

      gameEngine?.addProjectile(
        currentPos,
        targetPos,
        playerId,
        focusValue,
        true
      );
    },
    [gameEngine, playerDetails, isConnected, playerDetails]
  );

  // Use custom hook
  const { focus } = useFocus({
    onFocusRelease: handleShoot,
    onFocusChange: (e, focusValue) => {
      gameEngine?.updateFocusBar(focusValue);
    },
  });

  useEffect(() => {
    // paint when the player disconnects
    if (!playerDetails) return;
    if (!canvasRef.current) return;

    const engine = new GameEngine(
      canvasRef.current,
      () => engine.stop(),
      0,
      "multiplayer"
    );
    setGameEngine(engine);
    engine.start();

    return () => engine.stop();
  }, [playerId, isConnected]);

  useEffect(() => {
    if (playerDetails && gameEngine) {
      playerDetails.forEach((player) => {
        const newPlayer = new Circle(
          player.position.x,
          player.position.y,
          30,
          player.color
        );
        gameEngine.addPlayer(player.player_id, newPlayer);
      });
      const playerIds = gameEngine.getPlayers();
      const currentPlayers = new Set(
        playerDetails.map((player) => player.player_id)
      );
      playerIds.forEach((playerId) => {
        if (!currentPlayers.has(playerId)) gameEngine.removePlayer(playerId);
      });
    }
  }, [playerDetails, gameEngine, isConnected, playerDetails]);

  useEffect(() => {
    if (!playerId || !gameEngine || !socket) return;
    if (!canvasRef.current) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      const player = gameEngine.getPlayer(playerId)!;
      switch (event.key.toLowerCase()) {
        case "w":
          socket.emit("move", "up");
          break;
        case "a":
          socket.emit("move", "right");
          break;
        case "s":
          socket.emit("move", "down");
          break;
        case "d":
          socket.emit("move", "left");
          break;
        default:
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [playerDetails, isConnected, gameEngine]);

  // Move conditional return after all hook calls
  if (!playerDetails) return <h1>Loading.....</h1>;
  return (
    <canvas
      ref={canvasRef}
      width={window.innerWidth}
      height={window.innerHeight}
    />
  );
}
