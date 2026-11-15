"""Goeist Serif source construction: soft serif tips, cut-terminal caps, the
local-thickness radius clamp and static shape variants."""
import math
import sys
import unittest
from collections import Counter
from pathlib import Path

from glyphsLib import GSFont
from glyphsLib.classes import LINE, GSFontMaster, GSGlyph, GSLayer, GSNode, GSPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from families import FAMILIES  # noqa: E402
from rounding import Contour, OutlineContext, cross, evaluate, filled, prepare_corners, tangent  # noqa: E402
import serif  # noqa: E402

SERIF = FAMILIES["GoeistSerif"]


def node(x, y, handles=None):
    return {"pt": (float(x), float(y)), "h": handles, "serif": False}


def placed_serif():
    """Geist Serif's `_corner.ucSerif` on the right of a stem edge at x=198, as
    glyphs_corners places it in H: flat foot, 6-unit tip, wedge, bracket curve."""
    tag = object()
    shape = [
        node(188, 0), node(282, 0), node(282, 6), node(219, 42),
        node(198, 75, ((203, 51), (198, 57))), node(198, 600), node(500, 600), node(500, 0),
    ]
    for index in (0, 1, 2, 3, 4):
        shape[index]["serif"] = id(tag)
    return shape


def one_master_font(*paths):
    font = GSFont()
    master = GSFontMaster()
    master.id = "m"
    font.masters.append(master)
    glyph = GSGlyph("fixture")
    layer = GSLayer()
    layer.layerId = "m"
    for path in paths:
        layer.shapes.append(path)
    glyph.layers.append(layer)
    font.glyphs.append(glyph)
    return font, glyph, layer


def closed(points):
    path = GSPath()
    path.closed = True
    path.nodes = [GSNode(p, type=LINE) for p in points]
    return path


class SoftSerifTipTests(unittest.TestCase):
    def setUp(self):
        self.shape = serif.soften_shape(placed_serif(), SERIF.soft_serif.tip, Counter())
        self.points = [n["pt"] for n in self.shape]

    def arc(self):
        """Sample every cubic the softening added (nodes tagged True)."""
        samples, previous = [], self.shape[-1]["pt"]
        for item in self.shape:
            if item["h"] and item["serif"] is True:
                samples += [evaluate((previous, *item["h"], item["pt"]), t / 16) for t in range(17)]
            previous = item["pt"]
        return samples

    def test_tip_keeps_reach_and_flat_foot(self):
        arc = self.arc()
        self.assertTrue(arc)
        self.assertAlmostEqual(max(x for x, _ in arc), 282, delta=0.05)
        self.assertAlmostEqual(min(y for _, y in arc), 0, places=6)
        self.assertIn((188.0, 0.0), self.points)

    def test_tip_is_thickened_to_a_half_round_of_tip_thickness(self):
        arc = self.arc()
        radius = SERIF.soft_serif.tip / 2
        center = (282 - radius, radius)
        for p in arc:
            self.assertAlmostEqual(math.dist(p, center), radius, delta=radius * 0.003)
        self.assertLessEqual(max(y for _, y in arc), SERIF.soft_serif.tip + 1e-6)
        self.assertGreater(max(y for _, y in arc), SERIF.soft_serif.tip - 1)

    def test_bracket_stays_tangent_to_the_redrawn_wedge(self):
        bracket = next(i for i, n in enumerate(self.shape) if n["pt"] == (219.0, 42.0))
        wedge = tuple(a - b for a, b in zip(self.shape[bracket]["pt"], self.shape[bracket - 1]["pt"]))
        handle = tuple(a - b for a, b in zip(self.shape[bracket + 1]["h"][0], self.shape[bracket]["pt"]))
        self.assertAlmostEqual(cross(wedge, handle) / math.hypot(*wedge) / math.hypot(*handle), 0, places=9)


