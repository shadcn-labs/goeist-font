"""Smallest ink gap between shaped glyph pairs, and a guard that opens new collisions.

The make-font collision guard (design.how): every pair of encoded characters is
shaped with HarfBuzz, kerning on; each glyph's ink is read in rows `STEP` units
apart, and the pair's gap is the smallest distance between the left glyph's
right edge and the right glyph's left edge in any shared row. Negative gaps
overlap. The guard only opens pairs and never closes one.
"""
from __future__ import annotations

import math
import unicodedata

import uharfbuzz as hb
from fontTools.otlLib.builder import buildPairPosGlyphs, buildValue
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables

STEP = 4
FEATURES = {"kern": True, "liga": False, "clig": False, "dlig": False}
# TrueType outlines are quadratic approximations on an integer grid: each glyph's
# rounded curve can measure up to 1.5 units outside the cubic it came from (cu2qu
# error 1, rounding 0.5), so a pair's gap can shift by 3 units without any
# design change. Smaller deficits are not regressions.
TOLERANCE = 3.0


class _EdgePen(BasePen):
    """Outline edges as (x0, y0, x1, y1), curves flattened."""

    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.edges = []

    def _moveTo(self, p):
        self.start = self.last = p

    def _lineTo(self, p):
        self.edges.append((*self.last, *p))
        self.last = p

    def _curveToOne(self, a, b, c):
        p0 = self.last
        for i in range(1, 17):
            t = i / 16
            u = 1 - t
            self._lineTo(tuple(u ** 3 * p0[k] + 3 * u * u * t * a[k] + 3 * u * t * t * b[k] + t ** 3 * c[k]
                               for k in (0, 1)))

    def _qCurveToOne(self, a, b):
        p0 = self.last
        for i in range(1, 9):
            t = i / 8
            u = 1 - t
            self._lineTo(tuple(u * u * p0[k] + 2 * u * t * a[k] + t * t * b[k] for k in (0, 1)))

    def _closePath(self):
        if self.last != self.start:
            self._lineTo(self.start)


def _edges(font: TTFont, name: str):
    glyph_set = font.getGlyphSet()
    pen = _EdgePen(glyph_set)
    glyph_set[name].draw(pen)
    return pen.edges


def ink_rows(font: TTFont, name: str):
    """{row: (left, right)} ink extents in rows STEP units apart (row y = row * STEP)."""
    rows = {}
    for x0, y0, x1, y1 in _edges(font, name):
        if y0 == y1:
            continue
        for row in range(math.ceil(min(y0, y1) / STEP), math.ceil(max(y0, y1) / STEP)):
            x = x0 + (row * STEP - y0) * (x1 - x0) / (y1 - y0)
            left, right = rows.get(row, (x, x))
            rows[row] = (min(left, x), max(right, x))
    return rows


def characters(font: TTFont):
    """Encoded characters that draw ink on their own: no marks, spaces or controls."""
    return [chr(code) for code, name in sorted(font.getBestCmap().items())
            if unicodedata.category(chr(code))[0] not in "MZC" and _edges(font, name)]


def _shape(hbfont, text):
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(hbfont, buffer, FEATURES)
    return buffer.glyph_infos, buffer.glyph_positions


def pair_gaps(path, min_gap, chars=None):
    """{(left char, right char): (left glyph, right glyph, gap)} for pairs closer than `min_gap`.

    Each left character is shaped once against all right characters
    (L R1 L R2 …), so most pairs' kerning comes from one HarfBuzz run; a pair
    whose glyphs in that run are not its own characters' default glyphs (a
    ligature or contextual form across the run) is shaped on its own. Pairs
    whose bounding boxes alone keep them `min_gap` apart are not measured.
    """
    font = TTFont(path)
    chars = chars or characters(font)
    order = font.getGlyphOrder()
    cmap = font.getBestCmap()
    profiles = {}

    def profile(name):
        if name not in profiles:
            rows = ink_rows(font, name)
            box = (min(l for l, _ in rows.values()), max(r for _, r in rows.values())) if rows else None
            profiles[name] = (rows, box)
        return profiles[name]

    hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
    result = {}
    for a in chars:
        infos, positions = _shape(hbfont, "".join(a + b for b in chars))
        aligned = len(infos) == 2 * len(chars)
        for k, b in enumerate(chars):
            first, second = 2 * k, 2 * k + 1
            pair_infos, pair_positions = infos, positions
            if not (aligned and order[infos[first].codepoint] == cmap[ord(a)]
                    and order[infos[second].codepoint] == cmap[ord(b)]):
                pair_infos, pair_positions = _shape(hbfont, a + b)
                if len(pair_infos) != 2:
                    continue
                first, second = 0, 1
            ga, gb = order[pair_infos[first].codepoint], order[pair_infos[second].codepoint]
            (rows_a, box_a), (rows_b, box_b) = profile(ga), profile(gb)
            if not box_a or not box_b:
                continue
            offset = (pair_positions[first].x_advance + pair_positions[second].x_offset
                      - pair_positions[first].x_offset)
            if offset + box_b[0] - box_a[1] >= min_gap:
                continue
            shared = rows_a.keys() & rows_b.keys()
            if shared:
                gap = offset + min(rows_b[r][0] - rows_a[r][1] for r in shared)
                if gap < min_gap:
                    result[(a, b)] = (ga, gb, gap)
    return result


