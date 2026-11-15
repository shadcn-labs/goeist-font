# Goeist Sans and Goeist Mono 1.000: geometry and design audit

Scope: the committed variable fonts `fonts/Goeist/variable/*.ttf` and `fonts/GoeistMono/variable/*.ttf`, compared against the unrounded baseline that `make test` builds from the same pinned sources (`build/<Family>/baseline/variable/*.ttf`). This avoids the 1.700/1.800 drift in the older reference binaries under `sources/*/upstream/reference/`. Nothing in the repo was modified or rebuilt.

Method. All scripts live in `/tmp/goeist-audit/`, outside the repo. Pillow, freetype-py, scipy and matplotlib were installed into a temp venv at `/tmp/gaudit-venv`.
- `fillet_stats.py` runs in the repo venv. It imports `scripts/rounding.py`, runs `prepare_corners` in memory over the upstream `.glyphspackage` sources, and logs every accepted fillet: turn, requested trim, actual trims, edge lengths and effective radius.
- `analyze_base.py` instantiates each font at wght 100/400/900 and removes overlaps with skia-pathops. It then computes the area ratio (rounded / baseline) per glyph, plus the sharp ink-convex corners (turn ≥ 20°, and ≥ 45° for "real" ones) still left in the final outline.
- `render.py` writes diff sheets at large ppem: grey is shared ink, red is ink the rounding removed, blue is ink it added. `smalltext.py` writes 10–18 px text strips.
- `fonttools varLib.interpolatable --json` was run on all eight variable fonts.
- Comparison PNGs are in `/tmp/goeist-audit/*.png` and are described in the text below; none are in the repo.

## 1. Pipeline report summary

### Measured stems and radii (`build/*/rounding-*.json` → `masters`)

| Family / style | Master | Stem (u) | Terminal r | Acute r | Stem samples min/max |
| --- | --- | --- | --- | --- | --- |
| Goeist upright | Thin / Regular / Black | 32.0 / 86.0 / 196.0 | 16.6 / 44.7 / 101.9 | 7.0 / 18.9 / 43.1 | Black 18.9–222.3 |
| Goeist italic | Thin / Italic / Black | 30.5 / 85.9 / 195.9 | 15.9 / 44.7 / 101.9 | 6.7 / 18.9 / 43.1 | Thin 8.0–38.0 |
| Goeist Mono upright | Thin / Regular / UltraBlack | 32.0 / 86.0 / 175.0 | 16.6 / 44.7 / 91.0 | = terminal | UltraBlack 11.1–195.5 |
| Goeist Mono italic | Thin / Italic / Black | 30.6 / 85.9 / 174.9 | 15.9 / 44.6 / 90.9 | = terminal | Thin 8.1–38.5 |

The stem is the median of 20–24 scanline samples from H, I, n and h (`rounding.py:266-287`). The minimum values (8–19 u) show the scan also catches thin non-stem spans. The median absorbs them for now, but nothing rejects outliers.

### Corner classification counts

| | Goeist up | Goeist it | Mono up | Mono it |
| --- | --- | --- | --- | --- |
| convex, rounded | 5995 | 6523 | 6762 | 7593 |
| concave, left sharp | 1271 | 1182 | 1389 | 1434 |
| hidden/overlapping, left sharp | 1303 | 1570 | 1664 | 2049 |
| stadium-promoted corners | – | – | 2857 | 3213 |
| `local_radius_reduction` | 49 | 51 | 4 | 4 |
| `compatible_unmoved_counterparts` | 12 | 9 | 6 | 14 |
| exact-geometry glyphs | – | – | 172 | 172 |

`local_radius_reduction` by glyph. Factor is the radius multiplier; 1/32 is effectively sharp.
- Goeist upright: uni4F55 何 22 corners, down to 1/16 at Black; ni-hira に 16, down to 1/8; so-hira そ 8, down to **1/32** at Black. Also Tse-cy Ц and tse-cy ц at Black 0.5, and at @ at Black 0.25.
- Goeist italic: the same CJK/kana glyphs, plus n and eng at Black Italic 0.5 (node 24/15), threesuperior and fivesuperior at Italic 0.5, and @ at 0.5.
- Mono: upWhiteArrow ⇧ at UltraBlack 0.25/0.5, ze-cy з and be-cy б at Black 0.25, and @ at 0.25.

