# Goist

A rounded typeface by **Aniket-508**, based on **Vercel Geist Sans**. Goist keeps Geist's skeleton and typography while softening exposed corners and stroke endings.

- Nine weights, 100–900, in upright and genuine italic styles.
- Separate upright and italic weight-variable fonts.
- All 975 exported glyphs per style, including unencoded alternates, ligatures and combining marks.
- Latin, extended Latin, Vietnamese and Cyrillic coverage inherited from the pinned sources; isolated Greek symbols do not imply full Greek support.
- All eleven stylistic sets (`ss01`–`ss11`), localized forms, fractions, numeral variants, kerning and mark positioning.

## Installation

Download the files from `fonts/Goist/` or install the npm package:

```sh
npm install goist
```

```tsx
import { GoistSans } from "goist/font/sans"; // Next.js (next/font/local)
import "goist/sans.css";                     // any other bundler
```

See [`packages/goist/README.md`](packages/goist/README.md) for Tailwind, static fonts and CSS variables.

## Repository layout

Each family owns one directory under `sources/`, `fonts/`, `build/` and `out/`. Goist Mono will be added as `GoistMono` alongside `Goist`, and shipped from the same `goist` npm package as `goist/font/mono`.

| Path | Contents | Git |
| --- | --- | --- |
| `sources/Goist/` | gftools recipe and vendored upstream Geist Sans sources | committed |
| `fonts/Goist/` | release TTF, OTF, variable and WOFF2 fonts | committed |
| `build/Goist/` | generated editable sources, baseline build, manifests | ignored |
| `out/Goist/` | verification report and browser proof | ignored |
| `scripts/`, `tests/` | build driver, rounding geometry, audits, proofs | committed |
| `packages/goist/` | `goist` npm package; webfonts are staged from `fonts/` on pack | committed (assets ignored) |

