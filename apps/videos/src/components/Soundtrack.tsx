import { Sequence, random } from "remotion";
import { COMMAND_KEYS } from "../scenes/Command";
import { INTRO_CUES } from "../scenes/Intro";
import { LEAN_CUE } from "../scenes/Italic";
import { SETTLE_CUES } from "../scenes/Shuffle";
import { BLACK_CUE, THIN_CUE } from "../scenes/Weight";
import { type Line, WORD } from "../script";
import { SFX } from "../sfx";
import { CUE } from "../timeline";
import { type Keystroke, keystrokes } from "../typewriter";
import { Sfx } from "./Sfx";
import { DOT_CUE } from "./Title";

// The caption types 30 characters a second, faster than any typist, so keys sound at most every
// KEY_GAP frames (12 a second) and erasing is a sparser, softer patter.
const KEY_GAP = 5;
const ERASE_GAP = 6;

/** The keystrokes worth hearing: at most one per gap, so a fast run reads as typing rather than a buzz. */
const audible = (strokes: Keystroke[]) => {
  let last = -Infinity;
  return strokes.filter(({ frame, erase }) => {
    if (frame - last < (erase ? ERASE_GAP : KEY_GAP)) return false;
    last = frame;
    return true;
  });
};

/** One keyboard for the whole film: takes rotate, never twice in a row, with ±1.5 dB of hand variation. */
const Keys: React.FC<{ strokes: Keystroke[]; from: number; gain: number; seed: string }> = ({
  strokes,
  from,
  gain,
  seed,
}) => (
  <>
    {strokes.map(({ frame, space, erase }, i) => (
      <Sfx
        key={i}
        sound={space ? SFX.space : SFX.keys[(i * 5) % SFX.keys.length]}
        at={from + frame}
        gain={gain + (erase ? -4 : 0) + (random(`${seed}-${i}`) - 0.5) * 3}
      />
    ))}
  </>
);

// The intro letters climb C major pentatonic, C5 D5 E5 G5 A5 C6, from three marimba notes resampled
// by at most three semitones. The slot ticks climb the same scale.
const RUN = [
  { sound: SFX.marimba.c5, semitones: 0 },
  { sound: SFX.marimba.c5, semitones: 2 },
  { sound: SFX.marimba.g5, semitones: -3 },
  { sound: SFX.marimba.g5, semitones: 0 },
  { sound: SFX.marimba.b5, semitones: -2 },
  { sound: SFX.marimba.b5, semitones: 1 },
];
const PENTATONIC = [0, 2, 4, 7, 9, 12, 14];

/** Every sound in the film, each on the frame of what causes it. */
export const Soundtrack: React.FC<{ lines: Line[] }> = ({ lines }) => {
  const strokes = keystrokes(lines);
  const lastKey = strokes[strokes.length - 1].frame;
  return (
    <>
      <Sequence name="Sound: title" layout="none">
        {/* A reversed breath swells into the period's pop. */}
        <Sfx sound={SFX.breath} at={CUE.dot} gain={-15} />
        <Sfx sound={SFX.pop} at={DOT_CUE} gain={-4} />
      </Sequence>
      <Sequence name="Sound: caption keys" layout="none">
        <Keys strokes={audible(strokes)} from={0} gain={-7} seed="caption" />
      </Sequence>
      <Sequence name="Sound: intro" layout="none">
        {INTRO_CUES.map((cue, i) => (
          <Sfx key={i} {...RUN[i % RUN.length]} at={CUE.intro + cue} gain={-19} />
        ))}
      </Sequence>
      <Sequence name="Sound: glyphs" layout="none">
        {/* A card riffle starts with the shuffle and thins out as the slots lock, each with a wood tick. */}
        <Sfx sound={SFX.riffle} at={CUE.shuffle} gain={-9} />
        {SETTLE_CUES.slice(0, WORD.length).map((cue, i) => (
          <Sfx key={i} sound={SFX.wood} at={CUE.shuffle + cue} semitones={PENTATONIC[i % PENTATONIC.length]} gain={-11} />
        ))}
      </Sequence>
      <Sequence name="Sound: variable" layout="none">
        {/* A swoosh down to Thin; a reversed crash pulls up into Black, which lands on a kick and a low C. */}
        <Sfx sound={SFX.swoosh} at={CUE.weight + THIN_CUE} gain={-11} />
        <Sfx sound={SFX.rise} at={CUE.weight + BLACK_CUE - 3} gain={-14} />
        <Sfx sound={SFX.kick} at={CUE.weight + BLACK_CUE} gain={-4.5} />
        <Sfx sound={SFX.marimba.c3} at={CUE.weight + BLACK_CUE} gain={-14} />
      </Sequence>
      <Sequence name="Sound: italic" layout="none">
        <Sfx sound={SFX.whip} at={CUE.lean + LEAN_CUE} gain={-4} />
      </Sequence>
      <Sequence name="Sound: command keys" layout="none">
        <Keys strokes={COMMAND_KEYS} from={CUE.command} gain={-4} seed="command" />
      </Sequence>
      <Sequence name="Sound: end" layout="none">
        {/* A soft C and G as the last caption lands, ringing out under the fade. */}
        <Sfx sound={SFX.marimba.c5} at={lastKey + 2} gain={-16} />
        <Sfx sound={SFX.marimba.g5} at={lastKey + 2} gain={-20} />
      </Sequence>
    </>
  );
};
