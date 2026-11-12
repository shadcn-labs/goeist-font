# Contributing to Goeist

## Build

Requires Python 3.12 and `make`. The first command creates `venv/` and installs the locked Python toolchain. No Glyphs application, native font editor, or separately installed autohinter is required. Subsequent builds work offline with the installed environment and vendored sources.

```sh
make build
make test
make proof
```

Every target runs for each family in `scripts/families.py` (`Goeist`, `GoeistMono`); `make build FAMILIES=GoeistMono` limits it to one. The scripts take the same key: `venv/bin/python scripts/build.py --family GoeistMono`. Paths below use `<Family>`.

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
venv/bin/python scripts/build.py --family Goeist --force --jobs 4
```

## Preview

Serve the repository root, not just the proof directory:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open <http://127.0.0.1:8765/out/Goeist/proof/> or <http://127.0.0.1:8765/out/GoeistMono/proof/>. Each specimen provides weight, size, italic and OpenType controls, original-versus-rounded text, small-size waterfalls, a code sample, and 24 complete outline atlases. Unencoded glyphs are shown directly as SVG outlines. Unsupported characters receive explicit codepoint labels rather than silently appearing in a fallback font. All assets are local.

## Web use without npm

Load `fonts/Goeist/webfonts/goeist.css` or `fonts/GoeistMono/webfonts/goeist-mono.css` and keep its sibling WOFF2 files alongside it. Use the matching `-static.css` instead for individual static webfonts; do not load both.

```html
<link rel="stylesheet" href="/fonts/Goeist/webfonts/goeist.css">
<link rel="stylesheet" href="/fonts/GoeistMono/webfonts/goeist-mono.css">
```

## Versioning and npm release

Font versions (currently `0.001`) are set once in `FONT_VERSION` in `scripts/families.py`; keep `version` in each `sources/<Family>/config.yaml` equal to it (the build refuses a mismatch). The npm package `goeist` is versioned (currently `0.0.1`) by [Changesets](https://github.com/changesets/changesets) in `packages/goeist`, as in `vercel/geist-font`. Requires Node 22 (`.nvmrc`) and pnpm.

With every change that should ship, add a changeset describing it:

```sh
cd packages/goeist
pnpm install
pnpm changeset          # pick patch / minor / major and write the summary
```

To release:

```sh
make build                       # from the repository root; commit fonts/
cd packages/goeist
pnpm run version                 # apply changesets: bump package.json, update CHANGELOG.md
git commit -am "Version packages" && git push
pnpm release                     # changeset publish: packs (running prepack) and publishes to npm
git push --follow-tags
```

`changeset publish` runs npm non-interactively, so an account secured with a passkey or security key fails with `EOTP`. Until trusted publishing is configured, publish from a terminal with `npm publish` in `packages/goeist` (approve the browser prompt), then tag and push: `git tag v<version> && git push origin v<version>`.

The first release is already at `0.0.1` with its entry in `packages/goeist/CHANGELOG.md`, so publish it without adding a changeset. Do not merge Changesets prerelease state (`.changeset/pre.json`); the `Guard prerelease state` workflow rejects it. `make package` writes an inspectable `goeist-<version>.tgz` without publishing.

`prepack` (`scripts/stage-assets.mjs`) copies each family's `fonts/<Family>/webfonts/` into the package and renames `Goeist[wght].woff2` to `Goeist-Variable.woff2` (likewise for Goeist Mono), so publishing always ships the committed fonts.

Pushing the `v<version>` tag that `pnpm release` creates runs `.github/workflows/release.yaml`, which creates the GitHub Release with `Goeist-v<version>.zip` and `GoeistMono-v<version>.zip` (committed fonts plus licenses) and that version's `CHANGELOG.md` notes. Once on npm, the package is also served by jsDelivr and unpkg, e.g. `https://cdn.jsdelivr.net/npm/goeist@<version>/assets/goeist-mono/goeist-mono.css`.

## Adding a family

1. Vendor the upstream upright and italic `.glyphspackage` sources, reference variable fonts, licenses and a `manifest.json` under `sources/<Family>/upstream/`.
2. Add `sources/<Family>/config.yaml` (gftools recipe with the family name and STAT tables).
3. Register the family and its rounding profile in `scripts/families.py`, and add it to `FAMILIES` in the `Makefile`.
4. Add the family to `packages/goeist/scripts/stage-assets.mjs`, with `font/<name>.js`/`.d.ts` entries and `exports` in `package.json`.

