"""L4-01 Structural causal models: three scenes.

SCMMachine        U ~ Bernoulli(1/2), X := U, Y := 2X + U run as a machine; seeing gives a contrast of 3,
                  then graph surgery (X := x) gives E[Y | do(X=x)] = 2x + 1/2 and a contrast of 2.
GraphSurgery      the engine's binary SCM Z -> X -> Y <- Z: cut the arrow into X, replace its equation, and
                  watch the interventional bars (0.35, 0.55) part from the observational ones (0.20, 0.70).
ConfoundingSweep  the confounding strength c sweeps from 0 to 0.6: the observed contrast 0.2 + 0.6c climbs
                  while the causal effect stays at 0.2.
Numbers are computed here (with the course engine) and checked against the lesson text by facts().
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, Cross, DashedLine, Dot, FadeIn, FadeOut,
                   GrowFromEdge, Indicate, Line, Rectangle, Scene, ShowPassingFlash, SurroundingRectangle,
                   TracedPath, TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, INK, MUTED, RED, VIOLET, eq, label
from qcai import science

# ---- the toy model with a shared background input ------------------------------------------------
OBS1, OBS0 = 2 * 1 + 1, 2 * 0 + 0                  # X = U, so X = 1 means U = 1
DO1 = (2 * 1 + 0 + 2 * 1 + 1) / 2                  # U = 0 or 1 with probability 1/2
DO0 = (2 * 0 + 0 + 2 * 0 + 1) / 2
assert (OBS1, OBS0, DO1, DO0) == (3, 0, 2.5, 0.5)

# ---- the engine's binary SCM -----------------------------------------------------------------------
PREV, LOW, HIGH, BASE, EFFECT, CONF = 0.5, 0.2, 0.8, 0.1, 0.2, 0.5
R = science.causal(PREV, LOW, HIGH, BASE, EFFECT, CONF)
SEE0, SEE1, DOX0, DOX1 = R["untreated"], R["treated"], R["do0"], R["do1"]
assert all(abs(a - b) < 1e-12 for a, b in ((SEE0, 0.20), (SEE1, 0.70), (DOX0, 0.35), (DOX1, 0.55)))
P_Y_X1_Z1, P_Y_X1_Z0 = BASE + EFFECT + CONF, BASE + EFFECT          # 0.8 and 0.3
assert abs(PREV * P_Y_X1_Z1 + (1 - PREV) * P_Y_X1_Z0 - DOX1) < 1e-12  # adjustment formula
PZ_X1 = PREV * HIGH / (PREV * HIGH + (1 - PREV) * LOW)               # 0.8
PZ_X0 = PREV * (1 - HIGH) / (PREV * (1 - HIGH) + (1 - PREV) * (1 - LOW))  # 0.2
assert abs(PZ_X1 - 0.8) < 1e-12 and abs(PZ_X0 - 0.2) < 1e-12
for c in np.linspace(0, 0.6, 13):                                    # observed contrast = 0.2 + 0.6 c
    assert abs(science.causal(PREV, LOW, HIGH, BASE, EFFECT, c)["observed"] - (EFFECT + (PZ_X1 - PZ_X0) * c)) < 1e-12


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["Y := 2X + U", "X := U", "2x + \\tfrac{1}{2}", "0.70", "0.55", "0.35", "0.2 + 0.6c", "0.5 \\cdot 0.8 + 0.5 \\cdot 0.3"]


def node(name, pos, color=INK, r=0.42, size=40):
    pos = np.array([pos[0], pos[1], 0.0])
    c = Circle(radius=r, color=color, stroke_width=4).set_fill("#ffffff", 1).move_to(pos)
    t = eq(name, size=size, color=color).move_to(pos)
    return VGroup(c, t)


def edge(a, b, color=MUTED):
    return Arrow(a.get_center(), b.get_center(), buff=0.48, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.18)


class SCMMachine(Scene):
    def construct(self):
        title = label("A structural causal model is a machine", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        U = node("U", [-3.6, 1.9], VIOLET)
        X = node("X", [-5.3, -0.4], BLUE)
        Y = node("Y", [-1.9, -0.4], RED)
        eUX, eUY, eXY = edge(U, X), edge(U, Y), edge(X, Y)
        self.play(Write(title), FadeIn(U), FadeIn(X), FadeIn(Y), run_time=1.2)
        self.play(Create(eUX), Create(eUY), Create(eXY))
        eqs = VGroup(eq(r"U \sim \mathrm{Bernoulli}(1/2)", size=36),
                     eq("X := U", size=36, color=BLUE), eq("Y := 2X + U", size=36, color=RED)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-3.6, -2.35, 0])
        self.play(Write(eqs), run_time=1.6)

        head = label("Seeing: run the machine, record (X, Y)", 28, MUTED).move_to([3.3, 2.5, 0])
        self.play(FadeIn(head))
        rows = VGroup()
        for i, u in enumerate((0, 1)):
            x, y = u, 2 * u + u
            tags = VGroup(eq(f"U={u}", size=30, color=VIOLET).next_to(U, RIGHT, buff=0.15),
                          eq(f"X={x}", size=30, color=BLUE).next_to(X, DOWN, buff=0.15),
                          eq(f"Y={y}", size=30, color=RED).next_to(Y, DOWN, buff=0.15))
            self.play(FadeIn(tags[0]), run_time=0.4)
            self.play(ShowPassingFlash(eUX.copy().set_color(AMBER), time_width=0.6),
                      ShowPassingFlash(eUY.copy().set_color(AMBER), time_width=0.6), FadeIn(tags[1]), run_time=0.7)
            self.play(ShowPassingFlash(eXY.copy().set_color(AMBER), time_width=0.6), FadeIn(tags[2]), run_time=0.7)
            row = eq(f"U = {u}:\\quad X = {x},\\ Y = {y}", size=34).move_to([3.3, 1.7 - 0.65 * i, 0])
            self.play(Write(row), FadeOut(tags), run_time=0.7)
            rows.add(row)
        see = eq(r"\mathbb{E}[Y \mid X{=}1] - \mathbb{E}[Y \mid X{=}0] = 3 - 0 = 3", size=32, color=BLUE).move_to([3.3, 0.25, 0])
        self.play(Write(see))
        self.wait(0.8)

        # graph surgery: cut U -> X, replace X := U by X := x
        cut = Cross(eUX, stroke_color=RED, stroke_width=6, scale_factor=0.35)
        self.play(Create(cut))
        self.play(FadeOut(eUX), FadeOut(cut))
        new = eq("X := x", size=36, color=AMBER).move_to(eqs[1], aligned_edge=LEFT)
        self.play(TransformMatchingTex(eqs[1], new), X[0].animate.set_stroke(AMBER), X[1].animate.set_color(AMBER), run_time=1.2)
        head2 = label("Doing: set X = x, keep everything else", 28, MUTED).move_to([3.3, -0.6, 0])
        self.play(FadeIn(head2))
        d1 = eq(r"do(X{=}1):\ Y \in \{2, 3\},\ \text{mean } 2.5", size=32).move_to([3.3, -1.3, 0])
        d0 = eq(r"do(X{=}0):\ Y \in \{0, 1\},\ \text{mean } 0.5", size=32).move_to([3.3, -1.9, 0])
        self.play(Write(d1))
        self.play(Write(d0))
        res = eq(r"\mathbb{E}[Y \mid do(X{=}x)] = 2x + \tfrac{1}{2}", size=38, color=AMBER).move_to([3.3, -2.75, 0])
        self.play(Write(res))
        box = SurroundingRectangle(res, color=AMBER, buff=0.12)
        note = label("causal contrast 2, not the observed 3", 26, MUTED).next_to(box, DOWN, buff=0.12)
        self.play(Create(box), FadeIn(note))
        self.wait(1.6)


def bars_axes():
    return Axes(x_range=[0, 2, 1], y_range=[0, 1, 0.25], x_length=5.0, y_length=3.6,
                axis_config={"color": MUTED, "include_tip": False, "stroke_width": 2},
                y_axis_config={"include_numbers": False}).move_to([3.3, -0.5, 0])


class GraphSurgery(Scene):
    def construct(self):
        title = label("The do-operator is graph surgery", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        Zn = node("Z", [-4.1, 2.0], VIOLET)
        Xn = node("X", [-5.6, 0.2], BLUE)
        Yn = node("Y", [-2.6, 0.2], RED)
        eZX, eZY, eXY = edge(Zn, Xn), edge(Zn, Yn), edge(Xn, Yn)
        self.play(Write(title), FadeIn(VGroup(Zn, Xn, Yn)), run_time=1.0)
        self.play(Create(eZX), Create(eZY), Create(eXY))
        eqs = VGroup(eq(r"Z := U_Z", size=34, color=VIOLET), eq(r"X := f_X(Z, U_X)", size=34, color=BLUE),
                     eq(r"Y := f_Y(X, Z, U_Y)", size=34, color=RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        eqs.move_to([-4.1, -1.55, 0])
        self.play(Write(eqs), run_time=1.4)

        ax = bars_axes()
        ticks = VGroup(*[label(f"{v:.2f}", 24, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.12) for v in (0, 0.5, 1)])
        xl = VGroup(eq("x = 0", size=30).next_to(ax.c2p(0.5, 0), DOWN, buff=0.2),
                    eq("x = 1", size=30).next_to(ax.c2p(1.5, 0), DOWN, buff=0.2))
        self.play(Create(ax), FadeIn(ticks), FadeIn(xl))
        key1 = VGroup(Rectangle(width=0.3, height=0.3, color=BLUE, fill_opacity=1), label("seeing  P(Y=1 | X=x)", 24, INK)).arrange(RIGHT, buff=0.15)
        key2 = VGroup(Rectangle(width=0.3, height=0.3, color=AMBER, fill_opacity=1), label("doing  P(Y=1 | do(X=x))", 24, INK)).arrange(RIGHT, buff=0.15)
        keys = VGroup(key1, key2).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([3.3, 2.15, 0])

        def bar(xc, v, color):
            w = 0.55
            b0 = ax.c2p(xc, 0)
            h = ax.c2p(xc, v)[1] - b0[1]
            r = Rectangle(width=w, height=h, color=color, fill_opacity=0.9, stroke_width=0).move_to([b0[0], b0[1] + h / 2, 0])
            t = label(f"{v:.2f}", 24, color).next_to(r, UP, buff=0.08)
            return r, t

        s0, s0t = bar(0.5 - 0.3, SEE0, BLUE)
        s1, s1t = bar(1.5 - 0.3, SEE1, BLUE)
        self.play(FadeIn(key1))
        self.play(GrowFromEdge(s0, DOWN), GrowFromEdge(s1, DOWN), FadeIn(s0t), FadeIn(s1t), run_time=1.2)
        self.wait(0.5)

        cut = Cross(eZX, stroke_color=RED, stroke_width=6, scale_factor=0.35)
        self.play(Indicate(eZX, color=RED))
        self.play(Create(cut))
        self.play(FadeOut(eZX), FadeOut(cut))
        new = eq(r"X := x", size=34, color=AMBER).move_to(eqs[1], aligned_edge=LEFT)
        self.play(TransformMatchingTex(eqs[1], new), Xn[0].animate.set_stroke(AMBER), Xn[1].animate.set_color(AMBER), run_time=1.2)
        d0, d0t = bar(0.5 + 0.3, DOX0, AMBER)
        d1, d1t = bar(1.5 + 0.3, DOX1, AMBER)
        self.play(FadeIn(key2))
        self.play(GrowFromEdge(d0, DOWN), GrowFromEdge(d1, DOWN), FadeIn(d0t), FadeIn(d1t), run_time=1.4)
        self.wait(0.4)

        c1 = eq(r"\text{seeing: } 0.70 - 0.20 = 0.50", size=30, color=BLUE)
        c2 = eq(r"\text{doing: } 0.55 - 0.35 = 0.20", size=30, color=AMBER)
        cc = VGroup(c1, c2).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-4.0, -3.35, 0])
        self.play(FadeOut(eqs[0]), FadeOut(eqs[2]), FadeOut(new), run_time=0.5)
        why = VGroup(eq(r"P(Y{=}1 \mid do(X{=}1)) = \textstyle\sum_z P(Y{=}1 \mid X{=}1, z)\,P(z)", size=30),
                     eq(r"= 0.5 \cdot 0.8 + 0.5 \cdot 0.3 = 0.55", size=30, color=AMBER)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([-3.25, -1.3, 0])
        self.play(Write(cc))
        self.play(Write(why[0]))
        self.play(Write(why[1]))
        self.wait(1.8)


class ConfoundingSweep(Scene):
    def construct(self):
        title = label("Turn up the confounding: seeing drifts, doing stays", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        l1 = eq(r"P(Y{=}1 \mid X{=}1) - P(Y{=}1 \mid X{=}0)", size=36).move_to([-3.0, 2.3, 0])
        l2 = eq("=", "0.2 + ", "c", r"\,[P(Z{=}1 \mid X{=}1) - P(Z{=}1 \mid X{=}0)]", size=36)
        l2.next_to(l1, DOWN, buff=0.25).align_to(l1, LEFT)
        self.play(Write(l1))
        self.play(Write(l2))
        l3 = eq("=", "0.2 + ", "c", r"\,(0.8 - 0.2)", size=36).move_to(l2, aligned_edge=LEFT)
        self.play(TransformMatchingTex(l2, l3), run_time=1.2)
        l4 = eq("=", "0.2 + ", "0.6", "c", size=36, color=BLUE).move_to(l3, aligned_edge=LEFT)
        self.play(TransformMatchingTex(l3, l4), run_time=1.2)
        side = VGroup(eq(r"P(Y{=}1 \mid do(X{=}1)) - P(Y{=}1 \mid do(X{=}0))", size=30),
                      eq(r"= 0.2 \ \text{for every } c", size=30, color=AMBER)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        side.move_to([3.4, 2.05, 0])
        self.play(Write(side))

        ax = Axes(x_range=[0, 0.6, 0.1], y_range=[0, 0.6, 0.1], x_length=7.4, y_length=3.0,
                  axis_config={"color": MUTED, "include_tip": False}).move_to([0.2, -1.4, 0])
        xt = VGroup(*[label(f"{v:.1f}", 24, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.12) for v in (0, 0.2, 0.4, 0.6)])
        yt = VGroup(*[label(f"{v:.1f}", 24, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.12) for v in (0.2, 0.4, 0.6)])
        xlab = label("confounding strength c", 24, MUTED).next_to(ax.x_axis, DOWN, buff=0.45)
        ylab = label("risk difference", 24, MUTED).rotate(np.pi / 2).next_to(ax.y_axis, LEFT, buff=0.55)
        self.play(Create(ax), FadeIn(xt), FadeIn(yt), FadeIn(xlab), FadeIn(ylab))
        flat = DashedLine(ax.c2p(0, EFFECT), ax.c2p(0.6, EFFECT), color=AMBER, stroke_width=5)
        self.play(Create(flat))
        cv = ValueTracker(0.0)
        dot = always_redraw(lambda: Dot(ax.c2p(cv.get_value(), science.causal(PREV, LOW, HIGH, BASE, EFFECT, cv.get_value())["observed"]),
                                        color=BLUE, radius=0.08))
        trace = TracedPath(dot.get_center, stroke_color=BLUE, stroke_width=5)
        readout = always_redraw(lambda: label(f"c = {cv.get_value():.2f}   observed contrast = {EFFECT + 0.6 * cv.get_value():.2f}",
                                              24, BLUE).move_to([0.2, 0.75, 0]))
        self.add(trace, dot, readout)
        self.play(cv.animate.set_value(CONF), run_time=4, rate_func=linear)
        mark = DashedLine(ax.c2p(CONF, 0), ax.c2p(CONF, R["observed"]), color=MUTED)
        gap = Line(ax.c2p(CONF, EFFECT), ax.c2p(CONF, R["observed"]), color=RED, stroke_width=7)
        gl = label("bias 0.30", 24, RED).next_to(gap, RIGHT, buff=0.15)
        self.play(Create(mark), Create(gap), FadeIn(gl))
        self.play(cv.animate.set_value(0.6), run_time=1.5, rate_func=linear)
        self.wait(1.5)
        _ = (CYAN, VIOLET)
