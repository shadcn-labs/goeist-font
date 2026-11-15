# goeist

## 0.1.0

### Minor Changes

- 5dcf346: Add Goeist Serif, a soft take on Vercel's Geist Serif v1.9.2: serif tips thickened into half-rounds at their original reach, circular cut terminals, and every other corner rounded in proportion to its own stroke, with glyph pairs the rounded tips would bring into contact opened by kerning. One Regular weight with the Element Shape (`ELSH`) axis for round, square, triangle and heart dots, as a variable font (`goeist/font/serif`, `goeist/serif.css`) and one static font per shape (`goeist/font/serif/regular`, `square`, `triangle`, `heart`, `goeist/serif-static.css`).

  Goeist Sans and Goeist Mono static weights are now each rounded from their own outline instead of interpolated between rounded masters, removing kinks at curved terminals in the in-between weights; advances and kerning are unchanged. Glyphs open corners (looped stroke cuts) are no longer rounded as if they were ink. Every family now ships a FONTLOG.txt.

## 0.0.2

### Patch Changes

- 818d154: Update Goeist Sans and Goeist Mono attribution. The fonts credit Aniket Pawar as designer and copyright holder, use Shadcn Labs' CNLB vendor ID, and retain the original Geist notices. The package includes Next.js font imports, responsive theme-aware README banners, and links to shadcn-labs/goeist-font. The internal font version is 1.000, separate from the npm package version. Add a font issue report template based on Geist's.

## 0.0.1

### Patch Changes

- Initial release of Goeist Sans and Goeist Mono 0.001, rounded derivatives of Vercel Geist Sans and Geist Mono v1.9.2, with nine weights and genuine italics each, as variable and static WOFF2 for `next/font` (`goeist/font/sans`, `goeist/font/sans-non-variable`, `goeist/font/mono`, `goeist/font/mono-non-variable`) and plain CSS (`goeist/sans.css`, `goeist/sans-static.css`, `goeist/mono.css`, `goeist/mono-static.css`).
