#!/usr/bin/env python3
"""Build Goeist Serif's source and fonts from Geist Serif's corner-component serifs.

Geist Serif draws its serifs as Glyphs corner and cap components: a curved
bracket, a straight wedge and a 4-6 unit tip. glyphsLib cannot place them, so
upstream's `glyphs_corners.py` (vendored unchanged in
sources/GoeistSerif/upstream/scripts) places every component into its glyph
first. Goeist Serif hooks into that placement: each serif's tip becomes one
circular end tangent to the serif's flat side, at the original reach, so serif
lengths and spacing stay. A tip a few units thick cannot hold a visible round,
so the end is thickened to `SoftSerif.tip` first, the way Fraunces' SOFT axis
gives a serif end the thickness of a hairline. Open corners and overlaps are
then erased, cut terminals and spikes get inscribed circular caps, and the
shared fillets of rounding.py round every remaining corner. Compilation reuses
upstream's `build-geist-serif.py` table helpers.

  python scripts/serif.py --source <GeistSerif.glyphspackage> --output <out.glyphs> --report <report.json>
"""
from __future__ import annotations

import argparse
import copy
import glob
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import openstep_plist
import pathops
from fontTools.otlLib.optimize import compact
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps
from gftools.fix import fix_unhinted_font
from glyphsLib import GSFont
from glyphsLib.filters.eraseOpenCorners import EraseOpenCornersPen
from glyphsLib.classes import CURVE, LINE, OFFCURVE, GSNode, GSPath

import collisions
from families import FAMILIES, Family
from rounding import (Contour, GeometryError, OutlineContext, classify_corner, evaluate, filled, ink_side,
                      measure_stems, round_font, section, split, tangent)

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_SCRIPTS = ROOT / "sources" / "GoeistSerif" / "upstream" / "scripts"


