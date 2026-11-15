<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/shadcn-labs/goeist-font/main/documentation/img/goeist-banner--dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/shadcn-labs/goeist-font/main/documentation/img/goeist-banner--light.png">
  <img alt="Goeist Sans, Goeist Mono and Goeist Serif type specimens" src="https://raw.githubusercontent.com/shadcn-labs/goeist-font/main/documentation/img/goeist-banner--light.png" width="1024">
</picture>

# Goeist Sans, Goeist Mono & Goeist Serif

Goeist is a font family created by [Aniket Pawar](https://github.com/Aniket-508) at [Shadcn Labs](https://shadcn-labs.com/font). It is a rounded take on [Geist Sans, Geist Mono and Geist Serif](https://github.com/vercel/geist-font).

Goeist Sans keeps Geist's proportions and spacing, with softened corners and stroke endings. It is designed for body copy, headlines and interfaces.

Goeist Mono is its monospaced partner, rounded as if drawn with one round tool, for code editors, terminals and other text-based interfaces.

Goeist Serif is a soft display serif: Geist Serif's saw-toothed serifs end in half-rounds and its hairlines stay fine. It includes Regular, Square, Triangle and Heart dot shapes.

### Installation

```sh
npm install goeist
```

### Using with Next.js

`GoeistSans` is exported from `goeist/font/sans` and `GoeistMono` from `goeist/font/mono`. Goeist Serif ships a variable entry point (`goeist/font/serif`) and one entry point per variant (e.g. `goeist/font/serif/square`), so you only emit and preload the files you import. All are `NextFontWithVariable` instances. You can learn more by [reading the `next/font` docs](https://nextjs.org/docs/app/building-your-application/optimizing/fonts).

#### Goeist Serif Variants

Use `GoeistSerif` to load one variable font and select its shape through `ELSH`:

```jsx
import { GoeistSerif } from "goeist/font/serif";
```

| Shape | `ELSH` value |
| --- | --- |
| Regular | `0` |
| Square | `25` |
| Triangle | `50` |
| Heart | `100` |

Goeist Serif includes four distinct variants: Regular with round dots (the default), Square, Triangle and Heart. All have one Regular weight (400). Use their individual entry points to emit and preload only the fonts you import:

| Export | Entry point | CSS Variable |
| --- | --- | --- |
| `GoeistSerifRegular` | `goeist/font/serif/regular` | `--font-goeist-serif-regular` |
| `GoeistSerifSquare` | `goeist/font/serif/square` | `--font-goeist-serif-square` |
| `GoeistSerifTriangle` | `goeist/font/serif/triangle` | `--font-goeist-serif-triangle` |
| `GoeistSerifHeart` | `goeist/font/serif/heart` | `--font-goeist-serif-heart` |

```jsx
import { GoeistSerifRegular } from "goeist/font/serif/regular";
import { GoeistSerifSquare } from "goeist/font/serif/square";
import { GoeistSerifTriangle } from "goeist/font/serif/triangle";
import { GoeistSerifHeart } from "goeist/font/serif/heart";
```

#### App Router

In `app/layout.js`:

```jsx
import { GoeistSans } from "goeist/font/sans";

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={GoeistSans.className}>
      <body>{children}</body>
    </html>
  );
}
```

#### Pages Router

In `pages/_app.js`:

```jsx
import { GoeistSans } from "goeist/font/sans";

export default function MyApp({ Component, pageProps }) {
  return (
    <main className={GoeistSans.className}>
      <Component {...pageProps} />
    </main>
  );
}
```

If you're using a version of Next.js that's older than 15, then in `next.config.js` or `next.config.mjs` add:

```diff js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
+  transpilePackages: ["goeist"],
};

export default nextConfig;
```

This is required to fix errors like:

- `TypeError: next_font_local__WEBPACK_IMPORTED_MODULE_0___default(...) is not a function`
- `SyntaxError: Cannot use import statement outside a module`

#### With Tailwind CSS

All Goeist fonts can be used through CSS variables.

- `GoeistSans`: `--font-goeist-sans`
- `GoeistMono`: `--font-goeist-mono`
- `GoeistSerif`: `--font-goeist-serif`
- `GoeistSerifRegular`: `--font-goeist-serif-regular`
- `GoeistSerifSquare`: `--font-goeist-serif-square`
- `GoeistSerifTriangle`: `--font-goeist-serif-triangle`
- `GoeistSerifHeart`: `--font-goeist-serif-heart`

In `app/layout.js`:

```jsx
import { GoeistSans } from "goeist/font/sans";
import { GoeistMono } from "goeist/font/mono";
import { GoeistSerif } from "goeist/font/serif";

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={`${GoeistSans.variable} ${GoeistMono.variable} ${GoeistSerif.variable}`}
    >
      <body>{children}</body>
    </html>
  );
}
```

##### Tailwind CSS V4

Then in `tailwind.css`:

```css
@import "tailwindcss";

@theme inline {
  --font-sans: var(--font-goeist-sans);
  --font-mono: var(--font-goeist-mono);
  --font-serif: var(--font-goeist-serif);
}
```

##### Tailwind CSS V3

Then in `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-goeist-sans)"],
        mono: ["var(--font-goeist-mono)"],
        serif: ["var(--font-goeist-serif)"],
      },
    },
  },
};
```

### License

The Goeist font family is free and open sourced under the [SIL Open Font License](./LICENSE.txt).

### Inspiration

Goeist is a rounded take on [Geist](https://github.com/vercel/geist-font), created by Vercel and its collaborators. [ABC Diatype](https://abcdinamo.com/typefaces/diatype) is a visual reference only; none of its font data is used. We thank the creators of these typefaces for their craft.

Goeist is independent, not affiliated with or endorsed by Vercel or Dinamo.
