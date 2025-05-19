import { checkCollision, getVelocity, getVelocityFromAngle } from "../utils";
import {
  Circle,
  FocusBar,
  Particle,
  Projectile,
  type Coordinate,
} from "./core";
import { gsap } from "gsap";

export class GameEngine {
  private context: CanvasRenderingContext2D | null = null;
  private animationId: number | null = null;
  private intervalId: number | null = null;
  private players: Map<string, Circle>;
  private enemies: Projectile[] = [];
  private projectiles: Projectile[] = [];
  private projectilesWithIDs: Map<string, Projectile>;
  private particles: Particle[] = [];
  private focusBar: FocusBar;
  private onGameOver: () => void;
  public playing: boolean;
  constructor(
    // @ts-ignore
    private canvas: HTMLCanvasElement,
    onGameOver: () => void,
    public focus: number = 0,
    public gameMode: "single" | "multiplayer" = "single"
  ) {
    this.context = canvas.getContext("2d");
    this.focus = focus;
    this.focusBar = new FocusBar(0, 0, 100, 20, 20, this.focus);
    this.onGameOver = onGameOver;
    this.gameMode = gameMode;
    this.players = new Map();
    this.projectilesWithIDs = new Map();
    this.playing = true;
  }

  public addText(player:Circle,text:string){
    this.context?.fillText(text, player.x-3, player.y - 20);
  }

  public addPlayer(id: string, player: Circle) {
    const existing = this.getPlayer(id);
    if (existing) {
      // Tween from existing to the new position
      gsap.to(existing, {
        x: player.x,
        y: player.y,
        duration: 0.1,
        ease: "bounce.in",
      });
    } else {
      // Only add to the map if player is new
      this.players.set(id, player);
    }
  }

  spawnEnemies = () => {
    if (!this.playing) return;
    const player = this.getCurrentPlayer();
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
    // calculating velocity between two arbitary points and not between point and origin
    const endPoint = { x: player.x, y: player.y };
    const startPoint = { x, y };
    const velocity = getVelocity(startPoint, endPoint);
    const enemy = new Projectile(x, y, radius, color, velocity);

    this.enemies.push(enemy);
  };

  private updateGame = () => {
    if (!this.context) return;
    if (!this.playing) return;
    this.context.fillStyle = "rgba(0,0,0,0.1)";
    this.context.fillRect(0, 0, window.innerWidth, window.innerHeight);
    // this.context.fillStyle = "black";
    // this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);
    this.players.forEach((player) => {
      player.draw(this.context!);
    });

    const projectiles = this.getProjectiles();
    projectiles.forEach((projectileId) => {
      // we need update to avoid multiple draws
      // rather update the position of the previous draw and then draw
      const projectile = this.getProjectile(projectileId);
      if (projectile) projectile.draw(this.context!);
    });

    if (this.gameMode === "single") {
      this.projectiles.forEach((projectile) => {
        // we need update to avoid multiple draws
        // rather update the position of the previous draw and then draw
        projectile.update();
        projectile.draw(this.context!);
      });
      this.enemies.forEach((enemy, enemyIndex) => {
        enemy.update();
        enemy.draw(this.context!);
        const player = this.getCurrentPlayer();
        if (checkCollision(player, enemy)) {
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
    }

    this.particles.forEach((particle) => {
      particle.update();
      particle.draw(this.context!);
    });

    this.focusBar.draw(this.context);

    this.animationId = requestAnimationFrame(this.updateGame);
  };

  private getCurrentPlayer() {
    if (this.gameMode !== "single")
      throw new Error("this is for single player only");
    return Array.from(this.players.values())[0];
  }

  public getPlayer(id: string) {
    return this.players.get(id);
  }
  public getPlayers() {
    return Array.from(this.players.keys());
  }

  public removePlayer(id: string) {
    this.players.delete(id);
  }

  public getProjectiles() {
    if (this.gameMode !== "multiplayer")
      throw new Error("Not multiplayer mode");
    return Array.from(this.projectilesWithIDs.keys());
  }

  public getProjectile(id: string) {
    if (this.gameMode !== "multiplayer")
      throw new Error("Not multiplayer mode");
    return this.projectilesWithIDs.get(id);
  }

  public removeProjectile(id: string) {
    if (this.gameMode !== "multiplayer")
      throw new Error("Not multiplayer mode");
    this.projectilesWithIDs.delete(id);
  }

  public start = () => {
    this.animationId = requestAnimationFrame(this.updateGame);
    if (this.gameMode === "single")
      // @ts-ignore
      this.intervalId = setInterval(this.spawnEnemies, 1000);
  };

  public stop = () => {
    this.playing = false;
    if (this.animationId) cancelAnimationFrame(this.animationId);
    if (this.intervalId && this.gameMode === "single")
      clearInterval(this.intervalId);
  };

  public addProjectile = (
    currentPos: Coordinate,
    targetPos: Coordinate,
    id: string,
    force?: number,
    applyGravity?: boolean
  ) => {
    const velocity = getVelocity(currentPos, targetPos, 4);
    const player = this.players.get(id)!;
    this.projectiles.push(
      new Projectile(
        currentPos.x,
        currentPos.y,
        5,
        player.color,
        velocity,
        force,
        applyGravity
      )
    );
  };

  public addProjectileWithIdAndAngle = (
    currentPos: Coordinate,
    projectileId: string,
    angle: number,
    color: string,
    force?: number,
    applyGravity?: boolean
  ) => {
    if (this.gameMode !== "multiplayer")
      throw new Error("Not multiplayer mode");
    const velocity = getVelocityFromAngle(angle, 4);
    const projectile = this.getProjectile(projectileId);
    if (projectile) {
      projectile.x = currentPos.x;
      projectile.y = currentPos.y;
    } else {
      this.projectilesWithIDs.set(
        projectileId,
        new Projectile(
          currentPos.x,
          currentPos.y,
          5,
          color,
          velocity,
          force,
          applyGravity
        )
      );
    }
  };

  public updateFocusBar(newFocusValue: number) {
    if (!this.context) return;
    console.log({ newFocusValue });
    this.focusBar.draw(this.context);
    this.focusBar.update(newFocusValue);
  }

  public addParticles(x:number,y:number,radius:number,color:string){
    this.particles.push(
      ...Array.from({ length: radius }).map(() => {
        const radius = Math.random() * 4;
        return new Particle(x, y, radius, color, {
          x: (Math.random() - 0.5) * radius * 2,
          y: (Math.random() - 0.5) * radius * 2,
        });
      })
    );
  }

}
