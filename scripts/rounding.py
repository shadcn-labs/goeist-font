#!/usr/bin/env python3
"""Build editable Goeist family sources with compatible, stem-relative cubic fillets.

All geometry is computed in source units, without a Glyphs.app filter. Outlines
are not overlap-removed: winding tests distinguish exposed ink corners from
construction corners, and original components and interpolation correspondence
are retained. Fractional coordinates deliberately survive source serialization.
Fillet radii come from the family's profile in families.py.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import median

from glyphsLib import GSFont
from glyphsLib.classes import CURVE, LINE, OFFCURVE, GSFeature, GSNode
import pathops

from families import FAMILIES, FONT_VERSION, FONT_VERSION_STRING, SOFT, Family, Profile

EPSILON = 1e-9
FLATNESS = 0.08
# Designer (name ID 9) is the first AUTHORS.txt entry; Goeist is developed under Shadcn Labs.
MANUFACTURER = "Shadcn Labs"
MANUFACTURER_URL = "https://shadcn-labs.com/font"
DESIGNER_URL = "https://github.com/Aniket-508"
# OS/2 achVendID for Shadcn Labs (not yet in Microsoft's vendor registry).
VENDOR_ID = "CNLB"


class GeometryError(ValueError):
    """A source outline cannot be transformed safely; never silently discard it."""


def add(a, b, scale=1.0):
    return a[0] + b[0] * scale, a[1] + b[1] * scale


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def unit(v):
    length = math.hypot(*v)
    if length < EPSILON:
        raise GeometryError("Zero-length tangent")
    return v[0] / length, v[1] / length


def lerp(a, b, t):
    return add(a, sub(b, a), t)


def point(node):
    return float(node.position.x), float(node.position.y)


def split(points, t):
    """de Casteljau subdivision; lines and cubics share the same code."""
    rows = [list(points)]
    while len(rows[-1]) > 1:
        rows.append([lerp(a, b, t) for a, b in zip(rows[-1], rows[-1][1:])])
    return tuple(row[0] for row in rows), tuple(row[-1] for row in reversed(rows))


def section(points, start, end):
    if not 0 <= start <= end <= 1:
        raise GeometryError(f"Invalid segment interval {start}, {end}")
    left = split(points, end)[0] if end < 1 else points
    return split(left, start / end)[1] if start > 0 and end > 0 else left


def evaluate(points, t):
    return split(points, t)[0][-1]


def tangent(points, end=False):
    p = points[-1] if end else points[0]
    candidates = reversed(points[:-1]) if end else iter(points[1:])
    for q in candidates:
        v = sub(p, q) if end else sub(q, p)
        if math.hypot(*v) > EPSILON:
            return unit(v)
    raise GeometryError("Segment has no nonzero tangent")


def flatten(points, tolerance=FLATNESS):
    """Return (parameter, position) pairs, bounding chord error adaptively."""
    output = [(0.0, points[0])]

    def visit(curve, t0, t1, depth):
        chord = sub(curve[-1], curve[0])
        length = math.hypot(*chord)
        error = max((abs(cross(sub(p, curve[0]), chord)) / length
                     if length > EPSILON else math.dist(p, curve[0]))
                    for p in curve[1:-1]) if len(curve) > 2 else 0
        # Length excess catches collinear reversing handles, not just flatness.
        excess = sum(math.dist(a, b) for a, b in zip(curve, curve[1:])) - length
        if depth >= 18 or (error <= tolerance and excess <= tolerance):
            output.append((t1, curve[-1]))
            return
        left, right = split(curve, 0.5)
        middle = (t0 + t1) / 2
        visit(left, t0, middle, depth + 1)
        visit(right, middle, t1, depth + 1)

    visit(points, 0, 1, 0)
    return output


@dataclass
class Segment:
    points: tuple
    samples: list
    lengths: list
    length: float

    @classmethod
    def make(cls, points):
        samples = flatten(points)
        lengths = [0.0]
        for (_, a), (_, b) in zip(samples, samples[1:]):
            lengths.append(lengths[-1] + math.dist(a, b))
        return cls(tuple(points), samples, lengths, lengths[-1])

    def parameter(self, distance):
        distance = max(0, min(self.length, distance))
        for i in range(1, len(self.samples)):
            if self.lengths[i] >= distance:
                span = self.lengths[i] - self.lengths[i - 1]
                fraction = (distance - self.lengths[i - 1]) / span if span else 0
                return self.samples[i - 1][0] + fraction * (
                    self.samples[i][0] - self.samples[i - 1][0])
        return 1.0


class Contour:
    def __init__(self, path):
        self.path = path
        self.indices = [i for i, node in enumerate(path.nodes) if node.type != OFFCURVE]
        self.nodes = [path.nodes[i] for i in self.indices]
        self.segments = []
        if not path.closed:
            raise GeometryError("Open outlines need stroke expansion before rounding")
        if len(self.indices) < 2:
            raise GeometryError("Closed contour has fewer than two on-curve points")
        count = len(path.nodes)
        for i, start in enumerate(self.indices):
            end = self.indices[(i + 1) % len(self.indices)]
            off = []
            cursor = (start + 1) % count
            while cursor != end:
                off.append(point(path.nodes[cursor]))
                cursor = (cursor + 1) % count
            endpoint = path.nodes[end]
            if endpoint.type == LINE and not off:
                pts = (point(path.nodes[start]), point(endpoint))
            elif endpoint.type == CURVE and len(off) == 2:
                pts = (point(path.nodes[start]), *off, point(endpoint))
            else:
                raise GeometryError(f"Unsupported segment {endpoint.type} with {len(off)} handles")
            self.segments.append(Segment.make(pts))

    def polygon(self):
        result = []
        for segment in self.segments:
            result.extend(p for _, p in segment.samples[:-1])
        return result


def winding(polygons, p):
    result = 0
    for polygon in polygons:
        for a, b in zip(polygon, polygon[1:] + polygon[:1]):
            side = cross(sub(b, a), sub(p, a))
            if a[1] <= p[1] < b[1] and side > 0:
                result += 1
            elif b[1] <= p[1] < a[1] and side < 0:
                result -= 1
    return result


class InkGeometry(list):
    """Flattened edges for measurements, exact Béziers for ink containment."""

    def __init__(self):
        super().__init__()
        self.ink = pathops.Path()


def filled(polygons, p):
    if isinstance(polygons, InkGeometry):
        return polygons.ink.contains(p)
    return winding(polygons, p) != 0


def transform_polygon(polygon, matrix):
    xx, xy, yx, yy, dx, dy = matrix
    return [(xx * x + yx * y + dx, xy * x + yy * y + dy) for x, y in polygon]


class OutlineContext:
    """Immutable source geometry, including transformed component ink."""

    def __init__(self, font):
        self.font = font
        self.cache = {}

    def polygons(self, glyph, layer, stack=()):
        key = (glyph.name, layer.layerId)
        if key in self.cache:
            return self.cache[key]
        if glyph.name in stack:
            raise GeometryError(f"Component cycle: {' -> '.join((*stack, glyph.name))}")
        result = InkGeometry()
        for path in layer.paths:
            contour = Contour(path)
            result.append(contour.polygon())
            result.ink.moveTo(*contour.segments[0].points[0])
            for segment in contour.segments:
                if len(segment.points) == 2:
                    result.ink.lineTo(*segment.points[-1])
                else:
                    result.ink.cubicTo(*(coordinate for p in segment.points[1:] for coordinate in p))
            result.ink.close()
        for component in layer.components:
            base = self.font.glyphs[component.name]
            if base is None:
                raise GeometryError(f"Missing component {component.name} in {glyph.name}")
            base_layer = base.layers[layer.layerId] or base.layers[layer.associatedMasterId]
            if base_layer is None:
                raise GeometryError(f"Missing component layer {component.name}/{layer.layerId}")
            if component.smartComponentValues:
                raise GeometryError(f"Smart component {component.name} requires interpolation")
            base_geometry = self.polygons(base, base_layer, (*stack, glyph.name))
            result.ink.addPath(base_geometry.ink.transform(*component.transform))
            result.extend(transform_polygon(polygon, component.transform) for polygon in base_geometry)
        self.cache[key] = result
        return result


def scan_stems(polygons, y, upm):
    crossings = sorted(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
                       for polygon in polygons
                       for a, b in zip(polygon, polygon[1:] + polygon[:1])
                       if (a[1] <= y < b[1]) or (b[1] <= y < a[1]))
    return [right - left for left, right in zip(crossings, crossings[1:])
            if upm * 0.008 < right - left < upm * 0.27
            and filled(polygons, ((left + right) / 2, y))]


def measure_stems(font, context, profile: Profile):
    """Use real vertical ink widths, not a single arbitrary family-wide radius."""
    measurements = {}
    for master in font.masters:
        samples = []
        for name in ("H", "I", "n", "h"):
            glyph = font.glyphs[name]
            if glyph is None or glyph.layers[master.id] is None:
                continue
            polygons = context.polygons(glyph, glyph.layers[master.id])
            height = master.capHeight if name.isupper() else master.xHeight
            for fraction in (0.2, 0.72, 0.82):
                samples.extend(scan_stems(polygons, height * fraction, font.upm))
        if not samples:
            raise GeometryError(f"Cannot measure vertical stems for {master.name}")
        measurements[master.id] = {
            "name": master.name, "weight": master.weightValue,
            "stem": median(samples), "samples": samples,
            "terminal_radius": median(samples) * profile.terminal,
            "acute_radius": median(samples) * profile.acute,
        }
    return measurements


@dataclass
class Corner:
    start: float
    end: float
    curve: tuple
    radius: float


def ink_side(polygons, position, direction, probe):
    normal = (-direction[1], direction[0])
    left = filled(polygons, add(position, normal, probe))
    right = filled(polygons, add(position, normal, -probe))
    return 1 if left and not right else -1 if right and not left else 0


def classify_corner(contour, index, polygons, stem, profile: Profile = SOFT):
    node = contour.nodes[index]
    if node.smooth:
        return "smooth", None
    incoming = contour.segments[index - 1]
    outgoing = contour.segments[index]
    if min(incoming.length, outgoing.length) < EPSILON:
        return "zero_length_construction_edge", None
    a, b = tangent(incoming.points, True), tangent(outgoing.points)
    turn = math.atan2(cross(a, b), dot(a, b))
    if abs(turn) < math.radians(7):
        return "tangent_or_nearly_straight", None
    if abs(turn) > math.radians(175):
        return "reversing_construction_corner", None
    probe = max(0.22, min(stem * 0.018, min(incoming.length, outgoing.length) * 0.08))
    distance = min(stem * 0.08, incoming.length * 0.3, outgoing.length * 0.3)
    before = evaluate(incoming.points, incoming.parameter(incoming.length - distance))
    after = evaluate(outgoing.points, outgoing.parameter(distance))
    side_in = ink_side(polygons, before, tangent(incoming.points, True), probe)
    side_out = ink_side(polygons, after, tangent(outgoing.points), probe)
    if not side_in or not side_out or side_in != side_out:
        return "hidden_or_overlapping_construction_corner", None
    if turn * side_in < 0:
        return "concave_ink_join_or_counter", None
    radius = stem * (profile.terminal if abs(turn) <= math.radians(110) else profile.acute)
    return "convex", (radius, abs(turn))


def convex_polygon_width(contour):
    """Minimum caliper width of an all-line convex contour, else None.

    Under a round nib such a contour (dot, bar, slash, comma) is a stadium or a
    circle whose radius is half this width.
    """
    if any(len(segment.points) != 2 for segment in contour.segments):
        return None
    points = [segment.points[0] for segment in contour.segments if segment.length > EPSILON]
    edges = [sub(q, p) for p, q in zip(points, points[1:] + points[:1])]
    turns = [cross(u, v) for u, v in zip(edges, edges[1:] + edges[:1])]
    if len(edges) < 3 or not (all(t >= -EPSILON for t in turns) or all(t <= EPSILON for t in turns)):
        return None
    return min(max(abs(cross(unit(edge), sub(point, origin))) for point in points)
               for origin, edge in zip(points, edges))


def make_corner(contour, index, radius, angle, circular=False):
    incoming, outgoing = contour.segments[index - 1], contour.segments[index]
    trim = radius * math.tan(angle / 2)
    limit_in, limit_out = incoming.length * 0.48, outgoing.length * 0.48
    if circular:
        # A round tool leaves circular arcs: shrink the radius until both
        # trims fit, so short stroke ends become semicircles, not ellipses.
        trim_in = trim_out = min(trim, limit_in, limit_out)
        radius = trim_in / math.tan(angle / 2)
    else:
        trim_in, trim_out = min(trim, limit_in), min(trim, limit_out)
    t_in = incoming.parameter(incoming.length - trim_in)
    t_out = outgoing.parameter(trim_out)
    left = section(incoming.points, 0, t_in)
    right = section(outgoing.points, t_out, 1)
    p, q = left[-1], right[0]
    a, b = tangent(left, True), tangent(right)
    denominator = cross(a, b)
    if abs(denominator) < EPSILON:
        raise GeometryError("Fillet tangents do not intersect")
    distance_a = cross(sub(q, p), b) / denominator
    distance_b = cross(a, sub(q, p)) / denominator
    if min(distance_a, distance_b) <= EPSILON:
        raise GeometryError("Fillet tangent intersection is outside the corner")
    angle = math.acos(max(-1, min(1, dot(a, b))))
    alpha = (4 / 3) * math.tan(angle / 4) / math.tan(angle / 2)
    # These handles align exactly with the retained de Casteljau subcurves.
    curve = (p, add(p, a, alpha * distance_a), add(q, b, -alpha * distance_b), q)
    return Corner(t_in, t_out, curve, radius)


def proper_intersection(a, b, c, d):
    ab, cd = sub(b, a), sub(d, c)
    x, y = cross(ab, sub(c, a)), cross(ab, sub(d, a))
    z, w = cross(cd, sub(a, c)), cross(cd, sub(b, c))
    return x * y < -1e-12 and z * w < -1e-12


def safe_corner(corner, contour, index, polygons):
    curve = [p for _, p in flatten(corner.curve)]
    # Every point of the new boundary must remain in original ink. Check a
    # second dense parameter grid because a nearly flat cubic flattens sparsely.
    if not all(filled(polygons, evaluate(corner.curve, i / 24)) for i in range(1, 24)):
        return False
    for j, segment in enumerate(contour.segments):
        if j in (index - 1, index, (index - 1) % len(contour.segments)):
            continue
        line = [p for _, p in segment.samples]
        if any(proper_intersection(a, b, c, d)
               for a, b in zip(curve, curve[1:])
               for c, d in zip(line, line[1:])):
            return False
    return True


def prepare_corners(contour, polygons, stem, profile: Profile = SOFT):
    corners, reasons, exceptions = {}, Counter(), []
    width = convex_polygon_width(contour) if profile.stadium else None
    stadium = min(width / 2, profile.stadium * stem) if width else None
    for index in range(len(contour.nodes)):
        reason, proposal = classify_corner(contour, index, polygons, stem, profile)
        reasons[reason] += 1
        if proposal is None:
            if reason in {"zero_length_construction_edge", "reversing_construction_corner",
                          "hidden_or_overlapping_construction_corner"}:
                exceptions.append({"node": contour.indices[index], "reason": reason})
            continue
        radius, angle = proposal
        if stadium:
            reasons["stadium"] += 1
            radius = max(radius, stadium)
        failure = None
        for attempt in range(9):
            try:
                corner = make_corner(contour, index, radius / 2 ** attempt, angle, profile.circular)
                if safe_corner(corner, contour, index, polygons):
                    corners[index] = corner
                    if attempt:
                        exceptions.append({"node": contour.indices[index],
                                           "reason": "local_radius_reduction",
                                           "factor": 2 ** -attempt})
                    break
                failure = "new boundary leaves original ink or intersects another edge"
            except GeometryError as error:
                failure = str(error)
        else:
            raise GeometryError(f"Cannot fillet node {contour.indices[index]}: {failure}")
    return corners, reasons, exceptions


def write_contour(contour, selected, corners):
    """Same selected on-curve indices means the same topology in every master.

    A hidden, smooth or tangent counterpart receives a zero-length compatible
    cubic, not a moved point. The explicit report records these support nodes.
    """
    nodes = []
    count = len(contour.nodes)
    for index, segment in enumerate(contour.segments):
        next_index = (index + 1) % count
        source = contour.nodes[next_index]
        start = corners[index].end if index in corners else 0
        end = corners[next_index].start if next_index in corners else 1
        retained = section(segment.points, start, end)
        for control in retained[1:-1]:
            nodes.append(GSNode(control, type=OFFCURVE))
        endpoint = copy.copy(source)
        endpoint._userData = copy.deepcopy(source._userData)
        endpoint.position = retained[-1]
        endpoint.type = CURVE if len(retained) == 4 else LINE
        if next_index in corners:
            endpoint.smooth = True
        nodes.append(endpoint)
        if next_index in selected:
            fillet = corners[next_index].curve if next_index in corners else (retained[-1],) * 4
            nodes.extend(GSNode(p, type=OFFCURVE) for p in fillet[1:3])
            nodes.append(GSNode(fillet[-1], type=CURVE, smooth=True))
    # Keep the first original on-curve as the cyclic starting correspondence.
    # The emitted list starts after it, identically in every compatible layer.
    contour.path.nodes = nodes


def design_layers(glyph, font):
    master_ids = {master.id for master in font.masters}
    return [layer for layer in glyph.layers
            if layer.layerId in master_ids or layer._is_bracket_layer() or layer._is_brace_layer()]


def layer_stem(layer, masters):
    """Interpolate the measured master stems for intermediate source layers."""
    if layer._is_brace_layer():
        weight = layer._brace_coordinates()[0]
        ordered = sorted(masters.values(), key=lambda item: item["weight"])
        if weight <= ordered[0]["weight"]:
            return ordered[0]["stem"]
        for left, right in zip(ordered, ordered[1:]):
            if weight <= right["weight"]:
                t = (weight - left["weight"]) / (right["weight"] - left["weight"])
                return left["stem"] + t * (right["stem"] - left["stem"])
        return ordered[-1]["stem"]
    key = layer.associatedMasterId or layer.layerId
    if key not in masters:
        raise GeometryError(f"Layer {layer.layerId} has no known master")
    return masters[key]["stem"]


def rename_metadata(font, family: Family):
    old_family = font.familyName
    font.familyName = family.name
    font.versionMajor, font.versionMinor = FONT_VERSION
    name_keys = {"familyName", "postscriptFontName", "postscriptFullName", "fileName",
                 "variableFontFamilyName", "variableFontName", "variableFileName",
                 "preferredFamilyName", "Name Table Entry"}
    property_keys = {"familyNames", "preferredFamilyNames", "postscriptFontName",
                     "postscriptFullName", "uniqueID", "versionString", "fullNames",
                     "variableFontFamilyName", "variableFontName"}
    is_italic = bool(font.masters) and all(
        "italic" in master.name.lower() or abs(master.italicAngle) > EPSILON
        for master in font.masters)
    for owner in (font, *font.masters, *font.instances):
        for parameter in owner.customParameters:
            if parameter.name in name_keys and isinstance(parameter.value, str):
                parameter.value = parameter.value.replace(old_family, family.name).replace(
                    family.upstream_key, family.key)
                if parameter.name in {"fileName", "variableFileName"} and is_italic:
                    parameter.value = parameter.value.replace(f"{family.key}[", f"{family.key}-Italic[")
        for prop in getattr(owner, "properties", []):
            if prop.key in property_keys:
                if prop.key == "versionString":
                    prop.value = f"Version {FONT_VERSION_STRING}"
                elif isinstance(prop.value, str):
                    prop.value = prop.value.replace(old_family, family.name)
                if prop._localized_values:
                    for language, value in prop._localized_values.items():
                        if isinstance(value, str):
                            prop._localized_values[language] = (
                                f"Version {FONT_VERSION_STRING}" if prop.key == "versionString"
                                else value.replace(old_family, family.name))
    author_file = Path(__file__).resolve().parent.parent / "AUTHORS.txt"
    author_record = next((line.strip() for line in author_file.read_text(encoding="utf-8").splitlines()
                          if line.strip() and not line.lstrip().startswith("#")), "")
    author = author_record.partition("<")[0].strip()
    if not author:
        raise GeometryError("AUTHORS.txt must identify the Goeist author")
    font.properties["descriptions"] = (
        f"{family.name} by {author}, developed under {MANUFACTURER}. "
        f"Rounded derivative of Vercel {family.upstream_label}. "
        f"Original design: {font.designer}. Original publishers and contributors: {font.manufacturer}. "
        "Upstream: https://github.com/vercel/geist-font. "
        "Not affiliated with or endorsed by Vercel, Inc."
    )
    font.designer = author
    font.manufacturer = MANUFACTURER
    # glyphsLib's setters do not replace existing localized values.
    for prop in font.properties:
        if prop.key in {"designers", "manufacturers"} and prop._localized_values:
            for language in prop._localized_values:
                prop._localized_values[language] = author if prop.key == "designers" else MANUFACTURER
    font.designerURL = DESIGNER_URL
    font.manufacturerURL = MANUFACTURER_URL
    # Replace Geist's inherited "VRCL" so Goeist names Shadcn Labs as its vendor.
    font.properties["vendorID"] = VENDOR_ID
    # Preserve the exact inherited notice (including every localized value).
    notice = f"Copyright 2026 {author} ({family.name} modifications and rounded outlines)"
    copyrights = [prop for prop in font.properties if prop.key == "copyrights"]
    if not copyrights:
        font.copyright = notice
    for prop in copyrights:
        if prop._localized_values:
            for language, value in prop._localized_values.items():
                if notice not in value:
                    prop._localized_values[language] = f"{notice}; {value}"
        elif notice not in prop.value:
            prop.value = f"{notice}; {prop.value}" if prop.value else notice
    # The inherited license and feature labels remain unchanged.


def add_automatic_ligatures(font):
    """Add the `liga` feature Glyphs.app generates from exported `a_b.liga` names.

    Longest sequences come first so `->>` wins over `->`. Applied identically to
    the unrounded baseline and the rounded source.
    """
    if any(feature.name == "liga" for feature in font.features):
        raise GeometryError("Source already defines liga; automatic ligatures would duplicate it")
    exported = {glyph.name for glyph in font.glyphs if glyph.export}
    rules = []
    for name in sorted(exported):
        parts = name[:-len(".liga")].split("_") if name.endswith(".liga") else []
        if len(parts) > 1 and all(part in exported for part in parts):
            rules.append((parts, name))
    if not rules:
        raise GeometryError("No exported `a_b.liga` glyphs to build liga from")
    rules.sort(key=lambda rule: (-len(rule[0]), rule[1]))
    feature = GSFeature("liga", "\n".join(f"sub {' '.join(parts)} by {name};" for parts, name in rules))
    feature.automatic = True
    stylistic = next((i for i, item in enumerate(font.features) if item.name.startswith("ss")),
                     len(font.features))
    font.features.insert(stylistic, feature)
    return len(rules)


def exact_geometry(glyph, font, codepoints):
    """True for glyphs (or `.suffix` alternates of glyphs) encoded in `codepoints`."""
    if not codepoints:
        return False
    base = font.glyphs[glyph.name.split(".")[0]] or glyph
    return any(int(code, 16) in codepoints for code in base.unicodes or ())


def round_font(original, family: Family = FAMILIES["Goeist"]):
    """Return a deep-copied GSFont plus a machine-readable geometry audit."""
    font = copy.deepcopy(original)
    context = OutlineContext(original)
    masters = measure_stems(original, context, family.profile)
    report = {
        "family": family.name, "version": FONT_VERSION_STRING, "upm": original.upm,
        "original_family": original.familyName,
        "original_version": f"{original.versionMajor}.{original.versionMinor:03d}",
        "algorithm": "exposed-convex-cubic-fillet-v1", "profile": family.profile.name,
        "flatness": FLATNESS,
        "masters": masters, "glyphs": [], "counts": Counter(), "exceptions": [],
        "coordinate_policy": "fractional source coordinates; no pre-cu2qu integer rounding",
    }
    for source_glyph, glyph in zip(original.glyphs, font.glyphs):
        layers = design_layers(glyph, font)
        item = {"name": glyph.name, "export": bool(glyph.export), "layers": [],
                "rounded_corners": 0, "compatible_support_cubics": 0}
        if exact_geometry(glyph, font, family.exact_geometry):
            item["exact_geometry"] = True
            report["counts"]["exact_geometry_glyphs"] += 1
            report["glyphs"].append(item)
            continue
        # Special alternate layers may have genuinely different topology. Group
        # by full shape signature, retaining correspondence within each group.
        groups = {}
        for layer in layers:
            signature = tuple(
                ("path", shape.closed, tuple(n.type for n in shape.nodes))
                if hasattr(shape, "nodes") else ("component", shape.name)
                for shape in layer.shapes)
            groups.setdefault(signature, []).append(layer)
        master_ids = {master.id for master in font.masters}
        master_signatures = [signature for signature, group in groups.items()
                             if any(layer.layerId in master_ids for layer in group)]
        if len(master_signatures) > 1:
            # Do not manufacture compatibility for an incompatible upstream
            # design: that needs an explicit source correction, not reordering.
            raise GeometryError(f"{glyph.name}: original master shape topology is incompatible")
        for group in groups.values():
            prepared = []
            for layer in group:
                source_layer = source_glyph.layers[layer.layerId]
                polygons = context.polygons(source_glyph, source_layer)
                contours = [Contour(path) for path in layer.paths]
                decisions = []
                entry = {"id": layer.layerId, "name": layer.name, "paths": len(contours),
                         "width": layer.width, "rounded_corners": 0,
                         "nodes_before": sum(len(path.nodes) for path in layer.paths),
                         "components": len(layer.components), "anchors": len(layer.anchors),
                         "compatible_support_cubics": 0, "classifications": Counter()}
                for path_index, contour in enumerate(contours):
                    try:
                        corners, reasons, reductions = prepare_corners(
                            contour, polygons, layer_stem(layer, masters), family.profile)
                    except GeometryError as error:
                        raise GeometryError(f"{glyph.name}/{layer.name}/path {path_index}: {error}") from error
                    decisions.append(corners)
                    entry["classifications"].update(reasons)
                    for reduction in reductions:
                        report["exceptions"].append({"glyph": glyph.name, "layer": layer.layerId,
                                                     "path": path_index,
                                                     **reduction})
                prepared.append((contours, decisions, entry))
            for path_index in range(len(prepared[0][0])):
                selected = set().union(*(decisions[path_index] for _, decisions, _ in prepared))
                for contours, decisions, entry in prepared:
                    corners = decisions[path_index]
                    if selected:
                        write_contour(contours[path_index], selected, corners)
                    active = len(corners)
                    support = len(selected) - active
                    entry["rounded_corners"] += active
                    entry["compatible_support_cubics"] += support
                    if support:
                        report["exceptions"].append({"glyph": glyph.name, "layer": entry["id"],
                            "path": path_index, "reason": "compatible_unmoved_counterparts",
                            "nodes": [contours[path_index].indices[i] for i in sorted(selected - corners.keys())]})
            for contours, _, entry in prepared:
                entry["nodes_after"] = sum(len(contour.path.nodes) for contour in contours)
                item["layers"].append(entry)
                item["rounded_corners"] += entry["rounded_corners"]
                item["compatible_support_cubics"] += entry["compatible_support_cubics"]
                report["counts"].update(entry["classifications"])
                report["counts"]["rounded_corners"] += entry["rounded_corners"]
                report["counts"]["compatible_support_cubics"] += entry["compatible_support_cubics"]
                report["counts"]["design_layers"] += 1
                report["counts"]["paths"] += entry["paths"]
                report["counts"]["nodes_before"] += entry["nodes_before"]
                report["counts"]["nodes_after"] += entry["nodes_after"]
                report["counts"]["components"] += entry["components"]
                report["counts"]["anchors"] += entry["anchors"]
        report["glyphs"].append(item)
    rename_metadata(font, family)
    if family.automatic_ligatures:
        report["automatic_ligatures"] = add_automatic_ligatures(font)
    report["counts"]["glyphs"] = len(font.glyphs)
    report["counts"]["exported_glyphs"] = sum(bool(glyph.export) for glyph in font.glyphs)
    return font, report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--family", default="Goeist", choices=sorted(FAMILIES))
    args = parser.parse_args(argv)
    try:
        font, report = round_font(GSFont(args.source), FAMILIES[args.family])
    except GeometryError as error:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps({"status": "failed", "source": str(args.source),
                                          "error": str(error)}, indent=2) + "\n")
        parser.exit(1, f"Rounding failed: {error}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    font.save(args.output)
    report.update(status="complete", source=str(args.source), output=str(args.output))
    args.report.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
