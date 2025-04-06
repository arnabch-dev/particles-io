import { useEffect, useRef, useState, useCallback } from "react";
import { GameEngine } from "../core/gameEngine";
import { useFocus } from "../hooks/Focus";
import { Circle } from "../core/core";
const id = "local"
export default function SingleBoard() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [gameEngine, setGameEngine] = useState<GameEngine | null>(null);
  const player = new Circle(
    window.innerWidth / 2,
    window.innerHeight / 2,
    30,
    "red"
  );
  gameEngine?.addPlayer(id,player)
  // Stable reference to handle shooting
  const handleShoot = useCallback(
    (e: MouseEvent, focusValue: number) => {
      const player = gameEngine?.getPlayer(id);
      if (!player) return;
      
      const currentPos = { x: player.x, y: player.y };
      const targetPos = { x: e.clientX, y: e.clientY };
      
      gameEngine?.addProjectile(currentPos, targetPos, id,focusValue, true);
    },
    [gameEngine]
  );

  // Using useFocus hook
  const { focus } = useFocus({
    onFocusRelease: handleShoot,
    onFocusChange:(e,focusValue)=>{
        gameEngine?.updateFocusBar(focusValue)
    }
  });

  useEffect(() => {
    if (!canvasRef.current) return;

    const engine = new GameEngine(canvasRef.current, () => engine.stop(),0,"single");
    setGameEngine(engine);
    engine.start();

    return () => engine.stop();
  }, []);
  

  return <canvas ref={canvasRef} width={window.innerWidth} height={window.innerHeight} />;
}
