"""L6-08 The quantum switch: four 3Blue1Brown-style scenes.

SwitchRouting       a target follows two routes at once: through A then B (control |0>) and through
                    B then A (control |1>); each box is visited once on each route.
SwitchDerivation    TransformMatchingTex derivation of the output for control |+>:
                    1/2 |+> {U_A,U_B}|psi> + 1/2 |-> [U_B,U_A]|psi>, and P(+) in terms of the group commutator.
CommuteSweep        U_A = X, U_B = cos(beta) X + sin(beta) Z: P(+) = cos^2(beta) traced live, against 1/2 for a
                    classical mixture of orders.
DephasingControl    anticommuting gates: the control's density matrix as its coherence V is lost; P(-) = (1+V)/2.
Convention (as in qcai.science.quantum_switch): control |0> applies U_A first, i.e. U_B U_A.
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, DashedLine, DecimalNumber, Dot, FadeIn,
                   FadeOut, Line, MoveAlongPath, Rectangle, RoundedRectangle, Scene, SurroundingRectangle, TracedPath,
                   TransformMatchingTex, ValueTracker, VGroup, VMobject, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1.0, -1.0]).astype(complex)
KET0, KET1 = np.array([1, 0], dtype=complex), np.array([0, 1], dtype=complex)
PLUS, MINUS = (KET0 + KET1) / math.sqrt(2), (KET0 - KET1) / math.sqrt(2)


def switch_unitary(UA, UB):
    """Control |0>: U_A first (U_B U_A); control |1>: U_B first (U_A U_B)."""
    return np.kron(np.outer(KET0, KET0), UB @ UA) + np.kron(np.outer(KET1, KET1), UA @ UB)


def p_plus(UA, UB, psi):
    out = switch_unitary(UA, UB) @ np.kron(PLUS, psi)
    return float(np.linalg.norm(np.kron(PLUS.conj(), I2) @ out) ** 2)


def UB_of(beta):
    return math.cos(beta) * X + math.sin(beta) * Z


PSI = np.array([0.6, 0.8j])
for b in np.linspace(0, math.pi / 2, 7):
    assert abs(p_plus(X, UB_of(b), PSI) - math.cos(b) ** 2) < 1e-12
assert abs(p_plus(X, X, PSI) - 1) < 1e-12 and abs(p_plus(X, Z, PSI)) < 1e-12
# the derived output equals the direct computation
_out = switch_unitary(X, Z) @ np.kron(PLUS, PSI)
_der = 0.5 * np.kron(PLUS, (X @ Z + Z @ X) @ PSI) + 0.5 * np.kron(MINUS, (Z @ X - X @ Z) @ PSI)
assert np.allclose(_out, _der)


def control_state(V):
    """Control density matrix for U_A = X, U_B = Z when its coherence is multiplied by V."""
    out = switch_unitary(X, Z) @ np.kron(PLUS, PSI)
    rho = np.outer(out, out.conj()).reshape(2, 2, 2, 2)
    rc = np.einsum("ajbj->ab", rho)
    rc = np.array([[rc[0, 0], V * rc[0, 1]], [V * rc[1, 0], rc[1, 1]]])
    return rc


for V in (0, 0.5, 1):
    rc = control_state(V)
    assert abs(rc[0, 1].real + V / 2) < 1e-12
    assert abs(float((MINUS.conj() @ rc @ MINUS).real) - (1 + V) / 2) < 1e-12

FACT_OUT = r"\tfrac12|+\rangle\{U_A,U_B\}|\psi\rangle + \tfrac12|-\rangle[U_B,U_A]|\psi\rangle"
FACT_PK = r"P(+) = \tfrac12\big(1 + \operatorname{Re}\langle\psi|U_A^\dagger U_B^\dagger U_A U_B|\psi\rangle\big)"
FACT_COS = r"P(+) = \cos^2\beta"
FACT_DEPH = r"P(-) = \tfrac{1+V}{2}"


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [FACT_OUT, FACT_PK, FACT_COS, FACT_DEPH]


def gate_box(name, pos, color):
    b = RoundedRectangle(width=1.0, height=0.8, corner_radius=0.1, color=color, fill_color="#ffffff",
                         fill_opacity=1, stroke_width=4).move_to(pos)
    return VGroup(b, eq(name, size=38, color=color).move_to(b))


def smooth_path(points, color, width=5):
    m = VMobject(stroke_color=color, stroke_width=width)
    m.set_points_as_corners([np.array([x, y, 0.0]) for x, y in points])
    return m


class SwitchRouting(Scene):
    def construct(self):
        title = label("One target, two routes, one use of each gate", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.2)
        y0 = 0.3
        PA, PB = (-1.5, y0), (1.5, y0)
        A = gate_box("U_A", [*PA, 0], BLUE)
        B = gate_box("U_B", [*PB, 0], AMBER)
        # cyan: straight through A then B; amber: up through B, over the top, down through A, back under to the exit
        r0 = smooth_path([(-6.2, y0), PA, PB, (6.2, y0)], CYAN)
        r1 = smooth_path([(-6.2, y0), (-4.6, y0), (-3.4, y0 - 1.9), (1.5, y0 - 1.9), PB, (1.5, y0 + 1.6), (-1.5, y0 + 1.6),
                          PA, (-1.5, y0 - 1.1), (3.4, y0 - 1.1), (4.6, y0), (6.2, y0)], AMBER)
        r1.shift(DOWN * 0.0)
        r0.set_stroke(opacity=0.8)
        r1.set_stroke(opacity=0.8)
        self.play(Create(r0), Create(r1), run_time=2.0)
        self.play(FadeIn(A), FadeIn(B))
        l0 = eq(r"|0\rangle_c:\ U_A \text{ then } U_B", size=32, color=CYAN).move_to(LEFT * 4.3 + DOWN * 2.3)
        l1 = eq(r"|1\rangle_c:\ U_B \text{ then } U_A", size=32, color=AMBER).move_to(RIGHT * 4.0 + DOWN * 2.3)
        self.play(Write(l0), Write(l1))
        ctrl = eq(r"\text{control } |+\rangle_c = \tfrac{1}{\sqrt2}(|0\rangle_c + |1\rangle_c)", size=34, color=VIOLET)
        ctrl.move_to(DOWN * 3.15)
        self.play(Write(ctrl))
        for _ in range(2):
            d0 = Dot(color=CYAN, radius=0.11).set_opacity(0.75)
            d1 = Dot(color=AMBER, radius=0.11).set_opacity(0.75)
            self.play(MoveAlongPath(d0, r0), MoveAlongPath(d1, r1), run_time=4.0, rate_func=linear)
            self.remove(d0, d1)
        self.play(FadeOut(VGroup(l0, l1)))
        res = eq(r"\tfrac{1}{\sqrt2}\big(|0\rangle_c\,U_BU_A|\psi\rangle + |1\rangle_c\,U_AU_B|\psi\rangle\big)", size=36, color=INK)
        res.move_to(DOWN * 2.3)
        self.play(Write(res), run_time=1.6)
        note = label("each box is entered exactly once on each route", 26, MUTED).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(note))
        self.wait(2.0)


class SwitchDerivation(Scene):
    def construct(self):
        title = label("What the control learns", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        s = 42
        L1 = eq(r"\tfrac{1}{\sqrt2}", r"|0\rangle", r"U_BU_A|\psi\rangle", "+", r"\tfrac{1}{\sqrt2}", r"|1\rangle",
                r"U_AU_B|\psi\rangle", size=s)
        L2 = eq(r"\tfrac12", r"(|+\rangle + |-\rangle)", r"U_BU_A|\psi\rangle", "+", r"\tfrac12", r"(|+\rangle - |-\rangle)",
                r"U_AU_B|\psi\rangle", size=s)
        L3 = eq(r"\tfrac12", r"|+\rangle", r"(U_BU_A + U_AU_B)|\psi\rangle", "+", r"\tfrac12", r"|-\rangle",
                r"(U_BU_A - U_AU_B)|\psi\rangle", size=s)
        L4 = eq(r"\tfrac12", r"|+\rangle", r"\{U_A,U_B\}|\psi\rangle", "+", r"\tfrac12", r"|-\rangle",
                r"[U_B,U_A]|\psi\rangle", size=s)
        for L in (L1, L2, L3, L4):
            L.move_to(UP * 1.6)
        sub = eq(r"|0\rangle = \tfrac{1}{\sqrt2}(|+\rangle + |-\rangle),\quad |1\rangle = \tfrac{1}{\sqrt2}(|+\rangle - |-\rangle)",
                 size=30, color=MUTED).move_to(UP * 2.55)
        self.play(Write(L1), run_time=1.6)
        self.wait(0.6)
        self.play(FadeIn(sub))
        self.play(TransformMatchingTex(L1, L2), run_time=1.8)
        self.wait(0.6)
        self.play(TransformMatchingTex(L2, L3), run_time=1.8)
        self.wait(0.6)
        self.play(TransformMatchingTex(L3, L4), FadeOut(sub), run_time=1.8)
        fo = eq(FACT_OUT, size=34, color=VIOLET).move_to(UP * 1.6)
        self.play(FadeOut(L4), FadeIn(fo), run_time=0.6)
        box = SurroundingRectangle(fo, color=VIOLET, buff=0.15)
        self.play(Create(box))
        pk = eq(FACT_PK, size=34).move_to(UP * 0.3)
        self.play(Write(pk), run_time=1.6)
        self.wait(0.6)
        c1 = VGroup(eq(r"U_AU_B = U_BU_A", size=34, color=CYAN), eq(r"P(+) = 1", size=38, color=CYAN),
                    eq(r"\text{control ends in } |+\rangle", size=32, color=CYAN)).arrange(DOWN, buff=0.2).move_to(LEFT * 3.3 + DOWN * 1.9)
        c2 = VGroup(eq(r"U_AU_B = -U_BU_A", size=34, color=RED), eq(r"P(-) = 1", size=38, color=RED),
                    eq(r"\text{control ends in } |-\rangle", size=32, color=RED)).arrange(DOWN, buff=0.2).move_to(RIGHT * 3.3 + DOWN * 1.9)
        self.play(FadeIn(c1, shift=UP * 0.2))
        self.play(FadeIn(c2, shift=UP * 0.2))
        tag = label("one measurement of the control decides with certainty", 26, MUTED).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(tag))
        self.wait(2.2)


class CommuteSweep(Scene):
    def construct(self):
        title = label("From commuting to anticommuting", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        c = Circle(radius=1.7, color=GRID, stroke_width=3).move_to(LEFT * 4.0 + DOWN * 0.4)
        o = c.get_center()
        xl = eq("x", size=30, color=MUTED).next_to(c, RIGHT, buff=0.1)
        zl = eq("z", size=30, color=MUTED).next_to(c, UP, buff=0.1)
        axes_lines = VGroup(DashedLine(o + LEFT * 1.9, o + RIGHT * 1.9, color=MUTED, stroke_width=2),
                            DashedLine(o + DOWN * 1.9, o + UP * 1.9, color=MUTED, stroke_width=2))
        self.play(Create(c), Create(axes_lines), Write(xl), Write(zl))
        beta = ValueTracker(0.0)
        a_arrow = Arrow(o, o + RIGHT * 1.7, buff=0, color=BLUE, stroke_width=7)
        b_arrow = always_redraw(lambda: Arrow(o, o + 1.7 * np.array([math.cos(beta.get_value()), math.sin(beta.get_value()), 0]),
                                              buff=0, color=AMBER, stroke_width=5))
        la = eq(r"U_A = X", size=32, color=BLUE).move_to(LEFT * 4.0 + DOWN * 2.75)
        lb = eq(r"U_B = \cos\beta\,X + \sin\beta\,Z", size=32, color=AMBER).next_to(la, DOWN, buff=0.12)
        self.play(Create(a_arrow), Create(b_arrow), Write(la), Write(lb))

        ax = Axes(x_range=[0, math.pi / 2, math.pi / 8], y_range=[0, 1.05, 0.25], x_length=5.4, y_length=3.4,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 2.9 + DOWN * 0.6)
        yl = eq(r"P(+)", size=30).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        xt = VGroup(*[eq(s, size=28, color=MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.12)
                      for s, v in ((r"0^\circ", 0), (r"45^\circ", math.pi / 4), (r"90^\circ", math.pi / 2))])
        yt = VGroup(*[eq(s, size=28, color=MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.1) for s, v in (("0", 0), ("1/2", 0.5), ("1", 1))])
        half = DashedLine(ax.c2p(0, 0.5), ax.c2p(math.pi / 2, 0.5), color=MUTED, stroke_width=3)
        hl = VGroup(label("classical mixture", 22, MUTED), label("of orders: 1/2", 22, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.05).next_to(ax.c2p(0, 0.5), DOWN + RIGHT, buff=0.12)
        self.play(Create(ax), Write(yl), FadeIn(xt), FadeIn(yt), Create(half), FadeIn(hl))
        law = VGroup(eq(r"\{U_A,U_B\} = 2\cos\beta\,1", size=32), eq(FACT_COS, size=34, color=VIOLET)).arrange(
            DOWN, buff=0.12).move_to(RIGHT * 2.9 + UP * 2.1)
        self.play(Write(law), run_time=1.4)
        dot = always_redraw(lambda: Dot(ax.c2p(beta.get_value(), math.cos(beta.get_value()) ** 2), color=VIOLET, radius=0.08))
        tr = TracedPath(dot.get_center, stroke_color=VIOLET, stroke_width=4)
        bl = eq(r"\beta =", size=32, color=AMBER).move_to(LEFT * 4.6 + UP * 2.0)
        bn = DecimalNumber(0, num_decimal_places=0, unit=r"^\circ", font_size=32, color=AMBER).next_to(bl, RIGHT, buff=0.12)
        bn.add_updater(lambda m: m.set_value(math.degrees(beta.get_value())))
        self.add(tr, dot, bl, bn)
        self.play(beta.animate.set_value(math.pi / 2), run_time=7, rate_func=linear)
        e1 = label("0°: commute, P(+) = 1", 24, CYAN).move_to(ax.c2p(math.pi * 0.33, 0.95))
        e2 = label("90°: anticommute, P(+) = 0", 24, RED).move_to(ax.c2p(math.pi * 0.19, 0.13))
        self.play(FadeIn(e1), FadeIn(e2))
        self.wait(2.0)


class DephasingControl(Scene):
    def construct(self):
        title = label("The information sits in the control's coherence", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        setup = eq(r"U_A = X,\ U_B = Z:\quad \text{output } |-\rangle_c\otimes ZX|\psi\rangle", size=34).next_to(title, DOWN, buff=0.3)
        self.play(Write(setup))
        V = ValueTracker(1.0)

        def entry(i, j):
            return always_redraw(lambda: DecimalNumber(float(control_state(V.get_value())[i, j].real), num_decimal_places=2,
                                                       include_sign=(i != j), font_size=40, color=INK)
                                 .move_to(LEFT * 4.2 + RIGHT * (1.5 * j - 0.75) + DOWN * (1.0 * i - 0.1)))
        ents = VGroup(*[entry(i, j) for i in range(2) for j in range(2)])
        lb = Line(LEFT * 5.9 + UP * 0.6, LEFT * 5.9 + DOWN * 1.8, color=INK, stroke_width=3)
        rb = Line(LEFT * 2.5 + UP * 0.6, LEFT * 2.5 + DOWN * 1.8, color=INK, stroke_width=3)
        rl = eq(r"\rho_c =", size=38).next_to(lb, LEFT, buff=0.15)
        self.play(FadeIn(ents), Create(lb), Create(rb), Write(rl))
        vl = eq(r"V =", size=34, color=VIOLET).move_to(LEFT * 4.6 + DOWN * 2.6)
        vn = DecimalNumber(1.0, num_decimal_places=2, font_size=34, color=VIOLET).next_to(vl, RIGHT, buff=0.12)
        vn.add_updater(lambda m: m.set_value(V.get_value()))
        self.play(Write(vl), FadeIn(vn))

        base = DOWN * 2.2
        H = 3.2
        bm = always_redraw(lambda: Rectangle(width=1.0, height=max(H * (1 + V.get_value()) / 2, 0.01), color=RED,
                                             fill_color=RED, fill_opacity=0.7).move_to(RIGHT * 3.9 + base, aligned_edge=DOWN))
        bp = always_redraw(lambda: Rectangle(width=1.0, height=max(H * (1 - V.get_value()) / 2, 0.01), color=CYAN,
                                             fill_color=CYAN, fill_opacity=0.7).move_to(RIGHT * 2.2 + base, aligned_edge=DOWN))
        floor = Line(RIGHT * 1.3 + base, RIGHT * 4.8 + base, color=MUTED)
        lp = eq(r"P(+)", size=30, color=CYAN).next_to(RIGHT * 2.2 + base, DOWN, buff=0.15)
        lm = eq(r"P(-)", size=30, color=RED).next_to(RIGHT * 3.9 + base, DOWN, buff=0.15)
        halfl = DashedLine(RIGHT * 1.3 + base + UP * H / 2, RIGHT * 4.8 + base + UP * H / 2, color=MUTED, stroke_width=2)
        hlab = eq(r"\tfrac12", size=28, color=MUTED).next_to(halfl, RIGHT, buff=0.1)
        self.play(Create(floor), FadeIn(bm), FadeIn(bp), Write(lp), Write(lm), Create(halfl), Write(hlab))
        fd = eq(FACT_DEPH, size=34, color=RED).move_to(RIGHT * 3.1 + UP * 1.35)
        self.play(Write(fd))
        self.wait(0.6)
        self.play(V.animate.set_value(0.0), run_time=5, rate_func=linear)
        end = label("V = 0: a classical mixture of orders; the control is a coin", 26, MUTED).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(end))
        self.wait(0.8)
        self.play(V.animate.set_value(1.0), FadeOut(end), run_time=3, rate_func=linear)
        self.wait(1.5)
        _ = (BLUE, AMBER, VIOLET, Rectangle)
