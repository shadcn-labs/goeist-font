# Contributing to Goeist

## Reporting issues

Use the [Font Issue Report](https://github.com/shadcn-labs/goeist-font/issues/new?template=BUG_REPORT.md). Include the font family, steps to reproduce, screenshots, OS and software. The internal font version and npm package version are separate; include both when reporting a package issue.

## Build

Requires Python 3.12 and `make`. The first command creates `venv/` and installs the locked Python toolchain. No Glyphs application, native font editor, or separately installed autohinter is required. Subsequent builds work offline with the installed environment and vendored sources.

```sh
make build
make test
make proof
```

Every target runs for each family in `scripts/families.py` (`Goeist`, `GoeistMono`, `GoeistSerif`); `make build FAMILIES=GoeistMono` limits it to one. The scripts take the same key: `venv/bin/python scripts/build.py --family GoeistMono`. Paths below use `<Family>`.

| Output | Location |
| --- | --- |
| Variable TTF: upright and italic `[wght]` (Sans, Mono); one `[ELSH]` (Serif) | `fonts/<Family>/variable/` |
| Static TTF styles: eighteen weights (Sans, Mono); four Element Shapes (Serif) | `fonts/<Family>/ttf/` |
| Static OTF styles, as the TTFs | `fonts/<Family>/otf/` |
| Variable and static WOFF2, with CSS | `fonts/<Family>/webfonts/` |
| Editable rounded Glyphs sources | `build/<Family>/sources/` |
| Per-glyph geometry reports | `build/<Family>/rounding-upright.json` and, for families with italics, `build/<Family>/rounding-italic.json` |
| Coverage, shaping and delivery audit | `out/<Family>/verification.json` |
| Interactive specimen and full-glyph atlases | `out/<Family>/proof/` |

Commit `fonts/` after every rebuild; it is the release output and the npm package's source.

Static TTFs are strictly autohinted with `ttfautohint-py`. Variable TTFs and static OTFs are not autohinted; static TrueType instructions cannot be reused after outline changes or copied into variable fonts. Failed compilation or static hinting stops the build before publishing artifacts. Existing unrelated files in `fonts/<Family>/` are not deleted.

Static advances are taken from the corresponding variable-font location before hinting. This resolves one-unit component-interpolation differences between independently compiled statics and HVAR; both the horizontal metrics and embedded CFF charstring widths are aligned without changing outlines. Goeist Serif has one master, so its statics need no alignment.

Build manifests hash every upstream package file, build configuration, geometry code and compiler versions. Changed or missing outputs invalidate the cache. `SOURCE_DATE_EPOCH` controls binary timestamps; the default is fixed. To force exports or limit compiler concurrency:

```sh
venv/bin/python scripts/build.py --family Goeist --force --jobs 4
```

## Preview

Serve the repository root, not just the proof directory:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open <http://127.0.0.1:8765/out/Goeist/proof/>, <http://127.0.0.1:8765/out/GoeistMono/proof/> or <http://127.0.0.1:8765/out/GoeistSerif/proof/>. Each specimen provides axis (weight, or Element Shape for Goeist Serif), size, style and OpenType controls, original-versus-rounded text, small-size waterfalls, a code sample, and complete outline atlases of every static style (plus intermediate weights for Sans and Mono). Unencoded glyphs are shown directly as SVG outlines. Unsupported characters receive explicit codepoint labels rather than silently appearing in a fallback font. All assets are local.

## Web use without npm

Load `fonts/Goeist/webfonts/goeist.css`, `fonts/GoeistMono/webfonts/goeist-mono.css` or `fonts/GoeistSerif/webfonts/goeist-serif.css` and keep its sibling WOFF2 files alongside it. Use the matching `-static.css` instead for individual static webfonts; do not load both.

```html
<link rel="stylesheet" href="/fonts/Goeist/webfonts/goeist.css">
<link rel="stylesheet" href="/fonts/GoeistMono/webfonts/goeist-mono.css">
<link rel="stylesheet" href="/fonts/GoeistSerif/webfonts/goeist-serif.css">
```

Goeist Serif's variable font picks its dots with `font-variation-settings: "ELSH" 0` (round), `25` (square), `50` (triangle) or `100` (heart). Its static stylesheet declares each shape as its own family: `Goeist Serif`, `Goeist Serif Square`, `Goeist Serif Triangle` and `Goeist Serif Heart`.

## Versioning and npm release

Font versions (currently `1.000`) are set once in `FONT_VERSION` in `scripts/families.py`; keep `version` in each `sources/<Family>/config.yaml` equal to it (the build refuses a mismatch). Fontspector's Google Fonts profile requires font versions of at least `1.000`. The npm package uses semantic versions (such as `0.0.2`) independently, managed by [Changesets](https://github.com/changesets/changesets) in `packages/goeist`, as in `vercel/geist-font`. Requires Node 22 (`.nvmrc`) and pnpm.

With every change that should ship, add a changeset describing it:

```sh
cd packages/goeist
pnpm install
pnpm changeset          # pick patch / minor / major and write the summary
```

Releases are automated by `.github/workflows/release.yml`, which is registered as the npm trusted publisher for `goeist`. Changesets only versions; the same workflow publishes, tags and releases:

1. Commit the rebuilt `fonts/` (`make build`) and a changeset, and push or merge to `main`.
2. The workflow opens or updates a **Version packages** pull request that bumps `package.json` and `CHANGELOG.md`.
3. Merging it publishes the new version to npm through OIDC (no token, with provenance) and creates the GitHub Release `v<version>` with `Goeist-v<version>.zip`, `GoeistMono-v<version>.zip`, `GoeistSerif-v<version>.zip` (committed fonts plus licenses) and that version's changelog notes.

Pushes without changesets publish nothing: the workflow skips versions already on npm. Do not merge Changesets prerelease state (`.changeset/pre.json`); the `Guard prerelease state` workflow rejects it. `make package` writes an inspectable `goeist-<version>.tgz` without publishing.

`prepack` (`scripts/stage-assets.mjs`) copies each family's `fonts/<Family>/webfonts/` into the package and renames `Goeist[wght].woff2` to `Goeist-Variable.woff2` (likewise for Goeist Mono, and `GoeistSerif[ELSH].woff2` to `GoeistSerif-Variable.woff2`), so publishing always ships the committed fonts. Once on npm, the package is also served by jsDelivr and unpkg, e.g. `https://cdn.jsdelivr.net/npm/goeist@<version>/assets/goeist-mono/goeist-mono.css`.

## Adding a family

1. Vendor the upstream `.glyphspackage` sources (upright and italic, or the single package of a one-master family), reference fonts, licenses and a `manifest.json` under `sources/<Family>/upstream/`.
2. Add `sources/<Family>/config.yaml` (gftools recipe with the family name and STAT tables).
3. Register the family and its rounding profile in `scripts/families.py`, and add it to `FAMILIES` in the `Makefile`, the release workflow and `scripts/index.html`.
4. Add the family to `packages/goeist/scripts/stage-assets.mjs`, with `font/<name>.js`/`.d.ts` entries and `exports` in `package.json`.

## Source and rounding

Each family's original editable packages are vendored unchanged under `sources/<Family>/upstream/`, pinned to [Geist v1.9.2](https://github.com/vercel/geist-font/releases/tag/v1.9.2), commit `ef2597cfc42f4797676df105517ccc0a1cfa6569`. `manifest.json` records provenance and immutable reference-font hashes. The design research behind the profiles is in [`research/`](research/README.md).

`scripts/rounding.py` measures stems per master, then trims neighboring line/cubic segments and inserts tangent cubic fillets. Exact Bézier ink containment prevents polygon-approximation errors at curved terminals. Hidden overlap corners and concave counter corners retain their original construction. Short edges constrain local radii rather than allowing adjacent fillets to cross.

Fillet radii come from each family's profile in `scripts/families.py`, as multiples of the measured stem:

| Profile | Family | Squared ends and outer corners | Acute apexes and diagonal cuts | Arcs | Convex straight contours | Local stroke |
| --- | --- | --- | --- | --- | --- | --- |
| `soft` | Goeist | 0.52 | 0.22 | trimmed independently per edge | as other corners | — |
| `round-nib` | Goeist Mono | 0.52 | 0.52 | always circular | stadium, half width ≤ 1.5 | — |
| `soft-serif` | Goeist Serif | 0.33 | 0.22 | always circular | as other corners | radius ≤ 0.5 × thickness across the corner |

`round-nib` follows ABC Diatype Rounded Mono's "one chunky tool" construction. Every fillet is a circular arc: where a short edge limits the trim, the radius shrinks so both sides trim equally, so slab and stroke ends become semicircles rather than ellipses. Straight-edged convex contours (dots, bars, slashes, commas) become stadiums and circles, with a radius of half their width up to 1.5 stems, so dots wider than the stem are still round.

In Goeist Mono, box drawing, block elements and geometric shapes (U+2500–U+25FF) keep their exact upstream geometry: they tile across character cells, and rounding them would break connected lines and blocks in terminals.

Geist Mono's sources contain 69 exported coding-ligature glyphs (`hyphen_greater.liga`, …) but no `liga` feature: Glyphs.app derives it from glyph names at export and glyphsLib cannot. For Goeist Mono, `add_automatic_ligatures` recreates that feature, longest sequence first, identically in the unrounded baseline and the rounded source.

The transformation maintains corresponding contours and point types across Thin, Regular and Black masters, including the `f` intermediate layer at weight 801. Unmoved support cubics preserve correspondence where a corner is only exposed in some masters. Components, anchors, advances, kerning and feature definitions remain in the sources. Non-exporting helper glyphs and backup layers are retained. Geometry errors are explicit failures, not silent glyph reversions.

A fillet is not linear in weight, so interpolating only rounded Thin, Regular and Black bends the joins of curved terminals between them (up to 30° in S, g, 3 and 5). The static fonts are therefore built from a second source per slope, `build/<Family>/sources/statics/`, in which `add_intermediate_layers` adds an unrounded brace layer at every named weight in between (200, 300, 500, 600, 700, 800), interpolated through any existing sparse layer, and rounds each from its own outline; widths and anchors are rounded as the baseline rounds them, so no metric moves. The variable fonts keep the three masters: extra masters there would have their advance deltas rounded per region and move advances by a unit. In the variable fonts, where a fillet joins a curve whose tangent turns across masters, `equalize_join_ratios` gives its handle one length ratio to the opposite side in every master, which keeps the interpolated join smooth; a join that would need a handle changed by more than 1.6× keeps its circular handle.

Glyphs open corners (crossing loops that cut a terminal or an arrow tip) are erased with glyphsLib's own pen before ink is measured, so their loop corners count as construction, not exposed ink, in every family.

### Goeist Serif

Geist Serif draws its serifs with Glyphs corner and cap components (`_corner.ucSerif`, `_corner.lcSerif`, `_corner.numSerif`, `_corner.serif-alt`, `_cap.stem`, `_cap.stem-alt`): a curved bracket, a straight wedge and a tip only 4–6 units thick. glyphsLib and fontmake cannot place them, so upstream's `glyphs_corners.py` and `build-geist-serif.py` are vendored unchanged in `sources/GoeistSerif/upstream/scripts/`. `scripts/serif.py` builds the source in four steps, then compiles it as upstream does:

1. **Soft serif tips.** While each component is placed, its tip is replaced by one circular end tangent to the serif's flat side, at the serif's original reach, so serif lengths, spacing and kerning are unchanged. A 4-unit tip cannot hold a visible round, so the end is thickened to `tip` = 26 units (about Geist Serif's 29–38 unit hairline), closed with a half-round of 13, and the wedge is redrawn as the tangent from the bracket, whose handle is turned to stay tangent. This follows the serif ends of Fraunces' SOFT axis rather than trimming corners.
2. **Ink, not construction.** Glyphs open corners (the self-crossing loops that cut terminals such as c and e) are erased with glyphsLib's own filter and each layer's paths are unioned, removing skia's sub-unit slivers, so only exposed ink corners are rounded.
3. **Cut terminals and spikes.** A straight cut of up to 14 units between two convex corners (s, c, e, a, r, f, the figures) and any convex spike sharper than 140° becomes the arc of the 13-unit circle inscribed in the stroke where it is that thick, tangent to both sides and inside the original ink.
4. **Every other corner** gets the shared fillets with the `soft-serif` profile: circular, a third of a stem on stem corners, 0.22 stems on apexes, and never more than half the ink thickness measured across the corner, so hairline corners round in proportion to the hairline. Concave joins and brackets stay as drawn, as in Fraunces, SF Pro Rounded and Open Runde.

The family has one master, so topology is free per glyph. The compiled variable font has one Element Shape (`ELSH`) axis that only swaps dot glyphs through `rclt` feature variations (no `gvar`); each static applies its instance's Rename Glyphs and Replace Feature parameters, as Glyphs does. The variable font is not autohinted, like the other families' variable fonts.

5. **Collision guard.** The thickened tips add ink outside the drawn serif, so a few pairs (`yt`, `wt`, `vv`, `dA` …) would touch where Geist Serif's hairline points only met. `scripts/collisions.py` shapes every pair of encoded characters with kerning on, reads each glyph's ink in rows 4 units apart, and for every pair now closer than both 4 units and its Geist Serif gap adds the difference to one extra `kern` lookup, after the [make-font](https://github.com/arla6ka/design.how/blob/main/skills/make-font/references/spacing.md) collision guard. It only opens pairs; upstream's own touching serif points (AA, VV) are kept. The pairs are listed in `build/GoeistSerif/collision-guard.json` and summarized in `FONTLOG.txt`.

## Verification

`make test` builds a separate unrounded source baseline per family, compares final fonts against it, and runs geometry regressions. The font audit checks glyph and Unicode inventories, advances and line metrics, OpenType layout and HarfBuzz shaping, named and intermediate variable weights, genuine italic/style naming, CFF delivery, and WOFF2 parity. It covers unencoded glyph outlines as well as Unicode-mapped characters. The JSON report retains explicit differences between the source baseline and older official reference binaries; approved upstream drift is listed with its reason in `sources/<Family>/drift-allowlist.json`. For Goeist Serif, the recorded collision-guard lookup is removed before GPOS and shaping are compared, and its pair count must match the build's record. A collision check fails any static whose shaped pairs sit closer than both their baseline gap and the make-font minimum (6 units for Sans and Mono, 4 for Serif), allowing 3 units for TrueType quadratic conversion and grid rounding (1.5 per glyph).

Each build writes `fonts/<Family>/FONTLOG.txt`: the base and its licence, the rounding profile, measured stems, corner and join counts, serif and collision-guard numbers. The release workflow ships it in each family's zip.

Attribution checks require the designer name to match the first entry in `AUTHORS.txt`, the manufacturer to be Shadcn Labs, the OS/2 vendor ID to be Shadcn Labs' `CNLB` rather than Geist's inherited `VRCL`, the retained upstream copyright, the Vercel Geist Sans, Geist Mono or Geist Serif credit with its non-affiliation statement, and OFL licensing. Goeist Serif statics are checked as one legacy family per shape (`Goeist Serif Square`, …), and only the Regular static is compared against its variable instance, since the shape statics rename their dot glyphs.

`CNLB` identifies Shadcn Labs as the font vendor; the designer and modification copyright remain Aniket Pawar. The ID is not yet in Microsoft's vendor registry. [Registration is optional](https://learn.microsoft.com/en-us/typography/vendors/register), so Fontspector may warn about the unregistered ID.

**Upstream distinction, Goeist:** the pinned Geist source version is 1.900, whereas its committed reference binaries report 1.800. Both export 975 glyphs and map 728 codepoints. The source corrects an erroneous mapping of U+03C9 (lowercase omega) to the uppercase Omega outline, replacing that alias with U+2126 (ohm sign). Goeist follows this correction; it does not claim a lowercase omega design that Geist never supplied. No glyph outline is removed by this correction.

**Upstream distinction, Goeist Mono:** the pinned Geist Mono source version is 1.900, whereas its reference binaries report 1.700. The source's Italic (400) master has no kerning, while the 1.700 binary kerns at that weight; Goeist Mono follows the source.

**Upstream distinction, Goeist Serif:** the pinned Geist Serif source and its reference binaries both report 1.003, with 898 glyphs and 465 codepoints. Goeist Serif's baseline matches the reference statics in glyphs, codepoints, metrics, advances, layout features and shaping; only the binary encoding of GPOS differs. Geist Serif's source contains no italic and only the Regular master; its announced weights and italic are not yet published upstream.

Fontspector QA (Google Fonts profile), installed separately:

```sh
make qa
```

CI runs `make test`, `make qa` and `make proof` for pull requests and main-branch pushes. Main-branch builds publish the proofs, verification reports and Fontspector reports to GitHub Pages at <https://shadcn-labs.github.io/goeist-font/>. These are development pages, separate from the font's marketing page at <https://shadcn-labs.com/font>. Automated checks complement the browser proofs; they do not replace visual review of every glyph or establish testing on every operating system.
