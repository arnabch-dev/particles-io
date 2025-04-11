const startAngle = 0;
const endAngle = Math.PI * 2; // full circle
const gravity = 0.1;
export type Coordinate = {
  x: number;
  y: number;
};
export class Circle {
  constructor(
    public x: number,
    public y: number,
    public radius: number,
    public color: string
  ) {}
  draw(context: CanvasRenderingContext2D) {
    context.save()
    context.shadowColor = this.color
    context.shadowBlur = this.radius
    context.beginPath();
    context.arc(this.x, this.y, this.radius, startAngle, endAngle);
    context.fillStyle = this.color;
    context.fill();
    context.restore()
  }
}

export class Projectile extends Circle {
  constructor(
    x: number,
    y: number,
    radius: number,
    color: string,
    public velocity: Coordinate,
    public force: number = 0,
    public applyGravity: boolean = false
  ) {
    super(x, y, radius, color);
  }
  
  update() {
    this.x += this.velocity.x;
    this.y += this.velocity.y;
    
    if (this.applyGravity) {
      // Apply gravity, partially counteracted by force
      // This ensures the trajectory is curved, not straight
      const gravityEffect = Math.max(gravity - this.force * 0.08, 0.016);
      this.velocity.y += gravityEffect;
    }
  }
}

export class Particle extends Circle {
  public alpha: number;
  constructor(
    x: number,
    y: number,
    radius: number,
    color: string,
    public velocity: Coordinate
  ) {
    super(x, y, radius, color);
    this.alpha = 1;
  }
  update() {
    const friction = 0.99;
    this.velocity.x *= friction;
    this.velocity.y *= friction;
    this.x += this.velocity.x;
    this.y += this.velocity.y;
    this.alpha -= 0.01;
  }
  draw(context: CanvasRenderingContext2D) {
    if (this.alpha <= 0) return; // Prevents flickering before removal
    context.save(); // Save the current state
    context.globalAlpha = this.alpha;
    context.beginPath();
    context.arc(this.x, this.y, this.radius, startAngle, endAngle);
    context.fillStyle = this.color;
    context.fill();
    context.restore(); // Restore the previous state
  }
}


export class FocusBar {
  constructor(
    public x: number,
    public y: number,
    public width: number,
    public height: number,
    public maxHealth: number,
    public currentHealth: number,
    public backgroundColor: string = "#555",
    public foregroundColor: string = "#0f0"
  ) {}

  draw(context: CanvasRenderingContext2D) {
    context.fillStyle = this.backgroundColor;
    context.fillRect(this.x, this.y, this.width, this.height);

    const healthWidth = (this.currentHealth / this.maxHealth) * this.width;

    context.fillStyle = this.foregroundColor;
    context.fillRect(this.x, this.y, healthWidth, this.height);
  }

  update(newHealth: number) {
    this.currentHealth = Math.max(0, Math.min(newHealth, this.maxHealth));
  }
}