`compatible_unmoved_counterparts` marks a corner that is rounded in some masters but has a zero-length support cubic in others:
- Sans: Eng (Black), rupeeIndian ₹ (Regular and Black node 3), 世 今 何.
- Mono: uhorn and Uhorn, Lje-cy Љ and lje-cy љ, rupeeIndian, and the italic ligatures `slash_equal_equal`, `greater_equal_greater`, `greater_greater_equal` and `less_equal_less`.

Every one of these corners shows up as a residual sharp corner in the final font at the unrounded weights (issue 3).

### Verification and Fontspector

- `out/*/verification.json`: `ok: true`, 0 failed (1336 passed for Sans, 1337 for Mono). The only geometry assertion is `meaningful-rounding`: each glyph's outline changed by more than `max(0.25, area·5e-5)` (`verify.py:388-395`). No check covers residual sharp corners, kinks, radius consistency or ink loss.
- Fontspector `interpolation_issues`: Goeist has 179 "Kink" warnings across 124 glyph entries; Mono has 58 across 52 (`out/*/fontspector/report.md`).
- Fontspector `overlapping_path_segments` (Mono): `uni0459` has a zero-length quad at (420,530), the support cubic from `compatible_unmoved`, and `less_greater.liga` has duplicated line segments.
- Goeist Italic `suspicious_sidebearings`: uni03020301. Not rounding-related.
- The other warnings (WWS bit, avar, vendor ID, subsets, description length) concern metadata, not outlines.

## 2. Issues, prioritized

Severity scale: **Critical** means visibly wrong glyphs in core Latin. **High** means visible defects or systematic inconsistency. **Medium** is noticeable at display sizes. **Low** is cosmetic or a process gap.

### 1. Critical (Mono): the stadium rule fires on non-simple contours, so L, N, M, V, г, И get radius up to 1.5 stem
- **Glyphs** (Mono, both styles): `L`, `N`, `M`, `V`, `W`, `ge-cy` г, `Ii-cy`/`ii-cy` И и, `em-cy` м, `ustraight-cy`, `Yusbig-cy`, `greater`, `greaterequal`, `asciicircum`, `bar_greater.liga`, `less_bar_greater.liga`, `greater_equal.liga` and the circumflex combos.
- **Evidence**:
  - Effective fillet radius at Thin is 1.5 stem for L and г, 1.17 for N and И, 1.03 for M, about 0.83 for W, 0.75 for V. At Regular, L and г are still 1.5 stem (129 u). The correct value is ≤ 0.52.
  - These contours are single all-line contours whose total turning is −720° (L, V, г), −1080° (N, И) or −1440° (M). The construction loops back on itself, so the polygon is not simple.
  - Area ratio at Regular: L 0.945, E 0.980.
  - `mono-NMVL.png` at Regular: the bottom-left corner of L and the top-left corner of г are swept into a quarter-circle about 1.5 stems wide, while H's corners are tight. N's acute junction corners are oversized too.
- **Cause**:
  - `convex_polygon_width` (`rounding.py:333-347`) tests only that every local turn has the same sign. A self-looping polygon passes.
  - `prepare_corners` then applies `radius = max(radius, stadium)` to every corner of the contour (`:418-420`).
- **Fix**: accept a contour as a stadium candidate only if all of these hold: the turns sum to ±360° (±1°), the polygon is simple (no proper edge intersections), it has no child contour inside it, and its area is ≤ k·stem² (k ≈ 6). Add a regression test with Mono L/N.

### 2. High (Mono): the stadium rule and the round nib blunt framed shapes and arrowheads
- **Glyphs**:
  - `clear` ⌧ U+2327, `deleteLeftKey` ⌫, `increment` ∆: radius 1.5 stem at every weight.
  - `*Arrow.ss07`, `arrowright.ss07` and the other ss07 arrows, `upWhiteArrow`, `uni23CE` ⏎.
