import type { Run } from "./text";
import { BLUE, GREEN, ORANGE, PINK, PURPLE, paint } from "./theme";
import { CUE } from "./timeline";

/** A caption: at `at` the previous one is erased, then `runs` are typed. `accent` tints the caret and the title's dot. */
export type Line = { at: number; accent: string; runs: Run[] };

export const lines = (glyphCount: number): Line[] => [
  { at: CUE.tagline, accent: PINK, runs: [{ text: "a rounded take on " }, { text: "Geist", weight: 700 }] },
  {
    at: CUE.glyphs,
    accent: GREEN,
    runs: [{ text: glyphCount.toLocaleString("en-US"), weight: 700 }, { text: " Glyphs" }],
  },
  {
    at: CUE.variable,
    accent: BLUE,
    runs: [{ text: "Variable, " }, { text: "Thin", weight: 100 }, { text: " to " }, { text: "Black", weight: 900 }],
  },
  { at: CUE.italic, accent: ORANGE, runs: [{ text: "Upright & " }, { text: "Italic", italic: true }] },
  { at: CUE.mono, accent: PURPLE, runs: [{ text: "with " }, { text: "Goeist Mono", mono: true }] },
  { at: CUE.outro, accent: PINK, runs: [{ text: "Free & open source" }] },
];

// The bottom row: the first specimen, the word the glyph shuffle lands on, and the install
// command typed in Goeist Mono. Mono ligatures are left out: `liga` collapses each one into a
// single cell that overlaps the previous character (inherited from Geist Mono).
export const INTRO = paint("Ga@3&?");
export const WORD = paint("Rounded");
export const COMMAND: Run[] = [
  { text: "npm", color: PINK },
  { text: " " },
  { text: "i", color: GREEN },
  { text: " " },
  { text: "goeist", color: BLUE },
];