def regressions(built, baseline, min_gap):
    """Pairs tighter than both `min_gap` and their baseline gap: [(deficit, pair, built gap, baseline gap)].

    Both maps come from `pair_gaps` with the same `min_gap`; a pair absent from
    the baseline map sat at least `min_gap` apart there.
    """
    found = []
    for pair, (_, _, gap) in built.items():
        before = baseline[pair][2] if pair in baseline else min_gap
        target = min(before, min_gap)
        if gap < target - TOLERANCE:
            found.append((target - gap, pair, gap, before))
    return sorted(found, reverse=True)


def guard_pairs(built, baseline, min_gap):
    """{(left glyph, right glyph): units} that restore every regression to its target.

    The guard opens a new collision to `min_gap`, or to the baseline gap where
    the original design already sat closer, and leaves every other pair alone.
    """
    pairs = {}
    for deficit, pair, _, _ in regressions(built, baseline, min_gap):
        ga, gb, _ = built[pair]
        pairs[(ga, gb)] = max(pairs.get((ga, gb), 0), math.ceil(deficit))
    return pairs


def _kern_features(gpos):
    kern = [i for i, record in enumerate(gpos.FeatureList.FeatureRecord) if record.FeatureTag == "kern"]
    features = [gpos.FeatureList.FeatureRecord[i].Feature for i in kern]
    variations = getattr(gpos, "FeatureVariations", None)
    if variations:
        features += [s.Feature for r in variations.FeatureVariationRecord
                     for s in r.FeatureTableSubstitution.SubstitutionRecord if s.FeatureIndex in kern]
    return features


def add_guard_lookup(font: TTFont, pairs):
    """Append one glyph-pair PairPos lookup to every `kern` feature of `font`."""
    if not pairs:
        return
    gpos = font["GPOS"].table
    values = {pair: (buildValue({"XAdvance": units}), None) for pair, units in sorted(pairs.items())}
    lookup = otTables.Lookup()
    lookup.LookupType = 2
    lookup.LookupFlag = 0
    lookup.SubTable = buildPairPosGlyphs(values, font.getReverseGlyphMap())
    lookup.SubTableCount = len(lookup.SubTable)
    gpos.LookupList.Lookup.append(lookup)
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    index = gpos.LookupList.LookupCount - 1
    features = _kern_features(gpos)
    if not features:
        raise ValueError("font has no kern feature for the collision guard")
    for feature in features:
        feature.LookupListIndex.append(index)
        feature.LookupCount = len(feature.LookupListIndex)


def strip_guard_lookup(font: TTFont):
    """Remove the collision guard (the last GPOS lookup, a PairPos used only by
    `kern`) in place and return its pair count. Comparing the rest with the
    unrounded baseline then shows that nothing else in GPOS changed."""
    gpos = font["GPOS"].table
    index = gpos.LookupList.LookupCount - 1
    lookup = gpos.LookupList.Lookup[index]
    users = {record.FeatureTag for record in gpos.FeatureList.FeatureRecord
             if index in record.Feature.LookupListIndex}
    if lookup.LookupType != 2 or users != {"kern"}:
        raise ValueError("last GPOS lookup is not a kern-only collision guard")
    count = sum(len(pairset.PairValueRecord) for subtable in lookup.SubTable
                for pairset in getattr(subtable, "PairSet", []))
    del gpos.LookupList.Lookup[index]
    gpos.LookupList.LookupCount = index
    features = [record.Feature for record in gpos.FeatureList.FeatureRecord]
    variations = getattr(gpos, "FeatureVariations", None)
    if variations:
        features += [s.Feature for r in variations.FeatureVariationRecord
                     for s in r.FeatureTableSubstitution.SubstitutionRecord]
    for feature in features:
        feature.LookupListIndex = [i for i in feature.LookupListIndex if i != index]
        feature.LookupCount = len(feature.LookupListIndex)
    return count
