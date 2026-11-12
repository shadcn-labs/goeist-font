# Goeist Sans & Goeist Mono

Goeist is a font family created by [Aniket-508](https://github.com/Aniket-508), developed under [Shadcn Labs](https://shadcn-labs.com/font). Goeist Sans and Goeist Mono are rounded derivatives of [Geist Sans and Geist Mono](https://github.com/vercel/geist-font), created by Vercel in collaboration with Basement Studio.

Goeist Sans keeps Geist's skeleton, proportions, spacing and OpenType features, and softens exposed corners and stroke endings with stem-relative curves. It is designed for interfaces, body copy and display sizes where Geist's precision should feel a little warmer.

Goeist Mono is the monospaced partner to Goeist Sans. Every exposed corner is drawn as if by one round tool: stroke endings, slabs and dots become semicircles, and apexes are fully rounded, while widths stay fixed. It is designed for code editors, terminals and other text-based interfaces.

- Nine weights, Thin (100) to Black (900), with genuine italics, in both families.
- Upright and italic variable fonts, plus static TTF, OTF and WOFF2.
- Goeist Sans: 975 exported glyphs per style, eleven stylistic sets (`ss01`–`ss11`), fractions, numeral variants, kerning and mark positioning.
- Goeist Mono: 1,158 upright and 1,147 italic glyphs, coding ligatures (`->`, `=>`, `!=`, `===`, …), stylistic sets and fractions.
- Latin, extended Latin, Vietnamese and Cyrillic coverage.

### Installation

Download the latest release from the [releases page](https://github.com/shadcn-labs/goeist-font/releases/latest) (or the files in [`fonts/Goeist/`](fonts/Goeist/) and [`fonts/GoeistMono/`](fonts/GoeistMono/)) and install the fonts on your system.

**Via npm package:**

```
npm i goeist
```

```js
import { GoeistSans } from "goeist/font/sans"; // Next.js (next/font)
import { GoeistMono } from "goeist/font/mono";
import "goeist/sans.css";                     // any other bundler
import "goeist/mono.css";
```

See the [package README](packages/goeist/README.md) for Tailwind, static fonts and CSS variables. The specimen lives at [shadcn-labs.com/font](https://shadcn-labs.com/font).

**Via CDN:**

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/goeist@0.0.1/assets/goeist-sans/goeist-sans.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/goeist@0.0.1/assets/goeist-mono/goeist-mono.css">
```

Then use `font-family: "Goeist"` and `font-family: "Goeist Mono"`.

### Inspiration

Goeist is built on the outlines of [Geist Sans and Geist Mono](https://github.com/vercel/geist-font). Goeist Sans' rounding was informed by [Sunghyun Sans](https://github.com/anaclumos/sunghyun-sans), [Intern](https://github.com/bvvst/intern) and [Open Runde](https://github.com/lauridskern/open-runde). None of these has a monospaced counterpart, so Goeist Mono's rounding takes its cue from [ABC Diatype Rounded Mono](https://abcdinamo.com/typefaces/diatype-rounded) by Dinamo. Goeist does not use outlines from any of these references. We thank their creators for their craft.

## Building

- `make build` will produce font files in `fonts/Goeist/` and `fonts/GoeistMono/`.
- `make test` will verify the fonts against the unrounded Geist sources and run the geometry tests.
- `make proof` will generate HTML proofs in `out/Goeist/proof/` and `out/GoeistMono/proof/`.

Add `FAMILIES=GoeistMono` to any target to work on one family. Requires Python 3.12 and `make`. See [CONTRIBUTING.md](CONTRIBUTING.md) for the build pipeline, verification and npm releases.

## License

This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at https://openfontlicense.org

Goeist's rounded designs and modifications are copyright 2026 Aniket-508. The original Geist copyright and license notices are retained in [`OFL.txt`](OFL.txt) and in each family's `sources/<Family>/upstream/`, and the Geist contributors are credited in [`CONTRIBUTORS.txt`](CONTRIBUTORS.txt).

## Disclaimer

Goeist is an independent project. It is not affiliated with, sponsored by or endorsed by Vercel, Inc. or Dinamo, and is not an official Geist release. Vercel, the Vercel design, Next.js and related marks, designs and logos are trademarks or registered trademarks of Vercel, Inc. or its affiliates in the US and other countries. ABC Diatype Rounded is a typeface by Dinamo; Goeist Mono contains none of its outlines or font data.

## Repository Layout

Each family owns one directory under `sources/`, `fonts/`, `build/` and `out/`, and is registered in [`scripts/families.py`](scripts/families.py).

| Path | Contents |
| --- | --- |
| `sources/Goeist/`, `sources/GoeistMono/` | gftools recipes and vendored upstream Geist Sans and Geist Mono sources |
| `fonts/Goeist/`, `fonts/GoeistMono/` | release TTF, OTF, variable and WOFF2 fonts |
| `packages/goeist/` | the `goeist` npm package |
| `scripts/`, `tests/` | family registry, build driver, rounding geometry, audits, proofs |
| `build/`, `out/` | generated sources, baselines, reports and proofs (git-ignored) |