- **Evidence**:
  - ⌧ area ratio at UltraBlack is 0.754, the worst in the font. In `mono-zoom.png` its outer frame becomes a stadium while the inner window stays a sharp rectangle, so the frame nearly breaks through at the corners.
  - `arrowright.ss07` at wght 900: bbox (12,140,594,559) becomes (12,223,523,476). The tip recedes by 71 u and the head loses 40% of its height; area ratio is 0.817.
  - The default `arrowright` tip recedes by 38 u.
- **Cause**:
  - The outer contour of a frame is convex, so it gets the stadium radius min(w/2, 1.5·stem) (`:407-408`) even though it has a hole.
  - With `acute = 0.52`, the trim at a 45° tip is r·tan(67.5°) = 2.4r, clipped at 0.48 of the edge (`:352-358`). A disc of radius r in a wedge with interior angle φ pulls the apex back by r(1/sin(φ/2) − 1), which is 1.6r for φ = 45°.
- **Fix**:
  - Exclude contours that contain other contours from the stadium rule (as in issue 1).
  - Add pictographic blocks (U+2190–21FF, U+2300–23FF, the `.ss07` arrows) to `exact_geometry`, or give them a reduced-radius profile.
  - For apexes with turn > 110°, cap the radius so the apex recession is ≤ 0.15 stem, or move the apex outward by the recession (apex overshoot).

### 3. High (both): exposed convex corners left sharp
After overlap removal, these glyphs still have sharp ink-convex corners with turn ≥ 45°. Excluded from the count: Mono exact-geometry U+25xx, block elements and `.notdef`.

| Font | wght 100 | 400 | 900 |
| --- | --- | --- | --- |
| Goeist | 19 glyphs | 18 | 18 |
| Goeist Italic | 23 | 18 | 16 |
| Goeist Mono | 33 | 35 | 36 |
| Goeist Mono Italic | 45 | 30 | 37 |

- **Glyphs and coordinates** (wght 400 unless noted):
  - Cyrillic descender letters Җ җ Қ қ Ң ң Ҳ ҳ Ҷ ҷ Ү: one corner each at the baseline, e.g. uni0496 (787,0) at 90°.
  - Љ Њ: Sans (592,0) at 113°; Mono (369,710).
  - ™: four corners at y=710, at 90° and 110°.
  - √ radical: (359,710) and (173,−150).
  - ₹: (92,705) and (92,634).
  - ę eogonek: (467,66) at 121°.
  - Ѫ uni046B: two corners at 48°.
  - Sans `lozenge`: 4 corners at 118°.
  - Eng at Black: (495,0).
  - Mono: `l.ss03` (330,710); `uhorn` and ư-family Black (326,540); `less_bar.liga` and `bar_greater.liga` at the baseline (342,0); `equal_less_less`, `greater_greater_equal` and `less_equal_less` at the `=`/`<` junction (113,253) and (113,381); the `bar_*_greater` ligatures (italic).
- **Cause**:
  - (a) Flush or coincident overlaps between contours or components. `ink_side` probes 0.22 u or more on each side of the edge (`:298-302`), gets inconsistent answers, and the corner is filed as `hidden_or_overlapping_construction_corner` (`:319-326`). Example: the descender component on Җ abuts the leg.
  - (b) `compatible_unmoved_counterparts` (`:664-677`): a corner rounded in one master gets a zero-length cubic in the others, so it stays sharp at those weights and is only partly rounded in between (₹, Ŋ, Љ, ư).
- **Fix**:
  - Classify exposure against the overlap-removed union of the layer's ink, computed with pathops as `InkGeometry` already does (`:197-253`). Only then map corners back to source contours.
  - When some masters can round a corner and others cannot, use the smallest safe radius in every master rather than zero.
  - Add a residual-convex-corner gate to `verify.py`, with an allowlist for exact-geometry ranges.

