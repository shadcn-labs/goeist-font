# Goeist Sans & Goeist Mono

Goeist is a font family created by [Aniket-508](https://github.com/Aniket-508), developed under [Shadcn Labs](https://shadcn-labs.com/font). Goeist Sans is a rounded derivative of [Geist Sans](https://github.com/vercel/geist-font) and Goeist Mono of Geist Mono, both created by Vercel in collaboration with Basement Studio. Each has nine weights (100–900) with genuine italics, as variable and static WOFF2.

```sh
npm install goeist
```

## Next.js

`GoeistSans` and `GoeistMono` load the upright and italic variable fonts through `next/font/local`.

```tsx
// app/layout.tsx
import { GoeistSans } from "goeist/font/sans";
import { GoeistMono } from "goeist/font/mono";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${GoeistSans.variable} ${GoeistMono.variable}`}>
      <body className={GoeistSans.className}>{children}</body>
    </html>
  );
}
```

Use the CSS variables to combine them with Tailwind or other fonts:

```css
/* Tailwind v4 */
@theme {
  --font-sans: var(--font-goeist-sans);
  --font-mono: var(--font-goeist-mono);
}
```

| Export | Entry point | CSS variable |
| --- | --- | --- |
| `GoeistSans` | `goeist/font/sans` | `--font-goeist-sans` |
| `GoeistSansNonVariable` | `goeist/font/sans-non-variable` | `--font-goeist-sans-non-variable` |
| `GoeistMono` | `goeist/font/mono` | `--font-goeist-mono` |
| `GoeistMonoNonVariable` | `goeist/font/mono-non-variable` | `--font-goeist-mono-non-variable` |

Prefer the variable exports (two files each). The non-variable exports ship 18 static files and are only needed for browsers without variable-font support.

## Plain CSS (Vite, Astro, Remix, …)

```js
import "goeist/sans.css"; // or "goeist/sans-static.css"; never both
import "goeist/mono.css"; // or "goeist/mono-static.css"; never both
```

```css
body {
  font-family: "Goeist", sans-serif;
}

code, pre {
  font-family: "Goeist Mono", monospace;
}
```

## License

This Font Software is licensed under the SIL Open Font License, Version 1.1. Goeist's rounded design and modifications are copyright 2026 Aniket-508; the original Geist copyright notices are included in `LICENSE.txt`.

## Disclaimer

Goeist is an independent project. It is not affiliated with, sponsored by or endorsed by Vercel, Inc., and is not an official Geist release. Vercel, the Vercel design, Next.js and related marks, designs and logos are trademarks or registered trademarks of Vercel, Inc. or its affiliates in the US and other countries.
