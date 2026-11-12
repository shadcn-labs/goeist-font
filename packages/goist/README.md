# Goist

Goist is a font family created by [Aniket-508](https://github.com/Aniket-508), developed under [Shadcn Labs](https://shadcn-labs.com/font). It is a rounded derivative of [Geist Sans](https://github.com/vercel/geist-font), created by Vercel in collaboration with Basement Studio. Nine weights (100–900) with genuine italics, as variable and static WOFF2.

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

This Font Software is licensed under the SIL Open Font License, Version 1.1. Goist's rounded design and modifications are copyright 2026 Aniket-508; the original Geist copyright notices are included in `LICENSE.txt`.

## Disclaimer

Goist is an independent project. It is not affiliated with, sponsored by or endorsed by Vercel, Inc., and is not an official Geist release. Vercel, the Vercel design, Next.js and related marks, designs and logos are trademarks or registered trademarks of Vercel, Inc. or its affiliates in the US and other countries.
