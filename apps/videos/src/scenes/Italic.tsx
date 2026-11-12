import { spring, useCurrentFrame } from "remotion";
import { Glyph, firstFrame } from "../motion";
import { WORD } from "../script";
import { BASELINE, SPECIMEN } from "../theme";
import { FPS } from "../timeline";

const STAGGER = 4;
const ANGLE = 12; // post.italicAngle of Goeist Italic
const leanAt = (frame: number) => spring({ frame, fps: FPS, config: { damping: 13, stiffness: 140 } });

/** Scene frame where the centre letter leans fastest: the swish peaks here. */
export const LEAN_CUE =
  Math.floor(WORD.length / 2) * STAGGER +
  firstFrame((frame) => leanAt(frame + 1) - leanAt(frame) < leanAt(frame) - leanAt(frame - 1));

/**
 * Each letter leans into Goeist Italic. The upright glyph is skewed up to halfway, then the true
 * italic takes over with the remaining skew unwinding, so the slant never jumps.
 */
export const Italic: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {WORD.map(({ char, color }, i) => {
        const lean = leanAt(frame - i * STAGGER);
        const italic = lean >= 0.5;
        const skew = italic ? ANGLE * (1 - lean) : -ANGLE * lean;
        return (
          <Glyph
            key={i}
            style={{
              color,
              fontWeight: SPECIMEN.heavy,
              fontStyle: italic ? "italic" : undefined,
              transform: `skewX(${skew}deg)`,
              transformOrigin: `50% ${BASELINE}`,
            }}
          >
            {char}
          </Glyph>
        );
      })}
    </>
  );
};
