import localFont from "next/font/local";

export const GoistMono = localFont({
  src: [
    {
      path: "../assets/goist-mono/GoistMono-Variable.woff2",
      weight: "100 900",
      style: "normal",
    },
    {
      path: "../assets/goist-mono/GoistMono-Italic-Variable.woff2",
      weight: "100 900",
      style: "italic",
    },
  ],
  variable: "--font-goist-mono",
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
