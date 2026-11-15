---
"goeist": minor
---

Add Goeist Serif, a soft take on Vercel's Geist Serif v1.9.2: serif tips thickened into half-rounds at their original reach, circular cut terminals, and every other corner rounded in proportion to its own stroke, with glyph pairs the rounded tips would bring into contact opened by kerning. One Regular weight with the Element Shape (`ELSH`) axis for round, square, triangle and heart dots, as a variable font (`goeist/font/serif`, `goeist/serif.css`) and one static font per shape (`goeist/font/serif/regular`, `square`, `triangle`, `heart`, `goeist/serif-static.css`).

Goeist Sans and Goeist Mono static weights are now each rounded from their own outline instead of interpolated between rounded masters, removing kinks at curved terminals in the in-between weights; advances and kerning are unchanged. Glyphs open corners (looped stroke cuts) are no longer rounded as if they were ink. Every family now ships a FONTLOG.txt.
