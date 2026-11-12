import { AbsoluteFill, Easing, interpolate, interpolateColors, useCurrentFrame } from "remotion";
import { Caption } from "./components/Caption";
import { Soundtrack } from "./components/Soundtrack";
import { Specimen } from "./components/Specimen";
import { Title } from "./components/Title";
import "./fonts";
import { CLAMP } from "./motion";
import { lines } from "./script";
import { INK, PAPER, SANS } from "./theme";
import { CUE, sec } from "./timeline";

export type LaunchProps = { glyphCount: number };

const ACCENT_FADE = sec(0.2);

export const Launch: React.FC<LaunchProps> = ({ glyphCount }) => {
  const frame = useCurrentFrame();
  const script = lines(glyphCount);
  // The caret and the title's dot take each caption's color as that caption starts.
  const accent = script.reduce(
    (color, line) =>
      frame < line.at ? color : interpolateColors(frame, [line.at, line.at + ACCENT_FADE], [color, line.accent]),
    script[0].accent,
  );
  const fade = interpolate(frame, [CUE.fade, CUE.fade + sec(0.6)], [0, 1], { easing: Easing.inOut(Easing.cubic), ...CLAMP });
  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, color: INK, fontFamily: SANS }}>
      <AbsoluteFill style={{ opacity: 1 - fade, filter: fade > 0 ? `blur(${fade * 16}px)` : undefined }}>
        <Title accent={accent} />
        <Caption lines={script} accent={accent} caret={frame < CUE.command || frame >= CUE.outro} />
        <Specimen accent={accent} />
      </AbsoluteFill>
      <Soundtrack lines={script} />
    </AbsoluteFill>
  );
};
