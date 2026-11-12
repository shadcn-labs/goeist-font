# Contributing to Goist

## Build

Requires Python 3.12 and `make`. The first command creates `venv/` and installs the locked Python toolchain. No Glyphs application, native font editor, or separately installed autohinter is required. Subsequent builds work offline with the installed environment and vendored sources.

```sh
make build
make test
make proof
```

Every target runs for each family in `scripts/families.py` (`Goist`, `GoistMono`); `make build FAMILIES=GoistMono` limits it to one. The scripts take the same key: `venv/bin/python scripts/build.py --family GoistMono`. Paths below use `<Family>`.

| Output | Location |
| --- | --- |
| Upright and italic variable TTF | `fonts/<Family>/variable/` |
| Eighteen static TTF styles | `fonts/<Family>/ttf/` |
| Eighteen static OTF styles | `fonts/<Family>/otf/` |
| Variable and static WOFF2, with CSS | `fonts/<Family>/webfonts/` |
| Editable rounded Glyphs sources | `build/<Family>/sources/` |
| Per-glyph geometry reports | `build/<Family>/rounding-upright.json`, `build/<Family>/rounding-italic.json` |
| Coverage, shaping and delivery audit | `out/<Family>/verification.json` |
| Interactive specimen and full-glyph atlases | `out/<Family>/proof/` |

Commit `fonts/` after every rebuild; it is the release output and the npm package's source.

Static TTFs are strictly autohinted with `ttfautohint-py`. Variable TTFs and static OTFs are not autohinted; static TrueType instructions cannot be reused after outline changes or copied into variable fonts. Failed compilation or static hinting stops the build before publishing artifacts. Existing unrelated files in `fonts/<Family>/` are not deleted.

Static advances are taken from the corresponding variable-font location before hinting. This resolves one-unit component-interpolation differences between independently compiled statics and HVAR; both the horizontal metrics and embedded CFF charstring widths are aligned without changing outlines.

Build manifests hash every upstream package file, build configuration, geometry code and compiler versions. Changed or missing outputs invalidate the cache. `SOURCE_DATE_EPOCH` controls binary timestamps; the default is fixed. To force exports or limit compiler concurrency:

```sh
venv/bin/python scripts/build.py --family Goist --force --jobs 4
```

## Preview

Serve the repository root, not just the proof directory:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open <http://127.0.0.1:8765/out/Goist/proof/> or <http://127.0.0.1:8765/out/GoistMono/proof/>. Each specimen provides weight, size, italic and OpenType controls, original-versus-rounded text, small-size waterfalls, a code sample, and 24 complete outline atlases. Unencoded glyphs are shown directly as SVG outlines. Unsupported characters receive explicit codepoint labels rather than silently appearing in a fallback font. All assets are local.

## Web use without npm

Load `fonts/Goist/webfonts/goist.css` or `fonts/GoistMono/webfonts/goist-mono.css` and keep its sibling WOFF2 files alongside it. Use the matching `-static.css` instead for individual static webfonts; do not load both.

```html
<link rel="stylesheet" href="/fonts/Goist/webfonts/goist.css">
<link rel="stylesheet" href="/fonts/GoistMono/webfonts/goist-mono.css">
```

## npm release

```sh
make package        # build fonts, stage them into packages/goist/assets/, write goist-<version>.tgz
cd packages/goist && npm publish
```

`prepack` (`scripts/stage-assets.mjs`) copies each family's `fonts/<Family>/webfonts/` into the package and renames `Goist[wght].woff2` to `Goist-Variable.woff2` (likewise for Goist Mono), so publishing always ships the committed fonts. Bump `version` in `packages/goist/package.json` with each font release and add an entry to `CHANGELOG.md`.

## Adding a family

1. Vendor the upstream upright and italic `.glyphspackage` sources, reference variable fonts, licenses and a `manifest.json` under `sources/<Family>/upstream/`.
2. Add `sources/<Family>/config.yaml` (gftools recipe with the family name and STAT tables).
3. Register the family and its rounding profile in `scripts/families.py`, and add it to `FAMILIES` in the `Makefile`.
4. Add the family to `packages/goist/scripts/stage-assets.mjs`, with `font/<name>.js`/`.d.ts` entries and `exports` in `package.json`.