The public specimen site lives at [shadcn-labs.com/font](https://shadcn-labs.com/font), outside this repository.

## Build

Requires Python 3.12 and `make`. The first command creates `venv/` and installs the locked Python toolchain. No Glyphs application, native font editor, or separately installed autohinter is required. Subsequent builds work offline with the installed environment and vendored sources.

```sh
make build
make test
make proof
```

| Output | Location |
| --- | --- |
| Upright and italic variable TTF | `fonts/Goist/variable/` |
| Eighteen static TTF styles | `fonts/Goist/ttf/` |
| Eighteen static OTF styles | `fonts/Goist/otf/` |
| Variable and static WOFF2, with CSS | `fonts/Goist/webfonts/` |
| Editable rounded Glyphs sources | `build/Goist/sources/` |
| Per-glyph geometry reports | `build/Goist/rounding-upright.json`, `build/Goist/rounding-italic.json` |
| Coverage, shaping and delivery audit | `out/Goist/verification.json` |
| Interactive specimen and full-glyph atlases | `out/Goist/proof/` |

Static TTFs are strictly autohinted with `ttfautohint-py`. Variable TTFs and static OTFs are not autohinted; static TrueType instructions cannot be reused after outline changes or copied into variable fonts. Failed compilation or static hinting stops the build before publishing artifacts. Existing unrelated files in `fonts/Goist/` are not deleted. Commit `fonts/Goist/` after every rebuild; it is the release output and the npm package's source.

Static advances are taken from the corresponding variable-font location before hinting. This resolves one-unit component-interpolation differences between independently compiled statics and HVAR; both the horizontal metrics and embedded CFF charstring widths are aligned without changing outlines.

Build manifests hash every upstream package file, build configuration, geometry code and compiler versions. Changed or missing outputs invalidate the cache. `SOURCE_DATE_EPOCH` controls binary timestamps; the default is fixed. To force exports or limit compiler concurrency:

```sh
venv/bin/python scripts/build.py --force --jobs 4
```

## Preview

Serve the repository root, not just the proof directory:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open <http://127.0.0.1:8765/out/Goist/proof/>. The specimen provides weight, size, italic and OpenType controls, original-versus-rounded text, small-size waterfalls, and 24 complete outline atlases. Unencoded glyphs are shown directly as SVG outlines. Unsupported characters receive explicit codepoint labels rather than silently appearing in a fallback font. All assets are local.

## npm package

```sh
make package        # build fonts, stage them into packages/goist/assets/, write goist-<version>.tgz
cd packages/goist && npm publish
```

`prepack` (`scripts/stage-assets.mjs`) copies `fonts/Goist/webfonts/` into the package and renames `Goist[wght].woff2` to `Goist-Variable.woff2`, so publishing always ships the committed fonts. Bump `version` in `packages/goist/package.json` with each font release.

## Web use

Without npm, load `fonts/Goist/webfonts/goist.css` and keep its sibling WOFF2 files alongside it:

```html
<link rel="stylesheet" href="/fonts/Goist/webfonts/goist.css">
```

```css
body {
  font-family: "Goist", sans-serif;
  font-weight: 400;
}

em {
  font-style: italic;
}
```

Use `goist-static.css` instead if individual static webfonts are preferred; do not load both family definitions.

## Source and rounding

The original editable upright and italic packages are vendored unchanged under `sources/Goist/upstream/`, pinned to [Geist v1.9.2](https://github.com/vercel/geist-font/releases/tag/v1.9.2), commit `ef2597cfc42f4797676df105517ccc0a1cfa6569`. `manifest.json` records provenance and immutable reference-font hashes.

`scripts/rounding.py` measures stems per master, then trims neighboring line/cubic segments and inserts tangent cubic fillets. Exact Bézier ink containment prevents polygon-approximation errors at curved terminals. Hidden overlap corners and concave counter corners retain their original construction. Short edges constrain local radii rather than allowing adjacent fillets to cross.

The transformation maintains corresponding contours and point types across Thin, Regular and Black masters, including the `f` intermediate layer at weight 801. Unmoved support cubics preserve correspondence where a corner is only exposed in some masters. Components, anchors, advances, kerning and feature definitions remain in the sources. Non-exporting helper glyphs and backup layers are retained. Geometry errors are explicit failures, not silent glyph reversions.

Design and workflow references:

- [Sunghyun Sans](https://github.com/anaclumos/sunghyun-sans): weight-sensitive rounding and glyph-specific review.
- [Intern](https://github.com/bvvst/intern): fully rounded terminal treatment across variable weights.
- [Open Runde](https://github.com/lauridskern/open-runde): restrained softness and the need to correct automatic rounding.

Goist uses Geist outlines; it does not merge outlines from these references.

## Verification

`make test` builds a separate unrounded source baseline, compares final fonts against it, and runs geometry regressions. The font audit checks glyph and Unicode inventories, advances and line metrics, OpenType layout and HarfBuzz shaping, named and intermediate variable weights, genuine italic/style naming, CFF delivery, and WOFF2 parity. It covers unencoded glyph outlines as well as Unicode-mapped characters. The JSON report retains explicit differences between the source baseline and older official reference binaries.

Authorship checks compare exported designer and manufacturer names against the first entry in `AUTHORS.txt`, and require the retained upstream copyright, explicit Vercel Geist Sans credit and OFL licensing. Both font metadata and preview author labels use that author entry.

**Upstream distinction:** the pinned source version is 1.900, whereas its committed reference binaries report 1.800. Both export 975 glyphs and map 728 codepoints. The source corrects an erroneous mapping of U+03C9 (lowercase omega) to the uppercase Omega outline, replacing that alias with U+2126 (ohm sign). Goist follows this correction; it does not claim a lowercase omega design that Geist never supplied. No glyph outline is removed by this correction.

Optional additional binary QA, with Fontspector installed separately:

```sh
make qa
```

Automated checks complement the browser proofs; they do not replace visual review of every glyph or establish testing on every operating system.

## License and credits

Goist's rounded design and modifications are copyright 2026 **Aniket-508**, the project's primary author. The font is distributed under the **SIL Open Font License 1.1**. Required original Geist copyright and license notices remain in `OFL.txt` and `sources/upstream/`; Vercel Geist Sans and its contributors receive upstream credit in `CONTRIBUTORS.txt` and the font's description metadata. Goist is an independent derivative, not an official Vercel release.

## Changelog

### 1.000 — 2026-11-12

- Added stem-relative rounded outlines across the complete upright and italic source families.
- Preserved the full exported glyph repertoire, all eleven stylistic sets and the original advance/line-metric contract.
- Added portable static, variable and webfont builds, strict source-parity verification, geometry regression tests and offline interactive proofs.
- Replaced the Radio Canada project-template build with the pinned Geist-derived Goist workflow.
- Identified Aniket-508 as the Goist author and copyright holder for the derivative work, with Vercel Geist Sans credited upstream and its required notices retained.
