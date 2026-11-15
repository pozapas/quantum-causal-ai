"""L3-06 Derivatives and gradients: three 3Blue1Brown-style scenes.

SecantToTangent   f(x) = x^2 at x = 3: the secant through (3, 9) and (3 + h, (3 + h)^2) has slope 6 + h;
                  as h shrinks the secant turns into the tangent of slope 6.  The difference quotient
                  is simplified term by term.
ContourGradient   level curves of g(x, y) = x^2 + 3y^2 on equal axes; at (2, -1) the gradient (4, -6) is
                  perpendicular to the level curve, and a turning unit direction u shows the directional
                  derivative grad g . u, largest (sqrt 52 = 7.21) along the gradient, zero along the curve.
SteepestSurface   ThreeDScene: the surface z = g(x, y) over its contour map; slices through the point
                  (2, -1, 7) in turning directions; the steepest one lies over the gradient arrow.
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, RIGHT, UL, UP, WHITE, Arrow, Arrow3D, Axes, Create, DashedLine, DecimalNumber, Dot,
                   Dot3D, FadeIn, FadeOut, Line, ParametricFunction, RightAngle, Scene, Surface, ThreeDAxes,
                   ThreeDScene, TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear, smooth)

from qcai_style import AMBER, BLUE, BLUE_LIGHT, CYAN, CYAN_LIGHT, GRID, INK, MUTED, RED, VIOLET, eq, label

# ---- f(x) = x^2 at x0 = 3 ------------------------------------------------------------------------
X0 = 3.0


def f(x):
    return x * x


def secant_slope(h):
    return (f(X0 + h) - f(X0)) / h


for _h in (2.0, 1.0, 0.5, 0.1, 0.01):
    assert abs(secant_slope(_h) - (6 + _h)) < 1e-9

# ---- g(x, y) = x^2 + 3 y^2 at (2, -1) ---------------------------------------------------------------
PX, PY = 2.0, -1.0


def g(x, y):
    return x * x + 3 * y * y


GRAD = np.array([2 * PX, 6 * PY])                 # (4, -6)
NORM = float(np.linalg.norm(GRAD))                 # sqrt(52) = 7.2111
assert np.allclose(GRAD, [4, -6]) and abs(NORM - math.sqrt(52)) < 1e-12 and g(PX, PY) == 7
TANGENT = np.array([3.0, 2.0]) / math.sqrt(13)     # along the level curve: grad . tangent = 0
assert abs(GRAD @ TANGENT) < 1e-12


def dirderiv(phi):
    return float(GRAD @ np.array([math.cos(phi), math.sin(phi)]))


PHI_GRAD = math.atan2(GRAD[1], GRAD[0])            # -56.31 degrees
assert abs(dirderiv(PHI_GRAD) - NORM) < 1e-12
# central difference agrees with the formula
_h = 1e-6
assert abs((g(PX + _h, PY) - g(PX - _h, PY)) / (2 * _h) - 4) < 1e-6
assert abs((g(PX, PY + _h) - g(PX, PY - _h)) / (2 * _h) + 6) < 1e-6


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["6 + h", "\\frac{(3 + h)^2 - 9}{h}", "(4, -6)", f"{NORM:.2f}", "\\sqrt{52}", "x^2 + 3y^2"]


class SecantToTangent(Scene):
    def construct(self):
        title = label("A derivative is the limit of secant slopes", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        ax = Axes(x_range=[0, 5.2, 1], y_range=[0, 26, 5], x_length=6.2, y_length=5.6,
                  axis_config={"color": MUTED, "include_tip": False, "include_numbers": True, "font_size": 24,
                               "decimal_number_config": {"num_decimal_places": 0, "color": MUTED}}
                  ).move_to([-3.2, -0.55, 0])
        curve = ax.plot(f, x_range=[0, 5.05], color=INK, stroke_width=4)
        fl = eq(r"f(x) = x^2", size=34).next_to(ax.c2p(4.9, 24), LEFT, buff=0.35)
        self.play(Write(title), Create(ax), run_time=1.4)
        self.play(Create(curve), Write(fl))
        P = Dot(ax.c2p(X0, f(X0)), color=VIOLET, radius=0.08)
        Pl = eq(r"(3, 9)", size=30, color=VIOLET).next_to(P, LEFT, buff=0.15)
        self.play(FadeIn(P), Write(Pl))

        h = ValueTracker(2.0)

        def secant():
            m = secant_slope(h.get_value())
            x_lo = max(0.0, X0 - 9 / m + 0.02)
            x_hi = min(5.2, X0 + (26 - 9) / m)
            return Line(ax.c2p(x_lo, 9 + m * (x_lo - X0)), ax.c2p(x_hi, 9 + m * (x_hi - X0)), color=AMBER, stroke_width=4)

        sec = always_redraw(secant)
        Q = always_redraw(lambda: Dot(ax.c2p(X0 + h.get_value(), f(X0 + h.get_value())), color=AMBER, radius=0.08))
        run = always_redraw(lambda: DashedLine(ax.c2p(X0, 9), ax.c2p(X0 + h.get_value(), 9), color=MUTED, stroke_width=2))
        rise = always_redraw(lambda: DashedLine(ax.c2p(X0 + h.get_value(), 9), ax.c2p(X0 + h.get_value(), f(X0 + h.get_value())),
                                                color=MUTED, stroke_width=2))
        self.play(Create(sec), FadeIn(Q), Create(run), Create(rise))

        # the difference quotient, simplified term by term
        X = 3.3
        q0 = eq(r"\text{slope} = \frac{f(3 + h) - f(3)}{h}", size=36).move_to([X, 2.4, 0])
        self.play(Write(q0))
        q1 = eq(r"\text{slope} = \frac{(3 + h)^2 - 9}{h}", size=36).move_to([X, 2.4, 0])
        self.play(TransformMatchingTex(q0, q1), run_time=1.2)
        q2 = eq(r"\text{slope} = \frac{6h + h^2}{h}", size=36).move_to([X, 2.4, 0])
        self.play(TransformMatchingTex(q1, q2), run_time=1.2)
        q3 = eq(r"\text{slope} = 6 + h", size=40, color=AMBER).move_to([X, 2.4, 0])
        self.play(TransformMatchingTex(q2, q3), run_time=1.2)

        hl = eq(r"h =", size=36).move_to([X - 1.0, 0.9, 0])
        hv = always_redraw(lambda: DecimalNumber(h.get_value(), num_decimal_places=3, font_size=36, color=INK)
                           .next_to(hl, RIGHT, buff=0.2))
        sl = eq(r"6 + h =", size=36, color=AMBER).move_to([X - 1.35, 0.0, 0])
        sv = always_redraw(lambda: DecimalNumber(secant_slope(h.get_value()), num_decimal_places=3, font_size=36, color=AMBER)
                           .next_to(sl, RIGHT, buff=0.2))
        self.play(Write(hl), FadeIn(hv), Write(sl), FadeIn(sv))
        self.play(h.animate.set_value(1.0), run_time=2.2, rate_func=smooth)
        self.play(h.animate.set_value(0.25), run_time=2.2, rate_func=smooth)
        self.play(h.animate.set_value(0.01), run_time=2.6, rate_func=smooth)
        self.wait(0.4)

        tan = ax.plot(lambda x: 9 + 6 * (x - X0), x_range=[1.5, X0 + 17 / 6], color=RED, stroke_width=5)
        lim = eq(r"f'(3) = \lim_{h \to 0} (6 + h) = 6", size=38, color=RED).move_to([X, -1.3, 0])
        self.play(Create(tan), Write(lim))
        tl = eq(r"\text{tangent: } y = 9 + 6(x - 3)", size=32, color=RED).move_to([X, -2.3, 0])
        self.play(Write(tl))
        self.wait(2.0)


class ContourGradient(Scene):
    def construct(self):
        title = label("The gradient points straight uphill, across the level curves", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        ax = Axes(x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1], x_length=6.4, y_length=4.0,
                  axis_config={"color": MUTED, "include_tip": False, "include_numbers": True, "font_size": 22,
                               "decimal_number_config": {"num_decimal_places": 0, "color": MUTED}}).move_to([-3.25, -0.6, 0])
        assert abs((ax.c2p(1, 0)[0] - ax.c2p(0, 0)[0]) - (ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1])) < 1e-9   # equal scales
        self.play(Write(title), Create(ax), run_time=1.4)
        levels = [1, 4, 7, 10, 13]
        curves = VGroup()
        for c in levels:
            a, b = math.sqrt(c), math.sqrt(c / 3)
            col = VIOLET if c == 7 else BLUE_LIGHT
            curves.add(ParametricFunction(lambda s, a=a, b=b: ax.c2p(a * math.cos(s), b * math.sin(s)), t_range=[0, 2 * math.pi],
                                          color=col, stroke_width=4 if c == 7 else 2.5))
        gl = eq(r"g(x, y) = x^2 + 3y^2", size=34).move_to([3.3, 2.5, 0])
        self.play(Create(curves), Write(gl), run_time=2)
        c7 = eq(r"g = 7", size=28, color=VIOLET).next_to(ax.c2p(-math.sqrt(7) * 0.71, math.sqrt(7 / 3) * 0.71), UL, buff=0.05)
        self.play(Write(c7))

        p = ax.c2p(PX, PY)
        dot = Dot(p, color=INK, radius=0.08)
        dl = eq(r"(2, -1)", size=28).next_to(dot, DOWN + LEFT, buff=0.12)
        dl.add_background_rectangle(color=WHITE, opacity=0.9, buff=0.04)
        self.play(FadeIn(dot), Write(dl))
        unit = ax.c2p(1, 0)[0] - ax.c2p(0, 0)[0]
        gdir = GRAD / NORM
        garrow = Arrow(p, p + 1.7 * np.array([gdir[0], gdir[1], 0]), buff=0, color=RED, stroke_width=6)
        tline = Line(p - 1.3 * np.array([TANGENT[0], TANGENT[1], 0]), p + 1.3 * np.array([TANGENT[0], TANGENT[1], 0]),
                     color=VIOLET, stroke_width=3)
        ra = RightAngle(tline, garrow, length=0.22, color=INK, quadrant=(1, 1))
        f1 = eq(r"\nabla g = (2x, 6y) = (4, -6)", size=34, color=RED).move_to([3.3, 1.65, 0])
        self.play(Write(f1))
        self.play(Create(garrow), Create(tline))
        self.play(Create(ra))
        n1 = label("perpendicular to the level curve", 24, MUTED).move_to([3.3, 0.95, 0])
        self.play(FadeIn(n1))
        self.wait(0.8)

        # turning unit direction u and the directional derivative
        phi = ValueTracker(PHI_GRAD + math.radians(150))
        uarrow = always_redraw(lambda: Arrow(p, p + 1.25 * np.array([math.cos(phi.get_value()), math.sin(phi.get_value()), 0]),
                                             buff=0, color=AMBER, stroke_width=6))
        f2 = eq(r"D_u g = \nabla g \cdot u = |\nabla g| \cos\theta", size=34).move_to([3.3, 0.15, 0])
        self.play(FadeOut(n1), Write(f2), Create(uarrow))
        dl2 = eq(r"D_u g =", size=36, color=AMBER).move_to([2.55, -0.75, 0])
        dv = always_redraw(lambda: DecimalNumber(dirderiv(phi.get_value()), num_decimal_places=2, font_size=36, color=AMBER,
                                                 include_sign=True).next_to(dl2, RIGHT, buff=0.2))
        self.play(Write(dl2), FadeIn(dv))
        self.play(phi.animate.set_value(PHI_GRAD + math.radians(90)), run_time=2.4, rate_func=smooth)
        n2 = label("along the curve: 0", 24, VIOLET).move_to([3.3, -1.55, 0])
        self.play(FadeIn(n2))
        self.wait(0.4)
        self.play(phi.animate.set_value(PHI_GRAD), FadeOut(n2, run_time=0.6), run_time=2.4, rate_func=smooth)
        mx = eq(rf"\max_u D_u g = |\nabla g| = \sqrt{{52}} \approx {NORM:.2f}", size=34, color=RED).move_to([3.3, -1.6, 0])
        self.play(Write(mx))
        self.play(phi.animate.set_value(PHI_GRAD - math.radians(180)), run_time=3.0, rate_func=smooth)
        n3 = label("opposite the gradient: steepest descent", 24, MUTED).move_to([3.3, -2.45, 0])
        self.play(FadeIn(n3))
        self.wait(2.0)
        _ = (unit, linear, WHITE, LEFT, RIGHT, DOWN)


class SteepestSurface(ThreeDScene):
    def construct(self):
        zs = 0.25                                   # vertical axis drawn at 1/4 scale (ticks show true heights)
        ax = ThreeDAxes(x_range=[-3, 3, 1], y_range=[-2, 2, 1], z_range=[0, 14, 2], x_length=6, y_length=4, z_length=14 * zs,
                        axis_config={"color": MUTED, "include_tip": False})
        self.set_camera_orientation(phi=64 * DEGREES, theta=-62 * DEGREES, zoom=0.9)
        title = label("Steepest ascent is along the gradient", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.add_fixed_in_frame_mobjects(title)
        title.set_opacity(0)
        surf = Surface(lambda u, v: ax.c2p(u, v, g(u, v)), u_range=[-2.4, 2.4], v_range=[-1.45, 1.45], resolution=(20, 14),
                       fill_opacity=0.32, checkerboard_colors=[BLUE_LIGHT, CYAN_LIGHT], stroke_color=BLUE, stroke_width=0.4)
        floor = VGroup()
        for c in (1, 4, 7, 10):
            a, b = math.sqrt(c), math.sqrt(c / 3)
            floor.add(ParametricFunction(lambda s, a=a, b=b: ax.c2p(a * math.cos(s), b * math.sin(s), 0), t_range=[0, 2 * math.pi],
                                         color=VIOLET if c == 7 else BLUE, stroke_width=3 if c == 7 else 1.8))
        self.play(Create(ax), title.animate.set_opacity(1), run_time=1.4)
        self.play(Create(floor), run_time=1.5)
        self.play(Create(surf), run_time=2.5)

        top = ax.c2p(PX, PY, g(PX, PY))
        base = ax.c2p(PX, PY, 0)
        pd = Dot3D(top, color=INK, radius=0.07)
        drop = DashedLine(base, top, color=MUTED, stroke_width=2)
        bd = Dot3D(base, color=INK, radius=0.06)
        self.play(FadeIn(pd), Create(drop), FadeIn(bd))
        gdir = GRAD / NORM
        garrow = Arrow3D(base, ax.c2p(PX + 1.4 * gdir[0], PY + 1.4 * gdir[1], 0), color=RED, thickness=0.025)
        self.play(Create(garrow))
        info = VGroup(eq(r"z = x^2 + 3y^2", size=32), eq(r"\nabla g(2, -1) = (4, -6)", size=32, color=RED)).arrange(
            DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UP + LEFT, buff=0.35).shift(DOWN * 0.7)
        self.add_fixed_in_frame_mobjects(info)
        self.play(FadeIn(info))

        # slice through the point in direction u: a short tangent segment with slope D_u g
        phi = ValueTracker(PHI_GRAD + math.radians(110))
        L = 0.45

        def slice_seg():
            ph = phi.get_value()
            ux, uy = math.cos(ph), math.sin(ph)
            d = dirderiv(ph)
            a = ax.c2p(PX - L * ux, PY - L * uy, 7 - L * d)
            b = ax.c2p(PX + L * ux, PY + L * uy, 7 + L * d)
            return Line(a, b, color=AMBER, stroke_width=6)

        def floor_u():
            ph = phi.get_value()
            return Line(base, ax.c2p(PX + 0.9 * math.cos(ph), PY + 0.9 * math.sin(ph), 0), color=AMBER, stroke_width=5)

        seg = always_redraw(slice_seg)
        fu = always_redraw(floor_u)
        self.play(Create(seg), Create(fu))
        dl = eq(r"\text{slope along } u:\ D_u g =", size=32, color=AMBER)
        dv = DecimalNumber(dirderiv(phi.get_value()), num_decimal_places=2, font_size=32, color=AMBER, include_sign=True)
        row = VGroup(dl, dv).arrange(RIGHT, buff=0.15).to_corner(DOWN + LEFT, buff=0.4)
        self.add_fixed_in_frame_mobjects(row)
        def upd(m):
            m.set_value(dirderiv(phi.get_value()))
            self.renderer.camera.add_fixed_in_frame_mobjects(m)    # new digits must stay fixed in frame too
        dv.add_updater(upd)
        self.play(FadeIn(row))
        self.play(phi.animate.set_value(PHI_GRAD + math.radians(270)), run_time=5, rate_func=linear)
        self.play(phi.animate.set_value(PHI_GRAD + math.radians(360)), run_time=2.5, rate_func=smooth)
        msg = eq(rf"\text{{steepest: along }} \nabla g,\ \text{{slope }} \sqrt{{52}} \approx {NORM:.2f}", size=32, color=RED)
        msg.to_corner(DOWN + RIGHT, buff=0.4)
        self.add_fixed_in_frame_mobjects(msg)
        self.play(FadeIn(msg))
        self.move_camera(theta=-20 * DEGREES, run_time=4)
        self.wait(1.5)
        _ = (Axes, Scene, RightAngle, GRID, CYAN, LEFT, RIGHT, UP, DOWN, WHITE, smooth, Write)
