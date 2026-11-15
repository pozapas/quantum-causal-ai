"""L5-07 Measurements and instruments: four 3Blue1Brown-style scenes.

ProjectRenormalize  |psi> = (1/2)|0> + (sqrt3/2)|1> in the real amplitude plane: the Born rule as a squared
                    shadow, then the Lueders update as projection followed by renormalization; then the same
                    state measured in the X basis (p(+) = (2 + sqrt3)/4 = 0.933).
TrinePOVM           ThreeDScene: the three trine effects E_k = (1/3)(I + n_k . sigma) on the Bloch sphere and
                    live bars p(k) = (1 + n_k . r)/3 while the state r sweeps the x-z great circle.
SameEffectsDifferentInstruments
                    three apparatuses with identical outcome probabilities (the Z effects on |+>) but different
                    conditioned states; a later measurement in the next laboratory tells them apart.
WeakToStrong        the Lueders instrument of E_pm = (I pm eps Z)/2 on |+>: conditioned states stay on the circle at
                    (sqrt(1 - eps^2), pm eps), the average loses coherence sqrt(1 - eps^2); then repeated weak
                    measurements (eps = 0.3) walk z to +1 or -1 (seeded trajectories).
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (Arc, Dot3D, DEGREES, DOWN, LEFT, ORIGIN, PI, RIGHT, UP, Arrow, Arrow3D, Axes, Circle, Create, DashedLine,
                   DecimalNumber, Dot, FadeIn, FadeOut, Indicate, Line, Rectangle, RoundedRectangle, Scene, Sphere,
                   SurroundingRectangle, ThreeDAxes, ThreeDScene, TracedPath, Transform, TransformMatchingTex,
                   ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ---- numbers shared with the lesson text ------------------------------------------------------
A0, A1 = 0.5, math.sqrt(3) / 2                       # amplitudes of |psi>
P0, P1 = A0 ** 2, A1 ** 2                            # 1/4, 3/4
assert abs(P0 - 0.25) < 1e-12 and abs(P1 - 0.75) < 1e-12
PPLUS = (A0 + A1) ** 2 / 2                           # (2 + sqrt3)/4
PMINUS = (A0 - A1) ** 2 / 2                          # (2 - sqrt3)/4
assert abs(PPLUS - (2 + math.sqrt(3)) / 4) < 1e-12 and abs(PPLUS + PMINUS - 1) < 1e-12
assert f"{PPLUS:.3f}" == "0.933" and f"{PMINUS:.3f}" == "0.067"

TRINE = [np.array([math.sin(2 * math.pi * k / 3), 0.0, math.cos(2 * math.pi * k / 3)]) for k in range(3)]
assert np.allclose(sum(TRINE), 0)


def trine_probs(r):
    return [(1 + float(n @ r)) / 3 for n in TRINE]


assert np.allclose(trine_probs(TRINE[0]), [2 / 3, 1 / 6, 1 / 6])
assert np.allclose(trine_probs(-TRINE[0]), [0, 1 / 2, 1 / 2])

EPS_WALK = 0.3
SEED = 5
N_TRAJ, N_STEPS = 16, 60


def walk(eps=EPS_WALK, z0=0.0, n=N_STEPS, seed=SEED, m=N_TRAJ):
    """Seeded trajectories of z under repeated Lueders measurements of E_pm = (I pm eps Z)/2."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(m):
        z, path = z0, [z0]
        for _ in range(n):
            plus = rng.random() < (1 + eps * z) / 2
            s = 1 if plus else -1
            z = (z + s * eps) / (1 + s * eps * z)
            path.append(z)
        out.append(path)
    return out


PATHS = walk()
UP_COUNT = sum(1 for p in PATHS if p[-1] > 0)
assert all(abs(p[-1]) > 0.9 for p in PATHS)
assert UP_COUNT == 8  # the lesson text states 8 of 16


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["0.933", "0.067", "p(k) = (1 + n_k \\cdot r)/3", "\\sqrt{1 - \\varepsilon^2}",
            "\\frac{z \\pm \\varepsilon}{1 \\pm \\varepsilon z}"]


