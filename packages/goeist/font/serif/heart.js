import localFont from "next/font/local";

export const GoeistSerifHeart = localFont({
  src: [
    {
      path: "../../assets/goeist-serif/GoeistSerif-Heart.woff2",
      weight: "400",
      style: "normal",
    },
  ],
  variable: "--font-goeist-serif-heart",
  fallback: [
    "ui-serif",
    "Georgia",
    "Cambria",
    "Times New Roman",
    "Times",
    "serif",
  ],
});
