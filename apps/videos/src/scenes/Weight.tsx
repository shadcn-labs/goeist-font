import { Easing, interpolate, useCurrentFrame } from "remotion";
import { CLAMP, Glyph } from "../motion";
import { WORD } from "../script";
import { SPECIMEN } from "../theme";
import { sec } from "../timeline";

const STAGGER = 4;
// Thin, a short hold, then all the way to Black.
const KEYS = [0, sec(0.9), sec(1.5), sec(2.5)];
const WEIGHTS = [SPECIMEN.weight, 100, 100, SPECIMEN.heavy];
const CENTRE = Math.floor(WORD.length / 2) * STAGGER;

// Scene frames of the wave's centre letter: fastest on the way to Thin (eased in and out, so halfway),
// and arriving at Black.
export const THIN_CUE = KEYS[1] / 2 + CENTRE;
export const BLACK_CUE = KEYS[3] + CENTRE;

/** A wave across the word, down the wght axis and back up. */
export const Weight: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {WORD.map(({ char, color }, i) => {
        const weight = interpolate(frame - i * STAGGER, KEYS, WEIGHTS, { easing: Easing.inOut(Easing.cubic), ...CLAMP });
        return (
          <Glyph key={i} style={{ color, fontWeight: weight }}>
            {char}
          </Glyph>
        );
      })}
    </>
  );
};
