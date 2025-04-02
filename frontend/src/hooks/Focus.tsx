import { useEffect, useState } from "react";

interface FocusProps {
  onFocusRelease?: (e: MouseEvent, focusValue: number) => void;
  onFocusChange?: (e: MouseEvent, focusValue: number) => void;
}
export function useFocus({ onFocusRelease, onFocusChange }: FocusProps) {
  const [focus, setFocus] = useState<number>(0);

  useEffect(() => {
    let intervalId:number;
    function chargeFocus(e: MouseEvent) {
      if (intervalId) clearInterval(intervalId);
      intervalId = window.setInterval(() => {
        setFocus((prev) => {
          const newFocus = Math.min(prev + 0.5, 20);
          if (onFocusChange) onFocusChange(e, newFocus);
          return newFocus;
        });
      }, 100);
    }

    function releaseFocus(e: MouseEvent) {
      if (intervalId) {
        clearInterval(intervalId);
      }
      setFocus((prevFocus) => {
        onFocusRelease?.(e, prevFocus);
        // for ever action reduce by 1 like a powerup
        const curFocus = Math.max(0,prevFocus-1)
        if (onFocusChange) onFocusChange(e, curFocus);
        return curFocus;
      });
    }

    document.addEventListener("mousedown", chargeFocus);
    document.addEventListener("mouseup", releaseFocus);

    return () => {
      document.removeEventListener("mousedown", chargeFocus);
      document.removeEventListener("mouseup", releaseFocus);
      if (intervalId) clearInterval(intervalId);
    };
  }, [onFocusRelease]);
  return { focus };
}
