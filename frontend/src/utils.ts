import { type Coordinate } from "./core/core";
export function getAngle(start: Coordinate, end: Coordinate) {
  const x = end.x - start.x;
  const y = end.y - start.y;
  return Math.atan2(y, x);
}
// x = x_end - x_start
// y = x_end - x_start
// basically affinity to the ending
export function getVelocity(
  start: Coordinate,
  end: Coordinate,
  speed: number = 1
) {
  // v towards x= u cos(theta);u=1
  // v towards y= u sin(theta);u=1
  const angle = getAngle(start, end);
  const velocity = {
    x: Math.cos(angle) * speed,
    y: Math.sin(angle) * speed,
  };

  return velocity;
}

export function getVelocityFromAngle(
  angle: number,
  speed: number = 1
) {
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
