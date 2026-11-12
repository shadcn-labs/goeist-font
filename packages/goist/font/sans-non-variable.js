import localFont from "next/font/local";

export const GoistSansNonVariable = localFont({
  src: [
    {
      path: "../assets/goist-sans/Goist-Thin.woff2",
      weight: "100",
      style: "normal",
    },
    {
      path: "../assets/goist-sans/Goist-ThinItalic.woff2",
      weight: "100",
      style: "italic",
    },
    {
      path: "../assets/goist-sans/Goist-ExtraLight.woff2",
      weight: "200",
      style: "normal",
    },
    {
      path: "../assets/goist-sans/Goist-ExtraLightItalic.woff2",
      weight: "200",
      style: "italic",
    },
    {
      path: "../assets/goist-sans/Goist-Light.woff2",
      weight: "300",
      style: "normal",
    },
    {
      path: "../assets/goist-sans/Goist-LightItalic.woff2",
      weight: "300",
      style: "italic",
    },
    {
      path: "../assets/goist-sans/Goist-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../assets/goist-sans/Goist-Italic.woff2",
      weight: "400",
      style: "italic",
    },
    {
      path: "../assets/goist-sans/Goist-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../assets/goist-sans/Goist-MediumItalic.woff2",
      weight: "500",
      style: "italic",
    },
    {
      path: "../assets/goist-sans/Goist-SemiBold.woff2",
      weight: "600",
      style: "normal",
    },
    {
      path: "../assets/goist-sans/Goist-SemiBoldItalic.woff2",
      weight: "600",
      style: "italic",
    },
    {
      path: "../assets/goist-sans/Goist-Bold.woff2",
      weight: "700",
      style: "normal",
    },
    {
      path: "../assets/goist-sans/Goist-BoldItalic.woff2",
      weight: "700",
      style: "italic",
    },
    {
      path: "../assets/goist-sans/Goist-ExtraBold.woff2",
      weight: "800",
      style: "normal",
    },
    {
      path: "../assets/goist-sans/Goist-ExtraBoldItalic.woff2",
      weight: "800",
      style: "italic",
    },
    {
      path: "../assets/goist-sans/Goist-Black.woff2",
      weight: "900",
      style: "normal",
    },
    {
      path: "../assets/goist-sans/Goist-BlackItalic.woff2",
      weight: "900",
      style: "italic",
    },
  ],
  variable: "--font-goist-sans-non-variable",
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
