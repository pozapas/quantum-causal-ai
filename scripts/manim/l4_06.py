"""L4-06 Potential outcomes and randomization: three 3Blue1Brown-style scenes.

PotentialOutcomesTable  Eight units with both potential outcomes (the science table, ATE = 6 - 2 = 4).
                        Self-selection reveals one column per unit; the naive contrast 6.25 splits
                        into the effect on the treated 4.25 plus selection bias 2.00.
RandomizationBalance    Complete randomization (4 of 8 treated).  Each draw drops one dot into two dot
                        plots: the difference in means and the baseline imbalance.  All 70
                        assignments: estimates average exactly 4, imbalance averages exactly 0.
AssumptionCards         SUTVA, consistency, exchangeability and positivity as cards; the identification
                        chain E[Y | X = 1] = E[Y(1) | X = 1] = E[Y(1)] lights up the card used at each step.
Numbers are computed here from the table the lesson states and are checked by facts().
"""
import itertools
import pathlib
import random
import sys
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, Dot, FadeIn, FadeOut, Indicate, Line, NumberLine,
                   RoundedRectangle, Scene, SurroundingRectangle, Transform, TransformMatchingTex, VGroup, Write)

from qcai_style import AMBER, BLUE, CYAN, INK, MUTED, RED, VIOLET, eq, label

# ---- the science table (the same numbers as the lesson text) -------------------------------------
UNITS = "ABCDEFGH"
Y0 = [0, 1, 1, 2, 2, 3, 3, 4]
Y1 = [3, 5, 7, 4, 8, 6, 7, 8]
TAU = [b - a for a, b in zip(Y0, Y1)]
N = 8
SELF = [0, 0, 0, 0, 1, 1, 1, 1]               # self-selection: units with high Y(0) take the treatment
mean = lambda v: sum(v) / len(v)  # noqa: E731
ATE = mean(Y1) - mean(Y0)
NAIVE = mean([Y1[i] for i in range(N) if SELF[i]]) - mean([Y0[i] for i in range(N) if not SELF[i]])
ATT = mean([TAU[i] for i in range(N) if SELF[i]])
SELBIAS = mean([Y0[i] for i in range(N) if SELF[i]]) - mean([Y0[i] for i in range(N) if not SELF[i]])
assert mean(Y0) == 2 and mean(Y1) == 6 and ATE == 4
assert NAIVE == 6.25 and ATT == 4.25 and SELBIAS == 2.0 and abs(NAIVE - ATT - SELBIAS) < 1e-12

ASSIGN = list(itertools.combinations(range(N), 4))       # complete randomization: 70 assignments


def estimate(T):
    return mean([Y1[i] for i in T]) - mean([Y0[i] for i in range(N) if i not in T])


def imbalance(T):
    return mean([Y0[i] for i in T]) - mean([Y0[i] for i in range(N) if i not in T])


EST = [estimate(T) for T in ASSIGN]
IMB = [imbalance(T) for T in ASSIGN]
assert len(ASSIGN) == 70 and abs(mean(EST) - 4) < 1e-12 and abs(mean(IMB)) < 1e-12
VAR = Fraction(sum(Fraction(e).limit_denominator(100) ** 2 for e in EST), 70) - 16
assert VAR == Fraction(29, 28)

ID_STEP = r"E[Y \mid X = 1] = E[Y(1) \mid X = 1]"


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["6.25", "4.25", "29/28", "70", ID_STEP, "Y(x) \\perp\\!\\!\\!\\perp X"]


