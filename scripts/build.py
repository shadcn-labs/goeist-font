#!/usr/bin/env python3
"""Build a Goeist family from vendored, editable sources.

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

from families import FAMILIES, FONT_VERSION, FONT_VERSION_STRING, Family
from rounding import add_automatic_ligatures
import serif

ROOT = Path(__file__).resolve().parent.parent
# A fixed release epoch, overridable explicitly for reproducible release builds.
DEFAULT_EPOCH = 1767225600


def sources_dir(family: Family) -> Path:
    return ROOT / "sources" / family.key


def build_dir(family: Family) -> Path:
    return ROOT / "build" / family.key


def expected_paths(family: Family, prefix: str, css: str | None = None) -> list[Path]:
    """Every release file for `prefix`; webfonts and stylesheets only with `css`."""
    paths = [Path(kind) / f"{prefix}-{style.name}.{kind}"
             for kind in ("ttf", "otf") for style in family.styles]
    variables = [family.variable_stem(prefix, slope) for slope in family.slopes]
    paths += [Path("variable") / f"{name}.ttf" for name in variables]
    if css:
        paths += [Path("webfonts") / f"{prefix}-{style.name}.woff2" for style in family.styles]
        paths += [Path("webfonts") / f"{name}.woff2" for name in variables]
        paths += [Path("webfonts") / name for name in (f"{css}.css", f"{css}-static.css")]
        paths.append(Path("FONTLOG.txt"))
    return paths


def fontlog(family: Family, reports: list[Path], guard_report: Path | None,
            static_reports: list[Path] = ()) -> str:
    """FONTLOG.txt: the base, its licence, and every modification with its numbers."""
    upstream = sources_dir(family) / "upstream"
    manifest = json.loads((upstream / "manifest.json").read_text(encoding="utf-8"))
    info = glyphsLib.load(str(upstream / f"{family.upstream_packages[0]}.glyphspackage"))
    profile = family.profile
    tag, low, default, high = family.axis
    styles = ", ".join(style.name for style in family.styles)
    lines = [
        f"{family.name} {FONT_VERSION_STRING}: FONTLOG", "",
        f"{family.name} is a rounded derivative of {family.upstream_label}. Every outline comes from the",
        "upstream source; advances, kerning, OpenType features, character map and vertical metrics",
        "are kept, and only corners, serif ends and stroke endings change.", "",
        "Base",
        f"  {family.upstream_name}, {manifest['repository']} {manifest['tag']} ({manifest['commit']})",
        f"  Source version {manifest['source_version']}. Licence: SIL Open Font License 1.1,"
        " no Reserved Font Name.",
        f"  Original design: {info.designer}.",
        f"  Variable axis: {tag} {low}-{high}, default {default}; "
        f"{' and '.join(family.slopes)} variable fonts. Static styles: {styles}.", "",
        "Modifications",
        f"  Rounding profile '{profile.name}': squared ends and outer corners {profile.terminal} stem,"
        f" acute corners {profile.acute} stem,",
        f"  {'circular arcs' if profile.circular else 'arcs trimmed per edge'}"
        + (f", straight convex contours as stadiums up to {profile.stadium} stem" if profile.stadium else "")
        + (f", radius at most {profile.local} x the stroke across the corner" if profile.local else "")
        + ".",
        "  Concave joins, counters and hidden overlap corners keep their drawn construction.",
    ]
    if family.exact_geometry:
        lines.append(f"  U+{family.exact_geometry.start:04X}-U+{family.exact_geometry.stop - 1:04X}"
                     " keep their exact upstream outlines.")
    if family.automatic_ligatures:
        lines.append("  The liga feature Glyphs.app derives from `a_b.liga` glyph names is recreated.")
    for slope, path in zip(family.slopes, reports):
        report = json.loads(path.read_text(encoding="utf-8"))
        counts = report["counts"]
        stems = ", ".join(f"{m['name']} {m['stem']:.1f}" for m in report["masters"].values())
        reductions = sum(e["reason"] == "local_radius_reduction" for e in report["exceptions"])
        lines += ["", f"  {slope.title()}: measured stems {stems} units.",
                  f"    {counts['rounded_corners']} corners rounded over {counts['design_layers']} design layers,"
                  f" {reductions} with a locally reduced radius,"
                  f" {counts.get('compatible_support_cubics', 0)} zero-length support curves for interpolation."]
        joins = counts.get("interpolation_join_ratios", 0)
        if joins:
            lines.append(f"    {joins} fillet joins on turning curves given one handle ratio in every master;"
                         f" {counts.get('interpolation_join_ratios_kept', 0)} kept circular handles, so the variable"
                         " font can still bend at those joins between masters.")
        shape = report.get("soft_serif")
        if shape:
            lines += [f"    {shape['softened']} serif tips thickened to {shape['tip']} units and closed with a"
                      f" half-round of {shape['tip'] / 2:g} at their original reach.",
                      f"    {shape.get('terminal_capped', 0)} cut terminals and {shape.get('spike_capped', 0)}"
                      f" spikes capped with the inscribed {shape['cap']}-unit circle.",
                      f"    {shape['overlaps_removed']} layers had open corners and overlaps removed before"
                      " rounding."]
    for slope, path in zip(family.slopes, static_reports):
        counts = json.loads(path.read_text(encoding="utf-8"))["counts"]
        lines.append(f"  {slope.title()} static instances: every named weight rounded from its own interpolated"
                     f" outline ({counts['intermediate_layers']} intermediate layers), not interpolated"
                     " between rounded masters.")
    if guard_report:
        guard = json.loads(guard_report.read_text(encoding="utf-8"))
        lines += ["", f"  Collision guard (minimum ink gap {guard['min_gap']} units): pairs the rounded serif"
                      " tips brought closer than",
                  "  the upstream fonts are opened by one added kern lookup, never closed:"]
        for name, pairs in guard["fonts"].items():
            widest = max((units for _, _, units in pairs), default=0)
            lines.append(f"    {name}: {len(pairs)} pairs, widest opening {widest} units")
    lines += ["", "Acknowledgements",
              f"  {family.upstream_label} by {info.designer}, published by Vercel under the SIL Open Font"
              " License 1.1.",
              f"  {family.name} is independent and not affiliated with or endorsed by Vercel, Inc.", ""]
    return "\n".join(lines)


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
    files += [ROOT / "scripts/collisions.py"]
    if family.element_shapes:
        files += [ROOT / "scripts/serif.py", *sorted((upstream / "scripts").glob("*.py")),
                  *sorted((upstream / "reference").glob("*.ttf"))]
    files.append(upstream / "manifest.json")
    for name in family.upstream_packages:
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


def require_exports(directory: Path, family: Family, prefix: str):
    for relative in expected_paths(family, prefix):
        path = directory / relative
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Compiler did not produce required export: {path}")
    for kind in ("ttf", "otf", "variable"):
        expected = {path.name for path in expected_paths(family, prefix)
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


def normalize_static_advances(directory: Path, family: Family, prefix: str):
    for slope in family.slopes:
        with TTFont(directory / "variable" / f"{family.variable_stem(prefix, slope)}.ttf",
                    recalcTimestamp=False) as variable:
            for style in family.styles:
                if style.slope != slope:
                    continue
                glyphs = variable.getGlyphSet(location=dict(style.location))
                advances = {glyph: otRound(glyphs[glyph].width) for glyph in variable.getGlyphOrder()}
                for kind in ("ttf", "otf"):
                    path = directory / kind / f"{prefix}-{style.name}.{kind}"
                    with TTFont(path, recalcTimestamp=False) as font:
                        changed = align_static_advances(font, advances)
                        if changed:
                            print(f"Aligning {path.name}: {', '.join(changed)}", flush=True)
                            font.save(path)


def _gftools(config: dict, source_paths: list[Path], env: dict, jobs: int, workspace: Path, **overrides) -> Path:
    workspace.mkdir(parents=True, exist_ok=True)
    config = dict(config, **overrides)
    config["sources"] = [os.path.relpath(path, workspace) for path in source_paths]
    config["outputDir"] = "fonts"
    # Do not inherit directory overrides that would escape staging.
    for key in ("vfDir", "ttDir", "otDir", "woffDir"):
        config.pop(key, None)
    (workspace / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    run([sys.executable, "-m", "gftools.builder", "--no-ninja", "config.yaml"], env, workspace)
    run(["ninja", "-j", str(jobs), "-f", "build.ninja"], env, workspace)
    return workspace / "fonts"


def compile_family(config: dict, source_paths: list[Path], family: Family, prefix: str,
                   family_name: str, env: dict, jobs: int, workspace: Path,
                   guard_report: Path | None = None, static_sources: list[Path] | None = None) -> Path:
    """Compile one family into workspace/fonts.

    With `static_sources`, the variable fonts come from `source_paths` and the
    static instances from `static_sources` (the same design with every named
    weight rounded from its own outline).
    """
    if family.element_shapes:
        # One master, so every static is the master itself with that style's
        # glyph renames: no interpolated advances to align.
        (source,) = source_paths
        directory = serif.compile_fonts(source, family, prefix, family_name, env, workspace, guard_report)
        require_exports(directory, family, prefix)
    elif static_sources:
        variable = _gftools(config, source_paths, env, jobs, workspace / "variable", buildStatic=False)
        static = _gftools(config, static_sources, env, jobs, workspace / "static", buildVariable=False)
        directory = workspace / "fonts"
        shutil.copytree(variable / "variable", directory / "variable")
        for kind in ("ttf", "otf"):
            shutil.copytree(static / kind, directory / kind)
        require_exports(directory, family, prefix)
        normalize_static_advances(directory, family, prefix)
    else:
        directory = _gftools(config, source_paths, env, jobs, workspace)
        require_exports(directory, family, prefix)
        normalize_static_advances(directory, family, prefix)
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
    _, low, _, high = family.axis
    if family.element_shapes:
        # ELSH swaps glyphs rather than weights: one variable face picked with
        # font-variation-settings, and one static family per shape, as Geist Serif ships.
        variable_faces = [face(family.name, f"{family.variable_stem(family.key)}.woff2", "400", "normal")]
        static_faces = [face(family.name if style.name == "Regular" else f"{family.name} {style.name}",
                             f"{family.key}-{style.name}.woff2", "400", "normal") for style in family.styles]
    else:
        variable_faces = [face(family.name, f"{family.variable_stem(family.key, slope)}.woff2",
                               f"{low} {high}", "normal" if slope == "upright" else "italic")
                          for slope in family.slopes]
        static_faces = [face(family.name, f"{family.key}-{style.name}.woff2", str(style.weight),
                             "italic" if style.italic else "normal") for style in family.styles]
    (web / variable).write_text(
        f"/* Variable family: load this OR {static}, not both. */\n" + "\n".join(variable_faces),
        encoding="utf-8")
    (web / static).write_text(
        f"/* Static family: load this OR {variable}, not both. */\n" + "\n".join(static_faces),
        encoding="utf-8")


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
    paths = expected_paths(family, family.upstream_key)
    if not force and cached(manifest, state, destination, paths):
        print(f"Unrounded {family.upstream_name} source baseline is current.")
        return
    staging = build / "baseline-sources"
    staging.mkdir(parents=True, exist_ok=True)
    sources = []
    for basename in family.upstream_packages:
        target = staging / f"{basename}.glyphs"
        package = sources_dir(family) / "upstream" / f"{basename}.glyphspackage"
        if family.element_shapes:
            # Corner components must be placed before any compiler sees them.
            run([sys.executable, "scripts/serif.py", "--family", family.key, "--baseline",
                 "--source", str(package), "--output", str(target)], env)
        else:
            # Only serialization, plus the family's declared automatic-feature
            # recreation, keeps compiler side effects out of the pinned upstream
            # packages; no rounding or metadata rewriting is applied.
            font = glyphsLib.load(str(package))
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
        staged = compile_family(baseline_config, sources, family, family.upstream_key,
                                family.upstream_name, env, jobs, Path(temporary))
        publish(staged, destination, paths)
    record(manifest, state, [destination / path for path in paths])


def rounded(family: Family, config: dict, state: dict, env: dict, jobs: int, force: bool):
    build = build_dir(family)
    destination = ROOT / "fonts" / family.key
    manifest = build / "build-manifest.json"
    paths = expected_paths(family, family.key, family.css)
    staging = build / "sources"
    sources = [staging / f"{basename.replace(family.upstream_key, family.key, 1)}.glyphs"
               for basename in family.upstream_packages]
    reports = [build / f"rounding-{slope}.json" for slope in family.slopes]
    # Weight families get a second source per slope for their static instances,
    # with every named weight rounded from its own outline (same file stem).
    weighted = not family.element_shapes
    static_sources = [staging / "statics" / source.name for source in sources] if weighted else []
    static_reports = [build / f"rounding-{slope}-statics.json" for slope in family.slopes] if weighted else []
    extras = sources + reports + static_sources + static_reports
    # Written while compiling, after the sources: cached and recorded with them.
    guard_report = build / "collision-guard.json" if family.soft_serif else None
    outputs = extras + ([guard_report] if guard_report else [])
    if not force and cached(manifest, state, destination, paths, outputs):
        print(f"{family.name} exports are current.")
        return
    staging.mkdir(parents=True, exist_ok=True)
    script = "scripts/serif.py" if family.element_shapes else "scripts/rounding.py"
    jobs_list = [(basename, target, report, []) for basename, target, report
                 in zip(family.upstream_packages, sources, reports)]
    jobs_list += [(basename, target, report, ["--intermediate-weights"]) for basename, target, report
                  in zip(family.upstream_packages, static_sources, static_reports)]
    for basename, target, report, flags in jobs_list:
        target.parent.mkdir(parents=True, exist_ok=True)
        run([sys.executable, script, "--family", family.key, "--source",
             str(sources_dir(family) / "upstream" / f"{basename}.glyphspackage"), "--output", str(target),
             "--report", str(report), *flags], env)
    for path in extras:
        if not path.is_file():
            raise RuntimeError(f"Missing source generation artifact: {path}")
    for source in sources + static_sources:
        font = glyphsLib.load(str(source))
        if font.familyName != family.name or (font.versionMajor, font.versionMinor) != FONT_VERSION:
            raise RuntimeError(f"Generated source must declare family {family.name} "
                               f"and version {FONT_VERSION_STRING}: {source}")
    with tempfile.TemporaryDirectory(prefix="rounded-", dir=build) as temporary:
        staged = compile_family(config, sources, family, family.key, family.name, env, jobs, Path(temporary),
                                guard_report, static_sources)
        webfonts(staged, family)
        (staged / "FONTLOG.txt").write_text(fontlog(family, reports, guard_report, static_reports),
                                            encoding="utf-8")
        publish(staged, destination, paths)
    record(manifest, state, [destination / path for path in paths] + outputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", default="Goeist", choices=sorted(FAMILIES))
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
    if config.get("familyName") != family.name or str(config.get("version")) != FONT_VERSION_STRING:
        raise RuntimeError(f"{sources_dir(family) / 'config.yaml'} must declare familyName {family.name} "
                           f"and version '{FONT_VERSION_STRING}'")
    state = input_state(family, epoch)
    if args.baseline:
        baseline(family, config, state, env, args.jobs, args.force)
    else:
        rounded(family, config, state, env, args.jobs, args.force)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, TAError, subprocess.CalledProcessError) as error:
        print(f"Goeist build failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
