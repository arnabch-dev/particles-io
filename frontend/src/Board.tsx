import { useEffect, useRef, useState } from "react";
import { Circle, Projectile } from "./core";
const width = window.innerWidth;
const height = window.innerHeight;
const player = new Circle(width / 2, height / 2, 30, "blue");
export default function Board() {
  const [projectiles, setProjectiles] = useState<Projectile[]>([]);
  const players = [player];
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  function getContext() {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    return context;
  }

  // players and projectiles rendering
  useEffect(() => {
    const context = getContext()!;
    let animationId: number;
    const render = () => {
      context.clearRect(0, 0, width, height);
      players.forEach((player) => player.draw(context));
      projectiles.forEach((projectile) => {
        projectile.update();
        projectile.draw(context);
      });
      animationId = requestAnimationFrame(render);
    };
    render();
    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [projectiles, players]);

  useEffect(() => {
    function shoot(e: MouseEvent) {
      const { clientX, clientY } = e;
      const angle = Math.atan2(clientY - player.y, clientX - player.x);
      // v towards x= u cos(theta);u=1
      // v towards y= u sin(theta);u=1
      const speed = 5;
      const velocity = {
        x: Math.cos(angle) * speed,
        y: Math.sin(angle) * speed,
      };
      const projectile = new Projectile(player.x, player.y, 10, player.color, velocity);

      setProjectiles((prev) => {
        return [...prev, projectile];
      });
    }
    document.addEventListener("click", shoot);
    return () => {
      document.removeEventListener("click", shoot);
    };
  }, []);

  return <canvas ref={canvasRef} width={width} height={height} />;
}
