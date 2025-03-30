const startAngle = 0;
const endAngle = Math.PI * 2; // full circle
type Coodinate = {
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
    context.beginPath();
    context.arc(this.x, this.y, this.radius, startAngle, endAngle);
    context.fillStyle = this.color;
    context.fill();
  }
}

export class Projectile extends Circle {
  constructor(
    x: number,
    y: number,
    radius: number,
    color: string,
    public velocity: Coodinate
  ) {
    super(x, y, radius, color);
  }
  update() {
    this.x += this.velocity.x;
    this.y += this.velocity.y;
  }
}

export class Particle extends Circle {
  public alpha: number;
  constructor(
    x: number,
    y: number,
    radius: number,
    color: string,
    public velocity: Coodinate
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
