"""L6-06 Bell inequalities and causal inequalities: three scenes.

ThreeCeilings    the CHSH number S = E00 + E01 + E10 - E11 and its three ceilings: 2 for local
                 deterministic models (one bracket vanishes), 2 sqrt 2 for quantum models (the square of
                 the CHSH operator), 4 for the no-signaling PR box.
PolytopeShadow   the images of the local, quantum and no-signaling sets in the plane of two CHSH
                 expressions (S1, S2): the 16 deterministic boxes land on 4 corners of a square, a quantum
                 strategy sweeps the circle of radius 2 sqrt 2, and the PR boxes span a diamond.
OcbGame          the Oreshkov-Costa-Brukner game: a definite order caps the success probability at 3/4,
                 while the process matrix W_OCB reaches (2 + sqrt 2)/4.
Every number on screen is computed here; facts() lists strings that also appear in the lesson text.
"""
import itertools
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Create, DashedLine, Dot, FadeIn, FadeOut, GrowFromEdge, Line,
                   NumberLine, Polygon, Rectangle, RoundedRectangle, Scene, Square, TracedPath, Transform,
                   TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

SQ2 = math.sqrt(2)
TSIRELSON = 2 * SQ2                      # 2.828...
OCB_P = (2 + SQ2) / 4                    # 0.8536
assert abs(OCB_P - (0.5 + 2 * SQ2 / 8)) < 1e-12        # CHSH game value 1/2 + S/8 at S = 2 sqrt 2 is the same number


def S12(E):
    E00, E01, E10, E11 = E
    return (E00 + E01 + E10 - E11, -E00 + E01 + E10 + E11)


DET = [S12((a0 * b0, a0 * b1, a1 * b0, a1 * b1)) for a0, a1, b0, b1 in itertools.product((1, -1), repeat=4)]
assert sorted(set(DET)) == [(-2, -2), (-2, 2), (2, -2), (2, 2)]          # local image: square |S1|, |S2| <= 2
assert S12((1, 1, 1, -1)) == (4, 0)                                    # PR box


def quantum_point(phi):
    """|Phi+>, Alice angles 0 and pi/2, Bob angles phi + pi/4 and phi - pi/4 in the X-Z plane: E_xy = cos(a_x - b_y)."""
    al = (0.0, math.pi / 2)
    be = (phi + math.pi / 4, phi - math.pi / 4)
    E = [math.cos(al[x] - be[y]) for x in (0, 1) for y in (0, 1)]
    return S12(E)


for _phi in np.linspace(0, 2 * math.pi, 13):
    _p = quantum_point(_phi)
    assert abs(_p[0] - TSIRELSON * math.cos(_phi)) < 1e-12 and abs(_p[1] - TSIRELSON * math.sin(_phi)) < 1e-12


def facts(L):
    """Strings shown on screen that also appear in the lesson text."""
    return ["2\\sqrt{2}", "4I - [A_0, A_1]\\otimes[B_0, B_1]", "3/4", "(2+\\sqrt{2})/4", "0.854", "(4, 0)",
            "\\beta_0 = \\varphi + \\pi/4"]


