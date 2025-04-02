import { useEffect, useRef, useState } from "react";
import { Circle, FocusBar, Particle, Projectile } from "./core/core";
import { checkCollision, getVelocity } from "./utils";
import { gsap } from "gsap";
import { useSocket } from "./SocketProvider";
import SingleBoard from "./components/SingleBoard";

interface BoardProps {
  mode: "single" | "multiplayer";
}

export default function Board({ mode }: BoardProps) {
  return (
    <div>
      <SingleBoard />
    </div>
  );
}
