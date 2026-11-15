# Curve quality and variable-font design space for rounded corners

Research note for Goeist Serif (and a retrofit of Goeist Sans/Mono). Scope: the continuity Goeist's fillets achieve, how to get curvature-continuous (G2) corners from cubic Béziers, what existing tools and rounded families actually do, and how a roundness axis could be built. Nothing here changes code.

Conventions: UPM 1000. $r$ is the fillet radius, $\theta$ the **turning angle** at a corner (0 means straight, 90° means a square corner). These are the same conventions as `classify_corner`/`make_corner` in `scripts/rounding.py`. $V$ is the original corner node. I computed every number marked *measured* or *computed* in this session, with throwaway Python scripts (not committed) run against the repo's sources, `fonts/`, `build/` or the URLs cited.

---

## 1. Continuity vocabulary

| Order | Geometric (shape only) | Parametric (depends on parameterization) | What you see |
|---|---|---|---|
| 0 | G0: the segments share an endpoint | C0 (identical) | any corner (a "blue" node in Glyphs) |
| 1 | G1: the tangent direction is shared | C1: the first-derivative *vector* is equal (both handles the same length) | no visible angle, but a highlight or curvature comb still jumps |
| 2 | G2: the curvature $\kappa$ is equal | C2: the second derivative is equal | the comb is continuous, with no "flat spot then bend" |
| 3 | G3: $d\kappa/ds$ is equal | C3 | the comb's *slope* is continuous |

