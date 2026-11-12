"""Static CFF metrics must agree with their encoded charstring advances."""
import io
import unittest

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

from scripts.build import align_static_advances


def cff_font():
    builder = FontBuilder(1000, isTTF=False)
    order = [".notdef", "a", "b"]
    widths = {".notdef": 600, "a": 501, "b": 600}
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap({97: "a", 98: "b"})
    builder.setupHorizontalMetrics({name: (width, 30 if name == "a" else 0)
                                    for name, width in widths.items()})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable({"familyName": "Metrics Fixture", "styleName": "Regular",
                            "uniqueFontIdentifier": "MetricsFixture-Regular",
                            "fullName": "Metrics Fixture Regular", "psName": "MetricsFixture-Regular"})
    builder.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
    builder.setupPost()
    charstrings = {}
    for name, width in widths.items():
        pen = T2CharStringPen(None if width == 600 else width - 500, None, roundTolerance=0)
        pen.moveTo((30, 0))
        pen.lineTo((180, 0))
        pen.curveTo((210, 0), (210, 300), (180, 300))
        pen.lineTo((30, 300))
        pen.closePath()
        charstrings[name] = pen.getCharString()
    builder.setupCFF("MetricsFixture-Regular", {}, charstrings,
                     {"nominalWidthX": 500, "defaultWidthX": 600})
    return builder.font


class StaticAdvanceTests(unittest.TestCase):
    def test_cff_width_encoding_and_outlines_survive_metric_alignment(self):
        for expected in (502, 600, 702):
            with self.subTest(advance=expected):
                font = cff_font()
                original = RecordingPen()
                font.getGlyphSet()["a"].draw(original)
                align_static_advances(font, {".notdef": 600, "a": expected, "b": 600})
                buffer = io.BytesIO()
                font.save(buffer)
                with TTFont(io.BytesIO(buffer.getvalue())) as exported:
                    actual = RecordingPen()
                    exported.getGlyphSet()["a"].draw(actual)
                    charstring = exported["CFF "].cff.topDictIndex[0].CharStrings["a"]
                    self.assertEqual(exported["hmtx"]["a"], (expected, 30))
                    self.assertEqual(charstring.width, expected)
                    self.assertEqual(actual.value, original.value)
                    self.assertEqual(exported["hhea"].advanceWidthMax, max(expected, 600))


if __name__ == "__main__":
    unittest.main()
