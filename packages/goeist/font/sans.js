import localFont from "next/font/local";

export const GoistSans = localFont({
  src: [
    {
      path: "../assets/goist-sans/Goist-Variable.woff2",
      weight: "100 900",
      style: "normal",
    },
    {
      path: "../assets/goist-sans/Goist-Italic-Variable.woff2",
      weight: "100 900",
      style: "italic",
    },
  ],
  variable: "--font-goist-sans",
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