The Glyphs tutorial [Harmonization](https://glyphsapp.com/learn/harmonization) gives the same G0–G3 ladder in type-design terms. It says G2 means Speed Punk combs of equal size on both sides of a node, and that G3 rarely matters in type. Jake Low's [Hobby curves](https://www.jakelow.com/blog/hobby-curves) article explains C1 vs G1: font outlines only need G-continuity, because their parameterization is never visible.

### 1.1 Curvature of a cubic

For $B(t)=\sum_{i=0}^{3}\binom{3}{i}(1-t)^{3-i}t^iP_i$:

$$\kappa(t)=\frac{B'(t)\times B''(t)}{|B'(t)|^3}\quad(\text{signed; }a\times b=a_xb_y-a_yb_x)$$

At $t=0$ we have $B'(0)=3(P_1-P_0)$ and $B''(0)=6(P_2-2P_1+P_0)$, so $B'\times B''=18\,(P_1-P_0)\times(P_2-P_1)$ and

$$\boxed{\kappa(0)=\tfrac23\,\frac{(P_1-P_0)\times(P_2-P_1)}{|P_1-P_0|^3}=\frac{2h}{3a^2}}$$

where $a=|P_1-P_0|$ is the handle length and $h$ is the signed distance of $P_2$ from the tangent line through $P_0,P_1$. The $t=1$ end is the mirror image: $\kappa(1)=\tfrac23\,(P_2-P_1)\times(P_3-P_2)/|P_3-P_2|^3$. Two consequences drive everything below:

- **A line has $\kappa=0$.** A curve joins a line with G2 iff $h=0$, i.e. $P_2$ lies on the line's extension. This is the "three points in a row" rule of Glyphs' [curve-to-line harmonization](https://glyphsapp.com/learn/harmonization) and of Figma's squircle construction ([Figma blog, fig. 11.1–11.2](https://www.figma.com/blog/desperately-seeking-squircles/)).
- **Curvature matching at a known end:** to make a cubic reach curvature $\kappa^*$ at $P_0$ with handle length $a$, place $P_2$ at distance $h=\tfrac32\kappa^*a^2$ from the tangent line.

A **curvature comb** draws $\kappa(t)$ as normals of length $\propto\kappa$. [Speed Punk](https://github.com/yanone/speedpunk) (Yanone, Apache-2.0, Glyphs/RoboFont) draws exactly this, and its README spells out the reading rule: "if the illustrations are of same distance from the on-curve point … the two curves are of continuous curvature."

### 1.2 Why Goeist's current fillets show a jump

A tangent arc of radius $r$ that meets a line is G1 with a curvature step from $0$ to $1/r$. The cubic arc approximation makes the step slightly *smaller* at the ends, but it is still a step (*computed*, $r=1$):

| $\theta$ | $\alpha=\frac{(4/3)\tan(\theta/4)}{\tan(\theta/2)}$ | $\kappa_{end}\cdot r$ | $\kappa_{max}\cdot r$ | depth $V\to$ curve, $/r$ |
|---|---|---|---|---|
| 30° | 0.655 | 0.9997 | 1.0001 | 0.035 |
| 60° | 0.619 | 0.9955 | 1.0016 | 0.155 |
| 90° | 0.552 | 0.9786 | 1.0080 | 0.414 |
| 110° | 0.486 | 0.9545 | 1.0176 | 0.743 |
| 135° | 0.369 | 0.9047 | 1.0394 | 1.613 |
| 150° | 0.274 | 0.8627 | 1.0598 | 2.864 |

Goeist Sans Regular: stem 86 and terminal radius $0.52\cdot86=44.7$ (from `build/Goeist/rounding-upright.json`), so the step is $\approx0.022$ unit⁻¹ at every exposed fillet end. Stem terminals are worse, because `make_corner` caps each trim at 48% of the adjacent edge. A square stem end of width $s$ gets $trim_{side}=0.52s$ and $trim_{end}=0.48s$, which gives an asymmetric cubic with $\kappa=1.74/s$ at the stem side and $2.21/s$ at the apex. The leftover flat ($0.04s\approx3.4$ units in Regular) adds a second pair of $2.21/s\to0$ steps (*computed*).

---

## 2. Curvature-continuous corner constructions

### 2.1 Superellipse (Piet Hein)

$|x/a|^n+|y/b|^n=1$. Hein's $n=2.5$ "superellipse" is documented in secondary sources ([Wikipedia: Superellipse](https://en.wikipedia.org/wiki/Superellipse)) `[unverified primary]`. Solving near the axis point $(a,0)$ gives $x\approx a(1-|y/b|^n/n)$, so $\kappa\propto|y|^{n-2}$:

- **$n>2$: $\kappa\to0$ at the axis points**, so cutting a quadrant and attaching straight edges there is G2.
- $n\ge4$: $d\kappa/ds\to0$ too, which is G3.
- $n=2.5$: G2, but $d\kappa/ds$ is unbounded at the join.

Superellipses are not Bézier-native and need fitting. Figma reports that the iOS icon shape is *not* a superellipse for any $n$ ([Figma](https://www.figma.com/blog/desperately-seeking-squircles/), citing [ApplyPixels](https://applypixels.com/the-hunt-for-the-squircle/)).

### 2.2 Clothoid / Euler spiral; Spiro

An Euler spiral has curvature linear in arc length, $\kappa(s)=s/(RL)$. A line → clothoid → arc → clothoid → line corner gives a trapezoidal curvature profile. Figma derives this and then abandons it: truncating the clothoid series to cubic order "performs very poorly when ξ is large" ([Figma §9](https://www.figma.com/blog/desperately-seeking-squircles/)). Raph Levien's thesis [*From Spiral to Spline*](https://levien.com/phd/thesis.pdf) ([UCB EECS-2009-162](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2009/EECS-2009-162.html)) builds interpolating splines from Euler-spiral pieces. These are G2 by construction, and G4 for the full Spiro spline. Its implementation is [Spiro](https://levien.com/spiro/) ([raphlinus/spiro](https://github.com/raphlinus/spiro), Apache-2.0), which emits Béziers. Levien's [spline-research](https://github.com/raphlinus/spline-research) and [Euler-spiral parallel curves](https://raphlinus.github.io/curves/2022/09/09/parallel-beziers.html) cover cubic fitting of spirals.

### 2.3 Apple continuous corners / Figma corner smoothing

- Apple ships `CALayerCornerCurve.continuous` ([docs](https://developer.apple.com/documentation/quartzcore/calayercornercurve/continuous); iOS 13 / macOS 10.15). Apple does not document the geometry. Swanson (genetic-algorithm fit) and Schwind (direct inspection of the iOS code) reverse-engineered it as **three Béziers per corner**, all cited by [Figma](https://www.figma.com/blog/desperately-seeking-squircles/).
- **Figma's scheme** ([blog §11–12](https://www.figma.com/blog/desperately-seeking-squircles/)): a smoothing parameter $\xi\in[0,1]$. The consumed edge length is $p=(1+\xi)q$, with $q$ the plain-rounding trim. The corner is a transition cubic, then a circular arc spanning $90°(1-\xi)$, then a mirrored transition cubic. Its first three control points are collinear, so $\kappa=0$ at the line. The shipped split is $a=2b$, and "ξ = 0.6 just about nails the iOS shape" (hence "iOS 60%").
- **Computed caveat.** I evaluated the open-source re-implementation [phamfoo/figma-squircle `draw.ts`](https://raw.githubusercontent.com/phamfoo/figma-squircle/main/src/draw.ts), which is not Figma's binary. It is G2 at the line but **not at the arc join**: $\kappa\cdot R$ at the transition/arc join is 1.56, 1.53, 1.47, 1.39 and 1.30 for $\xi=0.2,0.4,0.6,0.8,1.0$, against 1.0 on the arc. True G2 there needs $b=3(c^2+d^2)^{3/2}/(2Rd)$ (0.190 instead of 0.280 at $\xi=0.6$). The blog's own figure 12.4 shows a "spiky" profile, which is consistent with this.

### 2.4 Hobby, Tunni, harmonizers

- **Hobby** ([Hobby 1986, *Smooth, easy to compute interpolating splines*, DCG 1:123–140](https://doi.org/10.1007/BF02187690); METAFONT/MetaPost) chooses tangent angles so that *mock* curvature, a first-order approximation, is continuous, and sets handle lengths through tension. The result is G1 with approximate G2 ([Jake Low](https://www.jakelow.com/blog/hobby-curves)). Glyphs exposes Hobby nodes with leading/trailing tension in its API ([`GSHobbyNodeInfo`](https://docu.glyphsapp.com/Core/GlyphsCore/GSHobbyNodeInfo)). I could not verify a command literally named "Hobbyfy" `[unverified]`. Jens Kutilek's [Curve EQ](https://github.com/jenskutilek/Curve-Equalizer) offers Hobby-based adjustment.
- **Tunni lines** (Eduardo Tunni) connect a segment's two handles. Dragging the line scales both handles together to tune tension ([FontLab manual](https://help.fontlab.com/fontlab/7/manual/Tunni-Lines)). Linus Romer analyses the smoothness of Tunni curves in a [TypeDrawers thread (PDF)](https://typedrawers.com/discussion/5101/smoothness-of-tunni-curves). Tunni balancing is a G1 tension control, not a G2 guarantee.
- **Harmonizers**, per the [Glyphs harmonization guide](https://glyphsapp.com/learn/harmonization):
  - RMX Harmonizer ([Remix Tools](https://remix-tools.com/glyphsapp/tutorials), commercial) moves nodes and handles to reach G2.
  - Green Harmony moves the on-curve node; Grey Harmony and SuperTool move the handles.
  - mekkablue *Harmonise Curve to Line* maximizes the handle that faces a line.

  The same guide gives handle-length anchors (55% ≈ circle; type curves are usually 58–76%; 100% = handles meet at the tangent intersection). It also warns that maximized curve-to-line handles (a) complicate TrueType conversion, (b) must be maximized in **all** masters, or instances "hang", and (c) are rarely visible at text sizes.

### 2.5 One cubic, G2 to two lines — derivation

Use the handle direction of each line: $P_1=P_0+\alpha_a d_a\,t_0$ and $P_2=P_3-\alpha_b d_b\,t_1$, where $d_a$ and $d_b$ are the distances from $P_0$ and $P_3$ to the tangent intersection $V$. These are exactly `distance_a` and `distance_b` in `make_corner`. With §1.1:

- $\kappa(0)=0$ requires $P_2$ on the incoming line. $P_2$ is already on the outgoing line, so $P_2=V$, i.e. $\alpha_b=1$.
- $\kappa(1)=0$ requires $P_1=V$, i.e. $\alpha_a=1$.

**Rule: a fillet end is G2 with its line iff the *opposite* handle reaches $V$. Both ends are G2 iff $P_1=P_2=V$ ($\alpha=1$).** For general $\alpha$ (equal trims $d$):

$$\kappa(0)=\tfrac23\,\frac{(1-\alpha_b)\,d_b\sin\theta}{\alpha_a^2d_a^2}$$

At 90°, if we change $\alpha$ and rescale the trim to keep the **same depth** as the current circular fillet (the same ink removed at $V$), we get (*computed*, $r=1$):

| $\alpha$ | trim / circular trim | $\kappa_{end}\cdot r$ | $\kappa_{peak}\cdot r$ | note |
|---|---|---|---|---|
| 0.552 | 1.000 | 0.978 | 1.008 | current |
| 0.600 | 1.065 | 0.695 | 1.084 | |
| 0.644 | 1.133 | 0.505 | 1.166 | Open Runde, measured (§3.2) |
| 0.700 | 1.233 | 0.331 | 1.267 | |
| 0.760 | 1.362 | 0.203 | 1.368 | |
| 0.850 | 1.616 | 0.086 | 1.500 | |
| 1.000 | 2.343 | 0.000 | 1.609 | exact G2 |

$\alpha=1$ at equal depth over all angles: the trim is 2.0× (30°), 2.1× (60°), 2.3× (90°), 2.5× (110°), 2.9× (135°) and 3.2× (150°) the circular trim, with peak $\kappa\cdot r$ of 1.36–3.24 (*computed*). Exact G2 with one cubic concentrates curvature mid-corner and eats much more edge. **Measured on upstream Geist:** with the existing 48% edge cap, only 32.7% of the 1519 convex line–line corners in Regular have room for the current circular trim. 25.6% have room at $\alpha=0.70$ and 10.7% at $\alpha=1$; Black gives 24.4%, 18.6% and 3.7%. Exact single-cubic G2 is therefore impossible at most corners; the realistic options are either a partial-$\alpha$ compromise or the terminal-cap construction below.

### 2.6 Terminal cap (two fillets that consume a shared edge)

Stem ends, serif ends and slab ends are a short edge with two convex corners. Take an end of half-width $w$, end edge $y=0$, stem side $x=w$ and apex $A=(0,0)$, and use one cubic per corner:

$$P_0=(w,-s),\quad P_1=(w,-s+fs),\quad P_2=V=(w,0),\quad P_3=A$$

$P_0,P_1,P_2$ are collinear, so $\kappa=0$ at the stem side (G2). The mirrored cubic from the other corner meets it at $A$ with an equal $\kappa_A=\tfrac23(1-f)s/w^2$ (G2 by symmetry). The leftover line is zero-length.

*Computed:* $s=1.25w$, $f=0.3$ gives the profile $0\to1.33/w$ at the shoulders $\to0.58/w$ at the apex. That is a superelliptic profile like Nunito's (§3.2), but G2. **Point cost is unchanged** (one cubic per corner, as now). For a non-perpendicular end the symmetry argument fails; solve for equal $\kappa_A$ instead (§2.8).

### 2.7 Two cubics per corner (symmetric, G2 everywhere)

Split at the bisector point $M$ at depth $\delta$ from $V$. Each half is $Q_0$ (trim $d$ on the line), then $Q_1$ and $Q_2$ (both on the line, so $\kappa(Q_0)=0$), then $Q_3=M$, with the tangent at $M$ parallel to the chord. The triangle $V,Q_2,M$ has a right angle at $M$, so

$$|VQ_2|=\frac{\delta}{\sin(\theta/2)},\qquad |Q_2M|=\delta\cot(\theta/2),\qquad \kappa_M=\frac{2}{3}\,\frac{(1-f)\,(d-|VQ_2|)\,\sin(\theta/2)}{\delta^2\cot^2(\theta/2)}$$

with $Q_1=Q_0+f(Q_2-Q_0)$. The mirror half gives equal $\kappa_M$, so the join is G2. Figma-like parameterization: $d=(1+\xi)\,r\tan(\theta/2)$ and $\delta=r(\sec(\theta/2)-1)$ (the current depth). At 90°, picking the $f$ that minimizes the steepest $d\kappa/ds$ with a monotone half-profile (*computed*):

| $\xi$ | trim/$r$ | $f$ | $\kappa_{peak}\cdot r$ (at $M$) | $\max\lvert d\kappa/ds\rvert\cdot r^2$ |
|---|---|---|---|---|
| 0.2 | 1.2 | 0.29 | 1.198 | 11.3 |
| 0.4 | 1.4 | 0.43 | 1.275 | 1.51 |
| 0.6 | 1.6 | 0.51 | 1.365 | 1.73 |
| 1.0 | 2.0 | 0.61 | 1.515 | 2.30 |

$\xi\approx0.4$ is the sweet spot: a near-triangular profile for 40% more trim. This adds **+6 nodes per corner** (currently +3).

### 2.8 Curve neighbours: geometric Hermite interpolation

Given end tangents $t_0,t_1$, signed curvatures $k_0,k_1$ and $D=P_3-P_0$, with $P_1=P_0+a\,t_0$ and $P_2=P_3-b\,t_1$:

$$\tfrac32k_0a^2=t_0\times D-b\,(t_0\times t_1),\qquad \tfrac32k_1b^2=D\times t_1-a\,(t_0\times t_1)$$

This is the system of [de Boor, Höllig, Sabin 1987, *High accuracy geometric Hermite interpolation*, CAGD 4:269–278](https://doi.org/10.1016/0167-8396(87)90002-1). It reduces to a quartic in $a$ with 0–3 admissible roots. With $k_0=k_1=0$ it returns $a=d_a$ and $b=d_b$, which is §2.5's $\alpha=1$.

*Computed:* I tested a line meeting a quarter-circle-like cubic (radius ≈100) at 90° with $r=44.7$. Over all trims the **single** cubic solutions are poor, with a near-zero handle on the line side and a peak $\kappa\cdot r\ge2.19$. A **two-cubic** split worked: split at the G1 fillet's midpoint and do a 1-D search over $\kappa_M$. It is exactly G2 at both ends, with a peak $\kappa\cdot r$ of 1.50–1.55, the same as the G1 reference at the same trims. **Measured share of corners with curve neighbours** in upstream Geist Regular (upright): 1519 line–line, 145 curve–line, 143 line–curve, 5 curve–curve, out of 1812. A serif will have many more, at brackets and bowls meeting serifs `[expected; count once Geist Serif sources are vendored]`.

### 2.9 Cost: points and TrueType

- **Cubic sources/OTF.**
  - §2.5 at any $\alpha$, and §2.6: +3 nodes per corner, same as now.
  - §2.7: +6 nodes per corner. Goeist Sans upright would grow from 38,830 to ≈56.9k nodes.
  - Figma-style transition–arc–transition: +9 nodes per corner.
- **TrueType/VF** go through cu2qu (`fontTools.cu2qu`, default `max_err` = 0.001 em, see [docs](https://fonttools.readthedocs.io/en/latest/cu2qu/index.html)). Quadratics have nonzero endpoint curvature unless degenerate, so **G2 at a line survives only within tolerance**. Quadratic segments per 90° corner at 1 unit (*measured* with `curve_to_quadratic`):
  - Circular fillet: 3.
  - $\alpha=1$ at equal depth: 4, 5 and 6 at $r$ = 16.6, 44.7 and 100.
  - Two-cubic at $\xi=0.4$: 6 (3+3).
  - `curves_to_quadratic` keeps masters compatible by taking the max over masters. Thin+Regular at $\alpha=1$ gives 5.

### 2.10 Python sketch (not committed)

```python
import math
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def add(a, v, s=1.0): return (a[0] + v[0] * s, a[1] + v[1] * s)
def cross(a, b): return a[0] * b[1] - a[1] * b[0]

def kappa_start(P):  # signed curvature at t=0: (2/3)|P0P1 x P1P2| / |P0P1|^3
    d = sub(P[1], P[0]); return (2 / 3) * cross(d, sub(P[2], P[1])) / math.hypot(*d) ** 3

def kappa_end(P):    # signed curvature at t=1
    d = sub(P[3], P[2]); return (2 / 3) * cross(sub(P[2], P[1]), d) / math.hypot(*d) ** 3

def fillet(p, a, da, q, b, db, alpha_a, alpha_b):
    """make_corner generalised: G2 at p iff alpha_b == 1, G2 at q iff alpha_a == 1."""
    return (p, add(p, a, alpha_a * da), add(q, b, -alpha_b * db), q)

def two_cubic_corner(theta, r, xi, f):
    """Symmetric G2 corner (section 2.7), V at origin, incoming along +x, left turn."""
    d, delta = (1 + xi) * r * math.tan(theta / 2), r * (1 / math.cos(theta / 2) - 1)
    n = (-math.sin(theta / 2), math.cos(theta / 2))
    M = (n[0] * delta, n[1] * delta); Q2 = (-delta / math.sin(theta / 2), 0.0)
    Q0 = (-d, 0.0); Q1 = (Q0[0] + f * (Q2[0] - Q0[0]), 0.0)
    mirror = lambda p: (2 * (p[0] * n[0] + p[1] * n[1]) * n[0] - p[0],
                        2 * (p[0] * n[0] + p[1] * n[1]) * n[1] - p[1])
    return (Q0, Q1, Q2, M), tuple(mirror(p) for p in (M, Q2, Q1, Q0))

def g2_hermite(p, t0, k0, q, t1, k1, samples=400):
    """de Boor-Hollig-Sabin: all cubics p->q with tangents t0,t1 and curvatures k0,k1."""
    D, c = sub(q, p), cross(t0, t1); e0, e1 = cross(t0, D), cross(D, t1)
    if abs(c) < 1e-12: return []
    b_of = lambda a: (e0 - 1.5 * k0 * a * a) / c
    f = lambda a: 1.5 * k1 * b_of(a) ** 2 + c * a - e1
    out, hi = [], 2 * math.hypot(*D); x0, f0 = 1e-9, f(1e-9)
    for i in range(1, samples + 1):
        x1 = hi * i / samples; f1 = f(x1)
        if f0 * f1 <= 0:
            lo, up = x0, x1
            for _ in range(60):
                mid = (lo + up) / 2
                lo, up = (lo, mid) if f(lo) * f(mid) <= 0 else (mid, up)
            a = (lo + up) / 2; b = b_of(a)
            if b > 0: out.append((p, add(p, t0, a), add(q, t1, -b), q))
        x0, f0 = x1, f1
    return out
```

---

## 3. Smooth-corner tools and rounded families in practice

### 3.1 Tools

| Tool | Mechanism | Continuity / caveats |
|---|---|---|
| Figma corner smoothing | Radius plus smoothing $\xi$ (§2.3); 60% ≈ iOS | G2 at the line; the re-implementation is not G2 at the arc join (computed) |
| Glyphs *Round Corners* filter | `Filter > Round Corners`, or the non-destructive instance parameter `RoundCorner; <radius>; <visual corrections 0/1>`. Rounds only outward ("black") corners; a negative radius rounds inner corners ([tutorial](https://glyphsapp.com/learn/rounded-corners)) | Per-corner radius; the curve shape is undocumented `[unverified]` |
| Glyphs *Rounded Font* filter | "applies elliptical rounding *to the stem*", using the master's first vertical stem; `RoundedFont; <stem>` ([tutorial](https://glyphsapp.com/learn/rounded-corners)) | Whole-terminal (cap) rounding, as in §2.6 |
| Glyphs corner components | `_corner.*` open-path glyphs injected at nodes, with `origin`/`left`/`right` anchors and intermediate layers for scaled variants. "They interpolate and export in variable fonts" ([tutorial](https://glyphsapp.com/learn/reusing-shapes-corner-components)) | You draw the continuity yourself; good for serifs and ink traps |
| FontLab Smart Corners | A live effect on a node: R > 0 rounds, R < 0 makes an ink trap. Converted to regular curves on export ([manual](https://help.fontlab.com/fontlab/7/manual/Using-Smart-Corners)) | Curve shape undocumented `[unverified]` |
| RMX Harmonizer / Tuner / Scaler | Harmonizer moves nodes and handles toward G2 while keeping the shape ([Glyphs guide](https://glyphsapp.com/learn/harmonization), [Remix Tools](https://remix-tools.com/glyphsapp/tutorials)) | Commercial; manual pass |
| Speed Punk | Curvature combs ([repo](https://github.com/yanone/speedpunk), Apache-2.0) | Diagnostic only |

### 3.2 How rounded families were made (measured where possible)

- **Open Runde** ([repo](https://github.com/lauridskern/open-runde), OFL-1.1 per GitHub license metadata). Its README says it is "made entirely with the rounded corners tool of Glyphs Mini" from Inter, ships four weights as **separate `.glyphs` files** with no masters, and "Can you make it a variable font? → Probably not."
  - *Measured* on `OpenRunde-Regular.otf` (UPM 2816): stem corners are 90-unit 90° fillets with **handles at 64.4% of the distance to the tangent intersection**, against 55.2% for a circle. That gives $\kappa_{end}\cdot trim=0.57$ (G1, about 40% smaller step than a circle) and a peak of 1.32. The radius is ≈0.38 of the `l` stem (236), with flats left between the fillets.
- **Nunito / Nunito Sans.** The direction is the reverse of the assumption: "The project began with Nunito, created by Vernon Adams as a rounded terminal sans … Jacques Le Bailly extended it … and an accompanying regular non-rounded terminal version, Nunito Sans" ([google/fonts DESCRIPTION](https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/DESCRIPTION.en_us.html)). Nunito's [source](https://github.com/googlefonts/nunito) is one hand-drawn `Nunito.glyphs` with `wght` and `ital` axes.
  - *Measured* on the `i`/`l`/`n` terminals in the first master (stem 42): each cap is two cubics from stem to apex. $\kappa$ jumps $0\to0.0272$ at the stem, peaks at 0.058 near the 45° shoulder, and falls to 0.032 at the apex. That is a **superelliptic cap, still G1 at the stem**. Normalized jump: $\Delta\kappa\cdot$stem ≈ 1.14, against Goeist Sans ≈ $0.98/0.52\approx1.88$.
- **Fraunces** ([repo](https://github.com/undercasetype/Fraunces), OFL-1.1). An Old Style "soft-serif" "inspired by … Windsor, Souvenir, and the Cooper Series" (README). This is the closest open analogue to the Souvenir brief.
  - Axes: `opsz` 9–144, `wght` 100–900, `SOFT` 0–100 (labels Sharp, Soft, SuperSoft; designspace default 0) and `WONK` 0–1 (binary). The `opsz`/`wght` axes carry avar maps.
  - **Masters:** 8 per style = opsz {9, 144} × SOFT {0, 100} × wght {Thin, Black} ([`sources/Roman/Fraunces.designspace`](https://github.com/undercasetype/Fraunces/tree/master/sources/Roman)). Some masters were generated with `ScaleAndInterpolate.py`, followed by "a great deal of manual corrections" ([production notes](https://github.com/undercasetype/Fraunces/tree/master/sources)).
  - *Measured* on `n.glif`, 144pt Black. The **Sharp master is not sharp**: its serif corners already carry 6–10 unit fillets (e.g. `1126,0 → 1136,8`), so SOFT interpolates between non-degenerate structures. SOFT also changes much more than corners: the advance goes from 1124 to 1153, serif and bracket geometry changes (the stem/bracket join moves from y = 64 to 266), and so does the inner shape. **SOFT is a drawn style axis, not a fillet-radius axis.**
- **Google Sans Flex** ([repo](https://github.com/googlefonts/googlesans-flex)): six axes including `ROND` 0–100 (default 0), quadratic sources, compiled with fontc.

---

## 4. Variable fonts: terms, axes, compatibility, a roundness axis

### 4.1 Terms

- **Design space:** the n-dimensional space spanned by the axes.
- **Axis:** a tag, min/default/max values and a name.
- **Master / source:** a drawn or generated outline set at a location.
- **Instance:** any location. *Named instances* are listed in `fvar`.
- **Default instance:** the outlines stored in `glyf`/`CFF2`; other locations come from deltas.

User coordinates are normalized to −1/0/+1 at min/default/max, and then optionally remapped by `avar` ([OpenType avar, 1.9.1](https://learn.microsoft.com/en-us/typography/opentype/spec/avar); [variations overview](https://learn.microsoft.com/en-us/typography/opentype/spec/otvaroverview)).

### 4.2 Registered vs custom axes

- [OpenType axis registry](https://learn.microsoft.com/en-us/typography/opentype/spec/dvaraxisreg): `ital`, `opsz`, `slnt`, `wdth`, `wght`. "Foundry-defined tags must begin with an uppercase letter … and must use only uppercase letters or digits. Registered axis tags must not use that pattern."
- The **Google Fonts axis registry** ([googlefonts/axisregistry](https://github.com/googlefonts/axisregistry/tree/main/Lib/axisregistry/data)) standardizes custom tags for GF onboarding. Relevant entries, read from the `.textproto` files:

| Tag | Name | Range (default) | Definition (abridged) | Origin / users |
|---|---|---|---|---|
| `ROND` | Roundness | 0–100 (0) | "from angular defaults (0%) to … increasingly rounded (up to 100%)" | "internal project"; used by Google Sans Flex, Kode Mono, Wavefont, Doto, Tiny5 (google/fonts `METADATA.pb` search) |
| `SOFT` | Softness | 0–100 (0); Sharp 0, Soft 50, SuperSoft 100 | "letterforms … more and more soft and rounded" | Fraunces |
| `CASL` | Casual | 0–1 (0) | stroke curvature, contrast, terminals: Linear → Casual | Recursive |
| `ELSH` | Element Shape | 0–100 (0) | "In modular fonts … controls the shape of the element" | Handjet |
| `ELGR` | Element Grid | 1–2 (1) | elements per grid unit (modular) | Handjet |
| `ELXP` | Element Expansion | 0–100 (0) | elements move apart | Bitcount |
| `SHRP` | Sharpness | 0–100 (0) | "angular or blunt … to increasingly sharped" | Geologica |
| `INFM` | Informality | 0–100 (0) | formal → informal | Shantell Sans |
| `FLAR` | Flare | 0–100 (0) | stem terminals straight → swelling | — |
| `CTRS` | Contrast | −100–100 (0) | thin-stroke thinning; 100 = hairlines vanish | — |

Per the registry, `ELSH` is defined for *modular* fonts. If Geist Serif uses `ELSH` for its dot shape (see `research/geist-serif.md`), that is a looser reuse of the tag `[unverified here]`.

**"Major axes"** can mean two things:
1. The five **registered** axes above, which apps understand: CSS `font-weight`/`font-stretch`/`font-style`/`font-optical-sizing` map to `wght`/`wdth`/`slnt`+`ital`/`opsz`.
2. The **master axes** of a project, i.e. the dimensions along which masters are placed. Upstream Geist has a single `wght` axis with masters at 100/400/900 (`fontinfo.plist` Axis Location), and Goeist inherits it. A roundness axis would be a second, custom master axis, reached in CSS only through `font-variation-settings: "ROND" n`.

### 4.3 avar / avar2 / STAT

- **avar v1:** a piecewise-linear per-axis remap. The Microsoft spec page (OpenType 1.9.1) still defines `majorVersion = 1` only.
- **avar v2** ([boring-expansion spec](https://raw.githubusercontent.com/harfbuzz/boring-expansion-spec/main/avar2.md)) adds a `DeltaSetIndexMap` + `ItemVariationStore`, so each axis value can depend on *all* axes. Use cases: "warped variable font designspaces", parametric fonts. Renderer support is narrower than v1 `[verify per target]`, so do not depend on it for Goeist.
- **STAT** ([spec](https://learn.microsoft.com/en-us/typography/opentype/spec/stat)) names axis values for UIs. For `ROND`: 0 "Sharp", 100 "Rounded", with an elidable flag on the family's default value.

### 4.4 Interpolation compatibility

Hard rule: "corresponding glyph outlines must be point-compatible: they must have the same number of contours and the same number of points in each contour" ([overview](https://learn.microsoft.com/en-us/typography/opentype/spec/otvaroverview)). In practice the same order, start points, directions, node types, components and anchors are also required ([Glyphs, Multiple Masters part 2](https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)). [`fontTools.varLib.interpolatable`](https://fonttools.readthedocs.io/en/latest/varLib/interpolatable.html) audits this.

**Soft rule (kinks):** a kink happens when three points form a smooth connection, "angles are different in the masters, [and] ratios between the points are different" ([same Glyphs tutorial](https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)). Algebraically, master $m$ has handles $N_m-a_mu_m$ and $N_m+b_mu_m$. The interpolated handles are parallel for every weight vector iff $b_m=c\,a_m$ for one $c$ across all masters, or iff $u_m$ is constant.

### 4.5 A roundness axis in this pipeline

- **Topology is already solved.** `write_contour` gives every master the union of selected corners. A layer lacking a fillet gets a zero-length cubic `(retained[-1],)*4`. A `ROND`=0 master is therefore "upstream + zero-length cubics at every rounded corner", which is exactly the existing support-cubic path.
- **Line–line corners interpolate exactly.** All four control points are $V+(P_i-V)$ in the rounded master and $V$ in the sharp one, so the instance at weight $w$ is $V+w(P_i-V)$: a similarity about $V$ with radius $w\cdot r$. The construction is preserved at every `ROND` value, so with $\alpha=1$, $P_1=P_2=V$ throughout, and G2 holds at every value. 84% of Regular's convex corners are line–line (§2.8).
- **Curve neighbours do not.** The retained segment interpolates between the full upstream cubic and its de Casteljau subsection. *Computed* for a line + quarter-circle-like cubic with $r=44.7$:
  - At $w=0.5$ the retained curve deviates 2.5 units from the original stroke, with a 15.4° tangent break at the fillet/curve join.
  - Worst break per interval: 24.8° with masters at {0, 100}; 12.3° / 2.7° with {0, 50, 100}; 6.1° / 1.2° / 0.8° / 0.6° with four steps; 3.0° then ≤ 0.6° with eight.
  - The first interval always carries the largest break, because the zero-length handle has no direction (and the fillet there is small).
- **Mitigations:**
  - Add intermediate `ROND` masters. Rounding is programmatic, so any radius scale can be generated exactly.
  - Make the `ROND`-min master non-degenerate, like Fraunces' Sharp master. A tiny radius (≈0.03 stem, ~3 units in Regular) means ROND=0 is no longer byte-identical to Geist.
  - Harmonize handle ratios across masters (§4.4).
- **Default location.** The family identity is rounded, so put the default (the `glyf` outlines non-variable apps see) at the rounded master and let ROND decrease toward sharp. The GF registry's default of 0 matters only for GF onboarding. A default at 0 would also put degenerate cubics in `glyf`. Glyphs' [harmonization guide](https://glyphsapp.com/learn/harmonization) notes that zero handles "pose a problem for some renderers" (its *Fix Zero Handles* entry).
- **avar.** Visual roundness is not linear in $r$: depth scales with $r$ and removed area with $r^2$. A v1 map such as user 25/50/75 → normalized 0.35/0.6/0.82 is a reasonable start `[heuristic; tune by eye]`.

---

## 5. What `scripts/rounding.py` achieves today

`make_corner` (lines 350–378):

1. `trim = radius·tan(θ/2)`, capped at 48% of each adjacent segment's length. `circular=True` (Mono) equalizes the trims and recomputes the radius; `SOFT` (Sans) caps each side independently, which gives **asymmetric trims at stem ends** (§1.2).
2. The adjacent segments are cut by de Casteljau (`section`), so the retained geometry is exact. The tangents `a` and `b` are taken from the retained pieces.
3. `distance_a` and `distance_b` are the distances from $p$ and $q$ to the tangent intersection. The handles are `alpha·distance` with `alpha = (4/3)tan(θ/4)/tan(θ/2)`, where θ is recomputed from `a`,`b`. With equal distances this is the standard circular-arc cubic.
4. `write_contour` marks the trim endpoints `smooth=True`. That is a Glyphs editing flag; compiled fonts ignore it.

**Continuity in each master: exactly G1** (collinear handles) at both fillet ends, with C∞ inside. **Curvature:** a step at every end, $\approx0.98/r$ at 90° line joins (table §1.2). Asymmetric trims give $\kappa(0)\propto d_b/d_a^2$. At curve neighbours the step is $|\kappa_{fillet}-\kappa_{curve}|$.

**Continuity in instances is not guaranteed. Measured:** I counted non-line–line joins with a tangent break of 3–20° (handles ≥ 30 units, so integer rounding contributes ≤ 1.4°) in the static OTFs.

| Weight | Role | Goeist breaks | max | Upstream Geist, same weight |
|---|---|---|---|---|
| Thin | master | 0 | — | 0 |
| Light | instance | 0 | — | 7 |
| Regular | master | 0 | — | 7 |
| SemiBold | instance | 447 | 18.1° | 7 |
| Bold | instance | 487 | 18.4° | 7 |
| Black | master | 1 | 4.3° | 1 |

Examples in Bold:
- `C` inner terminal: 6.8°. The handle ratio at the fillet/retained-curve join is 24:91 in Regular and 65:40 in Black.
- `gravecomb`/`grave` and every composite using them: 6.4°. The acute accents: 3.9°. The accent's long edge is 86 units in Regular but ≈15 in Black, so the 48% cap changes the trim ratio.

This is §4.4's kink rule. The fillet handle (stem-relative) and the retained handle (scaled by the de Casteljau parameter) change their ratio between Regular and Black. `verify.py` has no check for it.

**What a G2 upgrade needs:**
- **Per-side α (§2.5):** change one line, `alpha` → `alpha_a`, `alpha_b`. No new points; `write_contour` is unchanged. Exact G2 at an end needs the opposite α = 1, and is feasible only where the edge budget allows (§2.5 statistics). Partial α (0.65–0.75) gives approximate G2.
- **Terminal caps (§2.6):** detect two selected corners whose trims meet on one edge, emit each cubic with $P_2=V$, and make the shared edge zero-length. No new points. Every master must make the same cap/no-cap decision, or interpolation degrades. Decide it from the union, as `selected` already does.
- **Two-cubic corners (§2.7–2.8):** +3 extra nodes per corner. `write_contour` must emit `[off, off, on, off, off, on]` per selected corner. The support counterpart becomes six coincident points, i.e. two zero-length cubics. The node-type signature grouping in `round_font` still works, because every layer gets the same structure.
- **Compatibility:** any per-master choice of construction (cap vs not, one vs two cubics, local radius reduction) must be made per **corner across masters**, never per layer. Otherwise topology diverges (a hard failure) or kinks appear (soft).

---

## Implications for Goeist

Ranked by importance.

1. **Fix interpolation kinks before chasing G2.** SemiBold and Bold have 447 and 487 tangent breaks of 3–18° that no master has (§5). Goeist Serif (more curves, high contrast) will be worse.
   - Add a `verify.py` check: instantiate every source font at the midpoint of each master interval (e.g. wght 250, 650; `fontTools.varLib.instancer` on the VF, or interpolate the generated `.glyphs`). Assert that every join which is G1 in the masters has a tangent break < 0.5° where both handles are ≥ 10 units.
   - Fix A (preferred): after `prepare_corners`, **harmonize the handle ratio per join across masters.** Take $c$ as the median of $b_m/a_m$, then set $b_m=c\,a_m$ by scaling the fillet-side handle only (it is ours; the retained handle is upstream geometry). This exactly removes kinks at fillet joins (§4.4). Skip joins where a master has a zero-length support cubic, and report them.
   - Fix B (complementary): generate **intermediate masters** (brace layers at wght 700 at least, since Regular→Black is where breaks concentrate) by rounding the upstream interpolation at that location.
2. **Make continuity a profile parameter.** Add `tension` (α) to `Profile` and to `make_corner`, as `alpha_a`/`alpha_b`, and scale the trim to keep the current depth: $trim=\delta/\text{depth\_per\_trim}(\theta,\alpha)$ with $\delta=r(\sec\frac\theta2-1)$.
   - Recommended: Goeist Serif and Sans **α = 0.70**: the curvature step drops 66% (0.33/r against 0.98/r) for 23% more trim and a 26% higher peak (§2.5 table).
   - Mono keeps α = 0.552: circular is its round-nib identity.
   - When the 48% cap binds, reduce α toward 0.552 before shrinking the radius. This keeps the depth.
3. **G2 terminal caps for stem, serif and slab ends** (§2.6): $P_0$ at $s=1.25w$ down the side, $P_1$ at $f=0.3$, $P_2=V$, $P_3$ at the apex on the original edge. Exact G2 at the sides and at the apex, a Nunito-like superelliptic shoulder, no extra points, and no apex recession (better for Souvenir-like soft serif ends).
   - Gate on: two adjacent selected convex corners on one line edge, edge length ≤ 1.1 × the sum of the requested trims, and a near-perpendicular end (|θ₁−θ₂| < 10°).
   - For skewed ends, solve the apex curvature equality with §2.8 or fall back to rule 2.
4. **Curve neighbours.** About 16% of Sans corners, and most bracket/bowl joins in a serif. Keep them G1 with rule 2's α in v1 of Goeist Serif. In v2, implement the two-cubic Hermite fillet (§2.8, 1-D search on $\kappa_M$, fallback to G1, record every fallback in the report) only where the measured step $|\kappa_{fillet}-\kappa_{curve}|\cdot\text{stem}>1.0$. Cost: +3 nodes per such corner.
5. **Do not use one-cubic exact G2 (α = 1) globally.** It needs 2.3× the trim at 90° and fits only 11% (Regular) and 4% (Black) of line–line corners under the 48% cap, with a sharper apex (κ peak 1.61/r). Do not use Figma-style arcs either: the re-implementation is not G2 at the arc join, and it costs +9 nodes.
6. **Optional roundness axis: use the registered GF tag `ROND`** (0 angular → 100 round), not `SOFT`. Fraunces' SOFT is a drawn style axis that also changes widths and serifs.
   - Masters per weight: ROND {0, 50, 100}. Generate 25/75 too if curve-neighbour breaks exceed 1° (§4.5 shows ≤ 2.7° above 50 with three masters, ≤ 1.2° with five).
   - Upstream has three `wght` masters, so that is 9–15 masters per style. gvar size grows roughly with the number of non-zero delta sets (expect ≈2× for ROND {0, 100}) `[estimate]`.
   - Put the **default at ROND 100** (rounded identity, no degenerate `glyf` cubics). Add a STAT entry with 100 "Rounded" (elidable) and 0 "Sharp", and an avar v1 map for perceptual linearity (§4.5). Avoid avar2.
   - Risks:
     - ROND 0 equals Geist outlines (fine under OFL: no Reserved Font Name is declared in upstream `OFL.txt`; the family name stays Goeist).
     - Zero-length handles at ROND 0. Validate with FontBakery/OTS and target renderers, or use a 0.03-stem floor as Fraunces effectively does.
     - Kinks at curve neighbours (needs rule 1's check across the ROND axis too).
     - Build time and file size.
     - Static exports stay ROND 100 only.
7. **TrueType:** G2 survives cu2qu only approximately. Partial-α and cap fillets cost about 1–2 more quadratic segments per corner at 1-unit tolerance (§2.9). Keep the default `max_err`, and check the VF size delta in `verify.py` against a budget.
8. **Measure, don't eyeball.** Extend the rounding report:
   - per-master histograms of $\Delta\kappa\cdot\text{stem}$ at every fillet end (target for Sans/Serif: median < 0.4, from ≈1.9 today);
   - the cap and Hermite fallback counts;
   - the instance-kink count from rule 1.

   Use Speed Punk only for spot checks.
