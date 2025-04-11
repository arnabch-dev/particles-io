import { useEffect, useRef, useState, useCallback } from "react";
import { GameEngine } from "../core/gameEngine";
import { useFocus } from "../hooks/Focus";
import { Circle } from "../core/core";
import { useSocket } from "../SocketProvider";
import { getAngle } from "../utils";
const SPEED = 30;
export default function MultiplayerBoard() {
  // All hooks must be called before any conditional returns
  const {
    player: playerDetails,
    projectiles,
    isConnected,
    socket,
    playerId,
    emitMovement,
    emitShoot,
  } = useSocket();
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
      const angle = getAngle(currentPos, targetPos);
      emitShoot({ angle, position: currentPos });
    },
    [gameEngine, playerDetails, isConnected, projectiles]
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
          10,
          player.color
        );
        gameEngine.focus = focus;
        gameEngine.addPlayer(player.player_id, newPlayer);
      });
      const playerIds = gameEngine.getPlayers();
      const currentPlayers = new Set(
        playerDetails.map((player) => player.player_id)
      );
      playerIds.forEach((playerId) => {
        if (!currentPlayers.has(playerId)) gameEngine.removePlayer(playerId);
      });
      projectiles.forEach(({ position, angle, color }) => {
        gameEngine?.addProjectileWithAngle(
          position,
          playerId,
          angle,
          color,
          focus,
          true
        );
      });
    }
  }, [playerDetails, gameEngine, isConnected]);

  useEffect(() => {
    if (!playerId || !gameEngine || !socket) return;
    if (!canvasRef.current) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      const player = gameEngine.getPlayer(playerId)!;
      switch (event.key.toLowerCase()) {
        // we are not using interpolation for the moving the player
        // a kind of teleportation kind of effect if the frontend and backend mismatch
        case "w":
          player.y -= SPEED;
          emitMovement("up");
          break;
        case "a":
          player.x -= SPEED;
          emitMovement("left");
          break;
        case "s":
          player.y += SPEED;
          emitMovement("down");
          break;
        case "d":
          player.x += SPEED;
          emitMovement("right");
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
