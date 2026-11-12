// Copies the committed release webfonts into this package before packing.
// fonts/<Family>/webfonts/ in the repository root is the single source of truth.
import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const pkg = join(dirname(fileURLToPath(import.meta.url)), "..");
const repo = join(pkg, "..", "..");

// `css` is the stylesheet stem written by scripts/build.py; `slug` names the package directory.
const FAMILIES = [
  { family: "Goist", css: "goist", slug: "goist-sans" },
  { family: "GoistMono", css: "goist-mono", slug: "goist-mono" },
];

// Bracketed axis names are renamed so bundlers never see `[...]` in asset paths.
const variableName = (file) => file.replace(/\[wght\]\.woff2$/, "-Variable.woff2");

for (const { family, css: stem, slug } of FAMILIES) {
  const source = join(repo, "fonts", family, "webfonts");
  if (!existsSync(source)) {
    console.error(`Missing ${source}. Run \`make build\` in the repository root first.`);
    process.exit(1);
  }
  const target = join(pkg, "assets", slug);
  rmSync(target, { recursive: true, force: true });
  mkdirSync(target, { recursive: true });

  const files = readdirSync(source);
  let fonts = 0;
  for (const file of files.filter((name) => name.endsWith(".woff2"))) {
    copyFileSync(join(source, file), join(target, variableName(file)));
    fonts += 1;
  }
  const cssName = (file) => file.replace(new RegExp(`^${stem}(-static)?\\.css$`), `${slug}$1.css`);
  for (const file of files.filter((name) => name.endsWith(".css"))) {
    const css = readFileSync(join(source, file), "utf8")
      .replace(/[\w-]+\[wght\]\.woff2/g, variableName)
      .replace(new RegExp(`\\b${stem}(-static)?\\.css\\b`, "g"), (name) => cssName(name));
    writeFileSync(join(target, cssName(file)), css);
  }
  console.log(`Staged ${fonts} ${family} webfonts → assets/${slug}/`);
}

copyFileSync(join(repo, "OFL.txt"), join(pkg, "LICENSE.txt"));
