# Goeist

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./documentation/img/goeist-banner--dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./documentation/img/goeist-banner--light.png">
  <img alt="Goeist Sans and Goeist Mono type specimens" src="./documentation/img/goeist-banner--light.png" width="1024">
</picture>

# Goeist Sans & Goeist Mono

Goeist is a font family created by [Aniket Pawar](https://github.com/Aniket-508) at [Shadcn Labs](https://shadcn-labs.com/font). It is a rounded take on [Geist Sans and Geist Mono](https://github.com/vercel/geist-font) by Vercel and Basement Studio.

Goeist Sans keeps Geist's proportions, spacing and OpenType features, and softens every exposed corner and stroke ending. It is designed for interfaces, body copy and display sizes where Geist should feel a little warmer.

Goeist Mono is the monospaced partner to Goeist Sans. Every corner is rounded as if drawn with one round tool, so stroke ends, slabs and dots become semicircles while widths stay fixed. It is designed to be used in code editors, terminals and other text-based interfaces, and keeps Geist Mono's coding ligatures.

### Installation

Download the latest release from the [releases page](https://github.com/shadcn-labs/goeist-font/releases/latest) and install the fonts on your system.

**Via npm package:**

```
npm i goeist
```

```js
import { GoeistSans } from "goeist/font/sans";
import { GoeistMono } from "goeist/font/mono";
```

See the [package README](packages/goeist/README.md) for the App Router, Pages Router and Tailwind CSS setup.

### Inspiration

Goeist is drawn from Geist's outlines. [Open Runde](https://github.com/lauridskern/open-runde), [Intern](https://github.com/bvvst/intern) and [Sunghyun Sans](https://github.com/anaclumos/sunghyun-sans) showed how far rounding can go in a sans; Goeist Mono looks to [ABC Diatype Rounded Mono](https://abcdinamo.com/typefaces/diatype-rounded). Thanks to everyone behind them.

## Building

Fonts are built automatically by GitHub Actions - take a look in the "Actions" tab for the latest build.

If you want to build fonts manually on your own computer:

- `make build` will produce font files.
- `make test` will check the fonts against the unrounded Geist sources and run the geometry tests.
- `make qa` will run [Fontspector](https://github.com/fonttools/fontspector)'s quality assurance tests.
- `make proof` will generate HTML proof files.

The proof files and QA tests are also available automatically via GitHub Actions - look at https://shadcn-labs.github.io/goeist-font/.

## License

Copyright 2026 Aniket Pawar.

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is available with a FAQ at
https://openfontlicense.org

The original Geist copyright notices are kept in [`OFL.txt`](OFL.txt).

## Disclaimer

Goeist is independent, not affiliated with or endorsed by [Vercel](https://vercel.com/geist/brands#usage) or [Dinamo](https://abcdinamo.com/licenses). ABC Diatype is a visual reference only; none of its font data is used.

Vercel, the Vercel design, Next.js and related marks, designs and logos are trademarks or registered trademarks of Vercel, Inc. or its affiliates in the US and other countries.

## Repository Layout

This font repository structure is inspired by [Unified Font Repository v0.3](https://github.com/unified-font-repository/Unified-Font-Repository), modified for the Google Fonts workflow.
