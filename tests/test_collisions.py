"""Collision guard: what counts as a regression, and the lookup it adds."""
import sys
import tempfile
import unittest
from pathlib import Path

import uharfbuzz as hb
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import collisions  # noqa: E402


def box_font(path, kern=0):
    """Two 100-unit-wide boxes, A and B, on 120-unit advances (10-unit sidebearings)."""
    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder([".notdef", "A", "B"])
    builder.setupCharacterMap({0x41: "A", 0x42: "B"})
    glyphs = {}
    for name in (".notdef", "A", "B"):
        pen = TTGlyphPen(None)
        if name != ".notdef":
            pen.moveTo((10, 0))
            pen.lineTo((10, 700))
            pen.lineTo((110, 700))
            pen.lineTo((110, 0))
            pen.closePath()
        glyphs[name] = pen.glyph()
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics({name: (120, 10) for name in glyphs})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable({"familyName": "Box", "styleName": "Regular"})
    builder.setupOS2()
    builder.setupPost()
    addOpenTypeFeaturesFromString(builder.font, f"feature kern {{ pos A B {kern}; }} kern;")
    builder.save(path)
    return builder.font


class RegressionTests(unittest.TestCase):
    def test_only_pairs_tighter_than_both_targets_regress(self):
        baseline = {("A", "B"): ("A", "B", -10.0), ("C", "D"): ("C", "D", 3.0)}
        built = {("A", "B"): ("A", "B", -11.0),   # upstream already touched: within tolerance
                 ("C", "D"): ("C", "D", -17.0),   # was 3 apart, now overlaps
                 ("E", "F"): ("E", "F", -5.0)}    # was at least min_gap apart
        found = {pair: round(deficit) for deficit, pair, _, _ in collisions.regressions(built, baseline, 4)}
        self.assertEqual(found, {("C", "D"): 20, ("E", "F"): 9})
        self.assertEqual(collisions.guard_pairs(built, baseline, 4), {("C", "D"): 20, ("E", "F"): 9})


class GuardLookupTests(unittest.TestCase):
    def test_guard_opens_the_pair_and_strips_back_to_the_original(self):
        with tempfile.TemporaryDirectory() as directory:
            tight = Path(directory) / "tight.ttf"
            font = box_font(tight, kern=-30)
            # Ink gap: 10 + 10 sidebearings - 30 kern = -10 units.
            self.assertAlmostEqual(collisions.pair_gaps(tight, 4, chars=["A", "B"])[("A", "B")][2], -10)
            before = font["GPOS"].compile(font)
            collisions.add_guard_lookup(font, {("A", "B"): 14})
            opened = Path(directory) / "opened.ttf"
            font.save(opened)
            buffer = hb.Buffer()
            buffer.add_str("AB")
            buffer.guess_segment_properties()
            hb.shape(hb.Font(hb.Face(hb.Blob.from_file_path(str(opened)))), buffer, {"kern": True})
            self.assertEqual(buffer.glyph_positions[0].x_advance, 120 - 30 + 14)
            self.assertEqual(collisions.strip_guard_lookup(font), 1)
            self.assertEqual(font["GPOS"].compile(font), before)


if __name__ == "__main__":
    unittest.main()
