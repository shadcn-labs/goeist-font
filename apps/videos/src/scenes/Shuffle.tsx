import { interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Glyph } from "../motion";
import { INTRO, WORD } from "../script";
import { PALETTE } from "../theme";
import { sec } from "../timeline";

// Every character here is in Goeist's cmap; anything else would fall back to a system font.
const POOL = [
  ..."ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
  ..."@#&%$?!*+=<>{}[]()/~ßÆØÐþ€£¥→↗①❷☺▲∞≠",
];

const TICK = 5; // frames each random glyph stays up
const START_STAGGER = 3;
const SETTLE = sec(1.5); // first slot lands on WORD
const SETTLE_STAGGER = 6;
const SLOTS = Math.max(INTRO.length, WORD.length);

/** Scene frames at which each slot stops shuffling, left to right. */
export const SETTLE_CUES = Array.from({ length: SLOTS }, (_, i) => SETTLE + i * SETTLE_STAGGER);

/** Every slot cycles through random glyphs and colors, then they land on WORD from left to right. */
export const Shuffle: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {SETTLE_CUES.map((settleAt, i) => {
        if (frame >= settleAt) {
          const letter = WORD[i];
          if (!letter) return null;
          const pop = spring({ frame: frame - settleAt, fps, config: { damping: 11, stiffness: 220 } });
          return (
            <Glyph key={i} style={{ color: letter.color, transform: `scale(${interpolate(pop, [0, 1], [0.8, 1])})` }}>
              {letter.char}
            </Glyph>
          );
        }
        const startAt = i * START_STAGGER;
        if (frame < startAt) {
          const letter = INTRO[i];
          return letter ? (
            <Glyph key={i} style={{ color: letter.color }}>
              {letter.char}
            </Glyph>
          ) : null;
        }
        const tick = Math.floor((frame - startAt) / TICK);
        const char = POOL[Math.floor(random(`glyph-${i}-${tick}`) * POOL.length)];
        const color = PALETTE[Math.floor(random(`color-${i}-${tick}`) * PALETTE.length)];
        return (
          <Glyph key={i} style={{ color }}>
            {char}
          </Glyph>
        );
      })}
    </>
  );
};
