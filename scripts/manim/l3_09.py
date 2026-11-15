"""L3-09 Optimization and learning: three 3Blue1Brown-style scenes.

StepSizes      gradient descent on the loss L(w) = w1^2 + 4 w2^2 from (-4, 1.2), drawn on its contour map,
               with step sizes 0.02 (too small), 0.1 (good) and 0.26 (too large: the w2 coordinate is
               multiplied by 1 - 8(0.26) = -1.08 each step and the iterates zigzag outward).
LossBowl3D     the same loss as a 3-D bowl; a ball follows the gradient descent path with step 0.1
               down to the minimum while the camera turns.
Overfitting    polynomials of degree 0 to 9 fitted to 10 noisy training points; training error falls to
               zero while validation error, on 50 fresh points, is smallest at degree 3 and rises after.
Numbers are computed here and checked against the lesson text by facts().
"""
import pathlib
import sys

import numpy as np
from numpy.polynomial import Polynomial

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, IN, LEFT, RIGHT, UP, Axes, Create, DashedLine, Dot, Dot3D, FadeIn, FadeOut, Line,
                   Line3D, ParametricFunction, Scene, Surface, ThreeDAxes, ThreeDScene, Transform, VGroup, VMobject,
                   Write, always_redraw)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

A = (2.0, 8.0)                 # curvatures: L = (2/2) w1^2 + (8/2) w2^2
W0 = (-4.0, 1.2)
ETAS = (0.02, 0.1, 0.26)
STEPS = 12
THRESH = 2 / max(A)            # 0.25


def loss(w1, w2):
    return w1 ** 2 + 4 * w2 ** 2


def gd(eta, w=W0, steps=STEPS):
    pts = [w]
    for _ in range(steps):
        w1, w2 = pts[-1]
        pts.append((w1 - eta * 2 * w1, w2 - eta * 8 * w2))
    return pts


FACT = {eta: (round(1 - eta * A[0], 2), round(1 - eta * A[1], 2)) for eta in ETAS}
assert FACT == {0.02: (0.96, 0.84), 0.1: (0.8, 0.2), 0.26: (0.48, -1.08)} and THRESH == 0.25
L0 = loss(*W0)
assert abs(L0 - 21.76) < 1e-12
END = {eta: loss(*gd(eta)[-1]) for eta in ETAS}
assert END[0.26] > L0 > END[0.02] > END[0.1]

# overfitting data (same seed and recipe as the lesson's code block and figure)
SEED = 132


def poly_data():
    rng = np.random.default_rng(SEED)
    xt = np.linspace(0, 1, 10)
    yt = np.sin(2 * np.pi * xt) + rng.normal(0, 0.3, 10)
    xv = rng.uniform(0, 1, 50)
    yv = np.sin(2 * np.pi * xv) + rng.normal(0, 0.3, 50)
    return xt, yt, xv, yv


XT, YT, XV, YV = poly_data()
FITS = [Polynomial.fit(XT, YT, d) for d in range(10)]
TRAIN = [float(np.mean((p(XT) - YT) ** 2)) for p in FITS]
VAL = [float(np.mean((p(XV) - YV) ** 2)) for p in FITS]
BEST = int(np.argmin(VAL))
assert BEST == 3 and TRAIN[9] < 1e-12 and all(TRAIN[d + 1] <= TRAIN[d] + 1e-12 for d in range(9))
assert f"{VAL[3]:.2f}" == "0.08" and f"{VAL[9]:.2f}" == "1.00"


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["w_2 \\leftarrow (1 - 8\\eta)\\, w_2", "1 - 8(0.26) = -1.08", "\\eta < 2/8 = 0.25",
            f"{VAL[3]:.2f}", f"{VAL[9]:.2f}", "w \\leftarrow w - \\eta\\, \\nabla L(w)"]


