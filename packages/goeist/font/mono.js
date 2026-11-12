import localFont from "next/font/local";

export const GoeistMono = localFont({
  src: [
    {
      path: "../assets/goeist-mono/GoeistMono-Variable.woff2",
      weight: "100 900",
      style: "normal",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-Italic-Variable.woff2",
      weight: "100 900",
      style: "italic",
    },
  ],
  variable: "--font-goeist-mono",
  adjustFontFallback: false,
  fallback: [
    "ui-monospace",
    "SFMono-Regular",
    "Roboto Mono",
    "Menlo",
    "Monaco",
    "Liberation Mono",
    "DejaVu Sans Mono",
    "Courier New",
    "monospace",
  ],
});
