"""L5-09 Entropy and quantum tomography: three scenes.

EntropyAlongRadius   a state slides from the pure surface of a Bloch-ball slice to the center; eigenvalue bars
                     even out and S = h((1 + |r|)/2) is traced live; at |r| = 0.6 the state circles and S stays 0.722.
TomographyConverges  3-D Bloch sphere: clouds of linear-inversion estimates for N = 10, 100, 1000, 10000 shots per
                     basis shrink onto the true vector like sqrt(2.17 / N).
ProjectBackToBall    the worked-example estimate (0.86, 0, 0.6) lies outside the ball with eigenvalue -0.0243; it is
                     projected radially; then a cloud of estimates for a nearly pure state is projected together.
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, ORIGIN, OUT, PI, RIGHT, UP, Arrow, Arrow3D, Axes, Circle, Create, DashedLine,
                   DecimalNumber, Dot, Dot3D, FadeIn, FadeOut, Line, Rectangle, Scene, Surface, ThreeDScene, TracedPath,
                   Transform, ValueTracker, VGroup, Write, always_redraw, linear, smooth)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, VIOLET_LIGHT, eq, label


def h2(q):
    """Binary entropy in bits."""
    if q <= 0 or q >= 1:
        return 0.0
    return -q * math.log2(q) - (1 - q) * math.log2(1 - q)


def S_of_r(r):
    return h2((1 + r) / 2)


R_MID = 0.6
S_MID = S_of_r(R_MID)                                   # 0.7219
assert abs(S_MID - 0.7219) < 1e-4

R_TRUE = np.array([0.5, 0.3, 0.7])
MSE_NUM = 3 - float(R_TRUE @ R_TRUE)                    # 2.17
assert abs(MSE_NUM - 2.17) < 1e-12
RMS = {n: math.sqrt(MSE_NUM / n) for n in (10, 100, 1000, 10000)}
RMS_TXT = {10: "0.466", 100: "0.147", 1000: "0.0466", 10000: "0.0147"}
for n, t in RMS_TXT.items():
    assert f"{RMS[n]:.{len(t) - 2}f}" == t, (n, RMS[n], t)

COUNTS, NW = np.array([186, 100, 160]), 200             # worked example
R_HAT = 2 * COUNTS / NW - 1                             # (0.86, 0, 0.6)
LEN_HAT = float(np.linalg.norm(R_HAT))                  # 1.0486
LAM = ((1 + LEN_HAT) / 2, (1 - LEN_HAT) / 2)            # 1.0243, -0.0243
R_PROJ = R_HAT / LEN_HAT                                # (0.820, 0, 0.572)
assert f"{LEN_HAT:.4f}" == "1.0486" and f"{LAM[0]:.4f}" == "1.0243" and f"{LAM[1]:.4f}" == "-0.0243"
assert f"{R_PROJ[0]:.3f}" == "0.820" and f"{R_PROJ[2]:.3f}" == "0.572"


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["0.722", "0 bits", "1 bit", "2.17", "0.147", "0.0466", "1.0486", "-0.0243", "0.820", "0.572"]


class EntropyAlongRadius(Scene):
    def construct(self):
        title = label("Entropy depends only on the distance from the center", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.2)

        # Bloch-ball slice (x horizontal, z vertical)
        c0, R = np.array([-4.55, -0.45, 0]), 1.85
        disk = Circle(radius=R, color=VIOLET, stroke_width=3).move_to(c0)
        disk.set_fill(VIOLET_LIGHT, opacity=0.12)
        axes2 = VGroup(Line(c0 + LEFT * (R + 0.2), c0 + RIGHT * (R + 0.2), color=GRID, stroke_width=2),
                       Line(c0 + DOWN * (R + 0.2), c0 + UP * (R + 0.2), color=GRID, stroke_width=2))
        xl = eq("x", size=30, color=MUTED).next_to(c0 + RIGHT * (R + 0.2), RIGHT, buff=0.08)
        zl = eq("z", size=30, color=MUTED).next_to(c0 + UP * (R + 0.2), UP, buff=0.05)
        self.play(Create(axes2), Create(disk), FadeIn(xl), FadeIn(zl))

        r = ValueTracker(1.0)
        ang = ValueTracker(50 * DEGREES)

        def pos():
            a = ang.get_value()
            return c0 + R * r.get_value() * np.array([math.cos(a), math.sin(a), 0])

        radius = always_redraw(lambda: Line(c0, pos(), color=VIOLET, stroke_width=4))
        dot = always_redraw(lambda: Dot(pos(), color=VIOLET, radius=0.1))
        self.play(Create(radius), FadeIn(dot))

        # eigenvalue bars
        base_y, scale = -2.35, 3.2
        xs = (-1.75, -0.85)

        def bar(i):
            lam = (1 + r.get_value()) / 2 if i == 0 else (1 - r.get_value()) / 2
            hgt = max(lam * scale, 0.001)
            return Rectangle(width=0.55, height=hgt, stroke_width=0, fill_color=(BLUE if i == 0 else CYAN),
                             fill_opacity=0.9).move_to([xs[i], base_y + hgt / 2, 0])

        bars = VGroup(always_redraw(lambda: bar(0)), always_redraw(lambda: bar(1)))
        floor = Line([xs[0] - 0.45, base_y, 0], [xs[1] + 0.45, base_y, 0], color=MUTED, stroke_width=2)
        blabs = VGroup(eq(r"\lambda_+", size=32, color=BLUE).move_to([xs[0], base_y - 0.35, 0]),
                       eq(r"\lambda_-", size=32, color=CYAN).move_to([xs[1], base_y - 0.35, 0]))
        lamform = eq(r"\lambda_\pm = (1 \pm |\vec r|)/2", size=30).move_to([-1.3, 2.55, 0])
        self.play(Create(floor), FadeIn(bars), Write(blabs), Write(lamform))

        # entropy against Bloch length
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=4.3, y_length=3.3,
                  axis_config={"color": MUTED, "include_tip": False}).move_to([3.95, -0.45, 0])
        ticks = VGroup(*[label(t, 22, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.12) for v, t in ((0, "0"), (0.5, "0.5"), (1, "1"))],
                       *[label(t, 22, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.12) for v, t in ((0.5, "0.5"), (1, "1"))])
        axx = eq(r"|\vec r|", size=30).next_to(ax.x_axis, DOWN, buff=0.5)
        axy = label("S (bits)", 24, MUTED).next_to(ax.y_axis, UP, buff=0.15)
        form = eq(r"S = h\!\left(\tfrac{1 + |\vec r|}{2}\right)", size=34, color=RED).move_to([4.1, 2.45, 0])
        self.play(Create(ax), FadeIn(ticks), FadeIn(axx), FadeIn(axy), Write(form))
        gdot = always_redraw(lambda: Dot(ax.c2p(r.get_value(), S_of_r(r.get_value())), color=RED, radius=0.07))
        trace = TracedPath(gdot.get_center, stroke_color=RED, stroke_width=4)
        self.add(trace, gdot)
        pure = label("pure: 0 bits", 24, MUTED).move_to(ax.c2p(0.66, 0.1))
        self.play(FadeIn(pure))

        readout = always_redraw(lambda: VGroup(
            eq(r"|\vec r| =", size=30), DecimalNumber(r.get_value(), num_decimal_places=2, font_size=30, color=INK),
            eq(r"S =", size=30), DecimalNumber(S_of_r(r.get_value()), num_decimal_places=3, font_size=30, color=RED),
        ).arrange(RIGHT, buff=0.15).move_to([-4.55, -3.3, 0]))
        self.add(readout)
        self.play(r.animate.set_value(0.0), run_time=7, rate_func=linear)
        center = label("center: 1 bit", 24, MUTED).move_to(ax.c2p(0.3, 0.72))
        self.play(FadeIn(center))
        self.wait(0.5)

        # back out to |r| = 0.6, then go once around: a rotation does not change the entropy
        curve = ax.plot(lambda t: S_of_r(min(max(t, 0.0), 1.0)), x_range=[0, 1, 0.01], color=RED, stroke_width=4)
        self.add(curve)
        self.remove(trace)
        self.play(r.animate.set_value(R_MID), run_time=2)
        mid = eq(r"\lambda = 0.8,\ 0.2 \quad S = 0.722 \text{ bits}", size=32).move_to([-1.0, 2.0, 0])
        mid.next_to(lamform, DOWN, buff=0.25)
        ring = Circle(radius=R * R_MID, color=AMBER, stroke_width=2).move_to(c0)
        self.play(Write(mid), Create(ring))
        self.play(ang.animate.set_value(50 * DEGREES + 2 * PI), run_time=6, rate_func=smooth)
        note = label("a rotation keeps length and entropy", 24, MUTED).move_to([3.95, -3.45, 0])
        self.play(FadeIn(note))
        self.wait(1.5)
        _ = (ORIGIN, OUT, Transform)


class TomographyConverges(ThreeDScene):
    def construct(self):
        R = 1.95
        self.set_camera_orientation(phi=68 * DEGREES, theta=35 * DEGREES)
        title = label("Each dot is one full tomography run", 32, INK, "BOLD").to_corner(UP + LEFT, buff=0.35)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1.0)

        sphere = Surface(lambda u, v: R * np.array([math.cos(u) * math.sin(v), math.sin(u) * math.sin(v), math.cos(v)]),
                         u_range=[0, 2 * PI], v_range=[0, PI], resolution=(18, 10), fill_opacity=0.06,
                         stroke_color=VIOLET_LIGHT, stroke_width=0.6, checkerboard_colors=[VIOLET_LIGHT, VIOLET_LIGHT])
        axes = VGroup(*[Line(-v * (R + 0.3), v * (R + 0.3), color=MUTED, stroke_width=1.5)
                        for v in (np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1]))])
        labs = [eq("x", size=32, color=MUTED).move_to([R + 0.6, 0, 0]),
                eq("y", size=32, color=MUTED).move_to([0, R + 0.6, 0]),
                eq("z", size=32, color=MUTED).move_to([0, 0, R + 0.6])]
        self.play(Create(sphere), Create(axes), run_time=1.6)
        for lb in labs:
            self.add_fixed_orientation_mobjects(lb)
        true = Arrow3D(ORIGIN, R * R_TRUE, color=VIOLET, thickness=0.03)
        self.play(Create(true))

        panel_title = eq(r"\vec r = (0.5,\ 0.3,\ 0.7)", size=32, color=VIOLET)
        law = eq(r"\text{rms error} \approx \sqrt{(3 - |\vec r|^2)/N}", size=28)
        law2 = eq(r"= \sqrt{2.17/N}", size=28)
        panel = VGroup(panel_title, law, law2).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        panel.to_edge(RIGHT, buff=0.3).to_edge(UP, buff=1.0)
        self.add_fixed_in_frame_mobjects(panel)
        self.play(Write(panel))

        def cloud(n, seed):
            rng = np.random.default_rng(seed)
            est = 2 * rng.binomial(n, (1 + R_TRUE) / 2, size=(40, 3)) / n - 1
            return VGroup(*[Dot3D(R * e, radius=0.06, resolution=(5, 5),
                                  color=(RED if np.linalg.norm(e) > 1 else AMBER)) for e in est]), est

        def readout(n):
            g = VGroup(eq(rf"N = {n}", size=44, color=INK), label("shots per basis", 24, MUTED),
                       eq(rf"\text{{predicted rms}} = {RMS_TXT[n]}", size=30, color=INK))
            return g.arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(LEFT, buff=0.4).shift(UP * 1.2)

        key = VGroup(label("amber: valid estimate", 24, AMBER), label("red: outside the ball", 24, RED)).arrange(
            DOWN, aligned_edge=LEFT, buff=0.12).to_corner(DOWN + RIGHT, buff=0.4)
        self.add_fixed_in_frame_mobjects(key)
        dots, est = cloud(10, 1)
        one = Arrow3D(ORIGIN, R * est[0], color=AMBER, thickness=0.02)
        ro = readout(10)
        self.add_fixed_in_frame_mobjects(ro)
        self.play(FadeIn(dots), Create(one), Write(ro), FadeIn(key), run_time=1.6)
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(2.5)
        self.play(FadeOut(one), run_time=0.6)
        for k, n in enumerate((100, 1000, 10000)):
            new, _ = cloud(n, 2 + k)
            ro2 = readout(n)
            self.add_fixed_in_frame_mobjects(ro2)
            self.remove(ro2)
            self.play(Transform(dots, new), FadeOut(ro), FadeIn(ro2), run_time=2.2)
            ro = ro2
            self.wait(2.0)
        self.stop_ambient_camera_rotation()
        end = label("100 times the shots, 10 times the accuracy", 26, MUTED).to_corner(DOWN + LEFT, buff=0.4)
        self.add_fixed_in_frame_mobjects(end)
        self.play(FadeIn(end))
        self.wait(1.5)


class ProjectBackToBall(Scene):
    def construct(self):
        title = label("An estimate outside the ball is pulled straight back", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.2)
        c0, R = np.array([-3.4, -0.55, 0]), 2.45

        def P(x, z):
            return c0 + R * np.array([x, z, 0])

        disk = Circle(radius=R, color=VIOLET, stroke_width=3).move_to(c0).set_fill(VIOLET_LIGHT, opacity=0.12)
        ax2 = VGroup(Line(P(-1.12, 0), P(1.12, 0), color=GRID, stroke_width=2), Line(P(0, -1.12), P(0, 1.12), color=GRID, stroke_width=2))
        xl = eq("x", size=30, color=MUTED).next_to(P(1.12, 0), RIGHT, buff=0.08)
        zl = eq("z", size=30, color=MUTED).next_to(P(0, 1.12), RIGHT, buff=0.1)
        self.play(Create(ax2), Create(disk), FadeIn(xl), FadeIn(zl))

        # worked example
        est = Dot(P(R_HAT[0], R_HAT[2]), color=RED, radius=0.1)
        ray = DashedLine(c0, P(R_HAT[0], R_HAT[2]), color=RED, stroke_width=3)
        info = VGroup(eq(r"\hat{\vec r} = (0.86,\ 0,\ 0.6)", size=34, color=RED),
                      eq(r"|\hat{\vec r}| = 1.0486 > 1", size=34, color=RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        info.move_to([3.3, 2.2, 0])
        self.play(Create(ray), FadeIn(est, scale=0.5), Write(info))

        base, sc = -1.55, 1.55
        bx = (2.2, 3.4)
        zero = Line([1.6, base, 0], [4.0, base, 0], color=MUTED, stroke_width=2)

        def bars(l1, l2):
            out = VGroup()
            for x, lam, col in ((bx[0], l1, BLUE), (bx[1], l2, RED if l2 < 0 else CYAN)):
                hgt = max(abs(lam) * sc, 0.02)
                rect = Rectangle(width=0.7, height=hgt, stroke_width=0, fill_color=col, fill_opacity=0.9)
                rect.move_to([x, base + (hgt / 2 if lam >= 0 else -hgt / 2), 0])
                out.add(rect)
            return out

        b = bars(*LAM)
        vals = VGroup(eq(r"\lambda_+ = 1.0243", size=30, color=BLUE), eq(r"\lambda_- = -0.0243", size=30, color=RED))
        vals.arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([3.4, -2.35, 0])
        neg = label("negative: not a state", 24, RED).next_to(vals, DOWN, buff=0.15)
        self.play(Create(zero), FadeIn(b), Write(vals), FadeIn(neg))
        self.wait(1.0)

        # projection
        target = P(R_PROJ[0], R_PROJ[2])
        b2 = bars(1.0, 0.0)
        vals2 = VGroup(eq(r"\lambda_+ = 1", size=30, color=BLUE), eq(r"\lambda_- = 0", size=30, color=CYAN))
        vals2.arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(vals, aligned_edge=LEFT)
        proj = eq(r"\hat{\vec r}/|\hat{\vec r}| = (0.820,\ 0,\ 0.572)", size=32, color=VIOLET).move_to(info[1], aligned_edge=LEFT)
        proj.shift(DOWN * 0.75)
        self.play(est.animate.move_to(target).set_color(VIOLET), Transform(b, b2), Transform(vals, vals2),
                  FadeOut(neg), Write(proj), run_time=2.0)
        pure = label("pure state, entropy 0 bits", 24, MUTED).next_to(proj, DOWN, buff=0.2).align_to(proj, LEFT)
        self.play(FadeIn(pure))
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in (est, ray, info, b, vals, proj, pure, zero)])

        # a cloud of estimates for a nearly pure state; r_y = 0 is known, so only X and Z are measured
        th = 50 * DEGREES
        rt = 0.95 * np.array([math.sin(th), math.cos(th)])
        rng = np.random.default_rng(5)
        n = 20
        cl = 2 * rng.binomial(n, (1 + rt) / 2, size=(50, 2)) / n - 1
        out = np.linalg.norm(cl, axis=1) > 1
        k = int(out.sum())
        tdot = Dot(P(*rt), color=VIOLET, radius=0.11)
        setup = VGroup(eq(r"\text{true state: } |\vec r| = 0.95", size=32, color=VIOLET),
                       label("50 runs, 20 shots each in X and Z", 26, INK),
                       label("(preparation known to have r_y = 0)", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        setup.move_to([3.4, 2.0, 0])
        self.play(FadeIn(tdot), FadeIn(setup))
        dots = VGroup(*[Dot(P(*e), radius=0.06, color=(RED if o else AMBER)) for e, o in zip(cl, out)])
        self.play(FadeIn(dots, lag_ratio=0.05), run_time=2.0)
        cnt = label(f"{k} of 50 lie outside the ball", 26, RED).next_to(setup, DOWN, buff=0.4).align_to(setup, LEFT)
        self.play(FadeIn(cnt))
        moves = [d.animate.move_to(P(*(e / np.linalg.norm(e)))).set_color(VIOLET) for d, e, o in zip(dots, cl, out) if o]
        self.play(*moves, run_time=2.0)
        done = label("projected onto the surface: valid states", 26, VIOLET).next_to(cnt, DOWN, buff=0.25).align_to(cnt, LEFT)
        self.play(FadeIn(done))
        self.wait(2.0)
        _ = (Arrow, CYAN, UP)
