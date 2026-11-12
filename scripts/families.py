"""The Goeist families built from this repository, keyed by directory name.

Each family owns sources/<key>/, build/<key>/, fonts/<key>/ and out/<key>/.
"""
from __future__ import annotations

from dataclasses import dataclass

# Every family's font version (head.fontRevision and name ID 5); npm package
# versions are managed separately by Changesets in packages/goeist.
FONT_VERSION = (1, 0)
FONT_VERSION_STRING = f"{FONT_VERSION[0]}.{FONT_VERSION[1]:03d}"


@dataclass(frozen=True)
class Profile:
    """Fillet radii as multiples of the measured vertical stem.

    `terminal` applies to convex corners turning up to 110° (squared stem
    endings, outer corners); `acute` to sharper convex corners (apexes and
    diagonal cuts). `circular` keeps every fillet a circular arc by shrinking
    the radius where a short edge limits the trim. `stadium`, if set, turns
    straight-edged convex contours (dots, bars, slashes) into stadiums and
    circles: their radius is half the contour's width, at most `stadium` stems.
    """
    name: str
    terminal: float
    acute: float
    circular: bool = False
    stadium: float | None = None


# Goeist: soft terminals with restrained acute joins.
SOFT = Profile("soft", terminal=0.52, acute=0.22)
# Goeist Mono: one round tool for every exposed corner, after ABC Diatype
# Rounded Mono: semicircular terminals and slabs, round dots, rounded apexes.
ROUND_NIB = Profile("round-nib", terminal=0.52, acute=0.52, circular=True, stadium=1.5)


@dataclass(frozen=True)
class Family:
    key: str             # directory and file prefix, e.g. GoeistMono
    name: str            # font family name, e.g. Goeist Mono
    css: str             # webfont stylesheet stem, e.g. goeist-mono
    upstream_key: str    # upstream file prefix, e.g. GeistMono
    upstream_name: str   # upstream font family name, e.g. Geist Mono
    upstream_label: str  # credited upstream design, e.g. Geist Mono
    profile: Profile
    # Recreate the `liga` feature Glyphs.app derives from `a_b.liga` glyph
    # names; the upstream source does not store it and glyphsLib cannot derive it.
    automatic_ligatures: bool = False
    # Codepoints whose glyphs keep their exact upstream outlines.
    exact_geometry: range | None = None


FAMILIES = {
    family.key: family for family in (
        Family("Goeist", "Goeist", "goeist", "Geist", "Geist", "Geist Sans", SOFT),
        # Box drawing and block elements tile across character cells, and
        # geometric shapes are exact pictograms: rounding them breaks
        # connected lines and blocks in terminals.
        Family("GoeistMono", "Goeist Mono", "goeist-mono", "GeistMono", "Geist Mono", "Geist Mono", ROUND_NIB,
               automatic_ligatures=True, exact_geometry=range(0x2500, 0x2600)),
    )
}
