"""L6-05 Discovery and informational access: four scenes.

ClassicalBlind   two binary variables: a direct cause A -> B and a common cause L -> A, L -> B produce the
                 same table (0.45, 0.05, 0.05, 0.45); only an intervention on A separates them.
TransposeSign    the passive-observation correlations of Ried et al.: c_s = Tr[(s (x) s) rho] for a common
                 cause, c_s = (1/2) Tr[(s^T (x) s) J] for a direct cause; sigma_y^T = -sigma_y flips one sign.
Tetrahedra       ThreeDScene: the common-cause tetrahedron (Bell states), the direct-cause tetrahedron (Pauli
                 unitaries), their octahedral intersection, and two noisy families crossing out of it at 1/3.
FineTuning       a classical model with an arrow from Alice's setting to Bob's outcome reproduces CHSH 2 sqrt 2,
                 but hides signaling only when the hidden bit is exactly uniform: gap sqrt(2) epsilon.
Every number on screen is computed here; facts() lists strings that also appear in the lesson text.
"""
import itertools
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, RIGHT, UP, Arrow, Circle, Create, DashedLine, Dot, Dot3D, FadeIn, FadeOut,
                   GrowFromEdge, Line, Line3D, Polygon, Rectangle, RoundedRectangle, Scene, ThreeDAxes, ThreeDScene,
                   Transform, TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ---- classical blindness ---------------------------------------------------------------------
FLIP = 0.1
TABLE = {(a, b): 0.5 * ((1 - FLIP) if a == b else FLIP) for a in (0, 1) for b in (0, 1)}
assert TABLE == {(0, 0): 0.45, (0, 1): 0.05, (1, 0): 0.05, (1, 1): 0.45}
DO_DIRECT = 1 - FLIP          # p(b = 0 | do(a = 0)) for the direct-cause model
DO_COMMON = 0.5               # for the common-cause model

# ---- Pauli correlations ---------------------------------------------------------------------
I2 = np.eye(2)
PX = np.array([[0, 1], [1, 0]], dtype=complex)
PY = np.array([[0, -1j], [1j, 0]])
PZ = np.diag([1.0 + 0j, -1.0])
PAULI = (PX, PY, PZ)
assert np.allclose(PY.T, -PY)


def cc_triple(psi):
    rho = np.outer(psi, psi.conj())
    return tuple(int(round(np.real(np.trace(rho @ np.kron(P, P))))) for P in PAULI)


def ce_triple(U):
    return tuple(int(round(0.5 * np.real(np.trace(P @ U @ P @ U.conj().T)))) for P in PAULI)


s2 = 1 / math.sqrt(2)
BELL = {r"\Phi^+": np.array([s2, 0, 0, s2]), r"\Phi^-": np.array([s2, 0, 0, -s2]),
        r"\Psi^+": np.array([0, s2, s2, 0]), r"\Psi^-": np.array([0, s2, -s2, 0])}
UNIT = {"I": I2, "X": PX, "Y": PY, "Z": PZ}
V_CC = {k: cc_triple(v) for k, v in BELL.items()}
V_CE = {k: ce_triple(v) for k, v in UNIT.items()}
assert V_CC[r"\Phi^+"] == (1, -1, 1) and V_CE["I"] == (1, 1, 1)
assert all(a * b * c == -1 for a, b, c in V_CC.values()) and all(a * b * c == 1 for a, b, c in V_CE.values())

# ---- fine-tuning ---------------------------------------------------------------------------
F = math.sin(math.pi / 8) ** 2                 # Bob's flip probability; 1 - 2F = 1/sqrt 2


def ft_model(eps):
    """lambda ~ Bernoulli(1/2 + eps) gives a = lambda, b = lambda xor xy xor nu, nu ~ Bernoulli(F)."""
    p = {}
    for x, y, a, b in itertools.product((0, 1), repeat=4):
        tot = 0.0
        for lam, nu in itertools.product((0, 1), repeat=2):
            pl = 0.5 + eps if lam == 0 else 0.5 - eps
            pn = 1 - F if nu == 0 else F
            if a == lam and b == lam ^ (x & y) ^ nu:
                tot += pl * pn
        p[x, y, a, b] = tot
    E = {(x, y): sum((-1) ** (a ^ b) * p[x, y, a, b] for a in (0, 1) for b in (0, 1)) for x in (0, 1) for y in (0, 1)}
    S = E[0, 0] + E[0, 1] + E[1, 0] - E[1, 1]
    pb = {(x, y): sum(p[x, y, a, 0] for a in (0, 1)) for x in (0, 1) for y in (0, 1)}
    return S, pb


