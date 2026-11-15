import localFont from "next/font/local";

export const GoeistSerifTriangle = localFont({
  src: [
    {
      path: "../../assets/goeist-serif/GoeistSerif-Triangle.woff2",
      weight: "400",
      style: "normal",
    },
  ],
  variable: "--font-goeist-serif-triangle",
  fallback: [
    "ui-serif",
    "Georgia",
    "Cambria",
    "Times New Roman",
    "Times",
    "serif",
  ],
});
