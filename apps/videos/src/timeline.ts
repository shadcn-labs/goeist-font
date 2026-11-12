export const FPS = 60;

/** Seconds → frames. */
export const sec = (seconds: number) => Math.round(seconds * FPS);

/** Caption typewriter speed in frames per character: 30 typed or 60 erased per second. */
export const TYPE = 2;
export const ERASE = 1;

/** Caret blink half-period, and how long an idle caret keeps blinking before it hides. */
export const BLINK = sec(0.5);
export const CARET_IDLE = sec(2);

// Every beat of the video, in frames from the start. Captions erase the previous line at their cue,
// then type; specimen scenes take over the bottom row at theirs.
export const CUE = {
  title: sec(0.15),
  dot: sec(0.75),
  tagline: sec(0.85),
  intro: sec(1.3),
  glyphs: sec(3.8),
  shuffle: sec(4.05),
  variable: sec(7.4),
  weight: sec(7.95),
  italic: sec(11.4),
  lean: sec(12.2),
  mono: sec(13.9),
  command: sec(14.7),
  outro: sec(17),
  fade: sec(19.3),
  end: sec(20),
};