class CutTerminalCapTests(unittest.TestCase):
    def test_tapered_cut_becomes_one_circular_end_inside_the_ink(self):
        # A stroke 60 units thick narrowing to a 4-unit cut at the right.
        path = closed([(0, 0), (300, 28), (300, 32), (0, 60)])
        font, glyph, layer = one_master_font(path)
        original = OutlineContext(font).polygons(glyph, layer)
        stats = Counter()
        serif.cap_terminals(font, {"m": {"stem": 84}}, SERIF.profile, 13, 14, stats)
        self.assertEqual(stats["terminal_capped"], 1)
        contour = Contour(layer.paths[0])
        arcs = [s for s in contour.segments if len(s.points) == 4]
        self.assertTrue(arcs)
        for index in range(len(contour.nodes)):
            a = tangent(contour.segments[index - 1].points, True)
            b = tangent(contour.segments[index].points)
            if 4 in (len(contour.segments[index].points), len(contour.segments[index - 1].points)):
                self.assertAlmostEqual(cross(a, b), 0, places=6)
        for segment in arcs:
            for t in (0.25, 0.5, 0.75):
                self.assertTrue(filled(original, evaluate(segment.points, t)))
        # The end is round: the farthest point sits on the stroke's axis.
        tip = max((evaluate(s.points, t / 32) for s in arcs for t in range(33)), key=lambda p: p[0])
        self.assertAlmostEqual(tip[1], 30, delta=0.5)


class LocalThicknessTests(unittest.TestCase):
    def test_hairline_corners_round_in_proportion_to_the_hairline(self):
        # A 30-unit hairline bar measured against an 84-unit stem.
        path = closed([(0, 0), (400, 0), (400, 30), (0, 30)])
        font, glyph, layer = one_master_font(path)
        polygons = OutlineContext(font).polygons(glyph, layer)
        corners, _, _ = prepare_corners(Contour(path), polygons, 84, SERIF.profile)
        self.assertEqual(len(corners), 4)
        for corner in corners.values():
            self.assertLessEqual(corner.radius, 0.5 * 30 + 1e-6)

    def test_stem_corners_keep_the_stem_relative_radius(self):
        path = closed([(0, 0), (84, 0), (84, 700), (0, 700)])
        font, glyph, layer = one_master_font(path)
        polygons = OutlineContext(font).polygons(glyph, layer)
        corners, _, _ = prepare_corners(Contour(path), polygons, 84, SERIF.profile)
        self.assertTrue(all(math.isclose(c.radius, 84 * SERIF.profile.terminal) for c in corners.values()))


class OverlapTests(unittest.TestCase):
    def test_open_corner_loop_is_erased(self):
        # A square whose top-right corner overshoots into a Glyphs open corner.
        path = closed([(0, 0), (100, 0), (100, 120), (120, 100), (0, 100)])
        font, glyph, layer = one_master_font(path)
        serif.remove_overlaps(font)
        (result,) = layer.paths
        xs = [n.position.x for n in result.nodes]
        ys = [n.position.y for n in result.nodes]
        self.assertLessEqual(max(xs), 100 + 1e-6)
        self.assertLessEqual(max(ys), 100 + 1e-6)


class StaticVariantTests(unittest.TestCase):
    def test_rename_swaps_drawings_and_kerning_while_users_follow_by_name(self):
        info = {
            "features": [{"tag": "ss02", "code": "sub period by period.ss02;\n"},
                         {"tag": "rclt", "code": "#ifdef VARIABLE\ncondition 1;\n#endif\nsub a by b;\n"}],
            "glyphs": [
                {"glyphname": "period", "layers": [{"name": "round"}], "kernLeft": "round"},
                {"glyphname": "period.ss02", "layers": [{"name": "square"}], "kernLeft": "square"},
                {"glyphname": "ellipsis", "layers": [{"shapes": [{"ref": "period"}]}]},
            ],
            "kerningLTR": {"m": {"period": {"A": -10}}},
        }
        instance = {"customParameters": [
            {"name": "Rename Glyphs", "value": ["period=period.ss02"]},
            {"name": "Replace Feature", "value": "ss02; sub period by period.ss02;"},
        ]}
        variant = serif.static_variant(info, instance)
        glyphs = {g["glyphname"]: g for g in variant["glyphs"]}
        self.assertEqual(glyphs["period"]["layers"], [{"name": "square"}])
        self.assertEqual(glyphs["period.ss02"]["kernLeft"], "round")
        # The ellipsis keeps referring to `period`, which now holds the square dot.
        self.assertEqual(glyphs["ellipsis"]["layers"][0]["shapes"], [{"ref": "period"}])
        self.assertEqual(variant["kerningLTR"]["m"], {"period.ss02": {"A": -10}})
        self.assertNotIn("VARIABLE", variant["features"][1]["code"])
        self.assertEqual(info["glyphs"][0]["layers"], [{"name": "round"}])


if __name__ == "__main__":
    unittest.main()
