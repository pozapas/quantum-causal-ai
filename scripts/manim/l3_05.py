"""L3-05 Eigenvectors and observables: three 3Blue1Brown-style scenes.

EigenDirections     the symmetric matrix A = [[2, 1], [1, 2]] acts on a grid, a unit circle and five vectors;
                    most vectors leave their own line, the two eigenvectors only stretch (by 3 and by 1).
                    Then the characteristic polynomial is derived term by term.
SpectralPieces      A u for u = (2, 0) computed as 3 P_1 u + 1 P_2 u: project onto the eigenlines, stretch
                    each piece by its eigenvalue, add the pieces back: (4, 2).
OutcomesAndAverage  the state psi = (cos t, sin t) sweeps round; the probabilities of the outcomes 3 and 1
                    and the expectation 2 + sin 2t move with it, while every single outcome stays 3 or 1.
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UL, UP, UR, WHITE, ApplyMatrix, Arrow, Circle, Create, DashedLine, DecimalNumber,
                   Dot, FadeIn, FadeOut, Line, NumberLine, NumberPlane, Rectangle, Scene, TransformMatchingTex,
                   ValueTracker, VGroup, Write, always_redraw, linear, smooth)

from qcai_style import AMBER, BLUE, BLUE_LIGHT, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

A = np.array([[2.0, 1.0], [1.0, 2.0]])
EVALS, EVECS = np.linalg.eigh(A)                    # ascending: 1, 3
assert np.allclose(EVALS, [1, 3])
V1 = np.array([1.0, 1.0]) / math.sqrt(2)            # eigenvalue 3
V2 = np.array([1.0, -1.0]) / math.sqrt(2)           # eigenvalue 1
assert np.allclose(A @ V1, 3 * V1) and np.allclose(A @ V2, 1 * V2)
P1, P2 = np.outer(V1, V1), np.outer(V2, V2)
assert np.allclose(3 * P1 + 1 * P2, A) and np.allclose(P1 + P2, np.eye(2))
U = np.array([2.0, 0.0])
assert np.allclose(P1 @ U, [1, 1]) and np.allclose(P2 @ U, [1, -1]) and np.allclose(A @ U, [4, 2])
# characteristic polynomial (2 - l)^2 - 1 = l^2 - 4 l + 3 = (l - 3)(l - 1)
assert all(abs((2 - l) ** 2 - 1 - (l * l - 4 * l + 3)) < 1e-12 for l in (0.0, 1.7, 5.0))


def p3(t):
    """Probability of outcome 3 in psi = (cos t, sin t): |<v_1|psi>|^2 = (1 + sin 2t)/2."""
    return float((V1 @ np.array([math.cos(t), math.sin(t)])) ** 2)


def expect(t):
    psi = np.array([math.cos(t), math.sin(t)])
    return float(psi @ A @ psi)


for _t in (0.0, 0.3, math.pi / 4, 2.0):
    assert abs(p3(_t) - (1 + math.sin(2 * _t)) / 2) < 1e-12
    assert abs(expect(_t) - (2 + math.sin(2 * _t))) < 1e-12
    assert abs(expect(_t) - (3 * p3(_t) + 1 * (1 - p3(_t)))) < 1e-12


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["\\lambda^2 - 4\\lambda + 3", "(\\lambda - 3)(\\lambda - 1)", "A = 3P_1 + 1P_2", "(4, 2)",
            "2 + \\sin 2t", "\\frac{1 + \\sin 2t}{2}"]


def panel(width, height, center):
    return Rectangle(width=width, height=height, stroke_width=0, fill_color=WHITE, fill_opacity=0.94).move_to(center)


class EigenDirections(Scene):
    @staticmethod
    def live_arrow(P, xy, color, mix):
        v = np.array(xy, dtype=float)

        def make():
            a = mix.get_value()
            w = (1 - a) * v + a * (A @ v)
            return Arrow(P(0, 0), P(*w), buff=0, color=color, stroke_width=6, max_tip_length_to_length_ratio=0.3)
        return always_redraw(make)

    def construct(self):
        O = np.array([2.3, -0.7, 0.0])
        s = 0.82                                      # scene units per grid unit

        def P(x, y):
            return O + s * np.array([x, y, 0.0])

        bg = NumberPlane(x_range=[-6, 6, 1], y_range=[-5, 6, 1], background_line_style={"stroke_color": GRID, "stroke_width": 1},
                         axis_config={"color": MUTED, "stroke_width": 2}).scale(s).shift(O)
        grid = NumberPlane(x_range=[-4, 4, 1], y_range=[-4, 4, 1], faded_line_ratio=0,
                           background_line_style={"stroke_color": BLUE_LIGHT, "stroke_width": 1.6, "stroke_opacity": 0.7},
                           axis_config={"stroke_opacity": 0}).scale(s).shift(O)
        self.add(bg)
        box = panel(5.6, 8.2, np.array([-4.1, 0.0, 0.0]))
        title = label("Most vectors turn.", 32, INK, "BOLD")
        title2 = label("Eigenvectors only stretch.", 32, VIOLET, "BOLD")
        head = VGroup(title, title2).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([-4.1, 3.25, 0])
        mat = eq(r"A = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}", size=40).move_to([-4.1, 1.75, 0])
        self.play(Create(grid), FadeIn(box), Write(head), run_time=1.6)
        self.play(Write(mat))

        vecs = [((1, 0), BLUE), ((0, 1), AMBER), ((0.5, -1), MUTED), ((1, 1), VIOLET), ((-1, 1), CYAN)]
        spans, arrows = VGroup(), VGroup()
        mix = ValueTracker(0.0)                     # M(a) = (1 - a) I + a A, the same path ApplyMatrix takes
        for (x, y), c in vecs:
            d = np.array([x, y]) / math.hypot(x, y)
            eigen = c in (VIOLET, CYAN)
            ln = DashedLine(P(*(-5.5 * d)), P(*(5.5 * d)), color=c, stroke_width=3 if eigen else 1.5,
                            stroke_opacity=0.9 if eigen else 0.45, dash_length=0.12)
            spans.add(ln)
            arrows.add(self.live_arrow(P, (x, y), c, mix))
        circle = Circle(radius=s, color=INK, stroke_width=2.5).move_to(O)
        self.play(Create(spans), run_time=1.2)
        self.play(*[Create(a) for a in arrows], Create(circle), run_time=1.4)
        note = label("dashed: the line each vector starts on", 24, MUTED).move_to([-4.1, 0.75, 0])
        self.play(FadeIn(note))
        self.add(box, head, mat, note)          # keep the panel above the moving grid
        self.add(arrows)
        self.play(ApplyMatrix(A, VGroup(grid, circle), about_point=O), mix.animate.set_value(1.0), run_time=3.5, rate_func=smooth)
        self.add(arrows)
        self.add(box, head, mat, note)
        self.wait(0.5)

        l1 = eq(r"A v_1 = 3 v_1", size=34, color=VIOLET).next_to(P(3, 3), RIGHT, buff=0.12)
        l2 = eq(r"A v_2 = 1\, v_2", size=34, color=CYAN).next_to(P(-1, 1), LEFT, buff=0.3).shift(DOWN * 0.2)
        l3 = eq(r"(1, 0) \mapsto (2, 1)", size=32, color=BLUE).next_to(P(2, 1), RIGHT, buff=0.25).shift(DOWN * 0.25)
        for lb in (l1, l2, l3):
            lb.add_background_rectangle(color=WHITE, opacity=0.85, buff=0.06)
        self.play(Write(l1), Write(l2))
        self.play(Write(l3))
        self.wait(0.8)
        msg = label("off its line: not an eigenvector", 24, BLUE).move_to([-4.1, 0.25, 0])
        self.play(FadeIn(msg))
        self.wait(1.0)

        # the characteristic polynomial, term by term
        self.play(FadeOut(note), FadeOut(msg))
        steps = [r"A v = \lambda v \iff (A - \lambda I) v = 0", r"\det(A - \lambda I) = 0",
                 r"(2 - \lambda)^2 - 1 = 0", r"\lambda^2 - 4\lambda + 3 = 0", r"(\lambda - 3)(\lambda - 1) = 0"]
        cur = eq(steps[0], size=32).move_to([-4.1, 0.4, 0])
        self.play(Write(cur))
        self.wait(0.6)
        for st in steps[1:]:
            nxt = eq(st, size=36).move_to([-4.1, 0.4, 0])
            self.play(TransformMatchingTex(cur, nxt), run_time=1.3)
            cur = nxt
            self.wait(0.5)
        roots = eq(r"\lambda_1 = 3,\quad \lambda_2 = 1", size=38, color=VIOLET).move_to([-4.1, -0.8, 0])
        self.play(Write(roots))
        ell = label("the circle became an ellipse", 24, MUTED).move_to([-4.1, -2.0, 0])
        ell2 = label("with axes 3 and 1 along v1, v2", 24, MUTED).next_to(ell, DOWN, buff=0.12)
        self.play(FadeIn(ell), FadeIn(ell2))
        self.wait(2.0)


class SpectralPieces(Scene):
    def construct(self):
        O = np.array([-4.3, -1.0, 0.0])
        s = 0.72

        def P(x, y):
            return O + s * np.array([x, y, 0.0])

        bg = NumberPlane(x_range=[-3, 6, 1], y_range=[-3, 6, 1], background_line_style={"stroke_color": GRID, "stroke_width": 1},
                         axis_config={"color": MUTED, "stroke_width": 2}).scale(s).shift(O + s * np.array([1.5, 1.5, 0]))
        title = label("Split, stretch, add back", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Create(bg), Write(title), run_time=1.4)
        e1 = DashedLine(P(-2.5, -2.5), P(5, 5), color=VIOLET, stroke_width=2.5, dash_length=0.12)
        e2 = DashedLine(P(-2.5, 2.5), P(2.6, -2.6), color=CYAN, stroke_width=2.5, dash_length=0.12)
        el1 = eq(r"\lambda_1 = 3", size=30, color=VIOLET).next_to(P(5, 5), DOWN + RIGHT * 0.2, buff=0.1)
        el2 = eq(r"\lambda_2 = 1", size=30, color=CYAN).next_to(P(-2.5, 2.5), RIGHT, buff=0.1).shift(UP * 0.25)
        self.play(Create(e1), Create(e2), Write(el1), Write(el2))

        u = Arrow(P(0, 0), P(2, 0), buff=0, color=BLUE, stroke_width=6)
        ul = eq(r"u = (2, 0)", size=32, color=BLUE).next_to(P(2, 0), DOWN, buff=0.2).shift(RIGHT * 0.5)
        self.play(Create(u), Write(ul))

        r1 = eq(r"A = 3P_1 + 1P_2", size=40).move_to([2.9, 2.3, 0])
        r2 = eq(r"P_1 = \tfrac12\begin{pmatrix} 1 & 1 \\ 1 & 1 \end{pmatrix},\ P_2 = \tfrac12\begin{pmatrix} 1 & -1 \\ -1 & 1 \end{pmatrix}",
                size=32).move_to([2.9, 1.15, 0])
        self.play(Write(r1))
        self.play(Write(r2))

        # project u onto each eigenline
        f1 = DashedLine(P(2, 0), P(1, 1), color=MUTED, stroke_width=2)
        f2 = DashedLine(P(2, 0), P(1, -1), color=MUTED, stroke_width=2)
        c1 = Arrow(P(0, 0), P(1, 1), buff=0, color=VIOLET, stroke_width=6)
        c2 = Arrow(P(0, 0), P(1, -1), buff=0, color=CYAN, stroke_width=6)
        self.play(Create(f1), Create(f2))
        self.play(Create(c1), Create(c2))
        s1 = eq(r"P_1 u = (1, 1),\quad P_2 u = (1, -1)", size=32).move_to([2.9, 0.0, 0])
        self.play(Write(s1))
        self.wait(0.6)

        # stretch each piece by its eigenvalue
        c1b = Arrow(P(0, 0), P(3, 3), buff=0, color=VIOLET, stroke_width=6)
        self.play(c1.animate.become(c1b), FadeOut(f1), FadeOut(f2), run_time=1.6)
        s2 = eq(r"3P_1 u = (3, 3),\quad 1P_2 u = (1, -1)", size=32).move_to([2.9, -1.0, 0])
        self.play(Write(s2))

        # add back
        g1 = DashedLine(P(3, 3), P(4, 2), color=CYAN, stroke_width=2)
        g2 = DashedLine(P(1, -1), P(4, 2), color=VIOLET, stroke_width=2)
        au = Arrow(P(0, 0), P(4, 2), buff=0, color=RED, stroke_width=7)
        self.play(Create(g1), Create(g2))
        self.play(Create(au))
        aul = eq(r"Au", size=34, color=RED).next_to(P(4, 2), RIGHT, buff=0.1)
        self.play(Write(aul))
        cur = eq(r"Au = 3P_1 u + 1P_2 u", size=36).move_to([2.9, -2.1, 0])
        self.play(Write(cur))
        res = eq(r"Au = (3, 3) + (1, -1) = (4, 2)", size=36, color=RED).move_to([2.9, -2.1, 0])
        self.play(TransformMatchingTex(cur, res), run_time=1.4)
        chk = eq(r"\text{check: } (2\cdot 2 + 1\cdot 0,\ 1\cdot 2 + 2\cdot 0) = (4, 2)", size=30, color=MUTED).move_to([2.9, -3.0, 0])
        self.play(FadeIn(chk))
        self.wait(2.0)


class OutcomesAndAverage(Scene):
    def construct(self):
        title = label("Eigenvalues are outcomes; the average need not be one", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        C = np.array([-4.2, -0.5, 0.0])
        R = 2.0
        circ = Circle(radius=R, color=GRID, stroke_width=2).move_to(C)
        ax = VGroup(Line(C + LEFT * 2.4, C + RIGHT * 2.4, color=MUTED, stroke_width=1.5),
                    Line(C + DOWN * 2.4, C + UP * 2.4, color=MUTED, stroke_width=1.5))
        d1 = np.array([1, 1, 0]) / math.sqrt(2)
        d2 = np.array([1, -1, 0]) / math.sqrt(2)
        e1 = DashedLine(C - 2.5 * d1, C + 2.5 * d1, color=VIOLET, stroke_width=3)
        e2 = DashedLine(C - 2.5 * d2, C + 2.5 * d2, color=CYAN, stroke_width=3)
        lab1 = eq(r"v_1:\ 3", size=30, color=VIOLET).next_to(C + 2.5 * d1, UP, buff=0.05)
        lab2 = eq(r"v_2:\ 1", size=30, color=CYAN).next_to(C + 2.5 * d2, DOWN, buff=0.05)
        self.play(Create(circ), Create(ax), Create(e1), Create(e2), Write(lab1), Write(lab2))

        t = ValueTracker(0.0)

        def tip():
            return C + R * np.array([math.cos(t.get_value()), math.sin(t.get_value()), 0])

        psi = always_redraw(lambda: Arrow(C, tip(), buff=0, color=INK, stroke_width=6))
        foot1 = always_redraw(lambda: DashedLine(tip(), C + R * float(np.dot(tip() - C, d1) / R) * d1, color=VIOLET, stroke_width=2))
        foot2 = always_redraw(lambda: DashedLine(tip(), C + R * float(np.dot(tip() - C, d2) / R) * d2, color=CYAN, stroke_width=2))
        psil = eq(r"\psi = (\cos t, \sin t)", size=32).move_to([-4.2, -3.4, 0])
        self.play(Create(psi), Write(psil))
        self.add(foot1, foot2)

        # right: bars at the outcomes 1 and 3 on an outcome axis, and the expectation marker
        nl = NumberLine(x_range=[0, 4, 1], length=5.6, color=MUTED, include_numbers=False).move_to([2.6, -2.0, 0])
        nums = VGroup(*[eq(str(k), size=30, color=MUTED).next_to(nl.n2p(k), DOWN, buff=0.15) for k in range(5)])
        olab = label("outcome", 24, MUTED).next_to(nl, RIGHT, buff=0.2).shift(DOWN * 0.05)
        self.play(Create(nl), FadeIn(nums), FadeIn(olab))
        H = 2.4

        def bar(k, prob, color):
            w = 0.7
            h = max(H * prob, 0.001)
            return Rectangle(width=w, height=h, stroke_width=0, fill_color=color, fill_opacity=0.85).move_to(
                nl.n2p(k) + UP * h / 2)

        b3 = always_redraw(lambda: bar(3, p3(t.get_value()), VIOLET))
        b1 = always_redraw(lambda: bar(1, 1 - p3(t.get_value()), CYAN))
        v3 = always_redraw(lambda: DecimalNumber(p3(t.get_value()), num_decimal_places=2, font_size=30, color=VIOLET)
                           .next_to(nl.n2p(3) + UP * H * p3(t.get_value()), UP, buff=0.08))
        v1 = always_redraw(lambda: DecimalNumber(1 - p3(t.get_value()), num_decimal_places=2, font_size=30, color=CYAN)
                           .next_to(nl.n2p(1) + UP * H * (1 - p3(t.get_value())), UP, buff=0.08))
        self.play(FadeIn(b3), FadeIn(b1), FadeIn(v3), FadeIn(v1))
        mean = always_redraw(lambda: Dot(nl.n2p(expect(t.get_value())), color=RED, radius=0.11))
        mean_lab = always_redraw(lambda: eq(r"\langle A\rangle", size=28, color=RED).next_to(nl.n2p(expect(t.get_value())), DOWN, buff=0.55))
        self.play(FadeIn(mean), FadeIn(mean_lab))

        f1 = eq(r"p(3) = |\langle v_1|\psi\rangle|^2 = \frac{1 + \sin 2t}{2}", size=32).move_to([2.6, 2.55, 0])
        f2 = eq(r"\langle A\rangle = \psi^{T} A\, \psi = 3\,p(3) + 1\,p(1) = 2 + \sin 2t", size=32, color=RED).move_to([2.6, 1.75, 0])
        self.play(Write(f1))
        self.play(Write(f2))
        self.wait(0.6)
        self.play(t.animate.set_value(math.pi / 4), run_time=3, rate_func=smooth)
        n1 = label("ψ on v1: outcome 3 is certain", 24, VIOLET).move_to([2.6, 1.05, 0])
        self.play(FadeIn(n1))
        self.wait(0.8)
        self.play(FadeOut(n1))
        self.play(t.animate.set_value(3 * math.pi / 4), run_time=4, rate_func=smooth)
        n2 = label("ψ on v2: outcome 1 is certain", 24, CYAN).move_to([2.6, 1.05, 0])
        self.play(FadeIn(n2))
        self.wait(0.8)
        self.play(FadeOut(n2))
        self.play(t.animate.set_value(math.pi), run_time=2, rate_func=linear)
        n3 = label("back at t = π: average 2, yet each shot gives 3 or 1", 24, MUTED).move_to([2.6, 1.05, 0])
        self.play(FadeIn(n3))
        self.wait(2.0)
        _ = (UR, Dot)
