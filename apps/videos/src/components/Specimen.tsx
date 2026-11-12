import { Sequence } from "remotion";
import { Command } from "../scenes/Command";
import { Intro } from "../scenes/Intro";
import { Italic } from "../scenes/Italic";
import { Shuffle } from "../scenes/Shuffle";
import { Weight } from "../scenes/Weight";
import { MARGIN, SPECIMEN } from "../theme";
import { CUE } from "../timeline";

/** The big bottom row. Each scene owns it from its cue until the next one starts. */
export const Specimen: React.FC<{ accent: string }> = ({ accent }) => (
  <div
    style={{
      position: "absolute",
      left: MARGIN,
      top: SPECIMEN.top,
      fontSize: SPECIMEN.size,
      fontWeight: SPECIMEN.weight,
      lineHeight: 1,
      whiteSpace: "pre",
    }}
  >
    <Sequence name="Intro" from={CUE.intro} durationInFrames={CUE.shuffle - CUE.intro} layout="none">
      <Intro />
    </Sequence>
    <Sequence name="Glyphs" from={CUE.shuffle} durationInFrames={CUE.weight - CUE.shuffle} layout="none">
      <Shuffle />
    </Sequence>
    <Sequence name="Variable" from={CUE.weight} durationInFrames={CUE.lean - CUE.weight} layout="none">
      <Weight />
    </Sequence>
    <Sequence name="Italic" from={CUE.lean} durationInFrames={CUE.command - CUE.lean} layout="none">
      <Italic />
    </Sequence>
    <Sequence name="Mono" from={CUE.command} layout="none">
      <Command accent={accent} />
    </Sequence>
  </div>
);
