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
    `local`, if set, also caps each radius at that fraction of the ink
    thickness measured across the corner, so hairlines in a high-contrast
    design round in proportion to themselves rather than to the stem.
    """
    name: str
    terminal: float
    acute: float
    circular: bool = False
    stadium: float | None = None
    local: float | None = None


# Goeist: soft terminals with restrained acute joins.
SOFT = Profile("soft", terminal=0.52, acute=0.22)
# Goeist Mono: one round tool for every exposed corner, after ABC Diatype
# Rounded Mono: semicircular terminals and slabs, round dots, rounded apexes.
ROUND_NIB = Profile("round-nib", terminal=0.52, acute=0.52, circular=True, stadium=1.5)
# Goeist Serif: circular fillets bounded by the local stroke, after Fraunces'
# SOFT axis: a third of a stem on stem corners, a half-round on hairlines.
SOFT_SERIF = Profile("soft-serif", terminal=0.33, acute=0.22, circular=True, local=0.5)


@dataclass(frozen=True)
class SoftSerif:
    """Goeist Serif's construction on top of its `Profile`, in font units.

    `tip`: thickness of every serif end, closed with a half-circle of `tip / 2`
    at the serif's original reach. `cap`: radius of the circle that rounds
    drawn cut terminals and spikes (s, c, a, r, figures). `cut`: the longest
    straight cut that counts as such a terminal. `guard`: the display-size
    minimum ink gap (make-font's 4 units) below which a glyph pair the tips
    brought closer than Geist Serif is opened by the collision guard.
    """
    tip: float
    cap: float
    cut: float
    guard: int = 4


@dataclass(frozen=True)
class Style:
    name: str        # file and subfamily name, e.g. BoldItalic or Square
    weight: int      # usWeightClass
    italic: bool
    location: tuple  # (axis tag, value) pairs in the matching variable font

    @property
    def slope(self):
        return "italic" if self.italic else "upright"


WEIGHTS = (
    (100, "Thin"), (200, "ExtraLight"), (300, "Light"),
    (400, "Regular"), (500, "Medium"), (600, "SemiBold"),
    (700, "Bold"), (800, "ExtraBold"), (900, "Black"),
)


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
    # Set for a single-master family whose variable font has one Element Shape
    # (ELSH) axis that swaps dot glyphs (Geist Serif); otherwise the family
    # has upright and italic variable fonts on a 100-900 weight axis.
    soft_serif: SoftSerif | None = None

    @property
    def element_shapes(self):
        return self.soft_serif is not None

    @property
    def axis(self):
        """(tag, minimum, default, maximum) of the variable fonts' one axis."""
        return ("ELSH", 0, 0, 100) if self.element_shapes else ("wght", 100, 400, 900)

    @property
    def slopes(self):
        return ("upright",) if self.element_shapes else ("upright", "italic")

    @property
    def upstream_packages(self):
        """Upstream .glyphspackage basenames, one per slope."""
        return tuple(self.upstream_key + ("-Italic" if slope == "italic" else "") for slope in self.slopes)

    def variable_stem(self, prefix, slope="upright"):
        return f"{prefix}{'-Italic' if slope == 'italic' else ''}[{self.axis[0]}]"

    @property
    def styles(self):
        """Every static style, in release order."""
        if self.element_shapes:
            return tuple(Style(name, 400, False, (("ELSH", value),))
                         for name, value in (("Regular", 0), ("Square", 25), ("Triangle", 50), ("Heart", 100)))
        return tuple(style for weight, name in WEIGHTS for style in (
            Style(name, weight, False, (("wght", weight),)),
            Style("Italic" if name == "Regular" else name + "Italic", weight, True, (("wght", weight),))))


FAMILIES = {
    family.key: family for family in (
        Family("Goeist", "Goeist", "goeist", "Geist", "Geist", "Geist Sans", SOFT),
        # Box drawing and block elements tile across character cells, and
        # geometric shapes are exact pictograms: rounding them breaks
        # connected lines and blocks in terminals.
        Family("GoeistMono", "Goeist Mono", "goeist-mono", "GeistMono", "Geist Mono", "Geist Mono", ROUND_NIB,
               automatic_ligatures=True, exact_geometry=range(0x2500, 0x2600)),
        # Serif ends and cut terminals 26 units thick: about Geist Serif's
        # 29-38 unit hairline, so every end holds a visible half-round.
        Family("GoeistSerif", "Goeist Serif", "goeist-serif", "GeistSerif", "Geist Serif", "Geist Serif",
               SOFT_SERIF, soft_serif=SoftSerif(tip=26, cap=13, cut=14)),
    )
}
