# Rounded / soft serif references for Goeist Serif

Scope: visual and structural references for a rounded derivative of Geist Serif. Proprietary faces (ITC Souvenir, Cooper Black, Windsor, Bookmania, Recoleta, Gelica) are visual references only; no data from them was opened or measured. OFL faces were downloaded to `/tmp` (never the repo) and measured with fontTools.

Status tags: `[measured]` = my fontTools measurement (method below); `[observed]` = read off a linked specimen image; `[unverified]` = not confirmed from a primary source.

## 1. ITC Souvenir and its proprietary relatives

### 1.1 Souvenir history

| Date | Event | Source |
|---|---|---|
| 1914 | Morris Fuller Benton designs Souvenir for ATF, one weight, no italic; working title "Round Roman"; "an early typeface to feature rounded serifs and a soft, rubbery look" (Mac McGrew) | [Devroye](https://luc.devroye.org/fonts-67291.html), [MyFonts field guide](https://cms.myfonts.com/sites/default/files/2023-09/ITC-Souvenir-Font-Field-Guide.pdf) |
| — | Loosely based on Schelter-Antiqua / Schelter-Kursiv (J.G. Schelter & Giesecke, Leipzig, 1905–06): open-bottom g, narrowed U aperture, convex A diagonals | [Wikipedia](https://en.wikipedia.org/wiki/Souvenir_(typeface)), [Devroye quoting Paul Hunt](https://luc.devroye.org/fonts-67291.html) |
| 1920 / 1924 | Fonts In Use dates the ATF issue 1920; appears in the 1924 ATF catalog | [Fonts In Use](https://fontsinuse.com/typefaces/1913/itc-souvenir), [Devroye](https://luc.devroye.org/fonts-67291.html) |
| 1967 | Ed Benguiat redraws it for Photo-Lettering Inc. as Souvenir Graphic (five upright weights) plus the low-contrast Souvenir Balloon | [Wikipedia](https://en.wikipedia.org/wiki/Souvenir_(typeface)), [Fonts In Use](https://fontsinuse.com/typefaces/1913/itc-souvenir) |
| 1970–71 | ITC issues ITC Souvenir, drawn by Benguiat: four weights (Light, Medium, Demi, Bold), each with a matching italic, plus Bold Outline; ITC's first release alongside ITC Avant Garde Gothic | [MyFonts field guide](https://cms.myfonts.com/sites/default/files/2023-09/ITC-Souvenir-Font-Field-Guide.pdf), [Fonts In Use](https://fontsinuse.com/typefaces/1913/itc-souvenir), [Daylight weight list](http://e-daylight.jp/fonts/type/s/itc-souvenir.html) |
| 1970s | Demi and Bold become ubiquitous; cut back into Linotype metal by Matrotype, a rare photo→metal reversal; later backlash ("Times Roman dipped in chocolate") | [Wikipedia](https://en.wikipedia.org/wiki/Souvenir_(typeface)) |

Souvenir-adjacent digital faces: ITC Souvenir Monospaced, Souvenir Gothic (URW, sans companion), Sunset Serial (SoftMaker), Dez Petranian, Eastern Souvenir (VGC 1969, narrower) ([Devroye list](https://luc.devroye.org/myfonts-souvenir/), [Fonts In Use](https://fontsinuse.com/typefaces/1913/itc-souvenir)). No OFL Souvenir revival was found.

### 1.2 Souvenir defining traits

From the sources: "rounded serifs, and very little contrast between thick and thin strokes", "generally light look" ([Wikipedia](https://en.wikipedia.org/wiki/Souvenir_(typeface))); "soft serifs", "curved diagonals on w, v and y", "open loop on lowercase g", "Cap M diagonals do not reach baseline", "soft terminals"; Light is readable in text and "as its weights become heavier, legibility suffers" ([MyFonts field guide](https://cms.myfonts.com/sites/default/files/2023-09/ITC-Souvenir-Font-Field-Guide.pdf)).

From the specimens (Benguiat [Medium lowercase](https://luc.devroye.org/EdBenguiat-ITCSouvenirMedium-1977-after-MorrisFullerBenton-1914.gif), [Light lowercase](https://luc.devroye.org/EdBenguiat-ITCSouvenir-1970s.gif), [Bold](https://luc.devroye.org/EdBenguiat-ITCSouvenirBold-1970s.gif), [ITC poster 1](https://luc.devroye.org/myfonts-souvenir/ITC-ITCSouvenir-2000-199047.png), [ITC poster 2](https://luc.devroye.org/myfonts-souvenir/Adobe-ITCSouvenir-2000-131138.png), [Bold lowercase strip](https://luc.devroye.org/myfonts-souvenir/ITC-ITCSouvenir-2000.gif), [Benton 1916](https://luc.devroye.org/MorrisFullerBenton-Souvenir-1916b.png)) `[observed]`:

- **Serifs**: short, tapered wedges whose tips are blunt, round lumps. Head serifs on b d h k l i j m n r are sloped wedges ending in a round bump. Foot serifs are near-flat underneath with round ends. No serif ends in a point or a square.
- **Brackets**: very long concave curves; the serif grows out of the stem rather than being attached. Concave transitions are the dominant soft element, more than the convex tips.
- **No straight lines**: stems swell slightly, diagonals of v w x y A V W are convex curves, the bottom vertex of v w is a rounded U, not a point.
- **Contrast**: low in Light (near monoline), moderate in Bold; hairlines never go fine.
- **Terminals**: a c f r y j and the ear of g end in teardrop or ball bulbs; s and 5 end in cupped soft serifs; the asterisk has teardrop petals.
- **Weight behaviour**: Light has small, discreet round tips. Medium/Demi have bulbous tips and longer brackets. Bold is "inky": serifs merge into blobs, counters close up, round tips grow to roughly serif thickness. Softness goes up with weight: radius grows faster than stem.
- **Italic**: a true cursive, not a sloped roman, with soft entry and exit strokes and swashes ([Wikipedia](https://en.wikipedia.org/wiki/Souvenir_(typeface))).
- **Roundness is drawn**: tips are asymmetric (the head-serif lump sits on the wedge's upper side), radii vary per glyph, and curves flow into one another without circular arcs. It reads as lettering, not filleting.

### 1.3 Related proprietary references (visual only)

| Face | Designer, date | Relevance | Source |
|---|---|---|---|
| Cooper Black | Oswald B. Cooper, BB&S 1922; extra-bold of Cooper Old Style | Old-style lettering made ultra bold, "soft, 'muddy' appearance", low contrast | [Wikipedia](https://en.wikipedia.org/wiki/Cooper_Black) |
| Windsor | Eleisha Pechey, Stephenson Blake 1905 | Art Nouveau soft serif; in bold weights "the corners round off and serifs remain slender and jagged"; leaning n, tilted e | [Font Review Journal](https://fontreviewjournal.com/windsor/) |
| Bookmania | Mark Simonson 2011; 5 weights + italics, 680+ swashes | Bookman revival (not Souvenir); same 1960s–70s era, soft bracketed old style | [Simonson](https://www.marksimonson.com/fonts/view/bookmania/) |
| Recoleta | Jorge Cisterna / Latinotype 2018 | Mixes "the soft and gentle shapes found in Cooper" with Windsor's angled strokes | [Cisterna](https://jorgecisternatype.com/recoleta) |
| Gelica | Dave Rowland Type 2020; 7 weights + italics | Soft serif owing "more to Goudy Heavyface and Ludlow Black, particularly in the concave serifs" | [DRT](https://daverowlandtype.com/font/gelica/), [Fonts In Use](https://fontsinuse.com/typefaces/131541/gelica) |
| New Spirit | Miles Newlyn 2020 | Modern Windsor revival | [Newlyn](https://newlyn.com/blog/a-new-windsor-in-spirit) |

## 2. Open-licensed references

Licences were verified by reading each `OFL.txt` header (all read "licensed under the SIL Open Font License, Version 1.1") or the foundry's licence statement. RFN = Reserved Font Name; it matters only for derivatives, and Goeist derives from none of these.

| Font | Designer | Licence (verified) | Axes / styles | Rounding type |
|---|---|---|---|---|
| Fraunces | Undercase Type (Phaedra Charles, Flavia Zimbardi) | [OFL](https://github.com/google/fonts/blob/main/ofl/fraunces/OFL.txt) | `opsz` 9–144, `wght` 100–900, `SOFT` 0–100, `WONK` 0–1; roman + italic VF | Variable: contrast cut + thicker serifs + semicircular serif ends + larger brackets; crotches stay sharp |
| Caprasimo | DocRepair Project, Charles, Zimbardi (built from Fraunces) | [OFL](https://github.com/google/fonts/blob/main/ofl/caprasimo/OFL.txt) | 1 style (Cooper Black stand-in) | Uniform: tips and brackets ≈0.28 stem, ball terminals, crotches sharp |
| Cooper\* | Owen Earl (indestructible type\*) | [OFL](https://github.com/indestructible-type/Cooper/blob/main/OFL.txt) | `wght` 400–900 VF + italic VF; 6 statics each | Drawn/organic: no sharp corner anywhere, bulb serifs, bowed stems |
| Corben | Vernon Adams | [OFL, RFN "Corben"](https://github.com/google/fonts/blob/main/ofl/corben/OFL.txt) | Regular, Bold | Bulb serif ends (radius > serif thickness), crotches sharp |
| Young Serif | Bastien Sozeau (NoirBlancRouge) | [OFL](https://github.com/google/fonts/blob/main/ofl/youngserif/OFL.txt), [repo](https://github.com/noirblancrouge/YoungSerif) | GF: 1 style; repo: Light–Bold + italics, `wght` VF | Small uniform corner fillets (0.11 stem) + very large brackets |
| Calistoga | Yvonne Schüttler, Sorkin Type | [OFL](https://github.com/google/fonts/blob/main/ofl/calistoga/OFL.txt) | 1 style | Curved, cupped serif faces with sharp points: soft silhouette, not rounded corners |
| Coustard | Vernon Adams | [OFL](https://github.com/google/fonts/blob/main/ofl/coustard/OFL.txt) | Regular, Black | Soft slab: round slab ends, medium brackets |
| Kiwi Maru | Hiroki-Chan | [OFL](https://github.com/google/fonts/blob/main/ofl/kiwimaru/OFL.txt) | Light, Regular, Medium (CJK + Latin) | Round-nib monoline: every exposed corner semicircular, crotches lightly filleted |
| Zen Antique Soft | Yoshimichi Ohira | [OFL](https://github.com/google/fonts/blob/main/ofl/zenantiquesoft/OFL.txt) | 1 style (CJK + Latin) | Medium contrast kept; rounded serif ends, very large brackets |
| Shrikhand | Jonny Pinhorn | [OFL](https://github.com/google/fonts/blob/main/ofl/shrikhand/OFL.txt) | 1 style (italic display) | Small tips (0.17 stem), brackets 0.34 |
| Recursive | Arrow Type, Stephen Nixon | [OFL](https://github.com/google/fonts/blob/main/ofl/recursive/OFL.txt) | `MONO`, `CASL` 0–1, `wght` 300–1000, `slnt`, `CRSV` | Sans/mono. `CASL` changes "stroke curvature, contrast, and terminals" ([registry](https://github.com/googlefonts/axisregistry/blob/main/Lib/axisregistry/data/casual.textproto)); terminals 0.12 → 0.67–0.80 stem, joins sharp |
| Roboto Serif | Commercial Type, Greg Gazdowicz | [OFL](https://github.com/google/fonts/blob/main/ofl/robotoserif/OFL.txt) | `GRAD` −50–100, `opsz` 8–144, `wdth` 50–150, `wght` 100–900 | None: sharp convex corners, brackets 0.55–0.75 stem; useful only as an opsz contrast model (2.5 → 1.4) |
| Bree Serif / Patua One | TypeTogether / Latinotype | [OFL, RFN](https://github.com/google/fonts/blob/main/ofl/breeserif/OFL.txt) / [OFL, RFN](https://github.com/google/fonts/blob/main/ofl/patuaone/OFL.txt) | 1 style each | Not rounded (sharp corners); "soft" only in structure. Rejected as references |
| Bonbance | Louna Bourdon (X Cicéro / ESAD Valence) | `[unverified]`: listed as OFL by [A Type of Amigo](https://atypeofamigo.com/fonts/bonbance/); the [foundry page](https://xcicero.esad-gv.net/page/bonbance/), zip and name table carry no licence | Bold Condensed only | Flared, bulbous serif ends; no sharp corners |

Designer, licence and axis data for the Google Fonts entries come from each family's `METADATA.pb` in [google/fonts](https://github.com/google/fonts/tree/main/ofl) and the font name tables.

### 2.1 Fraunces `SOFT`, in detail

Primary sources: the [README](https://github.com/undercasetype/Fraunces#variable-axes), [production notes](https://github.com/undercasetype/Fraunces/tree/master/sources), [GF article](https://github.com/google/fonts/blob/main/ofl/fraunces/article/ARTICLE.en_us.html), [axis registry](https://github.com/googlefonts/axisregistry/blob/main/Lib/axisregistry/data/softness.textproto).

- Stated intent: Fraunces is inspired by "Windsor, Souvenir, and the Cooper Series". `SOFT` "gives access to the softer, rounded forms that are available towards the Optical Min, but still retaining other Optical Sizing considerations, such as change in character width, spacing, tall ascenders, and shorter x-height". The GF article says Softness controls the "'wetness' or 'inkiness'".
- Range 0–100, labelled Sharp (0), Soft (50), SuperSoft (100). The registry default is 0; the README table says 100. The GF binary's `fvar` defaults are opsz 9, wght 900, SOFT 0, WONK 1 `[measured]`.
- Masters: 8 per style. SuperSoft sits only at 144 pt and Sharp at 9 pt; the corners were generated with `ScaleAndInterpolate.py` and then needed "a great deal of manual corrections". So SOFT does not just add a fillet: it pulls the 144 pt drawing toward the soft text-size design.
- `WONK` is a binary substitution axis (leaning h n m, flagged ball terminals in the italic), applied automatically above opsz 18.

Measured at opsz 144 unless noted (UPM 2000; stem = `l` at mid x-height; hairline = H crossbar) `[measured]`:

| wght / SOFT | Stem | Hairline | Contrast | Serif-end thickness | Tip r (u / stem / serif t) | Bracket r (u / stem) |
|---|---|---|---|---|---|---|
| 100 / 0 | 54 | 10 | 5.4 | — | 0.09 stem | 0.53 stem |
| 100 / 100 | 54 | 45 | 1.2 | 32–41 | 29 / 0.53 / 0.70 | 60 / 1.10 |
| 400 / 0 | 177 | 16 | 11.1 | 14–18 | 8 / 0.04 / 0.44 | 33 / 0.19 |
| 400 / 50 | 181 | 64 | 2.8 | 60–65 | 34 / 0.19 / 0.52 | 52 / 0.29 |
| 400 / 100 | 184 | 111 | 1.7 | 95–112 | 60 / 0.33 / 0.54 | 72 / 0.39 |
| 900 / 0 | 362 | 24 | 15.1 | 25–40 | 12 / 0.03 / 0.31 | 43 / 0.12 |
| 900 / 100 | 379 | 211 | 1.8 | 192–235 | 111 / 0.29 / 0.47 | 100 / 0.26 |
| opsz 9, 400 / 0 | 212 | 86 | 2.5 | 74–83 | 46 / 0.22 / 0.55 | 60 / 0.29 |

What SOFT changes, in order of visual weight:
1. **Contrast**: hairlines grow about 7× at Regular (11:1 → 1.7:1). This is most of the Souvenir/Cooper feel. Stems grow only about 4%.
2. **Serif-end thickness tracks the hairline**: serif thickness ≈ crossbar thickness at every location measured (16/14–18, 64/60–65, 111/95–112, 211/192–235). Caprasimo (222 / 217) and Corben (115 / 92–117) follow the same rule.
3. **Serif ends become semicircles**: one continuous 155–163° convex run per serif end, r ≈ 0.5 × local serif thickness at every SOFT > 0 (0.47–0.54). Even SOFT = 0 has micro-rounded hairline serif ends (r 8 u / 2000).
4. **Brackets grow**: 0.19 → 0.39 stem at Regular. In stem units the radius falls with weight (0.39 → 0.26); in absolute units it rises (72 → 100 u).
5. **Structural concave joins stay sharp** at every SOFT value: H crossbar ×4, A 5, K 4, R 5, M 3, n arch-to-stem 2, V/M inner vertices (−139° to −155° breaks).
6. **Apexes are truncated, not pointed**: A has a flat top with both ends rounded (≈160° runs, r 0.32–0.34 stem). The V bottom is flat with two 90° rounds (r 0.31). The M middle vertex is one round (139°, r 0.61).
7. **Widths grow slightly**: n 996 → 1037 (+4.1%), a 864 → 895, o unchanged (wght 400).

The italic shows the same SOFT behaviour; at SOFT 0 it is a high-contrast display italic, at SOFT 100 a soft, low-contrast cursive (local renders of the GF [italic VF](https://github.com/google/fonts/tree/main/ofl/fraunces) `[observed]`).

### 2.2 Other measured references

`[measured]`. Stems are in font units at each font's UPM; "tip" = continuous convex run at serif ends; "crotch" = sharp structural concave joins in H A K R n.

| Font | Stem | Contrast | Tip r / stem | Tip r / serif t | Bracket r / stem | Crotches |
|---|---|---|---|---|---|---|
| Caprasimo | 450 | 2.0 | 0.28 | 0.58 | 0.28 | sharp (H 4, A 5, R 6, g 6) |
| Cooper\* 400 | 149 | 1.7 | 0.76 | 1.36 | 1.62 | none: all joins smooth |
| Cooper\* 900 | 411 | 1.5 | 0.47 | 0.69 | 0.48 | none |
| Corben Regular | 191 | 1.7 | 0.65 | 1.06 | 0.47 | sharp |
| Corben Bold | 613 | 3.2 | 0.41 | 1.10 | 0.20 | sharp |
| Young Serif | 137 | 1.7 | 0.11 (two quarter-rounds, flat between) | — | 0.62 | sharp |
| Coustard | 227 | 1.5 | 0.53 | 0.58 | 0.29 | sharp |
| Kiwi Maru | 76 | 1.0 | 0.50 | 0.53 | 0.12 | filleted ≈0.10–0.12 stem |
| Zen Antique Soft | 108 | 3.1 | 0.19 | 0.70 | 0.63 | smooth |
| Calistoga | 156 | 1.9 | sharp 49°/90° points, curved serif face r 0.61 | — | 0.37 | sharp |
| Recursive CASL 1 | 92 | 1.0 | 0.67–0.80 (stroke ends) | — | — | sharp |

Three serif-end models emerge:
- **Fillet** (Young Serif, Fraunces SOFT 0): two separate small corner rounds with a flat between. This is what Goeist Sans does.
- **Semicircle** (Fraunces SOFT ≥ 50, Caprasimo, Coustard, Kiwi Maru): r ≈ 0.5 × serif thickness, so the serif end is a stadium cap. This is the limit of Goeist Mono's `circular` mode.
- **Bulb** (Cooper\*, Corben, Souvenir): r > serif thickness. The serif's upper and lower edges are themselves convex, so it is lens- or teardrop-shaped. This needs drawing; trimming corners cannot produce it.

### 2.3 Quality notes

- **Fraunces**: the reference-grade design space: 8 masters, hand-corrected, GF QA. Its interpolation is visibly nonlinear (avar present `[measured]`); SOFT 50 is not halfway in appearance.
- **Caprasimo**: one style, the cleanest mechanical-looking system; uniform radii suggest a near-constant fillet rule after drawing `[inference]`.
- **Cooper\***: historically faithful, irregular outlines with print texture; best open source of drawn-organic roundness, poor model for a geometric pipeline.
- **Corben**: older (2010–11) GF upload, quadratic, coarse point structure; good for bulb shapes only.
- **Kiwi Maru**: geometrically consistent round-nib Latin; the closest open analogue of Goeist Mono's profile applied to a serif.
- **Young Serif**: shows that large brackets alone read as "soft" even with tiny tip fillets.

## 3. Glyph-level comparison

Souvenir columns are `[observed]` from the §1.2 specimens. Fraunces, Caprasimo and Kiwi Maru are `[measured]` plus renders. Geist Serif facts come from the companion note [research/geist-serif.md](geist-serif.md).

| Feature | ITC Souvenir (drawn) | Fraunces SOFT 100 (opsz 144, 400) | Caprasimo / Cooper\* | Kiwi Maru (round nib) | Geist Serif today |
|---|---|---|---|---|---|
| Foot serif tip | Round lump, flat underside, slight overhang | Semicircle, r 0.33 stem = 0.54 × serif t | Semicircle r 0.28 stem / bulb r 0.76 | Semicircle r 0.50 stem | Wedge to a 4–6 u vertical tip, flat bottom |
| Head serif (b d l n i) | Sloped wedge ending in a round bump | Sloped wedge, round end (≈142–156° run, r 0.28–0.29) | Same, larger | Round end | `_cap.stem` flag, sharp |
| Bracket (concave stem–serif) | Very long, merges into stem | r 0.39 stem (0.26 at Black) | 0.28 / up to 1.6 stem | 0.12 stem | Smooth curve ≈20 u (≈0.24 stem) |
| Crotches (bar–stem, arch–stem, K, R leg) | Tight but soft-looking (detail unresolved at specimen size) | Sharp | Sharp / smooth | Small fillet 0.10–0.12 | Sharp (872 concave corners) |
| A apex | Convex diagonals, softly rounded apex | Flat top, both ends rounded r 0.33 | Rounded / blunt | Rounded | Sharp |
| V W bottom vertex | Rounded U, curved diagonals | Flat with two 90° rounds r 0.31; inner vertex sharp | Two 90° rounds r 0.21–0.22; inner sharp | One round r 0.88; inner fillet 0.11 | Sharp |
| N M vertices | M diagonals stop above baseline | M middle vertex one round r 0.61; inner sharp | Rounded | Rounded | Sharp |
| a c f r y terminals | Teardrop/ball bulbs | Ball terminals | Balls | Round stroke ends | 4 u chisel cuts |
| g | Open-tailed lower loop; teardrop ear | Double-storey, ball ear | Double-storey, ball ear | Round ear end | Ear corner sharp, many concave joins |
| Q tail, R/K legs | Q tail a separate swash; R/K legs curved with soft ends | K/R leg feet get the serif-tip semicircle | Same | Round | Sharp leg-foot corners |
| Dots (i j . : !) | Round | Round | Round (Caprasimo i dot: full circle) | Round | ELSH: round / square / triangle / heart |
| Italic | True cursive, swashes | Soft cursive; WONK flags | Cooper\* italic VF | — | None yet (Python italic announced) |

## 4. Rounded-serif vocabulary

- **Serif tip / serif end**: the free end of a serif. Rounded-serif practice makes it a semicircle of r ≈ ½ local serif thickness (Fraunces, Caprasimo, Kiwi Maru, Coustard all measure 0.47–0.58), not a fillet sized from the stem.
- **Serif-thickness = hairline rule**: in every soft reference the serif end is about as thick as the hairline. Rounding a hair-thin serif tip is invisible; softness needs a tip thick enough to hold a visible arc.
- **Stem-end / terminal radius**: for stroke ends without serifs (a c f r y, legs), the round is again ≈ ½ local thickness (ball or semicircle). Souvenir and Fraunces go further and swell the end into a ball (adds ink).
- **Bracket (concave fillet)**: the concave transition from stem to serif. Soft serifs enlarge it to 0.26–0.47 stem (Fraunces, Caprasimo, Coustard, Corben) and up to 0.6–1.6 (Young Serif, Zen Antique Soft, Cooper\* Regular). In stem units it shrinks as weight grows; in font units it grows.
- **Crotch / structural join**: concave corners where two strokes meet (crossbar, arch, diagonals, leg–bowl). Most soft serifs leave these sharp (Fraunces, Caprasimo, Corben, Young Serif, Calistoga). Only round-nib (Kiwi Maru, ≈0.1 stem) or drawn (Cooper\*) designs smooth them. Keeping them sharp preserves crispness and avoids dark spots.
- **Truncated apex**: soft serifs blunt pointed vertices into a short flat closed by two rounds (Fraunces V: two 90° rounds of 0.31 stem; Caprasimo 0.21–0.22), rather than one big round.
- **Contrast reduction**: the strongest single softness cue. Fraunces SOFT is mostly this (11:1 → 1.7:1). Souvenir is low contrast by design; Zen Antique Soft shows that rounding at 3:1 contrast still reads soft but "refined" rather than Souvenir-like.
- **Drawn vs mechanical roundness**: Souvenir, Cooper\* and Windsor are drawn: asymmetric tips, convex "straight" strokes, radii varying per glyph, bulb serifs larger than the serif. Caprasimo, Kiwi Maru and (largely) Fraunces SOFT are systematic: one radius rule per corner class, circular-looking arcs. A fillet pipeline can only reach the systematic end. Curved diagonals, bowed stems, bulbs and the open-tailed g are redrawing, not rounding.
- **G1 vs G2**: all references join tips and brackets tangentially; nothing here shows a need for curvature continuity at serif scale. Large brackets (≥ 0.3 stem) meeting straight stems are where a curvature jump would show first `[inference]`.

## 5. Method (measurements)

Scripts lived in `/tmp/rsr` (not committed). Each font was instanced with `fontTools.varLib.instancer`, overlaps were removed with `fontTools.ttLib.removeOverlaps` (skia-pathops), and outlines were decomposed. Smoothly joined, same-direction curve segments (tangent break ≤ 8°) are merged into runs. Each run with total turn ≥ 35° is reported as convex or concave, measured against the ink, with equivalent radius r = arc length / total turn. Tangent breaks > 30° count as sharp corners. Stem = horizontal ink run of `l` at ½ x-height. Hairline = thinnest vertical run through the centre of H. Serif thickness = vertical run 0.15–0.3 stem inside the serif tip of H. Treat values as ±10%; quadratic GF binaries split arcs, and the run merge compensates only partly.

## Implications for Goeist

Ranked by importance. Geist Serif numbers (stem nV 84 u, cap stem 94, hairline 29–38 u, contrast 2.6–3.6, serif tips 4–6 u, ~30° wedge, smooth ≈20 u brackets, 872 concave joins, 1 master, ELSH dots) come from [research/geist-serif.md](geist-serif.md).

1. **Follow Fraunces SOFT ≈ 50–100 as the structural model, Caprasimo as the mechanical-rule model, and Souvenir/Cooper\* as visual targets only.** Fraunces is OFL, explicitly Souvenir-derived, and spans exactly the high-contrast → soft range Goeist Serif has to cross. Geist Serif's contrast (2.6–3.6) already sits at Fraunces SOFT ≈ 50 (2.8) and Zen Antique Soft (3.1). Rounding alone therefore lands at "Fraunces Soft", not Souvenir. Do not copy outlines from any reference (Corben, Bree, Patua carry RFNs; all would need attribution).

2. **Serif tips: semicircle at hairline thickness.** Reshape every serif end, as the companion note proposes at the corner-component level (`_corner.ucSerif`, `_corner.lcSerif`, `_corner.numSerif`, `_corner.serif-alt`, `_cap.stem`). Thicken the 4–6 u tip to **≈ hairline thickness, 34 u (0.40 stem)**, and close it with one arc of **r = t/2 ≈ 17 u (0.20 stem)**. Keep the flat baseline side, the ~30° wedge and the 84/81 u reach. Evidence: serif-end thickness = hairline in Fraunces at every SOFT and in Caprasimo/Corben; tip r / serif t = 0.47–0.58 in every semicircle reference. Fraunces SOFT 50 gives r 0.19 stem, close to this. This is slightly larger than the companion note's 0.30 × stem tip (≈ 25 u) and better matched to the references; settle it by proof.

3. **Make radii local-thickness relative, never stem-only.** New profile rule: `r = min(k_stem × stem, 0.5 × t_local)`, with `t_local` measured perpendicular across the ink at the corner. The current 48%-of-adjacent-edge clamp in `make_corner` approximates this only when an edge happens to equal the thickness; it fails on wedges with long sloped edges. With Goeist Sans' 0.52 the stem term (44 u) would never bind on serifs or hairlines; on stem ends and leg feet it caps at 0.33 stem (Fraunces S100 Regular) to 0.52 (Goeist house value).

4. **Brackets: enlarge in the corner components, not with a new concave-fillet pass.** Target **r ≈ 0.30–0.40 stem = 25–34 u** (Fraunces 0.29 at SOFT 50, 0.39 at SOFT 100; Caprasimo/Coustard 0.28–0.29), up from today's ≈ 20 u. Geist Serif brackets are already smooth curves, so `classify_corner` never sees them and nothing in `rounding.py` needs to change for brackets. Only the five serif components change. If the pipeline does gain concave fillets later, the safety test must be inverted: the arc must lie entirely in non-ink and must not narrow a counter below 0.8 × its width.

5. **Keep structural concave joins sharp** (H/E/F bar joins, n m h u arch joins, A V W M N inner vertices, K/R/x crotches, g link/ear joins). Every systematic soft-serif reference does this except round-nib Kiwi Maru. It matches the current Goeist rule and the companion note. Optional later experiment: ≤ 0.10 stem (≈ 8 u) fillets on crotches only where both edges ≥ 1 stem long, for a Kiwi-Maru-like variant. Lowest priority.

6. **Apexes and vertices: truncate and round, using the existing acute rule.** A, V, W, M, N vertices and K/R leg feet get **two rounds of ≈ 0.22 stem (18 u)** (Caprasimo 0.21–0.22; Fraunces 0.31). The current `acute = 0.22` already matches; keep it, bounded by rule 3. Inner (concave) vertices stay sharp.

7. **Terminals (s c e a r f j y, g ear, figures): round to semicircle at local thickness; balls are optional.** References use balls (Souvenir, Fraunces, Caprasimo), but a ball adds ink outside the outline, which the trim-only pipeline cannot do. Minimum: thicken each 4 u chisel cut to ≈ 0.40 stem and cap with r = t/2, the same construction as rule 2. Ball terminals are a separate drawn alternative; if wanted, ship them as a stylistic set rather than the default.

8. **Contrast: do not reduce it in v1; record it as the Souvenir lever.** Souvenir-like softness needs hairlines near 0.5–0.6 stem (contrast ≤ 2, Fraunces SOFT 100 / Caprasimo / Souvenir), i.e. hairlines of 42–50 u instead of 29–38. That requires stroke-aware thickening, which no part of the current pipeline does. Upstream's announced text-version tool and Thin–Black weights may supply it ([blog](https://vercel.com/blog/introducing-geist-serif)). Revisit when the weight axis ships.

9. **Dots: round dot unchanged; soften ELSH variants with corner radii, not stadiums.** The square dot gets r ≈ 0.25 × side (≈ 28 u), the triangle gets the acute rule, and the heart point gets ≈ 15 u while its cusp stays concave (agrees with the companion note). All soft references use round dots; a stadium square would duplicate the round variant.

10. **Weight scaling, for when Geist Serif gains weights**: express tip radius as 0.5 × serif thickness (scales automatically). For brackets, use a weight-dependent stem factor falling from ≈ 0.40 (Regular) to ≈ 0.26 (Black), as Fraunces does, i.e. roughly constant in font units. Do not reuse Goeist Sans' constant 0.52 × stem, which over-rounds heavy weights relative to every reference.

11. **Italic**: none upstream yet. When it lands, apply the same profile. Souvenir/Fraunces show that soft italics need no extra rules beyond tip/terminal treatment.

12. **Keep G1 circular fillets** for family consistency. If curvature continuity is ever added, apply it to brackets ≥ 0.3 stem first (largest curvature jump against straight stems) `[inference]`.

Proposed profile sketch (names illustrative): `Profile("soft-serif", terminal=0.33, acute=0.22, circular=True, local_thickness=0.5, stadium=None)`, plus component-level serif and bracket reshaping before expansion (rules 2 and 4).