## Source and rounding

Each family's original editable upright and italic packages are vendored unchanged under `sources/<Family>/upstream/`, pinned to [Geist v1.9.2](https://github.com/vercel/geist-font/releases/tag/v1.9.2), commit `ef2597cfc42f4797676df105517ccc0a1cfa6569`. `manifest.json` records provenance and immutable reference-font hashes.

`scripts/rounding.py` measures stems per master, then trims neighboring line/cubic segments and inserts tangent cubic fillets. Exact Bézier ink containment prevents polygon-approximation errors at curved terminals. Hidden overlap corners and concave counter corners retain their original construction. Short edges constrain local radii rather than allowing adjacent fillets to cross.

Fillet radii come from each family's profile in `scripts/families.py`, as multiples of the measured stem:

| Profile | Family | Squared ends and outer corners | Acute apexes and diagonal cuts | Arcs | Convex straight contours |
| --- | --- | --- | --- | --- | --- |
| `soft` | Goeist | 0.52 | 0.22 | trimmed independently per edge | as other corners |
| `round-nib` | Goeist Mono | 0.52 | 0.52 | always circular | stadium, half width ≤ 1.5 |

`round-nib` follows ABC Diatype Rounded Mono's "one chunky tool" construction. Every fillet is a circular arc: where a short edge limits the trim, the radius shrinks so both sides trim equally, so slab and stroke ends become semicircles rather than ellipses. Straight-edged convex contours (dots, bars, slashes, commas) become stadiums and circles, with a radius of half their width up to 1.5 stems, so dots wider than the stem are still round.

In Goeist Mono, box drawing, block elements and geometric shapes (U+2500–U+25FF) keep their exact upstream geometry: they tile across character cells, and rounding them would break connected lines and blocks in terminals.

Geist Mono's sources contain 69 exported coding-ligature glyphs (`hyphen_greater.liga`, …) but no `liga` feature: Glyphs.app derives it from glyph names at export and glyphsLib cannot. For Goeist Mono, `add_automatic_ligatures` recreates that feature, longest sequence first, identically in the unrounded baseline and the rounded source.

The transformation maintains corresponding contours and point types across Thin, Regular and Black masters, including the `f` intermediate layer at weight 801. Unmoved support cubics preserve correspondence where a corner is only exposed in some masters. Components, anchors, advances, kerning and feature definitions remain in the sources. Non-exporting helper glyphs and backup layers are retained. Geometry errors are explicit failures, not silent glyph reversions.

## Verification

`make test` builds a separate unrounded source baseline per family, compares final fonts against it, and runs geometry regressions. The font audit checks glyph and Unicode inventories, advances and line metrics, OpenType layout and HarfBuzz shaping, named and intermediate variable weights, genuine italic/style naming, CFF delivery, and WOFF2 parity. It covers unencoded glyph outlines as well as Unicode-mapped characters. The JSON report retains explicit differences between the source baseline and older official reference binaries; approved upstream drift is listed with its reason in `sources/<Family>/drift-allowlist.json`.

Attribution checks require the designer name to match the first entry in `AUTHORS.txt`, the manufacturer to be Shadcn Labs, the retained upstream copyright, the Vercel Geist Sans or Geist Mono credit with its non-affiliation statement, and OFL licensing.

**Upstream distinction, Goeist:** the pinned Geist source version is 1.900, whereas its committed reference binaries report 1.800. Both export 975 glyphs and map 728 codepoints. The source corrects an erroneous mapping of U+03C9 (lowercase omega) to the uppercase Omega outline, replacing that alias with U+2126 (ohm sign). Goeist follows this correction; it does not claim a lowercase omega design that Geist never supplied. No glyph outline is removed by this correction.

**Upstream distinction, Goeist Mono:** the pinned Geist Mono source version is 1.900, whereas its reference binaries report 1.700. The source's Italic (400) master has no kerning, while the 1.700 binary kerns at that weight; Goeist Mono follows the source.

Optional additional binary QA, with Fontspector installed separately:

```sh
make qa
```

Automated checks complement the browser proofs; they do not replace visual review of every glyph or establish testing on every operating system.