def upstream_module(name, filename):
    """A script vendored unchanged from vercel/geist-font (OFL-1.1)."""
    spec = importlib.util.spec_from_file_location(name, UPSTREAM_SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def corners_module():
    return upstream_module("glyphs_corners", "glyphs_corners.py")


def _sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def _add(a, b, k=1.0):
    return a[0] + b[0] * k, a[1] + b[1] * k


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _unit(v):
    length = math.hypot(*v)
    return v[0] / length, v[1] / length


def arc_nodes(center, radius, start, sweep):
    """Circular arc from angle `start` through `sweep` radians as chain nodes.

    Each node carries the handles of its arriving cubic; pieces stay within 90°.
    """
    pieces = max(1, math.ceil(abs(sweep) / (math.pi / 2) - 1e-9))
    step = sweep / pieces
    handle = 4 / 3 * math.tan(step / 4) * radius
    nodes = []
    for i in range(pieces):
        a, b = start + step * i, start + step * (i + 1)
        p = _add(center, (math.cos(a), math.sin(a)), radius)
        q = _add(center, (math.cos(b), math.sin(b)), radius)
        h1 = _add(p, (-math.sin(a), math.cos(a)), handle)
        h2 = _add(q, (math.sin(b), -math.cos(b)), handle)
        nodes.append({"pt": q, "h": (h1, h2), "serif": True})
    return nodes


def find_tip(shape, run):
    """Index i of the serif tip edge shape[i] -> shape[i + 1] inside `run`, or None.

    The tip is the short straight edge whose two straight neighbours converge
    on it most sharply: the cut-off point of the wedge.
    """
    count = len(shape)
    best = None
    for i in run:
        j, before, after = (i + 1) % count, (i - 1) % count, (i + 2) % count
        if j not in run or shape[j]["h"] or shape[i]["h"] or shape[after]["h"]:
            continue
        a, b, c, d = (shape[k]["pt"] for k in (before, i, j, after))
        edge = math.dist(b, c)
        if edge > 12 or math.dist(a, b) < 3 * edge or math.dist(c, d) < 3 * edge:
            continue
        angle = math.acos(max(-1, min(1, _dot(_unit(_sub(b, a)), _unit(_sub(c, d))))))
        if angle < math.radians(75) and (best is None or angle < best[0]):
            best = (angle, i)
    return None if best is None else best[1]


def soften_tip(shape, i, tip):
    """Shape with the tip edge shape[i] -> shape[i + 1] replaced by a circular end.

    The flat side (the neighbour edge not followed by the bracket curve) keeps
    its line and the serif keeps its reach; the wedge side is redrawn as the
    tangent from the bracket to the circle. Returns (shape, radius); radius is
    None, and the shape unchanged, when the serif is too small to hold the end.
    """
    # Rotate so the tip and its neighbours never wrap around the start node.
    offset = (i - 1) % len(shape)
    shape = shape[offset:] + shape[:offset]
    before, i, j, after = 0, 1, 2, 3
    # The wedge leads into the bracket curve; the flat side continues straight.
    wedge_first = bool(shape[before]["h"])
    if wedge_first == bool(shape[(after + 1) % len(shape)]["h"]):
        return shape, None
    if wedge_first:
        bracket, flat_far, flat_near = before, after, j
    else:
        bracket, flat_far, flat_near = after, before, i
    p = shape[bracket]["pt"]
    q0 = shape[flat_far]["pt"]
    u = _unit(_sub(shape[flat_near]["pt"], q0))
    normal = (-u[1], u[0])
    height = _dot(_sub(p, q0), normal)
    if abs(height) < 1e-6:
        return shape, None
    if height < 0:
        normal, height = (-normal[0], -normal[1]), -height
    radius = min(tip, 0.75 * height) / 2
    reach = max(_dot(_sub(shape[k]["pt"], q0), u) for k in (i, j))
    center = _add(_add(q0, u, reach - radius), normal, radius)
    flat_point = _add(center, normal, -radius)
    distance = math.dist(p, center)
    along = _dot(_sub(p, q0), u)
    if distance <= radius * 1.05 or along >= reach - 2 * radius or _dot(_sub(flat_point, q0), u) <= 0:
        return shape, None
    # Tangent from the bracket end to the circle, on the side away from the flat.
    w = _unit(_sub(p, center))
    beta = math.acos(radius / distance)
    candidates = []
    for sign in (1, -1):
        c, s = math.cos(sign * beta), math.sin(sign * beta)
        candidates.append(_add(center, (w[0] * c - w[1] * s, w[0] * s + w[1] * c), radius))
    wedge_point = max(candidates, key=lambda point: _dot(_sub(point, center), normal))
    angle = lambda point: math.atan2(point[1] - center[1], point[0] - center[0])
    start, end = (wedge_point, flat_point) if wedge_first else (flat_point, wedge_point)
    a0, a1, apex = angle(start), angle(end), math.atan2(u[1], u[0])
    sweep = (a1 - a0) % (2 * math.pi)
    # Go round the far side of the circle, through the serif's reach.
    if (apex - a0) % (2 * math.pi) > sweep:
        sweep -= 2 * math.pi
    replacement = [{"pt": start, "h": None, "serif": True}, *arc_nodes(center, radius, a0, sweep)]
    replacement[-1]["pt"] = end
    # Turn the bracket's end handle onto the new wedge line, so it stays tangent.
    direction = _unit(_sub(wedge_point, p))
    if wedge_first:
        h1, h2 = shape[bracket]["h"]
        shape[bracket] = {**shape[bracket], "h": (h1, _add(p, direction, -math.dist(p, h2)))}
    else:
        follower = bracket + 1
        h1, h2 = shape[follower]["h"]
        shape[follower] = {**shape[follower], "h": (_add(p, direction, -math.dist(p, h1)), h2)}
    shape = shape[:i] + replacement + shape[j + 1:]
    shape[i + len(replacement)]["h"] = None
    return shape, radius


def soften_shape(shape, tip, stats):
    """Soften every serif placed in one expanded shape (nodes tagged by their hint)."""
    done = set()
    while True:
        runs = {}
        for index, node in enumerate(shape):
            if node["serif"] and node["serif"] is not True and node["serif"] not in done:
                runs.setdefault(node["serif"], set()).add(index)
        if not runs:
            return shape
        serif, run = next(iter(runs.items()))
        done.add(serif)
        i = find_tip(shape, run)
        radius = None
        if i is not None:
            shape, radius = soften_tip(shape, i, tip)
        stats["softened" if radius else "kept"] += 1
        if radius:
            stats["radius_min"] = min(stats.get("radius_min", radius), radius)


def expand_package(src, dst, tip=None):
    """Expand corner/cap components and strokes in the package copy at `dst`.

    Mirrors glyphs_corners.expand_package; with `tip` set, every placed serif
    is softened before it is written. Returns per-outcome counts.
    """
    corners = corners_module()
    source = corners.GlyphsSource(str(src))
    masters = {m["id"] for m in source.fontinfo()["fontMaster"]}
    stats = Counter()
    for path in sorted(glob.glob(os.path.join(dst, "glyphs", "*.glyph"))):
        with open(path) as stream:
            glyph = openstep_plist.load(stream, use_numbers=True)
        touched = False
        for layer in glyph["layers"]:
            if layer.get("layerId") not in masters:
                continue
            shapes = layer.get("shapes", [])
            stroked = any("strokeWidth" in (s.get("attr") or {}) for s in shapes if "ref" not in s)
            if not stroked and not any(h.get("type") in ("Corner", "Cap") for h in layer.get("hints", [])):
                continue
            own = iter(corners.layer_parts(glyph["glyphname"], source, layer["layerId"])[1])
            new = []
            for shape in shapes:
                if "ref" in shape:
                    new.append(shape)
                    continue
                attr = {k: v for k, v in (shape.get("attr") or {}).items() if not k.startswith("stroke")}
                for index in range(2 if "strokeWidth" in (shape.get("attr") or {}) else 1):
                    item = {k: v for k, v in shape.items() if k != "attr"}
                    expanded = next(own)
                    if tip:
                        expanded = soften_shape(expanded, tip, stats)
                    item["nodes"] = corners._plist_nodes(expanded)
                    if attr and index == 0:
                        item["attr"] = attr
                    new.append(item)
            layer["shapes"] = new
            layer["hints"] = [h for h in layer.get("hints", []) if h.get("type") not in ("Corner", "Cap")]
            if not layer["hints"]:
                del layer["hints"]
            touched = True
        if touched:
            with open(path, "w") as stream:
                openstep_plist.dump(glyph, stream)
            stats["glyphs"] += 1
    return stats


def _sample(segment, reverse):
    """(t, point, unit direction of travel) along a segment, from its tip end."""
    steps = 96
    rows = []
    for k in range(steps + 1):
        t = 1 - k / steps if reverse else k / steps
        t = min(max(t, 1e-6), 1 - 1e-6)
        rows.append((t, evaluate(segment.points, t), tangent(split(segment.points, t)[1])))
    return rows


def _crossing(a, b):
    """First crossing of polylines a and b, nearest their starts: (i, s, j, u)."""
    best = None
    for i in range(len(a) - 1):
        p, r = a[i], _sub(a[i + 1], a[i])
        for j in range(len(b) - 1):
            q, s = b[j], _sub(b[j + 1], b[j])
            denominator = r[0] * s[1] - r[1] * s[0]
            if abs(denominator) < 1e-12:
                continue
            offset = _sub(q, p)
            x = (offset[0] * s[1] - offset[1] * s[0]) / denominator
            y = (offset[0] * r[1] - offset[1] * r[0]) / denominator
            if 0 <= x <= 1 and 0 <= y <= 1 and (best is None or i + x + j + y < best[0]):
                best = (i + x + j + y, i, x, j, y)
    return None if best is None else best[1:]


def _cap(incoming, outgoing, tip_mid, side, radius):
    """Circle of `radius` inscribed between two segments meeting at a cut tip.

    Returns (t_in, t_out, arc nodes) or None if the stroke never narrows to it.
    """
    rows_in, rows_out = _sample(incoming, True), _sample(outgoing, False)
    inward = lambda d: (-d[1] * side, d[0] * side)
    offset_in = [_add(p, inward(d), radius) for _, p, d in rows_in]
    offset_out = [_add(p, inward(d), radius) for _, p, d in rows_out]
    hit = _crossing(offset_in, offset_out)
    if hit is None:
        return None
    i, x, j, y = hit
    t_in = rows_in[i][0] + x * (rows_in[i + 1][0] - rows_in[i][0])
    t_out = rows_out[j][0] + y * (rows_out[j + 1][0] - rows_out[j][0])
    center = _add(offset_in[i], _sub(offset_in[i + 1], offset_in[i]), x)
    start, end = evaluate(incoming.points, t_in), evaluate(outgoing.points, t_out)
    if not all(0.85 * radius < math.dist(point, center) < 1.15 * radius for point in (start, end)):
        return None
    angle = lambda point: math.atan2(point[1] - center[1], point[0] - center[0])
    a0 = angle(start)
    sweep = (angle(end) - a0) % (2 * math.pi)
    # Round the end through the tip, not back through the stroke.
    middle = lambda s: _add(center, (math.cos(a0 + s / 2), math.sin(a0 + s / 2)), radius)
    if math.dist(middle(sweep - 2 * math.pi), tip_mid) < math.dist(middle(sweep), tip_mid):
        sweep -= 2 * math.pi
    nodes = arc_nodes(center, radius, a0, sweep)
    nodes[-1]["pt"] = end
    # Hold the source tangents exactly at both joins (G1 with the stroke).
    d_in = tangent(split(incoming.points, t_in)[1])
    d_out = tangent(split(outgoing.points, t_out)[1])
    first, last = nodes[0]["h"], nodes[-1]["h"]
    nodes[0]["h"] = (_add(start, d_in, math.dist(start, first[0])), first[1])
    nodes[-1]["h"] = (last[0], _add(end, d_out, -math.dist(end, last[1])))
    return t_in, t_out, nodes


def _write_segments(path, segments, smooth):
    nodes = []
    for points, is_smooth in zip(segments, smooth):
        for control in points[1:-1]:
            nodes.append(GSNode(control, type=OFFCURVE))
        nodes.append(GSNode(points[-1], type=CURVE if len(points) == 4 else LINE, smooth=is_smooth))
    path.nodes = nodes


def _inside(arc, start, polygons):
    """Every interior point of the arc lies in the source ink."""
    previous = start
    for node in arc:
        piece = (previous, *node["h"], node["pt"])
        if not all(filled(polygons, evaluate(piece, s / 12)) for s in range(1, 12)):
            return False
        previous = node["pt"]
    return True


def cap_terminals(font, stems, profile, radius, max_edge, stats):
    """Give drawn cut terminals (s, c, e, a, r, figures...) one circular end.

    A terminal is a short straight cut between two convex corners. The end
    becomes the arc of the circle of `radius` inscribed in the stroke where it
    is that thick, tangent to both sides; the arc must stay in the source ink.
    `font` is a single-master GSFont, edited in place; `stems` maps master ids
    to measured stems. Terminals that cannot hold the circle are left for the
    ordinary fillets.
    """
    original = OutlineContext(copy.deepcopy(font))
    master = font.masters[0].id
    stem = stems[master]["stem"]
    for glyph in font.glyphs:
        layer = glyph.layers[master]
        if layer is None or not layer.paths:
            continue
        source = original.font.glyphs[glyph.name]
        polygons = original.polygons(source, source.layers[master])
        for path in layer.paths:
            rejected = set()
            while True:
                contour = Contour(path)
                count = len(contour.segments)
                applied = False
                for k, span in ((k, span) for k in range(count if count >= 4 else 0) for span in (3, 2)):
                    # span 3: segment k is a short cut between two convex corners;
                    # span 2: node k is a convex spike sharper than 140°.
                    first, last = (k - 1) % count, (k + span - 2) % count
                    incoming, outgoing = contour.segments[first], contour.segments[last]
                    tip = contour.segments[k].points if span == 3 else (contour.nodes[k].position,) * 2
                    key = (span, *(round(v, 3) for p in (tip[0], tip[-1]) for v in p))
                    if key in rejected:
                        continue
                    if span == 3:
                        edge = contour.segments[k]
                        if (len(edge.points) != 2 or edge.length > max_edge
                                or min(incoming.length, outgoing.length) < max(3 * edge.length, radius)):
                            continue
                        if any(classify_corner(contour, n % count, polygons, stem, profile)[0] != "convex"
                               for n in (k, k + 1)):
                            continue
                    else:
                        # Hairline spurs are too thin for classify_corner's side
                        # probes: test the ink inside the spike's own wedge instead.
                        if contour.nodes[k].smooth or min(incoming.length, outgoing.length) < radius:
                            continue
                        a, b = tangent(incoming.points, True), tangent(outgoing.points)
                        turn = math.atan2(a[0] * b[1] - a[1] * b[0], _dot(a, b))
                        wedge = _sub(b, a)
                        if abs(turn) < math.radians(140) or not filled(
                                polygons, _add(tip[0], _unit(wedge), 1.5)):
                            continue
                    side = ink_side(polygons, evaluate(incoming.points, 0.5),
                                    tangent(split(incoming.points, 0.5)[1]), 0.5)
                    tip_mid = ((tip[0][0] + tip[-1][0]) / 2, (tip[0][1] + tip[-1][1]) / 2)
                    cap = None
                    for scale in (1, 0.85, 0.7, 0.55):
                        candidate = side and _cap(incoming, outgoing, tip_mid, side, radius * scale)
                        if candidate and _inside(candidate[2], evaluate(incoming.points, candidate[0]),
                                                 polygons):
                            cap = candidate
                            break
                    if cap is None:
                        rejected.add(key)
                        stats["terminal_kept" if span == 3 else "spike_kept"] += 1
                        continue
                    t_in, t_out, arc = cap
                    order = [(first + n) % count for n in range(count)]
                    start = section(incoming.points, 0, t_in)
                    pieces, previous = [], start[-1]
                    for node in arc:
                        pieces.append((previous, *node["h"], node["pt"]))
                        previous = node["pt"]
                    segments = [start, *pieces, section(outgoing.points, t_out, 1),
                                *(contour.segments[n].points for n in order[span:])]
                    smooth = [True] * (1 + len(pieces)) + [contour.nodes[(n + 1) % count].smooth
                                                           for n in order[span - 1:]]
                    _write_segments(path, segments, smooth)
                    stats["terminal_capped" if span == 3 else "spike_capped"] += 1
                    applied = True
                    break
                if not applied:
                    break


class _CubicRecorder(BasePen):
    """Records outlines as moveTo/lineTo/curveTo/closePath; quadratics become cubics."""

    def __init__(self):
        super().__init__(None)
        self.value = []

    def _moveTo(self, point):
        self.value.append(("moveTo", (point,)))

    def _lineTo(self, point):
        self.value.append(("lineTo", (point,)))

    def _curveToOne(self, a, b, c):
        self.value.append(("curveTo", (a, b, c)))

    def _closePath(self):
        self.value.append(("closePath", ()))


def _smooth(previous, point, following):
    a, b = _sub(point, previous), _sub(following, point)
    return (math.hypot(*a) > 1e-9 and math.hypot(*b) > 1e-9
            and abs(a[0] * b[1] - a[1] * b[0]) < 1e-3 * math.hypot(*a) * math.hypot(*b)
            and _dot(a, b) > 0)


def _clean(items, tolerance=1.5):
    """Drop the sub-unit segments and split lines that skia leaves at crossings.

    `items` is one closed contour as segments (each a list of (point, type),
    ending on its on-curve point; each starts where the previous ends). A
    segment whose points all lie within `tolerance` of its start is removed,
    and consecutive collinear lines merge, so a corner cut into slivers becomes
    one corner again.
    """
    changed = True
    while changed and len(items) > 3:
        changed = False
        for index, item in enumerate(items):
            start = items[index - 1][-1][0]
            if all(math.dist(start, point) < tolerance for point, _ in item):
                end = item[-1][0]
                del items[index]
                # Keep the contour closed: the previous segment now ends here.
                previous = items[index - 1]
                previous[-1] = (end, previous[-1][1])
                if len(previous) == 3:
                    previous[1] = (_add(previous[1][0], _sub(end, start)), OFFCURVE)
                changed = True
                break
            following = items[(index + 1) % len(items)]
            if len(item) == 1 and len(following) == 1:
                a, b, c = start, item[0][0], following[0][0]
                if _collinear(_sub(b, a), _sub(c, b), 1e-3):
                    del items[index]
                    changed = True
                    break
            # A stub of line continuing a curve's tangent joins that curve.
            if len(item) == 1 and math.dist(start, item[0][0]) < 4:
                end = item[0][0]
                handle = next((p for p, _ in following[:2] if math.dist(p, end) > 1e-6), None) \
                    if len(following) == 3 else None
                previous = items[index - 1]
                before = next((p for p, _ in reversed(previous[:2]) if math.dist(p, start) > 1e-6), None) \
                    if len(previous) == 3 else None
                if handle and _collinear(_sub(end, start), _sub(handle, end)):
                    del items[index]
                    changed = True
                    break
                if before and _collinear(_sub(start, before), _sub(end, start)):
                    previous[1] = (_add(previous[1][0], _sub(end, start)), OFFCURVE)
                    previous[2] = (end, previous[2][1])
                    del items[index]
                    changed = True
                    break
    return items


def _collinear(u, v, tolerance=0.02):
    """Same direction within `tolerance` radians."""
    lu, lv = math.hypot(*u), math.hypot(*v)
    return lu > 1e-9 and lv > 1e-9 and _dot(u, v) > 0 and abs(u[0] * v[1] - u[1] * v[0]) < tolerance * lu * lv


def remove_overlaps(font):
    """Erase open corners, then union every master layer's own paths.

    Geist Serif cuts several terminals (c, e, ...) as Glyphs open corners,
    self-crossing loops that Glyphs and glyphsLib erase on export, and lays
    corner serifs over their stems; only the resulting ink shows which corners
    are exposed. Components are untouched. Returns the number of layers changed.
    """
    changed = 0
    for glyph in font.glyphs:
        for master in font.masters:
            layer = glyph.layers[master.id]
            if layer is None or not layer.paths:
                continue
            ink = pathops.Path()
            pen = EraseOpenCornersPen(ink.getPen())
            for path in layer.paths:
                contour = Contour(path)
                pen.moveTo(contour.segments[0].points[0])
                for segment in contour.segments:
                    if len(segment.points) == 2:
                        pen.lineTo(segment.points[1])
                    else:
                        pen.curveTo(*segment.points[1:])
                pen.closePath()
            union = pathops.simplify(ink, clockwise=False)
            recording = _CubicRecorder()
            union.draw(recording)
            paths = []
            for operator, points in recording.value:
                if operator == "moveTo":
                    start, items = points[0], []
                elif operator == "lineTo":
                    items.append([(points[0], LINE)])
                elif operator == "curveTo":
                    items.append([(points[0], OFFCURVE), (points[1], OFFCURVE), (points[2], CURVE)])
                else:
                    if not items or math.dist(items[-1][-1][0], start) > 1e-9:
                        items.append([(start, LINE)])
                    paths.append(_clean(items))
            for path in list(layer.paths):
                layer.shapes.remove(path)
            for items in paths:
                flat = [node for item in items for node in item]
                nodes = []
                for index, (position, kind) in enumerate(flat):
                    smooth = kind != OFFCURVE and (flat[index - 1][1] == OFFCURVE or flat[(index + 1) % len(flat)][1] == OFFCURVE) \
                        and _smooth(flat[index - 1][0], position, flat[(index + 1) % len(flat)][0])
                    nodes.append(GSNode(position, type=kind, smooth=smooth))
                path = GSPath()
                path.closed = True
                path.nodes = nodes
                layer.shapes.insert(len(layer.paths), path)
            changed += 1
    return changed


def build_source(package: Path, family: Family, rounded: bool = True):
    """GSFont for `package` with every corner component placed, plus a report.

    The baseline (`rounded=False`) only places the components, exactly as
    upstream's build does. The rounded source also softens every serif, erases
    open corners and overlaps, caps cut terminals, then runs the shared
    stem-relative fillets for every remaining exposed corner.
    """
    shape = family.soft_serif
    with tempfile.TemporaryDirectory() as temporary:
        copy_path = Path(temporary) / package.name
        shutil.copytree(package, copy_path)
        stats = expand_package(package, copy_path, tip=shape.tip if rounded else None)
        font = GSFont(str(copy_path))
    if len(font.masters) != 1:
        raise GeometryError(f"{family.name} expects one master; got {len(font.masters)}")
    if not rounded:
        return font, {"expansion": dict(stats)}
    # Placed into every glyph; the open component outlines themselves are not exported.
    for name in [glyph.name for glyph in font.glyphs if glyph.name.startswith(("_corner.", "_cap."))]:
        del font.glyphs[name]
    stats["overlaps_removed"] = remove_overlaps(font)
    stems = measure_stems(font, OutlineContext(font), family.profile)
    cap_terminals(font, stems, family.profile, shape.cap, shape.cut, stats)
    font, report = round_font(font, family)
    report["algorithm"] = "soft-serif-v1+" + report["algorithm"]
    report["soft_serif"] = {"tip": shape.tip, "cap": shape.cap, "cut": shape.cut, **stats}
    return font, report


def static_variant(info: dict, instance: dict) -> dict:
    """The source as this named instance exports it: its Rename Glyphs and Replace
    Feature applied, as Glyphs (and upstream's static_source) does for statics."""
    upstream = upstream_module("build_geist_serif", "build-geist-serif.py")
    data = copy.deepcopy(info)
    params = {p["name"]: p["value"] for p in instance.get("customParameters", [])}
    for feature in data.get("features", []):
        feature["code"] = upstream.strip_variable_code(feature.get("code", ""))
    if "Replace Feature" in params:
        tag, code = params["Replace Feature"].split(";", 1)
        feature = next(x for x in data["features"] if x.get("tag") == tag.strip())
        feature["code"] = code.strip() + "\n"
    swaps = dict(rule.split("=") for rule in params.get("Rename Glyphs", []))
    swaps.update({b: a for a, b in list(swaps.items())})
    glyphs = {glyph["glyphname"]: glyph for glyph in data["glyphs"]}
    for a, b in swaps.items():
        if a < b:
            # The pair trades drawings and kerning groups; references follow by name.
            for key in ("layers", "kernLeft", "kernRight"):
                va, vb = glyphs[a].pop(key, None), glyphs[b].pop(key, None)
                if vb is not None:
                    glyphs[a][key] = vb
                if va is not None:
                    glyphs[b][key] = va
    for name in swaps:
        for layer in glyphs[name]["layers"]:
            for shape in layer.get("shapes", []):
                if shape.get("ref") in swaps:
                    shape["ref"] = swaps[shape["ref"]]
    data["kerningLTR"] = {master: {swaps.get(a, a): {swaps.get(b, b): v for b, v in right.items()}
                                   for a, right in pairs.items()}
                          for master, pairs in data.get("kerningLTR", {}).items()}
    return data


def _set_name(font, name_id, value):
    names = font["name"]
    names.removeNames(nameID=name_id)
    names.setName(value, name_id, 3, 1, 0x409)


def _fontmake(source, fmt, output, env, *extra):
    command = [sys.executable, "-m", "fontmake", "-g", str(source), "-o", *fmt, "--output-dir", str(output),
               "--verbose", "ERROR", *extra]
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, check=True, env=env)


