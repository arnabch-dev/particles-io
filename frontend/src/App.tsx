import { useEffect, useRef } from "react";
import Board from "./Board";

function App() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  function drawGrowingRectangle(context: CanvasRenderingContext2D, frameCount: number) {
    context.clearRect(0, 0, 500, 500);
    context.fillStyle = "red";
    context.beginPath();

    const scaleFactor = Math.abs(Math.sin(frameCount * 0.05));
    const width = 200 * scaleFactor;
    const height = 200 * scaleFactor;

    context.fillRect(0, 0, width, height);
  }

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    let frame = 0;
    let animationFrameId: number;

    const render = () => {
      frame++;
      drawGrowingRectangle(context, frame);
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [drawGrowingRectangle]);

  return <><Board/></>;
}

export default App;
