import localFont from "next/font/local";

// Every Element Shape in one file: pick the dots with
// `font-variation-settings: "ELSH" 0 | 25 | 50 | 100` (round, square, triangle, heart).
export const GoeistSerif = localFont({
  src: [
    {
      path: "../assets/goeist-serif/GoeistSerif-Variable.woff2",
      weight: "400",
      style: "normal",
    },
  ],
  variable: "--font-goeist-serif",
  fallback: [
    "ui-serif",
    "Georgia",
    "Cambria",
    "Times New Roman",
    "Times",
    "serif",
  ],
});