class ThreeCeilings(Scene):
    def construct(self):
        title = label("One number, three ceilings", 36, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        s_def = eq("S", "=", "E_{00}", "+", "E_{01}", "+", "E_{10}", "-", "E_{11}", size=42).next_to(title, DOWN, buff=0.35)
        self.play(Write(s_def))

        # local deterministic: one bracket vanishes
        head1 = label("Local deterministic: every outcome fixed as +1 or -1 in advance", 26, BLUE).move_to(UP * 1.55)
        l1 = eq("S", "=", "a_0 b_0", "+", "a_0 b_1", "+", "a_1 b_0", "-", "a_1 b_1", size=40).move_to(UP * 0.75)
        l2 = eq("S", "=", "a_0", "(b_0 + b_1)", "+", "a_1", "(b_0 - b_1)", size=40).move_to(l1)
        l3 = eq(r"\text{one bracket is } 0, \text{ the other } \pm 2", r"\;\Rightarrow\;", r"|S| \le 2", size=36,
                color=BLUE).move_to(DOWN * 0.1)
        self.play(FadeIn(head1))
        self.play(Write(l1))
        self.play(TransformMatchingTex(l1, l2), run_time=1.6)
        self.play(Write(l3))
        self.wait(1.2)
        self.play(FadeOut(VGroup(head1, l2, l3)))

        # quantum: square of the CHSH operator
        head2 = label("Quantum: observables with eigenvalues +1 and -1", 26, VIOLET).move_to(UP * 1.55)
        q1 = eq("C", "=", r"A_0\otimes(B_0 + B_1)", "+", r"A_1\otimes(B_0 - B_1)", size=38).move_to(UP * 0.8)
        q2 = eq("C^2", "=", r"4I - [A_0, A_1]\otimes[B_0, B_1]", size=40).move_to(DOWN * 0.05)
        q3 = eq(r"\|[A_0, A_1]\| \le 2", r"\;\Rightarrow\;", r"\|C^2\| \le 8", r"\;\Rightarrow\;", r"|S| \le 2\sqrt{2}",
                size=38, color=VIOLET).move_to(DOWN * 0.95)
        self.play(FadeIn(head2))
        self.play(Write(q1))
        self.play(Write(q2), run_time=1.5)
        self.play(Write(q3), run_time=1.5)
        self.wait(1.2)
        self.play(FadeOut(VGroup(head2, q1, q2, q3)))

        # no-signaling: PR box
        head3 = label("No-signaling only: the PR box", 26, RED).move_to(UP * 1.55)
        pr = eq(r"E_{00} = E_{01} = E_{10} = 1,\; E_{11} = -1", r"\;\Rightarrow\;", r"S = 4", size=38,
                color=RED).move_to(UP * 0.75)
        pr2 = label("every marginal is 1/2, so no setting signals", 24, MUTED).next_to(pr, DOWN, buff=0.2)
        self.play(FadeIn(head3), Write(pr))
        self.play(FadeIn(pr2))
        self.wait(0.6)

        nl = NumberLine(x_range=[0, 4.4, 1], length=10, color=MUTED, include_numbers=False).move_to(DOWN * 2.2)
        nums = VGroup(*[label(str(k), 24, MUTED).next_to(nl.n2p(k), DOWN, buff=0.18) for k in range(5)])
        self.play(Create(nl), FadeIn(nums))
        marks = [(2, BLUE, "local 2", UP), (TSIRELSON, VIOLET, "quantum 2√2 ≈ 2.83", DOWN), (4, RED, "no-signaling 4", UP)]
        for val, col, txt, side in marks:
            d = Dot(nl.n2p(val), color=col, radius=0.11)
            t = label(txt, 24, col).next_to(d, side, buff=0.55 if side is DOWN else 0.25)
            self.play(FadeIn(d, scale=0.5), Write(t), run_time=0.9)
        self.wait(1.8)


class PolytopeShadow(Scene):
    def construct(self):
        ax = Axes(x_range=[-4.6, 4.6, 1], y_range=[-4.6, 4.6, 1], x_length=6.9, y_length=6.9,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 2},
                  ).shift(LEFT * 3.1 + DOWN * 0.15)
        grid = VGroup(*[Line(ax.c2p(k, -4.4), ax.c2p(k, 4.4), color=GRID, stroke_width=1) for k in range(-4, 5) if k]
                      + [Line(ax.c2p(-4.4, k), ax.c2p(4.4, k), color=GRID, stroke_width=1) for k in range(-4, 5) if k])
        xl = eq("S_1", size=32).next_to(ax.c2p(4.6, 0), UP, buff=0.15)
        yl = eq("S_2", size=32).next_to(ax.c2p(0, 4.6), LEFT, buff=0.15)
        ticks = VGroup(*[label(str(k), 24, MUTED).next_to(ax.c2p(k, 0), DOWN + LEFT, buff=0.08) for k in (-2, 2)])
        self.play(Create(grid), Create(ax), Write(xl), Write(yl), FadeIn(ticks), run_time=1.5)

        rx = 3.85
        d1 = eq(r"S_1 = E_{00} + E_{01} + E_{10} - E_{11}", size=30).move_to(RIGHT * rx + UP * 3.3)
        d2 = eq(r"S_2 = -E_{00} + E_{01} + E_{10} + E_{11}", size=30).move_to(RIGHT * rx + UP * 2.75)
        self.play(Write(d1), Write(d2))

        # 16 deterministic boxes fly to 4 corners
        bank = VGroup(*[Dot(radius=0.07, color=BLUE) for _ in DET]).arrange_in_grid(2, 8, buff=0.22)
        bank.move_to(RIGHT * rx + UP * 1.85)
        bl = label("16 deterministic local boxes", 24, BLUE).next_to(bank, DOWN, buff=0.15)
        self.play(FadeIn(bank, lag_ratio=0.1), FadeIn(bl))
        targets = [Dot(ax.c2p(*p), radius=0.09, color=BLUE) for p in DET]
        self.play(*[Transform(bank[i], targets[i]) for i in range(len(DET))], run_time=2)
        sq = Polygon(*[ax.c2p(*p) for p in ((2, 2), (-2, 2), (-2, -2), (2, -2))], color=BLUE, fill_color=BLUE,
                     fill_opacity=0.18, stroke_width=3)
        self.play(Create(sq), FadeOut(bl))
        loc = eq(r"\text{local: } |S_1|, |S_2| \le 2", size=30, color=BLUE).move_to(RIGHT * rx + UP * 1.3)
        self.play(Write(loc))

        # quantum sweep
        phi = ValueTracker(0.0)
        qd = always_redraw(lambda: Dot(ax.c2p(*quantum_point(phi.get_value())), radius=0.09, color=VIOLET))
        trace = TracedPath(qd.get_center, stroke_color=VIOLET, stroke_width=4)
        qtxt = VGroup(eq(r"|\Phi^+\rangle:\ \alpha_0 = 0,\ \alpha_1 = \pi/2", size=28, color=VIOLET),
                      eq(r"\beta_0 = \varphi + \pi/4,\ \beta_1 = \varphi - \pi/4", size=28, color=VIOLET)
                      ).arrange(DOWN, buff=0.12).move_to(RIGHT * rx + UP * 0.3)
        self.play(Write(qtxt))
        self.add(trace, qd)
        self.play(phi.animate.set_value(2 * math.pi), run_time=7, rate_func=linear)
        qlab = eq(r"\text{quantum: } S_1^2 + S_2^2 \le 8", size=30, color=VIOLET).move_to(RIGHT * rx + DOWN * 0.7)
        self.play(Write(qlab))
        tp = Dot(ax.c2p(TSIRELSON, 0), radius=0.09, color=VIOLET)
        tpl = eq(r"(2\sqrt{2}, 0)", size=26, color=VIOLET).next_to(tp, UP + RIGHT * 0.2, buff=0.08)
        self.play(FadeIn(tp), Write(tpl))

        # no-signaling: PR boxes
        prs = [(4, 0), (0, 4), (-4, 0), (0, -4)]
        prd = VGroup(*[Dot(ax.c2p(*p), radius=0.1, color=RED) for p in prs])
        dia = Polygon(*[ax.c2p(*p) for p in prs], color=RED, stroke_width=3)
        self.play(FadeIn(prd, scale=0.5))
        self.play(Create(dia), run_time=1.5)
        prl = eq("(4, 0)", size=26, color=RED).next_to(ax.c2p(4, 0), DOWN, buff=0.18)
        nsl = eq(r"\text{no-signaling: } |S_1| + |S_2| \le 4", size=30, color=RED).move_to(RIGHT * rx + DOWN * 1.35)
        self.play(Write(prl), Write(nsl))

        # the three touch at (2, 2)
        ring = Dot(ax.c2p(2, 2), radius=0.2, color=AMBER, fill_opacity=0).set_stroke(AMBER, 4)
        touch = label("all three meet at (±2, ±2)", 24, AMBER).move_to(RIGHT * rx + DOWN * 2.1)
        note = label("a projection of the sets, not a slice", 24, MUTED).move_to(RIGHT * rx + DOWN * 2.7)
        self.play(Create(ring), FadeIn(touch))
        self.play(FadeIn(note))
        self.wait(2)


