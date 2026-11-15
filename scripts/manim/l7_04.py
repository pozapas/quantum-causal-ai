"""L7-04 Barren plateaus and trainability: four scenes.

GradientHistograms  exact gradients of 600 random deep circuits (our own simulation) for n = 2, 4, 6, 8:
                    the histogram narrows; the sample variances sit on the 2-design predictions
                    1/(2^n+1) (local Z_0) and 1/(2*2^n(2^n+1)) (global projector) on a log scale.
ShotNoiseDetect     a typical true gradient against shot noise: the sampling distributions of the
                    parameter-shift estimate under "gradient 0" and "gradient g" separate only when N
                    passes about 1/(2 Var); for the global cost at n = 8 that is 65,792 shots.
LocalVersusGlobal   depth-one product ansatz: term-by-term derivation of Var = (1/8)(3/8)^(n-1) for the
                    global cost and 1/(8 n^2) for the local cost, then both on a log scale.
NoiseFlattens       ThreeDScene: global depolarizing noise after each of L layers multiplies the whole
                    landscape by (1-p)^L; the surface sinks to a plane, at every point, not on average.
Numbers come from qcai/lessonfigs/l7_04.py and are checked against the lesson text by facts().
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DEGREES, DOWN, LEFT, PI, RIGHT, UP, Axes, Create, DashedLine, Dot, FadeIn, FadeOut, Line,
                   Rectangle, ReplacementTransform, Scene, Surface, ThreeDAxes, ThreeDScene, Transform,
                   TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label
from qcai.lessonfigs import l7_04 as M

# ---------------------------------------------------------------- shared numbers
HIST_NS = (2, 4, 6, 8)
HIST_DEPTH = 32            # layers L per circuit in the histogram scene (times n, see below)
HIST_SAMPLES = 600
SD_THEORY = {n: math.sqrt(M.var_local_2design(n)) for n in HIST_NS}     # 0.447, 0.243, 0.124, 0.0624
assert abs(SD_THEORY[2] - 1 / math.sqrt(5)) < 1e-12

G8 = M.SD_GLOBAL_8                    # typical global gradient at n = 8: 0.00276
N_RESOLVE_G8 = M.shots_to_resolve(M.var_global_2design(8))   # 65792
N_RESOLVE_L8 = M.shots_to_resolve(M.var_local_2design(8))    # 129
assert N_RESOLVE_G8 == 2 ** 8 * (2 ** 8 + 1)

VG3 = M.var_product_global(20)        # (1/8)(3/8)^19
VL3 = M.var_product_local(20)         # 1/3200
assert abs(VL3 - 1 / 3200) < 1e-15 and 1e-10 < VG3 < 1e-8

P_NOISE = 0.05
L_STEPS = (0, 10, 20, 40)
DAMP = {L: (1 - P_NOISE) ** L for L in L_STEPS}               # 1, 0.599, 0.358, 0.129
assert abs(DAMP[40] - 0.1285) < 1e-4


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [r"\frac{1}{2^n+1}", r"\frac{1}{2\cdot 2^n(2^n+1)}", "65,792", r"(3/8)^{n-1}", r"\frac{1}{8n^2}",
            r"(1-p)^L", "0.129"]


def depth_for(n: int) -> int:
    return HIST_DEPTH * n


def axes_with_labels(x_range, y_range, x_length, y_length, xticks, yticks, ylab=None, xfmt="{:g}", size=22):
    """Axes with tick labels in the course font (Manim's own numbers are white on white).
    ylab maps an axis value to its printed label (used for log scales stored with an offset)."""
    ax = Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length,
              axis_config={"color": MUTED, "include_tip": False})
    labs = VGroup()
    for x in xticks:
        labs.add(label(xfmt.format(x), size, MUTED).next_to(ax.c2p(x, y_range[0]), DOWN, buff=0.12))
    for y in yticks:
        labs.add(label((ylab or "{:g}".format)(y), size, MUTED).next_to(ax.c2p(x_range[0], y), LEFT, buff=0.12))
    return ax, labs


# ---- scene 1 ----------------------------------------------------------------------------------
class GradientHistograms(Scene):
    def construct(self):
        title = label("Random deep circuits: the gradient distribution collapses", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        ax, axl = axes_with_labels([-1, 1, 0.5], [0, 0.6, 0.2], 6.0, 4.0, [-1, -0.5, 0, 0.5, 1], [0.2, 0.4, 0.6])
        VGroup(ax, axl).move_to(LEFT * 3.0 + DOWN * 0.2)
        xl = eq(r"\partial_\theta \langle Z_0\rangle", size=30).next_to(ax.x_axis, DOWN, buff=0.5)
        yl = label("fraction of circuits", 22, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.7)
        self.play(Create(ax), FadeIn(axl), FadeIn(xl), FadeIn(yl))

        edges = np.linspace(-1, 1, 26)
        data = {}
        for n in HIST_NS:
            data[n] = M.simulate(n, depth_for(n), HIST_SAMPLES, seed=77 + n)

        def bars(n):
            h, _ = np.histogram(data[n][:, 0], bins=edges)
            frac = h / HIST_SAMPLES
            grp = VGroup()
            for k, f in enumerate(frac):
                x0, x1 = edges[k], edges[k + 1]
                hgt = max(f, 1e-4)
                r = Rectangle(width=ax.c2p(x1, 0)[0] - ax.c2p(x0, 0)[0], height=ax.c2p(0, hgt)[1] - ax.c2p(0, 0)[1],
                              fill_color=VIOLET, fill_opacity=0.65, stroke_color=INK, stroke_width=0.6)
                r.move_to(ax.c2p((x0 + x1) / 2, 0), aligned_edge=DOWN)
                grp.add(r)
            return grp

        # right: log variance against n
        rx, rxlab = axes_with_labels([1, 9, 1], [0, 6, 1], 4.4, 4.0, [2, 4, 6, 8], [0, 2, 4, 6], ylab=lambda y: f"{y - 6:g}")
        VGroup(rx, rxlab).move_to(RIGHT * 3.8 + DOWN * 0.2)

        def P(n, v):                      # log10 Var is stored with an offset of 6 so the x axis sits at the bottom
            return rx.c2p(n, math.log10(v) + 6)

        rxl = label("qubits n", 22, MUTED).next_to(rx.x_axis, DOWN, buff=0.5)
        ryl = eq(r"\log_{10}\operatorname{Var}", size=26).next_to(rx, UP, buff=0.15).align_to(rx, LEFT)
        self.play(Create(rx), FadeIn(rxlab), FadeIn(rxl), FadeIn(ryl))
        ns = np.linspace(1.6, 8.6, 60)
        tl = VGroup(*[Line(P(a, M.var_local_2design(a)), P(b, M.var_local_2design(b)), color=VIOLET, stroke_width=3)
                      for a, b in zip(ns[:-1], ns[1:])])
        tg = VGroup(*[Line(P(a, M.var_global_2design(a)), P(b, M.var_global_2design(b)), color=AMBER, stroke_width=3)
                      for a, b in zip(ns[:-1], ns[1:])])
        kl = eq(r"\frac{1}{2^n+1}", size=30, color=VIOLET).move_to(rx.c2p(7.2, 5.3))
        kg = eq(r"\frac{1}{2\cdot 2^n(2^n+1)}", size=30, color=AMBER).move_to(rx.c2p(3.3, 0.9))
        self.play(Create(tl), Create(tg), Write(kl), Write(kg), run_time=1.6)
        note = label("lines: exact 2-design prediction;  dots: our simulation", 22, MUTED).to_edge(DOWN, buff=0.12)
        self.play(FadeIn(note))

        cur = None
        tag = None
        for n in HIST_NS:
            b = bars(n)
            v_loc = float(data[n][:, 0].var(ddof=1))
            v_glo = float(data[n][:, 1].var(ddof=1))
            t = VGroup(eq(rf"n = {n},\ L = {depth_for(n)}", size=30),
                       eq(rf"\text{{s.d.}} = {math.sqrt(v_loc):.3f}", size=30, color=VIOLET)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            t.move_to(ax.c2p(0.55, 0.5))
            if cur is None:
                self.play(FadeIn(b), Write(t), run_time=1.2)
            else:
                self.play(Transform(cur, b), FadeOut(tag), FadeIn(t), run_time=1.4)
            if cur is None:
                cur = b
            tag = t
            d1 = Dot(P(n, v_loc), color=VIOLET, radius=0.08)
            d2 = Dot(P(n, v_glo), color=AMBER, radius=0.08)
            self.play(FadeIn(d1, scale=0.5), FadeIn(d2, scale=0.5), run_time=0.7)
            self.wait(0.6)
        self.wait(2)


# ---- scene 2 ----------------------------------------------------------------------------------
class ShotNoiseDetect(Scene):
    def construct(self):
        title = label("Can N shots tell a tiny gradient from zero?", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        setup = VGroup(eq(r"\hat g = \tfrac12(\bar z_+ - \bar z_-),\quad \operatorname{sd}(\hat g) \le \frac{1}{\sqrt{2N}}", size=32),
                       eq(rf"\text{{true gradient }} g = {G8:.5f}\ \ (\text{{global cost}},\ n = 8)", size=30, color=AMBER)
                       ).arrange(DOWN, buff=0.2).next_to(title, DOWN, buff=0.3)
        self.play(Write(setup[0]))
        self.play(Write(setup[1]))
        span = 0.02
        ax, axl = axes_with_labels([-span, span, 0.01], [0, 1.05, 0.5], 9.0, 2.7, [-0.02, -0.01, 0, 0.01, 0.02], [],
                                   xfmt="{:.2f}")
        VGroup(ax, axl).move_to(DOWN * 0.95)
        self.play(Create(ax), FadeIn(axl))
        logN = ValueTracker(2.0)
        xs = np.linspace(-span, span, 241)

        def curve(mu, color):
            def build():
                s = 1 / math.sqrt(2 * 10 ** logN.get_value())
                ys = np.exp(-0.5 * ((xs - mu) / s) ** 2)
                pts = [ax.c2p(x, y) for x, y in zip(xs, ys)]
                return VGroup(*[Line(a, b, color=color, stroke_width=4) for a, b in zip(pts[:-1], pts[1:])])
            return always_redraw(build)

        c0 = curve(0.0, BLUE)
        c1 = curve(G8, AMBER)
        k0 = label("if g = 0", 22, BLUE).move_to(ax.c2p(-0.0165, 0.72))
        k1 = label("if g = 0.00276", 22, AMBER).move_to(ax.c2p(0.0160, 0.72))
        self.play(Create(c0), Create(c1), FadeIn(k0), FadeIn(k1))
        readout = always_redraw(lambda: label(f"N = {int(round(10 ** logN.get_value())):,} shots per shift",
                                              28, INK).to_corner(DOWN + LEFT, buff=0.3))
        self.add(readout)
        self.play(logN.animate.set_value(math.log10(N_RESOLVE_G8)), run_time=7, rate_func=linear)
        mark = eq(r"N \approx \frac{1}{2\operatorname{Var}} = 2^n(2^n+1) = 65{,}792", size=30, color=RED).to_corner(DOWN + RIGHT, buff=0.3)
        self.play(Write(mark))
        self.wait(0.8)
        self.play(logN.animate.set_value(6.0), run_time=3, rate_func=linear)
        self.wait(0.5)
        self.remove(readout)
        fin = eq(rf"\text{{local cost at }} n = 8:\ N \approx {N_RESOLVE_L8}\qquad \text{{global cost: }} 65{{,}}792", size=30)
        fin.to_corner(DOWN + LEFT, buff=0.3)
        self.play(FadeOut(mark), FadeIn(fin))
        msg = label("one standard deviation only; a reliable sign needs several times more", 22, MUTED).next_to(fin, UP, buff=0.15).align_to(fin, LEFT)
        self.play(FadeIn(msg))
        self.wait(2)
        _ = (DashedLine, Dot)


# ---- scene 3 ----------------------------------------------------------------------------------
class LocalVersusGlobal(Scene):
    def construct(self):
        title = label("Same circuit, two costs: global versus local", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        ans = eq(r"|\psi\rangle = \textstyle\bigotimes_{j=1}^{n} R_Y(\theta_j)|0\rangle", size=34).next_to(title, DOWN, buff=0.25)
        self.play(Write(ans))
        g1 = eq(r"C_G = 1 - \prod_{j} \cos^2\tfrac{\theta_j}{2}", size=34, color=AMBER)
        g2 = eq(r"\partial_1 C_G = \tfrac12 \sin\theta_1 \prod_{j \ge 2} \cos^2\tfrac{\theta_j}{2}", size=34, color=AMBER)
        g3 = eq(r"\operatorname{Var} = \tfrac14 \cdot \tfrac12 \cdot \left(\tfrac38\right)^{n-1}", size=34, color=AMBER)
        g4 = eq(r"\operatorname{Var}\,\partial_1 C_G = \tfrac18 (3/8)^{n-1}", size=34, color=AMBER)
        l1 = eq(r"C_L = 1 - \tfrac1n \sum_{j} \cos^2\tfrac{\theta_j}{2}", size=34, color=VIOLET)
        l2 = eq(r"\partial_1 C_L = \tfrac{1}{2n} \sin\theta_1", size=34, color=VIOLET)
        l4 = eq(r"\operatorname{Var}\,\partial_1 C_L = \frac{1}{8n^2}", size=34, color=VIOLET)
        for m in (g1, g2, g3, g4):
            m.move_to(LEFT * 3.3 + UP * 1.0)
        for m in (l1, l2, l4):
            m.move_to(RIGHT * 3.3 + UP * 1.0)
        self.play(Write(g1), Write(l1))
        self.wait(0.5)
        self.play(TransformMatchingTex(g1, g2), TransformMatchingTex(l1, l2), run_time=1.5)
        facts_line = eq(r"\mathbb{E}\sin^2\theta = \tfrac12,\qquad \mathbb{E}\cos^4\tfrac{\theta}{2} = \tfrac38", size=30, color=MUTED).move_to(UP * 0.1)
        self.play(FadeIn(facts_line))
        self.play(TransformMatchingTex(g2, g3), run_time=1.4)
        self.play(TransformMatchingTex(g3, g4), TransformMatchingTex(l2, l4), run_time=1.4)
        self.wait(0.6)
        self.play(FadeOut(facts_line), FadeOut(ans))
        self.play(g4.animate.scale(0.85).move_to(LEFT * 3.4 + UP * 2.2), l4.animate.scale(0.85).move_to(RIGHT * 3.4 + UP * 2.2))

        ax, axl = axes_with_labels([0, 21, 5], [0, 10, 2], 8.5, 3.3, [5, 10, 15, 20], [0, 2, 4, 6, 8, 10],
                                   ylab=lambda y: f"{y - 10:g}")
        VGroup(ax, axl).move_to(DOWN * 0.95 + LEFT * 0.3)

        def P(n, v):                      # log10 Var stored with offset 10
            return ax.c2p(n, math.log10(v) + 10)

        xl = label("qubits n", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = eq(r"\log_{10}\operatorname{Var}", size=26).next_to(ax, UP, buff=0.1).align_to(ax, LEFT).shift(LEFT * 0.4)
        self.play(Create(ax), FadeIn(axl), FadeIn(xl), FadeIn(yl))
        t = ValueTracker(1.0)

        def trace(fun, color):
            def build():
                ns = np.linspace(1, max(t.get_value(), 1.0001), 80)
                pts = [P(x, fun(x)) for x in ns]
                return VGroup(*[Line(a, b, color=color, stroke_width=4) for a, b in zip(pts[:-1], pts[1:])])
            return always_redraw(build)

        tg, tl = trace(M.var_product_global, AMBER), trace(M.var_product_local, VIOLET)
        self.add(tg, tl)
        self.play(t.animate.set_value(20), run_time=5, rate_func=linear)
        endg = label(f"n = 20: {VG3:.1e}", 22, AMBER).next_to(P(20, VG3), RIGHT, buff=0.15)
        endl = label(f"n = 20: {VL3:.1e}", 22, VIOLET).next_to(P(20, VL3), RIGHT, buff=0.15)
        self.play(FadeIn(endg), FadeIn(endl))
        moral = label("no entanglement at all, yet the global cost has a barren plateau", 24, RED).to_edge(DOWN, buff=0.15)
        self.play(FadeIn(moral))
        self.wait(2)


# ---- scene 4 ----------------------------------------------------------------------------------
class NoiseFlattens(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(x_range=[-PI, PI, PI / 2], y_range=[-PI, PI, PI / 2], z_range=[-1, 1, 0.5], x_length=5.6,
                          y_length=5.6, z_length=2.8, axis_config={"color": MUTED, "include_tip": False})
        self.set_camera_orientation(phi=64 * DEGREES, theta=-48 * DEGREES, zoom=0.85)
        title = label("Depolarizing noise squashes the whole landscape", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Create(axes), Write(title), run_time=1.5)
        amp = ValueTracker(1.0)

        def surf():
            a = amp.get_value()
            s = Surface(lambda u, v: axes.c2p(u, v, a * math.cos(u) * math.cos(v)), u_range=[-PI, PI], v_range=[-PI, PI],
                        resolution=(18, 18), fill_opacity=0.6, stroke_width=0.4, stroke_color=GRID)
            s.set_fill_by_value(axes=axes, colorscale=[(BLUE, -1.0), (CYAN, 0.0), (AMBER, 1.0)], axis=2)
            return s

        sf = always_redraw(surf)
        self.add(sf)
        info = VGroup(eq(r"E_L(\theta) = (1-p)^L\, E_0(\theta) + \big(1 - (1-p)^L\big)\tfrac{\operatorname{Tr} H}{2^n}", size=30),
                      eq(r"\nabla E_L = (1-p)^L\, \nabla E_0", size=30, color=RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        info.to_corner(DOWN + LEFT, buff=0.3)
        self.add_fixed_in_frame_mobjects(info)
        self.remove(info)
        self.play(FadeIn(info[0]))
        self.play(FadeIn(info[1]))
        e0 = eq(r"E_0 = \langle Z_1 Z_2\rangle = \cos\theta_1\cos\theta_2", size=30, color=MUTED).to_corner(UP + RIGHT, buff=0.3).shift(DOWN * 0.7)
        self.add_fixed_in_frame_mobjects(e0)
        self.remove(e0)
        self.play(FadeIn(e0))
        tag = None
        for L in L_STEPS[1:]:
            new = eq(rf"p = 0.05,\ L = {L}:\ (1-p)^L = {DAMP[L]:.3f}", size=30, color=VIOLET).to_corner(DOWN + RIGHT, buff=0.35).shift(UP * 0.9)
            self.add_fixed_in_frame_mobjects(new)
            self.remove(new)
            anims = [amp.animate.set_value(DAMP[L])]
            if tag is not None:
                anims.append(FadeOut(tag))
            self.play(*anims, FadeIn(new), run_time=2.2)
            tag = new
            self.wait(0.4)
        tail = label("at every θ, not only on average: no initialization escapes it", 22, RED).to_corner(DOWN + RIGHT, buff=0.35)
        self.add_fixed_in_frame_mobjects(tail)
        self.remove(tail)
        self.play(FadeIn(tail))
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(3)
        self.stop_ambient_camera_rotation()
        _ = (linear, RIGHT, LEFT, UP, CYAN)