### 4. High (Sans): a step function at a 110° turn gives similar apexes different radii
- **Evidence** (`fillet_stats` at Regular):
  - In `y`, the right arm's outer top corner (turn 109.8°) is classed *terminal* and trimmed by 0.74/0.51 stem. The left arm's outer top corner (110.5°) is classed *acute* and trimmed by 0.32/0.32. That is a 2.3× difference on a symmetric letter.
  - `v` uses 0.31 at both top corners (110.0°). `V` and `A` (109.8–109.9°) get 0.74.
  - Across masters, A and V feet are 110.3–111.5° at Thin (acute, 0.22 stem) and 109.8° at Regular and Black (terminal, 0.52 stem), so their radius ratio jumps 2.4× along the weight axis.
  - 30 corners flip class between masters in upright, 27 in italic: A, V, y, Λ, eth, Ѫ, ≥, ‹ alternates, the combining acute/grave/hook marks and their stacks, and in italic S, e, ę, €, ∫, ∂.
  - 63 upright and 76 italic corners sit within ±5° of the threshold.
  - `sans-yvV-700.png`: y shows a large red cut on the right arm and a sliver on the left. V and A show large cuts, v small ones.
- **Cause**: `classify_corner` uses `profile.terminal if abs(turn) <= 110° else profile.acute` (`rounding.py:329`; profile in `families.py:34`).
- **Fix**: make the radius a continuous function of the turn angle. For example, r(θ) = stem·[terminal − (terminal − acute)·smoothstep((θ − 95°)/30°)], evaluated on the **mean turn across masters** so that each corner has one class per glyph. Better still, set the radius so the apex recession r(1/sin(φ/2) − 1) is constant (issue 9).

### 5. High (both): interpolation kinks at curved terminals
- **Evidence**:
  - `fonttools varLib.interpolatable` reports **0** issues on all four baseline fonts.
  - On the rounded fonts it reports: Goeist 25 kinks in 19 glyphs (S, g, five, dollar, braces, ª, ³, ⁵, ⁶, ⁹, ₉, nine.numr/dnom, Ω, З, ₴, ⑨, ǥ); Goeist Italic 26 in 25 (e, æ, ę, ə, ә, g, three, five, question ×4, §, breve marks, б, З, ₴, ⁹); Mono 8 in 7 (s, question ×4, ª, `asciitilde_at.liga`); Mono Italic 15 in 15 (e, s, §, ə, б, nine.numr/dnom, ³⁄₈, ⁵, ⁶, ⁹, ₉, ⑨, `asciitilde_equal.liga`).
  - Fontspector lists more (179 and 58 entries).
- **Cause**:
  - `write_contour` marks the junction node between the retained subcurve and the fillet as smooth (`:460-461`), and the fillet handles are `alpha·distance` computed per master (`:374-377`).
  - Interpolating collinear triples (h₁ = a·u, h₂ = b·u) stays collinear only if a/b is the same in every master or u does not change. At curved terminals both the tangent direction u and the trim ratios (0.48 clamp vs the nominal value) change from Thin to Black.
