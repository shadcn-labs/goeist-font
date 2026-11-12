import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import { MONO, SANS } from "./theme";

// Staged from the repository's fonts/ by scripts/stage-fonts.mjs.
export const SANS_URL = staticFile("fonts/Goeist-Variable.ttf");

// Each call holds the render until its face is ready. The weight range maps every
// `font-weight` onto the wght axis instead of snapping or synthesizing.
loadFont({ family: SANS, url: SANS_URL, weight: "100 900" });
loadFont({ family: SANS, url: staticFile("fonts/Goeist-Italic-Variable.ttf"), weight: "100 900", style: "italic" });
loadFont({ family: MONO, url: staticFile("fonts/GoeistMono-Variable.ttf"), weight: "100 900" });

const MAXP = 0x6d617870; // "maxp"

/** Reads `maxp.numGlyphs` from a TrueType or OpenType binary. */
export const countGlyphs = (font: ArrayBuffer): number => {
  const view = new DataView(font);
  const tables = view.getUint16(4);
  for (let i = 0; i < tables; i++) {
    const record = 12 + i * 16;
    if (view.getUint32(record) === MAXP) {
      return view.getUint16(view.getUint32(record + 8) + 4);
    }
  }
  throw new Error("Font has no maxp table");
};
