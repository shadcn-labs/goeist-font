# Goeist research

Pre-implementation research for **Goeist Serif** (a rounded Geist Serif) and for fixing the 1.000 releases of Goeist Sans and Goeist Mono. Kept apart from `documentation/`, which holds the shipped font article. Nothing here changes the build.

| Note | Covers |
| --- | --- |
| [geist-serif.md](geist-serif.md) | The upstream: provenance, license, structure, measured contrast, serif construction, why the current rounding cannot carry over |
| [rounded-serif-references.md](rounded-serif-references.md) | ITC Souvenir and its relatives (visual only), OFL soft serifs with verified licenses and measured radii, glyph-by-glyph treatment, rounded-serif vocabulary |
| [type-design-principles.md](type-design-principles.md) | General, serif, sans, mono and rounded design rules, with sources; measured SF Rounded, Google Sans Flex, Source Serif 4 |
| [curves-and-variable-fonts.md](curves-and-variable-fonts.md) | G0–G3 continuity, curvature maths for `make_corner`, G2 fillet constructions, the variable-font design space, axis registry (`ROND`, `SOFT`, `CASL`, `ELSH`), a possible roundness axis |
| [goeist-sans-mono-audit.md](goeist-sans-mono-audit.md) | 17 ranked defects in the committed Goeist Sans/Mono fonts, with evidence and code references |

## Key facts