class StepSizes(Scene):
    def construct(self):
        title = label("Gradient descent: the step size decides everything", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.0)
        ax = Axes(x_range=[-5, 5, 1], y_range=[-3, 3, 1], x_length=7.0, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False, "stroke_width": 2}).move_to([-3.0, -0.55, 0])
        xl = eq("w_1", size=32).next_to(ax.c2p(5, 0), DOWN, buff=0.15)
        yl = eq("w_2", size=32).next_to(ax.c2p(0, 3), RIGHT, buff=0.15)
        contours = VGroup(*[ParametricFunction(lambda t, c=c: ax.c2p(np.sqrt(c) * np.cos(t), np.sqrt(c) / 2 * np.sin(t)),
                                               t_range=[0, 2 * np.pi], color=CYAN, stroke_width=2, stroke_opacity=0.6)
                            for c in (1, 4, 9, 16, 25)])
        mn = Dot(ax.c2p(0, 0), color=INK, radius=0.06)
        self.play(Create(ax), Write(xl), Write(yl), Create(contours), FadeIn(mn), run_time=1.6)
        lossf = eq(r"L(w) = w_1^2 + 4w_2^2", size=34).move_to([3.8, 2.65, 0])
        rule = eq(r"w \leftarrow w - \eta\, \nabla L(w)", size=34).move_to([3.8, 1.95, 0])
        comp = VGroup(eq(r"w_1 \leftarrow (1 - 2\eta)\, w_1", size=32), eq(r"w_2 \leftarrow (1 - 8\eta)\, w_2", size=32)) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([3.8, 0.95, 0])
        self.play(Write(lossf))
        self.play(Write(rule))
        self.play(Write(comp))
        start = Dot(ax.c2p(*W0), color=INK, radius=0.07)
        self.play(FadeIn(start))

        info = [(0.02, BLUE, "too small: crawls"), (0.1, VIOLET, "good: fast and stable"),
                (0.26, RED, "too large: zigzags outward")]
        rows = VGroup()
        for i, (eta, col, words) in enumerate(info):
            pts = gd(eta)
            path = VMobject(color=col, stroke_width=4).set_points_as_corners([ax.c2p(*p) for p in pts])
            dots = VGroup(*[Dot(ax.c2p(*p), color=col, radius=0.045) for p in pts[1:]])
            row = VGroup(eq(rf"\eta = {eta}", size=32, color=col), label(words, 24, col)).arrange(RIGHT, buff=0.25)
            row.move_to([3.8, -0.35 - 0.6 * i, 0]).align_to([1.0, 0, 0], LEFT)
            rows.add(row)
            self.play(FadeIn(row))
            self.play(Create(path), FadeIn(dots, lag_ratio=0.2), run_time=2.4)
            self.wait(0.4)
        big = eq(r"1 - 8(0.26) = -1.08", size=32, color=RED).move_to([3.8, -2.35, 0])
        self.play(Write(big))
        thr = eq(r"\text{stable only if } \eta < 2/8 = 0.25", size=32, color=INK).move_to([3.8, -3.05, 0])
        thr2 = eq(r"\eta < 2/8 = 0.25", size=32, color=INK)
        self.play(Write(thr))
        self.wait(2.0)
        _ = (thr2, AMBER, GRID, DashedLine, Transform, always_redraw, LEFT, FadeOut)


class LossBowl3D(ThreeDScene):
    def construct(self):
        s = 0.1                                               # vertical scale of the bowl
        ax = ThreeDAxes(x_range=[-4.5, 4.5, 1], y_range=[-2, 2, 1], z_range=[0, 4, 1], x_length=7.2, y_length=3.2,
                        z_length=3.2, axis_config={"color": MUTED, "include_tip": False}).shift(IN * 1.3)
        surf = Surface(lambda u, v: ax.c2p(u, v, s * loss(u, v)), u_range=[-4.0, 4.0], v_range=[-1.6, 1.6],
                       resolution=(20, 12), fill_opacity=0.45, checkerboard_colors=[CYAN, "#a5f3fc"],
                       stroke_color="#0e7490", stroke_width=0.4)
        self.set_camera_orientation(phi=64 * DEGREES, theta=-58 * DEGREES, zoom=1.05)
        title = label("The loss as a landscape: descend the bowl", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), Create(ax), run_time=1.2)
        self.play(Create(surf), run_time=2.0)
        f1 = eq(r"L(w) = w_1^2 + 4w_2^2", size=32).to_corner(DOWN + LEFT, buff=0.35)
        self.add_fixed_in_frame_mobjects(f1)
        self.play(Write(f1))

        pts = gd(0.1, steps=12)
        p3 = [ax.c2p(a, b, s * loss(a, b) + 0.05) for a, b in pts]
        ball = Dot3D(p3[0], color=RED, radius=0.11)
        self.play(FadeIn(ball))
        g = eq(r"-\nabla L \text{ points downhill, across the contours}", size=32, color=VIOLET).to_corner(DOWN + RIGHT, buff=0.35)
        self.add_fixed_in_frame_mobjects(g)
        self.play(Write(g))
        segs = []
        for a, b in zip(p3, p3[1:]):
            seg = Line3D(a, b, color=RED, thickness=0.02)
            segs.append(seg)
            self.play(Create(seg), ball.animate.move_to(b), run_time=0.45)
        rule = eq(r"\eta = 0.1:\ L \text{ from } 21.76 \text{ to } " + f"{loss(*pts[-1]):.3f}", size=32, color=INK)
        rule.next_to(title, DOWN, buff=0.25)
        self.add_fixed_in_frame_mobjects(rule)
        self.play(Write(rule))
        self.begin_ambient_camera_rotation(rate=0.18)
        self.wait(4.0)
        self.stop_ambient_camera_rotation()
        self.wait(0.5)


