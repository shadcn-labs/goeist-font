<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/shadcn-labs/goeist-font/main/documentation/img/goeist-banner--dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/shadcn-labs/goeist-font/main/documentation/img/goeist-banner--light.png">
  <img alt="Goeist Sans and Goeist Mono type specimens" src="https://raw.githubusercontent.com/shadcn-labs/goeist-font/main/documentation/img/goeist-banner--light.png" width="1024">
</picture>

# Goeist Sans & Goeist Mono

Goeist is a font family created by [Aniket Pawar](https://github.com/Aniket-508) at [Shadcn Labs](https://shadcn-labs.com/font). It is a rounded take on [Geist Sans and Geist Mono](https://github.com/vercel/geist-font).

Goeist Sans keeps Geist's proportions and spacing, with softened corners and stroke endings. Goeist Mono is its monospaced partner, rounded as if drawn with one round tool, for code editors, terminals and other text-based interfaces.

### Installation

```sh
npm install goeist
```

### Using with Next.js

`GoeistSans` is exported from `goeist/font/sans` and `GoeistMono` from `goeist/font/mono`. Both are `NextFontWithVariable` instances that load the upright and italic variable fonts through `next/font/local`, so there is nothing else to import. You can learn more by [reading the `next/font` docs](https://nextjs.org/docs/app/building-your-application/optimizing/fonts).

| Export | Entry point | CSS Variable |
| --- | --- | --- |
| `GoeistSans` | `goeist/font/sans` | `--font-goeist-sans` |
| `GoeistMono` | `goeist/font/mono` | `--font-goeist-mono` |
| `GoeistSansNonVariable` | `goeist/font/sans-non-variable` | `--font-goeist-sans-non-variable` |
| `GoeistMonoNonVariable` | `goeist/font/mono-non-variable` | `--font-goeist-mono-non-variable` |

The non-variable exports load 18 static files and are only needed for browsers without variable-font support.

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

#### With Tailwind CSS

Both fonts can be used through CSS variables.

In `app/layout.js`:

```jsx
import { GoeistSans } from "goeist/font/sans";
import { GoeistMono } from "goeist/font/mono";

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${GoeistSans.variable} ${GoeistMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

##### Tailwind CSS V4

Then in `tailwind.css`:

```css
@theme {
  /* rest of your theme config */
  --font-sans: var(--font-goeist-sans);
  --font-mono: var(--font-goeist-mono);
}
```

##### Tailwind CSS V3

Then in `tailwind.config.js`:

```js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-goeist-sans)"],
        mono: ["var(--font-goeist-mono)"],
      },
    },
  },
};
```

### Other frameworks

Outside Next.js, import the stylesheet once and use the font family by name:

```js
import "goeist/sans.css"; // or "goeist/sans-static.css"
import "goeist/mono.css"; // or "goeist/mono-static.css"
```

```css
body {
  font-family: "Goeist", sans-serif;
}
```

### License

Copyright 2026 Aniket Pawar. This Font Software is licensed under the SIL Open Font License, Version 1.1. The original Geist copyright notices are included in `LICENSE.txt`.

### Disclaimer

Goeist is independent, not affiliated with or endorsed by [Vercel](https://vercel.com/geist/brands#usage) or [Dinamo](https://abcdinamo.com/licenses). ABC Diatype is a visual reference only; none of its font data is used.

Vercel, the Vercel design, Next.js and related marks, designs and logos are trademarks or registered trademarks of Vercel, Inc. or its affiliates in the US and other countries.
