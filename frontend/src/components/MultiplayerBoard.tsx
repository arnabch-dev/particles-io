import { useEffect, useRef, useState, useCallback } from "react";
import { GameEngine } from "../core/gameEngine";
import { useFocus } from "../hooks/Focus";
import { Circle } from "../core/core";
import { useSocket } from "../SocketProvider";
import { getAngle } from "../utils";
import gsap from "gsap";

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
    resetProjetiles,
  } = useSocket();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [gameEngine, setGameEngine] = useState<GameEngine | null>(null);

  // Stable reference to handle shooting
  const handleShoot = useCallback(
    (e: MouseEvent, focusValue: number) => {
      console.log("shooting");
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

  // for adding removing players and projetiles from the screen
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

      projectiles.forEach(({ position, angle, color, projectile_id }) => {
        gameEngine?.addProjectileWithIdAndAngle(
          position,
          projectile_id,
          angle,
          color,
          focus,
          true
        );
      });
      const projectileIds = gameEngine.getProjectiles();
      const currentProjectiles = new Set(projectiles.map(projectile=>projectile.projectile_id))
      projectileIds.forEach(projectileId=>{
        if(!currentProjectiles.has(projectileId)) gameEngine.removeProjectile(projectileId)
      })
    }
  }, [playerDetails, gameEngine, isConnected]);

  useEffect(() => {
    if (!playerId || !gameEngine || !socket) return;
    if (!canvasRef.current) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      const player = gameEngine.getPlayer(playerId)!;
      if (!player) return;

      const moveDistance = SPEED;
      let dx = 0,
        dy = 0;

      switch (event.key.toLowerCase()) {
        case "w":
          dy = -moveDistance;
          emitMovement("up");
          break;
        case "a":
          dx = -moveDistance;
          emitMovement("left");
          break;
        case "s":
          dy = moveDistance;
          emitMovement("down");
          break;
        case "d":
          dx = moveDistance;
          emitMovement("right");
          break;
        default:
          return;
      }

      gsap.to(player, {
        x: player.x + dx,
        y: player.y + dy,
        duration: 0.1,
        ease: "bounce.in",
      });
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
