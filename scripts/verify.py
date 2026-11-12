#!/usr/bin/env python3
"""Audit a Goeist family build, source/release drift, shaping, and delivery formats.

Verify the deliverables against the unrounded source build (`make baseline`):
  python scripts/verify.py --family GoeistMono
Paths default to fonts/<family>, sources/<family>/upstream/reference,
build/<family>/baseline and out/<family>/verification.json.

A release binary is NOT an interchangeable baseline for the newer editable source. Exact
source/release differences can be acknowledged with --drift-allowlist JSON:
{"approved": ["drift:upright:400:metrics", ...]}. All drift remains in the report.
No approval can waive a rounded-build regression against its source baseline.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import uharfbuzz as hb
from fontTools import agl
from fontTools.misc.xmlWriter import XMLWriter
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from families import FAMILIES, FONT_VERSION_STRING
from rounding import MANUFACTURER, VENDOR_ID

SCHEMA = 1
WEIGHTS = tuple(range(100, 901, 100))
INTERMEDIATES = (250, 550, 850)
SETS = {f"ss{i:02}" for i in range(1, 12)}
SAMPLES = {
    "latin": "Hamburgefontsiv AVATAR office affine ffi ffl fi fl rt tt 0123456789",
    "fractions": "1/2 3/4 11/16 123/456",
    "marks-composed": "ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝàáâãäåçéñöüÿ ĀĂĄĆČĐĖĘŁŃŘŠŤŮŽ",
    "marks-decomposed": "A\u0300A\u0301A\u0302A\u0308A\u030a a\u0301e\u0308o\u030bu\u0308 n\u0303 c\u0327 a\u0301\u0323",
    "cyrillic": "БГДЛПТбвгдпт ЃѓЌќ ЂђЉљЊњЋћЏџ",
    "symbols": "$¢£¤¥€₴₽₺ ₹ +−×÷=≠≤≥±∞∑∏√∫∆∂µπΩ←↑→↓↔",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":")).encode()).hexdigest()


def semantic_names(font):
    """Identify encoded glyphs by Unicode and unencoded glyphs by semantic name.

    Never compare GIDs: static/VF/CFF compilers may reorder the same glyph set.
    Normalize production uniXXXX names in alternate stems as well.
    """
    reverse = {}
    for cp, name in sorted(font.getBestCmap().items()):
        reverse.setdefault(name, []).append(cp)
    def canonical(name):
        if name in reverse:
            # A glyph with multiple Unicode aliases still has one semantic
            # identity. Alias additions/removals are audited separately in cmap.
            return f"U+{min(reverse[name]):04X}"
        stem, dot, suffix = name.partition(".")
        text = agl.toUnicode(stem)
        if text:
            stem = "U+" + "+".join(f"{ord(c):04X}" for c in text)
        return stem + (dot + suffix if dot else "")
    return {name: canonical(name) for name in font.getGlyphOrder()}


def layout_snapshot(font, tag, names):
    if tag not in font:
        return {"features": [], "sha256": None}
    output = io.BytesIO()
    writer = XMLWriter(output)
    writer.begintag("layout")
    font[tag].toXML(writer, font)
    writer.endtag("layout")
    root = ET.fromstring(output.getvalue())
    # XML glyph references are names, not binary IDs. Other attributes (lookup
    # indexes, values, anchors, scripts/languages) deliberately remain exact.
    for element in root.iter():
        for key, value in list(element.attrib.items()):
            if key in {"glyph", "value", "in", "out", "components", "second", "first"}:
                element.set(key, ",".join(names.get(v, v) for v in value.split(",")))
    feature_list = font[tag].table.FeatureList
    return {"features": sorted({r.FeatureTag for r in feature_list.FeatureRecord})
            if feature_list else [],
            "sha256": hashlib.sha256(ET.tostring(root)).hexdigest()}


def name_values(font, name_id):
    return sorted({n.toUnicode() for n in font["name"].names if n.nameID == name_id})


def identity(font):
    variable = "fvar" in font
    italic = bool(font["OS/2"].fsSelection & 1)
    return {"style": "italic" if italic else "upright",
            "weight": int(font["OS/2"].usWeightClass), "variable": variable}


def font_key(font):
    info = identity(font)
    return f"{info['style']}:{'variable' if info['variable'] else info['weight']}"


def raw_font(font):
    """HarfBuzz needs an SFNT, not a WOFF container."""
    old_flavor = font.flavor
    try:
        font.flavor = None
        stream = io.BytesIO()
        font.save(stream, reorderTables=False)
        return stream.getvalue()
    finally:
        font.flavor = old_flavor


def shape(hbfont, order, names, text, features=None, language=None, script=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if language:
        buf.language = language
    if script:
        buf.script = script
    hb.shape(hbfont, buf, features or {})
    rows = []
    missing = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        glyph = order[info.codepoint]
        rows.append([names[glyph], info.cluster, pos.x_advance, pos.y_advance,
                     pos.x_offset, pos.y_offset])
        if info.codepoint == 0:
            missing.append(info.cluster)
    return {"sha256": digest(rows), "count": len(rows), "missing": missing,
            "sample": rows[:24]}


def substitution_probes(font):
    """Recover encoded inputs to GSUB single/alternate/ligature lookups.

    This also reaches ligatures whose inputs are themselves substituted glyphs.
    Contextual rules are additionally protected by the full layout-table audit.
    """
    inputs = {g: chr(cp) for cp, g in sorted(font.getBestCmap().items(), reverse=True)}
    if "GSUB" not in font or not font["GSUB"].table.LookupList:
        return []
    tables = []
    for lookup in font["GSUB"].table.LookupList.Lookup:
        for table in lookup.SubTable:
            tables.append(getattr(table, "ExtSubTable", table))
    probes = set()
    for _ in range(5):
        previous = len(inputs)
        for table in tables:
            for source, target in getattr(table, "mapping", {}).items():
                if source in inputs:
                    probes.add(inputs[source])
                    for dest in target if isinstance(target, list) else [target]:
                        inputs.setdefault(dest, inputs[source])
            for source, targets in getattr(table, "alternates", {}).items():
                if source in inputs:
                    probes.add(inputs[source])
                    for target in targets:
                        inputs.setdefault(target, inputs[source])
            for first, ligatures in getattr(table, "ligatures", {}).items():
                for ligature in ligatures:
                    glyphs = [first] + list(ligature.Component)
                    if all(g in inputs for g in glyphs):
                        text = "".join(inputs[g] for g in glyphs)
                        probes.add(text)
                        inputs.setdefault(ligature.LigGlyph, text)
        if len(inputs) == previous:
            break
    return sorted(probes)


def shaping_snapshot(font, names, weight=None):
    face = hb.Face(raw_font(font))
    hbfont = hb.Font(face)
    hbfont.scale = (font["head"].unitsPerEm,) * 2
    if weight is not None and "fvar" in font:
        hbfont.set_variations({"wght": weight})
    cmap = font.getBestCmap()
    order = font.getGlyphOrder()
    tests = {}
    # Every covered scalar is tested separately, so script guessing cannot turn
    # the whole character repertoire into a single Latin-script buffer.
    corpus = []
    notdef = []
    for cp in sorted(cmap):
        result = shape(hbfont, order, names, chr(cp))
        corpus.append([cp, result["sha256"]])
        if result["missing"]:
            notdef.append(f"U+{cp:04X}")
    tests["all-encoded-scalars"] = {"sha256": digest(corpus), "count": len(corpus),
                                     "missing": notdef, "sample": []}
    for label, text in SAMPLES.items():
        # Do not manufacture failures for sample characters outside the baseline.
        text = "".join(c for c in text if ord(c) in cmap)
        tests[label] = shape(hbfont, order, names, text)
    for language in ("ru", "bg", "sr", "mk"):
        text = "".join(c for c in SAMPLES["cyrillic"] if ord(c) in cmap)
        for enabled in (0, 1):
            tests[f"locl:{language}:{enabled}"] = shape(
                hbfont, order, names, text, {"locl": enabled}, language, "Cyrl")
    features = set()
    for tag in ("GSUB", "GPOS"):
        features.update(layout_snapshot(font, tag, names)["features"])
    # All encoded glyphs and recovered ligature inputs exercise each feature,
    # not merely a hand-selected Latin specimen that may miss alternate glyphs.
    probes = [chr(cp) for cp in sorted(cmap)] + substitution_probes(font)
    effects = {}
    for feature in sorted(features | SETS | {"liga", "frac", "kern", "mark", "mkmk"}):
        off, on = [], []
        changes = 0
        for text in probes:
            a = shape(hbfont, order, names, text, {feature: 0})
            b = shape(hbfont, order, names, text, {feature: 1})
            off.append(a["sha256"])
            on.append(b["sha256"])
            changes += a["sha256"] != b["sha256"]
        tests[f"feature:{feature}:off"] = {"sha256": digest(off), "count": len(off)}
        tests[f"feature:{feature}:on"] = {"sha256": digest(on), "count": len(on)}
        effects[feature] = changes
    for tag, text in (("kern", "AVATAR To Wa Yo"),
                      ("mark", SAMPLES["marks-decomposed"]),
                      ("mkmk", "a\u0301\u0323 a\u0308\u0301"),
                      ("liga", SAMPLES["latin"]), ("frac", SAMPLES["fractions"])):
        text = "".join(c for c in text if ord(c) in cmap)
        for enabled in (0, 1):
            tests[f"sequence:{tag}:{enabled}"] = shape(hbfont, order, names, text, {tag: enabled})
    return {"tests": tests, "feature_effects": effects}


def outline_snapshot(font):
    glyph_set = font.getGlyphSet()
    names = semantic_names(font)
    result, errors = {}, []
    for name in font.getGlyphOrder():
        try:
            pen = DecomposingRecordingPen(glyph_set, skipMissingComponents=False)
            glyph_set[name].draw(pen)
            contour_open = False
            for operation, points in pen.value:
                if operation == "moveTo":
                    if contour_open:
                        raise ValueError("unclosed contour before moveTo")
                    contour_open = True
                elif operation in ("closePath", "endPath"):
                    if operation == "endPath":
                        raise ValueError("open font contour")
                    contour_open = False
                for point in points:
                    if point is not None and not all(math.isfinite(v) for v in point):
                        raise ValueError("nonfinite coordinate")
            if contour_open:
                raise ValueError("unclosed final contour")
            bounds = BoundsPen(glyph_set)
            area = AreaPen(glyph_set)
            pen.replay(bounds)
            pen.replay(area)
            result[names[name]] = {"sha256": digest(pen.value),
                                   "bounds": bounds.bounds, "area": round(abs(area.value), 6),
                                   "operations": len(pen.value)}
        except Exception as exc:
            errors.append({"glyph": name, "error": str(exc)})
    return result, errors


def snapshot(font, path, include_shaping=True):
    names = semantic_names(font)
    os2, hhea = font["OS/2"], font["hhea"]
    outlines, errors = outline_snapshot(font)
    result = {
        "path": str(path), "identity": identity(font),
        "upm": font["head"].unitsPerEm,
        "version": font["head"].fontRevision,
        "names": {str(i): name_values(font, i) for i in (1, 2, 4, 6, 16, 17)},
        "attribution": {str(i): name_values(font, i) for i in (0, 8, 9, 10, 13)},
        "style_bits": {"fsSelection": os2.fsSelection, "macStyle": font["head"].macStyle,
                       "italicAngle": font["post"].italicAngle},
        "vendor": os2.achVendID,
        "cmap": {str(cp): names[g] for cp, g in sorted(font.getBestCmap().items())},
        "glyphs": sorted(names.values()),
        "metrics": {"hhea": [hhea.ascent, hhea.descent, hhea.lineGap],
                    "typo": [os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap],
                    "win": [os2.usWinAscent, os2.usWinDescent]},
        "advances": {names[g]: width for g, (width, _) in font["hmtx"].metrics.items()},
        "layout": {tag: layout_snapshot(font, tag, names) for tag in ("GSUB", "GPOS")},
        "outlines": outlines, "outline_errors": errors,
        "axes": {a.axisTag: [a.minValue, a.defaultValue, a.maxValue]
                 for a in font["fvar"].axes} if "fvar" in font else {},
    }
    if include_shaping:
        result["shaping"] = shaping_snapshot(font, names)
    return result


def load_collection(directory, *, instances=False):
    """Prefer TTF over duplicate OTF instances; retain each style/weight once."""
    paths = sorted(Path(directory).rglob("*.ttf")) + sorted(Path(directory).rglob("*.otf"))
    collection = {}
    duplicates = []
    for path in paths:
        with TTFont(path, recalcTimestamp=False) as font:
            key = font_key(font)
            if key in collection:
                duplicates.append(str(path))
                continue
            print(f"  Reading {path}", flush=True)
            collection[key] = snapshot(font, path)
            if instances and "fvar" in font:
                for weight in WEIGHTS + INTERMEDIATES:
                    instance = instantiateVariableFont(font, {"wght": weight}, inplace=False)
                    try:
                        collection[f"{identity(font)['style']}:instance:{weight}"] = snapshot(
                            instance, f"{path}@wght={weight}")
                    finally:
                        instance.close()
    return {"schema": SCHEMA, "fonts": collection, "duplicate_formats": duplicates}


def comparable(data):
    return {key: {k: v for k, v in item.items() if k != "path"}
            for key, item in data["fonts"].items()}


class Audit:
    def __init__(self, family, approved=()):
        self.family = family
        self.checks = []
        self.drift = []
        self.approved = set(approved)
        author_file = Path(__file__).resolve().parent.parent / "AUTHORS.txt"
        author_record = next((line.strip() for line in author_file.read_text(encoding="utf-8").splitlines()
                              if line.strip() and not line.lstrip().startswith("#")), "")
        self.author = author_record.partition("<")[0].strip()
        if not self.author:
            raise ValueError("AUTHORS.txt must identify the Goeist author")

    def check(self, key, success, detail=None):
        self.checks.append({"id": key, "ok": bool(success), "detail": detail})

    def difference(self, key, old, new, regression=True):
        if old == new:
            return
        entry = {"id": "drift:" + key, "release": old, "source": new,
                 "regression": regression, "approved": "drift:" + key in self.approved}
        self.drift.append(entry)
        if regression:
            self.check(entry["id"], entry["approved"], "Source/release drift requires explicit approval")


def compare_font(audit, key, baseline, built, *, rounded=True):
    prefix = f"source:{key}"
    for field in ("cmap", "glyphs", "upm", "metrics", "advances"):
        audit.check(f"{prefix}:{field}", baseline[field] == built[field],
                    None if baseline[field] == built[field] else {"expected_sha256": digest(baseline[field]),
                                                                "actual_sha256": digest(built[field])})
    for tag in ("GSUB", "GPOS"):
        audit.check(f"{prefix}:{tag}", baseline["layout"][tag] == built["layout"][tag],
                    {"expected": baseline["layout"][tag], "actual": built["layout"][tag]})
    btests, tests = baseline["shaping"]["tests"], built["shaping"]["tests"]
    failures = [name for name in btests if name not in tests or
                btests[name]["sha256"] != tests[name]["sha256"]]
    audit.check(f"{prefix}:shaping", not failures, {"test_count": len(btests), "failures": failures})
    audit.check(f"{prefix}:notdef", not tests["all-encoded-scalars"]["missing"],
                tests["all-encoded-scalars"]["missing"])
    audit.check(f"{prefix}:valid-outlines", not built["outline_errors"], built["outline_errors"])
    lost_shapes = [name for name, outline in baseline["outlines"].items()
                   if outline["operations"] and not built["outlines"].get(name, {}).get("operations")]
    audit.check(f"{prefix}:all-encoded-and-unencoded-shapes", not lost_shapes, lost_shapes)
    if rounded and key.split(":")[-1] in {"400", "700"}:
        changes = {}
        for char in "HAntr":
            name = baseline["cmap"].get(str(ord(char)))
            before, after = baseline["outlines"].get(name), built["outlines"].get(name)
            if before and after:
                delta = abs(before["area"] - after["area"])
                changes[char] = {"area_delta": delta,
                                 "meaningful": before["sha256"] != after["sha256"] and
                                 delta > max(0.25, before["area"] * 0.00005)}
            else:
                changes[char] = {"meaningful": False}
        audit.check(f"{prefix}:meaningful-rounding", all(v["meaningful"] for v in changes.values()), changes)


def audit_drift(audit, source, release):
    for style in ("upright", "italic"):
        vf = release["fonts"].get(f"{style}:variable")
        if not vf:
            audit.check(f"reference:{style}:variable", False, "Missing official reference variable font")
            continue
        for weight in WEIGHTS:
            old = release["fonts"].get(f"{style}:instance:{weight}")
            new = source["fonts"].get(f"{style}:{weight}") or source["fonts"].get(f"{style}:instance:{weight}")
            if not old or not new:
                audit.check(f"baseline:{style}:{weight}", False, "Missing source/release weight")
                continue
            prefix = f"{style}:{weight}"
            known_omega_correction = (
                old["cmap"].get(str(0x03C9)) == old["cmap"].get(str(0x03A9)) and
                str(0x03C9) not in new["cmap"] and
                new["cmap"].get(str(0x2126)) == new["cmap"].get(str(0x03A9)) and
                old["cmap"].get(str(0x03A9)) == new["cmap"].get(str(0x03A9))
            )
            for field in ("cmap", "glyphs"):
                old_set, new_set = set(old[field]), set(new[field])
                lost = old_set - new_set
                expected_loss = field == "cmap" and known_omega_correction and lost == {str(0x03C9)}
                if lost:
                    audit.difference(f"{prefix}:{field}:lost", sorted(lost), [], not expected_loss)
                    if expected_loss:
                        audit.drift[-1]["reason"] = (
                            "upstream_source_drift: source corrects release's erroneous "
                            "lowercase omega alias to U+2126 OHM SIGN; no outline lost")
                if new_set - old_set:
                    audit.difference(f"{prefix}:{field}:added", [], sorted(new_set - old_set), False)
            for field in ("metrics", "upm"):
                audit.difference(f"{prefix}:{field}", old[field], new[field])
            common_advances = set(old["advances"]) & set(new["advances"])
            changed = {g: [old["advances"][g], new["advances"][g]] for g in common_advances
                       if old["advances"][g] != new["advances"][g]}
            if changed:
                audit.difference(f"{prefix}:advances", changed, {})
            for tag in ("GSUB", "GPOS"):
                lost = sorted(set(old["layout"][tag]["features"]) - set(new["layout"][tag]["features"]))
                if lost:
                    audit.difference(f"{prefix}:{tag}:lost-features", lost, [])
                audit.difference(f"{prefix}:{tag}:table", old["layout"][tag], new["layout"][tag], False)
            # Corpus digests cannot be compared across changed repertoires; fixed
            # probes still expose release-vs-source substitutions and positions.
            old_tests, new_tests = old["shaping"]["tests"], new["shaping"]["tests"]
            changes = {test: {"release": old_tests[test], "source": new_tests.get(test)}
                       for test in old_tests if not test.startswith(("feature:", "all-encoded"))
                       and old_tests[test]["sha256"] != new_tests.get(test, {}).get("sha256")}
            if changes:
                audit.difference(f"{prefix}:shaping", changes, {})


def audit_naming(audit, key, data):
    style, suffix = key.split(":", 1)
    italic = style == "italic"
    names = data["names"]
    attribution = data["attribution"]
    audit.check(f"naming:{key}:designer", attribution["9"] == [audit.author], attribution["9"])
    audit.check(f"naming:{key}:manufacturer", attribution["8"] == [MANUFACTURER], attribution["8"])
    audit.check(f"naming:{key}:copyright", bool(attribution["0"]) and
                all(audit.author in text and "The Geist Project Authors" in text
                    for text in attribution["0"]), attribution["0"])
    audit.check(f"naming:{key}:upstream-credit", bool(attribution["10"]) and
                all(f"Vercel {audit.family.upstream_label}" in text and
                    "Not affiliated with or endorsed by Vercel" in text
                    for text in attribution["10"]), attribution["10"])
    audit.check(f"naming:{key}:ofl", bool(attribution["13"]) and
                all("sil open font license" in text.casefold() for text in attribution["13"]),
                attribution["13"])
    family = names["16"] or names["1"]
    audit.check(f"naming:{key}:family", bool(family) and all(n == audit.family.name for n in family), family)
    audit.check(f"naming:{key}:derivative-version",
                abs(data["version"] - float(FONT_VERSION_STRING)) < 0.0001, data["version"])
    audit.check(f"naming:{key}:no-upstream-name", all("Geist" not in value for values in names.values()
                                                   for value in values), names)
    subfamilies = names["17"] or names["2"]
    audit.check(f"naming:{key}:italic", bool(subfamilies) and
                all(("Italic" in value) == italic for value in subfamilies), subfamilies)
    bits = data["style_bits"]
    audit.check(f"naming:{key}:style-bits", bool(bits["fsSelection"] & 1) == italic and
                bool(bits["macStyle"] & 2) == italic and (bits["italicAngle"] != 0) == italic, bits)
    audit.check(f"naming:{key}:vendor", data["vendor"] == VENDOR_ID, data["vendor"])
    if suffix != "variable":
        weight = int(suffix)
        bold = weight == 700
        audit.check(f"naming:{key}:bold-link", bool(bits["fsSelection"] & 32) == bold and
                    bool(bits["macStyle"] & 1) == bold, bits)
        # Legacy RIBBI families group only Regular/Bold/Italic/Bold Italic.
        if weight in (400, 700):
            audit.check(f"naming:{key}:legacy-family", names["1"] == [audit.family.name], names["1"])


def audit_delivery(audit, root, baseline):
    root = Path(root)
    for ext, directory in (("ttf", "ttf"), ("otf", "otf")):
        files = sorted((root / directory).glob(f"*.{ext}"))
        audit.check(f"delivery:{ext}:count", len(files) == 18, [str(p) for p in files])
        keys = []
        for path in files:
            try:
                with TTFont(path, recalcTimestamp=False) as font:
                    keys.append(font_key(font))
                    audit.check(f"delivery:{path.name}:static", "fvar" not in font)
                    if ext == "otf":
                        audit.check(f"delivery:{path.name}:cff", "CFF " in font)
                        data = snapshot(font, path)
                        key = font_key(font)
                        audit_naming(audit, key, data)
                        if key in baseline["fonts"]:
                            compare_font(audit, "otf:" + key, baseline["fonts"][key], data)
                        else:
                            audit.check(f"source:otf:{key}:baseline", False, "Missing source baseline")
            except Exception as exc:
                audit.check(f"delivery:{path.name}:load", False, str(exc))
        expected = {f"{style}:{w}" for style in ("upright", "italic") for w in WEIGHTS}
        audit.check(f"delivery:{ext}:styles", set(keys) == expected and len(keys) == len(set(keys)), keys)
    variables = sorted((root / "variable").glob("*.ttf"))
    audit.check("delivery:variables:count", len(variables) == 2, [str(p) for p in variables])
    ttfs = sorted((root / "ttf").glob("*.ttf")) + variables
    expected_web = set()
    for path in ttfs:
        web = root / "webfonts" / (path.stem + ".woff2")
        expected_web.add(web.name)
        if not web.exists():
            audit.check(f"web:{path.stem}:exists", False, str(web))
            continue
        try:
            with TTFont(path, recalcTimestamp=False) as sfnt, TTFont(web, recalcTimestamp=False) as woff:
                audit.check(f"web:{path.stem}:flavor", woff.flavor == "woff2")
                # WOFF2 can rewrite glyf/loca/head representations losslessly;
                # compare semantic outlines plus exact unaffected table bytes.
                tags = set(sfnt.keys()) - {"GlyphOrder", "DSIG"}
                audit.check(f"web:{path.stem}:table-set", tags == set(woff.keys()) - {"GlyphOrder", "DSIG"})
                differences = [tag for tag in sorted(tags - {"head", "glyf", "loca"})
                               if sfnt.getTableData(tag) != woff.getTableData(tag)]
                audit.check(f"web:{path.stem}:table-parity", not differences, differences)
                left, lerrors = outline_snapshot(sfnt)
                right, rerrors = outline_snapshot(woff)
                audit.check(f"web:{path.stem}:outline-parity", left == right and not lerrors and not rerrors,
                            {"sfnt_errors": lerrors, "woff_errors": rerrors})
        except Exception as exc:
            audit.check(f"web:{path.stem}:load", False, str(exc))
    actual_web = {p.name for p in (root / "webfonts").glob("*.woff2")}
    audit.check("delivery:webfonts:count-and-names", expected_web == actual_web and len(actual_web) == 20,
                {"expected": sorted(expected_web), "actual": sorted(actual_web)})


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--family", default="Goeist", choices=sorted(FAMILIES))
    parser.add_argument("--fonts", type=Path, help="default: fonts/<family>")
    parser.add_argument("--reference", type=Path, help="default: sources/<family>/upstream/reference")
    parser.add_argument("--source-baseline", type=Path, help="default: build/<family>/baseline")
    parser.add_argument("--drift-allowlist", type=Path,
                        help="default: sources/<family>/drift-allowlist.json, if present")
    parser.add_argument("--output", type=Path, help="default: out/<family>/verification.json")
    args = parser.parse_args()
    family = FAMILIES[args.family]
    args.fonts = args.fonts or Path("fonts") / family.key
    args.reference = args.reference or Path("sources") / family.key / "upstream/reference"
    args.source_baseline = args.source_baseline or Path("build") / family.key / "baseline"
    args.output = args.output or Path("out") / family.key / "verification.json"
    default_allowlist = Path("sources") / family.key / "drift-allowlist.json"
    args.drift_allowlist = args.drift_allowlist or (default_allowlist if default_allowlist.is_file() else None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    audit = Audit(family, json.loads(args.drift_allowlist.read_text()).get("approved", [])
                  if args.drift_allowlist else ())
    report = {"schema": SCHEMA, "checks": audit.checks, "source_release_drift": audit.drift}
    try:
        built = load_collection(args.fonts, instances=True)
        baseline = load_collection(args.source_baseline, instances=True)
        release = load_collection(args.reference, instances=True)
        report["source_baseline_fingerprint"] = digest(comparable(baseline))
        report["reference_fingerprint"] = digest(comparable(release))
        report["versions"] = {
            "release": sorted({f["version"] for f in release["fonts"].values()}),
            "source": sorted({f["version"] for f in baseline["fonts"].values()}),
            "rounded": sorted({f["version"] for f in built["fonts"].values()}),
        }
        audit_drift(audit, baseline, release)
        expected = {f"{style}:{w}" for style in ("upright", "italic") for w in WEIGHTS}
        expected |= {f"{style}:variable" for style in ("upright", "italic")}
        audit.check("inventory:built", expected.issubset(built["fonts"]),
                    sorted(expected - set(built["fonts"])))
        audit.check("inventory:source-baseline", expected.issubset(baseline["fonts"]),
                    sorted(expected - set(baseline["fonts"])))
        for key, data in built["fonts"].items():
            if ":instance:" not in key:
                audit_naming(audit, key, data)
            if key.endswith(":variable"):
                audit.check(f"axes:{key}", data["axes"] == {"wght": [100, 400, 900]}, data["axes"])
            if key in baseline["fonts"]:
                compare_font(audit, key, baseline["fonts"][key], data)
            else:
                audit.check(f"source:{key}:baseline", False, "Missing source baseline for this font/instance")
        for style in ("upright", "italic"):
            for weight in WEIGHTS:
                static = built["fonts"].get(f"{style}:{weight}")
                instance = built["fonts"].get(f"{style}:instance:{weight}")
                audit.check(f"instance:{style}:{weight}:available", bool(static and instance))
                if static and instance:
                    audit.check(f"instance:{style}:{weight}:advances", static["advances"] == instance["advances"])
        audit_delivery(audit, args.fonts, baseline)
        report["inventory"] = {key: {"path": value["path"], "glyph_count": len(value["glyphs"]),
                                      "cmap_count": len(value["cmap"]), "axes": value["axes"],
                                      "feature_effects": value["shaping"]["feature_effects"]}
                               for key, value in built["fonts"].items()}
    except Exception as exc:
        audit.check("verification:exception", False, f"{type(exc).__name__}: {exc}")
    failures = [check for check in audit.checks if not check["ok"]]
    report["ok"] = not failures
    report["summary"] = {"passed": len(audit.checks) - len(failures), "failed": len(failures),
                         "source_release_differences": len(audit.drift)}
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"{'PASS' if report['ok'] else 'FAIL'}: {report['summary']['passed']} passed; "
          f"{len(failures)} failed; {len(audit.drift)} explicit source/release differences")
    for failure in failures:
        print(f"  FAIL {failure['id']}: {json.dumps(failure['detail'], ensure_ascii=False)}")
    print(f"Report: {args.output}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