def finish_variable(path, dest, family: Family, prefix, family_name):
    """Upstream's variable-font finishing, with this family's names."""
    upstream = upstream_module("build_geist_serif", "build-geist-serif.py")
    font = TTFont(path)
    if "gvar" in font:
        del font["gvar"]  # all zero: the axis only swaps glyphs
    upstream.tidy(font)
    parts = upstream.component_parts(font)
    removeOverlaps(font)  # serifs overlap stems; fontmake only removes overlaps in statics
    upstream.tidy_contours(font)
    upstream.recompose(font, parts)
    upstream.add_meta(font)
    # Unhinted, as the other families' variable fonts: gasp and prep for smooth
    # rendering, as gftools' builder adds to them.
    fix_unhinted_font(font)
    names = font["name"]
    vendor = font["OS/2"].achVendID.strip()
    _set_name(font, 3, f"{font['head'].fontRevision:.3f};{vendor};{prefix}-Regular")
    _set_name(font, 4, f"{family_name} Regular")
    for name_id in (16, 17):
        names.removeNames(nameID=name_id)
    _set_name(font, 25, prefix)
    for instance in font["fvar"].instances:
        instance.postscriptNameID = names.addMultilingualName(
            {"en": f"{prefix}-{names.getDebugName(instance.subfamilyNameID)}"}, ttFont=font, windows=True, mac=False)
    stat = font["STAT"].table  # glyphsLib adds an ital axis the font does not have
    keep = [i for i, axis in enumerate(stat.DesignAxisRecord.Axis) if axis.AxisTag == family.axis[0]]
    dropped = {axis.AxisNameID for i, axis in enumerate(stat.DesignAxisRecord.Axis) if i not in keep}
    dropped |= {value.ValueNameID for value in stat.AxisValueArray.AxisValue if value.AxisIndex not in keep}
    stat.DesignAxisRecord.Axis = [stat.DesignAxisRecord.Axis[i] for i in keep]
    stat.DesignAxisCount = len(keep)
    stat.AxisValueArray.AxisValue = [value for value in stat.AxisValueArray.AxisValue if value.AxisIndex in keep]
    for value in stat.AxisValueArray.AxisValue:
        value.AxisIndex = 0
    stat.AxisValueCount = len(stat.AxisValueArray.AxisValue)
    used = {value.ValueNameID for value in stat.AxisValueArray.AxisValue} | {
        axis.AxisNameID for axis in stat.DesignAxisRecord.Axis}
    for name_id in dropped - used:
        names.removeNames(nameID=name_id)
    font.save(dest)


