"""L3-01 Complex numbers and phase: two 3Blue1Brown-style scenes.

ComplexPlaneTour  z = 3 + 4i on the complex plane: modulus by Pythagoras, argument, conjugate as a
                  reflection, z times its conjugate = 25, and the polar form 5 e^{i 0.927}.
MultiplyRotates   multiplying by i turns the plane a quarter turn; then the sum 1 + e^{i phi} as phi
                  sweeps once around, with a live trace of |1 + e^{i phi}|^2 = 2 + 2 cos(phi).
Numbers are computed here and checked against the lesson text by facts().
"""
import cmath
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, ORIGIN, PI, RIGHT, UL, UP, UR, Angle, Arrow, Axes, ComplexPlane, Create,
                   DashedLine, Dot, FadeIn, FadeOut, Line, ReplacementTransform, Rotate, Scene, TracedPath, Transform,
                   TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

Z = complex(3, 4)
MOD = abs(Z)                       # 5
ARG = cmath.phase(Z)               # 0.9273 rad
ARG_DEG = math.degrees(ARG)        # 53.13 degrees
assert MOD == 5 and abs((Z * Z.conjugate()).real - 25) < 1e-12


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["3 + 4i", "3 - 4i", f"{ARG_DEG:.2f}", f"{ARG:.3f}", "25", "2 + 2\\cos\\varphi"]


def plane(scale=0.75, xr=6, yr=5):
    p = ComplexPlane(x_range=[-xr, xr, 1], y_range=[-yr, yr, 1], background_line_style={"stroke_color": GRID, "stroke_width": 1},
                     axis_config={"color": MUTED}).scale(scale)
    return p


class ComplexPlaneTour(Scene):
    def construct(self):
        p = plane(0.62).shift(LEFT * 2.6)
        title = label("A complex number is a point, and an arrow", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Create(p), Write(title), run_time=1.6)

        tip = p.n2p(Z)
        dot = Dot(tip, color=VIOLET, radius=0.08)
        zlab = eq("z = 3 + 4i", size=38, color=VIOLET).next_to(dot, UR, buff=0.1)
        legs = VGroup(DashedLine(p.n2p(0), p.n2p(3), color=BLUE), DashedLine(p.n2p(3), tip, color=CYAN))
        self.play(FadeIn(dot, scale=0.5), Write(zlab))
        self.play(Create(legs), run_time=1.2)

        arrow = Arrow(p.n2p(0), tip, buff=0, color=VIOLET, stroke_width=6)
        self.play(Create(arrow))
        steps = VGroup(eq(r"|z| = \sqrt{3^2 + 4^2}"), eq(r"= \sqrt{25} = 5")).arrange(DOWN, aligned_edge=LEFT)
        steps.move_to(RIGHT * 3.6 + UP * 1.6)
        self.play(Write(steps[0]))
        self.play(Write(steps[1]))

        ang = Angle(Line(p.n2p(0), p.n2p(1)), Line(p.n2p(0), tip), radius=0.7, color=AMBER)
        alab = eq(rf"\theta = \arctan\tfrac{{4}}{{3}} \approx {ARG_DEG:.2f}^\circ", size=36, color=AMBER).move_to(RIGHT * 3.6 + UP * 0.1)
        self.play(Create(ang), Write(alab))
        self.wait(0.6)

        # conjugate: reflect in the real axis
        zc = Dot(p.n2p(Z.conjugate()), color=RED, radius=0.08)
        zclab = eq(r"\bar z = 3 - 4i", size=38, color=RED).next_to(zc, DOWN + RIGHT * 0.3, buff=0.1)
        ghost = arrow.copy().set_color(RED)
        self.play(ghost.animate.become(Arrow(p.n2p(0), p.n2p(Z.conjugate()), buff=0, color=RED, stroke_width=6)),
                  FadeIn(zc), Write(zclab), run_time=1.4)
        prod = eq(r"z\,\bar z = (3+4i)(3-4i)", size=36).move_to(RIGHT * 3.6 + DOWN * 1.3)
        prod2 = eq(r"z\,\bar z = 9 + 16 = 25 = |z|^2", size=36).move_to(prod)
        self.play(Write(prod))
        self.play(TransformMatchingTex(prod, prod2), run_time=1.4)
        self.wait(0.5)

        polar = eq(rf"z = 5\,e^{{i\,{ARG:.3f}}}", size=46, color=VIOLET).move_to(RIGHT * 3.6 + DOWN * 2.6)
        self.play(Write(polar))
        note = label("same point: length 5, angle 0.927 rad", 26, MUTED).next_to(polar, DOWN, buff=0.15)
        self.play(FadeIn(note))
        self.wait(1.5)


