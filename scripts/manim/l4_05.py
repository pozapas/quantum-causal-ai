"""L4-05 Frontdoor identification: three 3Blue1Brown-style scenes.

FrontdoorGraph       X -> M -> Y with a hidden U -> X, U -> Y.  The backdoor path cannot be blocked
                     (U is unmeasured).  The three frontdoor conditions are checked on the graph, then
                     two edits break them: a direct X -> Y arrow, and a U -> M arrow.
FrontdoorDerivation  The frontdoor formula derived term by term with TransformMatchingTex: truncated
                     factorization with U, swap the sums, replace the U-average by an X'-average.
FrontdoorAssembly    The two identified pieces as bars, P(M=1|x) and the standardized response
                     r(m) = sum_x' P(Y=1|m,x')P(x'), assembled into P(Y=1|do(x)) = 0.68 and 0.32.
Numbers come from the explicit model below (U fair, P(X=1|U) = 0.25 + 0.5U, P(M=1|X) = 0.2 + 0.6X,
P(Y=1|M,U) = 0.6M + 0.4U) and are checked by facts().
"""
import itertools
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Circle, Create, DashedVMobject, FadeIn, FadeOut, Indicate, Line,
                   Rectangle, RoundedRectangle, Scene, SurroundingRectangle, Transform, TransformMatchingTex, VGroup,
                   Write)

from qcai_style import AMBER, BLUE, CYAN, INK, MUTED, RED, VIOLET, eq, label

# ---- the explicit model with the hidden U -------------------------------------------------------
PU1 = 0.5


def p_u(u):
    return PU1 if u else 1 - PU1


def p_x(x, u):
    p = 0.25 + 0.5 * u
    return p if x else 1 - p


def p_m(m, x):
    p = 0.2 + 0.6 * x
    return p if m else 1 - p


def p_y(y, m, u):
    p = 0.6 * m + 0.4 * u
    return p if y else 1 - p


JOINT = {(u, x, m, y): p_u(u) * p_x(x, u) * p_m(m, x) * p_y(y, m, u)
         for u, x, m, y in itertools.product((0, 1), repeat=4)}


def P(**fix):
    return sum(v for (u, x, m, y), v in JOINT.items()
               if all({"u": u, "x": x, "m": m, "y": y}[k] == val for k, val in fix.items()))


PX = {x: P(x=x) for x in (0, 1)}
PM1 = {x: P(x=x, m=1) / PX[x] for x in (0, 1)}                                   # P(M=1 | x)
PY1 = {(m, x): P(m=m, x=x, y=1) / P(m=m, x=x) for m in (0, 1) for x in (0, 1)}    # P(Y=1 | m, x)
RESP = {m: sum(PY1[(m, x)] * PX[x] for x in (0, 1)) for m in (0, 1)}             # standardized response
FD = {x: PM1[x] * RESP[1] + (1 - PM1[x]) * RESP[0] for x in (0, 1)}              # frontdoor formula
TRUE = {x: sum(p_u(u) * p_m(m, x) * p_y(1, m, u) for u in (0, 1) for m in (0, 1)) for x in (0, 1)}
NAIVE = {x: P(x=x, y=1) / PX[x] for x in (0, 1)}
close = lambda a, b: abs(a - b) < 1e-12  # noqa: E731
assert close(PX[1], 0.5) and close(PM1[1], 0.8) and close(PM1[0], 0.2)
assert close(PY1[(1, 0)], 0.7) and close(PY1[(1, 1)], 0.9) and close(PY1[(0, 0)], 0.1) and close(PY1[(0, 1)], 0.3)
assert close(RESP[1], 0.8) and close(RESP[0], 0.2)
assert close(FD[1], 0.68) and close(FD[0], 0.32) and close(TRUE[1], 0.68) and close(TRUE[0], 0.32)
assert close(NAIVE[1], 0.78) and close(NAIVE[0], 0.22)

INDEP_Y = r"Y \perp\!\!\!\perp X \mid M, U"
INDEP_U = r"U \perp\!\!\!\perp M \mid X"


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["0.68", "0.32", "0.36", "0.56", "0.8(0.8) + 0.2(0.2)", INDEP_Y, INDEP_U]


# ---- graph toolkit --------------------------------------------------------------------------------
R_NODE = 0.36


def node(name, pos, color=INK, dashed=False):
    c = Circle(radius=R_NODE, color=color, stroke_width=3).set_fill("#ffffff", 1).move_to(pos)
    if dashed:
        c = DashedVMobject(c, num_dashes=14).set_color(color)
    return VGroup(c, eq(name, size=36, color=color).move_to(pos))


