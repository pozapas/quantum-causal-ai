"""L4-09 Counterfactual reasoning: three scenes.

ThreeSteps       the structural model X := U_X, Y := 2X + U_Y with the evidence X = 1, Y = 5.  Abduction
                 solves for the noise (u_Y = 3), action cuts the arrow into X and sets X := 0 (graph
                 surgery), prediction pushes the same noise through the edited model: Y_{X=0} = 3.
AverageVsUnit    the distribution of Y_{X=0} sharpens as evidence grows: no evidence gives the
                 interventional law N(1, 1), the evidence Y = 5 alone gives N(1.8, 0.8), and the full
                 evidence X = 1, Y = 5 collapses it to the single value 3.
TwoModels        two binary models with the same observational and interventional distributions that
                 disagree about one unit's counterfactual: probability of necessity 0 in one, 1 in the other.
Every number is computed here from the constants below and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (ManimColor, interpolate_color, DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, Cross, FadeIn, FadeOut, Indicate, Line,
                   ReplacementTransform, RoundedRectangle, Scene, SurroundingRectangle, Table, Transform,
                   TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, smooth)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ---- the lesson's numbers -------------------------------------------------------------------
BETA = 2                      # Y := BETA * X + U_Y
X_OBS, Y_OBS = 1, 5           # the factual evidence
X_ALT = 0                     # the counterfactual action do(X = 0)
U_X = X_OBS                   # abduction from X := U_X
U_Y = Y_OBS - BETA * X_OBS    # abduction from Y := 2X + U_Y
Y_CF = BETA * X_ALT + U_Y     # prediction in the edited model
assert (U_X, U_Y, Y_CF) == (1, 3, 3)

MU_UX, VAR_UX = 0.0, 1.0      # U_X ~ N(0, 1)
MU_UY, VAR_UY = 1.0, 1.0      # U_Y ~ N(1, 1)
DO0_MEAN = BETA * X_ALT + MU_UY                       # E[Y | do(X=0)] = E[U_Y] = 1
VAR_Y = BETA ** 2 * VAR_UX + VAR_UY                   # Var(Y) = 5
MEAN_Y = BETA * MU_UX + MU_UY                         # E[Y] = 1
POST_MEAN = MU_UY + VAR_UY / VAR_Y * (Y_OBS - MEAN_Y)  # E[U_Y | Y=5] = 1.8
POST_VAR = VAR_UY - VAR_UY ** 2 / VAR_Y                # Var(U_Y | Y=5) = 0.8
assert DO0_MEAN == 1 and VAR_Y == 5 and abs(POST_MEAN - 1.8) < 1e-12 and abs(POST_VAR - 0.8) < 1e-12


def model_a(x, u):
    return u                  # Y := U  (X does nothing for anyone)


def model_b(x, u):
    return x ^ u              # Y := X xor U  (X flips Y for everyone)


# both models: P(Y=1 | do(X=x)) = 1/2 for x = 0, 1 when P(U=1) = 1/2
for f in (model_a, model_b):
    for x in (0, 1):
        assert sum(f(x, u) for u in (0, 1)) / 2 == 0.5
# the unit with X=1, Y=1: which u is it, and what is Y_0?
PN_A = [1 - model_a(0, u) for u in (0, 1) if model_a(1, u) == 1][0]   # 0
PN_B = [1 - model_b(0, u) for u in (0, 1) if model_b(1, u) == 1][0]   # 1
assert (PN_A, PN_B) == (0, 1)


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["u_Y = 3", "Y_{X=0} = 2 \\cdot 0 + 3 = 3", "E[Y \\mid do(X=0)] = 1", "\\mathcal{N}(1.8,\\ 0.8)",
            "Y := X \\oplus U", "0 \\le \\mathrm{PN} \\le 1"]


def node(name, color=INK, r=0.42):
    c = Circle(radius=r, color=color, stroke_width=4).set_fill("#ffffff", 1)
    t = eq(name, size=36, color=color).move_to(c)
    return VGroup(c, t)


def link(a, b, color=MUTED):
    return Arrow(a.get_center(), b.get_center(), buff=0.46, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.18)


class ThreeSteps(Scene):
    def construct(self):
        title = label("A counterfactual in three steps", 36, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)

        ux, x = node("U_X", MUTED), node("X")
        uy, y = node("U_Y", MUTED), node("Y")
        ux.move_to(LEFT * 5.3 + UP * 1.3)
        x.move_to(LEFT * 5.3 + DOWN * 1.4)
        uy.move_to(LEFT * 2.2 + UP * 1.3)
        y.move_to(LEFT * 2.2 + DOWN * 1.4)
        a1, a2, a3 = link(ux, x), link(x, y), link(uy, y)
        self.play(*[FadeIn(n) for n in (ux, x, uy, y)], run_time=0.8)
        self.play(Create(a1), Create(a2), Create(a3), run_time=0.9)

        m1 = eq(r"X := U_X", size=36).move_to(RIGHT * 2.6 + UP * 2.2)
        m2 = eq(r"Y := 2X + U_Y", size=36).next_to(m1, DOWN, buff=0.25)
        box = SurroundingRectangle(VGroup(m1, m2), color=GRID, buff=0.2)
        self.play(Write(m1), Write(m2), Create(box))

        # evidence
        xv = eq("1", size=34, color=BLUE).next_to(x, DOWN, buff=0.15)
        yv = eq("5", size=34, color=BLUE).next_to(y, DOWN, buff=0.15)
        ev = eq(r"\text{seen: } X = 1,\ Y = 5", size=34, color=BLUE).next_to(box, DOWN, buff=0.35)
        self.play(Write(ev), FadeIn(xv), FadeIn(yv))
        self.wait(0.4)

        # step 1: abduction
        s1 = label("1  Abduction: solve for the noise", 28, VIOLET, "BOLD").move_to(RIGHT * 2.6 + DOWN * 0.15)
        self.play(FadeIn(s1))
        ab = eq("5", "=", r"2 \cdot 1", "+", "u_Y", size=36).next_to(s1, DOWN, buff=0.3)
        self.play(Write(ab))
        ab2 = eq("u_Y = 3", size=38, color=VIOLET).move_to(ab)
        self.play(TransformMatchingTex(ab, ab2), run_time=1.2)
        uyv = eq("u_Y = 3", size=32, color=VIOLET).next_to(uy, UP, buff=0.15)
        uxv = eq("u_X = 1", size=32, color=VIOLET).next_to(ux, UP, buff=0.15)
        self.play(ReplacementTransform(ab2.copy(), uyv), FadeIn(uxv), uy[0].animate.set_stroke(VIOLET),
                  ux[0].animate.set_stroke(VIOLET), run_time=1.2)
        self.wait(0.5)

        # step 2: action (graph surgery)
        s2 = label("2  Action: replace the mechanism of X", 28, AMBER, "BOLD").move_to(s1)
        self.play(FadeOut(s1), FadeIn(s2), FadeOut(ab2))
        cut = Cross(a1, stroke_color=RED, stroke_width=6, scale_factor=0.4)
        self.play(Create(cut))
        self.play(FadeOut(a1), FadeOut(cut))
        m1b = eq(r"X := 0", size=36, color=AMBER).move_to(m1)
        xv0 = eq("0", size=34, color=AMBER).move_to(xv)
        self.play(Transform(m1, m1b), Transform(xv, xv0), x[0].animate.set_stroke(AMBER), run_time=1.2)
        dolab = eq(r"do(X = 0)", size=32, color=AMBER).next_to(x, RIGHT, buff=0.25).shift(UP * 0.9)
        self.play(FadeIn(dolab))
        self.wait(0.4)

        # step 3: prediction
        s3 = label("3  Prediction: same noise, edited model", 28, CYAN, "BOLD").move_to(s2)
        self.play(FadeOut(s2), FadeIn(s3))
        pr = eq(r"Y_{X=0} = 2 \cdot 0 + 3 = 3", size=38, color=CYAN).next_to(s3, DOWN, buff=0.3)
        self.play(Write(pr))
        yv3 = eq("3", size=34, color=CYAN).move_to(yv)
        self.play(Transform(yv, yv3), y[0].animate.set_stroke(CYAN), run_time=1.0)
        self.wait(0.4)

        cmp_ = eq(r"\text{factual } 5,\ \text{counterfactual } 3,\ \text{effect } 5 - 3 = 2", size=32, color=INK)
        cmp_.next_to(pr, DOWN, buff=0.35)
        self.play(Write(cmp_))
        note = eq(r"\text{The noise } u_Y = 3 \text{ is carried from the factual world into the counterfactual one.}",
                  size=30, color=MUTED)
        note.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note))
        self.wait(2.0)


def normal_pdf(x, m, v):
    return math.exp(-(x - m) ** 2 / (2 * v)) / math.sqrt(2 * math.pi * v)


class AverageVsUnit(Scene):
    def construct(self):
        title = label("More evidence, sharper counterfactual", 36, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)
        ax = Axes(x_range=[-2, 6, 1], y_range=[0, 0.6, 0.2], x_length=6.4, y_length=3.5,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 26,
                               "decimal_number_config": {"num_decimal_places": 0, "color": MUTED}},
                  x_axis_config={"numbers_to_include": list(range(-2, 7))},
                  y_axis_config={"numbers_to_include": [0.2, 0.4, 0.6],
                                 "decimal_number_config": {"num_decimal_places": 1, "color": MUTED}}
                  ).move_to(LEFT * 3.0 + DOWN * 0.3)
        xl = eq(r"\text{value of } Y_{X=0}", size=30).next_to(ax.x_axis, DOWN, buff=0.45)
        self.play(Create(ax), Write(xl))

        mdl = eq(r"U_X \sim \mathcal{N}(0,1),\ U_Y \sim \mathcal{N}(1,1)", size=32).move_to(RIGHT * 3.7 + UP * 2.35)
        self.play(Write(mdl))

        m = ValueTracker(DO0_MEAN)
        v = ValueTracker(VAR_UY)

        def curve():
            k = min(1.0, max(0.0, (m.get_value() - DO0_MEAN) / (POST_MEAN - DO0_MEAN)))
            return ax.plot(lambda t: normal_pdf(t, m.get_value(), v.get_value()), x_range=[-2, 6, 0.04],
                           color=interpolate_color(ManimColor(VIOLET), ManimColor(BLUE), k), stroke_width=5)
        c = always_redraw(curve)
        meanline = always_redraw(lambda: Line(ax.c2p(m.get_value(), 0),
                                              ax.c2p(m.get_value(), normal_pdf(m.get_value(), m.get_value(), v.get_value())),
                                              color=VIOLET, stroke_width=3).set_opacity(0.6))
        stage1 = eq(r"\text{no evidence}", size=30, color=VIOLET).move_to(RIGHT * 3.7 + UP * 1.45)
        f1 = eq(r"E[Y \mid do(X=0)] = 1", size=32, color=VIOLET).next_to(stage1, DOWN, buff=0.2)
        self.play(Create(c), Create(meanline), Write(stage1), Write(f1), run_time=1.6)
        self.wait(0.8)

        # evidence Y = 5 only
        stage2 = eq(r"\text{seen: } Y = 5", size=30, color=BLUE).next_to(f1, DOWN, buff=0.45)
        f2a = eq(r"E[U_Y \mid Y=5] = 1 + \tfrac{1}{5}(5-1)", size=30, color=BLUE).next_to(stage2, DOWN, buff=0.2)
        f2b = eq(r"Y_{X=0} \mid Y=5 \ \sim\ \mathcal{N}(1.8,\ 0.8)", size=30, color=BLUE).next_to(f2a, DOWN, buff=0.2)
        self.play(Write(stage2), Write(f2a))
        ghost = ax.plot(lambda t: normal_pdf(t, DO0_MEAN, VAR_UY), x_range=[-2, 6, 0.04], color=VIOLET,
                        stroke_width=3).set_stroke(opacity=0.35)
        self.add(ghost)
        self.play(m.animate.set_value(POST_MEAN), v.animate.set_value(POST_VAR),                   run_time=2.2, rate_func=smooth)
        self.play(Write(f2b))
        self.wait(0.8)

        # full evidence X = 1, Y = 5
        stage3 = eq(r"\text{seen: } X = 1,\ Y = 5", size=30, color=CYAN).next_to(f2b, DOWN, buff=0.45)
        f3 = eq(r"Y_{X=0} = 2 \cdot 0 + 3 = 3", size=30, color=CYAN).next_to(stage3, DOWN, buff=0.2)
        self.play(Write(stage3))
        self.play(FadeOut(c), FadeOut(meanline), run_time=0.6)
        ghost2 = ax.plot(lambda t: normal_pdf(t, POST_MEAN, POST_VAR), x_range=[-2, 6, 0.04], color=BLUE,
                         stroke_width=3).set_stroke(opacity=0.35)
        self.add(ghost2)
        spike = Arrow(ax.c2p(Y_CF, 0), ax.c2p(Y_CF, 0.58), buff=0, color=CYAN, stroke_width=7)
        self.play(Create(spike), Write(f3), run_time=1.4)
        tag = label("one unit, one value", 24, CYAN).next_to(spike.get_end(), RIGHT, buff=0.15)
        self.play(FadeIn(tag))
        note = eq(r"\text{Population average under } do(X=0)\text{: } 1. \quad \text{This unit's counterfactual: } 3.",
                  size=30, color=MUTED)
        note.to_edge(DOWN, buff=0.25)
        self.play(FadeIn(note))
        self.wait(2.2)


class TwoModels(Scene):
    def construct(self):
        title = label("Same averages, different counterfactuals", 36, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)
        common = eq(r"U \sim \text{Bernoulli}(1/2),\ \ X \text{ randomized}", size=30, color=MUTED)
        common.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(common))

        def model_table(f, head, color, x0):
            h = eq(head, size=36, color=color).move_to(RIGHT * x0 + UP * 1.75)
            rows = [[str(f(0, u)), str(f(1, u))] for u in (0, 1)]
            t = Table(rows, row_labels=[eq("u = 0", size=34), eq("u = 1", size=34)],
                      col_labels=[eq("Y_0", size=36), eq("Y_1", size=36)],
                      include_outer_lines=False, line_config={"stroke_color": GRID, "stroke_width": 2},
                      element_to_mobject=lambda s: eq(s, size=38), h_buff=0.9, v_buff=0.45)
            t.next_to(h, DOWN, buff=0.25)
            return h, t

        ha, ta = model_table(model_a, r"\text{A: } Y := U", BLUE, -3.4)
        hb, tb = model_table(model_b, r"Y := X \oplus U", AMBER, 3.4)
        hb_full = VGroup(eq(r"\text{B: }", size=36, color=AMBER), hb.copy()).arrange(RIGHT, buff=0.12).move_to(hb)
        self.play(Write(ha), Write(hb_full))
        self.play(Create(ta), Create(tb), run_time=1.6)

        same = eq(r"P(Y=1 \mid do(X=x)) = P(Y=1 \mid X=x) = 1/2 \text{ in both}", size=30).to_edge(DOWN, buff=0.8)
        self.play(Write(same))
        self.wait(0.8)

        ask = eq(r"\text{unit seen with } X = 1,\ Y = 1:\ \text{was } Y_0 = 0?", size=30, color=VIOLET)
        ask.move_to(same)
        self.play(ReplacementTransform(same, ask))
        # model A: Y_1 = 1 only when u = 1; model B: Y_1 = 1 only when u = 0
        ra = ta.get_rows()[2]
        rb = tb.get_rows()[1]
        boxa = SurroundingRectangle(ra, color=VIOLET, buff=0.08)
        boxb = SurroundingRectangle(rb, color=VIOLET, buff=0.08)
        self.play(Create(boxa), Create(boxb))
        pa = eq(r"Y_0 = 1,\ \ \mathrm{PN} = 0", size=34, color=BLUE).next_to(ta, DOWN, buff=0.3)
        pb = eq(r"Y_0 = 0,\ \ \mathrm{PN} = 1", size=34, color=AMBER).next_to(tb, DOWN, buff=0.3)
        self.play(Write(pa), Write(pb))
        self.play(Indicate(pa, color=BLUE), Indicate(pb, color=AMBER))
        bound = eq(r"\text{the data allow anything in } 0 \le \mathrm{PN} \le 1", size=32, color=VIOLET)
        bound.move_to(ask)
        self.play(ReplacementTransform(ask, bound))
        frame_ = RoundedRectangle(width=bound.width + 0.5, height=bound.height + 0.35, corner_radius=0.15,
                                  color=VIOLET).move_to(bound)
        self.play(Create(frame_))
        self.wait(2.2)
        _ = (Axes, CYAN, RED, INK)