# ---- scene 1 ----------------------------------------------------------------------------------
class ProjectRenormalize(Scene):
    def construct(self):
        title = label("Measuring = project, then renormalize", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        U = 2.7
        O = LEFT * 4.3 + DOWN * 1.9

        def pt(x, y):
            return O + RIGHT * U * x + UP * U * y

        ax0 = Arrow(pt(-0.08, 0), pt(1.18, 0), buff=0, color=MUTED, stroke_width=3, max_tip_length_to_length_ratio=0.06)
        ax1 = Arrow(pt(0, -0.08), pt(0, 1.18), buff=0, color=MUTED, stroke_width=3, max_tip_length_to_length_ratio=0.06)
        l0 = eq(r"|0\rangle", size=34, color=MUTED).next_to(ax0.get_end(), DOWN, buff=0.12)
        l1 = eq(r"|1\rangle", size=34, color=MUTED).next_to(ax1.get_end(), LEFT, buff=0.12)
        arc = Arc(radius=U, start_angle=0, angle=PI / 2, arc_center=O, color=GRID, stroke_width=2)
        self.play(Write(title), Create(ax0), Create(ax1), FadeIn(l0), FadeIn(l1), FadeIn(arc), run_time=1.5)

        psi = Arrow(O, pt(A0, A1), buff=0, color=VIOLET, stroke_width=6)
        plab = eq(r"|\psi\rangle = \tfrac12|0\rangle + \tfrac{\sqrt{3}}{2}|1\rangle", size=34, color=VIOLET)
        plab.move_to(RIGHT * 2.6 + UP * 2.45)
        self.play(Create(psi), Write(plab))

        # shadows on both axes
        d0 = DashedLine(pt(A0, A1), pt(A0, 0), color=BLUE)
        d1 = DashedLine(pt(A0, A1), pt(0, A1), color=AMBER)
        s0 = Line(O, pt(A0, 0), color=BLUE, stroke_width=9)
        s1 = Line(O, pt(0, A1), color=AMBER, stroke_width=9)
        self.play(Create(d0), Create(d1), run_time=1)
        self.play(Create(s0), Create(s1))
        b0 = eq(r"p(0) = \|P_0|\psi\rangle\|^2 = \left(\tfrac12\right)^2", size=34, color=BLUE)
        b0.move_to(RIGHT * 2.6 + UP * 1.45)
        b0b = eq(r"p(0) = \|P_0|\psi\rangle\|^2 = 1/4", size=34, color=BLUE).move_to(b0)
        b1 = eq(r"p(1) = \|P_1|\psi\rangle\|^2 = 3/4", size=34, color=AMBER).move_to(RIGHT * 2.6 + UP * 0.65)
        self.play(Write(b0))
        self.play(TransformMatchingTex(b0, b0b))
        self.play(Write(b1))
        self.wait(0.4)

        # outcome 0: keep only the shadow, then stretch it back to unit length
        note = label("outcome 0 recorded: keep the blue shadow", 26, MUTED).move_to(RIGHT * 2.6 + DOWN * 0.3)
        self.play(FadeIn(note), FadeOut(s1), FadeOut(d1), psi.animate.set_opacity(0.25))
        post = eq(r"|\psi_0\rangle = \frac{P_0|\psi\rangle}{\sqrt{p(0)}} = \frac{\tfrac12|0\rangle}{1/2} = |0\rangle",
                  size=34, color=INK).move_to(RIGHT * 2.6 + DOWN * 1.3)
        self.play(Write(post))
        self.play(s0.animate.put_start_and_end_on(O, pt(1, 0)), run_time=1.6)
        again = label("measure Z again: outcome 0 with probability 1", 24, MUTED).move_to(RIGHT * 2.6 + DOWN * 2.3)
        self.play(FadeIn(again))
        self.wait(1)

        # the same state in the X basis
        self.play(FadeOut(VGroup(note, post, again, b0b, b1, d0, s0)), psi.animate.set_opacity(1))
        dp, dm_ = np.array([1, 1]) / math.sqrt(2), np.array([1, -1]) / math.sqrt(2)
        axp = DashedLine(pt(*(-0.15 * dp)), pt(*(1.15 * dp)), color=CYAN)
        axm = DashedLine(pt(*(-0.15 * dm_)), pt(*(0.5 * dm_)), color=CYAN)
        lp = eq(r"|+\rangle", size=34, color=CYAN).next_to(pt(*(1.15 * dp)), RIGHT, buff=0.08)
        self.play(Create(axp), Create(axm), FadeIn(lp))
        amp = (A0 + A1) / math.sqrt(2)
        foot = pt(*(amp * dp))
        dpp = DashedLine(pt(A0, A1), foot, color=CYAN)
        sp = Line(O, foot, color=CYAN, stroke_width=9)
        self.play(Create(dpp), Create(sp))
        c1 = eq(r"\langle +|\psi\rangle = \frac{1 + \sqrt{3}}{2\sqrt{2}}", size=34, color=CYAN).move_to(RIGHT * 2.6 + UP * 1.3)
        c2 = eq(r"p(+) = \frac{2 + \sqrt{3}}{4} \approx 0.933", size=34, color=CYAN).move_to(RIGHT * 2.6 + UP * 0.2)
        c3 = eq(r"p(-) = \frac{2 - \sqrt{3}}{4} \approx 0.067", size=34, color=MUTED).move_to(RIGHT * 2.6 + DOWN * 0.8)
        self.play(Write(c1))
        self.play(Write(c2))
        self.play(Write(c3))
        self.play(sp.animate.put_start_and_end_on(O, pt(*dp)), run_time=1.4)
        msg = label("a different basis: different shadows, different post-states", 24, MUTED).move_to(RIGHT * 2.3 + DOWN * 2.0)
        self.play(FadeIn(msg))
        self.wait(1.5)


# ---- scene 2 ----------------------------------------------------------------------------------
class TrinePOVM(ThreeDScene):
    def construct(self):
        SH = RIGHT * 2.4            # the camera looks at x = 2.4, so frame-fixed text is shifted by the same amount
        self.set_camera_orientation(phi=72 * DEGREES, theta=-68 * DEGREES, frame_center=SH)
        R = 2.0
        sphere = Sphere(radius=R, resolution=(16, 16), fill_opacity=0.08, stroke_width=0.4)
        sphere.set_fill(BLUE, 0.07).set_stroke(GRID, 0.6)
        axes = ThreeDAxes(x_range=[-1.3, 1.3, 1], y_range=[-1.3, 1.3, 1], z_range=[-1.3, 1.3, 1],
                          x_length=2.6 * R, y_length=2.6 * R, z_length=2.6 * R, axis_config={"color": MUTED, "stroke_width": 2})
        great = Circle(radius=R, color=MUTED, stroke_width=2).rotate(PI / 2, RIGHT)   # x-z great circle

        def fixed(*mobs):
            for m in mobs:
                m.shift(SH)
            self.add_fixed_in_frame_mobjects(*mobs)

        title = label("A three-outcome measurement on one qubit", 32, INK, "BOLD").to_corner(UP + LEFT, buff=0.3)
        fixed(title)
        self.play(FadeIn(sphere), Create(axes), Create(great), Write(title), run_time=1.6)
        xl = eq("x", size=30, color=MUTED).move_to(axes.c2p(1.45, 0, 0))
        self.add_fixed_orientation_mobjects(xl)

        cols = [VIOLET, CYAN, AMBER]
        arrows = VGroup(*[Arrow3D(ORIGIN, axes.c2p(*n), color=c, thickness=0.02, resolution=8) for n, c in zip(TRINE, cols)])
        tri = VGroup(*[Line(axes.c2p(*TRINE[k]), axes.c2p(*TRINE[(k + 1) % 3]), color=MUTED, stroke_width=2)
                       for k in range(3)])
        self.play(*[Create(a) for a in arrows], Create(tri), run_time=1.5)
        offs = [np.array([0.55, 0, 0.0]), np.array([0.1, 0, -0.2]), np.array([-0.1, 0, -0.2])]
        nlabs = [eq(r"n_0 = |0\rangle" if k == 0 else f"n_{k}", size=30, color=c).move_to(axes.c2p(*(1.1 * n + o)))
                 for k, (n, c, o) in enumerate(zip(TRINE, cols, offs))]
        self.add_fixed_orientation_mobjects(*nlabs)
        self.play(*[FadeIn(m) for m in nlabs])

        f1 = eq(r"E_k = \tfrac23|\phi_k\rangle\langle\phi_k| = \tfrac13(I + n_k\cdot\sigma)", size=32)
        f2 = eq(r"\textstyle\sum_k E_k = I \iff n_0 + n_1 + n_2 = 0", size=30)
        f3 = eq(r"p(k) = (1 + n_k \cdot r)/3", size=32, color=INK)
        VGroup(f1, f2, f3).arrange(DOWN, buff=0.28, aligned_edge=LEFT).to_corner(UP + RIGHT, buff=0.35).shift(DOWN * 0.6)
        for f in (f1, f2, f3):
            fixed(f)
            self.play(Write(f))

        # state arrow (a light line with a ball, cheap to redraw) and live bars
        t = ValueTracker(0.0)

        def rvec():
            a = t.get_value()
            return np.array([math.sin(a), 0.0, math.cos(a)])

        state = always_redraw(lambda: Line(ORIGIN, axes.c2p(*rvec()), color=RED, stroke_width=7))
        tipball = always_redraw(lambda: Dot3D(axes.c2p(*rvec()), radius=0.08, color=RED, resolution=(6, 6)))
        self.play(FadeIn(state), FadeIn(tipball))
        base_y, bw, H = -3.0, 0.7, 2.4
        xs = [2.6 + 1.25 * k for k in range(3)]
        bars = []
        for k in range(3):
            b = Rectangle(width=bw, height=0.01, fill_color=cols[k], fill_opacity=0.85, stroke_width=0)
            b.move_to([xs[k], base_y, 0], aligned_edge=DOWN)
            bars.append(b)
        base = Line([xs[0] - 0.6, base_y, 0], [xs[2] + 0.6, base_y, 0], color=MUTED, stroke_width=2)
        blabs = VGroup(*[eq(f"p({k})", size=28, color=cols[k]).move_to([xs[k], base_y - 0.32, 0]) for k in range(3)])
        lim = DashedLine([xs[0] - 0.6, base_y + H * 2 / 3, 0], [xs[2] + 0.6, base_y + H * 2 / 3, 0], color=GRID)
        liml = label("2/3", 22, MUTED).next_to(lim, LEFT, buff=0.1)

        def upd_bar(k):
            def f(m):
                h = max(H * trine_probs(rvec())[k], 0.01)
                m.stretch_to_fit_height(h)
                m.move_to(np.array([xs[k], base_y, 0]) + SH, aligned_edge=DOWN)
            return f

        fixed(base, blabs, lim, liml, *bars)
        for k in range(3):
            bars[k].add_updater(upd_bar(k))
        self.play(FadeIn(base), FadeIn(blabs), FadeIn(lim), FadeIn(liml), *[FadeIn(b) for b in bars])

        def values(ps):
            g = VGroup(*[label(s, 24, INK).move_to([xs[k], base_y + H * p + 0.25, 0]) for k, (s, p) in enumerate(ps)])
            fixed(g)
            return g

        def note(text):
            n = label(text, 24, MUTED).to_edge(DOWN, buff=0.15).shift(LEFT * 3.0)
            fixed(n)
            return n

        v1 = values([("2/3", 2 / 3), ("1/6", 1 / 6), ("1/6", 1 / 6)])
        n1 = note("state along n₀: outcome 0 is most likely")
        self.play(FadeIn(v1), FadeIn(n1))
        self.wait(1.2)
        self.play(FadeOut(v1), FadeOut(n1))
        self.begin_ambient_camera_rotation(rate=0.06)
        self.play(t.animate.set_value(PI), run_time=6, rate_func=linear)
        v2 = values([("0", 0.0), ("1/2", 0.5), ("1/2", 0.5)])
        n2 = note("state along −n₀: outcome 0 never occurs")
        self.play(FadeIn(v2), FadeIn(n2))
        self.wait(1.2)
        self.play(FadeOut(v2), FadeOut(n2))
        self.play(t.animate.set_value(2 * PI), run_time=6, rate_func=linear)
        self.stop_ambient_camera_rotation()
        n3 = note("three outcomes on a qubit: not projective")
        self.play(FadeIn(n3))
        self.wait(1.5)


# ---- scene 3 ----------------------------------------------------------------------------------
class SameEffectsDifferentInstruments(Scene):
    def construct(self):
        title = label("Same outcome probabilities, different instruments", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title))
        rows = [("Lüders: keep projection", r"|0\rangle \text{ or } |1\rangle", VIOLET, ("1/2", "always")),
                ("record, then prepare |+>", r"|+\rangle", CYAN, ("1", "half the time")),
                ("record, then flip", r"|1\rangle \text{ or } |0\rangle", AMBER, ("1/2", "never"))]
        ys = [1.35, -0.1, -1.55]
        XI, XB, XP, XS, XX, XZ = -6.45, -3.85, -1.45, 0.65, 3.0, 5.2
        hdr = VGroup(label("input", 22, MUTED).move_to([XI, 2.45, 0]), label("instrument", 22, MUTED).move_to([XB, 2.45, 0]),
                     label("p(0), p(1)", 22, MUTED).move_to([XP, 2.45, 0]),
                     label("state passed on", 22, MUTED).move_to([XS, 2.45, 0]))
        self.play(FadeIn(hdr))
        groups = []
        for (name, out, col, _), y in zip(rows, ys):
            inp = eq(r"|+\rangle", size=32).move_to([XI, y, 0])
            box = RoundedRectangle(width=3.3, height=0.9, corner_radius=0.15, color=col, stroke_width=3).move_to([XB, y, 0])
            bl = label(name, 21, col).move_to(box)
            a1 = Arrow([XI + 0.35, y, 0], [XB - 1.65, y, 0], buff=0, color=MUTED, stroke_width=3,
                       max_tip_length_to_length_ratio=0.35)
            bars = VGroup(*[Rectangle(width=0.32, height=0.5, fill_color=col, fill_opacity=0.8, stroke_width=0)
                            .move_to([XP - 0.25 + 0.5 * k, y - 0.3, 0], aligned_edge=DOWN) for k in range(2)])
            hl = VGroup(eq("0", size=24, color=MUTED).next_to(bars[0], DOWN, buff=0.05),
                        eq("1", size=24, color=MUTED).next_to(bars[1], DOWN, buff=0.05))
            a2 = Arrow([XB + 1.65, y + 0.3, 0], [XS - 0.85, y + 0.3, 0], buff=0, color=col, stroke_width=3,
                       max_tip_length_to_length_ratio=0.08)
            o = eq(out, size=30, color=col).move_to([XS + 0.15, y, 0])
            g = VGroup(inp, a1, box, bl, bars, hl, a2, o)
            groups.append(g)
            self.play(FadeIn(VGroup(inp, a1, box, bl)), run_time=0.6)
            self.play(FadeIn(bars), FadeIn(hl), Create(a2), Write(o), run_time=0.8)
        same = SurroundingRectangle(VGroup(*[VGroup(g[4], g[5]) for g in groups]), color=RED, buff=0.12)
        sl = label("identical: 1/2, 1/2", 22, RED).next_to(same, DOWN, buff=0.08)
        self.play(Create(same), FadeIn(sl))
        f = eq(r"p(a) = \operatorname{Tr}(E_a\rho)", size=32, color=INK).move_to([-3.6, -3.1, 0])
        self.play(Write(f))
        self.wait(0.8)

        # next laboratory
        h2 = VGroup(VGroup(label("later X:", 22, MUTED), label("p(+)", 22, MUTED)).arrange(DOWN, buff=0.06).move_to([XX, 2.5, 0]),
                    VGroup(label("later Z matches", 22, MUTED), label("the record", 22, MUTED)).arrange(DOWN, buff=0.06)
                    .move_to([XZ, 2.5, 0]))
        sep = DashedLine([1.95, 2.9, 0], [1.95, -2.2, 0], color=GRID)
        self.play(FadeIn(h2), Create(sep), FadeOut(same), FadeOut(sl))
        for (_, _, col, (px, agree)), y in zip(rows, ys):
            self.play(Write(eq(px, size=32, color=col).move_to([XX, y, 0])),
                      FadeIn(label(agree, 24, col).move_to([XZ, y, 0])), run_time=0.7)
        f2 = eq(r"\rho_a = \mathcal{I}_a(\rho)/p(a)", size=32, color=RED).move_to([2.6, -3.1, 0])
        f2b = label("differs", 24, RED).next_to(f2, RIGHT, buff=0.2)
        self.play(Write(f2), FadeIn(f2b))
        self.play(Indicate(VGroup(f2, f2b), color=RED))
        self.wait(3.5)