for _e in (0.0, 0.1, 0.2):
    _S, _pb = ft_model(_e)
    assert abs(_S - 2 * math.sqrt(2)) < 1e-12
    assert abs((_pb[0, 1] - _pb[1, 1]) - math.sqrt(2) * _e) < 1e-12


def facts(L):
    """Strings shown on screen that also appear in the lesson text."""
    return ["0.45", "0.05", "\\sigma_y^{T} = -\\sigma_y", "(1, -1, 1)", "(1, 1, 1)", "c_x c_y c_z",
            "|c_x| + |c_y| + |c_z| \\le 1", "\\sqrt{2}\\,\\varepsilon"]


def node(txt, color, pos, r=0.42, size=30):
    c = Circle(radius=r, color=color, stroke_width=4).move_to(pos)
    return VGroup(c, eq(txt, size=size, color=color).move_to(c))


class ClassicalBlind(Scene):
    def construct(self):
        title = label("Two stories, one table", 36, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        # direct cause
        a1 = node("A", BLUE, LEFT * 5.2 + UP * 1.2)
        b1 = node("B", CYAN, LEFT * 3.2 + UP * 1.2)
        e1 = Arrow(a1[0].get_right(), b1[0].get_left(), buff=0.05, color=INK, stroke_width=5)
        t1 = label("direct cause", 26, INK).next_to(VGroup(a1, b1), UP, buff=0.3)
        r1 = VGroup(label("A a fair coin;", 24, MUTED), label("B copies A, flipped w.p. 0.1", 24, MUTED)
                    ).arrange(DOWN, buff=0.06).next_to(VGroup(a1, b1), DOWN, buff=0.3)
        # common cause
        l2 = node(r"\Lambda", AMBER, RIGHT * 3.4 + UP * 2.0)
        a2 = node("A", BLUE, RIGHT * 2.4 + UP * 0.6)
        b2 = node("B", CYAN, RIGHT * 4.4 + UP * 0.6)
        e2 = VGroup(Arrow(l2[0].get_bottom(), a2[0].get_top(), buff=0.05, color=INK, stroke_width=5),
                    Arrow(l2[0].get_bottom(), b2[0].get_top(), buff=0.05, color=INK, stroke_width=5))
        t2 = label("common cause", 26, INK).next_to(l2, LEFT, buff=0.4)
        r2 = VGroup(label("Λ a fair coin; A = Λ;", 24, MUTED), label("B = Λ, flipped w.p. 0.1", 24, MUTED)
                    ).arrange(DOWN, buff=0.06).next_to(VGroup(a2, b2), DOWN, buff=0.3)
        self.play(FadeIn(VGroup(a1, b1, t1)), Create(e1))
        self.play(FadeIn(r1))
        self.play(FadeIn(VGroup(l2, a2, b2, t2)), Create(e2))
        self.play(FadeIn(r2))

        # the shared table
        cells = VGroup()
        origin = DOWN * 2.3
        for (a, b), v in TABLE.items():
            sq = Rectangle(width=1.5, height=0.65, color=MUTED, stroke_width=2).move_to(origin + RIGHT * (b - 0.5) * 1.5 + DOWN * (a - 0.5) * 0.65)
            cells.add(VGroup(sq, label(f"{v:.2f}", 26, VIOLET).move_to(sq)))
        hdr = VGroup(eq("b=0", size=26).next_to(cells[0], UP, buff=0.08), eq("b=1", size=26).next_to(cells[1], UP, buff=0.08),
                     eq("a=0", size=26).next_to(cells[0], LEFT, buff=0.1), eq("a=1", size=26).next_to(cells[2], LEFT, buff=0.1))
        tl = label("p(a, b): identical for both", 24, VIOLET).next_to(cells, RIGHT, buff=0.4)
        self.play(FadeIn(cells), FadeIn(hdr), FadeIn(tl))
        self.wait(1.2)

        # intervention separates them
        self.play(FadeOut(VGroup(cells, hdr, tl)))
        dl = eq(r"\text{apply } do(a = 0) \text{ in both stories}", size=32, color=RED).move_to(DOWN * 2.2)
        d1 = eq(rf"p(b=0 \mid do(a=0)) = {DO_DIRECT:.1f}", size=32, color=RED).next_to(VGroup(a1, b1), DOWN, buff=1.5)
        d2 = eq(rf"p(b=0 \mid do(a=0)) = {DO_COMMON:.1f}", size=32, color=RED).next_to(VGroup(a2, b2), DOWN, buff=1.5)
        cut = Line(l2[0].get_bottom() + LEFT * 0.2, a2[0].get_top() + RIGHT * 0.1, color=RED, stroke_width=0)
        self.play(Write(dl))
        self.play(e2[0].animate.set_color(RED).set_opacity(0.25), Write(d1), Write(d2), run_time=1.5)
        msg = label("observation alone never separates them; intervention does", 26, INK).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(msg))
        self.wait(2)
        _ = (cut, DashedLine)


