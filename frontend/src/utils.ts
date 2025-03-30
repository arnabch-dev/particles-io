// x = x_end - x_start
// y = x_end - x_start
// basically affinity to the ending
export function getVelocity(y: number, x: number ,speed:number=6) {
  const angle = Math.atan2(y, x);
  // v towards x= u cos(theta);u=1
  // v towards y= u sin(theta);u=1
  const velocity = {
    x: Math.cos(angle) * speed,
    y: Math.sin(angle) * speed,
  };

  return velocity;
}

type GameElement = { x: number; y: number; radius: number };
export function checkCollision(obj1: GameElement, obj2: GameElement) {
  const dist = Math.hypot(obj1.x - obj2.x, obj1.y - obj2.y);
  return dist - obj1.radius - obj2.radius < 1;
}
