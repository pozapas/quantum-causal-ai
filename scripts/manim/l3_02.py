"""L3-02 Vectors and inner products: three 3Blue1Brown-style scenes.

ProjectionShadow  v = (3, 4) has length 5; normalizing slides it onto the unit circle at (0.6, 0.8);
                  its shadow on the unit vector u = (0.8, 0.6) has length 4.8, the remainder 1.4, and
                  4.8^2 + 1.4^2 = 25.
ShadowSweep       a unit vector u turns once around; the signed shadow <u, v> = 5 cos(alpha - 53.13 deg)
                  is traced live between the Cauchy-Schwarz bounds +5 and -5.
ComplexOverlap    (1, i) has squared length 0 without a conjugate and 2 with it (term by term); the
                  overlap of (1, 1)/sqrt2 with (1, e^{i phi})/sqrt2 is (1 + e^{i phi})/2, drawn as an arrow
                  whose squared length traces (1 + cos phi)/2; swapping the slots conjugates.
Numbers are computed here and checked against the lesson text by facts().
"""
import cmath
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from manim import (DOWN, LEFT, PI, RIGHT, UP, UR, Arrow, Axes, Circle, ComplexPlane, Create, DashedLine,  # noqa: E402
                   DashedVMobject, Dot, FadeIn, FadeOut, Line, NumberPlane, RightAngle, Scene, TracedPath,
                   TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label  # noqa: E402

V = np.array([3.0, 4.0])
NORM = float(np.linalg.norm(V))                    # 5
VHAT = V / NORM                                    # (0.6, 0.8)
U = np.array([0.8, 0.6])
SHADOW = float(U @ V)                              # 4.8
FOOT = SHADOW * U                                  # (3.84, 2.88)
REST = V - FOOT                                    # (-0.84, 1.12)
REST_LEN = float(np.linalg.norm(REST))             # 1.4
ARG_V = math.degrees(math.atan2(V[1], V[0]))       # 53.13
assert NORM == 5 and np.allclose(VHAT, [0.6, 0.8]) and abs(SHADOW - 4.8) < 1e-12
assert abs(REST_LEN - 1.4) < 1e-12 and abs(U @ REST) < 1e-12
assert abs(SHADOW ** 2 + REST_LEN ** 2 - 25) < 1e-9
ZEROS = [(ARG_V + 90) % 360, (ARG_V + 270) % 360]  # 143.13, 323.13
assert abs(ZEROS[0] - 143.13) < 0.01 and abs(ZEROS[1] - 323.13) < 0.01

# complex: (1, i)
W = np.array([1, 1j])
assert abs(np.sum(W * W)) < 1e-12 and abs(np.vdot(W, W) - 2) < 1e-12


def overlap(phi):
    """<u, v_phi> with u = (1, 1)/sqrt2, v_phi = (1, e^{i phi})/sqrt2 (first slot conjugated)."""
    u = np.array([1, 1]) / math.sqrt(2)
    v = np.array([1, cmath.exp(1j * phi)]) / math.sqrt(2)
    return complex(np.vdot(u, v))


assert abs(overlap(PI / 2) - (1 + 1j) / 2) < 1e-12 and abs(abs(overlap(PI / 2)) ** 2 - 0.5) < 1e-12
assert abs(overlap(PI)) < 1e-12


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["(0.6, 0.8)", "0.8 \\cdot 3 + 0.6 \\cdot 4 = 4.8", "4.8^2 + 1.4^2 = 25", "143.13",
            "5\\cos(\\alpha - 53.13^\\circ)", "\\frac{1 + e^{i\\varphi}}{2}", "\\frac{1 + \\cos\\varphi}{2}"]


def plane(xr, yr, unit):
    return NumberPlane(x_range=[xr[0], xr[1], 1], y_range=[yr[0], yr[1], 1], x_length=(xr[1] - xr[0]) * unit,
                       y_length=(yr[1] - yr[0]) * unit, background_line_style={"stroke_color": GRID, "stroke_width": 1},
                       axis_config={"color": MUTED})


def arrow(p, a, b, color, width=6):
    return Arrow(p.c2p(*a), p.c2p(*b), buff=0, color=color, stroke_width=width, max_tip_length_to_length_ratio=0.18)


class ProjectionShadow(Scene):
    def construct(self):
        title = label("Normalize, then project", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        p = plane((-1.5, 5.5), (-1, 5), 0.92).move_to(LEFT * 3.3 + DOWN * 0.4)
        self.play(Create(p), Write(title), run_time=1.4)
        o = (0, 0)
        va = arrow(p, o, V, VIOLET)
        vlab = eq("v = (3, 4)", size=34, color=VIOLET).next_to(va.get_end(), UP, buff=0.12)
        self.play(Create(va), Write(vlab))
        X = 3.7
        s1 = eq(r"\|v\| = \sqrt{3^2 + 4^2} = 5", size=36).move_to(RIGHT * X + UP * 2.4)
        self.play(Write(s1))

        circ = Circle(radius=p.x_length / (p.x_range[1] - p.x_range[0]), color=BLUE, stroke_width=3).move_to(p.c2p(0, 0))
        self.play(Create(circ))
        shrink = va.copy()
        self.play(shrink.animate.become(arrow(p, o, VHAT, BLUE, 7)), run_time=1.6)
        s2 = eq(r"\hat v = \frac{v}{\|v\|} = (0.6, 0.8)", size=36, color=BLUE).move_to(RIGHT * X + UP * 1.35)
        self.play(Write(s2))
        self.wait(0.8)
        self.play(FadeOut(shrink), FadeOut(circ))

        # unit vector u and the line through it
        line = DashedLine(p.c2p(*(-1.0 * U)), p.c2p(*(6.0 * U)), color=MUTED, dash_length=0.12)
        ua = arrow(p, o, U, AMBER, 7)
        ulab = eq("u = (0.8, 0.6)", size=32, color=AMBER).next_to(p.c2p(*U), DOWN + RIGHT * 0.2, buff=0.12)
        self.play(Create(line), Create(ua), Write(ulab))
        perp = DashedLine(p.c2p(*V), p.c2p(*FOOT), color=MUTED)
        ra = RightAngle(Line(p.c2p(*FOOT), p.c2p(0, 0)), Line(p.c2p(*FOOT), p.c2p(*V)), length=0.22, color=MUTED, quadrant=(1, 1))
        self.play(Create(perp), run_time=1.0)
        self.play(Create(ra))
        shadow = Line(p.c2p(0, 0), p.c2p(*FOOT), color=CYAN, stroke_width=10)
        self.play(Create(shadow), run_time=1.2)
        self.bring_to_front(ua)
        slab = eq("4.8", size=34, color=CYAN).next_to(p.c2p(*(0.6 * FOOT)), DOWN + RIGHT * 0.6, buff=0.15)
        self.play(Write(slab))
        s3 = eq(r"\langle u, v\rangle = 0.8 \cdot 3 + 0.6 \cdot 4 = 4.8", size=34, color=CYAN).move_to(RIGHT * X + UP * 0.25)
        self.play(Write(s3))
        rest = Line(p.c2p(*FOOT), p.c2p(*V), color=RED, stroke_width=8)
        rlab = eq("1.4", size=32, color=RED).next_to(p.c2p(*(FOOT + 0.5 * REST)), RIGHT, buff=0.15)
        self.play(Create(rest), Write(rlab))
        s4 = eq(r"\text{remainder: } \|v - 4.8\,u\| = 1.4", size=34, color=RED).move_to(RIGHT * X + DOWN * 0.85)
        self.play(Write(s4))
        s5 = eq(r"4.8^2 + 1.4^2 = 25", size=40).move_to(RIGHT * X + DOWN * 1.95)
        s6 = eq(r"\cos\theta = \frac{4.8}{5} = 0.96", size=36, color=MUTED).move_to(RIGHT * X + DOWN * 3.05)
        self.play(Write(s5))
        self.play(Write(s6))
        self.wait(2)


class ShadowSweep(Scene):
    def construct(self):
        title = label("A shadow is never longer than the arrow", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        p = plane((-5.5, 5.5), (-5.5, 5.5), 0.54).move_to(LEFT * 3.55 + DOWN * 0.45)
        self.play(Create(p), Write(title), run_time=1.4)
        va = arrow(p, (0, 0), V, VIOLET)
        vlab = eq("v", size=34, color=VIOLET).next_to(va.get_end(), UR, buff=0.05)
        self.play(Create(va), Write(vlab))

        al = ValueTracker(0.0)

        def u_of():
            a = math.radians(al.get_value())
            return np.array([math.cos(a), math.sin(a)])

        def line_of():
            u = u_of()
            return DashedLine(p.c2p(*(-5.4 * u)), p.c2p(*(5.4 * u)), color=MUTED, dash_length=0.1, stroke_width=2)

        def shadow_of():
            u = u_of()
            s = float(u @ V)
            col = CYAN if s >= 0 else RED
            return Line(p.c2p(0, 0), p.c2p(*(s * u)), color=col, stroke_width=9)

        def perp_of():
            u = u_of()
            return DashedLine(p.c2p(*V), p.c2p(*((u @ V) * u)), color=MUTED, stroke_width=2)

        lin = always_redraw(line_of)
        sh = always_redraw(shadow_of)
        pe = always_redraw(perp_of)
        ua = always_redraw(lambda: arrow(p, (0, 0), u_of(), AMBER, 7))
        ul = always_redraw(lambda: eq("u", size=32, color=AMBER).move_to(p.c2p(*(1.7 * u_of()))))
        self.play(Create(lin), Create(pe), Create(sh), Create(ua), FadeIn(ul))
        self.add(va)

        ax = Axes(x_range=[0, 360, 90], y_range=[-5, 5, 5], x_length=5.4, y_length=4.0,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 3.45 + DOWN * 0.75)
        nums = VGroup(*[label(str(d), 24, MUTED).next_to(ax.c2p(d, 0), DOWN, buff=0.12) for d in (90, 180, 270, 360)])
        ynums = VGroup(*[label(str(y), 24, MUTED).next_to(ax.c2p(0, y), LEFT, buff=0.12) for y in (5, -5)])
        bounds = VGroup(DashedLine(ax.c2p(0, 5), ax.c2p(360, 5), color=RED, stroke_width=2),
                        DashedLine(ax.c2p(0, -5), ax.c2p(360, -5), color=RED, stroke_width=2))
        cs = eq(r"|\langle u, v\rangle| \le \|u\|\,\|v\| = 5", size=32, color=RED).next_to(ax, UP, buff=0.55)
        curve_lab = eq(r"\langle u, v\rangle = 5\cos(\alpha - 53.13^\circ)", size=32).next_to(cs, UP, buff=0.22)
        xl = eq(r"\alpha", size=32).next_to(ax.x_axis, RIGHT, buff=0.12)
        self.play(Create(ax), FadeIn(nums), FadeIn(ynums), Write(xl), Write(curve_lab))
        self.play(Create(bounds), Write(cs))
        dot = always_redraw(lambda: Dot(ax.c2p(al.get_value(), float(u_of() @ V)), color=INK, radius=0.06))
        trace = TracedPath(dot.get_center, stroke_color=VIOLET, stroke_width=4)
        self.add(trace, dot)
        self.play(al.animate.set_value(360), run_time=12, rate_func=linear)

        mx = Dot(ax.c2p(ARG_V, 5), color=CYAN, radius=0.08)
        mxl = label(f"max 5 at {ARG_V:.2f}°", 24, CYAN).next_to(mx, UR, buff=0.06)
        z1 = Dot(ax.c2p(ZEROS[0], 0), color=INK, radius=0.08)
        z2 = Dot(ax.c2p(ZEROS[1], 0), color=INK, radius=0.08)
        zl = label(f"u ⟂ v at {ZEROS[0]:.2f}° and {ZEROS[1]:.2f}°", 24, INK).next_to(ax, DOWN, buff=0.6)
        self.play(FadeIn(mx), FadeIn(mxl))
        self.play(FadeIn(z1), FadeIn(z2), FadeIn(zl))
        self.play(al.animate.set_value(ZEROS[0]), run_time=2)
        self.wait(1.5)


class ComplexOverlap(Scene):
    def construct(self):
        title = label("Complex entries need a conjugate", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        wrong = eq(r"\|(1, i)\|^2", r"=", r"1\cdot 1", r"+", r"i\cdot i", r"=", r"1 - 1 = 0", size=46).move_to(UP * 1.6)
        self.play(Write(wrong))
        warn = label("a nonzero vector with length 0? wrong", 28, RED).next_to(wrong, DOWN, buff=0.3)
        self.play(FadeIn(warn))
        self.wait(0.8)
        right = eq(r"\|(1, i)\|^2", r"=", r"\bar 1\cdot 1", r"+", r"\bar i\cdot i", r"=", r"1 + 1 = 2", size=46).move_to(wrong)
        self.play(FadeOut(warn), TransformMatchingTex(wrong, right), run_time=1.8)
        good = label("conjugate the first slot:  z times its conjugate = |z|²", 28, CYAN).next_to(right, DOWN, buff=0.3)
        self.play(FadeIn(good))
        d1 = eq(r"u = \tfrac{1}{\sqrt2}(1, 1), \quad v_\varphi = \tfrac{1}{\sqrt2}(1, e^{i\varphi})", size=38).move_to(DOWN * 0.7)
        d2 = eq(r"\langle u, v_\varphi\rangle = \tfrac12\left(\bar 1\cdot 1 + \bar 1\cdot e^{i\varphi}\right) = \frac{1 + e^{i\varphi}}{2}",
                size=38, color=VIOLET).move_to(DOWN * 2.1)
        self.play(Write(d1))
        self.play(Write(d2))
        self.wait(1.2)
        self.play(FadeOut(VGroup(right, good, d1)), d2.animate.scale(0.85).next_to(title, DOWN, buff=0.3))

        cp = ComplexPlane(x_range=[-0.5, 1.5, 0.5], y_range=[-1, 1, 0.5], x_length=4.4, y_length=4.4,
                          background_line_style={"stroke_color": GRID, "stroke_width": 1},
                          axis_config={"color": MUTED}).move_to(LEFT * 3.9 + DOWN * 1.2)
        ring = DashedVMobject(Circle(radius=cp.x_length / 4, color=MUTED, stroke_width=2).move_to(cp.n2p(0.5)), num_dashes=40)
        re1 = label("1", 24, MUTED).next_to(cp.n2p(1), DOWN + RIGHT * 0.3, buff=0.1)
        self.play(Create(cp), Create(ring), FadeIn(re1))
        phi = ValueTracker(0.0)
        def ov_arrow():
            z = overlap(phi.get_value())
            if abs(z) < 0.04:                        # near phi = pi the overlap vanishes: draw a dot, not a broken arrow
                return Dot(cp.n2p(0), color=VIOLET, radius=0.07)
            return Arrow(cp.n2p(0), cp.n2p(z), buff=0, color=VIOLET, stroke_width=6, max_tip_length_to_length_ratio=0.2)

        ov = always_redraw(ov_arrow)
        self.play(Create(ov))

        ax = Axes(x_range=[0, 2 * PI, PI / 2], y_range=[0, 1, 0.5], x_length=5.4, y_length=3.0,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 3.3 + DOWN * 1.5)
        yl = eq(r"|\langle u, v_\varphi\rangle|^2 = \frac{1 + \cos\varphi}{2}", size=34, color=RED).next_to(ax, UP, buff=0.3)
        xl = eq(r"\varphi", size=32).next_to(ax.x_axis, RIGHT, buff=0.12)
        ticks = VGroup(eq(r"\pi", size=30, color=MUTED).next_to(ax.c2p(PI, 0), DOWN, buff=0.12),
                       eq(r"2\pi", size=30, color=MUTED).next_to(ax.c2p(2 * PI, 0), DOWN, buff=0.12),
                       eq("1", size=30, color=MUTED).next_to(ax.c2p(0, 1), LEFT, buff=0.12),
                       eq(r"\tfrac12", size=30, color=MUTED).next_to(ax.c2p(0, 0.5), LEFT, buff=0.12))
        self.play(Create(ax), Write(yl), Write(xl), FadeIn(ticks))
        dot = always_redraw(lambda: Dot(ax.c2p(phi.get_value(), abs(overlap(phi.get_value())) ** 2), color=RED, radius=0.06))
        trace = TracedPath(dot.get_center, stroke_color=RED, stroke_width=4)
        self.add(trace, dot)
        self.play(phi.animate.set_value(2 * PI), run_time=8, rate_func=linear)
        orth = label("orthogonal at φ = π", 24, MUTED).move_to(ax.c2p(PI, 0.9))
        self.play(FadeIn(orth))

        # swap the slots: the arrow reflects in the real axis
        trace.clear_updaters()
        self.remove(dot)
        self.play(phi.animate.set_value(PI / 2), run_time=1.5)
        z = overlap(PI / 2)
        lab1 = eq(r"\langle u, v_\varphi\rangle = \frac{1 + i}{2}", size=32, color=VIOLET).next_to(cp.n2p(z), UR, buff=0.05)
        refl = Arrow(cp.n2p(0), cp.n2p(z.conjugate()), buff=0, color=AMBER, stroke_width=6, max_tip_length_to_length_ratio=0.2)
        lab2 = eq(r"\langle v_\varphi, u\rangle = \frac{1 - i}{2}", size=32, color=AMBER).next_to(cp.n2p(z.conjugate()), RIGHT, buff=0.25)
        self.play(Write(lab1))
        self.play(Create(refl), Write(lab2))
        half = label("both have squared length 1/2", 26, INK).next_to(ax, DOWN, buff=0.45)
        self.play(FadeIn(half))
        self.wait(2)
