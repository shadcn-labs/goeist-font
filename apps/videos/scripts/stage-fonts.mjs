// Copies the committed variable fonts into public/ so Remotion can serve them.
// fonts/<Family>/variable/ in the repository root is the single source of truth.
import { copyFileSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const app = join(dirname(fileURLToPath(import.meta.url)), "..");
const repo = join(app, "..", "..");
const target = join(app, "public", "fonts");

const FONTS = [
  ["Goeist", "Goeist[wght].ttf"],
  ["Goeist", "Goeist-Italic[wght].ttf"],
  ["GoeistMono", "GoeistMono[wght].ttf"],
];

rmSync(target, { recursive: true, force: true });
mkdirSync(target, { recursive: true });

for (const [family, file] of FONTS) {
  const source = join(repo, "fonts", family, "variable", file);
  if (!existsSync(source)) {
    console.error(`Missing ${source}. Run \`make build\` in the repository root first.`);
    process.exit(1);
  }
  // Bracketed axis names are renamed so the bundler never sees `[...]` in asset paths.
  copyFileSync(source, join(target, file.replace("[wght]", "-Variable")));
}

console.log(`Staged ${FONTS.length} variable fonts → public/fonts/`);
