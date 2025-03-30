const speed = 5;
// x = x_end - x_start
// y = x_end - x_start
// basically affinity to the ending
export function getVelocity(y:number,x:number){
    const angle = Math.atan2(y,x);
      // v towards x= u cos(theta);u=1
      // v towards y= u sin(theta);u=1
      const velocity = {
        x: Math.cos(angle) * speed,
        y: Math.sin(angle) * speed,
      };

      return velocity
}