class OcbGame(Scene):
    def lab(self, name, color, pos):
        box = RoundedRectangle(corner_radius=0.15, width=2.2, height=1.5, color=color, stroke_width=4).move_to(pos)
        nm = label(name, 28, color, "BOLD").move_to(box)
        inp = Line(box.get_bottom() + DOWN * 0.55, box.get_bottom(), color=color, stroke_width=4)
        out = Line(box.get_top(), box.get_top() + UP * 0.55, color=color, stroke_width=4)
        return VGroup(box, nm, inp, out)

    def construct(self):
        title = label("A causal inequality: the OCB game", 36, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        A = self.lab("Alice", BLUE, LEFT * 5.3 + UP * 0.6)
        B = self.lab("Bob", CYAN, LEFT * 1.6 + UP * 0.6)
        self.play(FadeIn(A), FadeIn(B))
        bits = VGroup(eq("a", size=34, color=BLUE).next_to(A[0], LEFT, buff=0.2),
                      eq("b,\\ b'", size=34, color=CYAN).next_to(B[0], RIGHT, buff=0.2))
        gx = VGroup(eq("x", size=34, color=BLUE).next_to(A[0], DOWN + RIGHT * 0.5, buff=0.15),
                    eq("y", size=34, color=CYAN).next_to(B[0], DOWN + RIGHT * 0.5, buff=0.15))
        self.play(Write(bits), Write(gx))
        rules = VGroup(eq(r"b' = 0:\ \text{Alice guesses } b\ (x = b)", size=30),
                       eq(r"b' = 1:\ \text{Bob guesses } a\ (y = a)", size=30)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        rules.move_to(RIGHT * 3.75 + UP * 1.75)
        self.play(Write(rules))
        psucc = eq(r"p_{\rm succ}", "=", r"\tfrac12\big[P(x = b \mid b' = 0)", "+", r"P(y = a \mid b' = 1)\big]",
                   size=30).move_to(RIGHT * 3.85 + UP * 0.55)
        self.play(Write(psucc))

        # definite order A before B
        arrow = Arrow(A[0].get_right(), B[0].get_left(), color=AMBER, stroke_width=6, buff=0.08)
        ord_l = eq(r"A \prec B", size=34, color=AMBER).next_to(arrow, UP, buff=0.25)
        self.play(Create(arrow), Write(ord_l))
        why = label("Alice acts first, so x cannot depend on b", 22, AMBER).move_to(RIGHT * 3.7 + DOWN * 0.3)
        self.play(FadeIn(why))
        bound1 = eq(r"p_{\rm succ}", "=", r"\tfrac12\big[\tfrac12", "+", r"P(y = a \mid b' = 1)\big]", size=30).move_to(psucc)
        self.play(TransformMatchingTex(psucc, bound1), run_time=1.4)
        bound2 = eq(r"p_{\rm succ}", r"\le", r"\tfrac12\big[\tfrac12", "+", r"1\big]", "=", "3/4", size=34).move_to(psucc)
        self.play(TransformMatchingTex(bound1, bound2), run_time=1.4)
        mix = VGroup(label("the same cap holds for B before A", 24, MUTED), label("and for any mixture of the two orders", 24, MUTED)).arrange(DOWN, buff=0.08).move_to(RIGHT * 3.85 + DOWN * 1.05)
        self.play(FadeIn(mix))
        self.wait(1.0)
        self.play(FadeOut(VGroup(arrow, ord_l, why, mix)))

        # the OCB process
        W = eq(r"W_{\rm OCB} = \tfrac14\big[I + \tfrac{1}{\sqrt2}(Z^{A_2} Z^{B_1} + Z^{A_1} X^{B_1} Z^{B_2})\big]",
               size=32, color=VIOLET).move_to(LEFT * 3.0 + DOWN * 1.55)
        self.play(Write(W))
        wl = label("no definite order between the labs", 24, VIOLET).next_to(W, DOWN, buff=0.15)
        self.play(FadeIn(wl))

        # bars
        base = RIGHT * 1.8 + DOWN * 3.3
        scale = 2.9
        axis = Line(base, base + RIGHT * 4.8, color=MUTED)
        vals = [(0.75, BLUE, "causal order", "3/4"), (OCB_P, VIOLET, "W_OCB", "0.854"), (1.0, MUTED, "ceiling", "1")]
        self.play(Create(axis), FadeOut(rules))
        bars = VGroup()
        for i, (v, col, name, txt) in enumerate(vals):
            r = Rectangle(width=0.9, height=v * scale, color=col, fill_color=col, fill_opacity=0.6).move_to(
                base + RIGHT * (0.8 + 1.6 * i) + UP * v * scale / 2)
            nm = label(name, 24, col).next_to(r, DOWN, buff=0.12)
            tv = label(txt, 24, col).next_to(r, UP, buff=0.08)
            bars.add(VGroup(r, nm, tv))
            self.play(GrowFromEdge(r, DOWN), FadeIn(nm), FadeIn(tv), run_time=0.9)
        cap = DashedLine(base + UP * 0.75 * scale, base + UP * 0.75 * scale + RIGHT * 4.8, color=BLUE)
        self.play(Create(cap))
        fin = eq(r"(2+\sqrt{2})/4 > 3/4", size=34, color=VIOLET).move_to(LEFT * 3.0 + DOWN * 3.0)
        self.play(Write(fin))
        self.wait(2)
        _ = (Square, CYAN, RED)