class Overfitting(Scene):
    def construct(self):
        title = label("Lower training error is not the goal", 34, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.0)
        lax = Axes(x_range=[0, 1, 0.25], y_range=[-3.5, 3.5, 1], x_length=5.6, y_length=4.6,
                   axis_config={"color": MUTED, "include_tip": False}).move_to([-3.4, -0.55, 0])
        rax = Axes(x_range=[0, 9, 1], y_range=[0, 1.1, 0.25], x_length=5.4, y_length=3.6,
                   axis_config={"color": MUTED, "include_tip": False}).move_to([3.3, -0.75, 0])
        lx = eq("x", size=32).next_to(lax.c2p(1, -3.5), RIGHT, buff=0.15)
        rx = label("polynomial degree", 24, MUTED).next_to(rax, DOWN, buff=0.4)
        rticks = VGroup(*[label(str(d), 24, MUTED).next_to(rax.c2p(d, 0), DOWN, buff=0.12) for d in range(0, 10, 3)])
        yticks = VGroup(*[label(t, 24, MUTED).next_to(rax.c2p(0, v), LEFT, buff=0.12) for v, t in ((0.5, "0.5"), (1.0, "1.0"))])
        ry = label("mean squared error", 24, MUTED).next_to(rax.c2p(0, 1.1), UP, buff=0.15).align_to(rax, LEFT)
        tr_dots = VGroup(*[Dot(lax.c2p(x, y), color=BLUE, radius=0.07) for x, y in zip(XT, YT)])
        va_dots = VGroup(*[Dot(lax.c2p(x, y), color=AMBER, radius=0.04, fill_opacity=0.7) for x, y in zip(XV, YV)])
        leg = VGroup(VGroup(Dot(color=BLUE, radius=0.07), label("training (10)", 24, BLUE)).arrange(RIGHT, buff=0.12),
                     VGroup(Dot(color=AMBER, radius=0.05), label("validation (50)", 24, AMBER)).arrange(RIGHT, buff=0.12)) \
            .arrange(RIGHT, buff=0.4).next_to(lax, UP, buff=0.12)
        self.play(Create(lax), Write(lx), FadeIn(tr_dots), FadeIn(leg), run_time=1.4)
        self.play(FadeIn(va_dots))
        self.play(Create(rax), FadeIn(rx), FadeIn(rticks), FadeIn(yticks), FadeIn(ry))

        xs = np.linspace(0, 1, 300)

        def curve(d):
            ys = np.clip(FITS[d](xs), -3.5, 3.5)
            return VMobject(color=VIOLET, stroke_width=4).set_points_smoothly([lax.c2p(x, y) for x, y in zip(xs, ys)])

        cur = curve(0)
        deg = label("degree 0", 26, VIOLET).move_to([-3.4, 2.45, 0]).align_to(lax, RIGHT)
        self.play(Create(cur), FadeIn(deg))
        tdots, vdots = VGroup(), VGroup()
        tline, vline = VMobject(color=BLUE, stroke_width=4), VMobject(color=AMBER, stroke_width=4)
        for d in range(10):
            if d > 0:
                self.play(Transform(cur, curve(d)), Transform(deg, label(f"degree {d}", 26, VIOLET).move_to(deg)), run_time=0.7)
            td = Dot(rax.c2p(d, TRAIN[d]), color=BLUE, radius=0.06)
            vd = Dot(rax.c2p(d, min(VAL[d], 1.1)), color=AMBER, radius=0.06)
            tdots.add(td)
            vdots.add(vd)
            anims = [FadeIn(td), FadeIn(vd)]
            if d > 0:
                anims += [Create(Line(rax.c2p(d - 1, TRAIN[d - 1]), rax.c2p(d, TRAIN[d]), color=BLUE, stroke_width=4)),
                          Create(Line(rax.c2p(d - 1, min(VAL[d - 1], 1.1)), rax.c2p(d, min(VAL[d], 1.1)), color=AMBER, stroke_width=4))]
            self.play(*anims, run_time=0.5)
            if d == BEST:
                note = eq(rf"\text{{degree 3: validation }} {VAL[3]:.2f}", size=32, color=AMBER).move_to([3.3, 1.95, 0])
                self.play(Write(note))
                self.wait(0.6)
        n9 = eq(rf"\text{{degree 9: training }} 0,\ \text{{validation }} {VAL[9]:.2f}", size=32, color=RED).move_to([3.3, 2.5, 0])
        self.play(Write(n9))
        moral = label("it memorized the noise: judge a model on data it has not seen", 26, INK).move_to([0, -3.62, 0])
        self.play(FadeIn(moral))
        self.wait(2.5)
        _ = (tline, vline, CYAN, GRID, RED, LEFT, FadeOut, DashedLine, Line, always_redraw)
