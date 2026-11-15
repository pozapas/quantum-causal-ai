"""L4-03 Confounders, mediators, and colliders: three scenes.

ConfounderStrata   Z in {0, 1}, X := 2Z + N_X, Y := 3Z - 0.5 X + 0.5 N_Y: the pooled slope is +0.25, the slope
                   inside each stratum of Z is -0.5; the omitted-variable formula explains the gap.
MediatorAdjust     M := 1.5 X + N_M, Y := X + 2M + N_Y: the total effect 4 splits into direct 1 and indirect 3;
                   adjusting for M drains the indirect part and leaves 1.
ColliderSelection  A, B independent N(0, 1); keep A + B > t.  As t rises the kept points become negatively
                   correlated, with corr = (v - 2)/(v + 2), v = Var(A + B | A + B > t); at t = 0 it is -1/(pi - 1).
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, DashedLine, Dot, FadeIn, FadeOut, Line,
                   Rectangle, Scene, SurroundingRectangle, TracedPath, TransformMatchingTex, ValueTracker, VGroup,
                   Write, always_redraw, linear, smooth)

from qcai_style import AMBER, BLUE, INK, MUTED, RED, VIOLET, eq, label
from qcai.lessonfigs.l4_03 import RHO0, selected_corr

GREY = "#cbd5e1"

# ---- confounder: population numbers -------------------------------------------------------------
VAR_Z = 0.25
COV_XZ, VAR_X = 2 * VAR_Z, 4 * VAR_Z + 1
BETA, GAMMA = -0.5, 3.0
POOLED = BETA + GAMMA * COV_XZ / VAR_X
assert abs(POOLED - 0.25) < 1e-12
rng = np.random.default_rng(8)
ZS = np.repeat([0, 1], 80)
XS = 2 * ZS + rng.normal(size=160)
YS = GAMMA * ZS + BETA * XS + 0.5 * rng.normal(size=160)
SAMPLE_POOLED = np.polyfit(XS, YS, 1)[0]
SAMPLE_WITHIN = [np.polyfit(XS[ZS == k], YS[ZS == k], 1)[0] for k in (0, 1)]
assert abs(SAMPLE_POOLED - POOLED) < 0.15 and all(abs(s - BETA) < 0.15 for s in SAMPLE_WITHIN)

# ---- mediator ---------------------------------------------------------------------------------------
A_XM, E_MY, D_XY = 1.5, 2.0, 1.0
TOTAL = D_XY + A_XM * E_MY
cov = np.array([[1, A_XM], [A_XM, A_XM ** 2 + 1]])               # Cov of (X, M) with Var X = 1
cxy = np.array([TOTAL, A_XM * TOTAL + E_MY])                      # Cov(X, Y), Cov(M, Y) (Var N_M = 1)
coef_x_given_m = np.linalg.solve(cov, cxy)[0]
assert TOTAL == 4.0 and abs(coef_x_given_m - D_XY) < 1e-12

# ---- collider ---------------------------------------------------------------------------------------
assert abs(RHO0 + 1 / (math.pi - 1)) < 1e-10 and abs(RHO0 + 0.467) < 5e-4
g2 = np.random.default_rng(21)
AS, BS = g2.normal(size=(2, 300))
AS, BS = np.clip(AS, -2.9, 2.9), np.clip(BS, -2.9, 2.9)
TS = np.linspace(-3.5, 1.5, 201)
RHOS = np.array([selected_corr(t) for t in TS])


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["0.25", "-0.5", "4X + 2N_M + N_Y", "-1/(\\pi - 1)", "\\frac{v - 2}{v + 2}", "-0.467"]


def make_node(name, pos, color=INK, r=0.38, size=38):
    pos = np.array([pos[0], pos[1], 0.0])
    c = Circle(radius=r, color=color, stroke_width=4).set_fill("#ffffff", 1).move_to(pos)
    return VGroup(c, eq(name, size=size, color=color).move_to(pos))


def arrow(a, b, color=MUTED):
    return Arrow(a.get_center(), b.get_center(), buff=0.44, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.18)


class ConfounderStrata(Scene):
    def construct(self):
        title = label("A confounder can reverse a slope", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        ax = Axes(x_range=[-3, 5, 1], y_range=[-3, 4.5, 1], x_length=6.6, y_length=5.0,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 2}).move_to([-2.9, -0.55, 0])
        xl = eq("X", size=34).next_to(ax.x_axis, RIGHT, buff=0.15)
        yl = eq("Y", size=34).next_to(ax.y_axis, UP, buff=0.1)
        self.play(Write(title), Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)
        Zn, Xn, Yn = make_node("Z", [3.7, 2.35], VIOLET), make_node("X", [2.4, 1.05], BLUE), make_node("Y", [5.0, 1.05], RED)
        cz = label("3", 24, MUTED).move_to([4.6, 1.85, 0])
        cx = label("-0.5", 24, MUTED).move_to([3.7, 0.75, 0])
        ca = label("2", 24, MUTED).move_to([2.8, 1.85, 0])
        self.play(FadeIn(VGroup(Zn, Xn, Yn)), Create(arrow(Zn, Xn)), Create(arrow(Zn, Yn)), Create(arrow(Xn, Yn)),
                  FadeIn(VGroup(cz, cx, ca)))
        dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.045, color=MUTED) for x, y in zip(XS, YS)])
        self.play(FadeIn(dots, lag_ratio=0.01), run_time=1.6)
        mx, my = 1.0, GAMMA * 0.5 + BETA * 1.0
        pooled = Line(ax.c2p(-3, my + POOLED * (-3 - mx)), ax.c2p(5, my + POOLED * (5 - mx)), color=INK, stroke_width=5)
        pl = eq(r"\text{pooled slope } 0.25", size=32).move_to(ax.c2p(1.2, 4.3), aligned_edge=LEFT)
        self.play(Create(pooled), Write(pl))
        self.wait(0.6)
        self.play(*[d.animate.set_color(BLUE if z == 0 else AMBER) for d, z in zip(dots, ZS)], run_time=1.0)
        keys = VGroup(label("Z = 0", 26, BLUE), label("Z = 1", 26, AMBER)).arrange(RIGHT, buff=0.5).move_to([3.7, 0.0, 0])
        self.play(FadeIn(keys))
        s0 = Line(ax.c2p(-2.6, BETA * -2.6), ax.c2p(2.6, BETA * 2.6), color=BLUE, stroke_width=6)
        s1 = Line(ax.c2p(-0.6, GAMMA + BETA * -0.6), ax.c2p(4.6, GAMMA + BETA * 4.6), color=AMBER, stroke_width=6)
        self.play(Create(s0), Create(s1), pooled.animate.set_stroke(opacity=0.35))
        wl = eq(r"\text{within each stratum: } {-0.5}", size=32, color=VIOLET).move_to([3.7, -0.75, 0])
        self.play(Write(wl))
        d1 = eq(r"\beta_{\text{pooled}}", "=", r"\beta + \gamma\,\frac{\mathrm{Cov}(X, Z)}{\mathrm{Var}(X)}", size=34).move_to([3.7, -1.9, 0])
        self.play(Write(d1))
        d2 = eq(r"\beta_{\text{pooled}}", "=", r"-0.5 + 3 \cdot \tfrac{0.5}{2}", size=34).move_to(d1)
        self.play(TransformMatchingTex(d1, d2), run_time=1.2)
        d3 = eq(r"\beta_{\text{pooled}}", "=", "0.25", size=34).move_to(d1)
        self.play(TransformMatchingTex(d2, d3), run_time=1.0)
        note = label("adjusting for Z recovers -0.5", 26, MUTED).move_to([3.7, -2.9, 0])
        self.play(FadeIn(note))
        self.wait(1.8)


class MediatorAdjust(Scene):
    def construct(self):
        title = label("Adjusting for a mediator removes part of the effect", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        Xn, Mn, Yn = make_node("X", [-5.3, 0.9], BLUE), make_node("M", [-3.5, 2.3], INK), make_node("Y", [-1.7, 0.9], RED)
        exm, emy, exy = arrow(Xn, Mn), arrow(Mn, Yn), arrow(Xn, Yn)
        labs = VGroup(label("1.5", 24, AMBER).move_to([-4.7, 1.95, 0]), label("2", 24, AMBER).move_to([-2.35, 1.95, 0]),
                      label("1", 24, VIOLET).move_to([-3.5, 0.6, 0]))
        self.play(Write(title), FadeIn(VGroup(Xn, Mn, Yn)), run_time=1.0)
        self.play(Create(exm), Create(emy), Create(exy), FadeIn(labs))
        e1 = eq("M := 1.5X + N_M", size=34).move_to([3.2, 2.2, 0])
        e2 = eq("Y := X + 2M + N_Y", size=34).next_to(e1, DOWN, buff=0.25).align_to(e1, LEFT)
        self.play(Write(e1), Write(e2))
        s1 = eq("Y", "=", "X + 2(1.5X + N_M) + N_Y", size=34).next_to(e2, DOWN, buff=0.35).align_to(e1, LEFT)
        self.play(Write(s1))
        s2 = eq("Y", "=", "4X + 2N_M + N_Y", size=34, color=AMBER).move_to(s1, aligned_edge=LEFT)
        self.play(TransformMatchingTex(s1, s2), run_time=1.2)
        t1 = label("total effect of X on Y: 4", 26, AMBER).next_to(s2, DOWN, buff=0.25).align_to(e1, LEFT)
        self.play(FadeIn(t1))

        ax = Axes(x_range=[0, 2, 1], y_range=[0, 4, 1], x_length=4.2, y_length=3.0,
                  axis_config={"color": MUTED, "include_tip": False}).move_to([-3.4, -1.45, 0])
        ticks = VGroup(*[label(str(v), 24, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.12) for v in (0, 1, 2, 3, 4)])
        self.play(Create(ax), FadeIn(ticks))
        u = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
        base = ax.c2p(0.5, 0)
        direct = Rectangle(width=0.9, height=u * D_XY, color=VIOLET, fill_opacity=0.9, stroke_width=0).move_to([base[0], base[1] + u * D_XY / 2, 0])
        indirect = Rectangle(width=0.9, height=u * A_XM * E_MY, color=AMBER, fill_opacity=0.9, stroke_width=0)
        indirect.next_to(direct, UP, buff=0)
        keyd = label("direct 1", 24, VIOLET).next_to(direct, RIGHT, buff=0.2)
        keyi = label("indirect 1.5 x 2 = 3", 24, AMBER).next_to(indirect, RIGHT, buff=0.2)
        cap1 = label("regress Y on X", 24, INK).next_to(ax, DOWN, buff=0.15)
        self.play(FadeIn(direct), FadeIn(indirect), FadeIn(keyd), FadeIn(keyi), FadeIn(cap1))
        self.wait(0.6)

        # adjust for M
        self.play(Mn[0].animate.set_fill(GREY, 1), run_time=0.6)
        cap2 = label("regress Y on X and M", 24, INK).move_to(cap1)
        self.play(indirect.animate.stretch_to_fit_height(0.001).align_to(direct, UP).shift(UP * 0.001), FadeOut(keyi),
                  FadeOut(cap1), FadeIn(cap2), emy.animate.set_opacity(0.25), exm.animate.set_opacity(0.25), run_time=1.6)
        ghost = DashedLine(ax.c2p(0.2, TOTAL), ax.c2p(0.8, TOTAL), color=AMBER, stroke_width=4)
        gl = label("total 4, no longer measured", 24, AMBER).next_to(ghost, RIGHT, buff=0.15)
        self.play(Create(ghost), FadeIn(gl))
        r = eq(r"\mathbb{E}[Y \mid X, M] = 1 \cdot X + 2M", size=34, color=VIOLET).move_to([3.2, -1.0, 0])
        self.play(Write(r))
        w1 = label("coefficient of X: 1, the direct effect", 26, VIOLET).next_to(r, DOWN, buff=0.25)
        w2 = label("valid only if nothing else links M and Y", 24, MUTED).next_to(w1, DOWN, buff=0.25)
        self.play(FadeIn(w1))
        self.play(FadeIn(w2))
        self.wait(1.8)


class ColliderSelection(Scene):
    def construct(self):
        title = label("Selecting on a sum creates a correlation", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        ax = Axes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], x_length=5.0, y_length=5.0,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 2}).move_to([-3.6, -0.55, 0])
        al = eq("A", size=32).next_to(ax.x_axis, RIGHT, buff=0.12)
        bl = eq("B", size=32).next_to(ax.y_axis, UP, buff=0.08)
        self.play(Write(title), Create(ax), FadeIn(al), FadeIn(bl), run_time=1.2)
        dots = VGroup(*[Dot(ax.c2p(a, b), radius=0.045, color=RED) for a, b in zip(AS, BS)])
        self.play(FadeIn(dots, lag_ratio=0.005), run_time=1.2)

        t = ValueTracker(-3.5)

        def boundary():
            tv = t.get_value()
            pts = [(a, tv - a) for a in np.linspace(-3, 3, 61) if -3 <= tv - a <= 3]
            if len(pts) < 2:
                return Line(ax.c2p(-3, -3), ax.c2p(-3, -3), stroke_width=0)
            return Line(ax.c2p(*pts[0]), ax.c2p(*pts[-1]), color=INK, stroke_width=4)

        line = always_redraw(boundary)

        def recolor(group):
            tv = t.get_value()
            for d, a, b in zip(group, AS, BS):
                d.set_color(RED if a + b > tv else GREY)

        dots.add_updater(recolor)
        self.add(line)
        keep = eq("\\text{keep } A + B > t", size=30).next_to(ax, DOWN, buff=0.2)
        self.play(FadeIn(keep))

        rx = Axes(x_range=[0, 5, 1], y_range=[0, 0.8, 0.2], x_length=5.0, y_length=3.0,
                  axis_config={"color": MUTED, "include_tip": False}).move_to([3.4, 0.35, 0])
        cp = lambda tt, r: rx.c2p(tt + 3.5, r + 0.8)  # noqa: E731  (axes meet at the lower left)
        xt = VGroup(*[label(f"{v:g}", 24, MUTED).next_to(cp(v, -0.8), DOWN, buff=0.1) for v in (-3, -2, -1, 0, 1)])
        yt = VGroup(*[label(f"{v:.1f}", 24, MUTED).next_to(cp(-3.5, v), LEFT, buff=0.1) for v in (-0.8, -0.4, 0.0)])
        xlab = eq("t", size=30).next_to(cp(1.5, -0.8), RIGHT, buff=0.15)
        ylab = eq(r"\operatorname{corr}(A, B \mid A + B > t)", size=32).next_to(rx, UP, buff=0.2)
        self.play(Create(rx), FadeIn(xt), FadeIn(yt), FadeIn(xlab), FadeIn(ylab))
        dot = always_redraw(lambda: Dot(cp(t.get_value(), float(np.interp(t.get_value(), TS, RHOS))), color=RED, radius=0.08))
        trace = TracedPath(dot.get_center, stroke_color=RED, stroke_width=5)
        read = always_redraw(lambda: label(f"t = {t.get_value():+.2f}    corr = {float(np.interp(t.get_value(), TS, RHOS)):.3f}",
                                           26, RED).move_to([3.4, -1.75, 0]))
        self.add(trace, dot, read)
        self.play(t.animate.set_value(1.5), run_time=7, rate_func=linear)
        self.play(t.animate.set_value(0.0), run_time=2, rate_func=smooth)
        mark = DashedLine(cp(0, -0.8), cp(0, RHO0), color=MUTED)
        val = eq(r"t = 0:\ -1/(\pi - 1) \approx -0.467", size=34).move_to([3.4, -1.85, 0])
        self.play(Create(mark), FadeOut(read), Write(val))
        form = VGroup(eq(r"\operatorname{corr} = \frac{v - 2}{v + 2}", size=32),
                      eq(r"v = \mathrm{Var}(A + B \mid A + B > t)", size=32)).arrange(DOWN, buff=0.15).move_to([3.4, -2.95, 0])
        self.play(Write(form))
        dots.clear_updaters()
        box = SurroundingRectangle(val, color=RED, buff=0.1)
        self.play(Create(box))
        self.wait(1.6)
        _ = (DOWN, FadeOut, Rectangle)