- **Fix**: make the handle-length ratio at each smooth junction identical across masters. Either compute the trim as the same fraction of the segment in all masters, or post-adjust handle lengths so that a_m/b_m is constant (fontTools' kink test is the acceptance check). Add `interpolatable` to `make test`.

### 6. Medium (Sans): per-edge trimming makes fillets elliptical and asymmetric
- **Evidence**:
  - Ratio of the larger to the smaller trim within one fillet:

    | Master | > 1.2 | > 1.5 | > 2 |
    | --- | --- | --- | --- |
    | Thin | 376 | 67 | 13 |
    | Regular | 430 | 144 | 28 |
    | Black | 912 | 496 | 192 |
    | Black Italic | 1008 | 527 | 186 |

  - At Black:
    - t and f crossbar ends: 0.52/0.34 stem (1.53×).
    - E arm ends: 0.52/0.38 (1.37×).
    - **r ear: 0.12/0.38 and 0.38/0.11 (3.2–3.5×)**; at Regular 0.28/0.45 (1.6×).
    - t tail terminal: 0.34/0.18.
    - i dot: a wide rectangle that becomes an ellipse.
  - Glyphs with fillets above 2× at Black: 83 upright (a & @ b , d $ e g l 1 r y …) and 101 italic.
  - `sans-zoom-black.png`: crossbars end in elliptical caps, and the r ear stays nearly square beside fully round stems. In `sans-dots-r-t.png` the i dot is an ellipse.
- **Cause**: `circular=False` → `trim_in, trim_out = min(trim, 0.48·len_in), min(trim, 0.48·len_out)` (`rounding.py:359-360`). The circular-arc handle formula (`:374-375`) is then applied to an asymmetric corner, so the arc is neither circular nor elliptical, just a sheared quarter-circle.
- **Fix**: use circular fillets everywhere and shrink r to fit, as `round-nib` already does. If a softer look is wanted, use a smaller radius (issue 10) rather than asymmetric trims.

### 7. Medium (both): dots change shape across weights and lose ink; tittles and periods disagree
- **Evidence**:
  - Sans `period` radius relative to its half-width is 0.56 at Thin, 0.79 at Regular and 0.96 at Black. The dot morphs from rounded square to squircle to circle along the axis, while stems are about 0.96 at every weight.
  - Sans area ratio for period, colon, ellipsis and ·: 0.937 / 0.868 / 0.804. Dieresis and dotaccent: 0.901 / 0.814 / 0.806. i: 0.976 / 0.941 / 0.898.
  - Mono period: circle at all weights (0.96), area 0.81–0.83.
  - Mono i and j dots (wide rectangles) become horizontal pills, unlike the circular period (`mono-zoom.png`).
  - A circle inscribed in a square keeps π/4 = 78.5% of its area, so rounded dots look smaller and lighter than the stems.
- **Cause**: Sans has no stadium rule (`families.py:34`); Mono's stadium uses the min-caliper width (`:346`), so a non-square dot becomes a pill.
- **Fix**: treat convex dot contours (area < 2·stem², 4 line edges) as dots. Replace each with a circle of equal area, d = 2·√(A/π) ≈ 1.128·side, centred on the original, provided clearance to the neighbouring ink is at least 0.3 stem. Apply this to every weight and to both families.

### 8. Medium (italics): stem ends are lopsided
- **Evidence**:
  - Goeist Italic Regular `n`: the obtuse corner of the stem end (turn 78°) trims 0.42/0.42 stem (r = 0.52). The acute corner (102°) trims 0.64/0.47, which is non-circular, with r_out = 0.38.
  - Goeist Mono Italic: the two corners of the same stem end have r = 0.52 and r = 0.38 stem.
  - `sans-italic-black.png` and `mono-italic-black.png`: stem ends look tilted and blobby, and the italic i dot is a long sheared ellipse.
  - Diatype Rounded Ultra Italic, in Dinamo's [process screenshot](https://abcdinamo.com/news/release-notes-diatype-rounded), caps H with one continuous semicircle through an extreme node sitting in the overshoot zone below the baseline.
- **Cause**: each corner is filleted independently, and the 0.48 clamp (`:353`) hits the acute side first.
- **Fix**: detect a terminal (a short edge flanked by two convex corners whose turns sum to about 180°). Replace it with a single circular cap of diameter = stem width measured perpendicular to the stem axis, centred on that axis, with its extreme overshooting the alignment zone.

### 9. Medium (both): rounding acute corners loosens spacing and drops points below the alignment zones
Bboxes before → after:

| Glyph | wght | Before | After |
| --- | --- | --- | --- |
| Sans A | 400 | x 20–648 | x 38–630 (+18 u each side) |
| Sans A | 900 | x 18–753 | x 57–714 (+39 u each side) |
| Sans v | 900 | x 20–637 | x 38–619 |
| Mono A, V | 900 | – | about +19–22 u each side |
| Sans arrowright | 900 | xMax 750 | xMax 708 |
| Sans `>` | 900 | y 16–572 | y 36–552 |
| Sans `*` | 900 | yMax 727 | yMax 709 (below cap height 710) |
| Mono `*` | 900 | yMax 710 | yMax 690 |
| Mono `^` | 900 | – | 21 u narrower each side |

- **Effect**: advance widths and kerning are unchanged, so A V W v w y X x k and `< > ^ *` look more loosely spaced and smaller than straight-stem letters at heavy weights. Stems still touch y = 0 only over a 4% flat.
- **Fix**:
  - Compensate sidebearings by half the recession, or extend apexes and feet by the recession r(1/sin(φ/2) − 1) where they meet an alignment zone.
  - Add terminal overshoot, which Dinamo describes as essential: "We carefully adjusted all the over- and undershoots to reinforce the sturdy and balanced baseline, x-height, and cap height" ([Dinamo release notes](https://abcdinamo.com/news/release-notes-diatype-rounded)).

### 10. Medium (Sans, design decision): the `soft` profile is effectively a full round nib
- **Evidence**:
  - `terminal = 0.52` exceeds the 0.48·edge clamp (`:353`) on every stem-width edge, so all vertical stem ends trim to about 0.48 stem: a near-semicircle with a 4% flat, at every weight. 66–78% of Sans fillets are length-limited (Thin 66%, Regular 69%, Black 78%).
  - The documented 0.52 is never realized on stems, and rounding saturates at Black (`sans-lc-black.png`: n/h/m/i/l/r stems become pills).
  - Open Runde, the cited soft inspiration, measured from its OFL [v1.0.1 release](https://github.com/lauridskern/open-runde/releases/tag/v1.0.1) (UPM 2816):
    - Regular stem is 236 u with corner trim 90 u (**0.38 stem**); Bold stem is 426 u with trim 120 u (**0.28 stem**).
    - The radius grows sub-linearly (about stem^0.5) and leaves visible flats.
    - The same absolute radius applies to every corner of a weight (E arm ends 90 u at Regular).
- **Fix (decide)**: either rename and document Sans as a full-round profile, or adopt an Open Runde-like curve, for example r = min(0.40·stem, 0.48·edge) with exponent < 1 against weight, keeping flats ≥ 0.2 stem.

### 11. Medium (Mono): the "one chunky tool" is not one radius
- **Evidence**:
  - Effective radius / stem, 10th–50th–90th percentile: Thin 0.33–0.45–0.52; Regular 0.28–0.47–0.52; UltraBlack **0.20–0.39–0.52**.
  - At UltraBlack: r ear 0.31–0.35, `one` flag 0.18, slabs 0.36–0.44, stems 0.48.
  - Fillets below 0.3 stem: 179 (Thin), 246 (Regular), 596 (UltraBlack). In `mono-black.png` the r ear and the 1 flag read as nearly square against pill-ended slabs.
- **Cause**: `circular=True` shrinks r to 0.48 of the shorter edge (`:354-358`), and Geist Mono's heavy master thins its horizontals and terminals.
- **Fix**: for stroke terminals (issue 8 detection), cap the end with a full semicircle (r = half the terminal width) and accept a 0.5 rather than 0.48 limit there. Keep 0.48 only for corners between long edges.

### 12. Medium: local radius reductions are coarse and differ per master
- **Evidence**: the factors are 1, ½, ¼, …, 1/32 (`:422-436`). そ at Black 1/32 is sharp. Ц and ц are 0.5 at Black only (full at Thin and Regular). n and eng are 0.5 at Black Italic only. ³ and ⁵ are 0.5 at Italic only.
- **Fix**: bisect for the largest safe radius, then apply the minimum safe *fraction* across all masters of the glyph so that the radius/stem ratio is constant along the axis.

### 13. Low: G1-only joins produce a curvature step
- **Evidence**:
  - Goeist fillets use k = (4/3)tan(θ/4)/tan(θ/2), which is 0.552 for a 90° corner (`:375`; circular-arc approximation, see [Mortensen](https://spencermortensen.com/articles/bezier-circle/)). Curvature jumps from 0 on the straight to 0.98/d at the join, where d is the trim.
  - Open Runde handles are 58/90 = 0.64 (Regular) and 78/120 = 0.65 (Bold). For a 90° cubic with handle ratio k, the endpoint curvature is κ₀ = (2/3)(1−k)/(k²d): 0.586/d at k = 0.64, a 40% smaller step.
- **Effect**: visible only at display sizes, as a "ridge" where a semicircular stem end meets the stem sides.
- **Fix**: offer a `handle` parameter of about 0.60–0.65 (a superellipse-like corner), with the ink-containment check still applied.

### 14. Low: degenerate segments
`compatible_unmoved` support cubics are zero-length (`:464`). Fontspector flags uni0459's quad at (420,530) and duplicate segments in `less_greater.liga`. These can upset autohinting and some rasterizers. Fix: a minimum-radius fallback (issue 3) removes the need for them.

### 15. Low: TrueType integer quantization at Thin
- glyf coordinates are integers ([OpenType glyf](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf)).
- Sub-unit shifts of fillet endpoints tilt long diagonals by up to 0.5 u. That is enough to give `<` and `>` a 1.013 area ratio at Thin, slash and `(` 1.006–1.02 (Mono), and Λ 1.007.
- At Thin curved terminals (C S a c З 3 eth), the 2-unit flats left between fillets round to 22–27° false corners (C at (613,248)). Not visible, but it is noise in any automated corner check: use a ≥ 45° threshold or compare in source units.

### 16. Low / informational: small sizes
- The radius in pixels is trim·ppem/UPM. At Regular (about 41 u) that is 0.66 px at 16 px and 2 px at 48 px; at Black (about 94 u) it is 1.5 px at 16 px.
- `small-sans.png`: Goeist and Geist are indistinguishable at 10–14 px at 400 and 800, apart from slightly lighter dots and comma. At 18 px Bold the stem ends just begin to soften. The autohinted static is consistent with the variable font.
- The design only shows above about 24 px (Regular) or 16 px (Black).

### 17. Low (process): no geometry quality gates
`verify.py` asserts that rounding changed each glyph (`:388-395`), but none of issues 1–5 fail the build.

### Checked and not a defect
- Concave joins and counters are left sharp in Goeist, Open Runde and Diatype Rounded alike. In Open Runde Regular, E's inner corner (496,220) and n's crotch are plain line joins. Dinamo's H screenshot shows square nodes at the crossbar.
- n, h and m stems are consistent (0.48/0.52 stem; m's narrower middle stem 0.42).
- O, o and e lose 0–2% area. Upright Sans k and x acute junctions use 0.22 stem consistently.

## 3. Comparison with the stated inspirations

| Rule | Goeist Sans (`soft`) | [Open Runde](https://github.com/lauridskern/open-runde) (OFL, [license](https://raw.githubusercontent.com/lauridskern/open-runde/main/LICENSE.txt)) | Goeist Mono (`round-nib`) | [ABC Diatype Rounded / Rounded Mono](https://abcdinamo.com/typefaces/diatype-rounded) (proprietary, visual only; the evidence images show the proportional Rounded styles; the Mono is described as the "blueprint") |
| --- | --- | --- | --- | --- |
| Construction | per-corner cubic fillets, automatic | "made entirely with the rounded corners tool of Glyphs Mini" ([README](https://github.com/lauridskern/open-runde/blob/main/README.md)) | per-corner circular fillets plus stadium | "engraved with a chunky tool in one continuous line"; "We rounded those beauties one by one" ([release notes](https://abcdinamo.com/news/release-notes-diatype-rounded)) |
| Radius / stem | about 0.48 effective at all weights (0.52 nominal) | 0.38 at 400 → 0.28 at 700, sub-linear | 0.20–0.52 at Black, median 0.39 | full semicircle at stroke ends ([process image](https://abcdinamo.com/news/release-notes-diatype-rounded)) |
| Flats at stem ends | about 4% | about 24% at Regular | about 4% | none (one arc through an extreme node) |
| Corner shape | sheared or elliptical where clamped | symmetric, handle about 0.64 | circular | circular |
| Concave corners | sharp | sharp | sharp | sharp at crossbar joins (H in the process image) |
| Dots | rounded square → circle across weight | circles, Ø 1.53 stem at 400 | circle (period), pill (i/j) | round ([charset](https://abcdinamo.com/news/release-notes-diatype-rounded)) |
| Over/undershoot of rounded ends | none | none (n, i stem fillets end on y = 0 and 1536 in the Regular/Bold OTFs) | none | adjusted; the rounded end's extreme sits in the overshoot zone |
| Italic terminals | two independent fillets, lopsided | n/a (no italic) | two radii (0.52/0.38) | one semicircle on the slanted stem |

Open Runde ships only four static weights (400–700) and says variable is "Probably not" ([README](https://github.com/lauridskern/open-runde/blob/main/README.md)). It therefore never faces Goeist's Thin–Black interpolation problems (issues 4, 5, 12).

## Implications for Goeist

Ranked by importance. Each item names the pipeline change and what it means for Goeist Serif.

1. **Classify against the union, and fail on residual corners.** Compute exposure on the pathops union of each layer (`classify_corner` / `ink_side`, `rounding.py:298-330`). Add a `verify.py` gate: no ink-convex corner with turn ≥ 45° outside an allowlist, at wght 100/400/900 and two intermediates. Serif: bracketed serifs overlap stems flush, and component-built accents with descenders are common, so the false "hidden" class would leave a sharp serif corner on every such join.
2. **Fix stadium eligibility** (`convex_polygon_width`, `:333-347`): require a simple polygon, total turning of ±360°, no inner contour, and area ≤ 6·stem². Serif: wedge and saw-tooth serifs are convex polygons and must never be promoted to stadiums.
3. **Make the radius continuous in angle and consistent across masters.** Replace the 110° step (`:329`) with a smooth r(θ) evaluated on the mean turn across masters, and use one safe fraction per corner across masters (`:422-436`; replaces `compatible_unmoved`, `:664-677`). Serif: ELSH-like dot shapes and saw-toothed serifs produce many corners near any fixed threshold. A high-contrast design also varies its angles between Thin and Black.
4. **Keep handle ratios constant across masters at smooth junctions** (`make_corner` `:374-377`, `write_contour` `:460-461`). Run `fonttools varLib.interpolatable` in `make test` and require 0 kinks. Serif: its terminals are mostly curved (ball, beak, teardrop), so the kink rate would be far higher than in the Sans.
5. **Use circular fillets only; drop per-edge trimming** (`:359-360`). Size the radius against the **local edge thickness, not one global stem**. For a high-contrast serif the relevant thickness is the hairline: Geist Serif's thin strokes are a small fraction of the stem, so a fixed `0.52·stem` would clamp on every hairline serif and turn it elliptical. Measure both a vertical stem and a horizontal hairline per master (extend `measure_stems`, `:266-287`, with an e/o/H-bar hairline scan), then set r = min(k_t·local_thickness, k_s·stem).
6. **Treat terminals and dots as primitives, not corner pairs.**
   - Terminal cap: a short edge between two convex corners whose turns sum to about 180° becomes one semicircle perpendicular to the stroke axis, overshooting the alignment zone by about 1.5–2% of UPM, as Diatype does.
   - Dot: a small convex contour becomes an equal-area circle (d ≈ 1.128·side) at every weight.
   - This fixes italic lopsidedness, r/1/t terminals, i/j vs period, and the dot morph. Serif: ball terminals and the ELSH dot axis must keep their designed shape. Exclude glyphs whose dot shape varies along that axis, or round them with the same primitive per axis master.
7. **Compensate optics after rounding.**
   - Apex recession r(1/sin(φ/2) − 1): extend the apex, or cap the radius so recession is ≤ 0.15 stem.
   - Sidebearings: shift by half the recession for glyphs whose bbox shrinks by more than 5 u.
   - Arrows and pictographs: exact geometry or a reduced radius.
   - Serif: wedge serifs and sharp beaks have small φ. Under a fixed radius they recede most, shortening serif reach and loosening spacing exactly where a display serif depends on it.
8. **Choose the Sans character deliberately.** Either document a full-round profile, or move to an Open Runde-like softness (0.38 → 0.28 stem with flats kept). For Serif with a Souvenir-like goal, size the radii to keep soft flats on serifs (≈ 0.3–0.4 of serif thickness), not semicircles. Souvenir's serifs read as soft, not as pills (visual reference only; no data used).
9. **Offer a G2-ish handle option** (k ≈ 0.62, `:375`), for the display sizes where Goeist Serif will mostly be used.
10. **Add audit tooling to `make test`:** per-glyph area ratio vs the baseline per master (flag below 0.9 or above 1.01), radius/stem distribution per class, the class-flip count across masters (0 required), and Fontspector `interpolation_issues` / `overlapping_path_segments` treated as errors.
