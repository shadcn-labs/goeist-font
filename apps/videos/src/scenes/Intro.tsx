import { useCurrentFrame } from "remotion";
import { Glyph, blurIn, firstFrame, reveal } from "../motion";
import { INTRO } from "../script";
import { SPECIMEN } from "../theme";
import { sec } from "../timeline";

const STAGGER = sec(0.07);
const RISE = sec(0.7);

/** Scene frames at which each letter is half revealed, where its note sounds. */
export const INTRO_CUES = INTRO.map((_, i) => i * STAGGER + firstFrame((frame) => reveal(frame, RISE) >= 0.5));

/** The first specimen rises in letter by letter. */
export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {INTRO.map(({ char, color }, i) => (
        <Glyph key={i} style={{ color, ...blurIn(reveal(frame - i * STAGGER, RISE), SPECIMEN.size) }}>
          {char}
        </Glyph>
      ))}
    </>
  );
};