class PotentialOutcomesTable(Scene):
    def construct(self):
        title = label("Two potential outcomes per unit, one observed", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        xs = {"u": -6.25, "y0": -5.05, "y1": -3.85, "t": -2.6, "x": -1.35}
        top, h = 2.45, 0.53
        heads = VGroup(label("unit", 24, MUTED).move_to([xs["u"], top, 0]), eq("Y(0)", size=32, color=BLUE).move_to([xs["y0"], top, 0]),
                       eq("Y(1)", size=32, color=VIOLET).move_to([xs["y1"], top, 0]),
                       label("effect", 24, INK).move_to([xs["t"], top, 0]))
        rule = Line([-6.7, top - 0.3, 0], [-1.9, top - 0.3, 0], color=MUTED, stroke_width=2)
        rows = []
        for i in range(N):
            y = top - 0.65 - h * i
            rows.append({"u": label(UNITS[i], 26, INK).move_to([xs["u"], y, 0]),
                         "y0": eq(str(Y0[i]), size=34, color=BLUE).move_to([xs["y0"], y, 0]),
                         "y1": eq(str(Y1[i]), size=34, color=VIOLET).move_to([xs["y1"], y, 0]),
                         "t": eq(str(TAU[i]), size=34).move_to([xs["t"], y, 0]), "y": y})
        ymean = top - 0.65 - h * N - 0.1
        rule2 = Line([-6.7, ymean + 0.32, 0], [-1.9, ymean + 0.32, 0], color=MUTED, stroke_width=2)
        means = VGroup(label("mean", 24, MUTED).move_to([xs["u"], ymean, 0]), eq("2", size=34, color=BLUE).move_to([xs["y0"], ymean, 0]),
                       eq("6", size=34, color=VIOLET).move_to([xs["y1"], ymean, 0]), eq("4", size=34).move_to([xs["t"], ymean, 0]))
        self.play(FadeIn(heads), Create(rule))
        self.play(*[FadeIn(VGroup(r["u"], r["y0"], r["y1"])) for r in rows], run_time=1.2)
        self.play(*[FadeIn(r["t"]) for r in rows])
        self.play(Create(rule2), FadeIn(means))
        oracle = label("an oracle's view: both columns", 26, MUTED).move_to([2.9, 2.45, 0])
        ate = eq(r"\text{ATE} = E[Y(1)] - E[Y(0)] = 6 - 2 = 4", size=38).move_to([2.9, 1.7, 0])
        self.play(FadeIn(oracle), Write(ate))
        self.wait(1.2)

        # reality: self-selection reveals one column per unit
        real = label("reality: units with high Y(0) choose treatment", 26, RED).move_to(oracle)
        xh = eq("X", size=32).move_to([xs["x"], top, 0])
        xcol = VGroup(*[eq(str(SELF[i]), size=34, color=RED).move_to([xs["x"], rows[i]["y"], 0]) for i in range(N)])
        self.play(Transform(oracle, real), FadeIn(xh), FadeIn(xcol))
        hide = []
        for i, r in enumerate(rows):
            k = "y0" if SELF[i] else "y1"
            q = eq("?", size=34, color=MUTED).move_to(r[k])
            hide.append(Transform(r[k], q))
            hide.append(Transform(r["t"], eq("?", size=34, color=MUTED).move_to(r["t"])))
        self.play(*hide, FadeOut(means[3]), run_time=1.6)
        fp = label("no unit shows its own effect", 24, MUTED).move_to([2.9, 1.05, 0])
        self.play(FadeIn(fp))
        self.wait(0.8)
        naive = eq(r"7.25 - 1.00 = 6.25", size=40, color=RED).move_to([2.9, 0.2, 0])
        nlab = label("treated mean of Y(1) minus control mean of Y(0)", 22, MUTED).next_to(naive, DOWN, buff=0.12)
        self.play(Write(naive), FadeIn(nlab))
        self.wait(0.8)
        dec = eq(r"6.25", "=", r"\underbrace{4.25}_{\text{effect on treated}}", "+", r"\underbrace{2.00}_{\text{selection bias}}", size=40)
        dec.move_to([2.9, -1.35, 0])
        self.play(Write(dec), run_time=1.8)
        sb = eq(r"E[Y(0) \mid X=1] - E[Y(0) \mid X=0] = 3 - 1 = 2.00", size=30, color=AMBER).move_to([2.9, -2.75, 0])
        self.play(Write(sb))
        self.wait(2.2)
        _ = (CYAN, ate)


class RandomizationBalance(Scene):
    def construct(self):
        title = label("Randomization balances on average, not every time", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        circ = VGroup()
        for i in range(N):
            c = Circle(radius=0.3, color=MUTED, stroke_width=3).set_fill("#ffffff", 1).move_to([-4.9 + 1.4 * i, 2.25, 0])
            circ.add(VGroup(c, label(UNITS[i], 24, INK).move_to(c), label(f"Y(0)={Y0[i]}", 20, MUTED).next_to(c, DOWN, buff=0.08)))
        rule = label("complete randomization: 4 of the 8 units are drawn for treatment", 24, MUTED).move_to([0, 1.35, 0])
        self.play(FadeIn(circ), FadeIn(rule))

        lo_e, hi_e = min(EST), max(EST)
        lo_i, hi_i = min(IMB), max(IMB)
        NL_e = NumberLine(x_range=[1, 7, 1], length=5.4, color=MUTED, include_numbers=True, font_size=24,
                          numbers_to_exclude=[]).move_to([-3.4, -2.75, 0])
        NL_i = NumberLine(x_range=[-2, 2, 1], length=5.0, color=MUTED, include_numbers=True, font_size=24).move_to([3.4, -2.75, 0])
        for nl in (NL_e, NL_i):
            for n_ in nl.numbers:
                n_.set_color(INK)
        assert 1 <= lo_e and hi_e <= 7 and -2 <= lo_i and hi_i <= 2
        he = label("difference in means", 24, VIOLET).move_to([-3.4, 0.75, 0])
        hi = label("baseline imbalance in Y(0)", 24, AMBER).move_to([3.4, 0.75, 0])
        ate_line = Line(NL_e.n2p(4), NL_e.n2p(4) + UP * 2.7, color=RED, stroke_width=3)
        zero_line = Line(NL_i.n2p(0), NL_i.n2p(0) + UP * 2.7, color=RED, stroke_width=3)
        self.play(Create(NL_e), Create(NL_i), FadeIn(he), FadeIn(hi), Create(ate_line), Create(zero_line))
        stack_e, stack_i = {}, {}

        def dot_for(v, nl, stack, color):
            k = round(v * 4)
            j = stack.get(k, 0)
            stack[k] = j + 1
            return Dot(nl.n2p(v) + UP * (0.12 + 0.17 * j), radius=0.075, color=color)

        order = list(range(len(ASSIGN)))
        random.Random(3).shuffle(order)
        readout = None
        for step, a in enumerate(order[:10]):
            T = ASSIGN[a]
            for i in range(N):
                col = VIOLET if i in T else BLUE
                circ[i][0].set_fill(col, 0.35).set_stroke(col)
            e, b = EST[a], IMB[a]
            new = eq(rf"\hat\tau = {e:.2f}", r"\quad", rf"\text{{imbalance}} = {b:+.2f}", size=32).move_to([0, 0.1, 0])
            de, di = dot_for(e, NL_e, stack_e, VIOLET), dot_for(b, NL_i, stack_i, AMBER)
            anims = [FadeIn(de, scale=2), FadeIn(di, scale=2)]
            if readout is None:
                readout = new
                anims.append(FadeIn(readout))
            else:
                anims.append(Transform(readout, new))
            self.play(*anims, run_time=0.55 if step > 2 else 1.0)
        self.play(FadeOut(readout))
        rest = VGroup()
        for a in order[10:]:
            rest.add(dot_for(EST[a], NL_e, stack_e, VIOLET), dot_for(IMB[a], NL_i, stack_i, AMBER))
        allnote = label("all 70 possible assignments", 26, INK, "BOLD").move_to([0, 0.1, 0])
        self.play(FadeIn(allnote), FadeIn(rest, lag_ratio=0.02), run_time=2.5)
        self.wait(0.6)
        r1 = eq(r"\text{mean} = 4 = \text{ATE},\ \ \text{variance} = 29/28", size=30, color=RED).move_to([-3.4, -3.45, 0])
        r2 = eq(r"\text{mean imbalance} = 0", size=30, color=RED).move_to([3.4, -3.45, 0])
        self.play(Write(r1), Write(r2))
        self.wait(2.2)
        _ = (CYAN, RoundedRectangle, SurroundingRectangle)


class AssumptionCards(Scene):
    def construct(self):
        title = label("Four assumptions turn a contrast into an effect", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))

        def card(name, formula, pos, color):
            f = eq(formula, size=32, color=INK)
            t = label(name, 26, color, "BOLD")
            body = VGroup(t, f).arrange(DOWN, buff=0.18)
            box = RoundedRectangle(corner_radius=0.15, width=max(5.9, body.width + 0.4), height=1.35, stroke_color=color, stroke_width=3)
            box.set_fill("#ffffff", 1)
            return VGroup(box, body).move_to(pos)

        cards = {
            "sutva": card("SUTVA: no interference", r"Y_i(x_1, \dots, x_n) = Y_i(x_i)", [-3.25, 1.75, 0], BLUE),
            "cons": card("consistency", r"X_i = x \ \Rightarrow\ Y_i = Y_i(x)", [3.25, 1.75, 0], VIOLET),
            "exch": card("exchangeability", r"Y(x) \perp\!\!\!\perp X", [-3.25, 0.2, 0], CYAN),
            "pos": card("positivity", r"0 < P(X = 1) < 1", [3.25, 0.2, 0], AMBER),
        }
        for k in ("sutva", "cons", "exch", "pos"):
            self.play(FadeIn(cards[k], shift=UP * 0.2), run_time=0.8)
        self.wait(0.6)
        S = 40
        l0 = eq(r"E[Y \mid X = 1]", size=S)
        l1 = eq(r"E[Y \mid X = 1]", "=", r"E[Y(1) \mid X = 1]", size=S)
        l2 = eq(r"E[Y \mid X = 1]", "=", r"E[Y(1) \mid X = 1]", "=", r"E[Y(1)]", size=S)
        for m in (l0, l1, l2):
            m.move_to(DOWN * 1.55)
        note = label("SUTVA makes Y(1) and Y(0) well defined for each unit", 24, BLUE).move_to(DOWN * 2.45)
        self.play(Indicate(cards["sutva"], color=BLUE, scale_factor=1.04), FadeIn(note))
        self.play(Write(l0))
        self.wait(0.4)
        n1 = label("consistency: among the treated, Y is Y(1)", 24, VIOLET).move_to(note)
        self.play(TransformMatchingTex(l0, l1), Transform(note, n1), Indicate(cards["cons"], color=VIOLET, scale_factor=1.04),
                  run_time=1.6)
        self.wait(0.8)
        n2 = label("exchangeability: the treated are a fair sample for Y(1)", 24, CYAN).move_to(note)
        self.play(TransformMatchingTex(l1, l2), Transform(note, n2), Indicate(cards["exch"], color=CYAN, scale_factor=1.04),
                  run_time=1.6)
        self.wait(0.8)
        n3 = label("positivity: both arms exist, so both sides are defined", 24, AMBER).move_to(note)
        self.play(Transform(note, n3), Indicate(cards["pos"], color=AMBER, scale_factor=1.04))
        self.wait(0.8)
        fin = eq(r"E[Y \mid X=1] - E[Y \mid X=0] = E[Y(1)] - E[Y(0)] = \text{ATE}", size=38, color=RED).move_to(DOWN * 3.2)
        self.play(Write(fin))
        self.wait(2.2)
        _ = (MUTED, ID_STEP)
