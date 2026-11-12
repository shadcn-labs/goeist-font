import { BLINK, CARET_IDLE } from "../timeline";

/** Solid while text changes (`idleSince` null); afterwards it blinks, then hides after CARET_IDLE. */
export const caretOn = (frame: number, idleSince: number | null) => {
  if (idleSince === null) return true;
  const idle = frame - idleSince;
  return idle < CARET_IDLE && Math.floor(idle / BLINK) % 2 === 0;
};

/**
 * A rounded caret sized in em of the surrounding text. `drop` is how far it reaches below the
 * baseline; keep `height - drop` under 0.855em so it never grows the line box.
 */
export const Caret: React.FC<{ color: string; visible: boolean; width?: number; height?: number; drop?: number }> = ({
  color,
  visible,
  width = 0.06,
  height = 1.06,
  drop = 0.21,
}) => (
  <span
    style={{
      display: "inline-block",
      width: `${width}em`,
      height: `${height}em`,
      marginLeft: `${width}em`,
      borderRadius: `${width / 2}em`,
      verticalAlign: `${-drop}em`,
      backgroundColor: color,
      opacity: visible ? 1 : 0,
    }}
  />
);
