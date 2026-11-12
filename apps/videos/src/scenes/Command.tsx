import { interpolate, useCurrentFrame } from "remotion";
import { Caret, caretOn } from "../components/Caret";
import { CLAMP, Glyph } from "../motion";
import { COMMAND, WORD } from "../script";
import { Runs, runsLength, sliceRuns } from "../text";
import { MONO, SPECIMEN } from "../theme";
import { CUE, sec } from "../timeline";
import type { Keystroke } from "../typewriter";

// Frames per deleted letter and per typed character: 12 a second, slow enough that every key is heard.
const ERASE = 5;
const TYPE = 5;
const ERASED = WORD.length * ERASE;
const TYPE_START = ERASED + sec(0.15);
const CARET_END = CUE.outro - CUE.command; // the caption takes the caret back for the outro

/** The big caret's keystrokes in scene frames: backspaces through the word, then the command. */
export const COMMAND_KEYS: Keystroke[] = [
  ...WORD.map((_, k) => ({ frame: (k + 1) * ERASE, space: false, erase: true })),
  ...[...COMMAND.map((run) => run.text).join("")].map((char, k) => ({
    frame: TYPE_START + (k + 1) * TYPE,
    space: char === " ",
    erase: false,
  })),
];

/** A big caret deletes the word, shrinks to the Mono size and types the install command. */
export const Command: React.FC<{ accent: string }> = ({ accent }) => {
  const frame = useCurrentFrame();
  const kept = Math.max(0, WORD.length - Math.floor(frame / ERASE));
  const length = runsLength(COMMAND);
  const chars = Math.min(length, Math.max(0, Math.floor((frame - TYPE_START) / TYPE)));
  const idleSince = chars === length ? TYPE_START + length * TYPE : null;
  return (
    <>
      {WORD.slice(0, kept).map(({ char, color }, i) => (
        <Glyph key={i} style={{ color, fontWeight: SPECIMEN.heavy, fontStyle: "italic" }}>
          {char}
        </Glyph>
      ))}
      <span style={{ fontFamily: MONO, fontSize: SPECIMEN.code, fontWeight: 500 }}>
        <Runs runs={sliceRuns(COMMAND, chars)} />
      </span>
      <span style={{ fontSize: interpolate(frame, [ERASED, TYPE_START], [SPECIMEN.size, SPECIMEN.code], CLAMP) }}>
        <Caret color={accent} visible={frame < CARET_END && caretOn(frame, idleSince)} width={0.045} />
      </span>
    </>
  );
};
