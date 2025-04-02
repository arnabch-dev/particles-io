import { checkCollision, getVelocity } from "../utils";
import { Circle, FocusBar, Particle, Projectile } from "./core";
import { gsap } from "gsap";
const radius = 30
export class GameEngine {
  private context: CanvasRenderingContext2D | null = null;
  private animationId: number | null = null;
  private intervalId: number | null = null;
  private player: Circle;
  private enemies: Projectile[] = [];
  private projectiles: Projectile[] = [];
  private particles: Particle[] = [];
  private focusBar: FocusBar;
  private onGameOver: () => void;

  constructor(
    private canvas: HTMLCanvasElement,
    playerColor: string,
    onGameOver: () => void,
    public focus: number = 0
  ) {
    this.context = canvas.getContext("2d");
    this.player = new Circle(
      window.innerWidth / 2,
      window.innerHeight / 2,
      radius,
      playerColor
    );
    this.focus = focus;
    this.focusBar = new FocusBar(0, 0, 100, 20, 20, this.focus);
    this.onGameOver = onGameOver;
  }

  spawnEnemies = () => {
    const radius = Math.random() * 20 + 10;
    const edge = Math.floor(Math.random() * 4);
    let x, y;

    if (edge === 0) (x = -radius), (y = Math.random() * window.innerHeight);
    else if (edge === 1)
      (x = window.innerWidth + radius),
        (y = Math.random() * window.innerHeight);
    else if (edge === 2) (x = Math.random() * window.innerWidth), (y = -radius);
    else
      (x = Math.random() * window.innerWidth),
        (y = window.innerHeight + radius);

    const hue = Math.random() * 360;
    const color = `hsl(${hue},50%,50%)`;
    const velocity = getVelocity(this.player.y - y, this.player.x - x);
    const enemy = new Projectile(x, y, radius, color, velocity);

    this.enemies.push(enemy);
  };

  private updateGame = () => {
    if (!this.context) return;

    this.context.fillStyle = "rgba(0,0,0,0.1)";
    this.context.fillRect(0, 0, window.innerWidth, window.innerHeight);
    this.player.draw(this.context);

    this.projectiles.forEach((projectile) => {
      projectile.update();
      projectile.draw(this.context!);
    });

    this.enemies.forEach((enemy, enemyIndex) => {
      enemy.update();
      enemy.draw(this.context!);

      if (checkCollision(this.player, enemy)) {
        this.stop();
        this.onGameOver();
      }

      this.projectiles.forEach((projectile, projectileIndex) => {
        if (checkCollision(projectile, enemy)) {
          setTimeout(() => {
            this.projectiles = this.projectiles.filter(
              (_, i) => i !== projectileIndex
            );
            const newRadius = enemy.radius - 10;

            if (newRadius < 15) {
              this.enemies = this.enemies.filter((_, i) => i !== enemyIndex);
            } else {
              gsap.to(enemy, {
                radius: newRadius,
                duration: 0.3,
                ease: "expo.out(1, 0.3)",
              });
            }

            this.particles.push(
              ...Array.from({ length: enemy.radius }).map(() => {
                const radius = Math.random() * 4;
                return new Particle(enemy.x, enemy.y, radius, enemy.color, {
                  x: (Math.random() - 0.5) * radius * 2,
                  y: (Math.random() - 0.5) * radius * 2,
                });
              })
            );
          }, 0);
        }
      });
    });

    this.particles.forEach((particle) => {
      particle.update();
      particle.draw(this.context!);
    });

    this.focusBar.draw(this.context);

    this.animationId = requestAnimationFrame(this.updateGame);
  };

  public start = () => {
    this.animationId = requestAnimationFrame(this.updateGame);
    this.intervalId = setInterval(this.spawnEnemies, 1000);
  };

  public stop = () => {
    if (this.animationId) cancelAnimationFrame(this.animationId);
    if (this.intervalId) clearInterval(this.intervalId);
  };

  public addProjectile = (x: number, y: number,force?:number,applyGravity?:boolean) => {
    const velocity = getVelocity(y - this.player.y, x - this.player.x, 4);
    this.projectiles.push(
      new Projectile(
        this.player.x,
        this.player.y,
        5,
        this.player.color,
        velocity,
        force,
        applyGravity
      )
    );
  };

  public updateFocusBar(newFocusValue:number) {
    if (!this.context) return;
    this.focusBar.draw(this.context);
    this.focusBar.update(newFocusValue);
  }
  public addTrajectoryVisualiser(targetX: number, targetY: number, force?: number, applyGravity?: boolean) {
    return    
  }
}
