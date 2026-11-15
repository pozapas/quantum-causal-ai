"""L5-08 Bell correlations and the CHSH test: three 3Blue1Brown-style scenes.

CHSH form used throughout:  S = E(a0,b0) + E(a0,b1) + E(a1,b0) - E(a1,b1), outcomes +1 / -1.
Angles are polarizer angles: A(t) = cos(2t) Z + sin(2t) X, so for |Phi+> E(a,b) = cos 2(a - b).

LocalStrategies      the 16 local deterministic strategies (A0, A1, B0, B1), each giving S = +2 or -2; the algebra
                     A0(B0 + B1) + A1(B0 - B1); mixtures with p(lambda) independent of the settings stay in [-2, 2].
QuantumAngles        the family a0 = 0, a1 = 2 phi, b0 = phi, b1 = -phi on a polarizer dial; live correlation terms and
                     the trace of S(phi) = 3 cos 2phi - cos 6phi, which reaches 2 sqrt 2 at phi = 22.5 degrees.
TsirelsonDerivation  S^2 = 4 I - [A0, A1] (x) [B0, B1], the norm bound, the sum-of-squares certificate and the
                     optimal Pauli observables.
Numbers are computed here and checked against the lesson text by facts().
"""
import itertools
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, ORIGIN, PI, RIGHT, UP, Arrow, Axes, Circle, Create, DashedLine, DecimalNumber,
                   Dot, FadeIn, FadeOut, Indicate, Line, NumberLine, Rectangle, RoundedRectangle, Scene,
                   SurroundingRectangle, TracedPath, TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw,
                   linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

SQ2 = math.sqrt(2)
NUMCFG = {"color": INK, "num_decimal_places": 0}


def chsh(E):
    return E[0][0] + E[0][1] + E[1][0] - E[1][1]


STRATS = list(itertools.product([1, -1], repeat=4))          # (A0, A1, B0, B1)
S_LOCAL = [chsh([[a0 * b0, a0 * b1], [a1 * b0, a1 * b1]]) for a0, a1, b0, b1 in STRATS]
assert len(STRATS) == 16 and sorted(set(S_LOCAL)) == [-2, 2] and S_LOCAL.count(2) == 8


def E_q(a, b):
    """Correlation of |Phi+> for polarizer angles a, b (radians)."""
    return math.cos(2 * (a - b))


def angles(phi):
    return 0.0, 2 * phi, phi, -phi                           # a0, a1, b0, b1


def S_q(phi):
    a0, a1, b0, b1 = angles(phi)
    return E_q(a0, b0) + E_q(a0, b1) + E_q(a1, b0) - E_q(a1, b1)


OPT = math.pi / 8
assert abs(S_q(OPT) - 2 * SQ2) < 1e-12
assert all(abs(S_q(p) - (3 * math.cos(2 * p) - math.cos(6 * p))) < 1e-12 for p in np.linspace(0, math.pi / 2, 19))
assert abs(S_q(0) - 2) < 1e-12 and abs(S_q(3 * math.pi / 8) + 2 * SQ2) < 1e-12

# operator identity, checked numerically with seeded random +-1 observables
_rng = np.random.default_rng(3)


def _rand_obs(d):
    M = _rng.normal(size=(d, d)) + 1j * _rng.normal(size=(d, d))
    H = M + M.conj().T
    w, U = np.linalg.eigh(H)
    return U @ np.diag(np.sign(w)) @ U.conj().T


_A0, _A1, _B0, _B1 = (_rand_obs(3) for _ in range(4))
_I = np.eye(3)
_S = np.kron(_A0, _B0 + _B1) + np.kron(_A1, _B0 - _B1)
_comm = lambda P, Q: P @ Q - Q @ P  # noqa: E731
assert np.allclose(_S @ _S, 4 * np.eye(9) - np.kron(_comm(_A0, _A1), _comm(_B0, _B1)))


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["|S| \\le 2", "2\\sqrt{2}", "E(a,b) = \\cos 2(a - b)", "3\\cos 2\\varphi - \\cos 6\\varphi",
            "S^2 = 4\\,I - [A_0, A_1] \\otimes [B_0, B_1]", "A_0(B_0 + B_1) + A_1(B_0 - B_1)"]


def sgn(v):
    return "+" if v > 0 else "-"