## Source and rounding

Each family's original editable upright and italic packages are vendored unchanged under `sources/<Family>/upstream/`, pinned to [Geist v1.9.2](https://github.com/vercel/geist-font/releases/tag/v1.9.2), commit `ef2597cfc42f4797676df105517ccc0a1cfa6569`. `manifest.json` records provenance and immutable reference-font hashes.

`scripts/rounding.py` measures stems per master, then trims neighboring line/cubic segments and inserts tangent cubic fillets. Exact Bézier ink containment prevents polygon-approximation errors at curved terminals. Hidden overlap corners and concave counter corners retain their original construction. Short edges constrain local radii rather than allowing adjacent fillets to cross.

Fillet radii come from each family's profile in `scripts/families.py`, as multiples of the measured stem:

| Profile | Family | Squared ends and outer corners | Acute apexes and diagonal cuts | Arcs | Convex straight contours |
| --- | --- | --- | --- | --- | --- |
| `soft` | Goist | 0.52 | 0.22 | trimmed independently per edge | as other corners |
| `round-nib` | Goist Mono | 0.52 | 0.52 | always circular | stadium, half width ≤ 1.5 |

`round-nib` follows ABC Diatype Rounded Mono's "one chunky tool" construction. Every fillet is a circular arc: where a short edge limits the trim, the radius shrinks so both sides trim equally, so slab and stroke ends become semicircles rather than ellipses. Straight-edged convex contours (dots, bars, slashes, commas) become stadiums and circles, with a radius of half their width up to 1.5 stems, so dots wider than the stem are still round.

In Goist Mono, box drawing, block elements and geometric shapes (U+2500–U+25FF) keep their exact upstream geometry: they tile across character cells, and rounding them would break connected lines and blocks in terminals.

Geist Mono's sources contain 69 exported coding-ligature glyphs (`hyphen_greater.liga`, …) but no `liga` feature: Glyphs.app derives it from glyph names at export and glyphsLib cannot. For Goist Mono, `add_automatic_ligatures` recreates that feature, longest sequence first, identically in the unrounded baseline and the rounded source.

The transformation maintains corresponding contours and point types across Thin, Regular and Black masters, including the `f` intermediate layer at weight 801. Unmoved support cubics preserve correspondence where a corner is only exposed in some masters. Components, anchors, advances, kerning and feature definitions remain in the sources. Non-exporting helper glyphs and backup layers are retained. Geometry errors are explicit failures, not silent glyph reversions.

## Verification

`make test` builds a separate unrounded source baseline per family, compares final fonts against it, and runs geometry regressions. The font audit checks glyph and Unicode inventories, advances and line metrics, OpenType layout and HarfBuzz shaping, named and intermediate variable weights, genuine italic/style naming, CFF delivery, and WOFF2 parity. It covers unencoded glyph outlines as well as Unicode-mapped characters. The JSON report retains explicit differences between the source baseline and older official reference binaries; approved upstream drift is listed with its reason in `sources/<Family>/drift-allowlist.json`.

Attribution checks require the designer name to match the first entry in `AUTHORS.txt`, the manufacturer to be Shadcn Labs, the retained upstream copyright, the Vercel Geist Sans or Geist Mono credit with its non-affiliation statement, and OFL licensing.

**Upstream distinction, Goist:** the pinned Geist source version is 1.900, whereas its committed reference binaries report 1.800. Both export 975 glyphs and map 728 codepoints. The source corrects an erroneous mapping of U+03C9 (lowercase omega) to the uppercase Omega outline, replacing that alias with U+2126 (ohm sign). Goist follows this correction; it does not claim a lowercase omega design that Geist never supplied. No glyph outline is removed by this correction.

**Upstream distinction, Goist Mono:** the pinned Geist Mono source version is 1.900, whereas its reference binaries report 1.700. The source's Italic (400) master has no kerning, while the 1.700 binary kerns at that weight; Goist Mono follows the source.

Optional additional binary QA, with Fontspector installed separately:

```sh
make qa
```

Automated checks complement the browser proofs; they do not replace visual review of every glyph or establish testing on every operating system.
