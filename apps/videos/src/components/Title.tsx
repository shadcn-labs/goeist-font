import { spring, useCurrentFrame } from "remotion";
import { Glyph, blurIn, firstFrame, reveal } from "../motion";
import { MARGIN, TITLE } from "../theme";
import { CUE, FPS, sec } from "../timeline";

const NAME = "Goeist";
const STAGGER = 4;
const DOT_SPRING = { damping: 10, stiffness: 170, mass: 0.7 };
const dotScale = (frame: number) => spring({ frame: frame - CUE.dot, fps: FPS, config: DOT_SPRING });

/** The frame the period is half grown: where its pop sounds. */
export const DOT_CUE = firstFrame((frame) => dotScale(frame) >= 0.5);

/** The wordmark: letters rise out of a blur, then the period pops in, tinted with the caption accent. */
export const Title: React.FC<{ accent: string }> = ({ accent }) => {
  const frame = useCurrentFrame();
  const dot = dotScale(frame);
  return (
    <div
      style={{
        position: "absolute",
        left: MARGIN,
        top: TITLE.top,
        fontSize: TITLE.size,
        fontWeight: 700,
        lineHeight: 1,
        letterSpacing: "-0.02em",
        whiteSpace: "pre",
      }}
    >
      {[...NAME].map((char, i) => (
        <Glyph key={i} style={blurIn(reveal(frame - CUE.title - i * STAGGER, sec(0.6)), TITLE.size)}>
          {char}
        </Glyph>
      ))}
      {/* Scales around the period itself, which sits just above the 85.5% baseline. */}
      <Glyph style={{ color: accent, transform: `scale(${dot})`, transformOrigin: "50% 78%" }}>.</Glyph>
    </div>
  );
};