class MultiplyRotates(Scene):
    def construct(self):
        p = plane(0.85, 3, 2.5).shift(LEFT * 3.4 + DOWN * 0.3)
        title = label("Multiplying by a unit complex number rotates", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Create(p), Write(title), run_time=1.4)

        z = complex(2, 1)
        a = Arrow(p.n2p(0), p.n2p(z), buff=0, color=VIOLET, stroke_width=6)
        za = eq("z = 2 + i", size=34, color=VIOLET).next_to(a.get_end(), RIGHT, buff=0.1)
        self.play(Create(a), Write(za))
        iz = Arrow(p.n2p(0), p.n2p(1j * z), buff=0, color=CYAN, stroke_width=6)
        iza = eq("iz = -1 + 2i", size=34, color=CYAN).next_to(iz.get_end(), UL, buff=0.1)
        rot = a.copy()
        self.play(Rotate(rot, angle=PI / 2, about_point=p.n2p(0)), run_time=1.5)
        self.play(ReplacementTransform(rot, iz), Write(iza))
        rule = eq(r"i = e^{i\pi/2}:\ \text{a quarter turn, length kept}", size=32).move_to(RIGHT * 3.0 + UP * 2.2)
        self.play(Write(rule))
        self.wait(0.6)
        self.play(FadeOut(VGroup(a, za, iz, iza)))

        # sum of two unit phasors with relative phase phi
        phi = ValueTracker(0.0)
        one = Arrow(p.n2p(0), p.n2p(1), buff=0, color=BLUE, stroke_width=6)
        second = always_redraw(lambda: Arrow(p.n2p(1), p.n2p(1 + cmath.exp(1j * phi.get_value())), buff=0,
                                             color=AMBER, stroke_width=6))
        total = always_redraw(lambda: Arrow(p.n2p(0), p.n2p(1 + cmath.exp(1j * phi.get_value())), buff=0,
                                            color=RED, stroke_width=5))
        self.play(Create(one), Create(second), Create(total))

        ax = Axes(x_range=[0, 2 * PI, PI / 2], y_range=[0, 4, 1], x_length=5.2, y_length=2.6,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 3.0 + DOWN * 1.2)
        ylab = eq(r"|1 + e^{i\varphi}|^2", size=30).next_to(ax, UP, buff=0.35).align_to(ax, LEFT)
        xlab = eq(r"\varphi", size=30).next_to(ax.x_axis, RIGHT, buff=0.1)
        formula = eq(r"= 2 + 2\cos\varphi", size=30, color=RED).next_to(ylab, RIGHT, buff=0.15)
        self.play(Create(ax), Write(ylab), Write(xlab), Write(formula))
        dot = always_redraw(lambda: Dot(ax.c2p(phi.get_value(), abs(1 + cmath.exp(1j * phi.get_value())) ** 2),
                                        color=RED, radius=0.06))
        trace = TracedPath(dot.get_center, stroke_color=RED, stroke_width=4)
        self.add(trace, dot)
        self.play(phi.animate.set_value(2 * PI), run_time=8, rate_func=linear)
        peak = label("in step: 4", 24, MUTED).next_to(ax.c2p(2 * PI, 4), LEFT, buff=0.25)
        trough = label("opposite: 0", 24, MUTED).next_to(ax.c2p(PI, 0.6), RIGHT, buff=0.35)
        self.play(FadeIn(peak), FadeIn(trough))
        self.wait(1.5)
        _ = (DEGREES, ORIGIN, Transform)
