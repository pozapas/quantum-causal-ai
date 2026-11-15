"""L4-10 Causal machine learning, transport, and fairness: three scenes.

TransportReweight    a selection diagram (S points into Z only); stratum effects 1 and 3 stay fixed while
                     the population mix moves from the source (0.5, 0.5) to the target (0.8, 0.2), and the
                     average effect moves from 2 to 1.4.  Then S points into Y as well and the formula fails.
SpuriousShift        a predictor that leans on a feature caused by Y beats the causal predictor in the
                     training environment (MSE 0.2 against 1) and collapses as the environment changes the
                     feature's mechanism: live trace of MSE(e) = 0.64(1-e)^2 + (1-0.8e)^2 + 0.16.
FairnessWorlds       counterfactual fairness in the model X := U + A: a unit's prediction in its own world
                     (A = 1) and in the world with A set to 0, for a predictor that ignores A and one that uses it.
Every number is computed here from the constants below and checked against the lesson text by facts().
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, Cross, DashedLine, Dot, FadeIn, FadeOut,
                   Indicate, Line, Rectangle, ReplacementTransform, Scene, Square, SurroundingRectangle, TracedPath,
                   Transform, TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ---- transport -------------------------------------------------------------------------------
TAU = (1, 3)                  # stratum effects tau(z) for z = 0, 1
W_SRC = (0.5, 0.5)            # P(Z = z) in the source
W_TGT = (0.8, 0.2)            # P*(Z = z) in the target
ATE_SRC = sum(t * w for t, w in zip(TAU, W_SRC))
ATE_TGT = sum(t * w for t, w in zip(TAU, W_TGT))
assert abs(ATE_SRC - 2) < 1e-12 and abs(ATE_TGT - 1.4) < 1e-12

# ---- spurious feature under shift --------------------------------------------------------------
# X_c ~ N(0,1); Y := X_c + N_Y, N_Y ~ N(0,1); X_s := e*Y + N_s, N_s ~ N(0, 0.25); training e = 1
VAR_NS = 0.25
B_C, B_S = 0.2, 0.8           # least squares of Y on (X_c, X_s) at e = 1: (X_c + 4 X_s) / 5
assert abs(B_C - 1 / (1 + 1 / VAR_NS)) < 1e-12 and abs(B_S - (1 / VAR_NS) / (1 + 1 / VAR_NS)) < 1e-12


def mse_spurious(e):
    return (1 - B_C - B_S * e) ** 2 + (1 - B_S * e) ** 2 + B_S ** 2 * VAR_NS


MSE_CAUSAL = 1.0
assert abs(mse_spurious(1) - 0.2) < 1e-12 and abs(mse_spurious(0) - 1.8) < 1e-12 and abs(mse_spurious(-1) - 5.96) < 1e-12
# where the two predictors are equally good: 1.28 e^2 - 2.88 e + 0.8 = 0
E_CROSS = (2.88 - (2.88 ** 2 - 4 * 1.28 * 0.8) ** 0.5) / (2 * 1.28)
assert abs(mse_spurious(E_CROSS) - 1) < 1e-9 and abs(E_CROSS - 0.32) < 0.01

# ---- counterfactual fairness -------------------------------------------------------------------
A_OBS, X_OBS = 1, 3           # the unit: A = 1, X = 3 in the model X := U + A
U_UNIT = X_OBS - A_OBS        # abduction: u = 2
X_CF = U_UNIT + 0             # the world with A set to 0
H1 = (X_OBS, X_CF)            # h1 = X, ignores A: 3 and 2
H2 = (X_OBS - A_OBS, X_CF - 0)  # h2 = X - A: 2 and 2
assert U_UNIT == 2 and H1 == (3, 2) and H2 == (2, 2)


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["0.5(1) + 0.5(3) = 2", "0.8(1) + 0.2(3) = 1.4", "5.96",
            "\\mathrm{MSE}(e) = 0.64(1-e)^2 + (1-0.8e)^2 + 0.16", "X := U + A", "h_2 = X - A"]


def node(name, color=INK, r=0.38, size=34):
    c = Circle(radius=r, color=color, stroke_width=4).set_fill("#ffffff", 1)
    return VGroup(c, eq(name, size=size, color=color).move_to(c))


def snode(name, color=AMBER, side=0.7):
    s = Square(side_length=side, color=color, stroke_width=4).set_fill("#fff7ed", 1)
    return VGroup(s, eq(name, size=34, color=color).move_to(s))


def link(a, b, color=MUTED, buff=0.42):
    return Arrow(a.get_center(), b.get_center(), buff=buff, color=color, stroke_width=5,
                 max_tip_length_to_length_ratio=0.2)


class TransportReweight(Scene):
    def construct(self):
        title = label("Transport: reweight stratum effects to the target", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)

        z, x, y = node("Z"), node("X"), node("Y")
        s = snode("S")
        z.move_to(LEFT * 4.6 + UP * 1.2)
        x.move_to(LEFT * 5.8 + DOWN * 0.9)
        y.move_to(LEFT * 3.4 + DOWN * 0.9)
        s.move_to(LEFT * 2.6 + UP * 2.0)
        ezx, ezy, exy, esz = link(z, x), link(z, y), link(x, y), link(s, z, AMBER)
        self.play(*[FadeIn(n) for n in (z, x, y)], Create(ezx), Create(ezy), Create(exy), run_time=1.2)
        self.play(FadeIn(s), Create(esz))
        cap = label("S: where the populations differ", 24, AMBER).move_to(LEFT * 4.3 + DOWN * 2.0)
        self.play(FadeIn(cap))

        # bars of stratum effects
        ax = Axes(x_range=[0, 3, 1], y_range=[0, 4, 1], x_length=4.2, y_length=2.6,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24, "decimal_number_config": {"num_decimal_places": 0, "color": MUTED}},
                  y_axis_config={"numbers_to_include": [1, 2, 3, 4]}).move_to(RIGHT * 2.9 + UP * 0.95)
        yl = eq(r"\tau(z)", size=30).next_to(ax.y_axis, UP, buff=0.12)
        bars = VGroup()
        for i, (t, col) in enumerate(zip(TAU, (VIOLET, CYAN))):
            p0, p1 = ax.c2p(i + 0.6, 0), ax.c2p(i + 1.4, t)
            bars.add(Rectangle(width=p1[0] - p0[0], height=p1[1] - p0[1], color=col, fill_opacity=0.55,
                               stroke_width=2).move_to([(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0]))
        names = VGroup(eq("z = 0", size=32, color=VIOLET).next_to(bars[0], DOWN, buff=0.12),
                       eq("z = 1", size=32, color=CYAN).next_to(bars[1], DOWN, buff=0.12))
        vals = VGroup(eq("1", size=30).next_to(bars[0], UP, buff=0.08), eq("3", size=30).next_to(bars[1], UP, buff=0.08))
        self.play(Create(ax), Write(yl), *[FadeIn(b) for b in bars], Write(names), Write(vals), run_time=1.4)

        # population mix as ten dots
        def dots(w0):
            n0 = round(10 * w0)
            g = VGroup(*[Dot(radius=0.11, color=VIOLET if k < n0 else CYAN) for k in range(10)])
            return g.arrange(RIGHT, buff=0.12).move_to(RIGHT * 2.9 + DOWN * 1.2)
        d = dots(W_SRC[0])
        mix_lab = label("source mix", 24, MUTED).next_to(d, LEFT, buff=0.3)
        f_src = eq(r"\tau_{\text{source}} = 0.5(1) + 0.5(3) = 2", size=34).move_to(RIGHT * 2.9 + DOWN * 2.1)
        self.play(FadeIn(d), FadeIn(mix_lab))
        self.play(Write(f_src))
        self.wait(0.6)

        d2 = dots(W_TGT[0])
        mix_lab2 = label("target mix", 24, MUTED).move_to(mix_lab)
        f_tgt = eq(r"\tau_{\text{target}} = 0.8(1) + 0.2(3) = 1.4", size=34).move_to(f_src)
        self.play(Indicate(esz, color=AMBER), Indicate(z, color=AMBER))
        self.play(Transform(d, d2), Transform(mix_lab, mix_lab2), run_time=1.4)
        self.play(TransformMatchingTex(f_src, f_tgt), run_time=1.6)
        note = label("Same stratum effects, new weights.", 24, MUTED).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(note))
        self.wait(1.2)

        # failure: S also points into Y
        esy = link(s, y, RED)
        self.play(FadeOut(note), Create(esy))
        warn = label("If S points into Y, the stratum effects may differ too.", 24, RED).to_edge(DOWN, buff=0.25)
        cross = Cross(f_tgt, stroke_color=RED, stroke_width=5, scale_factor=0.9)
        self.play(FadeIn(warn), Create(cross))
        self.wait(2.0)
        _ = (DashedLine, Line, Rectangle, ReplacementTransform, BLUE, GRID)


class SpuriousShift(Scene):
    def construct(self):
        title = label("A shortcut feature fails when its mechanism shifts", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)

        xc, yv, xs = node("X_c", CYAN, size=30), node("Y"), node("X_s", AMBER, size=30)
        xc.move_to(RIGHT * 2.2 + UP * 1.7)
        yv.move_to(RIGHT * 4.1 + UP * 1.7)
        xs.move_to(RIGHT * 6.0 + UP * 1.7)
        env = snode("e", AMBER, 0.62).move_to(RIGHT * 6.0 + UP * 0.2)
        a1, a2, a3 = link(xc, yv), link(yv, xs), link(env, xs, AMBER, buff=0.4)
        self.play(*[FadeIn(n) for n in (xc, yv, xs, env)], Create(a1), Create(a2), Create(a3), run_time=1.4)
        mech = eq(r"X_s := e\,Y + N_s", size=30, color=AMBER).move_to(RIGHT * 3.6 + UP * 0.2)
        self.play(Write(mech))

        p1 = eq(r"\text{causal: } \hat Y = X_c", size=30, color=CYAN)
        p1.move_to([-0.3 + p1.width / 2, -0.9, 0])
        p2 = eq(r"\text{all features: } \hat Y = 0.2X_c + 0.8X_s", size=30, color=AMBER).next_to(p1, DOWN, buff=0.25)
        p2.align_to(p1, LEFT)
        self.play(Write(p1), Write(p2))

        ax = Axes(x_range=[-1, 2, 0.5], y_range=[0, 6, 1], x_length=5.4, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24, "decimal_number_config": {"num_decimal_places": 0, "color": MUTED}},
                  x_axis_config={"numbers_to_include": [-1, 0, 1, 2]},
                  y_axis_config={"numbers_to_include": [1, 2, 3, 4, 5, 6]}).move_to(LEFT * 3.5 + DOWN * 0.55)
        xl = eq("e", size=30).next_to(ax.x_axis, RIGHT, buff=0.12)
        yl = eq(r"\text{test MSE}", size=28).next_to(ax.y_axis, UP, buff=0.12)
        train = DashedLine(ax.c2p(1, 0), ax.c2p(1, 6), color=MUTED, stroke_width=2)
        tl = label("training e = 1", 24, MUTED).next_to(ax.c2p(1, 6), RIGHT, buff=0.1)
        self.play(Create(ax), Write(xl), Write(yl), Create(train), FadeIn(tl), run_time=1.2)

        e = ValueTracker(1.0)
        dc = always_redraw(lambda: Dot(ax.c2p(e.get_value(), MSE_CAUSAL), color=CYAN, radius=0.07))
        ds = always_redraw(lambda: Dot(ax.c2p(e.get_value(), min(mse_spurious(e.get_value()), 6)), color=AMBER, radius=0.07))
        self.play(FadeIn(dc), FadeIn(ds))
        r1 = eq(r"0.2 \text{ vs } 1 \text{ at } e = 1", size=32).next_to(p2, DOWN, buff=0.3).align_to(p1, LEFT)
        self.play(Write(r1))
        tc = TracedPath(dc.get_center, stroke_color=CYAN, stroke_width=4)
        ts = TracedPath(ds.get_center, stroke_color=AMBER, stroke_width=4)
        self.add(tc, ts)
        self.play(e.animate.set_value(-1.0), run_time=6, rate_func=linear)
        r2 = eq(r"5.96 \text{ vs } 1 \text{ at } e = -1", size=32).move_to(r1).align_to(p1, LEFT)
        self.play(ReplacementTransform(r1, r2))
        formula = eq(r"\mathrm{MSE}(e) = 0.64(1-e)^2 + (1-0.8e)^2 + 0.16", size=32, color=AMBER)
        formula.next_to(r2, DOWN, buff=0.3).align_to(p1, LEFT)
        self.play(Write(formula))
        cross = Dot(ax.c2p(E_CROSS, 1), color=RED, radius=0.08)
        cl = label("red dot: equal near e = 0.32", 24, RED).next_to(formula, DOWN, buff=0.25).align_to(p1, LEFT)
        self.play(FadeIn(cross), FadeIn(cl))
        note = label("The causal predictor is worse in training and stable everywhere.", 24, MUTED).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(note))
        self.wait(2.0)
        _ = (Line, Transform, VIOLET, BLUE)


class FairnessWorlds(Scene):
    def construct(self):
        title = label("Counterfactual fairness: one unit, two worlds", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)
        mdl = eq(r"X := U + A,\quad U \text{ independent of } A", size=30, color=MUTED).next_to(title, DOWN, buff=0.2)
        self.play(FadeIn(mdl))

        u = node("U", VIOLET).move_to(UP * 1.1)
        a1, x1 = node("A"), node("X")
        a2, x2 = node("A", AMBER), node("X")
        a1.move_to(LEFT * 5.0 + UP * 1.1)
        x1.move_to(LEFT * 3.0 + DOWN * 0.5)
        a2.move_to(RIGHT * 5.0 + UP * 1.1)
        x2.move_to(RIGHT * 3.0 + DOWN * 0.5)
        own = label("own world", 26, INK, "BOLD").move_to(LEFT * 4.6 + DOWN * 1.75)
        cfw = label("world with A set to 0", 26, AMBER, "BOLD").move_to(RIGHT * 4.6 + DOWN * 1.75)
        e1, e2, e3, e4 = link(a1, x1), link(u, x1, VIOLET), link(a2, x2), link(u, x2, VIOLET)
        self.play(FadeIn(u), FadeIn(a1), FadeIn(x1), Create(e1), Create(e2), FadeIn(own), run_time=1.2)

        va1 = eq("A = 1", size=30, color=BLUE).next_to(a1, UP, buff=0.12)
        vx1 = eq("X = 3", size=30, color=BLUE).next_to(x1, DOWN, buff=0.12).shift(LEFT * 0.0)
        self.play(Write(va1), Write(vx1))
        ab = eq(r"u = 3 - 1 = 2", size=30, color=VIOLET).next_to(u, UP, buff=0.12)
        self.play(Write(ab))
        self.wait(0.4)

        self.play(FadeIn(a2), FadeIn(x2), Create(e3), Create(e4), FadeIn(cfw), run_time=1.2)
        va2 = eq("A := 0", size=30, color=AMBER).next_to(a2, UP, buff=0.12)
        vx2 = eq("X = 2 + 0 = 2", size=30, color=AMBER).next_to(x2, DOWN, buff=0.12)
        self.play(Write(va2), Write(vx2))
        self.wait(0.4)

        h1 = eq(r"h_1 = X\text{:}", r"\quad 3", r"\ \text{vs}\ ", "2", size=34, color=INK).move_to(DOWN * 2.45 + LEFT * 3.0)
        h2 = eq(r"h_2 = X - A\text{:}", r"\quad 2", r"\ \text{vs}\ ", "2", size=34, color=INK).move_to(DOWN * 2.45 + RIGHT * 3.0)
        self.play(Write(h1))
        bad = label("changes: not counterfactually fair", 24, RED).next_to(h1, DOWN, buff=0.15)
        self.play(FadeIn(bad))
        self.play(Write(h2))
        good = label("same in both worlds, in this model", 24, CYAN).next_to(h2, DOWN, buff=0.15)
        self.play(FadeIn(good))
        self.play(Indicate(h2, color=CYAN))
        box = SurroundingRectangle(VGroup(h2, good), color=CYAN, buff=0.12)
        self.play(Create(box))
        caveat = label("The verdict depends on the model and on choosing to block the path from A to X.", 24, MUTED)
        caveat.to_edge(DOWN, buff=0.15)
        self.play(FadeIn(caveat))
        self.wait(2.2)
        _ = (Rectangle, Line, Cross, DashedLine)
