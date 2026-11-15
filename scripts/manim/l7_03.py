"""L7-03 Quantum kernels and data access: three scenes.

FeatureMapBloch   x on a line is embedded as RY(x)|0> on a Bloch great circle; the kernel of two inputs is
                  |<phi(x)|phi(x')>|^2 = cos^2((x - x')/2) = (1 + r.r')/2, swept live.
GramShots         the 8 x 8 Gram matrix of equally spaced inputs (rank 3, eigenvalues 4, 2, 2, 0...), then
                  shot-noise estimates with N = 10, 100, 1000, 10000 shots per entry: total shots 28 N, and the
                  smallest eigenvalue of the estimate is negative.
Concentration     the product feature map on n qubits: off-diagonal kernel values collapse toward 2^-n, and
                  past n ~ 10 the typical entry is smaller than the noise of 1000 shots.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DEGREES, DOWN, LEFT, ORIGIN, PI, RIGHT, UP, Arrow3D, Axes, Create, DashedLine, DecimalNumber,
                   Dot, FadeIn, FadeOut, Line, NumberLine, ParametricFunction, Rectangle, Scene, Sphere, Square,
                   ThreeDAxes, ThreeDScene, Transform, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ------------------------------------------------------------------ shared numbers
K0 = math.cos((0 - PI / 2) / 2) ** 2           # x = 0, x' = pi/2 -> 1/2
assert abs(K0 - 0.5) < 1e-12

M = 8
XG = 2 * np.pi * np.arange(M) / M
KG = np.cos((XG[:, None] - XG[None, :]) / 2) ** 2
EIG = np.sort(np.linalg.eigvalsh(KG))[::-1]
assert np.allclose(EIG[:3], [4, 2, 2]) and np.allclose(EIG[3:], 0, atol=1e-12)
PAIRS = M * (M - 1) // 2                       # 28 off-diagonal entries to estimate
assert PAIRS == 28
NS = (10, 100, 1000, 10000)


def noisy_gram(n, seed=100):
    g = np.random.default_rng(seed)
    kh = np.eye(M)
    iu = np.triu_indices(M, 1)
    v = g.binomial(n, KG[iu]) / n
    kh[iu] = v
    kh[(iu[1], iu[0])] = v
    return kh


LMIN = [float(np.linalg.eigvalsh(noisy_gram(n)).min()) for n in NS]
assert all(v < 0 for v in LMIN)

# product feature map: E k = 2^-n, E k^2 = (3/8)^n
NQ = (1, 2, 4, 8)
N_CROSS = math.log2(1001)                      # 2^-n = sd of 1000 shots  <=>  k = 1/(N+1)
assert abs(N_CROSS - 9.967) < 1e-3


def product_kernel_samples(n, count=3000, seed=5):
    g = np.random.default_rng(seed + n)
    x = g.uniform(0, 2 * PI, size=(count, n))
    z = g.uniform(0, 2 * PI, size=(count, n))
    return np.prod(np.cos((x - z) / 2) ** 2, axis=1)


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["\\cos^2\\tfrac{x - x'}{2}", "\\tfrac{1}{2}(1 + \\vec r\\cdot\\vec r')", "4, 2, 2", "28 N",
            f"{LMIN[0]:.3f}", "2^{-n}", "9.97"]


# ================================================================ scene 1
class FeatureMapBloch(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=72 * DEGREES, theta=-60 * DEGREES, zoom=0.85)
        sc = 2.0
        axes = ThreeDAxes(x_range=[-1.4, 1.4, 1], y_range=[-1.4, 1.4, 1], z_range=[-1.4, 1.4, 1], x_length=4.4,
                          y_length=4.4, z_length=4.4, axis_config={"color": MUTED, "include_tip": False})
        sph = Sphere(radius=sc, resolution=(18, 18)).set_fill(CYAN, opacity=0.06).set_stroke(GRID, width=0.5)
        circ = ParametricFunction(lambda t: np.array([sc * math.sin(t), 0, sc * math.cos(t)]), t_range=[0, 2 * PI],
                                  color=MUTED, stroke_width=2)
        title = label("A feature map embeds data as quantum states", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Create(axes), FadeIn(sph), Create(circ), Write(title), run_time=1.6)

        line = NumberLine(x_range=[0, 2 * PI, PI / 2], length=5.0, color=MUTED, include_numbers=False)
        line.to_corner(LEFT + DOWN, buff=0.6).shift(UP * 0.3)
        ticks = VGroup(*[eq(s, size=26, color=MUTED).next_to(line.n2p(v), DOWN, buff=0.15)
                         for s, v in (("0", 0), ("\\pi", PI), ("2\\pi", 2 * PI))])
        xname = label("input x", 24, MUTED).next_to(line, UP, buff=0.5).align_to(line, LEFT)
        self.add_fixed_in_frame_mobjects(line, ticks, xname)
        self.play(Create(line), FadeIn(ticks), FadeIn(xname))
        fm = eq(r"|\phi(x)\rangle = R_Y(x)|0\rangle", size=34, color=VIOLET).to_corner(LEFT + UP, buff=0.5).shift(DOWN * 0.7)
        self.add_fixed_in_frame_mobjects(fm)
        self.play(Write(fm))

        x1 = ValueTracker(0.0)
        x2 = ValueTracker(PI / 2)

        def vec(t):
            return np.array([sc * math.sin(t), 0, sc * math.cos(t)])

        a1 = always_redraw(lambda: Arrow3D(ORIGIN, vec(x1.get_value()), color=VIOLET, thickness=0.03))
        a2 = always_redraw(lambda: Arrow3D(ORIGIN, vec(x2.get_value()), color=AMBER, thickness=0.03))
        d1 = Dot(line.n2p(0.0), color=VIOLET, radius=0.09)
        d2 = Dot(line.n2p(PI / 2), color=AMBER, radius=0.09)
        d1.add_updater(lambda m: m.move_to(line.n2p(x1.get_value())))
        d2.add_updater(lambda m: m.move_to(line.n2p(x2.get_value())))
        self.add_fixed_in_frame_mobjects(d1, d2)
        self.play(FadeIn(a1), FadeIn(a2), FadeIn(d1), FadeIn(d2))

        kform = VGroup(
            eq(r"k(x, x') = |\langle\phi(x)|\phi(x')\rangle|^2", size=32),
            eq(r"= \cos^2\tfrac{x - x'}{2}", size=32),
            eq(r"= \tfrac{1}{2}(1 + \vec r\cdot\vec r')", size=32, color=MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).to_corner(RIGHT + UP, buff=0.5).shift(DOWN * 0.7)
        self.add_fixed_in_frame_mobjects(kform)
        for m in kform:
            self.play(FadeIn(m), run_time=0.8)
        klab = label("k =", 30, INK)
        kval = DecimalNumber(K0, num_decimal_places=3, color=RED, font_size=40)
        def _upd(m):
            m.set_value(math.cos((x1.get_value() - x2.get_value()) / 2) ** 2)
            self.renderer.camera.add_fixed_in_frame_mobjects(m)
        kval.add_updater(_upd)
        row = VGroup(klab, kval).arrange(RIGHT, buff=0.2).to_corner(RIGHT + DOWN, buff=0.8)
        self.add_fixed_in_frame_mobjects(row)
        self.play(FadeIn(row))
        self.wait(0.8)
        self.play(x2.animate.set_value(PI), run_time=2.5, rate_func=linear)
        orth = label("x' - x = π: orthogonal states, k = 0", 24, MUTED).next_to(row, UP, buff=0.3).align_to(row, RIGHT)
        self.add_fixed_in_frame_mobjects(orth)
        self.play(FadeIn(orth))
        self.wait(1.0)
        self.play(FadeOut(orth))
        self.play(x2.animate.set_value(2 * PI), run_time=3.5, rate_func=linear)
        note = label("x' = 2π gives the same state as x = 0: k = 1", 24, MUTED).next_to(row, UP, buff=0.3).align_to(row, RIGHT)
        self.add_fixed_in_frame_mobjects(note)
        self.play(FadeIn(note))
        self.wait(1.0)
        self.play(FadeOut(note), x1.animate.set_value(PI / 3), x2.animate.set_value(PI), run_time=2.0)
        last = label("x = π/3, x' = π: k = 1/4", 24, MUTED).next_to(row, UP, buff=0.3).align_to(row, RIGHT)
        self.add_fixed_in_frame_mobjects(last)
        self.play(FadeIn(last))
        self.move_camera(theta=-95 * DEGREES, run_time=3)
        self.wait(1.2)
        _ = (DashedLine, Line)


# ================================================================ scene 2
class GramShots(Scene):
    def construct(self):
        title = label("Every kernel entry is an estimate", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        cell = 0.58
        origin = LEFT * 3.6 + UP * 0.3

        def color_of(v):
            v = max(-0.15, min(1.0, v))
            if v < 0:
                return RED
            from manim import interpolate_color, ManimColor
            return interpolate_color(ManimColor("#ffffff"), ManimColor(VIOLET), v)

        def grid(K):
            g = VGroup()
            for i in range(M):
                for j in range(M):
                    sq = Square(side_length=cell, stroke_width=0.6, stroke_color=GRID).set_fill(color_of(K[i, j]), opacity=1)
                    sq.move_to(origin + RIGHT * (j - (M - 1) / 2) * cell + DOWN * (i - (M - 1) / 2) * cell)
                    g.add(sq)
            return g

        exact = grid(KG)
        cap = eq(r"K_{ij} = \cos^2\tfrac{x_i - x_j}{2},\ \ x_i = \tfrac{2\pi i}{8}", size=30).next_to(exact, DOWN, buff=0.3)
        self.play(FadeIn(exact), Write(cap))
        info = VGroup(
            label("exact Gram matrix", 26, INK),
            eq(r"\text{eigenvalues } 4, 2, 2, 0, 0, 0, 0, 0", size=30),
            label("rank 3: positive semidefinite", 24, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(RIGHT * 3.2 + UP * 1.6)
        self.play(FadeIn(info))
        self.wait(1.5)

        est = VGroup(
            label("compute-uncompute estimate", 26, INK),
            eq(r"\hat K_{ij} = \tfrac{1}{N}\#\{\text{outcome } 0\cdots0\}", size=30),
            eq(r"28\ \text{entries} \times N\ \text{shots} = 28 N", size=30, color=VIOLET),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(RIGHT * 3.2 + UP * 1.6)
        self.play(Transform(info, est))
        cur = exact
        readout = None
        for n, lm in zip(NS, LMIN):
            new = grid(noisy_gram(n))
            r = VGroup(
                eq(rf"N = {n}", size=32),
                eq(rf"\text{{total shots}} = {PAIRS * n:,}".replace(",", "{,}"), size=30),
                eq(rf"\lambda_{{\min}}(\hat K) = {lm:.3f}", size=32, color=RED),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 3.2 + DOWN * 1.1)
            if readout is None:
                self.play(Transform(cur, new), FadeIn(r), run_time=1.4)
                readout = r
            else:
                self.play(Transform(cur, new), Transform(readout, r), run_time=1.4)
            self.wait(1.8)
        key = label("a negative eigenvalue: the estimate is not a valid kernel matrix", 26, RED)
        key.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(key))
        self.wait(2.0)
        _ = (Rectangle, Line)


# ================================================================ scene 3
class Concentration(Scene):
    def construct(self):
        title = label("Bigger feature spaces push kernel values to zero", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 1, 0.25], x_length=6.0, y_length=3.8,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(LEFT * 3.2 + DOWN * 0.6)
        nums = VGroup(*[eq(f"{v:g}", size=26, color=MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.15) for v in (0, 0.5, 1)])
        xl = eq(r"k(x, x') \text{ for random } x \ne x'", size=28, color=MUTED).next_to(ax, DOWN, buff=0.55)
        fm = eq(r"|\phi(x)\rangle = \bigotimes_{j=1}^{n} R_Y(x_j)|0\rangle", size=32, color=VIOLET).next_to(ax, UP, buff=0.35)
        self.play(Create(ax), FadeIn(nums), FadeIn(xl), Write(fm))
        edges = np.linspace(0, 1, 26)

        def hist(n):
            v = product_kernel_samples(n)
            c, _ = np.histogram(v, bins=edges)
            frac = c / c.sum()
            g = VGroup()
            for f, e0 in zip(frac, edges[:-1]):
                if f <= 0:
                    continue
                h = min(f / 0.6, 1.0) * 3.8
                r = Rectangle(width=ax.c2p(edges[1], 0)[0] - ax.c2p(0, 0)[0], height=max(h, 0.001), stroke_width=0.5,
                              stroke_color=VIOLET).set_fill(VIOLET, opacity=0.55)
                r.move_to(ax.c2p(e0 + (edges[1] - edges[0]) / 2, 0), aligned_edge=DOWN)
                g.add(r)
            return g, v

        cur = None
        txt = None
        for n in NQ:
            g, v = hist(n)
            assert abs(v.mean() - 2.0 ** -n) < 4 * v.std() / math.sqrt(len(v)) + 1e-12
            t = VGroup(eq(rf"n = {n}", size=34),
                       eq(rf"E\,k = 2^{{-n}} = {2.0 ** -n:.4f}", size=30, color=VIOLET),
                       eq(rf"\text{{sample mean}} = {v.mean():.4f}", size=28, color=MUTED)
                       ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(RIGHT * 3.4 + UP * 1.7)
            if cur is None:
                self.play(FadeIn(g), FadeIn(t))
                cur, txt = g, t
            else:
                self.play(Transform(cur, g), Transform(txt, t), run_time=1.4)
            self.wait(1.4)

        # phase 2: typical value against shot noise, log scale
        self.play(FadeOut(VGroup(ax, nums, xl, fm, cur, txt)))
        ax2 = Axes(x_range=[0, 16, 2], y_range=[0, 5, 1], x_length=7.4, y_length=4.2,
                   axis_config={"color": MUTED, "include_tip": False}).move_to(LEFT * 2.2 + DOWN * 0.5)
        yl = VGroup(*[eq(f"10^{{{p}}}", size=26, color=MUTED).next_to(ax2.c2p(0, p + 5), LEFT, buff=0.12) for p in range(-5, 1)])
        xt = VGroup(*[eq(str(v), size=26, color=MUTED).next_to(ax2.c2p(v, 0), DOWN, buff=0.12) for v in (0, 4, 8, 12, 16)])
        xn = label("qubits n", 24, MUTED).next_to(ax2, DOWN, buff=0.5)
        self.play(Create(ax2), FadeIn(yl), FadeIn(xt), FadeIn(xn))
        mean_curve = ax2.plot(lambda n: 5 - n * math.log10(2), x_range=[0, 16], color=VIOLET, stroke_width=4)
        sd_curve = ax2.plot(lambda n: 5 + 0.5 * math.log10(2.0 ** -n * (1 - 2.0 ** -n) / 1000 + 1e-30),
                            x_range=[1, 16], color=AMBER, stroke_width=4)
        l1 = eq(r"E\,k = 2^{-n}", size=30, color=VIOLET).move_to(ax2.c2p(5.6, 4.3))
        l2 = eq(r"\text{shot sd, } N = 1000", size=28, color=AMBER).next_to(ax2.c2p(14.5, 2.1), UP, buff=0.12)
        self.play(Create(mean_curve), Write(l1), run_time=1.6)
        self.play(Create(sd_curve), Write(l2), run_time=1.6)
        cross = DashedLine(ax2.c2p(N_CROSS, 0), ax2.c2p(N_CROSS, 5), color=RED)
        cl = eq(rf"n = \log_2 1001 \approx {N_CROSS:.2f}", size=30, color=RED).move_to(RIGHT * 4.3 + UP * 1.0)
        self.play(Create(cross), Write(cl))
        expl = VGroup(label("beyond this n the typical", 24, INK), label("entry is smaller than its", 24, INK),
                      label("own shot noise", 24, INK)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(cl, DOWN, buff=0.3)
        self.play(FadeIn(expl))
        self.wait(2.5)
        _ = (Dot, Line, ORIGIN)
