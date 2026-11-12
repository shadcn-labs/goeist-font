import localFont from "next/font/local";

export const GoeistSans = localFont({
  src: [
    {
      path: "../assets/goeist-sans/Goeist-Variable.woff2",
      weight: "100 900",
      style: "normal",
    },
    {
      path: "../assets/goeist-sans/Goeist-Italic-Variable.woff2",
      weight: "100 900",
      style: "italic",
    },
  ],
  variable: "--font-goeist-sans",
  fallback: [
    "ui-sans-serif",
    "system-ui",
    "-apple-system",
    "BlinkMacSystemFont",
    "Segoe UI",
    "Roboto",
    "sans-serif",
  ],
});
