# Goist

A rounded typeface by Aniket-508, based on [Vercel Geist Sans](https://github.com/vercel/geist-font). Nine weights (100–900) with genuine italics, as variable and static WOFF2.

```sh
npm install goist
```

## Next.js

`GoistSans` loads the upright and italic variable fonts through `next/font/local`.

```tsx
// app/layout.tsx
import { GoistSans } from "goist/font/sans";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={GoistSans.className}>
      <body>{children}</body>
    </html>
  );
}
```

Use the CSS variable instead of `className` to combine it with Tailwind or other fonts:

```tsx
<html lang="en" className={GoistSans.variable}>
```

```css
/* Tailwind v4 */
@theme {
  --font-sans: var(--font-goist-sans);
}
```

| Export | Entry point | CSS variable |
| --- | --- | --- |
| `GoistSans` | `goist/font/sans` | `--font-goist-sans` |
| `GoistSansNonVariable` | `goist/font/sans-non-variable` | `--font-goist-sans-non-variable` |

Prefer `GoistSans` (two files). `GoistSansNonVariable` ships 18 static files and is only needed for browsers without variable-font support.

## Plain CSS (Vite, Astro, Remix, …)

```js
import "goist/sans.css"; // variable, or "goist/sans-static.css" for static files; never both
```

```css
body {
  font-family: "Goist", sans-serif;
}
```

## License

SIL Open Font License 1.1. Goist is an independent derivative of Geist, not an official Vercel release.
