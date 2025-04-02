import { useEffect, useRef, useState, useCallback } from "react";
import { GameEngine } from "../core/gameEngine";
import { useFocus } from "../hooks/Focus";

export default function SingleBoard() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [gameEngine, setGameEngine] = useState<GameEngine | null>(null);

  // Stable reference to handle shooting
  const handleShoot = useCallback(
    (e: MouseEvent, focusValue: number) => {
      gameEngine?.addProjectile(e.clientX, e.clientY,focusValue,true);
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

    const engine = new GameEngine(canvasRef.current, "blue", () => {});
    setGameEngine(engine);
    engine.start();

    return () => engine.stop();
  }, []);
  

  return <canvas ref={canvasRef} width={window.innerWidth} height={window.innerHeight} />;
}
