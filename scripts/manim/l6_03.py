"""L6-03 Quantum DAGs and Markov assumptions: three scenes.

QuantumDAGFactorization  the five-node DAG of Barrett, Lorenz and Oreshkov (Fig. 5): each node gets an input and
                         an output space, the process operator is built factor by factor, and the factors that
                         share the parent A1 must commute.
ChainLinkProduct         chain A -> B -> C: with no intervention at B the marginal process is the composed
                         channel (link product); an intervention at B enters through its transposed Choi operator.
HiddenInfluence          a present wire with no visible dependence: P(+|phi) = (1 + (1 - p) cos phi)/2 flattens as
                         dephasing grows; then the CNOT one-time pad (no signaling without the coin, full
                         dependence with it).
All numbers on screen are computed and asserted here.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, PI, RIGHT, UP, Arrow, Axes, Circle, Create, DashedLine, DecimalNumber, FadeIn, FadeOut,
                   Line, Rectangle, RoundedRectangle, Scene, SurroundingRectangle, TransformMatchingTex, ValueTracker,
                   VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label
from qcai import science as s

# ---------------------------------------------------------------- checks behind the on-screen statements
EDGES = [("A1", "A2"), ("A1", "A3"), ("A2", "A4"), ("A3", "A4"), ("A1", "A5"), ("A4", "A5")]
PARENTS = {n: [a for a, b in EDGES if b == n] for n in ("A1", "A2", "A3", "A4", "A5")}
assert PARENTS == {"A1": [], "A2": ["A1"], "A3": ["A1"], "A4": ["A2", "A3"], "A5": ["A1", "A4"]}


def p_plus(phi, p):
    """P(+) for an X measurement of (|0> + e^{i phi}|1>)/sqrt 2 after dephasing D_p (course convention)."""
    return (1 + (1 - p) * math.cos(phi)) / 2


for _p in (0.0, 0.5, 1.0):
    for _ph in (0.0, 1.3, PI):
        _psi = np.array([1, np.exp(1j * _ph)]) / math.sqrt(2)
        _out = s.apply_kraus(s.dm(_psi), s.dephasing_kraus(_p))
        assert abs(np.real(np.array([1, 1]) @ _out @ np.array([1, 1])) / 2 - p_plus(_ph, _p)) < 1e-12


def choi_of(E, d=2):
    J = 0
    for i in range(d):
        for j in range(d):
            Eij = np.zeros((d, d), complex)
            Eij[i, j] = 1
            J = J + np.kron(Eij, E(Eij))
    return J


_CN = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])


def _pad(lam):
    def f(X):
        out = _CN @ np.kron(X, lam) @ _CN.T
        return np.einsum("aiaj->ij", out.reshape(2, 2, 2, 2))
    return f


assert np.allclose(choi_of(_pad(np.eye(2) / 2)), np.kron(np.eye(2), np.eye(2) / 2))      # coin unknown: replacement by I/2
assert np.allclose(choi_of(_pad(s.dm(s.KET0))).real, np.diag([1, 0, 0, 1]))            # coin known: Z value copied


def facts(L):
    """Strings shown on screen that also appear in the lesson text."""
    return ["\\rho_{A_5|A_1A_4}", "\\rho_{A_4|A_2A_3}", "\\tau^{\\mathrm{id}}_B", "(1 + (1-p)\\cos\\varphi)/2",
            "I \\otimes I/2"]


def node(txt, pos, color=BLUE, r=0.4, size=34):
    c = Circle(radius=r, color=color, stroke_width=4).set_fill(color, opacity=0.12)
    return VGroup(c, eq(txt, size=size, color=color)).move_to(pos)


def edge(a, b, color=INK):
    return Arrow(a.get_center(), b.get_center(), buff=0.45, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.15)


class QuantumDAGFactorization(Scene):
    def construct(self):
        title = label("A quantum causal model: one channel per node", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        pos = {"A1": LEFT * 5.6 + DOWN * 0.4, "A2": LEFT * 4.2 + UP * 1.05, "A3": LEFT * 4.2 + DOWN * 1.85,
               "A4": LEFT * 2.8 + DOWN * 0.4, "A5": LEFT * 1.4 + UP * 1.6}
        N = {k: node(k[0] + "_" + k[1], v) for k, v in pos.items()}
        E = {e: edge(N[e[0]], N[e[1]]) for e in EDGES}
        self.play(*[FadeIn(n, scale=0.7) for n in N.values()], run_time=1.0)
        self.play(*[Create(a) for a in E.values()], run_time=1.2)

        # one node as a pair of spaces
        zoom = VGroup(Rectangle(width=1.6, height=0.55, color=VIOLET).set_fill(VIOLET, 0.08),
                      Rectangle(width=1.6, height=0.55, color=CYAN).set_fill(CYAN, 0.08)).arrange(DOWN, buff=0)
        zoom.move_to(LEFT * 3.6 + DOWN * 3.0)
        zl = VGroup(eq(r"A^{\mathrm{out}}", size=30, color=VIOLET).move_to(zoom[0]), eq(r"A^{\mathrm{in}}", size=30, color=CYAN).move_to(zoom[1]))
        zt = VGroup(label("node = place to intervene:", 24, MUTED), label("input from parents, output to children", 24, MUTED))
        zt.arrange(DOWN, aligned_edge=LEFT, buff=0.05).next_to(zoom, RIGHT, buff=0.25)
        self.play(FadeIn(zoom), FadeIn(zl), FadeIn(zt))
        self.wait(0.6)

        parts = [r"\sigma_{A_1\cdots A_5} =", r"\rho_{A_5|A_1A_4}", r"\,\rho_{A_4|A_2A_3}", r"\,\rho_{A_2|A_1}", r"\,\rho_{A_3|A_1}", r"\,\rho_{A_1}"]
        F = eq(*parts, size=32).move_to(RIGHT * 3.3 + UP * 1.9)
        self.play(Write(F[0]))
        order = ["A5", "A4", "A2", "A3", "A1"]
        for k, n in enumerate(order):
            hl = [SurroundingRectangle(N[n], color=AMBER, buff=0.06)] + [E[(p, n)].copy().set_color(AMBER) for p in PARENTS[n]]
            self.play(*[Create(h) for h in hl], Write(F[k + 1]), run_time=0.9)
            self.play(*[FadeOut(h) for h in hl], run_time=0.3)
        cls = eq(r"P = P(x_5|x_1x_4)\,P(x_4|x_2x_3)\,P(x_2|x_1)\,P(x_3|x_1)\,P(x_1)", size=30, color=MUTED).next_to(F, DOWN, buff=0.3)
        cls.scale_to_fit_width(min(cls.width, F.width))
        clt = label("same shape as the classical Markov factorization", 24, MUTED).next_to(cls, DOWN, buff=0.1)
        self.play(FadeIn(cls), FadeIn(clt))
        self.wait(0.8)

        # factors sharing the parent A1 must commute
        shared = VGroup(F[1], F[3], F[4])
        boxes = VGroup(*[SurroundingRectangle(m, color=RED, buff=0.05) for m in shared])
        ring = Circle(radius=0.55, color=RED, stroke_width=5).move_to(N["A1"])
        self.play(Create(boxes), Create(ring))
        com = eq(r"[\rho_{A_i|\mathrm{Pa}(A_i)},\, \rho_{A_j|\mathrm{Pa}(A_j)}] = 0", size=34, color=RED).move_to(RIGHT * 3.3 + DOWN * 0.75)
        ct = VGroup(label("three factors act on the output of A1,", 24, MUTED),
                    label("so they must commute: A1's output splits,", 24, MUTED),
                    label("block by block, into one piece per child", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        ct.next_to(com, DOWN, buff=0.2)
        self.play(Write(com), FadeIn(ct))
        self.wait(2.0)


class ChainLinkProduct(Scene):
    def construct(self):
        title = label("A chain, with and without an intervention at B", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))

        def nodebox(name, x, color):
            r = VGroup(Rectangle(width=0.7, height=0.9, color=color).set_fill(color, 0.08),
                       Rectangle(width=0.7, height=0.9, color=color).set_fill(color, 0.08)).arrange(RIGHT, buff=0)
            r.move_to([x, 1.6, 0])
            t = VGroup(label("in", 24, color).move_to(r[0]), label("out", 24, color).move_to(r[1]))
            n = eq(name, size=36, color=color).next_to(r, UP, buff=0.12)
            return VGroup(r, t, n)

        A = nodebox("A", -5.2, CYAN)
        B = nodebox("B", -0.6, VIOLET)
        C = nodebox("C", 4.0, CYAN)

        def chan(txt, x, color=BLUE):
            b = RoundedRectangle(width=1.0, height=0.7, corner_radius=0.1, color=color).set_fill(color, 0.1).move_to([x, 1.6, 0])
            return VGroup(b, eq(txt, size=34, color=color).move_to(b))

        cE = chan(r"\mathcal{E}", -2.9)
        cF = chan(r"\mathcal{F}", 1.7)
        wires = VGroup(Line(A[0].get_right(), cE.get_left(), color=INK), Line(cE.get_right(), B[0].get_left(), color=INK),
                       Line(B[0].get_right(), cF.get_left(), color=INK), Line(cF.get_right(), C[0].get_left(), color=INK))
        self.play(FadeIn(A), FadeIn(B), FadeIn(C), FadeIn(cE), FadeIn(cF), Create(wires), run_time=1.4)
        s0 = eq(r"\sigma_{ABC} = \rho_{C|B}\,\rho_{B|A}\,\rho_A", size=38).move_to(UP * 0.1)
        self.play(Write(s0))
        self.wait(0.6)

        # no intervention at B: plug the identity
        plug = Line(B[0][0].get_center() + LEFT * 0.35, B[0][1].get_center() + RIGHT * 0.35, color=VIOLET, stroke_width=8)
        pl = label("no intervention: the identity channel", 24, VIOLET).next_to(B, DOWN, buff=0.25)
        self.play(Create(plug), FadeIn(pl))
        d1 = eq(r"\sigma_{AC} =", r"\operatorname{Tr}_B\big[\sigma_{ABC}\, \tau^{\mathrm{id}}_B\big]", size=38).move_to(DOWN * 0.9)
        d2 = eq(r"\sigma_{AC} =", r"\rho_{C|A}\,\rho_A,\quad \mathcal{E}_{C|A} = \mathcal{F} \circ \mathcal{E}", size=38).move_to(DOWN * 0.9)
        self.play(Write(d1))
        self.wait(0.5)
        self.play(TransformMatchingTex(d1, d2), run_time=1.4)
        lk = eq(r"J_{\mathcal{F}\circ\mathcal{E}} = \operatorname{Tr}_B\big[(J_{\mathcal{E}}^{T_B} \otimes I)(I \otimes J_{\mathcal{F}})\big]", size=34, color=BLUE)
        lk.move_to(DOWN * 1.95)
        lkt = label("course convention: the link product of L6-02", 24, MUTED).next_to(lk, DOWN, buff=0.12)
        self.play(Write(lk), FadeIn(lkt))
        self.wait(1.2)

        # intervene at B instead: a measurement with outcome k
        self.play(FadeOut(VGroup(plug, pl, d2, lk, lkt)))
        mbox = RoundedRectangle(width=1.3, height=0.75, corner_radius=0.1, color=AMBER).set_fill(AMBER, 0.15).move_to(B[0])
        mt = eq(r"\mathcal{M}_k", size=34, color=AMBER).move_to(mbox)
        ml = label("intervention at B with outcome k", 24, AMBER).next_to(B, DOWN, buff=0.25)
        self.play(FadeOut(B[1]), FadeIn(mbox), Write(mt), FadeIn(ml))
        pk = eq(r"P(k) = \operatorname{Tr}\big[\sigma_{ABC}\,(\tau_A \otimes \tau^{k}_B \otimes \tau_C)\big]", size=36).move_to(DOWN * 1.0)
        tk = eq(r"\tau^{k}_B = (J_{\mathcal{M}_k})^{T}", size=36, color=AMBER).move_to(DOWN * 2.0)
        tkt = label("interventions enter through transposed Choi operators", 24, MUTED).next_to(tk, DOWN, buff=0.12)
        self.play(Write(pk))
        self.play(Write(tk), FadeIn(tkt))
        self.wait(2.0)


class HiddenInfluence(Scene):
    def construct(self):
        title = label("A present arrow can leave no trace in the data", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        setup = eq(r"|\varphi\rangle \;\to\; \mathcal{D}_p \;\to\; \text{measure } X", size=36).move_to(LEFT * 3.4 + UP * 2.2)
        self.play(Write(setup))
        ax = Axes(x_range=[0, 2 * PI, PI / 2], y_range=[0, 1, 0.5], x_length=5.8, y_length=3.2,
                  axis_config={"color": MUTED, "include_tip": False},
                  y_axis_config={"numbers_to_include": [0, 0.5, 1], "font_size": 26,
                                 "decimal_number_config": {"color": INK, "num_decimal_places": 1}})
        ax.move_to(LEFT * 3.2 + DOWN * 0.6)
        xl = eq(r"\varphi", size=30).next_to(ax.x_axis, RIGHT, buff=0.15)
        yl = eq(r"P(+\,|\,\varphi)", size=30).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        xt = VGroup(*[eq(t, size=26).next_to(ax.c2p(v, 0), DOWN, buff=0.12) for t, v in (("0", 0), (r"\pi", PI), (r"2\pi", 2 * PI))])
        self.play(Create(ax), Write(xl), Write(yl), FadeIn(xt))
        p = ValueTracker(0.0)
        curve = always_redraw(lambda: ax.plot(lambda t: p_plus(t, p.get_value()), x_range=[0, 2 * PI], color=RED, stroke_width=5))
        self.add(curve)
        fm = eq(r"P(+\,|\,\varphi) = (1 + (1-p)\cos\varphi)/2", size=34, color=RED).move_to(RIGHT * 3.4 + UP * 1.2)
        self.play(Write(fm))
        ro = VGroup(eq("p =", size=36), DecimalNumber(0, num_decimal_places=2, font_size=36, color=INK)).arrange(RIGHT, buff=0.15)
        ro.move_to(RIGHT * 3.4 + UP * 0.2)
        ro[1].add_updater(lambda m: m.set_value(p.get_value()))
        self.add(ro)
        self.play(p.animate.set_value(1.0), run_time=5, rate_func=linear)
        n1 = VGroup(label("p = 1: no dependence on phi,", 26, RED),
                    label("but the wire from the preparation", 24, MUTED),
                    label("to the measurement is still there", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        n1.move_to(RIGHT * 3.4 + DOWN * 1.0)
        self.play(FadeIn(n1))
        self.wait(1.2)

        self.remove(curve, ro)
        self.play(FadeOut(VGroup(setup, ax, xl, yl, xt, fm, n1)))
        # the CNOT one-time pad
        ctrl = Line(LEFT * 5.6 + UP * 1.2, LEFT * 1.6 + UP * 1.2, color=INK)
        targ = Line(LEFT * 5.6 + DOWN * 0.2, LEFT * 1.6 + DOWN * 0.2, color=INK)
        dot = Circle(radius=0.09, color=INK).set_fill(INK, 1).move_to(LEFT * 3.6 + UP * 1.2)
        plus = VGroup(Circle(radius=0.25, color=INK), Line(UP * 0.25, DOWN * 0.25, color=INK)).move_to(LEFT * 3.6 + DOWN * 0.2)
        vert = Line(dot.get_center(), plus.get_top(), color=INK)
        la = eq("A", size=34, color=CYAN).next_to(ctrl, LEFT, buff=0.15)
        ll = eq(r"\lambda", size=34, color=AMBER).next_to(targ, LEFT, buff=0.15)
        lb = eq("B", size=34, color=VIOLET).next_to(targ, RIGHT, buff=0.15)
        cap = label("CNOT: control A, target a coin lambda", 24, MUTED).move_to(LEFT * 3.6 + DOWN * 1.1)
        self.play(Create(ctrl), Create(targ), FadeIn(dot), Create(plus), Create(vert), Write(la), Write(ll), Write(lb), FadeIn(cap))
        u1 = eq(r"\text{coin unknown: } \rho_{B|A} = I \otimes I/2", size=34, color=MUTED).move_to(RIGHT * 2.9 + UP * 1.3)
        u2 = label("A cannot signal to B", 24, MUTED).next_to(u1, DOWN, buff=0.12)
        self.play(Write(u1), FadeIn(u2))
        k1 = eq(r"\text{coin known: } B \text{ copies the } Z \text{ value of } A", size=34, color=VIOLET).move_to(RIGHT * 2.9 + DOWN * 0.1)
        k2 = label("A signals to B perfectly", 24, VIOLET).next_to(k1, DOWN, buff=0.12)
        self.play(Write(k1), FadeIn(k2))
        fin = VGroup(label("no signaling is not no influence:", 26, RED, "BOLD"),
                     label("an absent dependence does not prove an absent arrow", 26, RED)).arrange(DOWN, buff=0.08)
        fin.move_to(DOWN * 2.6)
        self.play(FadeIn(fin))
        self.wait(2.0)
        _ = (DashedLine, GRID)
