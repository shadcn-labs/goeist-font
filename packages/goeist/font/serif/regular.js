import localFont from "next/font/local";

export const GoeistSerifRegular = localFont({
  src: [
    {
      path: "../../assets/goeist-serif/GoeistSerif-Regular.woff2",
      weight: "400",
      style: "normal",
    },
  ],
  variable: "--font-goeist-serif-regular",
  fallback: [
    "ui-serif",
    "Georgia",
    "Cambria",
    "Times New Roman",
    "Times",
    "serif",
  ],
});