class LocalStrategies(Scene):
    def construct(self):
        title = label("Every local deterministic strategy gives S = +2 or −2", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        form = eq(r"S = E_{00} + E_{01} + E_{10} - E_{11}", size=34).next_to(title, DOWN, buff=0.2)
        self.play(Write(title), Write(form))
        hdr = label("A₀ A₁ | B₀ B₁        S", 24, MUTED).move_to([-3.7, 2.05, 0])
        cards = VGroup()
        for k, (st, s) in enumerate(zip(STRATS, S_LOCAL)):
            a0, a1, b0, b1 = st
            col = BLUE if s > 0 else AMBER
            txt = eq(rf"{sgn(a0)}\,{sgn(a1)}\;|\;{sgn(b0)}\,{sgn(b1)}\quad {s:+d}", size=28, color=col)
            box = RoundedRectangle(width=2.55, height=0.55, corner_radius=0.1, stroke_color=GRID, stroke_width=1.5)
            cards.add(VGroup(box, txt))
        cards.arrange_in_grid(rows=8, cols=2, buff=(0.2, 0.06)).move_to([-3.7, -1.2, 0])
        self.play(FadeIn(hdr))
        self.play(*[FadeIn(c, shift=0.1 * DOWN) for c in cards], lag_ratio=0.12, run_time=4)

        # histogram of S over the 16 strategies
        nl = NumberLine(x_range=[-3, 3, 1], length=5.2, color=MUTED, include_numbers=True, font_size=26,
                        decimal_number_config={"color": INK, "num_decimal_places": 0}).move_to([3.3, -2.3, 0])
        band = Rectangle(width=nl.n2p(2)[0] - nl.n2p(-2)[0], height=3.1, fill_color=CYAN, fill_opacity=0.08,
                         stroke_width=0).move_to([3.3, -0.7, 0])
        unit = 0.32
        bars = VGroup(*[Rectangle(width=0.55, height=unit * 8, fill_color=c, fill_opacity=0.85, stroke_width=0)
                        .move_to(nl.n2p(v), aligned_edge=DOWN).shift(UP * 0.02) for v, c in ((-2, AMBER), (2, BLUE))])
        counts = VGroup(label("8 strategies", 24, AMBER).next_to(bars[0], UP, buff=0.1),
                        label("8 strategies", 24, BLUE).next_to(bars[1], UP, buff=0.1))
        bl = eq(r"|S| \le 2", size=34, color=CYAN).move_to([3.3, 1.75, 0])
        self.play(Create(nl), FadeIn(band))
        self.play(*[Create(b) for b in bars], FadeIn(counts))
        self.play(Write(bl))
        self.wait(1)

        # the algebra
        self.play(FadeOut(VGroup(cards, hdr, nl, band, bars, counts)), bl.animate.move_to([4.6, 2.3, 0]))
        l1 = eq("S", "=", "A_0B_0 + A_0B_1", "+", "A_1B_0 - A_1B_1", size=40)
        l2 = eq("S", "=", "A_0(B_0 + B_1)", "+", "A_1(B_0 - B_1)", size=40)
        l1.move_to([0, 1.2, 0])
        l2.move_to([0, 1.2, 0])
        self.play(Write(l1))
        self.play(TransformMatchingTex(l1, l2), run_time=1.6)
        note = VGroup(label("B₀ = B₁:  first bracket is ±2, second is 0", 26, MUTED),
                      label("B₀ = −B₁: first bracket is 0, second is ±2", 26, MUTED)).arrange(DOWN, buff=0.18)
        note.move_to([0, 0.0, 0])
        self.play(FadeIn(note))
        res = eq(r"\Rightarrow\ S = \pm 2 \text{ for every strategy}", size=36, color=RED).move_to([0, -1.1, 0])
        self.play(Write(res))
        self.wait(1)

        # mixtures: lambda chosen independently of the settings
        self.play(FadeOut(VGroup(note, res)), l2.animate.scale(0.8).move_to([-3.2, 2.3, 0]))
        mix = eq(r"S_{\rm local} = \sum_\lambda p(\lambda)\, S_\lambda,\quad p(\lambda) \text{ independent of } x, y",
                 size=34).move_to([0, 0.9, 0])
        self.play(Write(mix))
        line = NumberLine(x_range=[-3, 3, 1], length=9, color=MUTED, include_numbers=True, font_size=28,
                          decimal_number_config={"color": INK, "num_decimal_places": 0}).move_to([0, -1.2, 0])
        lo, hi = Dot(line.n2p(-2), color=AMBER, radius=0.1), Dot(line.n2p(2), color=BLUE, radius=0.1)
        w = ValueTracker(0.5)
        pt = always_redraw(lambda: Dot(line.n2p(4 * w.get_value() - 2), color=RED, radius=0.11))
        vlab = eq(r"p(S_\lambda = +2) =", size=30, color=RED)
        vnum = DecimalNumber(0.5, num_decimal_places=2, font_size=30, color=RED)
        val = VGroup(vlab, vnum)

        def upd_val(m):
            vnum.set_value(w.get_value())
            vnum.next_to(vlab, RIGHT, buff=0.12)
            m.next_to(line.n2p(4 * w.get_value() - 2), UP, buff=0.35)
        val.add_updater(upd_val)
        self.play(Create(line), FadeIn(lo), FadeIn(hi), FadeIn(pt), FadeIn(val))
        self.play(w.animate.set_value(1.0), run_time=1.6)
        self.play(w.animate.set_value(0.0), run_time=2.4)
        self.play(w.animate.set_value(0.8), run_time=1.6)
        fin = label("any mixture stays between −2 and +2", 26, MUTED).move_to([0, -2.5, 0])
        self.play(FadeIn(fin))
        self.wait(1.5)


class QuantumAngles(Scene):
    def construct(self):
        title = label("Entangled qubits push S past the local bound", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        st = eq(r"|\Phi^+\rangle,\quad A(\theta) = \cos 2\theta\, Z + \sin 2\theta\, X", size=32).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), Write(st))
        Eform = eq(r"E(a,b) = \cos 2(a - b)", size=34, color=INK).move_to([-4.0, 1.75, 0])
        self.play(Write(Eform))

        # polarizer dial
        C = np.array([-4.0, -0.75, 0])
        R = 1.5
        dial = Circle(radius=R, color=GRID, stroke_width=2).move_to(C)
        phi = ValueTracker(0.0)

        def ray(theta, col, width=5):
            d = np.array([math.cos(theta), math.sin(theta), 0])
            return Line(C - R * d, C + R * d, color=col, stroke_width=width)

        cols = [VIOLET, RED, CYAN, BLUE]
        rays = [always_redraw(lambda k=k, col=col: ray(angles(phi.get_value())[k], col)) for k, col in enumerate(cols)]
        names = [r"a_0", r"a_1", r"b_0", r"b_1"]
        tags = [always_redraw(lambda k=k, col=col: eq(names[k], size=30, color=col).move_to(
            C + (R + 0.32) * np.array([math.cos(angles(phi.get_value())[k]), math.sin(angles(phi.get_value())[k]), 0])))
            for k, col in enumerate(cols)]
        fam = eq(r"a_0 = 0,\ a_1 = 2\varphi,\ b_{0,1} = \pm\varphi", size=28, color=MUTED).move_to([-4.0, -3.3, 0])
        self.play(Create(dial), *[FadeIn(r) for r in rays], *[FadeIn(t) for t in tags], FadeIn(fam))

        # trace of S(phi)
        ax = Axes(x_range=[0, 90, 22.5], y_range=[-3, 3, 1], x_length=5.6, y_length=3.7,
                  axis_config={"color": MUTED, "include_tip": False},
                  y_axis_config={"numbers_to_include": [-2, 0, 2], "decimal_number_config": NUMCFG},
                  x_axis_config={"numbers_to_include": [45, 90], "decimal_number_config": NUMCFG}).move_to([2.9, -0.35, 0])
        xl = eq(r"\varphi\ (\text{deg})", size=26).next_to(ax.c2p(90, 0), UP + LEFT, buff=0.12)
        sl = eq(r"S(\varphi) = 3\cos 2\varphi - \cos 6\varphi", size=32, color=RED).move_to([1.9, 1.95, 0])
        loc = VGroup(DashedLine(ax.c2p(0, 2), ax.c2p(90, 2), color=CYAN), DashedLine(ax.c2p(0, -2), ax.c2p(90, -2), color=CYAN))
        tsi = VGroup(Line(ax.c2p(0, 2 * SQ2), ax.c2p(90, 2 * SQ2), color=AMBER, stroke_width=2),
                     Line(ax.c2p(0, -2 * SQ2), ax.c2p(90, -2 * SQ2), color=AMBER, stroke_width=2))
        loc_l = label("local bound", 24, CYAN).next_to(ax.c2p(70, 2), DOWN, buff=0.08)
        tsi_l = eq(r"2\sqrt{2}", size=26, color=AMBER).next_to(ax.c2p(90, 2 * SQ2), RIGHT, buff=0.08)
        self.play(Create(ax), Write(xl), Write(sl), Create(loc), Create(tsi), FadeIn(loc_l), FadeIn(tsi_l))
        dot = always_redraw(lambda: Dot(ax.c2p(math.degrees(phi.get_value()), S_q(phi.get_value())), color=RED, radius=0.07))
        trace = TracedPath(dot.get_center, stroke_color=RED, stroke_width=4)
        slab = eq("S =", size=32, color=RED).move_to([5.0, 1.95, 0])
        num = DecimalNumber(S_q(0), num_decimal_places=3, font_size=32, color=RED, include_sign=True).next_to(slab, RIGHT, buff=0.12)
        num.add_updater(lambda m: m.set_value(S_q(phi.get_value())))
        self.add(trace, dot)
        self.play(FadeIn(slab), FadeIn(num))
        self.play(phi.animate.set_value(OPT), run_time=4, rate_func=linear)

        # pause at the optimum: four correlations
        vals = eq(r"E_{00} = E_{01} = E_{10} = \tfrac{1}{\sqrt2},\ \ E_{11} = -\tfrac{1}{\sqrt2}", size=28).move_to([2.6, -2.75, 0])
        best = eq(r"S = \tfrac{4}{\sqrt2} = 2\sqrt{2} \approx 2.828", size=30, color=RED).move_to([2.6, -3.45, 0])
        self.play(Write(vals), Write(best))
        self.play(Indicate(best, color=RED))
        self.wait(1.2)
        self.play(FadeOut(vals), FadeOut(best))
        self.play(phi.animate.set_value(PI / 2), run_time=7, rate_func=linear)
        end = label("at 67.5°: S = −2.828; the sign of S is a labeling choice", 24, MUTED).move_to([2.6, -3.1, 0])
        self.play(FadeIn(end))
        self.wait(1.5)
        _ = (Arrow, RoundedRectangle, DEGREES, ORIGIN, LEFT, SurroundingRectangle)


