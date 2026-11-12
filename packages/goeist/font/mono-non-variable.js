import localFont from "next/font/local";

export const GoeistMonoNonVariable = localFont({
  src: [
    {
      path: "../assets/goeist-mono/GoeistMono-Thin.woff2",
      weight: "100",
      style: "normal",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-ThinItalic.woff2",
      weight: "100",
      style: "italic",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-ExtraLight.woff2",
      weight: "200",
      style: "normal",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-ExtraLightItalic.woff2",
      weight: "200",
      style: "italic",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-Light.woff2",
      weight: "300",
      style: "normal",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-LightItalic.woff2",
      weight: "300",
      style: "italic",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-Italic.woff2",
      weight: "400",
      style: "italic",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-MediumItalic.woff2",
      weight: "500",
      style: "italic",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-SemiBold.woff2",
      weight: "600",
      style: "normal",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-SemiBoldItalic.woff2",
      weight: "600",
      style: "italic",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-Bold.woff2",
      weight: "700",
      style: "normal",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-BoldItalic.woff2",
      weight: "700",
      style: "italic",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-ExtraBold.woff2",
      weight: "800",
      style: "normal",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-ExtraBoldItalic.woff2",
      weight: "800",
      style: "italic",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-Black.woff2",
      weight: "900",
      style: "normal",
    },
    {
      path: "../assets/goeist-mono/GoeistMono-BlackItalic.woff2",
      weight: "900",
      style: "italic",
    },
  ],
  variable: "--font-goeist-mono-non-variable",
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