# ---- scene 4 ----------------------------------------------------------------------------------
class WeakToStrong(Scene):
    def construct(self):
        title = label("From weak to strong: information costs coherence", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        R = 2.1
        C = LEFT * 3.9 + DOWN * 0.45
        disk = Circle(radius=R, color=MUTED, stroke_width=2).move_to(C)
        xa = Line(C + LEFT * (R + 0.2), C + RIGHT * (R + 0.2), color=GRID)
        za = Line(C + DOWN * (R + 0.2), C + UP * (R + 0.2), color=GRID)
        zl = eq(r"|0\rangle", size=28, color=MUTED).next_to(C + UP * R, UP, buff=0.08)
        z1 = eq(r"|1\rangle", size=28, color=MUTED).next_to(C + DOWN * R, DOWN, buff=0.08)
        xl = eq(r"|+\rangle", size=28, color=MUTED).next_to(C + RIGHT * R, RIGHT, buff=0.08)
        cap = label("Bloch disk (x, z)", 24, MUTED).move_to(C + LEFT * 1.6 + UP * 2.3)
        self.play(Write(title), Create(disk), Create(xa), Create(za), FadeIn(VGroup(zl, z1, xl, cap)), run_time=1.5)

        e = ValueTracker(0.0)

        def P(x, z):
            return C + RIGHT * R * x + UP * R * z

        start = Dot(P(1, 0), color=VIOLET, radius=0.09)
        self.play(FadeIn(start))
        kr = eq(r"E_\pm = \tfrac12(I \pm \varepsilon Z)", size=32).move_to(RIGHT * 2.9 + UP * 2.35)
        kr2 = eq(r"M_\pm = \sqrt{E_\pm}", size=32).next_to(kr, DOWN, buff=0.2)
        self.play(Write(kr), Write(kr2))

        def cx():
            return math.sqrt(max(1 - e.get_value() ** 2, 0))

        plus = always_redraw(lambda: Dot(P(cx(), e.get_value()), color=BLUE, radius=0.09))
        minus = always_redraw(lambda: Dot(P(cx(), -e.get_value()), color=AMBER, radius=0.09))
        chord = always_redraw(lambda: DashedLine(P(cx(), e.get_value()), P(cx(), -e.get_value()), color=MUTED))
        avg = always_redraw(lambda: Dot(P(cx(), 0), color=RED, radius=0.08))
        self.add(chord, plus, minus, avg)
        leg = VGroup(VGroup(Dot(color=BLUE, radius=0.07), label("after +", 24, BLUE)).arrange(RIGHT, buff=0.1),
                     VGroup(Dot(color=AMBER, radius=0.07), label("after -", 24, AMBER)).arrange(RIGHT, buff=0.1),
                     VGroup(Dot(color=RED, radius=0.07), label("average", 24, RED)).arrange(RIGHT, buff=0.1)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(LEFT * 6.0 + DOWN * 3.15)
        leg.arrange(RIGHT, buff=0.4).move_to(LEFT * 3.9 + DOWN * 3.45)
        self.add(leg)

        # bars: information eps and coherence sqrt(1 - eps^2)
        base = -1.55
        H = 1.9
        b_inf = always_redraw(lambda: Rectangle(width=0.7, height=max(H * e.get_value(), 0.01), fill_color=BLUE,
                                                fill_opacity=0.85, stroke_width=0).move_to([1.0, base, 0], aligned_edge=DOWN))
        b_coh = always_redraw(lambda: Rectangle(width=0.7, height=max(H * cx(), 0.01), fill_color=RED,
                                                fill_opacity=0.85, stroke_width=0).move_to([3.45, base, 0], aligned_edge=DOWN))
        li = eq(r"\varepsilon", size=32, color=BLUE).move_to([1.0, base - 0.3, 0])
        lc = eq(r"\sqrt{1 - \varepsilon^2}", size=32, color=RED).move_to([3.45, base - 0.38, 0])
        ti = label("information", 24, MUTED).move_to([1.0, base - 0.85, 0])
        tc = label("coherence kept", 24, MUTED).move_to([3.45, base - 0.92, 0])
        vlab = eq(r"\varepsilon =", size=34).move_to([5.0, 0.7, 0])
        vnum = DecimalNumber(0, num_decimal_places=2, font_size=34, color=INK).next_to(vlab, RIGHT, buff=0.12)
        vnum.add_updater(lambda m: m.set_value(e.get_value()))
        self.add(b_inf, b_coh, li, lc, ti, tc, vlab, vnum)
        self.play(e.animate.set_value(1.0), run_time=6, rate_func=linear)
        strong = VGroup(label("ε = 1: projective,", 24, MUTED), label("all coherence gone", 24, MUTED)).arrange(DOWN, buff=0.08)
        strong.move_to([5.3, -0.6, 0])
        self.play(FadeIn(strong))
        self.play(e.animate.set_value(EPS_WALK), run_time=2)
        upd = eq(r"z' = \frac{z \pm \varepsilon}{1 \pm \varepsilon z}", size=34, color=INK).move_to([5.3, -0.6, 0])
        self.play(FadeOut(strong), Write(upd))
        self.wait(1.2)

        # repeated weak measurements
        vnum.clear_updaters()
        keep = VGroup(title, upd)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep])
        self.play(upd.animate.move_to([4.7, 2.3, 0]).scale(0.9))
        num_cfg = {"color": INK}
        axes = Axes(x_range=[0, N_STEPS, 10], y_range=[-1, 1, 0.5], x_length=8.2, y_length=4.6,
                    axis_config={"color": MUTED, "include_tip": False, "decimal_number_config": num_cfg},
                    y_axis_config={"numbers_to_include": [-1, 0, 1], "decimal_number_config": dict(num_cfg, num_decimal_places=0)},
                    x_axis_config={"numbers_to_include": [20, 40, 60], "decimal_number_config": dict(num_cfg, num_decimal_places=0)}
                    ).move_to(LEFT * 1.7 + DOWN * 0.5)
        yl = eq(r"z_n", size=32).next_to(axes.y_axis, UP, buff=0.12)
        xl2 = label("measurement number n", 24, MUTED).next_to(axes, DOWN, buff=0.2)
        sub = VGroup(label(f"ε = {EPS_WALK}, start |+⟩ (z = 0)", 24, MUTED),
                     label(f"{N_TRAJ} seeded simulated runs", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        sub.move_to([4.7, 1.2, 0])
        self.play(Create(axes), Write(yl), FadeIn(xl2), FadeIn(sub))
        curves = VGroup()
        for k, path in enumerate(PATHS):
            col = BLUE if path[-1] > 0 else AMBER
            curves.add(axes.plot_line_graph(list(range(N_STEPS + 1)), path, line_color=col, add_vertex_dots=False,
                                            stroke_width=2.5))
        self.play(*[Create(c) for c in curves], run_time=7, rate_func=linear)
        res = VGroup(label(f"ended near |0⟩: {UP_COUNT} of {N_TRAJ}", 24, BLUE),
                     label(f"ended near |1⟩: {N_TRAJ - UP_COUNT} of {N_TRAJ}", 24, AMBER),
                     label("Born rule: 1/2 each", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        res.move_to([4.7, -0.5, 0])
        mart = eq(r"\mathbb{E}[z'] = z", size=34).move_to([4.7, -2.1, 0])
        self.play(FadeIn(res), Write(mart))
        self.wait(2.5)
        _ = (Transform, TracedPath, DecimalNumber)