def finish_static(path, dest, prefix, family_name, style):
    """Upstream's static finishing: one family per shape, Regular as its style."""
    upstream = upstream_module("build_geist_serif", "build-geist-serif.py")
    font = TTFont(path)
    if "glyf" in font:
        upstream.tidy(font)
    else:
        compact(font, 9)
    upstream.add_meta(font)
    legacy = family_name if style == "Regular" else f"{family_name} {style}"
    vendor = font["OS/2"].achVendID.strip()
    _set_name(font, 1, legacy)
    _set_name(font, 2, "Regular")
    _set_name(font, 4, f"{family_name} {style}")
    _set_name(font, 16, family_name)
    _set_name(font, 17, style)
    _set_name(font, 3, f"{font['head'].fontRevision:.3f};{vendor};{prefix}-{style}")
    _set_name(font, 6, f"{prefix}-{style}")
    if "CFF " in font:
        top = font["CFF "].cff
        top.fontNames = [f"{prefix}-{style}"]
        top.topDictIndex[0].FullName = f"{family_name} {style}"
        top.topDictIndex[0].FamilyName = legacy
    font.save(dest)


def apply_collision_guard(directory: Path, family: Family, prefix: str, reference: Path) -> dict:
    """Open every pair the soft serif tips brought closer than Geist Serif had it.

    Each TTF is measured against the reference file of the same style; the
    guard lookup goes into that TTF and its OTF (same glyph names and GPOS).
    Returns {file stem: [[left glyph, right glyph, units], ...]}.
    """
    min_gap = family.soft_serif.guard
    files = [(directory / "variable" / f"{family.variable_stem(prefix)}.ttf",
              reference / f"{family.variable_stem(family.upstream_key)}.ttf", None)]
    files += [(directory / "ttf" / f"{prefix}-{style.name}.ttf",
               reference / f"{family.upstream_key}-{style.name}.ttf",
               directory / "otf" / f"{prefix}-{style.name}.otf") for style in family.styles]
    report = {}
    for ttf, upstream, otf in files:
        pairs = collisions.guard_pairs(collisions.pair_gaps(ttf, min_gap),
                                       collisions.pair_gaps(upstream, min_gap), min_gap)
        for path in filter(None, (ttf, otf)):
            font = TTFont(path)
            collisions.add_guard_lookup(font, pairs)
            font.save(path)
        report[ttf.stem] = [[a, b, units] for (a, b), units in sorted(pairs.items())]
        print(f"Collision guard {ttf.name}: {len(pairs)} pairs", flush=True)
    return report


