"""L3-04 Tensor products and joint systems: three 3Blue1Brown-style scenes.

ProductGrid     a 2-outcome system and a 3-outcome system give a 2 x 3 grid of joint outcomes; the grid
                is read row by row into a 6-entry vector (order 00, 01, 02, 10, 11, 12); dimensions multiply,
                and n two-outcome systems need 2^n entries (2^{10} = 1024).
KroneckerFill   a = (3/5, 4/5) and b = (2/3, 2/3, 1/3): the cells of the grid fill with the products a_j b_k,
                the grid is the outer product a b^T (every row proportional), and it unrolls into a (x) b.
RankTest        a two-qubit vector as a 2 x 2 table: the product (0.48, 0.36, 0.64, 0.48) has determinant 0,
                the vector (1, 0, 0, 1)/sqrt2 has determinant 1/2 and cannot factor; for
                cos(theta)|00> + sin(theta)|11> the determinant cos(theta) sin(theta) is traced live.
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys
from fractions import Fraction as Fr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from manim import (DOWN, LEFT, PI, RIGHT, UP, Axes, Create, Dot, FadeIn, FadeOut,  # noqa: E402
                   Line, Rectangle, ReplacementTransform, Scene, SurroundingRectangle, TracedPath, Transform,
                   TransformFromCopy, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, CYAN_LIGHT, GRID, INK, MUTED, RED, VIOLET, eq, label  # noqa: E402

A = [Fr(3, 5), Fr(4, 5)]
B = [Fr(2, 3), Fr(2, 3), Fr(1, 3)]
AB = [x * y for x in A for y in B]
assert AB == [Fr(2, 5), Fr(2, 5), Fr(1, 5), Fr(8, 15), Fr(8, 15), Fr(4, 15)]
assert sum(x * x for x in A) == 1 and sum(x * x for x in B) == 1 and sum(x * x for x in AB) == 1
assert np.allclose(np.kron([float(x) for x in A], [float(x) for x in B]), [float(x) for x in AB])

PROD = np.kron([0.6, 0.8], [0.8, 0.6])                      # (0.48, 0.36, 0.64, 0.48)
assert np.allclose(PROD, [0.48, 0.36, 0.64, 0.48])
assert abs(0.48 * 0.48 - 0.36 * 0.64) < 1e-12
BELL = np.array([1, 0, 0, 1]) / math.sqrt(2)
assert abs(np.linalg.det(BELL.reshape(2, 2)) - 0.5) < 1e-12
assert 2 ** 10 == 1024


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["2 \\times 3 = 6", "2^{10} = 1024", "\\tfrac{8}{15}", "0.48 \\cdot 0.48 - 0.36 \\cdot 0.64 = 0",
            "\\cos\\theta\\,\\sin\\theta"]


def tf(x: Fr) -> str:
    return rf"\tfrac{{{x.numerator}}}{{{x.denominator}}}" if x.denominator != 1 else str(x.numerator)


def grid(rows, cols, w=1.35, h=0.95):
    cells = VGroup(*[Rectangle(width=w, height=h, color=MUTED, stroke_width=2) for _ in range(rows * cols)])
    cells.arrange_in_grid(rows=rows, cols=cols, buff=0)
    return cells


class ProductGrid(Scene):
    def construct(self):
        title = label("Joint outcomes multiply", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        g = grid(2, 3).move_to(LEFT * 2.6 + DOWN * 0.1)
        alab = VGroup(*[eq(rf"a = {j}", size=32, color=VIOLET).next_to(g[3 * j], LEFT, buff=0.25) for j in range(2)])
        blab = VGroup(*[eq(rf"b = {k}", size=32, color=AMBER).next_to(g[k], UP, buff=0.2) for k in range(3)])
        sysB = label("columns: system B, 3 outcomes", 26, AMBER).next_to(blab, UP, buff=0.25)
        sysA = label("rows: system A, 2 outcomes", 26, VIOLET).next_to(sysB, UP, buff=0.12)
        self.play(FadeIn(alab), FadeIn(sysA))
        self.play(FadeIn(blab), FadeIn(sysB))
        self.play(Create(g), run_time=1.2)
        names = VGroup(*[eq(f"{j}{k}", size=36).move_to(g[3 * j + k]) for j in range(2) for k in range(3)])
        self.play(Write(names), run_time=1.5)
        count = eq(r"2 \times 3 = 6 \text{ joint outcomes}", size=38).next_to(g, DOWN, buff=0.45)
        add = eq(r"\text{not } 2 + 3 = 5", size=34, color=RED).next_to(count, DOWN, buff=0.2)
        self.play(Write(count))
        self.play(FadeIn(add))
        self.wait(0.8)

        # unroll row by row into a 6-entry column
        col = VGroup(*[eq(f"{j}{k}", size=34) for j in range(2) for k in range(3)]).arrange(DOWN, buff=0.22)
        col.move_to(RIGHT * 1.6 + DOWN * 0.3)
        br = VGroup(Line(col.get_corner(UP + LEFT) + LEFT * 0.25, col.get_corner(DOWN + LEFT) + LEFT * 0.25, color=INK),
                    Line(col.get_corner(UP + RIGHT) + RIGHT * 0.25, col.get_corner(DOWN + RIGHT) + RIGHT * 0.25, color=INK))
        order = label("order: row by row", 26, MUTED).next_to(br, UP, buff=0.25)
        self.play(Create(br), FadeIn(order))
        for i in range(6):
            self.play(TransformFromCopy(names[i], col[i]), run_time=0.45)
        idx = eq(r"\text{position } = 3a + b", size=32, color=MUTED).next_to(br, DOWN, buff=0.3)
        self.play(Write(idx))
        self.wait(0.6)

        # growth with the number of two-outcome systems
        ax = Axes(x_range=[0, 10.5, 1], y_range=[0, 1100, 500], x_length=3.4, y_length=4.0,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 5.0 + DOWN * 0.3)
        nl = label("n two-outcome systems", 24, MUTED).next_to(ax, DOWN, buff=0.2)
        self.play(Create(ax), FadeIn(nl))
        bars = VGroup()
        for n in range(1, 11):
            top = ax.c2p(n, 2 ** n)
            bar = Rectangle(width=0.22, height=max(top[1] - ax.c2p(n, 0)[1], 0.01), color=VIOLET, fill_opacity=0.7,
                            stroke_width=0)
            bar.move_to(ax.c2p(n, 0), aligned_edge=DOWN)
            bars.add(bar)
        self.play(Create(bars), run_time=2)
        grow = eq(r"2^{10} = 1024", size=34, color=VIOLET).next_to(ax.c2p(10, 1024), LEFT, buff=0.2)
        self.play(Write(grow))
        self.wait(2)


class KroneckerFill(Scene):
    def construct(self):
        title = label("The tensor product fills the grid with products", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        g = grid(2, 3, w=1.5, h=1.0).move_to(LEFT * 2.2 + DOWN * 0.5)
        acol = VGroup(*[eq(tf(A[j]), size=38, color=VIOLET).next_to(g[3 * j], LEFT, buff=0.35) for j in range(2)])
        brow = VGroup(*[eq(tf(B[k]), size=38, color=AMBER).next_to(g[k], UP, buff=0.25) for k in range(3)])
        an = eq(r"a = (\tfrac{3}{5}, \tfrac{4}{5})", size=36, color=VIOLET).to_corner(LEFT + UP).shift(DOWN * 1.0)
        bn = eq(r"b = (\tfrac{2}{3}, \tfrac{2}{3}, \tfrac{1}{3})", size=36, color=AMBER).next_to(an, RIGHT, buff=0.8)
        self.play(Write(an), Write(bn))
        self.play(Create(g), FadeIn(acol), FadeIn(brow))
        vals = VGroup()
        for j in range(2):
            for k in range(3):
                v = eq(tf(AB[3 * j + k]), size=38).move_to(g[3 * j + k])
                vals.add(v)
        for j in range(2):
            for k in range(3):
                hl = VGroup(SurroundingRectangle(acol[j], color=VIOLET, buff=0.06), SurroundingRectangle(brow[k], color=AMBER, buff=0.06))
                self.play(FadeIn(hl), run_time=0.25)
                self.play(TransformFromCopy(VGroup(acol[j], brow[k]), vals[3 * j + k]), run_time=0.6)
                self.play(FadeOut(hl), run_time=0.2)
        outer = eq(r"\text{grid} = a\,b^{\mathsf T}: \text{ row } 2 = \tfrac43 \times \text{row } 1", size=32, color=MUTED).next_to(g, DOWN, buff=0.4)
        self.play(Write(outer))
        self.wait(0.6)

        col = VGroup(*[eq(tf(x), size=42) for x in AB]).arrange(DOWN, buff=0.12).move_to(RIGHT * 3.3 + DOWN * 0.45)
        brl = Line(col.get_corner(UP + LEFT) + LEFT * 0.3, col.get_corner(DOWN + LEFT) + LEFT * 0.3, color=INK)
        brr = Line(col.get_corner(UP + RIGHT) + RIGHT * 0.3, col.get_corner(DOWN + RIGHT) + RIGHT * 0.3, color=INK)
        lhs = eq(r"a \otimes b =", size=38).next_to(brl, LEFT, buff=0.2)
        self.play(Write(lhs), Create(brl), Create(brr))
        for i in range(6):
            self.play(TransformFromCopy(vals[i], col[i]), run_time=0.4)
        blocks = VGroup(SurroundingRectangle(col[0:3], color=VIOLET, buff=0.08), SurroundingRectangle(col[3:6], color=VIOLET, buff=0.08))
        blabs = VGroup(eq(r"\tfrac35\, b", size=32, color=VIOLET).next_to(blocks[0], RIGHT, buff=0.35),
                       eq(r"\tfrac45\, b", size=32, color=VIOLET).next_to(blocks[1], RIGHT, buff=0.35))
        self.play(Create(blocks), Write(blabs))
        norm = eq(r"\|a \otimes b\|^2 = \tfrac{9}{25} + \tfrac{144}{225} = 1", size=32).to_edge(DOWN, buff=0.3).shift(RIGHT * 2.6)
        self.play(Write(norm))
        self.wait(2)


class RankTest(Scene):
    def table(self, vals, colr=INK):
        g = grid(2, 2, w=1.45, h=0.95)
        txt = VGroup(*[eq(v, size=36, color=colr).move_to(g[i]) for i, v in enumerate(vals)])
        heads = VGroup(eq("0", size=30, color=MUTED).next_to(g[0], UP, buff=0.12), eq("1", size=30, color=MUTED).next_to(g[1], UP, buff=0.12),
                       eq("0", size=30, color=MUTED).next_to(g[0], LEFT, buff=0.15), eq("1", size=30, color=MUTED).next_to(g[2], LEFT, buff=0.15))
        return VGroup(g, txt, heads)

    def construct(self):
        title = label("Can a joint vector be split into two parts?", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        rule = eq(r"c = a \otimes b \iff \det\begin{pmatrix} c_{00} & c_{01} \\ c_{10} & c_{11} \end{pmatrix} = 0", size=36).next_to(title, DOWN, buff=0.3)
        self.play(Write(rule))

        t1 = self.table(["0.48", "0.36", "0.64", "0.48"], CYAN).move_to(LEFT * 3.6 + DOWN * 0.6)
        h1 = label("product of (0.6, 0.8) and (0.8, 0.6)", 24, CYAN).next_to(t1, UP, buff=0.35)
        self.play(FadeIn(h1), Create(t1[0]), FadeIn(t1[2]), Write(t1[1]))
        d1 = eq(r"0.48 \cdot 0.48 - 0.36 \cdot 0.64 = 0", size=32, color=CYAN).next_to(t1, DOWN, buff=0.35)
        self.play(Write(d1))
        prop = label("rows proportional: rank 1", 24, MUTED).next_to(d1, DOWN, buff=0.2)
        self.play(FadeIn(prop))

        t2 = self.table([r"\tfrac{1}{\sqrt2}", "0", "0", r"\tfrac{1}{\sqrt2}"], RED).move_to(RIGHT * 3.4 + DOWN * 0.6)
        h2 = label("the vector (1, 0, 0, 1)/√2", 24, RED).next_to(t2, UP, buff=0.35)
        self.play(FadeIn(h2), Create(t2[0]), FadeIn(t2[2]), Write(t2[1]))
        d2 = eq(r"\tfrac12 - 0 = \tfrac12 \ne 0", size=32, color=RED).next_to(t2, DOWN, buff=0.35)
        self.play(Write(d2))
        why = eq(r"a_0 b_0 \ne 0,\ a_1 b_1 \ne 0 \Rightarrow a_0 b_1 \ne 0", size=30, color=MUTED).next_to(d2, DOWN, buff=0.2)
        self.play(Write(why))
        ent = label("cannot factor: entangled", 26, RED).next_to(why, DOWN, buff=0.15)
        self.play(FadeIn(ent))
        self.wait(1.5)
        self.play(FadeOut(VGroup(t1, h1, d1, prop, t2, h2, d2, why, ent)))

        # sweep cos(theta)|00> + sin(theta)|11>
        th = ValueTracker(0.0)
        fam = eq(r"c(\theta) = \cos\theta\,|00\rangle + \sin\theta\,|11\rangle", size=34).move_to(LEFT * 3.4 + UP * 1.1)
        self.play(Write(fam))
        g = grid(2, 2, w=1.45, h=0.95).move_to(LEFT * 3.4 + DOWN * 1.0)
        self.play(Create(g))

        def cell(i, val):
            return eq(f"{val:.2f}", size=34, color=INK if abs(val) > 1e-9 else MUTED).move_to(g[i])

        nums = always_redraw(lambda: VGroup(cell(0, math.cos(th.get_value())), cell(1, 0.0), cell(2, 0.0),
                                            cell(3, math.sin(th.get_value()))))
        self.add(nums)
        ax = Axes(x_range=[0, PI / 2, PI / 4], y_range=[0, 0.5, 0.25], x_length=5.0, y_length=3.2,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 3.2 + DOWN * 0.9)
        yl = eq(r"\det = \cos\theta\,\sin\theta", size=34, color=VIOLET).next_to(ax, UP, buff=0.3)
        xt = VGroup(eq(r"\theta", size=32).next_to(ax.x_axis, RIGHT, buff=0.12),
                    eq(r"\tfrac{\pi}{4}", size=30, color=MUTED).next_to(ax.c2p(PI / 4, 0), DOWN, buff=0.12),
                    eq(r"\tfrac{\pi}{2}", size=30, color=MUTED).next_to(ax.c2p(PI / 2, 0), DOWN, buff=0.12),
                    eq(r"\tfrac12", size=30, color=MUTED).next_to(ax.c2p(0, 0.5), LEFT, buff=0.12))
        self.play(Create(ax), Write(yl), FadeIn(xt))
        dot = always_redraw(lambda: Dot(ax.c2p(th.get_value(), math.cos(th.get_value()) * math.sin(th.get_value())), color=VIOLET, radius=0.06))
        trace = TracedPath(dot.get_center, stroke_color=VIOLET, stroke_width=4)
        self.add(trace, dot)
        self.play(th.animate.set_value(PI / 2), run_time=7, rate_func=linear)
        ends = label("product only at θ = 0 and θ = π/2", 26, INK).next_to(ax, DOWN, buff=0.55)
        most = label("largest at θ = π/4", 24, VIOLET).move_to(ax.c2p(PI / 4, 0.25))
        self.play(FadeIn(ends), FadeIn(most))
        self.wait(2)
        _ = (BLUE, CYAN_LIGHT, GRID, AMBER, ReplacementTransform, Transform, DOWN)
