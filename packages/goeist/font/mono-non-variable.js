import localFont from "next/font/local";

export const GoistMonoNonVariable = localFont({
  src: [
    {
      path: "../assets/goist-mono/GoistMono-Thin.woff2",
      weight: "100",
      style: "normal",
    },
    {
      path: "../assets/goist-mono/GoistMono-ThinItalic.woff2",
      weight: "100",
      style: "italic",
    },
    {
      path: "../assets/goist-mono/GoistMono-ExtraLight.woff2",
      weight: "200",
      style: "normal",
    },
    {
      path: "../assets/goist-mono/GoistMono-ExtraLightItalic.woff2",
      weight: "200",
      style: "italic",
    },
    {
      path: "../assets/goist-mono/GoistMono-Light.woff2",
      weight: "300",
      style: "normal",
    },
    {
      path: "../assets/goist-mono/GoistMono-LightItalic.woff2",
      weight: "300",
      style: "italic",
    },
    {
      path: "../assets/goist-mono/GoistMono-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../assets/goist-mono/GoistMono-Italic.woff2",
      weight: "400",
      style: "italic",
    },
    {
      path: "../assets/goist-mono/GoistMono-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../assets/goist-mono/GoistMono-MediumItalic.woff2",
      weight: "500",
      style: "italic",
    },
    {
      path: "../assets/goist-mono/GoistMono-SemiBold.woff2",
      weight: "600",
      style: "normal",
    },
    {
      path: "../assets/goist-mono/GoistMono-SemiBoldItalic.woff2",
      weight: "600",
      style: "italic",
    },
    {
      path: "../assets/goist-mono/GoistMono-Bold.woff2",
      weight: "700",
      style: "normal",
    },
    {
      path: "../assets/goist-mono/GoistMono-BoldItalic.woff2",
      weight: "700",
      style: "italic",
    },
    {
      path: "../assets/goist-mono/GoistMono-ExtraBold.woff2",
      weight: "800",
      style: "normal",
    },
    {
      path: "../assets/goist-mono/GoistMono-ExtraBoldItalic.woff2",
      weight: "800",
      style: "italic",
    },
    {
      path: "../assets/goist-mono/GoistMono-Black.woff2",
      weight: "900",
      style: "normal",
    },
    {
      path: "../assets/goist-mono/GoistMono-BlackItalic.woff2",
      weight: "900",
      style: "italic",
    },
  ],
  variable: "--font-goist-mono-non-variable",
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