class TransposeSign(Scene):
    def construct(self):
        title = label("Passive observation: one sign tells the structures apart", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        setup = VGroup(label("A's input maximally mixed; A measures Pauli s; the collapsed state moves on;", 24, MUTED),
                       label("B measures the same Pauli s; record agreement minus disagreement", 24, MUTED)
                       ).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(setup))
        cc = eq(r"\text{common cause: }", r"c_s", "=", r"\operatorname{Tr}[(\sigma_s\otimes\sigma_s)\,\rho_{AB}]", size=36,
                color=BLUE).move_to(UP * 0.9)
        dc1 = eq(r"\text{direct cause: }", r"c_s", "=", r"\tfrac12\operatorname{Tr}[\sigma_s\,\mathcal E(\sigma_s)]", size=36,
                 color=RED).move_to(DOWN * 0.1)
        dc2 = eq(r"\text{direct cause: }", r"c_s", "=", r"\tfrac12\operatorname{Tr}[(\sigma_s^{T}\otimes\sigma_s)\,J_{\mathcal E}]",
                 size=36, color=RED).move_to(dc1)
        self.play(Write(cc))
        self.play(Write(dc1))
        self.play(TransformMatchingTex(dc1, dc2), run_time=1.5)
        key = eq(r"\sigma_x^{T} = \sigma_x,\quad \sigma_y^{T} = -\sigma_y,\quad \sigma_z^{T} = \sigma_z", size=36,
                 color=VIOLET).move_to(DOWN * 1.1)
        self.play(Write(key))
        self.wait(0.8)
        ex1 = eq(r"|\Phi^+\rangle:\ (c_x, c_y, c_z) = (1, -1, 1)", size=34, color=BLUE).move_to(DOWN * 2.1 + LEFT * 3.4)
        ex2 = eq(r"\text{identity channel: } (1, 1, 1)", size=34, color=RED).move_to(DOWN * 2.1 + RIGHT * 3.4)
        self.play(Write(ex1), Write(ex2))
        prod = eq(r"c_x c_y c_z = -1 \ \text{ versus } \ c_x c_y c_z = +1", size=34).move_to(DOWN * 3.05)
        self.play(Write(prod))
        self.wait(2)


