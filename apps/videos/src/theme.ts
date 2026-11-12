export const SANS = "Goeist";
export const MONO = "Goeist Mono";

export const PAPER = "#FFFFFF";
export const INK = "#0A0A0A";

// Tuned for a white canvas: green and orange sit darker than their neon versions.
export const PINK = "#FF2E74";
export const GREEN = "#14C948";
export const BLUE = "#1F5EFF";
export const ORANGE = "#FF9500";
export const PURPLE = "#A23BFF";
export const PALETTE = [PINK, GREEN, BLUE, ORANGE, PURPLE];

export const WIDTH = 1920;
export const HEIGHT = 1080;
export const MARGIN = 128;

// `top` is the line box top; every block uses line-height 1.
export const TITLE = { size: 240, top: 96 };
export const CAPTION = { size: 88, top: 372 };
// `weight` is the resting specimen weight, `heavy` where the weight sweep ends; `code` sizes the
// Mono command, whose 12 cells must fit between the margins.
export const SPECIMEN = { size: 360, top: 640, weight: 600, heavy: 900, code: 228 };

// With line-height 1 the baseline sits (1 - 1.3) / 2 + 1.005 = 0.855em below the line box top
// (Goeist ascender 1005, descender 295 units per 1000).
export const BASELINE = "85.5%";

type Letter = { char: string; color: string };

/** Colors each character of `text` with the next palette entry. */
export const paint = (text: string): Letter[] =>
  [...text].map((char, i) => ({ char, color: PALETTE[i % PALETTE.length] }));
