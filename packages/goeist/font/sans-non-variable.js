import localFont from "next/font/local";

export const GoeistSansNonVariable = localFont({
  src: [
    {
      path: "../assets/goeist-sans/Goeist-Thin.woff2",
      weight: "100",
      style: "normal",
    },
    {
      path: "../assets/goeist-sans/Goeist-ThinItalic.woff2",
      weight: "100",
      style: "italic",
    },
    {
      path: "../assets/goeist-sans/Goeist-ExtraLight.woff2",
      weight: "200",
      style: "normal",
    },
    {
      path: "../assets/goeist-sans/Goeist-ExtraLightItalic.woff2",
      weight: "200",
      style: "italic",
    },
    {
      path: "../assets/goeist-sans/Goeist-Light.woff2",
      weight: "300",
      style: "normal",
    },
    {
      path: "../assets/goeist-sans/Goeist-LightItalic.woff2",
      weight: "300",
      style: "italic",
    },
    {
      path: "../assets/goeist-sans/Goeist-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../assets/goeist-sans/Goeist-Italic.woff2",
      weight: "400",
      style: "italic",
    },
    {
      path: "../assets/goeist-sans/Goeist-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../assets/goeist-sans/Goeist-MediumItalic.woff2",
      weight: "500",
      style: "italic",
    },
    {
      path: "../assets/goeist-sans/Goeist-SemiBold.woff2",
      weight: "600",
      style: "normal",
    },
    {
      path: "../assets/goeist-sans/Goeist-SemiBoldItalic.woff2",
      weight: "600",
      style: "italic",
    },
    {
      path: "../assets/goeist-sans/Goeist-Bold.woff2",
      weight: "700",
      style: "normal",
    },
    {
      path: "../assets/goeist-sans/Goeist-BoldItalic.woff2",
      weight: "700",
      style: "italic",
    },
    {
      path: "../assets/goeist-sans/Goeist-ExtraBold.woff2",
      weight: "800",
      style: "normal",
    },
    {
      path: "../assets/goeist-sans/Goeist-ExtraBoldItalic.woff2",
      weight: "800",
      style: "italic",
    },
    {
      path: "../assets/goeist-sans/Goeist-Black.woff2",
      weight: "900",
      style: "normal",
    },
    {
      path: "../assets/goeist-sans/Goeist-BlackItalic.woff2",
      weight: "900",
      style: "italic",
    },
  ],
  variable: "--font-goeist-sans-non-variable",
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