def compile_fonts(source: Path, family: Family, prefix: str, family_name: str, env: dict,
                  workspace: Path, guard_report: Path | None = None) -> Path:
    """Compile one ELSH variable font and a TTF and OTF per named instance.

    With `guard_report`, the soft serif's collision guard is added against the
    vendored Geist Serif reference fonts and written there as JSON.
    """
    directory = workspace / "fonts"
    for kind in ("variable", "ttf", "otf"):
        (directory / kind).mkdir(parents=True, exist_ok=True)
    _fontmake(source, ["variable"], workspace / "vf", env)
    (built,) = (workspace / "vf").glob("*.ttf")
    finish_variable(built, directory / "variable" / f"{family.variable_stem(prefix)}.ttf",
                    family, prefix, family_name)
    with open(source, encoding="utf-8") as stream:
        info = openstep_plist.load(stream, use_numbers=True)
    instances = {instance["name"]: instance for instance in info["instances"]
                 if instance.get("type") != "variable"}
    for style in family.styles:
        work = workspace / style.name
        work.mkdir()
        variant = work / source.name
        with open(variant, "w", encoding="utf-8") as stream:
            openstep_plist.dump(static_variant(info, instances[style.name]), stream)
        _fontmake(variant, ["ttf", "otf"], work / "out", env, "--overlaps-backend", "pathops")
        for kind in ("ttf", "otf"):
            (built,) = (work / "out").glob(f"*.{kind}")
            finish_static(built, directory / kind / f"{prefix}-{style.name}.{kind}", prefix, family_name,
                          style.name)
    if guard_report:
        reference = ROOT / "sources" / family.key / "upstream" / "reference"
        report = apply_collision_guard(directory, family, prefix, reference)
        guard_report.write_text(json.dumps({"min_gap": family.soft_serif.guard, "fonts": report},
                                           indent=2) + "\n")
    return directory


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path, help="required unless --baseline")
    parser.add_argument("--family", default="GoeistSerif",
                        choices=sorted(key for key, family in FAMILIES.items() if family.element_shapes))
    parser.add_argument("--baseline", action="store_true", help="Place components only; no rounding")
    args = parser.parse_args(argv)
    if not args.baseline and not args.report:
        parser.error("--report is required unless --baseline")
    try:
        font, report = build_source(args.source, FAMILIES[args.family], rounded=not args.baseline)
    except GeometryError as error:
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps({"status": "failed", "source": str(args.source),
                                               "error": str(error)}, indent=2) + "\n")
        parser.exit(1, f"Rounding failed: {error}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    font.save(str(args.output))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        report.update(status="complete", source=str(args.source), output=str(args.output))
        args.report.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
