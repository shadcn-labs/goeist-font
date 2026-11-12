import { staticFile } from "remotion";

/** A one-shot in public/sfx; `anchor` is the seconds from the file start to its sync point. */
export type Sound = { src: string; anchor: number };

const sound = (name: string, anchor = 0): Sound => ({ src: staticFile(`sfx/${name}.wav`), anchor });

// CC0 recordings from Freesound, trimmed and peak-normalised to -1 dBFS (sources in README.md).
// Hits start on their attack (anchor 0); swells and swishes anchor on their peak.
export const SFX = {
  keys: Array.from({ length: 12 }, (_, i) => sound(`key-${String(i + 1).padStart(2, "0")}`)),
  space: sound("key-space"),
  pop: sound("pop"),
  breath: sound("breath", 0.752),
  riffle: sound("riffle"),
  wood: sound("wood"),
  swoosh: sound("swoosh", 0.9),
  whip: sound("whip", 0.062),
  rise: sound("rise", 1.2), // the reversed crash stops right after its peak
  kick: sound("kick"),
  marimba: {
    c3: sound("marimba-c3"),
    c5: sound("marimba-c5"),
    g5: sound("marimba-g5"),
    b5: sound("marimba-b5"),
  },
};
