# Changelog

## Goist Mono 1.000, `goist` 1.1.0 — 2026-11-12

- Added Goist Mono, a rounded derivative of Geist Mono v1.9.2: nine weights with genuine italics, variable and static TTF, OTF and WOFF2.
- Added the `round-nib` rounding profile after ABC Diatype Rounded Mono: fully rounded apexes and circular arcs, so stroke ends, slabs and dots become semicircles and circles.
- Recreated Geist Mono's coding ligatures (`liga`), which the upstream source leaves to Glyphs.app's automatic features.
- Added `goist/font/mono`, `goist/font/mono-non-variable`, `goist/mono.css` and `goist/mono-static.css` to the npm package.
- Build, verification and proof scripts now take `--family`; `make` targets run for every family.

## Goist 1.000, `goist` 1.0.0 — 2026-11-12

- Added stem-relative rounded outlines across the complete upright and italic source families.
- Preserved the full exported glyph repertoire, all eleven stylistic sets and the original advance/line-metric contract.
- Added portable static, variable and webfont builds, strict source-parity verification, geometry regression tests and offline interactive proofs.
- Added the `goist` npm package with `next/font` and plain CSS entry points.
- Font metadata names Aniket-508 as designer and copyright holder and Shadcn Labs as manufacturer, credits Vercel Geist Sans, retains its required notices and states that Goist is not affiliated with Vercel.
