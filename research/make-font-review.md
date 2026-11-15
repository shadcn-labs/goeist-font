# Goeist against the make-font skill

Review of Goeist Sans, Goeist Mono and Goeist Serif (fonts built 2026-11-15) against
[arla6ka/design.how `skills/make-font`](https://github.com/arla6ka/design.how/blob/main/skills/make-font/SKILL.md)
and its references (`checks.md`, `licensing.md`, `spacing.md`, `font-book.md`).

The skill fits an open base font to measurements of liked fonts (width classes, spacing passes). Goeist instead
modifies Geist's own outlines in place, so the measure, targets, foundation, fit and space steps have no direct
counterpart. Its provenance and licensing rules, its gates and its specimen book do apply.

## Holds

| Skill rule | Goeist | Evidence |
| --- | --- | --- |
| Never copy reference outlines | All outlines come from Geist (OFL 1.1, no Reserved Font Name). Souvenir, Diatype and Open Runde are visual references; OFL research fonts were measured outside the repo | `research/rounded-serif-references.md` |
| OFL travels; base copyright kept in name ID 0; IDs 13/14 | Yes, ours first, upstream after | name table dump |
| No trademark record (ID 7) | None | name table dump |
| No base name in non-`name` tables | None of "Geist", "Diatype", "Souvenir" in any other table, ASCII or UTF-16 | byte scan |
| Win ascent/descent cover every glyph | Sans 1088/262 vs 1058/−240; Mono 1088/394 vs 1058/−394; Serif 1128/277, exactly equal to its extremes | glyph bounds |
| Widths, metrics and kerning gates | Pass by construction: advances, cmap, GPOS and shaping equal the unrounded baseline | `verify.py` |
| Collision guard, text (6 units) | Sans and Mono Regular: 0 pairs (unrounded Geist: 1, `7Y`) | pair scan, kerning on, rows 4 units apart |

## Gaps

| # | Skill rule | Goeist | Severity |
| --- | --- | --- | --- |
| 1 | Collision guard, display (4 units) | Goeist Serif: 161 pairs under 4, 104 touching. Upstream Geist Serif already has 200 by design (serif points meeting in AA, VV), but 21 pairs are new (`yt` −11, `wt` −9, `wf` −6, `vt` −5, `vw`, `vv`, `0v`, `Vi`) and `dA` went from +3 to −17: the thickened tips add ink outside the drawn serif | High |
| 2 | Kink criterion: a curve that kinks in a mix goes back a step | Sans and Mono intermediate weights kink at rounded joins (447–487 tangent breaks in SemiBold/Bold statics; `interpolatable` 25/26/8/15 against 0 in the baseline) | High |
| 3 | No reference name in README or book | README and proof footer name ABC Diatype and ITC Souvenir (commercial), Fraunces, Open Runde | Medium, owner's policy |
| 4 | No base name outside the copyright line | Name ID 10 credits "Vercel Geist …"; `verify.py` requires it | Low, owner's policy |
| 5 | New name shares no word with the base | "Goeist" is one letter from "Geist" | Low, owner's policy |
| 6 | ID 9: base designers, then modifier | ID 9 is the modifier only; base designers are in ID 10 | Low |
| 7 | `FONTLOG.txt` with every modification and its numbers | None | Medium |
| 8 | Font book: metrics, character set, spacing strings, PDF, fallback and overflow checks | Proof page has text, waterfall, scripts and atlases; no metrics, character-set or spacing pages, no PDF | Medium |
| 9 | ttx dump-and-reload validity | Not run | Low |
| 10 | Spacing re-checked after changes | Rounded apexes pull ink in (A, V, `*`, `>`), spacing not compensated | Medium |

Not applicable: reference measurement, targets, the 3 % stretch limit, class sidebearings.

## Order of fixes

1. Collision guard for Goeist Serif, gated in `make test` against the baseline. Done.
2. Kinks in Sans and Mono intermediate weights. Done for statics; variable fonts partly.
3. `FONTLOG.txt` per family. Done.
4. Metrics, spacing and character-set sections in the proof. Done.
5. Items 3–6 and 10 wait on owner decisions.

## Fixes made

See CONTRIBUTING.md (Verification, Goeist Serif) for the mechanics; numbers below are from the rebuilt fonts.

| Gap | Fix | Result |
| --- | --- | --- |
| 1 Collision guard | `scripts/collisions.py`: every pair of encoded characters shaped with kerning, ink read in 4-unit rows. Goeist Serif opens every pair now closer than both 4 units and its Geist Serif gap with one added `kern` lookup (never closes); `verify.py` gates all three families against their baselines (6 units text, 4 display, 3-unit outline tolerance) | Serif Regular: 368 glyph pairs opened (most accented forms of ~40 letter pairs), 1–20 units, `dA` the widest. Sans and Mono: 0 regressions in all 36 statics. The guard is stripped before GPOS/shaping parity, and its recorded pair count must match |
| 2 Kinks | Statics are built from a second source in which each named weight (200–800) is rounded from its own interpolated outline; widths and anchors are mixed in the baseline instancer's arithmetic, so advances and GPOS stay identical to Geist. The variable fonts keep three masters (extra masters moved advances by a unit through HVAR rounding); there, fillet joins on turning curves get one handle ratio in every master where that needs less than a 1.6× handle change | Static SemiBold/Bold now break tangents at the same rate as the master weights (103/116 joins over 3°, against 130 in Regular: TrueType/CFF integer noise on short handles). Variable-font instances still kink between masters: 499 joins over 3° at wght 550 against 288 at the 400 master; 873 of 1,107 upright joins keep circular handles |
| 3 FONTLOG | `build.py` writes `fonts/<Family>/FONTLOG.txt` (base, licence, profile, stems, corner counts, serif and guard numbers); the release zip ships it | Present for all three families |
| 4 Font book | Proof page gains vertical metrics (Hxdop with labelled lines and advances), spacing strings at 48 px, and the full character set set in the font | Rendered in Chromium for Sans and Serif, no console errors. No PDF and no overflow check yet |
| Open corners | Ink geometry erases Glyphs open corners (glyphsLib's own pen) in every family, so loop corners are construction, not ink | Shared with Goeist Serif's overlap pass |

Not done: gaps 3–6 and 10 (owner decisions on naming and references; spacing compensation for rounded apexes), gap 9 (ttx round-trip), a PDF font book, and kink-free variable fonts. The serif guard count (368 pairs) is above make-font's 150 health limit: it reflects the 26-unit tips; a thinner tip (22) would need fewer.