def edge(a, b, color=MUTED, width=4, dashed=False):
    ar = Arrow(a, b, buff=R_NODE + 0.05, color=color, stroke_width=width, tip_length=0.22,
               max_tip_length_to_length_ratio=0.25)
    if dashed:
        ar = VGroup(DashedVMobject(Line(ar.get_start(), ar.get_end() - (ar.get_end() - ar.get_start()) * 0.08),
                                   num_dashes=9, color=color).set_stroke(color, width), ar.tip.copy())
    return ar


def hl(a, b, color, width=12):
    d = (b - a) / (((b - a) ** 2).sum() ** 0.5)
    return Line(a + d * R_NODE, b - d * R_NODE, color=color, stroke_width=width, stroke_opacity=0.7)


class FrontdoorGraph(Scene):
    def construct(self):
        title = label("A hidden confounder and a mediator chain", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        P_ = {"X": LEFT * 5.4 + DOWN * 1.2, "M": LEFT * 3.4 + DOWN * 1.2, "Y": LEFT * 1.4 + DOWN * 1.2,
              "U": LEFT * 3.4 + UP * 1.3}
        X, M, Y = node("X", P_["X"], VIOLET), node("M", P_["M"]), node("Y", P_["Y"], VIOLET)
        U = node("U", P_["U"], MUTED, dashed=True)
        ulab = label("unmeasured", 22, MUTED).next_to(U, UP, buff=0.12)
        exm, emy = edge(P_["X"], P_["M"]), edge(P_["M"], P_["Y"])
        eux, euy = edge(P_["U"], P_["X"], MUTED, dashed=True), edge(P_["U"], P_["Y"], MUTED, dashed=True)
        self.play(Write(title), FadeIn(X), FadeIn(M), FadeIn(Y), run_time=1.0)
        self.play(Create(exm), Create(emy))
        self.play(FadeIn(U), FadeIn(ulab), Create(eux), Create(euy))
        self.add_foreground_mobjects(X, M, Y, U)

        bd = VGroup(hl(P_["X"], P_["U"], RED), hl(P_["U"], P_["Y"], RED))
        msg = label("backdoor path X ← U → Y: cannot condition on U", 26, RED).move_to(RIGHT * 2.9 + UP * 2.4)
        self.play(Create(bd), FadeIn(msg))
        self.wait(0.8)
        nope = label("so backdoor adjustment is unavailable", 24, MUTED).next_to(msg, DOWN, buff=0.15)
        self.play(FadeIn(nope))
        self.wait(0.8)
        self.play(FadeOut(bd), FadeOut(msg), FadeOut(nope))

        def card(text, y):
            t = label(text, 24, INK)
            box = RoundedRectangle(corner_radius=0.12, width=t.width + 0.45, height=t.height + 0.36, stroke_color=CYAN,
                                   stroke_width=2).set_fill("#ffffff", 1)
            return VGroup(box, t).move_to(RIGHT * 3.15 + UP * y)

        c1 = card("1. M intercepts all directed paths X → Y", 2.35)
        c2 = card("2. no open backdoor path from X to M", 1.05)
        c3 = card("3. X blocks all backdoor paths from M to Y", -0.25)
        # condition 1
        h1 = VGroup(hl(P_["X"], P_["M"], BLUE), hl(P_["M"], P_["Y"], BLUE))
        self.play(FadeIn(c1), Create(h1))
        tick1 = label("holds", 22, CYAN, "BOLD").next_to(c1, DOWN, buff=0.06).align_to(c1, RIGHT)
        self.play(FadeIn(tick1))
        self.play(FadeOut(h1))
        # condition 2: X <- U -> Y <- M is blocked at the collider Y
        h2 = VGroup(hl(P_["X"], P_["U"], AMBER), hl(P_["U"], P_["Y"], AMBER), hl(P_["M"], P_["Y"], AMBER))
        coll = label("collider Y blocks X ← U → Y ← M", 22, AMBER).next_to(c2, DOWN, buff=0.06).align_to(c2, RIGHT)
        self.play(FadeIn(c2), Create(h2))
        self.play(FadeIn(coll), Indicate(Y, color=AMBER))
        self.play(FadeOut(h2))
        # condition 3: M <- X <- U -> Y is blocked by conditioning on X
        h3 = VGroup(hl(P_["M"], P_["X"], AMBER), hl(P_["X"], P_["U"], AMBER), hl(P_["U"], P_["Y"], AMBER))
        ring = SurroundingRectangle(X, color=CYAN, buff=0.06, stroke_width=4)
        by_x = label("conditioning on X blocks M ← X ← U → Y", 22, AMBER).next_to(c3, DOWN, buff=0.06).align_to(c3, RIGHT)
        self.play(FadeIn(c3), Create(h3))
        self.play(Create(ring), FadeIn(by_x))
        self.play(FadeOut(h3))
        self.wait(0.6)

        # break it: a direct arrow X -> Y
        direct = Arrow(P_["X"] + DOWN * 0.3, P_["Y"] + DOWN * 0.3, buff=0.12, color=RED, stroke_width=4, path_arc=1.2,
                       tip_length=0.22, max_tip_length_to_length_ratio=0.1)
        bad1 = label("direct X → Y: condition 1 fails", 24, RED, "BOLD").move_to(RIGHT * 3.25 + DOWN * 1.75)
        fail1 = label("fails", 22, RED, "BOLD").move_to(tick1)
        self.play(Create(direct), FadeIn(bad1), Indicate(c1, color=RED), FadeOut(tick1), FadeIn(fail1))
        self.wait(1.0)
        self.play(FadeOut(direct), FadeOut(bad1), FadeOut(fail1), FadeIn(tick1))
        um = edge(P_["U"], P_["M"], RED)
        bad2 = label("U → M: conditions 2 and 3 fail", 24, RED, "BOLD").move_to(RIGHT * 3.25 + DOWN * 1.75)
        fail2 = label("fails: X ← U → M is open", 22, RED, "BOLD").next_to(c2, DOWN, buff=0.06).align_to(c2, RIGHT)
        fail3 = label("fails: M ← U → Y avoids X", 22, RED, "BOLD").next_to(c3, DOWN, buff=0.06).align_to(c3, RIGHT)
        self.play(Create(um), FadeIn(bad2), Indicate(c2, color=RED), Indicate(c3, color=RED),
                  FadeOut(coll), FadeOut(by_x), FadeIn(fail2), FadeIn(fail3))
        self.wait(1.0)
        moral = label("a measured mediator alone is not enough", 26, INK, "BOLD").move_to(RIGHT * 3.1 + DOWN * 2.6)
        self.play(FadeIn(moral))
        self.wait(1.8)


class FrontdoorDerivation(Scene):
    def construct(self):
        title = label("Deriving the frontdoor formula", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        S = 40
        l0 = eq(r"P(y \mid \operatorname{do}(x))", "=", r"\sum_u", r"\sum_m", "P(u)", r"P(m \mid x)", r"P(y \mid m, u)", size=S)
        l1 = eq(r"P(y \mid \operatorname{do}(x))", "=", r"\sum_m", r"P(m \mid x)", r"\sum_u", r"P(y \mid m, u)", "P(u)", size=S)
        l2 = eq(r"P(y \mid \operatorname{do}(x))", "=", r"\sum_m", r"P(m \mid x)", r"\sum_{x'}", r"P(y \mid m, x')", "P(x')",
                size=S)
        for m in (l0, l1, l2):
            m.move_to(UP * 1.9)
        why0 = label("truncated factorization on the full graph, U included", 24, MUTED).next_to(l0, DOWN, buff=0.3)
        self.play(Write(l0))
        self.play(FadeIn(why0))
        self.wait(1.2)
        why1 = label("collect the terms that depend on u", 24, MUTED).move_to(why0)
        self.play(TransformMatchingTex(l0, l1), Transform(why0, why1), run_time=1.6)
        self.wait(0.8)
        box = SurroundingRectangle(VGroup(l1[4], l1[5], l1[6]), color=AMBER, buff=0.08)
        self.play(Create(box))
        warn = label("U is unmeasured: this inner average is not yet computable", 24, AMBER).move_to(why0)
        self.play(Transform(why0, warn))
        self.wait(0.8)

        # the lemma, derived below
        k0 = eq(r"\sum_{x'} P(x')\,P(y \mid m, x')", "=", r"\sum_{x'} P(x') \sum_u P(y \mid m, u, x')\,P(u \mid m, x')", size=34)
        k1 = eq(r"\sum_{x'} P(x')\,P(y \mid m, x')", "=", r"\sum_{x'} P(x') \sum_u P(y \mid m, u)\,P(u \mid x')", size=34)
        k2 = eq(r"\sum_{x'} P(x')\,P(y \mid m, x')", "=", r"\sum_u P(y \mid m, u)\,P(u)", size=34)
        for k in (k0, k1, k2):
            k.move_to(DOWN * 0.35)
        self.play(Write(k0))
        r0 = label("condition on U inside each x' stratum", 24, MUTED).next_to(k0, DOWN, buff=0.3)
        self.play(FadeIn(r0))
        self.wait(1.0)
        r1 = VGroup(eq(INDEP_Y, size=34, color=CYAN), eq(INDEP_U, size=34, color=CYAN)).arrange(RIGHT, buff=0.8)
        r1.move_to(r0)
        self.play(TransformMatchingTex(k0, k1), FadeOut(r0), FadeIn(r1), run_time=1.6)
        self.wait(1.2)
        r2 = label("sum over x': the mixture of P(u | x') is P(u)", 24, MUTED).move_to(r1)
        self.play(TransformMatchingTex(k1, k2), FadeOut(r1), FadeIn(r2), run_time=1.6)
        self.wait(1.2)
        self.play(FadeOut(box))
        sub = label("substitute: every term is now observable", 24, CYAN).move_to(why0)
        self.play(TransformMatchingTex(l1, l2), Transform(why0, sub), run_time=1.8)
        fin = SurroundingRectangle(l2, color=VIOLET, buff=0.15)
        self.play(Create(fin))
        num = eq(r"P(Y=1 \mid \operatorname{do}(X=1)) = 0.8(0.8) + 0.2(0.2) = 0.68", size=38, color=VIOLET)
        num.move_to(DOWN * 2.55)
        self.play(FadeOut(k2), FadeOut(r2), Write(num))
        num0 = eq(r"P(Y=1 \mid \operatorname{do}(X=0)) = 0.2(0.8) + 0.8(0.2) = 0.32", size=38, color=BLUE)
        num0.next_to(num, DOWN, buff=0.25)
        self.play(Write(num0))
        self.wait(2.2)


class FrontdoorAssembly(Scene):
    def construct(self):
        title = label("Two identified pieces, one causal effect", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        HS, BASE = 2.2, -0.85

        def bars(vals, names, cx, color, head):
            g = VGroup()
            for i, (v, n) in enumerate(zip(vals, names)):
                x = cx + (i - 0.5) * 1.5
                r = Rectangle(width=1.0, height=v * HS, stroke_color=color, stroke_width=3).set_fill(color, 0.4)
                r.move_to([x, BASE + v * HS / 2, 0])
                g.add(VGroup(r, label(f"{v:.1f}", 24, INK).next_to(r, UP, buff=0.08),
                             eq(n, size=30, color=MUTED).move_to([x, BASE - 0.32, 0])))
            base = Line([cx - 1.6, BASE, 0], [cx + 1.6, BASE, 0], color=MUTED, stroke_width=2)
            h = head.move_to([cx, 2.25, 0])
            return VGroup(base, g, h)

        piece1 = eq(r"P(m \mid x)", size=40, color=VIOLET)
        piece2 = eq(r"\sum_{x'} P(y \mid m, x')\, P(x')", size=40, color=CYAN)
        A = bars([PM1[0], PM1[1]], ["x=0", "x=1"], -3.4, VIOLET, piece1)
        B = bars([RESP[0], RESP[1]], ["m=0", "m=1"], 3.4, CYAN, piece2)
        capA = label("piece 1: P(M = 1 | x), no open backdoor X to M", 22, MUTED).move_to([-3.4, 1.5, 0])
        capB = label("piece 2: adjust for X to get M's effect on Y", 22, MUTED).move_to([3.4, 1.5, 0])
        self.play(FadeIn(A), FadeIn(capA), run_time=1.2)
        self.wait(0.6)
        calc = VGroup(eq(r"r(1) = 0.5(0.7) + 0.5(0.9) = 0.8", size=30), eq(r"r(0) = 0.5(0.1) + 0.5(0.3) = 0.2", size=30))
        calc.arrange(DOWN, buff=0.15).move_to([3.4, 0.6, 0])
        self.play(FadeIn(B[0]), Write(B[2]), FadeIn(capB))
        self.play(Write(calc))
        self.play(FadeOut(calc), FadeIn(B[1]))
        self.wait(0.8)

        # assemble: the two pieces fly into the formula
        whole = eq(r"P(y \mid \operatorname{do}(x)) = \sum_m", r"P(m \mid x)", r"\sum_{x'} P(y \mid m, x')\, P(x')", size=40)
        whole[1].set_color(VIOLET)
        whole[2].set_color(CYAN)
        whole.move_to(DOWN * 2.25)
        self.play(Write(whole[0]))
        self.play(Transform(piece1.copy(), whole[1]), Transform(piece2.copy(), whole[2]), run_time=1.6)
        self.add(whole[1], whole[2])
        self.wait(0.8)
        res = eq(r"\operatorname{do}(X=1):\ 0.68 \qquad \operatorname{do}(X=0):\ 0.32 \qquad \text{effect } 0.36", size=36, color=RED)
        res.move_to(DOWN * 3.02)
        self.play(Write(res))
        self.wait(0.8)
        cmp = label("naive contrast 0.78 - 0.22 = 0.56 is biased by U", 24, MUTED).move_to(DOWN * 3.6)
        self.play(FadeIn(cmp))
        self.wait(2.2)
        _ = (TRUE, BLUE)
