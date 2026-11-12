# Goist

Goist is a font family created by [Aniket-508](https://github.com/Aniket-508), developed under [Shadcn Labs](https://shadcn-labs.com/font). It is a rounded derivative of [Geist Sans](https://github.com/vercel/geist-font), created by Vercel in collaboration with Basement Studio.

Goist keeps Geist's skeleton, proportions, spacing and OpenType features, and softens exposed corners and stroke endings with stem-relative curves. It is designed for interfaces, body copy and display sizes where Geist's precision should feel a little warmer.

- Nine weights, Thin (100) to Black (900), with genuine italics.
- Upright and italic variable fonts, plus static TTF, OTF and WOFF2.
- All 975 exported glyphs per style: Latin, extended Latin, Vietnamese and Cyrillic.
- Eleven stylistic sets (`ss01`–`ss11`), localized forms, fractions, numeral variants, kerning and mark positioning.

### Installation

Download the fonts from [`fonts/Goist/`](fonts/Goist/) and install them on your system.

**Via npm package:**

```
npm i goist
```

```js
import { GoistSans } from "goist/font/sans"; // Next.js (next/font)
import "goist/sans.css";                     // any other bundler
```

See the [package README](packages/goist/README.md) for Tailwind, static fonts and CSS variables. The specimen lives at [shadcn-labs.com/font](https://shadcn-labs.com/font).

### Inspiration

Goist is built on the outlines of [Geist Sans](https://github.com/vercel/geist-font). Its rounding was informed by [Sunghyun Sans](https://github.com/anaclumos/sunghyun-sans), [Intern](https://github.com/bvvst/intern) and [Open Runde](https://github.com/lauridskern/open-runde). Goist does not merge outlines from these references. We thank their creators for their craft.

## Building

- `make build` will produce font files in `fonts/Goist/`.
- `make test` will verify the fonts against the unrounded Geist sources and run the geometry tests.
- `make proof` will generate an HTML proof in `out/Goist/proof/`.

Requires Python 3.12 and `make`. See [CONTRIBUTING.md](CONTRIBUTING.md) for the build pipeline, verification and npm releases.

## License

This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at https://openfontlicense.org

Goist's rounded design and modifications are copyright 2026 Aniket-508. The original Geist copyright and license notices are retained in [`OFL.txt`](OFL.txt) and [`sources/Goist/upstream/`](sources/Goist/upstream/), and the Geist contributors are credited in [`CONTRIBUTORS.txt`](CONTRIBUTORS.txt).

## Disclaimer

Goist is an independent project. It is not affiliated with, sponsored by or endorsed by Vercel, Inc., and is not an official Geist release. Vercel, the Vercel design, Next.js and related marks, designs and logos are trademarks or registered trademarks of Vercel, Inc. or its affiliates in the US and other countries.

## Repository Layout

Each family owns one directory under `sources/`, `fonts/`, `build/` and `out/`; Goist Mono will be added as `GoistMono`.

| Path | Contents |
| --- | --- |
| `sources/Goist/` | gftools recipe and vendored upstream Geist Sans sources |
| `fonts/Goist/` | release TTF, OTF, variable and WOFF2 fonts |
| `packages/goist/` | the `goist` npm package |
| `scripts/`, `tests/` | build driver, rounding geometry, audits, proofs |
| `build/`, `out/` | generated sources, baselines, reports and proofs (git-ignored) |
