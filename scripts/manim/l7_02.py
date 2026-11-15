"""L7-02 Variational circuits and parameter-shift gradients: four scenes.

ShiftRuleDerivation  U = cos(t/2) I - i sin(t/2) P, so f = a + b cos t + c sin t, and half the difference
                     of two shifted values is exactly f'(t); then the chord is NOT the tangent (slope 2/pi f').
BlochShift           Ry(t)|0> on the Bloch sphere: f = <Z> is the height; the two shifted states sit a
                     quarter turn either side and half their height difference is the slope.
ShotNoiseHistograms  2000 repeated gradient estimates at t = pi/6 with N shots per setting: parameter
                     shift versus a central difference with h = 0.1, as N grows 100 -> 1000 -> 10000.
LossLandscape3D      the regression loss of the two-parameter re-uploading model over (t0, t1), with a
                     gradient-descent path driven by exact parameter-shift gradients.
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DEGREES, DOWN, LEFT, ORIGIN, OUT, PI, RIGHT, UP, Arrow3D, Axes, Create, DashedLine, DecimalNumber,
                   Dot, Dot3D, FadeIn, FadeOut, Line, ParametricFunction, Rectangle, Scene, Sphere, Surface,
                   ThreeDAxes, ThreeDScene, TransformMatchingTex, Transform, ValueTracker, VGroup, Write,
                   always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label
from qcai import science as s

# ---------------------------------------------------------------- shared numbers
TH = PI / 6                                    # the worked point
F = math.cos                                   # f(theta) = <Z> after Ry(theta)|0>
FP, FM = F(TH + PI / 2), F(TH - PI / 2)        # -1/2 and +1/2
PS = (FP - FM) / 2                             # -1/2
assert abs(FP + 0.5) < 1e-12 and abs(FM - 0.5) < 1e-12 and abs(PS + 0.5) < 1e-12 and abs(PS + math.sin(TH)) < 1e-12
CHORD = (FP - FM) / PI                         # -1/pi, the secant slope
assert abs(CHORD - 2 / PI * PS) < 1e-12

H = 0.1                                        # finite-difference step
VPS = ((1 - FP ** 2) + (1 - FM ** 2)) / 4      # N * Var(parameter shift) = 0.375
VFD = ((1 - F(TH + H) ** 2) + (1 - F(TH - H) ** 2)) / (4 * H * H)   # N * Var(finite difference) = 12.75
assert abs(VPS - 0.375) < 1e-12 and abs(VFD - 12.749) < 1e-3
NS = (100, 1000, 10000)
SD_PS = [math.sqrt(VPS / n) for n in NS]       # 0.061, 0.019, 0.006
SD_FD = [math.sqrt(VFD / n) for n in NS]       # 0.357, 0.113, 0.036
REPS = 2000

# loss landscape (same model and data as lab 8)
THETA_STAR = np.array([1.1, 0.7])
XS = np.linspace(-PI, PI, 15)
YS = np.array([s.vqc_expectation(THETA_STAR, x) for x in XS])


def loss(t):
    return float(np.mean([(s.vqc_expectation(t, x) - y) ** 2 for x, y in zip(XS, YS)]))


def loss_grad(t):
    return sum(2 * (s.vqc_expectation(t, x) - y) * s.vqc_gradient(t, x) for x, y in zip(XS, YS)) / len(XS)


def gd_path(start=(0.3, -2.2), lr=0.4, steps=80):
    t = np.array(start, dtype=float)
    out = [t.copy()]
    for _ in range(steps):
        t = t - lr * loss_grad(t)
        out.append(t.copy())
    return np.array(out)


SETTINGS_PER_STEP = 2 * 2 * len(XS)            # 2 parameters x 2 shifts x 15 inputs = 60
assert SETTINGS_PER_STEP == 60


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["a + b\\cos\\theta + c\\sin\\theta", "-b\\sin\\theta + c\\cos\\theta", "\\tfrac{2}{\\pi}",
            f"{SD_PS[0]:.3f}", f"{SD_FD[0]:.3f}", f"{SD_PS[2]:.4f}", "60 circuit settings"]


# ================================================================ scene 1
class ShiftRuleDerivation(Scene):
    def construct(self):
        title = label("Why two shifted circuits give an exact derivative", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.2)

        gate = eq(r"U(\theta) = e^{-i\theta P/2}", "=", r"\cos\tfrac{\theta}{2}\, I - i\sin\tfrac{\theta}{2}\, P", size=38)
        cond = eq(r"P^2 = I", size=34, color=VIOLET)
        gate.move_to(UP * 2.1)
        cond.next_to(gate, RIGHT, buff=0.5)
        if cond.get_right()[0] > 6.6:
            VGroup(gate, cond).arrange(RIGHT, buff=0.5).move_to(UP * 2.1)
        self.play(Write(gate), FadeIn(cond))

        line1 = eq(r"f(\theta)", "=", r"\langle\psi|\, U(\theta)^\dagger A\, U(\theta)\,|\psi\rangle", size=38)
        line1.move_to(UP * 0.9)
        self.play(Write(line1))
        line2 = eq(r"f(\theta)", "=", r"\cos^2\tfrac{\theta}{2}\langle A\rangle", "+",
                   r"\sin^2\tfrac{\theta}{2}\langle PAP\rangle", "+", r"\tfrac{1}{2}\sin\theta\,\langle i[P,A]\rangle", size=36)
        line2.move_to(UP * 0.9)
        self.play(TransformMatchingTex(line1, line2), run_time=1.8)
        self.wait(0.6)
        line3 = eq(r"f(\theta)", "=", "a", "+", r"b\cos\theta", "+", r"c\sin\theta", size=40, color=INK)
        line3.move_to(UP * 0.9)
        self.play(TransformMatchingTex(line2, line3), run_time=1.6)
        coeffs = eq(r"a = \tfrac{1}{2}\langle A + PAP\rangle,\quad b = \tfrac{1}{2}\langle A - PAP\rangle,\quad c = \tfrac{1}{2}\langle i[P,A]\rangle",
                    size=30, color=MUTED).next_to(line3, DOWN, buff=0.3)
        self.play(FadeIn(coeffs))
        self.wait(1.0)

        shift = eq(r"\tfrac{1}{2}\big[f(\theta+\tfrac{\pi}{2}) - f(\theta-\tfrac{\pi}{2})\big]", "=",
                   r"\tfrac{1}{2}\big[-2b\sin\theta + 2c\cos\theta\big]", size=38).move_to(DOWN * 1.3)
        self.play(Write(shift), run_time=1.6)
        shift2 = eq(r"\tfrac{1}{2}\big[f(\theta+\tfrac{\pi}{2}) - f(\theta-\tfrac{\pi}{2})\big]", "=",
                    r"-b\sin\theta + c\cos\theta", "=", r"f'(\theta)", size=38).move_to(DOWN * 1.3)
        self.play(TransformMatchingTex(shift, shift2), run_time=1.6)
        box = Rectangle(width=shift2.width + 0.4, height=shift2.height + 0.35, color=AMBER).move_to(shift2)
        note = label("exact identity: no small step, no Taylor remainder", 26, MUTED).next_to(box, DOWN, buff=0.25)
        self.play(Create(box), FadeIn(note))
        self.wait(1.8)
        self.play(FadeOut(VGroup(gate, cond, line3, coeffs, shift2, box, note)))

        # ---- phase 2: the chord is not the tangent
        ax = Axes(x_range=[-PI / 2, 3 * PI / 2 + 0.2, PI / 2], y_range=[-1.2, 1.2, 0.5], x_length=7.0, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(LEFT * 2.6 + DOWN * 0.45)
        curve = ax.plot(np.cos, x_range=[-PI / 2, 3 * PI / 2 + 0.2], color=VIOLET, stroke_width=4)
        flab = eq(r"f(\theta) = \cos\theta", size=32, color=VIOLET).move_to(RIGHT * 3.9 + UP * 2.6)
        self.play(Create(ax), Create(curve), Write(flab), run_time=1.6)
        th = ValueTracker(TH)

        def pts():
            t = th.get_value()
            return t, ax.c2p(t - PI / 2, F(t - PI / 2)), ax.c2p(t + PI / 2, F(t + PI / 2)), ax.c2p(t, F(t))

        dots = always_redraw(lambda: VGroup(Dot(pts()[1], color=BLUE, radius=0.08), Dot(pts()[2], color=BLUE, radius=0.08),
                                            Dot(pts()[3], color=RED, radius=0.08)))
        chord = always_redraw(lambda: Line(pts()[1], pts()[2], color=BLUE, stroke_width=3))

        def tangent():
            t = th.get_value()
            d = -math.sin(t)
            return Line(ax.c2p(t - 0.9, F(t) - 0.9 * d), ax.c2p(t + 0.9, F(t) + 0.9 * d), color=RED, stroke_width=5)

        tan = always_redraw(tangent)
        self.play(FadeIn(dots), Create(chord), Create(tan))
        info = VGroup(
            eq(r"\theta = \pi/6", size=32),
            eq(r"f(\theta + \tfrac{\pi}{2}) = -\tfrac{1}{2},\ \ f(\theta - \tfrac{\pi}{2}) = \tfrac{1}{2}", size=30, color=BLUE),
            eq(r"\text{half difference} = -\tfrac{1}{2} = f'(\pi/6)", size=30, color=RED),
            eq(r"\text{chord slope} = -\tfrac{1}{\pi} = \tfrac{2}{\pi}\, f'(\theta)", size=30, color=BLUE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(RIGHT * 3.9 + UP * 0.9)
        for m in info:
            self.play(FadeIn(m), run_time=0.8)
        self.wait(1.2)
        live_lab = label("shift rule", 26, BLUE)
        live = DecimalNumber(PS, num_decimal_places=3, include_sign=True, color=BLUE, font_size=34)
        der_lab = label("f'(θ)", 26, RED)
        der = DecimalNumber(-math.sin(TH), num_decimal_places=3, include_sign=True, color=RED, font_size=34)
        live.add_updater(lambda m: m.set_value((F(th.get_value() + PI / 2) - F(th.get_value() - PI / 2)) / 2))
        der.add_updater(lambda m: m.set_value(-math.sin(th.get_value())))
        rows = VGroup(VGroup(live_lab, live).arrange(RIGHT, buff=0.3), VGroup(der_lab, der).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(RIGHT * 3.9 + DOWN * 1.9)
        self.play(FadeIn(rows))
        self.play(th.animate.set_value(PI * 0.95), run_time=5, rate_func=linear)
        self.play(th.animate.set_value(PI / 6), run_time=3)
        self.wait(1.5)
        _ = (DashedLine, ORIGIN, Transform)


# ================================================================ scene 2
class BlochShift(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=72 * DEGREES, theta=-60 * DEGREES, zoom=0.95)
        axes = ThreeDAxes(x_range=[-1.4, 1.4, 1], y_range=[-1.4, 1.4, 1], z_range=[-1.4, 1.4, 1], x_length=4.6,
                          y_length=4.6, z_length=4.6, axis_config={"color": MUTED, "include_tip": False})
        sph = Sphere(radius=2.0, resolution=(18, 18)).set_fill(CYAN, opacity=0.07).set_stroke(GRID, width=0.5)
        sc = 2.0
        circle = ParametricFunction(lambda t: np.array([sc * math.sin(t), 0, sc * math.cos(t)]), t_range=[0, 2 * PI],
                                    color=MUTED, stroke_width=2)
        title = label("Ry(θ)|0⟩ on the Bloch sphere: f(θ) = ⟨Z⟩ is the height", 30, INK, "BOLD").to_edge(UP, buff=0.3)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Create(axes), FadeIn(sph), Create(circle), Write(title), run_time=1.8)
        zl = eq("|0\\rangle", size=34, color=INK)
        zl1 = eq("|1\\rangle", size=34, color=INK)
        self.add_fixed_in_frame_mobjects(zl, zl1)
        zl.move_to(UP * 2.75 + LEFT * 0.35)
        zl1.move_to(DOWN * 2.95 + LEFT * 0.35)
        self.play(FadeIn(zl), FadeIn(zl1))

        th = ValueTracker(0.0)

        def vec(t):
            return np.array([sc * math.sin(t), 0, sc * math.cos(t)])

        state = always_redraw(lambda: Arrow3D(ORIGIN, vec(th.get_value()), color=VIOLET, thickness=0.03))
        self.play(FadeIn(state))
        self.play(th.animate.set_value(TH), run_time=1.5)
        plus = Arrow3D(ORIGIN, vec(TH + PI / 2), color=BLUE, thickness=0.025)
        minus = Arrow3D(ORIGIN, vec(TH - PI / 2), color=BLUE, thickness=0.025)
        self.play(FadeIn(plus), FadeIn(minus))
        hp = DashedLine(vec(TH + PI / 2), np.array([0, 0, vec(TH + PI / 2)[2]]), color=BLUE)
        hm = DashedLine(vec(TH - PI / 2), np.array([0, 0, vec(TH - PI / 2)[2]]), color=BLUE)
        self.play(Create(hp), Create(hm))
        panel = VGroup(
            eq(r"\theta = \pi/6:\ \ f = \cos\theta", size=32),
            eq(r"\text{shifted heights: } -\tfrac{1}{2},\ +\tfrac{1}{2}", size=30, color=BLUE),
            eq(r"\tfrac{1}{2}\left(-\tfrac{1}{2} - \tfrac{1}{2}\right) = -\tfrac{1}{2} = -\sin\tfrac{\pi}{6}", size=30, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_corner(RIGHT + DOWN, buff=0.45)
        self.add_fixed_in_frame_mobjects(panel)
        for m in panel:
            self.play(FadeIn(m), run_time=0.9)
        note = VGroup(label("the shifted states sit a quarter", 24, MUTED), label("turn on either side of the state", 24, MUTED)
                      ).arrange(DOWN, aligned_edge=RIGHT, buff=0.08).next_to(panel, UP, buff=0.3).align_to(panel, RIGHT)
        self.add_fixed_in_frame_mobjects(note)
        self.play(FadeIn(note))
        self.wait(1.0)
        self.move_camera(theta=-100 * DEGREES, run_time=4)
        self.wait(1.5)
        _ = (Dot3D, OUT)


# ================================================================ scene 3
def _estimates(n, seed):
    g = np.random.default_rng(seed)

    def fhat(t):
        p0 = (1 + F(t)) / 2
        return 2 * g.binomial(n, p0, size=REPS) / n - 1
    ps = 0.5 * (fhat(TH + PI / 2) - fhat(TH - PI / 2))
    fd = (fhat(TH + H) - fhat(TH - H)) / (2 * H)
    return ps, fd


class ShotNoiseHistograms(Scene):
    def construct(self):
        title = label("Same shot budget, very different spread", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        lo, hi, bw = -1.7, 0.7, 0.04
        edges = np.arange(lo, hi + 1e-9, bw)
        ax = Axes(x_range=[lo, hi, 0.5], y_range=[0, 1, 0.25], x_length=10.5, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(DOWN * 0.7)
        nums = VGroup(*[eq(f"{v:.1f}" if v else "0", size=26, color=MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.15)
                        for v in (-1.5, -1.0, -0.5, 0.0, 0.5)])
        xl = label("gradient estimate", 24, MUTED).next_to(ax, DOWN, buff=0.55)
        true = DashedLine(ax.c2p(-0.5, 0), ax.c2p(-0.5, 1.0), color=INK)
        tl = eq(r"f'(\pi/6) = -\tfrac{1}{2}", size=30).next_to(true, UP, buff=0.08)
        self.play(Create(ax), FadeIn(nums), FadeIn(xl), Create(true), Write(tl))

        def bars(vals, color, peak):
            cnt, _ = np.histogram(vals, bins=edges)
            grp = VGroup()
            for c, e0 in zip(cnt, edges[:-1]):
                hgt = c / peak
                if hgt <= 0:
                    continue
                r = Rectangle(width=ax.c2p(e0 + bw, 0)[0] - ax.c2p(e0, 0)[0], height=max(hgt * 4.2 * 0.95, 0.001),
                              stroke_width=0.5, stroke_color=color).set_fill(color, opacity=0.55)
                r.move_to(ax.c2p(e0 + bw / 2, 0), aligned_edge=DOWN)
                grp.add(r)
            return grp

        legend = VGroup(VGroup(Rectangle(width=0.35, height=0.25).set_fill(VIOLET, 0.6).set_stroke(VIOLET),
                               label("parameter shift", 24, VIOLET)).arrange(RIGHT, buff=0.15),
                        VGroup(Rectangle(width=0.35, height=0.25).set_fill(AMBER, 0.6).set_stroke(AMBER),
                               label("central difference, h = 0.1", 24, AMBER)).arrange(RIGHT, buff=0.15)
                        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(LEFT + UP, buff=0.5).shift(DOWN * 0.65)
        self.play(FadeIn(legend))
        cur_ps = cur_fd = cur_txt = None
        for i, n in enumerate(NS):
            ps, fd = _estimates(n, 70 + i)
            assert abs(ps.std() - SD_PS[i]) / SD_PS[i] < 0.08 and abs(fd.std() - SD_FD[i]) / SD_FD[i] < 0.08
            peak = max(np.histogram(ps, bins=edges)[0].max(), 1)
            b_ps, b_fd = bars(ps, VIOLET, peak), bars(fd, AMBER, peak)
            txt = VGroup(label(f"N = {n} shots per setting, {REPS} repeats", 26, INK),
                         eq(rf"\text{{sd: shift }} {SD_PS[i]:.4f}\ \ \text{{vs}}\ \ \text{{difference }} {SD_FD[i]:.3f}" if i == 2 else
                            rf"\text{{sd: shift }} {SD_PS[i]:.3f}\ \ \text{{vs}}\ \ \text{{difference }} {SD_FD[i]:.3f}", size=30)
                         ).arrange(DOWN, aligned_edge=RIGHT, buff=0.12).to_corner(RIGHT + UP, buff=0.5).shift(DOWN * 0.6)
            if cur_ps is None:
                self.play(FadeIn(b_fd), FadeIn(b_ps), FadeIn(txt), run_time=1.5)
            else:
                self.play(Transform(cur_fd, b_fd), Transform(cur_ps, b_ps), Transform(cur_txt, txt), run_time=1.8)
                b_ps, b_fd, txt = cur_ps, cur_fd, cur_txt
            cur_ps, cur_fd, cur_txt = b_ps, b_fd, txt
            self.wait(2.2)
        ratio = math.sqrt(VFD / VPS)
        concl = eq(rf"\text{{at equal shots the difference has }} {ratio:.1f}\times \text{{ the spread}}", size=30, color=RED)
        concl.to_corner(RIGHT + UP, buff=0.5).shift(DOWN * 0.75)
        self.play(FadeOut(cur_txt), FadeIn(concl))
        self.wait(2.5)


# ================================================================ scene 4
class LossLandscape3D(ThreeDScene):
    def construct(self):
        path = gd_path()
        assert loss(path[-1]) < 1e-6 < loss(path[0])
        zs = 1.1
        axes = ThreeDAxes(x_range=[-PI, PI, PI / 2], y_range=[-PI, PI, PI / 2], z_range=[0, 2.2, 1], x_length=6.0,
                          y_length=6.0, z_length=2.2 * zs, axis_config={"color": MUTED, "include_tip": False})
        self.set_camera_orientation(phi=62 * DEGREES, theta=-50 * DEGREES, zoom=0.82)
        surf = Surface(lambda u, v: axes.c2p(u, v, loss((u, v)) * zs / zs), u_range=[-PI, PI], v_range=[-PI, PI],
                       resolution=(22, 22), fill_opacity=0.55, stroke_width=0.4, stroke_color=GRID)
        surf.set_fill_by_value(axes=axes, colorscale=[(BLUE, 0.0), (CYAN, 0.6), (AMBER, 1.4), (RED, 2.1)], axis=2)
        title = label("Loss landscape and descent with parameter-shift gradients", 30, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Create(axes), Write(title), run_time=1.5)
        self.play(FadeIn(surf), run_time=2.0)
        axes_note = VGroup(eq(r"\theta_0, \theta_1 \in [-\pi, \pi]", size=30, color=MUTED), label("height: loss", 24, MUTED)
                           ).arrange(DOWN, aligned_edge=RIGHT, buff=0.1).to_corner(RIGHT + UP, buff=0.4).shift(DOWN * 0.6)
        self.add_fixed_in_frame_mobjects(axes_note)
        self.play(FadeIn(axes_note))
        info = VGroup(
            eq(r"L(\theta) = \tfrac{1}{15}\sum_j \big(f_\theta(x_j) - y_j\big)^2", size=30),
            eq(r"\partial_k L = \tfrac{2}{15}\sum_j (f_\theta(x_j) - y_j)\,\partial_k f_\theta(x_j)", size=30),
            label(f"{SETTINGS_PER_STEP} circuit settings per step", 24, VIOLET),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).to_corner(LEFT + DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(info)
        self.play(FadeIn(info[0]), FadeIn(info[1]))
        self.play(FadeIn(info[2]))

        pts = [axes.c2p(p[0], p[1], loss(p) + 0.03) for p in path]
        ball = Dot3D(pts[0], color=RED, radius=0.13)
        self.play(FadeIn(ball))
        idx = list(range(0, 25)) + list(range(25, len(pts), 5)) + [len(pts) - 1]
        trail = VGroup()
        self.add(trail)
        for a, b in zip(idx[:-1], idx[1:]):
            seg = Line(pts[a], pts[b], color=RED, stroke_width=7)
            trail.add(seg)
            self.play(ball.animate.move_to(pts[b]), Create(seg), run_time=0.18, rate_func=linear)
        readout = VGroup(label(f"loss {loss(path[0]):.3f} → {loss(path[-1]):.0e} in 80 steps", 24, INK),
                         label(f"ends at θ = ({path[-1][0]:.2f}, {path[-1][1]:.2f}), a symmetric copy of θ* = (1.1, 0.7)", 22, MUTED)
                         ).arrange(DOWN, aligned_edge=RIGHT, buff=0.12).to_corner(RIGHT + DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(readout)
        self.play(FadeIn(readout))
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(4)
        self.stop_ambient_camera_rotation()
        self.wait(1)
        _ = (always_redraw, ValueTracker, DecimalNumber)