class Tetrahedra(ThreeDScene):
    def construct(self):
        R = 1.2
        self.set_camera_orientation(phi=70 * DEGREES, theta=-40 * DEGREES)
        axes = ThreeDAxes(x_range=[-1.3, 1.3, 1], y_range=[-1.3, 1.3, 1], z_range=[-1.3, 1.3, 1],
                          x_length=2.6 * R, y_length=2.6 * R, z_length=2.6 * R, axis_config={"color": GRID})
        c = lambda v: axes.c2p(*v)  # noqa: E731
        labs = [eq(t, size=32, color=MUTED).move_to(c(p)) for t, p in (("c_x", (1.5, 0, 0)), ("c_y", (0, 1.5, 0)), ("c_z", (0, 0, 1.5)))]
        for m in labs:
            self.add_fixed_orientation_mobjects(m)
        title = label("Two tetrahedra of Pauli correlations", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Create(axes), Write(title), run_time=1.2)

        def tetra(verts, color, op):
            vs = list(verts)
            return VGroup(*[Polygon(*[c(vs[i]) for i in f], color=color, stroke_width=2, fill_color=color, fill_opacity=op)
                            for f in itertools.combinations(range(4), 3)])
        tcc = tetra(V_CC.values(), BLUE, 0.12)
        tce = tetra(V_CE.values(), RED, 0.12)
        cc_l = [eq(f"{k}", size=28, color=BLUE).move_to(c(np.array(v) * 1.22)) for k, v in V_CC.items()]
        ce_l = [eq(k, size=28, color=RED).move_to(c(np.array(v) * 1.22)) for k, v in V_CE.items()]
        for m in cc_l + ce_l:
            self.add_fixed_orientation_mobjects(m)
        k1 = label("blue: common cause (Bell states)", 24, BLUE).to_corner(UP + LEFT, buff=0.35).shift(DOWN * 0.6)
        self.add_fixed_in_frame_mobjects(k1)
        self.play(Create(tcc), FadeIn(VGroup(*cc_l)), FadeIn(k1), run_time=2)
        k2 = label("red: direct cause (Pauli unitaries)", 24, RED).next_to(k1, DOWN, aligned_edge=LEFT, buff=0.12)
        self.add_fixed_in_frame_mobjects(k2)
        self.play(Create(tce), FadeIn(VGroup(*ce_l)), FadeIn(k2), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.09)
        self.wait(2)

        # octahedron edges
        octv = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        edges = VGroup(*[Line(c(p), c(q), color=VIOLET, stroke_width=3) for p, q in itertools.combinations(octv, 2)
                         if np.dot(p, q) == 0])
        k3 = VGroup(label("violet: the overlap", 24, VIOLET), eq(r"|c_x| + |c_y| + |c_z| \le 1", size=30, color=VIOLET)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        k3.next_to(k2, DOWN, aligned_edge=LEFT, buff=0.15)
        self.add_fixed_in_frame_mobjects(k3)
        self.play(Create(edges), FadeIn(k3), run_time=2)
        self.wait(1)

        # two noisy families
        v = ValueTracker(0.0)
        pcc = always_redraw(lambda: Dot3D(c((-v.get_value(),) * 3), radius=0.09,
                                          color=BLUE if 3 * v.get_value() > 1 + 1e-9 else VIOLET, resolution=(8, 8)))
        pce = always_redraw(lambda: Dot3D(c((v.get_value(),) * 3), radius=0.09,
                                          color=RED if 3 * v.get_value() > 1 + 1e-9 else VIOLET, resolution=(8, 8)))
        vt = always_redraw(lambda: eq(rf"v = {v.get_value():.2f}", size=34, color=AMBER).to_corner(DOWN + RIGHT, buff=0.5))
        self.add_fixed_in_frame_mobjects(vt)
        fam = VGroup(eq(r"v|\Psi^-\rangle\langle\Psi^-| + (1-v)I/4:\ (-v, -v, -v)", size=28, color=BLUE),
                     eq(r"\text{identity mixed with } \rho\mapsto I/2:\ (v, v, v)", size=28, color=RED)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(DOWN + LEFT, buff=0.4)
        self.add_fixed_in_frame_mobjects(fam)
        self.play(FadeIn(fam))
        self.add(pcc, pce)
        self.play(v.animate.set_value(1 / 3), run_time=3, rate_func=linear)
        nb = label("v = 1/3: both leave the octahedron here", 24, VIOLET).next_to(fam, UP, aligned_edge=LEFT, buff=0.2)
        self.add_fixed_in_frame_mobjects(nb)
        self.play(FadeIn(nb))
        self.wait(0.6)
        self.play(FadeOut(nb))
        self.play(v.animate.set_value(1.0), run_time=3, rate_func=linear)
        nv = label("beyond 1/3 each point fits only its own structure", 24, INK).next_to(fam, UP, aligned_edge=LEFT, buff=0.2)
        self.add_fixed_in_frame_mobjects(nv)
        self.play(FadeIn(nv))
        self.wait(2.5)
        self.stop_ambient_camera_rotation()
        _ = (Line3D, Transform)


class FineTuning(Scene):
    def construct(self):
        title = label("A classical story for Bell correlations needs fine-tuning", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        X = node("x", MUTED, LEFT * 5.6 + UP * 1.6, r=0.36, size=28)
        A = node("a", BLUE, LEFT * 5.6 + DOWN * 0.4, r=0.36, size=28)
        Lm = node(r"\lambda", AMBER, LEFT * 4.0 + DOWN * 1.5, r=0.36, size=28)
        B = node("b", CYAN, LEFT * 2.4 + DOWN * 0.4, r=0.36, size=28)
        Y = node("y", MUTED, LEFT * 2.4 + UP * 1.6, r=0.36, size=28)
        arr = VGroup(Arrow(X[0].get_bottom(), A[0].get_top(), buff=0.05, color=INK, stroke_width=4),
                     Arrow(Y[0].get_bottom(), B[0].get_top(), buff=0.05, color=INK, stroke_width=4),
                     Arrow(Lm[0].get_left(), A[0].get_bottom() + RIGHT * 0.1, buff=0.05, color=INK, stroke_width=4),
                     Arrow(Lm[0].get_right(), B[0].get_bottom() + LEFT * 0.1, buff=0.05, color=INK, stroke_width=4))
        sup = Arrow(X[0].get_right() + DOWN * 0.1, B[0].get_left() + UP * 0.1, buff=0.05, color=RED, stroke_width=5)
        self.play(FadeIn(VGroup(X, A, Lm, B, Y)), Create(arr))
        self.play(Create(sup))
        sl = label("x influences b", 24, RED).move_to(sup.get_center() + DOWN * 0.45 + LEFT * 0.45)
        self.play(FadeIn(sl))
        model = VGroup(eq(r"a = \lambda,\quad b = \lambda \oplus xy \oplus \nu", size=30),
                       eq(r"\nu \sim \text{Bernoulli}(\sin^2\tfrac{\pi}{8})", size=30),
                       eq(r"P(\lambda = 0) = \tfrac12 + \varepsilon", size=30, color=AMBER)
                       ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(LEFT * 4.0 + DOWN * 2.95)
        self.play(Write(model), run_time=2)

        # right: CHSH and the signaling gap
        eps = ValueTracker(0.0)
        S0, _ = ft_model(0.0)
        chsh = eq(rf"S = 2\sqrt{{2}} \approx {S0:.3f}\ \text{{for every }} \varepsilon", size=30, color=VIOLET).move_to(RIGHT * 3.2 + UP * 2.3)
        self.play(Write(chsh))
        base = RIGHT * 1.6 + DOWN * 2.6
        scale = 3.2
        axis = Line(base, base + RIGHT * 3.6, color=MUTED)
        half = DashedLine(base + UP * 0.5 * scale, base + UP * 0.5 * scale + RIGHT * 3.6, color=MUTED)

        def bar(i, col):
            def make():
                _, pb = ft_model(eps.get_value())
                v = pb[i, 1]
                return Rectangle(width=1.0, height=v * scale, color=col, fill_color=col, fill_opacity=0.6).move_to(
                    base + RIGHT * (0.9 + 1.8 * i) + UP * v * scale / 2)
            return always_redraw(make)
        b0, b1 = bar(0, BLUE), bar(1, AMBER)
        n0 = eq(r"p(b=0 \mid x=0, y=1)", size=28, color=BLUE).next_to(base + RIGHT * 0.9, DOWN, buff=0.15)
        n1 = eq(r"p(b=0 \mid x=1, y=1)", size=28, color=AMBER).next_to(base + RIGHT * 2.7, DOWN, buff=0.15).shift(DOWN * 0.45)
        self.play(Create(axis), Create(half), FadeIn(b0), FadeIn(b1), Write(n0), Write(n1))
        gap = always_redraw(lambda: eq(rf"\text{{gap}} = \sqrt{{2}}\,\varepsilon = {math.sqrt(2) * eps.get_value():.3f}",
                                       size=30, color=RED).move_to(RIGHT * 3.2 + UP * 1.5))
        et = always_redraw(lambda: eq(rf"\varepsilon = {eps.get_value():.2f}", size=30, color=AMBER).move_to(RIGHT * 3.2 + UP * 0.8))
        self.add(gap, et)
        self.play(eps.animate.set_value(0.2), run_time=4, rate_func=linear)
        self.wait(0.5)
        self.play(eps.animate.set_value(0.0), run_time=3, rate_func=linear)
        msg = VGroup(label("no-signaling holds only at exactly ε = 0:", 24, INK),
                     label("the graph does not imply it; the parameters must", 24, INK),
                     label("be tuned to hide the arrow", 24, INK)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        msg.move_to(RIGHT * 3.0 + UP * 1.0)
        self.play(FadeOut(gap), FadeOut(et))
        self.play(FadeIn(msg))
        self.wait(2.5)
        _ = (GrowFromEdge, RoundedRectangle, Dot)
