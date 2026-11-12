"""Focused source-geometry regressions; run with unittest discovery."""
import copy
import dataclasses
import math
import sys
import tempfile
import unittest
from pathlib import Path

from glyphsLib import GSFont, load
from glyphsLib.classes import (
    CURVE, LINE, OFFCURVE, GSAnchor, GSComponent, GSFeature, GSFontMaster,
    GSGlyph, GSInstance, GSLayer, GSNode, GSPath,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from families import FAMILIES, FONT_VERSION  # noqa: E402
from rounding import (  # noqa: E402
    Contour, GeometryError, OutlineContext, add_automatic_ligatures, classify_corner, cross, dot,
    evaluate, filled,
    point, prepare_corners, proper_intersection, round_font,
    tangent, write_contour,
)


def polygon(points):
    path = GSPath()
    path.closed = True
    path.nodes = [GSNode(p, type=LINE) for p in points]
    return path


def rectangle(width=100, height=100, x=0, y=0, clockwise=False):
    points = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
    return polygon(list(reversed(points)) if clockwise else points)


def round_path(path, stem=20, others=()):
    contour = Contour(path)
    font = GSFont()
    glyph = GSGlyph("fixture")
    layer = GSLayer()
    layer.layerId = "fixture"
    layer.shapes.extend((path, *others))
    glyph.layers.append(layer)
    font.glyphs.append(glyph)
    polygons = OutlineContext(font).polygons(glyph, layer)
    corners, reasons, exceptions = prepare_corners(contour, polygons, stem)
    write_contour(contour, set(corners), corners)
    return corners, reasons, exceptions


def source_font():
    font = GSFont()
    font.format_version = 3
    font.familyName = "Geist"
    font.versionMajor, font.versionMinor = 1, 900
    font.upm = 1000
    for name, weight in (("Thin", 100), ("Regular", 400), ("Black", 900)):
        master = GSFontMaster()
        master.id = name
        master.name = name
        master.axes = [weight]
        master.capHeight = 710
        master.xHeight = 530
        font.masters.append(master)
    for name in ("H", "O", "acutecomb", "Aacute"):
        glyph = GSGlyph(name)
        glyph.export = name != "acutecomb"
        glyph.leftKerningGroup = "H"
        glyph.rightKerningGroup = "O"
        for master, width in zip(font.masters, (32, 84, 194)):
            layer = GSLayer()
            layer.layerId = master.id
            layer.associatedMasterId = master.id
            layer.width = 600
            layer.anchors.append(GSAnchor("top", (300, 710)))
            if name == "H":
                layer.paths.append(rectangle(width, 710))
            elif name == "O":
                layer.paths.append(rectangle(400, 710))
                layer.paths.append(rectangle(180, 400, 100, 150, clockwise=True))
            elif name == "acutecomb":
                layer.paths.append(polygon([(0, 0), (40, 0), (100, 120), (60, 120)]))
            else:
                layer.components.append(GSComponent("H"))
                layer.components.append(GSComponent("acutecomb", offset=(100, 750)))
            glyph.layers.append(layer)
        font.glyphs.append(glyph)
    feature = GSFeature("ss01", "sub H by O;")
    font.features.append(feature)
    instance = GSInstance()
    instance.name = "Regular"
    instance.customParameters["fileName"] = "Geist-Regular"
    font.instances.append(instance)
    font.kerning = {font.masters[0].id: {"H": {"O": -25}}}
    return font


class RoundedGeometryTests(unittest.TestCase):
    def test_square_has_real_cubic_arcs_and_tangent_joins(self):
        path = rectangle()
        corners, _, _ = round_path(path)
        self.assertEqual(len(corners), 4)
        self.assertEqual(sum(n.type == CURVE for n in path.nodes), 4)
        contour = Contour(path)
        for index, node in enumerate(contour.nodes):
            self.assertTrue(node.smooth)
            a = tangent(contour.segments[index - 1].points, True)
            b = tangent(contour.segments[index].points)
            self.assertAlmostEqual(cross(a, b), 0, places=10)
            self.assertGreater(dot(a, b), 0.999999)
        arc = corners[1].curve
        midpoint = evaluate(arc, 0.5)
        chord_midpoint = ((arc[0][0] + arc[-1][0]) / 2,
                          (arc[0][1] + arc[-1][1]) / 2)
        self.assertGreater(math.dist(midpoint, chord_midpoint), 1)
        rounded = [contour.polygon()]
        self.assertFalse(filled(rounded, (99, 1)))
        self.assertTrue(filled(rounded, (50, 50)))

    def test_thin_heavy_and_intermediate_have_identical_topology(self):
        font = source_font()
        brace = copy.deepcopy(font.glyphs["H"].layers["Black"])
        brace.layerId = "intermediate"
        brace.attributes["coordinates"] = [801]
        brace.name = "{801}"
        font.glyphs["H"].layers.append(brace)
        rounded, report = round_font(font)
        layers = rounded.glyphs["H"].layers
        signatures = [tuple(node.type for node in layer.paths[0].nodes) for layer in layers]
        self.assertTrue(all(signature == signatures[0] for signature in signatures))
        self.assertGreater(report["masters"]["Black"]["terminal_radius"],
                           report["masters"]["Thin"]["terminal_radius"] * 4)
        self.assertTrue(any(layer["id"] == "intermediate"
                            and layer["rounded_corners"] == 4
                            for glyph in report["glyphs"] if glyph["name"] == "H"
                            for layer in glyph["layers"]))
        # More ink is removed from a heavy terminal, without using UPM alone.
        thin_max = max(n.position.y for n in layers["Thin"].paths[0].nodes
                       if n.type == CURVE and n.position.y < 100)
        heavy_max = max(n.position.y for n in layers["Black"].paths[0].nodes
                        if n.type == CURVE and n.position.y < 200)
        self.assertGreater(heavy_max, thin_max * 4)

    def test_short_edges_remain_ordered_and_do_not_self_intersect(self):
        path = rectangle(2, 100)
        corners, _, _ = round_path(path, stem=40)
        self.assertEqual(len(corners), 4)
        contour = Contour(path)
        for segment in contour.segments:
            self.assertGreater(segment.length, 0)
        points = contour.polygon()
        edges = list(zip(points, points[1:] + points[:1]))
        for i, (a, b) in enumerate(edges):
            for j, (c, d) in enumerate(edges):
                if abs(i - j) > 1 and {i, j} != {0, len(edges) - 1}:
                    self.assertFalse(proper_intersection(a, b, c, d))
        self.assertTrue(filled([points], (1, 50)))

    def test_existing_curve_is_trimmed_without_losing_tangency(self):
        path = polygon([(0, 0), (100, 0)])
        path.nodes.extend([GSNode((100, 30), type=OFFCURVE),
                           GSNode((120, 80), type=OFFCURVE),
                           GSNode((100, 100), type=CURVE),
                           GSNode((0, 100), type=LINE)])
        original_curve = Contour(path).segments[1].points
        corners, _, _ = round_path(path, stem=20)
        self.assertIn(1, corners)
        trimmed_point = evaluate(original_curve, corners[1].end)
        self.assertLess(math.dist(trimmed_point, corners[1].curve[-1]), 1e-8)
        right = Contour(path)
        for index, node in enumerate(right.nodes):
            if node.smooth:
                self.assertAlmostEqual(cross(tangent(right.segments[index - 1].points, True),
                                             tangent(right.segments[index].points)), 0, places=8)

    def test_curved_terminal_keeps_a_real_fillet_inside_exact_ink(self):
        source = Path(__file__).resolve().parents[1] / "sources/Goeist/upstream/Geist.glyphspackage"
        font = GSFont(source)
        glyph = font.glyphs["C"]
        layer = glyph.layers[font.masters[0].id]
        contour = Contour(copy.deepcopy(layer.paths[0]))
        polygons = OutlineContext(font).polygons(glyph, layer)
        terminal = contour.indices.index(16)
        corners, _, _ = prepare_corners(contour, polygons, 32)
        self.assertIn(terminal, corners)
        self.assertGreater(corners[terminal].radius, 10)
        self.assertTrue(all(filled(polygons, evaluate(corners[terminal].curve, i / 24))
                            for i in range(1, 24)))

    def test_counter_widths_features_components_and_input_survive(self):
        font = source_font()
        original_counter = [point(n) for n in font.glyphs["O"].layers["Thin"].paths[1].nodes]
        rounded, report = round_font(font)
        self.assertEqual(rounded.familyName, "Goeist")
        self.assertEqual((rounded.versionMajor, rounded.versionMinor), FONT_VERSION)
        self.assertEqual(rounded.instances[0].customParameters["fileName"], "Goeist-Regular")
        self.assertEqual(rounded.features[0].code, font.features[0].code)
        self.assertEqual(rounded.kerning, font.kerning)
        self.assertEqual([point(n) for n in rounded.glyphs["O"].layers["Thin"].paths[1].nodes],
                         original_counter)
        for before, after in zip(font.glyphs, rounded.glyphs):
            self.assertEqual(before.export, after.export)
            self.assertEqual(before.leftKerningGroup, after.leftKerningGroup)
            self.assertEqual(before.rightKerningGroup, after.rightKerningGroup)
            for old_layer, new_layer in zip(before.layers, after.layers):
                self.assertEqual(old_layer.width, new_layer.width)
                self.assertEqual([(a.name, tuple(a.position)) for a in old_layer.anchors],
                                 [(a.name, tuple(a.position)) for a in new_layer.anchors])
                self.assertEqual([(c.name, c.transform) for c in old_layer.components],
                                 [(c.name, c.transform) for c in new_layer.components])
        self.assertEqual(font.familyName, "Geist")
        self.assertEqual(len(font.glyphs["H"].layers["Thin"].paths[0].nodes), 4)
        self.assertTrue(any(g["name"] == "acutecomb" and g["rounded_corners"] > 0
                            for g in report["glyphs"]))

    def test_hidden_overlap_corners_are_not_nicked(self):
        path = rectangle()
        overlap = rectangle(50, 120, x=80, y=-10)
        corners, reasons, exceptions = round_path(path, stem=20, others=[overlap])
        self.assertEqual(set(corners), {0, 3})
        self.assertEqual(reasons["hidden_or_overlapping_construction_corner"], 2)
        self.assertTrue(any(e["reason"] == "hidden_or_overlapping_construction_corner"
                            for e in exceptions))
        after = [Contour(path).polygon(), Contour(overlap).polygon()]
        self.assertTrue(filled(after, (99.9, 0.1)))

    def test_smooth_and_tangent_nodes_are_not_rounded(self):
        path = polygon([(0, 0), (50, 0), (100, 0), (100, 100), (0, 100)])
        path.nodes[3].smooth = True
        contour = Contour(path)
        polygons = [contour.polygon()]
        self.assertEqual(classify_corner(contour, 1, polygons, 20)[0],
                         "tangent_or_nearly_straight")
        self.assertEqual(classify_corner(contour, 3, polygons, 20)[0], "smooth")
        corners, _, _ = prepare_corners(contour, polygons, 20)
        self.assertNotIn(1, corners)
        self.assertNotIn(3, corners)

    def test_hidden_master_counterpart_keeps_corresponding_nodes(self):
        a, b = rectangle(), rectangle()
        first, second = Contour(a), Contour(b)
        decisions, _, _ = prepare_corners(first, [first.polygon()], 20)
        b.nodes[1].smooth = True
        other, _, _ = prepare_corners(second, [second.polygon()], 20)
        selected = set(decisions) | set(other)
        write_contour(first, selected, decisions)
        write_contour(second, selected, other)
        self.assertEqual([n.type for n in a.nodes], [n.type for n in b.nodes])
        self.assertTrue(any(point(node) == (100, 0) for node in b.nodes))

    def test_serialized_source_retains_fractional_geometry_and_features(self):
        rounded, _ = round_font(source_font())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Goeist.glyphs"
            rounded.save(path)
            with path.open(encoding="utf-8") as stream:
                reopened = load(stream)
        self.assertEqual(reopened.familyName, "Goeist")
        self.assertEqual(reopened.features[0].code, "sub H by O;")
        for before, after in zip(rounded.glyphs["H"].layers["Thin"].paths[0].nodes,
                                 reopened.glyphs["H"].layers["Thin"].paths[0].nodes):
            self.assertLess(math.dist(point(before), point(after)), 0.001)
        self.assertTrue(any(abs(n.position.x - round(n.position.x)) > 0.01
                            for n in reopened.glyphs["H"].layers["Thin"].paths[0].nodes))

    def test_italic_variable_name_does_not_collide_with_upright(self):
        font = source_font()
        for master in font.masters:
            master.name += " Italic"
        font.instances[0].customParameters["fileName"] = "Geist[wght]"
        rounded, _ = round_font(font)
        self.assertEqual(rounded.instances[0].customParameters["fileName"],
                         "Goeist-Italic[wght]")
        self.assertEqual(font.instances[0].customParameters["fileName"], "Geist[wght]")

    def test_round_nib_profile_fully_rounds_acute_apex(self):
        chevron = [(0, 400), (50, 400), (100, 150), (150, 400), (200, 400), (100, 0)]

        def apex_radius(profile):
            contour = Contour(polygon(chevron))
            corners, _, exceptions = prepare_corners(contour, [contour.polygon()], 40, profile)
            self.assertEqual(exceptions, [])
            return corners[5].radius

        self.assertAlmostEqual(apex_radius(FAMILIES["Goeist"].profile), 40 * 0.22)
        self.assertAlmostEqual(apex_radius(FAMILIES["GoeistMono"].profile), 40 * 0.52)

    def test_round_nib_stroke_end_is_circular_not_elliptical(self):
        contour = Contour(rectangle(width=40, height=400))
        corners, _, _ = prepare_corners(contour, [contour.polygon()], 40, FAMILIES["GoeistMono"].profile)
        corner = corners[0]  # bottom-left: short bottom edge limits the trim
        start, end = corner.curve[0], corner.curve[-1]
        self.assertAlmostEqual(math.dist(start, (0, 0)), math.dist(end, (0, 0)), places=6)
        self.assertAlmostEqual(corner.radius, 40 * 0.48)

    def test_round_nib_turns_dot_wider_than_stem_into_circle(self):
        def dot_radii(profile):
            contour = Contour(rectangle(width=80, height=80))
            corners, _, _ = prepare_corners(contour, [contour.polygon()], 32, profile)
            return {round(corner.radius, 6) for corner in corners.values()}

        self.assertEqual(dot_radii(FAMILIES["GoeistMono"].profile), {80 * 0.48})
        self.assertEqual(dot_radii(FAMILIES["Goeist"].profile), {round(32 * 0.52, 6)})

    def test_box_drawing_keeps_exact_cell_edge_geometry(self):
        font = source_font()
        glyph = GSGlyph("lightHorizontal")
        glyph.unicodes = ["2500"]
        for master in font.masters:
            layer = GSLayer()
            layer.layerId = layer.associatedMasterId = master.id
            layer.width = 600
            layer.paths.append(rectangle(600, 60, 0, 300))
            glyph.layers.append(layer)
        font.glyphs.append(glyph)
        mono = dataclasses.replace(FAMILIES["GoeistMono"], automatic_ligatures=False)
        rounded, report = round_font(font, mono)
        self.assertEqual([point(n) for n in rounded.glyphs["lightHorizontal"].layers["Regular"].paths[0].nodes],
                         [(0, 300), (600, 300), (600, 360), (0, 360)])
        self.assertEqual(report["counts"]["exact_geometry_glyphs"], 1)

    def test_automatic_ligatures_prefer_longest_exported_sequence(self):
        font = GSFont()
        for name, export in (("hyphen", True), ("greater", True), ("hyphen_greater.liga", True),
                             ("hyphen_greater_greater.liga", True), ("greater_greater.liga", False)):
            glyph = GSGlyph(name)
            glyph.export = export
            font.glyphs.append(glyph)
        font.features.append(GSFeature("ss01", "sub hyphen by greater;"))
        self.assertEqual(add_automatic_ligatures(font), 2)
        self.assertEqual([feature.name for feature in font.features], ["liga", "ss01"])
        self.assertEqual(font.features[0].code.splitlines(),
                         ["sub hyphen greater greater by hyphen_greater_greater.liga;",
                          "sub hyphen greater by hyphen_greater.liga;"])
        with self.assertRaisesRegex(GeometryError, "already defines liga"):
            add_automatic_ligatures(font)

    def test_unsupported_outline_fails_explicitly(self):
        path = rectangle()
        path.closed = False
        with self.assertRaisesRegex(GeometryError, "Open outlines"):
            Contour(path)
        path.closed = True
        path.nodes[0].type = "qcurve"
        with self.assertRaisesRegex(GeometryError, "Unsupported segment"):
            Contour(path)


if __name__ == "__main__":
    unittest.main()
