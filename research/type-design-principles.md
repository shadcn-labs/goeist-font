# Type design principles for Goeist (Sans, Mono, future Serif)

Research note, 2026-11-14. Scope: what makes a good typeface in general, per genre (serif, sans, mono), and what changes when a design is rounded. Every rule links to its source. Tags:

- `[measured]`: numbers I measured from OFL or system font binaries with fontTools + skia-pathops (overlaps removed before area/scan measurements). Method: instantiate the variable font at the stated location, scan outlines horizontally/vertically, compare bounding boxes and filled area. Fonts measured: SF Pro (`/System/Library/Fonts/SFNS.ttf`) vs SF Pro Rounded (`SFNSRounded.ttf`) from macOS 26, [Source Serif 4 variable](https://github.com/adobe-fonts/source-serif) ([OFL](https://github.com/adobe-fonts/source-serif/blob/release/LICENSE.md)), [Google Sans Flex](https://github.com/google/fonts/tree/main/ofl/googlesansflex) ([OFL.txt](https://github.com/google/fonts/blob/main/ofl/googlesansflex/OFL.txt)), [Kode Mono](https://github.com/google/fonts/tree/main/ofl/kodemono) ([OFL.txt](https://github.com/google/fonts/blob/main/ofl/kodemono/OFL.txt)), and this repo's `sources/*/upstream/reference/*.ttf` vs `fonts/*/variable/*.ttf`. SF fonts are proprietary: measured for reference only, no data reused.
- `[derived]`: my own geometry/arithmetic from sourced premises.
- `[unverified]`: claim I could not confirm from a primary source.

Books named in the brief that I could not read directly (Cheng, *Designing Type*; Tracy, *Letters of Credit*; Smeijers, *Counterpunch*; Harvey): only cited via the publisher page or a source that quotes them. Michael Harvey was not consulted.

---

## 1. Universal principles

### 1.1 Optical corrections

| Rule | Detail | Source |
|---|---|---|
| Overshoot | Round shapes extend beyond flat alignment lines because "only a narrow sliver of an O is the full height"; pointed shapes get more overshoot than round ones. | [Frere-Jones, Typeface Mechanics 001 (Slate reprint)](https://slate.com/human-interest/2015/04/tobias-frere-jones-explains-the-optical-illusion-that-tricks-our-brains-into-perceiving-typeface-letters-are-of-equal-height.html); [GF glossary: overshoot](https://fonts.google.com/knowledge/glossary/overshoot) |
| Overshoot scales with curvature and bluntness | Slow (squarish) curves need less overshoot; "overshoot decreasing as bluntness increases" (heavier, blunter V apex needs a new alignment). | [Frere-Jones 001](https://slate.com/human-interest/2015/04/tobias-frere-jones-explains-the-optical-illusion-that-tricks-our-brains-into-perceiving-typeface-letters-are-of-equal-height.html) |
| Same top/bottom overshoot | Lowercase rounds overshoot the baseline by the same amount the top overshoots x-height; s and c are often slightly smaller than o; a pointed v descends below the baseline, a blunt one may sit on it. | [Microsoft character design standards, lowercase](https://learn.microsoft.com/en-us/typography/develop/character-design-standards/lowercase) |
| Cupped serifs straddle | Concave serifs straddle the baseline, rising and falling equally. | [Frere-Jones 001](https://slate.com/human-interest/2015/04/tobias-frere-jones-explains-the-optical-illusion-that-tricks-our-brains-into-perceiving-typeface-letters-are-of-equal-height.html) |
| Horizontals thinner than verticals | Horizontals look heavier at equal measure; "peel some weight from the horizontals". Futura's O is an ellipse inside a circle. | [Frere-Jones, Typeface Mechanics 002 (mirror)](https://stockholmstypografiskagille.se/typonyheter/typeface-mechanics-002/) |
| Curve "overmass" | Curves are heavier than straight stems at their crest: 12% (high-contrast Initiales Labeur), 9% (Candida), 1% (Memphis, monolinear slab). Overmass scales with contrast; no universal number. | [Frere-Jones 002](https://stockholmstypografiskagille.se/typonyheter/typeface-mechanics-002/) |
| Junction thinning / ink traps | Parallel strokes pile up weight where they cross; taper strokes into intersections, more as the angle gets more acute (x, v, W). Diagonals are thinner than the H stem; downstrokes (left-to-right descending) heavier than upstrokes. | [Frere-Jones 002](https://stockholmstypografiskagille.se/typonyheter/typeface-mechanics-002/); [TypeType UniversiTTy 7](https://typetype.org/blog/universitty-lesson-7-designing-basic-latin-characters-glyph-height-contrast-optical-sizes/); [GF glossary: ink trap](https://fonts.google.com/knowledge/glossary/ink_trap) |
| Apex compensation | A pointed apex looks short: cut it flat or extend it above the flat letters. | [TypeType UniversiTTy 7](https://typetype.org/blog/universitty-lesson-7-designing-basic-latin-characters-glyph-height-contrast-optical-sizes/) |
| Scaled parts are too light | Scaling a shape down (fake small caps) makes strokes visibly lighter; black and white must be rebalanced "neither arithmetic nor geometric". | [Frere-Jones 002](https://stockholmstypografiskagille.se/typonyheter/typeface-mechanics-002/) |
| Optical vertical centre | Sidebearings follow the optical, not mathematical, centre; they coincide only for symmetric glyphs (H, O). | [de Mello Vargas, Reading MA essay, §2.4](https://typeculture.com/wp-content/uploads/2016/02/tc_article_49.pdf) |
| Round vs straight widths | Decide O vs H stem difference and overshoot by testing in text; D slightly wider than H, narrower than O. | [TypeType UniversiTTy 7](https://typetype.org/blog/universitty-lesson-7-designing-basic-latin-characters-glyph-height-contrast-optical-sizes/); [Ohno Type School: D](https://ohnotype.co/blog/ohno-type-school-d) |
| Kill visible compensation when the style changes | In Cera Round, the 4 and + had optical H/V weight corrections that became "visible and distracting" once terminals were round; they were set mathematically equal. | [TypeMates, making of Cera Round](https://www.typemates.com/news/round-and-round-we-go-making-of-cera-round) |

### 1.2 Spacing and kerning

- **Tracy method.** Groups: upright, round, diagonal, odd letters; standards H/O (caps) and n/o (lowercase). H gets half its interior counter on each side for bold faces, less for regular and lighter; test `HHOHH`, `HHOOHH`; n's left side gets half its counter, right side a little less (arch); test `nnonn`, `nnonon`, `nnoonn`. Source chart reproduced in [de Mello Vargas §3.2.1](https://typeculture.com/wp-content/uploads/2016/02/tc_article_49.pdf) and [Society of Fonts part 1](https://www.societyoffonts.com/2018/09/19/spacing-a-font-part-1/), [part 2](https://www.societyoffonts.com/2018/09/26/spacing-a-font-part-2/); book: [Tracy, Letters of Credit (Godine 1986)](https://books.google.com/books/about/Letters_of_Credit.html?id=3FI8AQAAIAAJ). Tracy's method was built on serif faces; serifs make spacing easier because they mark the white at baseline/x-height ([de Mello Vargas §4](https://typeculture.com/wp-content/uploads/2016/02/tc_article_49.pdf)).
- **Starting ratios.** o sidebearing ≈ 1/3 of its counter width (more for small sizes, more for flat-sided bowls); n sidebearings ≈ 1.5× o, not counting serifs; shift n right inside its width to centre it optically between o's ([Glyphs: Spacing](https://glyphsapp.com/learn/spacing)).
- **Serif needs more space than sans** at equal x-height ([de Mello Vargas §3.3](https://typeculture.com/wp-content/uploads/2016/02/tc_article_49.pdf)).
- **Inner and outer white balance**: spaces between letters balance with counters ([Smeijers, Counterpunch, quoted in de Mello Vargas §2.2](https://typeculture.com/wp-content/uploads/2016/02/tc_article_49.pdf); [Hyphen Press](https://hyphenpress.co.uk/products/books/978-0-907259-42-8)). Open-counter letters are hardest to space because the boundary between inner and outer white is unclear (Tracy, same source).
- **Link metrics** with keys (`=n`, `=|a+20`) so changes propagate ([Glyphs: Spacing](https://glyphsapp.com/learn/spacing)).
- **Kern last**: only after spacing cannot be improved further ([Glyphs: Spacing](https://glyphsapp.com/learn/spacing)); "the better the spacing, the less kerning" ([Society of Fonts part 1](https://www.societyoffonts.com/2018/09/19/spacing-a-font-part-1/)).
- **Err loose for text**: typographers track in at large sizes more readily than they track out at small ones (Dave Crossland in the [Nunito rework thread](https://groups.google.com/g/googlefonts-discuss/c/eIWeNyhXal0/m/953AXA7lAAAJ)); added letter spacing is the attribute most consistently shown to improve ease of reading ([Biľak, Typotheque](https://www.typotheque.com/articles/sans-for-small-text-sizes)).

### 1.3 Vertical metrics (Google Fonts profile)

From [GF Guide: Vertical metrics](https://googlefonts.github.io/gf-guide/metrics): not editor-computed; identical across the family; `USE_TYPO_METRICS` on; `winAscent/winDescent` = family yMax/|yMin|; hhea = typo; LineGap = 0; caps centred (`typoAscender − capHeight = |typoDescender|`); `typoAscender` ≥ tallest `Ắ` (U+1EAE); sum ≈ 120–130% UPM. Once published, line height must not change. [Glyphs: Vertical metrics](https://glyphsapp.com/learn/vertical-metrics) restates the same scheme.

### 1.4 Consistency checks / QA

- Google Fonts now uses Fontspector, successor of Font Bakery ([GF Guide: QA](https://googlefonts.github.io/gf-guide/qa.html); [fonttools/fontspector](https://github.com/fonttools/fontspector)).
- Outline checks relevant to programmatic rounding: `outline_alignment_miss`, `outline_short_segments`, `outline_colinear_vectors`, `outline_jaggy_segments`, `outline_semi_vertical`, `outline_direction`, plus `googlefonts/vertical_metrics`, `googlefonts/use_typo_metrics`, `googlefonts/family/tnum_horizontal_metrics`, `googlefonts/varfont/has_HVAR` ([Font Bakery Google Fonts profile](https://fontbakery.readthedocs.io/en/stable/fontbakery/profiles/googlefonts.html)) and `opentype/monospace` ([OpenType profile](https://fontbakery.readthedocs.io/en/stable/fontbakery/profiles/opentype.html)). Check names are Font Bakery's; Fontspector reuses them `[unverified per check]`. Fillets create short segments near corners; expect `outline_short_segments` warnings to need triage.
- Glyphs-side: mekkablue *Kink Finder*, *Find Shapeshifting Glyphs*, *Travel Tracker*; Glyphs compatibility view ([Glyphs: MM part 2](https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)).

### 1.5 Proofing

- Print and proof at intended size; one designer regretted not printing while spacing and had to respace ([Society of Fonts part 1](https://www.societyoffonts.com/2018/09/19/spacing-a-font-part-1/)).
- Proof every interpolated instance, not just masters: Ohno Softie's Medium "looked muddled" until a middle master re-anchored it ([Ohno: Softie](https://ohnotype.co/blog/the-process-of-ohno-softie)).
- Proof in live contexts (real websites using the family) ([Nunito thread](https://groups.google.com/g/googlefonts-discuss/c/eIWeNyhXal0/m/953AXA7lAAAJ)).
- Compare releases visually with diffenator2 ([GF Guide: metrics](https://googlefonts.github.io/gf-guide/metrics)).

### 1.6 Interpolation-compatible design

- Same number/order of paths, nodes, handles, anchors, components in all masters ([Glyphs: MM part 2](https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)).
- Kinks appear when a smooth triplet changes angle *and* ratio between masters; fix by removing the triplet, syncing angles (keep smooth points at extrema, H/V handles), or syncing ratios ([same](https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)).
- Keep overlaps for editing and interpolation; remove at export ([same](https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)); "overlap with triangles" lets ball terminals change without touching the stroke ([Ohno: Drawing vectors](https://ohnotype.co/blog/drawing-vectors)).
- Points on extrema, shared curve tension (point–point line parallel to handle–handle line) ([Ohno: Drawing vectors](https://ohnotype.co/blog/drawing-vectors)).
- Very different extremes need intermediate masters (Softie) ([Ohno](https://ohnotype.co/blog/the-process-of-ohno-softie)).

### 1.7 Weight progression

- **De Groot**: optically even intermediate weights lie on a hollow curve below the straight line; for Regular 40 / Bold 70, SemiBold is "slightly less" than 55 ([LucasFonts: Interpolation Theory](https://www.lucasfonts.com/learn/interpolation-theory)). Mathematically a geometric sequence, `stem_i = stem_A · (stem_B/stem_A)^((i−A)/(B−A))` ([Romer, TypeDrawers](https://typedrawers.com/discussion/2665/a-generalization-of-lucas-de-groot-s-interpolation-theory); example Thin 92 → Black 162 in 4 steps: 92, 111, 134, 162, [TypeDrawers](https://typedrawers.com/discussion/comment/23216)).
- **Anisotropic, topology-dependent**: horizontals grow slower than verticals, and the more horizontals share the height (L: 1, F: 2, E: 3, € : 4) the less each can grow; intermediate contrast should be slightly lower than linear ([LucasFonts](https://www.lucasfonts.com/learn/interpolation-theory)).
- **Grade**: GF registry `GRAD` changes typographic colour without changing widths ([GF axis registry metadata](https://fonts.google.com/metadata/fonts)); Input ships finer weights to offset halation of light-on-dark ([Input info](https://input.djr.com/info)).

---

## 2. Serif

### 2.1 Contrast and stress

- Noordzij: contrast is "the flow of the width in strokes"; three kinds: **translation** (counterpoint length and direction constant; stiff broad pen; strokes are lozenges), **expansion** (counterpoint length varies; flexible pointed pen; strokes are trapezia), **rotation** (counterpoint direction varies; mannerist calligraphy). A "monoline" stroke is the stroke of a more or less circular tool. Primary source: [Noordzij, "The shape of the stroke", RIDT 1991, pp. 35–37 (KABK Type]Media PDF)](https://typemedia.org/assets/download/The%20Shape%20of%20the%20Stroke,%20RIDT%201991,%20pp%2034-42_low.pdf); book: [The stroke (Hyphen Press)](https://hyphenpress.co.uk/products/books/978-0-907259-30-5).
- Stress axis = line through the thinnest parts of rounds; in calligraphic/old-style designs all rounds share one slant and the widest parts are perpendicular to it ([TypeType UniversiTTy 9](https://typetype.org/blog/universitty-lesson-9-uppercase-characters-detailed-contour-refinement/)). Keep the chosen contrast system consistent or the font reads as unrelated letters ([TypeType UniversiTTy 7](https://typetype.org/blog/universitty-lesson-7-designing-basic-latin-characters-glyph-height-contrast-optical-sizes/)). Note: that lesson calls broad-nib contrast "high" and pointed-nib contrast "low", which contradicts Noordzij (Didones are high-contrast expansion); follow Noordzij.
- High-contrast (Didone-like) display serifs = vertical stress, expansion. [derived from Noordzij] Geist Serif is reportedly high-contrast display ([Vercel blog](https://vercel.com/blog/introducing-geist-serif)) `[unverified]`, so expect expansion contrast: thin horizontals/hairline serifs, vertical stress.

### 2.2 Serif types

Bracketed (curved stem-to-serif transition; old-style, transitional), slab (thick, block-like, often unbracketed), hairline (Didone), wedge (triangular) ([Monotype: typography terms](https://www.monotype.com/resources/expertise/typography-terms-and-definitions)). In dynamic (calligraphic) serifs, serifs are asymmetric and follow the tool; in static ones they are near-geometric ([TypeType UniversiTTy 9](https://typetype.org/blog/universitty-lesson-9-uppercase-characters-detailed-contour-refinement/)). Counting convention: a serif n has 5 serifs (spur + 2×2 feet) ([Glyphs: serif components](https://glyphsapp.com/learn/serif-components)).

### 2.3 Serif length and thickness vs stem `[measured]`

Source Serif 4 (Adobe, OFL), lowercase n, UPM 1000:

| Instance | Stem | Serif overhang L/R (stem multiples) | Serif tip thickness / stem | o contrast (thick/thin) | H bar / H stem | Ascender serif slope | xh/cap | n advance |
|---|---|---|---|---|---|---|---|---|
| Regular, opsz 8 | 96 | 84/80 (0.88/0.83) | 0.62 | 1.73 | 0.59 | 7.3° | 0.758 | 680 |
| Regular, opsz 20 | 85 | 76/71 (0.89/0.84) | 0.43 | 2.11 | 0.49 | 13.7° | 0.709 | 606 |
| Regular, opsz 60 | 67 | 74/69 (1.10/1.03) | 0.25 | 3.47 | 0.34 | 13.0° | 0.675 | 558 |
| Bold, opsz 20 | 159 | 56/48 (0.35/0.30) | 0.30 | 3.25 | 0.35 | 9.8° | 0.721 | 616 |
| Bold, opsz 60 | 133 | 56/51 (0.42/0.39) | 0.17 | 5.51 | 0.20 | 11.8° | 0.684 | 568 |

Readings:
- Serif overhang is nearly constant in **absolute units** across optical sizes (74–84) and weights (≈55 in Bold); it does **not** scale with the stem. In Bold the overhang shrinks to ~0.3–0.4 stem.
- Outer overhang (left foot) is slightly longer than inner (≈5 units).
- Serif thickness, hairlines and bar thickness are what optical size changes most (tip 0.62 → 0.25 stem; contrast 1.7 → 3.5).

### 2.4 Brackets

Build serifs as reusable components; Glyphs corner components support bracketed serifs with smooth transitions ([Glyphs: serif components](https://glyphsapp.com/learn/serif-components), [corner components](https://glyphsapp.com/learn/reusing-shapes-corner-components)); segment components handle cupped serifs ([Glyphs](https://glyphsapp.com/learn/reusing-shapes-segment-components)). Bracket curves should harmonise with bowl/oval curvature: "all letters with rounded elements depend on the specific bracket form" ([TypeType UniversiTTy 9](https://typetype.org/blog/universitty-lesson-9-uppercase-characters-detailed-contour-refinement/)). Measured: Source Serif 4 Regular bracket+serif height ≈ 60 (opsz 8) to ≈ 100 (opsz 20–60) units, i.e. 0.6–1.5 stem `[measured]`.

### 2.5 Ascender (head) serif angle

Source Serif 4 head-serif top slope: 7° (caption) to 13–14° (text/display), 10–12° in Bold `[measured]`. Sloped head serifs leave few truly flat tops in old-style lowercase, so alignment is negotiated by eye ([Frere-Jones 001](https://slate.com/human-interest/2015/04/tobias-frere-jones-explains-the-optical-illusion-that-tricks-our-brains-into-perceiving-typeface-letters-are-of-equal-height.html)).

### 2.6 Terminals

Ball (circular), teardrop, beak; terminal = stroke end without serif ([Monotype terms](https://www.monotype.com/resources/expertise/typography-terms-and-definitions)). Don't mix terminal cut logics; cut angles consistent across the font; teardrops mainly lowercase (a, c, f, r, y) ([TypeType UniversiTTy 9](https://typetype.org/blog/universitty-lesson-9-uppercase-characters-detailed-contour-refinement/), [10](https://typetype.org/blog/universitty-lesson-10-designing-basic-lowercase-characters/)). Draw balls with a triangular overlap so ball and stroke edit independently ([Ohno: Drawing vectors](https://ohnotype.co/blog/drawing-vectors)).

### 2.7 Optical size

- Smaller sizes: lower contrast, wider glyphs, larger x-height, more open apertures, fewer details, looser spacing; display: more contrast and detail, tighter ([TypeType UniversiTTy 7](https://typetype.org/blog/universitty-lesson-7-designing-basic-latin-characters-glyph-height-contrast-optical-sizes/); [GF: optical sizes](https://fonts.google.com/knowledge/glossary/optical_sizes); [Biľak](https://www.typotheque.com/articles/sans-for-small-text-sizes)). Book: [JAF, Size-specific adjustments to type designs](https://justanotherfoundry.com/size-specific-adjustments-to-type-designs).
- Source Serif 4 opsz 8 → 60 confirms every item numerically (§2.3) `[measured]`.
- High contrast needs larger sizes; thin parts fail on screen at small sizes ([TypeType 7](https://typetype.org/blog/universitty-lesson-7-designing-basic-latin-characters-glyph-height-contrast-optical-sizes/)). Low stroke contrast reads at smaller sizes (Minakata & Beier 2022, via [Biľak](https://www.typotheque.com/articles/sans-for-small-text-sizes)).
- `opsz` axis registered 1–1200 in GF ([axis registry metadata](https://fonts.google.com/metadata/fonts)).

### 2.8 Italic construction

- Obliques: 6–12° typical; geometric slant thins verticals (30° slant thins a vertical stem ≈13%, a stem slanted −30° into upright gains ≈16%); use Cursivy (stem-aware) and re-add extremes; slant pivot at half x-height ([Glyphs: Easy oblique](https://glyphsapp.com/learn/easy-oblique)). Even true italics need obliqued caps ([same](https://glyphsapp.com/learn/easy-oblique)).
- 11.31° (tan = 0.2) is not a rule, only an angle that avoids rounding glitches (John Hudson, [TypeDrawers](https://typedrawers.com/discussion/4976/rules-while-designing-italics)).
- Process research: [Gaultney, Designing italics](https://gaultney.org/jvgtype/italics/designing-italics) (not read in depth here).

---

## 3. Sans

- **Monolinear vs modulated**: no sans is truly monolinear; contrast "never goes away completely" ([Frere-Jones 002](https://stockholmstypografiskagille.se/typonyheter/typeface-mechanics-002/)). Zed Display horizontals 90% of verticals, Zed Text 80% (more contrast helps small text) ([Biľak](https://www.typotheque.com/articles/sans-for-small-text-sizes)).
- **Aperture**: open apertures in a, c, e, r, s increase glance recognition (Beier & Oderkerk 2021, via [Biľak](https://www.typotheque.com/articles/sans-for-small-text-sizes)); closed apertures read as static/display ([TypeType 7](https://typetype.org/blog/universitty-lesson-7-designing-basic-latin-characters-glyph-height-contrast-optical-sizes/)).
- **Terminal angle**: choose one cut logic (perpendicular, horizontal/vertical, or angled) and keep angles similar font-wide ([TypeType 9](https://typetype.org/blog/universitty-lesson-9-uppercase-characters-detailed-contour-refinement/)).
- **x-height**: higher for small/UI use ([TypeType 7](https://typetype.org/blog/universitty-lesson-7-designing-basic-latin-characters-glyph-height-contrast-optical-sizes/); [Biľak](https://www.typotheque.com/articles/sans-for-small-text-sizes)).
- **Small sizes**: digital fonts scaled from large masters look "too light, too narrow" small; small-size cuts are darker, wider, looser ([Biľak](https://www.typotheque.com/articles/sans-for-small-text-sizes)). Distance-reading faces share the small-text visual angle ([same](https://www.typotheque.com/articles/sans-for-small-text-sizes)).
- **UI**: SF Pro uses variable optical sizes that adjust spacing and proportion with point size ([Apple Fonts](https://developer.apple.com/fonts/)). Backlit/negative contexts need lighter weights (FF Transit Front/Back Positive/Negative; FF Info Display Regular for negative, Medium for positive) ([FontShop part 2](https://www.myfonts.com/pages/fontshop-a-round-of-applause-for-well-rounded-type-talent-part-2)).

---

## 4. Mono

- **Metadata**: all glyphs, including combining marks, share one advance; collapse mark widths in GPOS if needed; `post.isFixedPitch = 1`; PANOSE `bProportion = 9` (John Hudson, Dave Crossland, [TypeDrawers](https://typedrawers.com/discussion/983/monospace-font-attributes)); Windows GDI uses `xAvgCharWidth` for simple glyphs and 2× for CJK (same thread). Checked by `opentype/monospace` ([Font Bakery](https://fontbakery.readthedocs.io/en/stable/fontbakery/profiles/opentype.html)).
- **Fixed advance cost**: "wide characters are forced to squeeze; narrow characters are forced to stretch. Uppercase letters look skinny next to lowercase, and bold characters don't have enough room to get very bold" ([Input info](https://input.djr.com/info)). Usual remedies: slab serifs/spurs on i, l, j, r, f to fill the cell (Input offers serif arrangements for i/l); compressed m/w/M/W with thinned middle strokes `[unverified as a sourced rule; standard practice]`.
- **Disambiguation**: 1/l/I distinct; dotted 0 vs plain O; comma shape differs from period at small sizes ([JetBrains Mono](https://www.jetbrains.com/lp/mono/)); alternates for a, g, i, l, 0, *, {} ([Input](https://input.djr.com/info)).
- **Proportions**: JetBrains Mono keeps standard widths but maximises lowercase height so each letter gets more pixels; ovals approach rectangles for vertical scanning; 9° italic ([JetBrains Mono](https://www.jetbrains.com/lp/mono/)).
- **Punctuation**: large, clear punctuation and carefully sized/positioned code symbols (braces, < >, @) ([Input](https://input.djr.com/info)).
- **Ligatures**: code ligatures merge multi-character tokens (`->`, `<=`, `:=`) and rebalance spacing (`..`, `//`); they are a rendering feature, text stays ASCII ([Fira Code README](https://github.com/tonsky/FiraCode/blob/master/README.md); [JetBrains Mono](https://www.jetbrains.com/lp/mono/)). Each ligature must still occupy N whole cells [derived from the fixed-advance rule].
- **Box drawing / block elements** tile across cells; renderers show gaps when line height or glyph extents mismatch ([neovide #2491](https://github.com/neovide/neovide/issues/2491); [kitty #7680](https://github.com/kovidgoyal/kitty/discussions/7680)). This repo already keeps U+2500–U+25FF exact (`scripts/families.py`).
- **Line height**: many code editors don't expose leading; Input lets users bake metrics ([Input](https://input.djr.com/info)).

---

## 5. Rounded-specific rules

### 5.1 Terminology

"Round" = fully semicircular stroke ends; "rounded" = corners with a radius (FF DIN Round vs FF Unit Rounded); no consensus ([FontShop part 1](https://www.myfonts.com/pages/fontshop-a-round-of-applause-for-well-rounded-type-talent-part-1)). Noordzij: a "monoline" stroke is the stroke of a circular tool ([Noordzij 1991, p. 36](https://typemedia.org/assets/download/The%20Shape%20of%20the%20Stroke,%20RIDT%201991,%20pp%2034-42_low.pdf)). Goeist Mono's `round-nib` = round; Goeist Sans' `soft` = rounded.

### 5.2 How rounding loses ink, and what shipping fonts do `[measured]`

Geometry `[derived]`: replacing a square stem end of width s by a semicircle removes `(1/2 − π/8)·s² ≈ 0.1073·s²`. Two corner fillets of radius r remove `2(1 − π/4)·r² ≈ 0.429·r²`. A stroke extension e adds `e·s`. Break-even extension for a semicircular end: **e ≈ 0.107·s**.

Area change (overlaps removed) and terminal extension, rounded vs sharp sibling:

| Family pair | Weight | n | H | l | i | o | Stem changed? | Advance changed? | Terminal extension beyond baseline/cap |
|---|---|---|---|---|---|---|---|---|---|
| SF Pro (opsz 28) → SF Pro Rounded, UPM 2048 | 100 | +0.3% | +0.8% | +1.1% | +1.9% | −1.1% | no (73.2) | no | 15–16 (≈0.22 s) |
| | 400 | −0.5% | −0.4% | −0.1% | −0.4% | −0.8% | no (174) | no | lc 18 (0.10 s), caps 14 |
| | 700 | −0.9% | −1.0% | −0.9% | −1.1% | −0.6% | no (292) | no | lc 22, caps 19–20 |
| | 900 | −1.4% | −1.5% | −1.5% | −1.5% | −0.3% | no (371) | no | lc 24 (0.065 s), caps 23 |
| Google Sans Flex ROND 0 → 100, UPM 2000 | 100 | −0.4% | −0.4% | −0.5% | −0.5% | 0 | no | no | 4 (≈0.06 s) |
| | 400 | −1.1% | −1.0% | −1.3% | −1.5% | 0 | no | no | 9 (0.053 s) |
| | 1000 | −3.1% | −3.1% | −3.4% | −3.5% | 0 | no | no | 25 (0.055 s) |
| Kode Mono ROND 0 → 100, UPM 1000 | 400 | −1.6% | −1.3% | −1.6% | −4.2% | −0.3% | no | no | 0 |
| | 700 | −2.9% | −2.9% | −2.4% | −5.1% | −0.4% | no | no | 0 |
| Geist → Goeist (`soft`), UPM 1000 | 100 | −0.75% | −0.75% | −0.8% | −2.4% | 0 | no (32) | no | 0 |
| | 400 | −2.1% | −2.0% | −1.8% | −5.9% | 0 | no (86) | no | 0 |
| | 900 | −5.1% | −5.2% | −3.5% | −10.2% | 0 | no (196) | no | 0 |
| Geist Mono → Goeist Mono (`round-nib`) | 400 | −1.9% | −1.9% | −1.6% | −3.7% | 0 | no | no | 0 |
| | 900 | −4.1% | −4.6% | −2.6% | −5.6% | 0 | no | no | 0 |

Findings:
1. **Nobody thickens stems.** SF Rounded's stems equal SF Pro's to 0.1 unit at every weight; GSF likewise. SF Rounded is literally SF Pro's display optical size (opsz ≥ 28) with identical advances, stems and x-height (1040 at 400), plus round terminals.
2. **Both Apple and Google extend stroke ends past the alignment lines** (H spans −14…1457 vs 0…1443 at SF 400). SF's lowercase terminal extension ≈ the lowercase round overshoot (18 vs o's 20 at 400; 24 vs 23–26 at 900); its cap terminal extension is 0.6–0.9× the O overshoot (14 vs 24 at 400, 23 vs 25 at 900). At Regular this is almost exactly the break-even 0.107·s; thin weights gain ink, heavy weights still lose ~1.5%. GSF uses a proportional ≈0.055·s.
3. SF Rounded and GSF ROND=100 terminals are semicircles: full stem width is reached ≈0.5 s above the terminal tip at all weights (SF H stem 180: quarter arcs from x=140 to 230, y=1364 to 1457, a single top point, no flat). Kode Mono uses ≈0.25 s corner radii with no extension.
4. Goeist currently has the largest ink loss of the set (−2% Regular, −5% Black on n/H; −6%/−10% on i) and the only one besides Kode Mono with no terminal extension.
5. Typographers confirm the optical side: Cera Round "every stem … was carefully assessed and brought into balance" because a semicircular end "looks shorter" ([TypeMates](https://www.typemates.com/news/round-and-round-we-go-making-of-cera-round)); Glyphs' *Rounded Font* filter rounds the stem elliptically "with overshoots" ([Glyphs: Rounded corners](https://glyphsapp.com/learn/rounded-corners)); Unger widened stroke ends on Markeur so the engraver wouldn't cut them too round ([FontShop part 2](https://www.myfonts.com/pages/fontshop-a-round-of-applause-for-well-rounded-type-talent-part-2)).
6. Nunito: removing the rounding (to make Nunito Sans) changed "weight dispersion" and needed counterbalancing; Le Bailly added overshoot to rounds, deepened Light joints/crotches and thinned Light cap horizontals by 2 units; both families share widths and metrics ([Nunito thread](https://groups.google.com/g/googlefonts-discuss/c/eIWeNyhXal0/m/953AXA7lAAAJ)).

### 5.3 Radius vs weight

- FF Unit Rounded: radius set per weight independently of stem; light weights have almost no flat at stroke ends, bolds keep straight bottoms with rounded corners; without any flat "you get the pure sausage effect" ([Spiekermann: Unit Rounded](https://spiekermann.com/en/unit-rounded)). So relative radius decreases with weight there.
- Cera Round: light weights were easy; the Black needed redesign (e.g. top of a) so strokes don't narrow toward the end ([TypeMates](https://www.typemates.com/news/round-and-round-we-go-making-of-cera-round)).
- SF Rounded and GSF keep r = s/2 at every weight `[measured]`. Goeist uses r ∝ s (0.52) at every weight.
- Glyphs *Round Corners* "visual corrections" use smaller radii on acute corners and larger on obtuse ones ([Glyphs Handbook: Round Corners](https://handbook.glyphsapp.com/filters/round-corners/)), which is what Goeist's `terminal`/`acute` split does.

### 5.4 Diagonals and widths

- Cera Round kept every advance identical to Cera Pro so kerning/layout don't change; changed diagonal angles where needed; v/w/ν got slightly wider to compensate the lost tip ([TypeMates](https://www.typemates.com/news/round-and-round-we-go-making-of-cera-round)).
- SF Rounded and GSF keep advances but the x's black narrows (SF 400: 32…927 → 70…891; GSF 400: 14…955 → 78…889) because round caps on diagonals shrink their horizontal extent `[measured]`.
- Punctuation and accent ends: Cera narrowed them slightly so they stay "just distinguishable enough" ([TypeMates](https://www.typemates.com/news/round-and-round-we-go-making-of-cera-round)).

### 5.5 Concave corners

- Glyphs *Round Corners* rounds only outward ("black") corners by default; inward corners need a negative radius, and "inner roundings appear bigger than they are", so reduce the radius ([Glyphs: Rounded corners](https://glyphsapp.com/learn/rounded-corners)).
- SF Rounded keeps concave corners sharp (H crossbar joins at (320,819), (1112,657) etc. are single on-curve corners) `[measured]`.
- When softened anyway: wood type with round counter corners was easier to mill; HWT Artz rounds "all corners (especially those in the counters)" ([FontShop part 1](https://www.myfonts.com/pages/fontshop-a-round-of-applause-for-well-rounded-type-talent-part-1)); Ohno Softie rounds negative space too, as a style ("Even the negative space shouldn't have any hard corners") ([Ohno](https://ohnotype.co/blog/the-process-of-ohno-softie)); Cera Round's @ got a round connection ([TypeMates](https://www.typemates.com/news/round-and-round-we-go-making-of-cera-round)).
- Round-nib geometry `[derived]`: a circular nib of diameter s traced along a sharp skeleton leaves outer radius s/2 and a **sharp** inner corner; inner radius > 0 only if the skeleton itself is curved (inner = outer − s). So sharp concave corners are correct for `round-nib`, and softening them is a stylistic choice (Softie, Souvenir-like), not a correction.

### 5.6 Circular vs superelliptic (G2) corners

A circular fillet has continuous tangent but discontinuous curvature; a squircle's curvature ramps up and down, so it "doesn't look like a square with surgery performed on it" ([Figma: Desperately seeking squircles](https://www.figma.com/blog/desperately-seeking-squircles/)). Figma parameterises "smoothing" from a tabletop curvature profile (circular) to a triangular one (fully smoothed), with total turning fixed at π/2. Goeist's fillets are G1 circular approximations. G2 smoothing matters mostly at display sizes and on large radii; at r ≈ s/2 terminals there is no straight part left to smooth into on the end edge [derived].

### 5.7 Small sizes and hinting

- Goeist Sans terminal radius at Regular is 44.7 units (stem 86 × 0.52, `build/Goeist/rounding-upright.json`); at 16 px/1000 UPM one pixel is 62.5 units, so the radius is 0.7 px; at 12 px it is 0.5 px [derived]. Rounding is mostly invisible at UI text sizes; its main effect there is the 2% ink loss.
- Autohinting: FreeType classifies edges as round or flat; round edges snap to the overshoot line, flat edges to the reference; a round edge is not snapped when it sits below the reference ([FreeType: blue zones](https://freetype.org/autohinting/blues.html)). A semicircular stem end that stops exactly on the baseline/x-height is a round edge at the reference line [derived]: extending it to the overshoot line (as SF/GSF do) puts it in the zone the hinter expects. Overshoots are suppressed below ~1 px zone height ([same](https://freetype.org/autohinting/blues.html)).
- Rounded type historically solves halation on backlit signs and low-res screens (FF Info Display, ZDF, VAG on Apple keyboards) ([FontShop part 2](https://www.myfonts.com/pages/fontshop-a-round-of-applause-for-well-rounded-type-talent-part-2); [Spiekermann](https://spiekermann.com/en/unit-rounded)).

### 5.8 Stroke-end rounding vs whole-letterform rounding

- Rounded companions of static sans (Helvetica Rounded 1980, AG Book Rounded 1984, Arial Rounded by Robin Nicholas) round an existing design; VAG Rundschrift (1978) was drawn rounded, with Futura-like a/j/t/u ([FontShop part 2](https://www.myfonts.com/pages/fontshop-a-round-of-applause-for-well-rounded-type-talent-part-2)).
- Open Runde = Inter rounded entirely with the Glyphs Mini rounded-corner tool; "some glyphs might not look perfect"; four static weights, no variable font ([README](https://github.com/lauridskern/open-runde/blob/main/README.md)); license same as Inter (OFL) per the README.
- Nunito (rounded) and Nunito Sans (straight) share widths and metrics per weight ([Nunito thread](https://groups.google.com/g/googlefonts-discuss/c/eIWeNyhXal0/m/953AXA7lAAAJ)).
- SF Pro Rounded: Apple documents only that SF Pro and SF Compact "include a rounded variant" ([Apple Fonts](https://developer.apple.com/fonts/)); everything else above is `[measured]`. Varela Round: no design notes found `[unverified]`.
- GF registry has `ROND` (Roundness 0–100: "from angular defaults (0%) to become increasingly rounded") used by Google Sans Flex, Kode Mono, Doto, Tiny5, Wavefont; and `ELSH` (Element Shape, for modular fonts) used by Geist Pixel, Danfo, Bitcount, Handjet ([GF metadata](https://fonts.google.com/metadata/fonts)).
- Souvenir (visual reference only, proprietary): soft serifs, open g loop, curved diagonals on v/w/y, M diagonals not reaching the baseline; best at display sizes, light weight usable for short text ([MyFonts field guide PDF](https://cms.myfonts.com/sites/default/files/2023-09/ITC-Souvenir-Font-Field-Guide.pdf)); Benton 1914, Benguiat 1970 ITC expansion ([Fonts In Use](https://fontsinuse.com/typefaces/1913/itc-souvenir)). Its softness is whole-letterform (curved diagonals, bulbous soft serifs), not filleted corners.

---

## Implications for Goeist

Ranked by expected visual impact. **S** = Goeist Sans, **M** = Goeist Mono, **R** = future Goeist Serif.

1. **[S M R] Extend rounded stroke ends past their alignment line before filleting.** Today `rounding.py` only subtracts ink (fillets must stay inside original ink), so round ends look short and Goeist loses the most ink of any family measured (n/H −2% Regular, −5% Black). Rule: for a convex terminal whose flat end edge lies on baseline, x-height, cap height, ascender, descender, or figure height, move that edge outward by `e` before inserting fillets. Values from SF Rounded at matching ratios: lowercase `e ≈ 0.9 × lowercase round overshoot` (Goeist o overshoot = 12 → e ≈ 11), caps `e ≈ 0.6 × O overshoot` at Regular rising to `0.9×` at Black (Goeist O = 16 → 10…14); sanity bound `e ≈ 0.107·s` (ink break-even: 9 at Regular stem 86, 21 at Black 196). Use the measured stem per master so the extension interpolates. Re-run the vertical metrics check: `winAscent/winDescent` change if yMax/yMin grow ([GF metrics rule 6](https://googlefonts.github.io/gf-guide/metrics)); typo/hhea stay. Exclude `exact_geometry` and joins.
2. **[S M R] Do not thicken stems or change advances.** SF Rounded, Google Sans Flex ROND, Kode Mono ROND, Cera Round and Nunito all keep stems and widths; Goeist already keeps advances (n 556/581/631 unchanged). Keep it so Goeist stays metric-compatible with Geist.
3. **[S M] Restore dot and punctuation colour.** i loses 6% (Regular) to 10% (Black) in Goeist Sans. A circle inscribed in a square dot loses `1 − π/4 = 21.5%` [derived]; make rounded dots area-preserving (diameter ≈ 1.13 × original square side) where clearance to the stem allows, else at least diameter = stem + e. Check comma vs period stay distinct at 11–13 px in Mono ([JetBrains Mono](https://www.jetbrains.com/lp/mono/)).
4. **[M] Keep concave corners sharp.** Under a circular nib (Noordzij's monoline tool), outer radius s/2 with sharp inner corners is the correct offset geometry [derived]; SF Rounded does the same `[measured]`. Soften concave corners only as an explicit style choice and then with radius < outer radius ([Glyphs](https://glyphsapp.com/learn/rounded-corners)).
5. **[S M] Re-check visible optical corrections after rounding.** Where upstream Geist thins horizontals in symmetrical symbols (+, 4, ×, arrows), round ends make the difference visible (Cera Round). Proof `+ − × ÷ = 4 # →` in Mono and Sans at 48–96 px; equalise if it reads as two weights.
6. **[S M] Diagonal endings keep advances; re-test diagonal letters.** Rounding narrows the black of x/v/w/y (SF/GSF) `[measured]`; Cera widened v/w instead. Proof `vwxyVWXY` spacing; adjust kerning, not advances, if gaps open.
7. **[S M R] Proof at sizes where rounding is visible.** At Regular, terminal radius ≈ 0.7 px at 16 px, so review rounding at ≥ 24 px and colour (ink loss) at 11–16 px. Add a proof page of `nnonnoHHOHH`, `illi1lI|`, `minimum`, `0Oo`, `rnm` per weight.
8. **[S M R] Keep acute/obtuse radius split; consider per-weight radius tuning.** Glyphs' visual corrections and FF Unit Rounded both vary radius by angle and weight. Goeist's `terminal` 0.52 / `acute` 0.22 matches the angle rule; optional: lower the sans terminal multiple slightly in Black (Unit Rounded keeps flats in bolds) if Black looks "sausage" in proofs.
9. **[S M R] QA.** Run Fontspector with outline checks (`outline_short_segments`, `outline_jaggy_segments`, `outline_colinear_vectors`, `outline_alignment_miss`) and `opentype/monospace` for Mono; whitelist expected fillet short segments. Run mekkablue Kink Finder on rounded masters ([Glyphs MM part 2](https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)).
10. **[S M] Optional future axes.** If a rounded/sharp toggle is ever wanted in one file, the registered `ROND` axis (0–100) exists; ink compensation without reflow belongs on `GRAD` ([GF metadata](https://fonts.google.com/metadata/fonts)). Not needed for separate Goeist families.

### Goeist Serif (R) specific

11. **Radius must be bounded by local thickness, not only by the vertical stem.** In a high-contrast serif, hairline serifs and joins are 0.17–0.6 stem thick (Source Serif 4: serif tip 0.25 s at opsz 60, 0.17 s in Bold display) `[measured]`. Rule: `r = min(k · stem, 0.5 · local stroke thickness)`; with `circular=True` this turns hairline serif tips into tiny semicircles, which is the Souvenir-like soft serif look. A stem-relative 0.52·s radius applied to a 0.25·s serif would be clamped by the 0.48-edge trim limit into an ellipse; measure local thickness instead.
12. **Serif length after rounding.** Serif overhang in a well-made serif is roughly constant in absolute units (≈75–85 in Source Serif 4 Regular, ≈55 Bold) `[measured]`; rounding a serif tip of thickness t into a semicircle removes ≈0.107·t² of ink at the tip, so it reads shorter. Either extend the tip outward by ≈0.107·t (same break-even as §5.2) [derived], or accept shorter serifs and respace.
13. **Brackets are concave: leave them, or round them deliberately.** Brackets already curve; rounding the outer serif corners while leaving brackets gives Souvenir-like soft serifs. Saw-toothed/acute serifs (Geist Serif, reportedly) take the `acute` radius; check that acute radii do not erase the tooth. `[unverified: Geist Serif serif shapes; see research/geist-serif.md]`
14. **Ball/teardrop terminals and dots**: already round; leave untouched (no fillet, no extension), like SF Rounded leaves its already-round dots.
15. **Expansion contrast survives rounding only at display sizes.** Geist Serif is a display design `[unverified]`; hairlines (≈0.2–0.35 s for bars at display opsz) `[measured, SS4]` lose proportionally more ink to rounding than stems. Test rounded hairlines at ≥ 32 px; if a text cut is ever added, lower contrast first (opsz 8 in SS4: contrast 1.7, serif tip 0.62 s).
16. **Italic**: if Geist Serif ships an italic, round after slanting (fillets are not slant-invariant), and expect 6–12° ([Glyphs](https://glyphsapp.com/learn/easy-oblique)).
17. **Profile proposal for `families.py`** (to validate in proofs): `terminal = 0.5` (semicircular stem ends, `circular=True`), `acute = 0.22`, local-thickness clamp from rule 11, terminal extension from rule 1, no stadium conversion for serif dots that are already round.
