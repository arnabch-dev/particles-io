import { useEffect, useRef } from "react";
interface LoaderProps {
  text: string;
}
export default function Loader({ text }: LoaderProps) {
  return (
    <div className="min-h-screen flex justify-center items-center">
      <div className="flex flex-col justify-center items-center">
        <h4 className="text-xl">{text}</h4>
        <LoadingWithCanvas />
      </div>
    </div>
  );
}

const LoadingWithCanvas = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const direction = useRef(1);
  const xPos = useRef(50);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");

    const width = 200;
    const height = 30;
    canvas.width = width;
    canvas.height = height;

    function animate() {
      if (!context) return;
      context.fillStyle = "rgba(0,0,0,0.1)";
      context.fillRect(0, 0, width, height);

      // reversing at edge
      if (xPos.current > width - 10 || xPos.current < 10) {
        direction.current *= -1;
      }
      xPos.current += 2 * direction.current;

      context.beginPath();
      context.arc(xPos.current, height / 2, 5, 0, Math.PI * 2);
      // Neon blue
      context.fillStyle = "#00f6ff";
      context.fill();
      requestAnimationFrame(animate);
    }
    animate();
  }, []);

  return <canvas ref={canvasRef} className="mt-4 rounded bg-black" />;
};
