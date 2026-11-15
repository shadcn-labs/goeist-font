import localFont from "next/font/local";

export const GoeistSerifSquare = localFont({
  src: [
    {
      path: "../../assets/goeist-serif/GoeistSerif-Square.woff2",
      weight: "400",
      style: "normal",
    },
  ],
  variable: "--font-goeist-serif-square",
  fallback: [
    "ui-serif",
    "Georgia",
    "Cambria",
    "Times New Roman",
    "Times",
    "serif",
  ],
});
