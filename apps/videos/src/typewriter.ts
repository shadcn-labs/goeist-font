import type { Line } from "./script";
import { type Run, runsLength } from "./text";
import { ERASE, TYPE } from "./timeline";

/** Frame at which line `index` starts typing: after whatever the previous line showed has been erased. */
const typingStart = (lines: Line[], index: number): number => {
  const { at } = lines[index];
  return index === 0 ? at : at + typed(lines, index - 1, at) * ERASE;
};

/** Characters of line `index` typed by `frame`, ignoring later lines. */
const typed = (lines: Line[], index: number, frame: number): number =>
  Math.min(runsLength(lines[index].runs), Math.max(0, Math.floor((frame - typingStart(lines, index)) / TYPE)));

export type CaptionState = { runs: Run[]; chars: number; idleSince: number | null };

/** The previous line while it is being erased, then the current line as it is typed. */
export const captionAt = (lines: Line[], frame: number): CaptionState | null => {
  const index = lines.findLastIndex((line) => line.at <= frame);
  if (index < 0) return null;
  const start = typingStart(lines, index);
  if (frame < start) {
    return { runs: lines[index - 1].runs, chars: Math.ceil((start - frame) / ERASE), idleSince: null };
  }
  const { runs } = lines[index];
  const length = runsLength(runs);
  const chars = typed(lines, index, frame);
  return { runs, chars, idleSince: chars === length ? start + length * TYPE : null };
};

/** A character appearing (or, when `erase`, disappearing) on `frame`. */
export type Keystroke = { frame: number; space: boolean; erase: boolean };

/** Every keystroke of the caption line, in order: each line erases what the previous one showed, then types. */
export const keystrokes = (lines: Line[]): Keystroke[] =>
  lines.flatMap((line, index) => {
    const start = typingStart(lines, index);
    const erases = Array.from({ length: (start - line.at) / ERASE }, (_, k) => ({
      frame: line.at + (k + 1) * ERASE,
      space: false,
      erase: true,
    }));
    const text = line.runs.map((run) => run.text).join("");
    const types = [...text].map((char, k) => ({ frame: start + (k + 1) * TYPE, space: char === " ", erase: false }));
    return [...erases, ...types];
  });
