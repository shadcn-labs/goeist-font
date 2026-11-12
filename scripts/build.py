#!/usr/bin/env python3
"""Build a Goist family from vendored, editable sources.

Each family (see families.py) owns sources/<Family>/, build/<Family>/ and
fonts/<Family>/. Compilation happens in a private staging directory. Existing
release files are replaced only after every expected export, hinting step and
WOFF2 succeeds; unrelated files in fonts/<Family>/ are never removed. Content
hashes, rather than package directory mtimes, govern incremental rebuilding.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import glyphsLib
from fontTools.misc.timeTools import epoch_diff
from fontTools.misc.roundTools import otRound
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont
from ttfautohint import TAError, ttfautohint
import yaml

from families import FAMILIES, Family
from rounding import add_automatic_ligatures

ROOT = Path(__file__).resolve().parent.parent
STYLES = (
    (100, "Thin"), (200, "ExtraLight"), (300, "Light"),
    (400, "Regular"), (500, "Medium"), (600, "SemiBold"),
    (700, "Bold"), (800, "ExtraBold"), (900, "Black"),
)
# A fixed release epoch, overridable explicitly for reproducible release builds.
DEFAULT_EPOCH = 1767225600


def styles():
    for weight, name in STYLES:
        yield weight, name, "normal"
        yield weight, "Italic" if name == "Regular" else name + "Italic", "italic"


def sources_dir(family: Family) -> Path:
    return ROOT / "sources" / family.key


def build_dir(family: Family) -> Path:
    return ROOT / "build" / family.key


def expected_paths(prefix: str, css: str | None = None) -> list[Path]:
    """Every release file for `prefix`; webfonts and stylesheets only with `css`."""
    paths = [Path(kind) / f"{prefix}-{name}.{kind}"
             for kind in ("ttf", "otf") for _, name, _ in styles()]
    variables = [f"{prefix}[wght]", f"{prefix}-Italic[wght]"]
    paths += [Path("variable") / f"{name}.ttf" for name in variables]
    if css:
        paths += [Path("webfonts") / f"{prefix}-{name}.woff2"
                  for _, name, _ in styles()]
        paths += [Path("webfonts") / f"{name}.woff2" for name in variables]
        paths += [Path("webfonts") / name for name in (f"{css}.css", f"{css}-static.css")]
    return paths


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_state(family: Family, epoch: int) -> dict:
    upstream = sources_dir(family) / "upstream"
    files = [sources_dir(family) / "config.yaml", ROOT / "requirements.txt", ROOT / "requirements.in",
             ROOT / "scripts/build.py", ROOT / "scripts/rounding.py", ROOT / "scripts/families.py",
             ROOT / "AUTHORS.txt"]
    for name in (family.upstream_key, family.upstream_key + "-Italic"):
        package = upstream / f"{name}.glyphspackage"
        if not package.is_dir():
            raise RuntimeError(f"Missing vendored source package: {package}")
        files.extend(path for path in package.rglob("*") if path.is_file())
    for path in files:
        if not path.is_file():
            raise RuntimeError(f"Missing build input: {path}")
    # Include every installed distribution: transitive compiler versions matter.
    versions = sorted((dist.metadata["Name"], dist.version)
                      for dist in importlib.metadata.distributions())
    return {
        "inputs": {str(path.relative_to(ROOT)): sha256(path)
                   for path in sorted(set(files))},
        "dependencies": versions,
        "python": sys.version.split()[0],
        "source_date_epoch": epoch,
    }


def cached(manifest: Path, state: dict, destination: Path, paths: list[Path],
           extras: list[Path] = ()) -> bool:
    if not manifest.is_file():
        return False
    try:
        previous = json.loads(manifest.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return False
    if previous.get("state") != json.loads(json.dumps(state)):
        return False
    outputs = [destination / path for path in paths] + list(extras)
    recorded = previous.get("outputs", {})
    return all(path.is_file() and recorded.get(str(path.relative_to(ROOT))) == sha256(path)
               for path in outputs)


def record(manifest: Path, state: dict, outputs: list[Path]):
    content = {"state": state,
               "outputs": {str(path.relative_to(ROOT)): sha256(path)
                           for path in sorted(outputs)}}
    temporary = manifest.with_suffix(".tmp")
    temporary.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
    temporary.replace(manifest)


def run(command: list[str], env: dict, cwd: Path = ROOT):
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, check=True, cwd=cwd, env=env)


def require_exports(directory: Path, prefix: str):
    for relative in expected_paths(prefix):
        path = directory / relative
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Compiler did not produce required export: {path}")
    for kind in ("ttf", "otf", "variable"):
        expected = {path.name for path in expected_paths(prefix)
                    if path.parts[0] == kind}
        actual = {path.name for path in (directory / kind).glob("*") if path.is_file()}
        if actual != expected:
            raise RuntimeError(f"Unexpected {kind} exports: expected {sorted(expected)}, got {sorted(actual)}")


def align_static_advances(font: TTFont, advances: dict[str, int]) -> list[str]:
    """Use the VF's interpolated advances in both SFNT and CFF metrics.

    Independently interpolated UFO components can round their advances one unit
    differently from HVAR. The variable font is the family-wide metric contract.
    """
    changed = []
    glyph_set = None
    for name, (width, bearing) in list(font["hmtx"].metrics.items()):
        expected = advances[name]
        if width == expected:
            continue
        if "CFF " in font:
            if glyph_set is None:
                glyph_set = font.getGlyphSet()
            charstrings = font["CFF "].cff.topDictIndex[0].CharStrings
            original = charstrings[name]
            private = original.private
            encoded_width = (None if expected == private.defaultWidthX
                             else expected - private.nominalWidthX)
            pen = T2CharStringPen(encoded_width, glyph_set, roundTolerance=0)
            glyph_set[name].draw(pen)
            charstrings[name] = pen.getCharString(private=private, globalSubrs=original.globalSubrs)
        font["hmtx"].metrics[name] = (expected, bearing)
        changed.append(name)
    font["hhea"].advanceWidthMax = max(width for width, _ in font["hmtx"].metrics.values())
    return changed


def normalize_static_advances(directory: Path, family: str):
    for style, variable_name in (("normal", family), ("italic", family + "-Italic")):
        with TTFont(directory / "variable" / f"{variable_name}[wght].ttf",
                    recalcTimestamp=False) as variable:
            for weight, name, instance_style in styles():
                if instance_style != style:
                    continue
                glyphs = variable.getGlyphSet(location={"wght": weight})
                advances = {glyph: otRound(glyphs[glyph].width) for glyph in variable.getGlyphOrder()}
                for kind in ("ttf", "otf"):
                    path = directory / kind / f"{family}-{name}.{kind}"
                    with TTFont(path, recalcTimestamp=False) as font:
                        changed = align_static_advances(font, advances)
                        if changed:
                            print(f"Aligning {path.name}: {', '.join(changed)}", flush=True)
                            font.save(path)


def compile_family(config: dict, source_paths: list[Path], family: str,
                   env: dict, jobs: int, workspace: Path) -> Path:
    config = dict(config)
    config["sources"] = [os.path.relpath(path, workspace) for path in source_paths]
    config["outputDir"] = "fonts"
    # Do not inherit directory overrides that would escape staging.
    for key in ("vfDir", "ttDir", "otDir", "woffDir"):
        config.pop(key, None)
    config_path = workspace / "config.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    run([sys.executable, "-m", "gftools.builder", "--no-ninja", "config.yaml"], env, workspace)
    run(["ninja", "-j", str(jobs), "-f", "build.ninja"], env, workspace)
    directory = workspace / "fonts"
    require_exports(directory, family)
    normalize_static_advances(directory, family)
    # gftools' default hint recipe permits failure; this direct API does not.
    for path in sorted((directory / "ttf").glob("*.ttf")):
        print(f"Autohinting {path.name}", flush=True)
        hinted = path.with_suffix(".hinted.ttf")
        ttfautohint(in_file=str(path), out_file=str(hinted), epoch=int(env["SOURCE_DATE_EPOCH"]))
        hinted.replace(path)
    # Fontmake preserves variable outline compatibility; ttfautohint cannot hint
    # variable fonts. VFs deliberately do not pass through the static autohinter.
    timestamp = int(env["SOURCE_DATE_EPOCH"]) - epoch_diff
    for path in sorted(directory.rglob("*")):
        if path.suffix not in (".ttf", ".otf"):
            continue
        with TTFont(path, recalcTimestamp=False) as font:
            font["head"].created = timestamp
            font["head"].modified = timestamp
            font.save(path, reorderTables=True)
    return directory


def face(family_name: str, filename: str, weight: str, style: str) -> str:
    return ("@font-face {\n"
            f"  font-family: '{family_name}';\n"
            f"  src: url('./{filename}') format('woff2');\n"
            f"  font-weight: {weight};\n"
            f"  font-style: {style};\n"
            "  font-display: swap;\n"
            "}\n")


def webfonts(directory: Path, family: Family):
    web = directory / "webfonts"
    web.mkdir(exist_ok=True)
    for kind in ("ttf", "variable"):
        for path in sorted((directory / kind).glob("*.ttf")):
            with TTFont(path, recalcTimestamp=False) as font:
                font.flavor = "woff2"
                font.save(web / path.with_suffix(".woff2").name)
    variable, static = f"{family.css}.css", f"{family.css}-static.css"
    (web / variable).write_text(
        f"/* Variable family: load this OR {static}, not both. */\n" +
        face(family.name, f"{family.key}[wght].woff2", "100 900", "normal") + "\n" +
        face(family.name, f"{family.key}-Italic[wght].woff2", "100 900", "italic"), encoding="utf-8")
    (web / static).write_text(
        f"/* Static family: load this OR {variable}, not both. */\n" +
        "\n".join(face(family.name, f"{family.key}-{name}.woff2", str(weight), style)
                  for weight, name, style in styles()), encoding="utf-8")


def publish(staged: Path, destination: Path, paths: list[Path]):
    # Validate the entire staged set before replacing any published file.
    for relative in paths:
        path = staged / relative
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing staged artifact: {path}")
    for relative in paths:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".tmp")
        shutil.copyfile(staged / relative, temporary)
        temporary.replace(target)


def baseline(family: Family, config: dict, state: dict, env: dict, jobs: int, force: bool):
    build = build_dir(family)
    destination = build / "baseline"
    manifest = build / "baseline-manifest.json"
    paths = expected_paths(family.upstream_key)
    if not force and cached(manifest, state, destination, paths):
        print(f"Unrounded {family.upstream_name} source baseline is current.")
        return
    staging = build / "baseline-sources"
    staging.mkdir(parents=True, exist_ok=True)
    sources = []
    for basename in (family.upstream_key, family.upstream_key + "-Italic"):
        target = staging / f"{basename}.glyphs"
        # Only serialization, plus the family's declared automatic-feature
        # recreation, keeps compiler side effects out of the pinned upstream
        # packages; no rounding or metadata rewriting is applied.
        font = glyphsLib.load(str(sources_dir(family) / "upstream" / f"{basename}.glyphspackage"))
        if family.automatic_ligatures:
            add_automatic_ligatures(font)
        font.save(str(target))
        sources.append(target)
    baseline_config = dict(config)
    baseline_config["familyName"] = family.upstream_name
    baseline_config.pop("version", None)
    baseline_config["stat"] = {name.replace(family.key, family.upstream_key): axes
                               for name, axes in config["stat"].items()}
    with tempfile.TemporaryDirectory(prefix="baseline-", dir=build) as temporary:
        staged = compile_family(baseline_config, sources, family.upstream_key, env, jobs, Path(temporary))
        publish(staged, destination, paths)
    record(manifest, state, [destination / path for path in paths])


def rounded(family: Family, config: dict, state: dict, env: dict, jobs: int, force: bool):
    build = build_dir(family)
    destination = ROOT / "fonts" / family.key
    manifest = build / "build-manifest.json"
    paths = expected_paths(family.key, family.css)
    staging = build / "sources"
    sources = [staging / f"{family.key}.glyphs", staging / f"{family.key}-Italic.glyphs"]
    reports = [build / "rounding-upright.json", build / "rounding-italic.json"]
    extras = sources + reports
    if not force and cached(manifest, state, destination, paths, extras):
        print(f"{family.name} exports are current.")
        return
    staging.mkdir(parents=True, exist_ok=True)
    for basename, target, report in zip((family.upstream_key, family.upstream_key + "-Italic"),
                                        sources, reports):
        run([sys.executable, "scripts/rounding.py", "--family", family.key, "--source",
             str(sources_dir(family) / "upstream" / f"{basename}.glyphspackage"), "--output", str(target),
             "--report", str(report)], env)
    for path in extras:
        if not path.is_file():
            raise RuntimeError(f"Missing source generation artifact: {path}")
    for source in sources:
        font = glyphsLib.load(str(source))
        if font.familyName != family.name or (font.versionMajor, font.versionMinor) != (1, 0):
            raise RuntimeError(f"Generated source must declare family {family.name} and version 1.000: {source}")
    with tempfile.TemporaryDirectory(prefix="rounded-", dir=build) as temporary:
        staged = compile_family(config, sources, family.key, env, jobs, Path(temporary))
        webfonts(staged, family)
        publish(staged, destination, paths)
    record(manifest, state, [destination / path for path in paths] + extras)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", default="Goist", choices=sorted(FAMILIES))
    parser.add_argument("--baseline", action="store_true", help="Build only the unrounded source baseline")
    parser.add_argument("--force", action="store_true", help="Rebuild even when content hashes match")
    parser.add_argument("--jobs", type=int, default=min(os.cpu_count() or 1, 4))
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    env = dict(os.environ)
    env.setdefault("SOURCE_DATE_EPOCH", str(DEFAULT_EPOCH))
    env["PYTHONHASHSEED"] = "0"
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    epoch = int(env["SOURCE_DATE_EPOCH"])
    if epoch < 0:
        raise RuntimeError("SOURCE_DATE_EPOCH must be nonnegative")
    family = FAMILIES[args.family]
    build_dir(family).mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load((sources_dir(family) / "config.yaml").read_text(encoding="utf-8"))
    if config.get("familyName") != family.name:
        raise RuntimeError(f"{sources_dir(family) / 'config.yaml'} must declare familyName {family.name}")
    state = input_state(family, epoch)
    if args.baseline:
        baseline(family, config, state, env, args.jobs, args.force)
    else:
        rounded(family, config, state, env, args.jobs, args.force)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, TAError, subprocess.CalledProcessError) as error:
        print(f"Goist build failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
