# Geist Serif as upstream for Goeist Serif

Scope: provenance, structure and measured geometry of Geist Serif, and what a rounding profile for it must handle. Measurements were taken from a sparse clone of `vercel/geist-font` at tag `v1.9.2` (`ef2597c`, 2026-11-06), kept in `/tmp/geist-serif` and not vendored. Scripts used: `/tmp/gsa/m.py` (fontTools + skia-pathops scanlines and corner detection on the compiled static `GeistSerif-Regular.ttf`). Units are font units (UPM 1000).

## 1. Provenance and license

| Item | Value | Source |
|---|---|---|
| Announced | 2026-10-30, by Evil Rabbit and Mark Davis | [Vercel blog](https://vercel.com/blog/introducing-geist-serif) |
| Repo tag containing it | **`v1.9.2`** (`ef2597cfc42f4797676df105517ccc0a1cfa6569`) is the latest tag and already ships Serif. This is the **same tag Goeist already vendors**; only `Geist*.glyphspackage` and `GeistMono*` were copied into `sources/*/upstream/` | `git ls-remote --tags`, [repo](https://github.com/vercel/geist-font/tree/v1.9.2) |
| Source | `sources/GeistSerif.glyphspackage` (Glyphs 3 package, 922 `.glyph` files) | [tree](https://github.com/vercel/geist-font/tree/v1.9.2/sources/GeistSerif.glyphspackage) |
| Build | `scripts/build-geist-serif.py` + `scripts/glyphs_corners.py`; `make build-serif`; `requirements-serif.in` = fontmake, skia-pathops, ttfautohint-py, brotli | [script](https://github.com/vercel/geist-font/blob/v1.9.2/scripts/build-geist-serif.py) |
| License | SIL OFL 1.1, repo-wide `LICENSE.txt` ("Copyright (c) 2023 Vercel, in collaboration with basement.studio ... licensed under the SIL Open Font License, Version 1.1") | [LICENSE.txt](https://github.com/vercel/geist-font/blob/v1.9.2/LICENSE.txt) |
| Copyright string in source | "Copyright 2026 The Geist Project Authors (https://github.com/vercel/geist-font)" | `fontinfo.plist` |
| Designers (source) | "WORDMARK, Mark Davis, Andrés Briganti, Evil Rabbit" | `fontinfo.plist` |
| Reserved Font Name | none declared in LICENSE.txt (same as Sans/Mono), so "Goeist Serif" naming is unconstrained beyond OFL rules | [LICENSE.txt](https://github.com/vercel/geist-font/blob/v1.9.2/LICENSE.txt) |
| Version | 1.3 (`versionMajor 1`, `versionMinor 3`) | `fontinfo.plist` |
| Distribution | npm `geist` (`geist/font/serif/{regular,square,triangle,heart,variable}`); not on Google Fonts yet | [readme](https://github.com/vercel/geist-font/blob/v1.9.2/readme.md) |

Intended use: "a high-contrast display serif with fine, saw-toothed serifs and sharp hairlines" ([readme](https://github.com/vercel/geist-font/blob/v1.9.2/readme.md)). Display first; downstrokes were "thinned by 50%" and sidebearings tightened to push contrast; a text version and Thin–Black weights and a Python-generated italic are announced as future work ([blog](https://vercel.com/blog/introducing-geist-serif)). Stylistic lineage named by Vercel: Victor Serif, Stanley; Rolling Stone / Harper's Bazaar headline type ([blog](https://vercel.com/blog/introducing-geist-serif)).

## 2. Family structure

- **1 master** ("Regular", id `DCBCDAAA-...`), axis value ELSH=0. No weight axis, **no italic**. The variable instance carries a stale "Disable Masters: Thin, Black, Thin Italic, Black Italic" parameter, consistent with weights being in progress ([blog](https://vercel.com/blog/introducing-geist-serif)) `[inference]`.
- **Axis `ELSH` "Element Shape"**, range 0–100, default 0, no outline deltas (compiled VF has no `gvar`). Named instances: Regular=0 (round dots), Square=25, Triangle=50, Heart=100. Implemented as Feature Variations: `conditionset` ELSH 24.5–49.5 → ss02 glyphs, 49.5–74.5 → ss03, 74.5–100 → ss04, applied in `rclt`. Build script: "The ELSH axis only swaps glyphs through rclt, so the variable font carries no outline deltas." Statics are produced per instance with `Rename Glyphs` / `Replace Feature`. (Sources: `fontinfo.plist` feature code; [build script](https://github.com/vercel/geist-font/blob/v1.9.2/scripts/build-geist-serif.py).) The blog compares it to Geist Pixel's ELSH ([blog](https://vercel.com/blog/introducing-geist-serif)).
- **Glyphs**: 898 in compiled VF, 465 cmap entries (95 ASCII, 85 Latin-1, 113 Latin Ext-A, 12 Ext-B, 99 Latin Extended Additional, 61 other: punctuation, symbols, figures). Blog: 894 glyphs, 352 Latin languages, >52,000 kerning pairs; Cyrillic planned ([blog](https://vercel.com/blog/introducing-geist-serif)).
- **GSUB features**: aalt, case, ccmp, lnum, locl, onum, pnum, rclt, ss01–ss05, tnum (+ kern in GPOS). ss01 = alternate R, a, k (49 `.ss01` glyphs incl. accented); ss02/03/04 = square/triangle/heart dot glyphs (also reachable via ELSH); ss05 = alternate O/o/zero family. All three dot-set `featureNames` are labelled "Round dots" in the source (copy-paste bug upstream) `[observed]`.
- **Metrics** (source master): cap 710, x 530, ascender 800, descender -150, overshoot ±12; hhea/typo 1005/-295, win 1128/277. Blog table instead says ascender 750, descender -200 ([blog](https://vercel.com/blog/introducing-geist-serif)); source values win for the pipeline. Geist Sans: cap 710, x 530, hhea 1005/-295 (measured from vendored `Geist[wght].ttf`). Same vertical system.
- **Construction**: serifs are **Glyphs corner components**. 5 corner/cap glyphs, 359 placements in the source:

| Component | Placements | Role |
|---|---|---|
| `_corner.ucSerif` | 172 | caps foot/head serifs |
| `_corner.lcSerif` | 121 | lowercase serifs |
| `_corner.serif` / `_corner.serif-alt` | 23 | older/alt serif (some refs only in archived layers) |
| `_corner.numSerif` | 9 | figures |
| `_cap.stem` | 33 | lowercase head (flag) serif on i, j, n, m, r, u... |

78 glyph files reference corner components directly; composites inherit. Upstream notes "fontmake alone breaks the serifs, because they are Glyphs corner components, so glyphs_corners.py expands them (and the stroked rings of (c) and (R)) in a temporary copy first" ([build script](https://github.com/vercel/geist-font/blob/v1.9.2/scripts/build-geist-serif.py)). Several backup layers carry `Letterink-NibData`, i.e. serifs were explored with a nib/stroke tool.

`_corner.ucSerif` main-layer path (open, origin at stem/baseline corner, width 72):
`(0,75) ls → (0,57) o (-5,51) o (-21,42) cs → (-84,6) l → (-84,0) l → (10,0) l`.
Read: vertical stem edge, a short curved **bracket** (≈20 u), a straight **wedge** rising from tip to bracket, a **6 u vertical tip**, flat bottom. `_corner.lcSerif` identical shape at 81 u reach and 4 u tip. This matches "a wedge on one side and a curve on the other" ([blog](https://vercel.com/blog/introducing-geist-serif)): the "saw tooth" is an asymmetric wedge, flat on the baseline side.

## 3. Measurements (compiled `GeistSerif-Regular.ttf`, v1.9.2)

Source stem hints: vStem 33, hStem 84. GSDimensionPlugin values: HV 94, HH 35, nV 84, oV 100, oH 33, OV 114, OH 38, tH 56, nd 25.

| Glyph | Adv | Thick (scan) | Thin (scan) | Contrast | Corners (convex / concave) | Notes |
|---|---|---|---|---|---|---|
| H | 750 | stems 94 (y=120) | bar 35 | 2.7 | 16 / 4 | 8 serifs, each = 90° + ~60° corner pair 6 u apart; concave only at bar joins |
| I | 302 | 94 | – | – | 8 / 0 | serifs reach 84 u beyond stem |
| n | 602 | 83–84 | arch at apex 69 (x=cx) | – | 11 / 2 | foot serif tips 4 u; head serif tip 4 u at (26,483–487) |
| o | 604 | 99–100 | 33 | 3.0 | 0 / 0 | stress vertical |
| O | 792 | 117 | 37–38 | 3.1 | 0 / 0 | |
| a | 549 | 87–90 | 34–36 | 2.6 | 6 / 3 | spur at bowl/stem with 2 u segments |
| e | 557 | 107 (bowl, y=150) | bar 35, top 30 | 3.6 | 5 / 1 | terminal cut ~12 u long edge at (498–508,142–148) |
| s | 470 | spine 92 | 34 | 2.7 | 6 / 0 | both terminals are vertical cuts 4 u high: (48,168)-(52,169), (386–390,360) |
| g | 491 | 84–96 | 29–32 | 3.3 | 2 / 7 | ear corner (501,573); many concave joins (ear, link) |
| R | 621 | stem 94, leg 95–109 | 35 | 2.7 | 11 / 3 | leg foot corners at (604,0)/(614,8) |
| i | 288 | 84 | – | – | 7 / 0 | dot 110 u tall, gap 76 u above x-height |

Whole cmap (465 glyphs, threshold 25° tangent break): **5,826 corners, 872 concave, 2,597 corners with an adjacent edge ≤ 8 u** (serif tips and terminal cuts).

Dots (`period`, bbox):

| Variant | ELSH | bbox | Outline |
|---|---|---|---|
| Regular | 0 | 140 × 136 (35,-12)–(175,124) | 4 quad segments (circle-ish, overshoots baseline) |
| Square | 25 | 113 × 113 | 4 lines |
| Triangle | 50 | 150 × 130 | 3 lines (equilateral-ish, point up) |
| Heart | 100 | 150 × 133 | 6 curves (has a cusp at top and a point at bottom) |

Sans comparison (vendored `Geist[wght].ttf` at wght 400): lowercase stem 84 = Serif 84; cap stem 90 (Sans) vs 94 (Serif); widths are close but not equal (H 713/750, n 581/602, o 573/604, s 520/470, g 594/491, R 672/621). The blog's "stems match Geist Sans, and the two share widths and postures" is approximate; the Serif is a separate drawing, not a Sans outline with added serifs `[inference from measurements]`. Thick strokes match Sans; thin strokes are ~33–38, i.e. about Geist Sans Thin's stem (32) ([vendored Sans stems](../sources/Goeist/upstream/Geist.glyphspackage/fontinfo.plist): Thin 32/30, Regular 90/84).

## 4. What makes rounding hard

1. **Serif tips 4–6 u.** A stem-relative radius (Goeist Sans terminal 0.52 × 84 ≈ 44 u) is about 8× the tip thickness. Each tip is a *pair* of convex corners (90° at the baseline, ~120° turn at the wedge top) 4–6 u apart; filleting them separately is impossible past r ≈ 3 u.
2. **Wedge length ≈ 65–75 u at ~30° slope** ((-84,6)→(-21,42): rise 36 over run 63 → 29.7°). The tip is effectively an acute ~30° point with its end cut off. Rounding to a visible radius moves material, it does not just trim a corner.
3. **Contrast 2.6–3.6.** One stem-based radius is wrong for both thick (84–117) and thin (29–38) strokes. Any fillet with r > ~0.5 × local thickness eats through hairlines (bar of e at 30 u, hairline of g at 29 u).
4. **Terminal cuts 4 u (s, c, e, a).** Chisel terminals have no thickness to round; they need reshaping into a ball/blob or a rounded flare.
5. **Concave joins (872).** Mostly bar/stem joins, the g ear/link, k/x crotches; serif brackets are already smooth curves (no tangent break), so the Goeist rule "leave concave sharp" is compatible with brackets.
6. **Corner components.** fontmake does not expand them; the Goeist pipeline (glyphsLib) will see unexpanded serifs unless it uses upstream's `glyphs_corners.py` expansion first. Rounding expanded outlines treats 359 serif placements as independent geometry and risks inconsistency.
7. **Stroked rings in © ®** are also expanded by upstream's script and must be handled before rounding.
8. **Dot variants**: Square and Triangle dots are pure polygons; Heart has a cusp and a bottom point; Regular dot is already round. ELSH is substitution-only, so dot rounding is per-glyph, never per-delta.

## Implications for Goeist

Ranked by importance.

1. **Vendor `sources/GeistSerif.glyphspackage` from the already-pinned `v1.9.2`.** No new upstream tag is needed; add it to `sources/GoeistSerif/upstream/` alongside the existing OFL/LICENSE copy and manifest. Also vendor (or port) upstream `scripts/glyphs_corners.py` behaviour: corner components and the © ® stroked rings must be expanded before any outline work.
2. **Round the serif at the component level, not per glyph.** Edit the 5 corner/cap glyphs (`_corner.ucSerif`, `_corner.lcSerif`, `_corner.numSerif`, `_corner.serif-alt`, `_cap.stem`) in the temp copy *before* expansion. 359 placements then inherit one consistent soft serif. Per-glyph corner detection would otherwise hit 2,597 corners with edges ≤ 8 u.
3. **Reshape serif tips, do not fillet them.** Replace each tip's 90° + wedge corner pair with one arc: thicken the tip from 6/4 u to about **0.30 × stem (≈ 24–28 u)** and close it with a semicircle of r = tip/2 (≈ 12–14 u), keeping the flat baseline side, the wedge slope (~30°) and the bracket. This gives the Souvenir-like soft blob tip; a 3 u radius on the existing tip would be invisible. Keep serif reach (84 / 81 u) unchanged so spacing and kerning (52k pairs) stay valid.
4. **Make the radius local-thickness-relative.** New profile parameter: `r = min(k × stem, f × t_local)` with `t_local` the stroke thickness measured perpendicular at the corner (scanline/pathops ray cast as in `/tmp/gsa/m.py`), `f ≈ 0.45`. Suggested classes: thick ≥ 70 u (stems 84–117) → stem rule (terminal 0.52 × 84 ≈ 44, acute 0.22 × 84 ≈ 18); thin ≤ 40 u (hairlines 29–38) → `r ≤ 0.45 × t` ≈ 13–17 u; between → linear. Measure stem from `nV` = 84 (cap HV 94).
5. **Terminal cuts (s, c, e, a, r, f, j, y and similar, with edges ≤ 12 u) become ball/soft terminals.** Detect convex corner pairs closer than 0.25 × stem and replace them with one arc of diameter = the local thickness after a short thickening, the way rule 3 handles serifs. Rank: s, c, e, a, r, f, g ear, j, y, then figures.
6. **Leave concave corners and brackets sharp, as the current pipeline does.** Brackets are already smooth (`cs` nodes), and the 872 concave corners are hairline/stem joins where a concave fillet would thicken the hairline junctions and blur contrast.
7. **Dots per ELSH variant**: Regular: keep (already round). Square (113 u): round all 4 corners with r ≈ 0.25 × side ≈ 28 u (soft square, not a stadium). Triangle (150 × 130): r ≈ 20 u on all 3 vertices. Heart: round the bottom point (r ≈ 15 u) and keep the top cusp as concave. Apply to every `.ss02/.ss03/.ss04` dot glyph and to base glyphs whose dots are not components (check component usage before editing). Keep ELSH as substitution-only (`rclt` conditionsets); no `gvar` work is needed.
8. **Keep G1 fillets**, as in the current pipeline, for consistency across the family; at display sizes and high contrast the tip blobs are where G2 would be most visible `[inference]`. G2 is optional on serif tips only.
9. **Pipeline guards**: refuse any fillet whose two tangent points come closer than 2 u, or whose arc would cut a hairline below 0.8 × its original thickness. Report per-glyph counts (corners rounded/skipped) so the 465-glyph cmap can be reviewed. Check output with skia-pathops `simplify` (upstream already does `removeOverlaps`).
10. **Metadata**: one Regular weight, no italic, axis ELSH 0/25/50/100 with the same instance names. Fix the copy-pasted "Round dots" featureNames in our build: ss02 = Square, ss03 = Triangle, ss04 = Heart. Use source vertical metrics (asc 800 / desc -150 / hhea 1005/-295), not the blog table. The copyright line must add the Goeist authors, keep "The Geist Project Authors" and keep the OFL text.