class TsirelsonDerivation(Scene):
    def construct(self):
        title = label("Why quantum S stops at 2√2 (Tsirelson)", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        hyp = eq(r"A_x^2 = B_y^2 = I,\qquad A_x \otimes I \text{ commutes with } I \otimes B_y", size=30, color=MUTED)
        hyp.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(hyp))
        l1 = eq(r"S", "=", r"A_0 \otimes (B_0 + B_1) + A_1 \otimes (B_0 - B_1)", size=36).move_to([0, 1.3, 0])
        self.play(Write(l1))
        sq = eq(r"(B_0 \pm B_1)^2 = 2I \pm \{B_0, B_1\}", size=32, color=MUTED).move_to([0, 0.35, 0])
        self.play(FadeIn(sq))
        l2 = eq(r"S^2", "=", r"4\,I - [A_0, A_1] \otimes [B_0, B_1]", size=40).move_to([0, 1.3, 0])
        self.play(TransformMatchingTex(l1, l2), FadeOut(sq), run_time=1.8)
        box = SurroundingRectangle(l2, color=VIOLET, buff=0.15)
        self.play(Create(box))
        fact = eq(r"S^2 = 4\,I - [A_0, A_1] \otimes [B_0, B_1]", size=40)
        _ = fact
        n1 = eq(r"\|[A_0, A_1]\| \le 2\|A_0\|\,\|A_1\| = 2", size=34, color=INK).move_to([0, 0.2, 0])
        self.play(Write(n1))
        n2 = eq(r"\|S^2\| \le 4 + 2 \cdot 2 = 8", size=34).move_to([0, -0.7, 0])
        self.play(Write(n2))
        n3 = eq(r"\langle S\rangle \le \|S\| \le 2\sqrt{2}", size=40, color=RED).move_to([0, -1.65, 0])
        self.play(Write(n3))
        cls = label("commuting A's (a classical model): S² = 4I, so |S| ≤ 2", 24, MUTED).move_to([0, -2.6, 0])
        self.play(FadeIn(cls))
        self.wait(1.5)

        # sum of squares certificate and the optimal observables
        self.play(FadeOut(VGroup(n1, n2, n3, cls, box)), l2.animate.scale(0.8).move_to([0, 2.05, 0]).shift(DOWN * 0.1))
        sos = eq(r"2\sqrt{2}\,I - S = \tfrac{1}{\sqrt2}\Big[\big(A_0 - \tfrac{B_0 + B_1}{\sqrt2}\big)^2 + \big(A_1 - \tfrac{B_0 - B_1}{\sqrt2}\big)^2\Big] \ge 0",
                 size=32).move_to([0, 0.85, 0])
        self.play(Write(sos), run_time=2)
        opt = eq(r"A_0 = Z,\ A_1 = X,\ B_{0,1} = \tfrac{Z \pm X}{\sqrt2}", size=34, color=VIOLET).move_to([0, -0.3, 0])
        ang = label("polarizer angles 0, 45, 22.5 and -22.5 degrees", 24, MUTED).next_to(opt, DOWN, buff=0.2)
        self.play(Write(opt), FadeIn(ang))
        yy = eq(r"[Z, X] = 2iY,\ \ [B_0, B_1] = -2iY \ \Rightarrow\ S^2 = 4I - 4\,Y \otimes Y", size=32).move_to([0, -1.75, 0])
        self.play(Write(yy))
        fin = eq(r"Y \otimes Y\,|\Phi^+\rangle = -|\Phi^+\rangle \ \Rightarrow\ S^2|\Phi^+\rangle = 8|\Phi^+\rangle", size=32,
                 color=RED).move_to([0, -2.75, 0])
        self.play(Write(fin))
        self.wait(2)