- **Geist Serif is already in the pinned upstream.** It ships in `vercel/geist-font` `v1.9.2` (`ef2597c`) as `sources/GeistSerif.glyphspackage`, under OFL 1.1 with no Reserved Font Name. Only the Sans and Mono packages were vendored.
- **What Geist Serif is:** a display serif with one master (Regular), no italic and 898 glyphs (465 mapped). The `ELSH` axis (0/25/50/100 = round/square/triangle/heart dots) only swaps glyphs, through `rclt` feature variations; it has no outline deltas. Vercel says Thin–Black weights, an italic and a text cut are in progress ([blog](https://vercel.com/blog/introducing-geist-serif)).
- **Serifs are Glyphs corner components:** five components, 359 placements. Each is an asymmetric wedge (about 30°) with a curved bracket and a tip only 4–6 units thick. fontmake does not expand corner components; upstream uses `scripts/glyphs_corners.py` for that.
- **Contrast is 2.6–3.6:** stems 84–117 units, hairlines 29–38. On a hairline, a stem-relative radius (Goeist Sans: 0.52 × 84 ≈ 44 units) is about 8× the tip thickness.
- **ITC Souvenir** is proprietary, so it can only be a visual reference. Its softness is drawn by hand: low contrast, bulb serifs, curved diagonals and an open g. Trimming corners cannot produce any of that.
- **Closest OFL reference: Fraunces `SOFT`.** Fraunces is OFL and cites Souvenir as an inspiration. Its `SOFT` axis is mostly a contrast axis (11:1 → 1.7:1 at opsz 144) with semicircular serif ends (r ≈ ½ serif thickness) and larger brackets, and joins where strokes meet stay sharp. Geist Serif's contrast already sits near Fraunces `SOFT` ≈ 50.
- **What other rounded families do:** none of the measured ones (SF Rounded, Google Sans Flex `ROND`, Kode Mono, Nunito, Cera Round) change stems or advances. Apple and Google extend rounded stroke ends slightly past the alignment line to recover lost ink; Goeist does not, and it loses the most ink of any family measured.
- **Terminology.**
  - *Registered axes* are `wght`, `wdth`, `opsz`, `ital` and `slnt`. Custom axes use uppercase tags: `ROND`, `SOFT`, `ELSH`.
  - *Masters* are the drawn designs a variable axis interpolates between: one at the start of the axis, usually one in the middle (the default), one at the end. Geist Sans and Mono have masters at Thin (100), Regular (400) and Black (900) on `wght`; every Goeist fillet is built in all three with matching point structure so the weights in between interpolate. Geist Serif has a single master: its only axis, `ELSH`, swaps dot glyphs instead of interpolating, so Goeist Serif cannot have weights until upstream publishes its announced Thin–Black masters.
  - *G1* means the tangents match at a join; *G2* means the curvature matches too. Goeist's fillets are exactly G1. Curvature jumps by about 0.98/r at a 90° corner.

## Reconciled disagreements between notes

| Topic | Positions | Resolution |
| --- | --- | --- |
| Serif tip thickness | One note says 0.30 stem (≈ 25 units); the other says hairline thickness, 0.40 stem (≈ 34 units) | Proof both. References favour a tip as thick as the hairline. Close the tip with one arc, r = t/2 |
| Curve continuity | Keep G1 for consistency, vs. raise the handle tension | Adopt `alpha` ≈ 0.70 as a profile parameter. It stays G1 and adds no points, but cuts the curvature jump by 66% for 23% more trim (Open Runde measures 0.644). Exact G2 caps are second; two-cubic G2 fillets next to curves come later |
| Concave corners | Soften them, or leave them sharp | Leave them sharp, as Fraunces, SF Rounded, Open Runde and Diatype do. Brackets are already smooth curves; enlarge them inside the serif components, not with a concave-fillet pass |

## Owner decisions

1. **Goeist Serif character: Fraunces-soft** (decided 2026-11-15). Geist Serif keeps its contrast and editorial voice; serif tips, cut terminals and apexes are rounded. The Souvenir-like redraw (contrast ≤ 2, bulb serifs, curved diagonals) remains a possible later direction, once upstream weights exist.
2. **Terminals:** semicircular ends at local thickness, as implemented. Ball terminals were not requested.
3. **Character of Goeist Sans** and **4. `ROND` axis:** still open.

## Goeist Serif as built

Implemented in `scripts/serif.py`; the construction is documented in [CONTRIBUTING.md](../CONTRIBUTING.md#goeist-serif). How it settled the open questions above:

| Question | Built |
| --- | --- |
| Serif tip thickness (25 vs 34 units) | 26 units, half-round radius 13. Proofs at 22 and 30: 30 read as a slab serif, 22 kept more of the saw tooth; 26 sits between the two notes' values |
| Reshape tips in the components, or in each glyph | In each placed serif during component expansion: scaled serifs (0.42–2× in Geist Serif) would otherwise turn the half-round into an ellipse |
| Brackets | Kept as drawn; only the bracket's last handle turns to stay tangent to the redrawn wedge |
| Terminal caps | A 13-unit circle inscribed where the stroke is that thick, for cuts up to 14 units and spikes sharper than 140°. 89 cuts and 2 spikes capped |
| Remaining corners | `soft-serif`: circular, 0.33 stem (terminal) / 0.22 stem (acute), at most 0.5 × local thickness |
| Handle tension (`alpha`) and G2 | Not adopted: fillets stay G1 with the circular-arc handle, as in Sans and Mono |
| "Round dots" feature names | Not an upstream bug: only each shape static's replacement `ss02`/`ss03`/`ss04` carries the label, where it does switch back to round dots |
| Known leftovers | The hairline spur where the bowl meets the stem in a and d (about 8 units) stays sharp; corners with a sub-unit flat between two fillets read as half-rounds |

## Remaining work: Goeist Sans and Goeist Mono

All eight fixes below remain open for Sans and Mono, whose outputs are byte-identical after Goeist Serif's addition. Goeist Serif already applies items 1 (rounding the unioned ink) and 5 (circular fillets bounded by local thickness) to itself.

**Pipeline fixes, from the audit's ranked issues:**

1. Decide whether a corner is exposed from the glyph's merged ink, and fail the build on any sharp exposed convex corner that remains.
2. Allow a stadium only for a simple convex contour with no hole inside. This fixes the 1.5-stem radii on Mono L/N/M/V/г/И and the blunted ⌧ ⌫ ∆ and arrowheads.
3. Make the radius a continuous function of the corner angle, replacing the hard switch at 110°. Pick one radius fraction per corner and apply it in every master.
4. Keep the handle-length ratio at each smooth join equal across masters. Today it differs, which causes 447–487 kinks in the SemiBold and Bold instances. Gate the build on `fontTools.varLib.interpolatable` and on a check at the midpoints between masters.
5. Use circular fillets only, with `r = min(k × stem, 0.5 × local thickness)`. Replace the halving fallback with a bisection search for the largest safe radius.
6. Extend stroke ends that sit on an alignment line by about 0.107 × stem before filleting. Size rounded dots to keep the original dot's area.
7. Compensate for points that pull in at rounded apexes (A, V, `*`, `>`) and adjust kerning, never advances.
8. Add a profile parameter for handle tension (`alpha`).

**Goeist Serif keeps upstream's metrics:** one Regular master, no italic, `ELSH` kept substitution-only, source vertical metrics (ascender 800, descender −150, hhea 1005/−295) rather than the blog's table.
