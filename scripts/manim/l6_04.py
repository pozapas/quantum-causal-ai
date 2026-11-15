"""L6-04 Operational interventions: three scenes on one two-node quantum process.

The process (Ried et al.'s mixture of a common cause and a direct cause): a source prepares |Phi+> on
A_in and a side system E.  With probability p, B receives E (common cause; A's output is lost); with
probability 1 - p, B receives A's output through the identity channel (direct cause).  B measures Z.

ThreeOperations   graph surgery on the process: condition on a Z outcome (p(b=0|a=0) = 1), measure and
                  discard (1/2), replace A's output by |0> (1 - p/2 = 3/4) or |1> (p/2 = 1/4).
BlochImages       ThreeDScene: the Bloch sphere of A's options and its image at B under replacement
                  (a ball of radius 1 - p), under conditioning on +n ((n_x, (1-2p) n_y, n_z), swept in p),
                  and under measure-and-discard (the center).
ReplacementCut    the Choi operator of a replacement channel is I (x) sigma, derived term by term, then a
                  live sweep of p showing conditioning (1) against intervention (1 - p/2, p/2).
Every number on screen is computed here; facts() lists strings that also appear in the lesson text.
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP, Arrow, Axes, Create, Cross, DashedLine, Dot, Dot3D,
                   DecimalNumber, FadeIn, FadeOut, GrowFromEdge, Line, Rectangle, RoundedRectangle, Scene, Sphere, ThreeDAxes,
                   ThreeDScene, TracedPath, Transform, TransformMatchingTex, ValueTracker, VGroup, Write,
                   always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

P_CC = 0.5                                     # common-cause weight p used in the text


def b0_probs(p):
    """p(b = 0) at B for the four operations at A (B measures Z)."""
    cond = 1.0                                  # Lüders Z, keep a = 0: both branches deliver |0>
    nonsel = 0.5                                # Z measured, outcome discarded
    do0 = p * 0.5 + (1 - p) * 1.0               # A_out := |0>; common-cause branch gives I/2
    do1 = p * 0.5 + (1 - p) * 0.0
    return cond, nonsel, do0, do1


# exact density-matrix check of the four numbers at p = 1/2
def _check():
    phi = np.array([1, 0, 0, 1]) / math.sqrt(2)
    rho = np.outer(phi, phi)                   # order A_in, E
    P = [np.diag([1.0, 0]), np.diag([0, 1.0])]

    def to_B(rho_AoutE, p):                    # mixing channel: keep E with prob p, keep A_out with prob 1-p
        r = rho_AoutE.reshape(2, 2, 2, 2)
        keepE = np.einsum("ijik->jk", r)
        keepA = np.einsum("ijkj->ik", r)
        return p * keepE + (1 - p) * keepA
    # conditioning on a = 0
    post = np.kron(P[0], np.eye(2)) @ rho @ np.kron(P[0], np.eye(2))
    pa = np.trace(post)
    B = to_B(post / pa, P_CC)
    assert abs(pa - 0.5) < 1e-12 and abs(B[0, 0] - 1) < 1e-12
    # non-selective
    ns = sum(np.kron(Pa, np.eye(2)) @ rho @ np.kron(Pa, np.eye(2)) for Pa in P)
    assert abs(to_B(ns, P_CC)[0, 0] - 0.5) < 1e-12
    # replacement by |0>
    rE = np.einsum("ijik->jk", rho.reshape(2, 2, 2, 2))
    rep = np.kron(P[0], rE)
    assert abs(to_B(rep, P_CC)[0, 0] - 0.75) < 1e-12


_check()
assert b0_probs(P_CC) == (1.0, 0.5, 0.75, 0.25)


def cond_image(n, p):
    """Bloch vector at B after conditioning on outcome +n of a Lüders measurement at A."""
    return np.array([n[0], (1 - 2 * p) * n[1], n[2]])


def facts(L):
    """Strings shown on screen that also appear in the lesson text."""
    return ["p(b=0 \\mid a=0) = 1", "1 - p/2", "J_R = I\\otimes\\sigma", "(n_x, (1-2p)n_y, n_z)", "(1-p)\\,\\vec r_\\sigma",
            "3/4", "1/4"]


def box(txt, color, pos, w=1.7, h=0.9, size=26):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, color=color, stroke_width=4).move_to(pos)
    return VGroup(r, label(txt, size, color, "BOLD").move_to(r))


class ThreeOperations(Scene):
    def construct(self):
        title = label("Three things an agent can do at A", 36, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        # process diagram on the left
        src = box("source", MUTED, LEFT * 5.4 + DOWN * 0.6, w=1.6)
        srcl = eq(r"|\Phi^+\rangle", size=30, color=MUTED).next_to(src, DOWN, buff=0.12)
        A = box("A", BLUE, LEFT * 3.4 + UP * 0.9, w=1.3)
        mix = box("mix p", AMBER, LEFT * 1.4 + DOWN * 0.6, w=1.5, size=24)
        B = box("B", CYAN, LEFT * 1.4 + UP * 2.2, w=1.3)
        w_in = Arrow(src[0].get_top(), A[0].get_bottom() + LEFT * 0.3, color=MUTED, buff=0.05, stroke_width=4)
        w_E = Arrow(src[0].get_right(), mix[0].get_left(), color=MUTED, buff=0.05, stroke_width=4)
        w_out = Arrow(A[0].get_right(), mix[0].get_top() + LEFT * 0.4, color=BLUE, buff=0.05, stroke_width=4)
        w_B = Arrow(mix[0].get_top(), B[0].get_bottom(), color=AMBER, buff=0.05, stroke_width=4)
        tags = VGroup(eq("A_{in}", size=26, color=MUTED).next_to(w_in, LEFT, buff=0.08),
                      eq("E", size=26, color=MUTED).next_to(w_E, DOWN, buff=0.08),
                      eq("A_{out}", size=26, color=BLUE).next_to(w_out.get_center(), UP + RIGHT * 0.3, buff=0.05))
        self.play(FadeIn(VGroup(src, srcl, A, mix, B)), run_time=1)
        self.play(Create(VGroup(w_in, w_E, w_out, w_B)), FadeIn(tags), run_time=1.5)
        legend = VGroup(label("with prob. p, B gets E (common cause)", 24, MUTED),
                        label("with prob. 1 - p, B gets A's output (direct cause)", 24, MUTED)
                        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to(LEFT * 3.6 + DOWN * 2.6)
        pl = eq(r"p = 1/2,\ \ B \text{ measures } Z", size=28).next_to(legend, DOWN, buff=0.15)
        self.play(FadeIn(legend), Write(pl))

        rx = 3.6
        c, ns, d0, d1 = b0_probs(P_CC)
        # 1 conditioning
        h1 = label("1  Condition: measure Z, keep a = 0", 26, BLUE).move_to(RIGHT * rx + UP * 2.4)
        r1 = eq(r"p(b=0 \mid a=0) = 1", size=34, color=BLUE).next_to(h1, DOWN, buff=0.15)
        n1 = eq(r"\text{both branches deliver } |0\rangle \text{ to } B", size=26, color=MUTED).next_to(r1, DOWN, buff=0.1)
        self.play(FadeIn(h1), Indicate_(A, self))
        self.play(Write(r1), FadeIn(n1))
        self.wait(0.6)
        # 2 non-selective
        h2 = label("2  Measure Z, discard the outcome", 26, VIOLET).move_to(RIGHT * rx + UP * 1.0)
        r2 = eq(r"p(b=0) = 1/2", size=34, color=VIOLET).next_to(h2, DOWN, buff=0.15)
        self.play(FadeIn(h2), Write(r2))
        self.wait(0.6)
        # 3 replacement: cut the input wire
        h3 = eq(r"\text{3\ \ Replace: discard } A_{in}, \text{ prepare } |0\rangle", size=30, color=RED).move_to(RIGHT * rx + DOWN * 0.25)
        cut = Cross(w_in, stroke_color=RED, stroke_width=6, scale_factor=0.35)
        fresh = eq(r"|0\rangle", size=34, color=RED).next_to(A[0], LEFT, buff=0.2)
        self.play(FadeIn(h3), Create(cut), Write(fresh))
        r3 = eq(r"p(b=0 \mid do(|0\rangle)) = 1 - p/2 = 3/4", size=32, color=RED).next_to(h3, DOWN, buff=0.15)
        r4 = eq(r"p(b=0 \mid do(|1\rangle)) = p/2 = 1/4", size=32, color=RED).next_to(r3, DOWN, buff=0.12)
        self.play(Write(r3))
        self.play(Write(r4))
        self.wait(0.6)
        # verdict
        v1 = eq(r"\text{association: } 1 - 0 = 1", size=30, color=BLUE).move_to(RIGHT * rx + DOWN * 2.2)
        v2 = eq(r"\text{causal effect: } 3/4 - 1/4 = 1 - p", size=30, color=RED).next_to(v1, DOWN, buff=0.15)
        self.play(Write(v1))
        self.play(Write(v2))
        self.wait(2)
        assert (c, ns, d0, d1) == (1.0, 0.5, 0.75, 0.25) and d0 - d1 == 1 - P_CC


def Indicate_(mob, scene):
    from manim import Indicate
    return Indicate(mob, color=BLUE)


def fib_sphere(n=60):
    pts = []
    g = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - z * z)
        pts.append(np.array([r * math.cos(g * i), r * math.sin(g * i), z]))
    return pts


class BlochImages(ThreeDScene):
    def construct(self):
        R = 2.1
        self.set_camera_orientation(phi=68 * DEGREES, theta=-50 * DEGREES)
        axes = ThreeDAxes(x_range=[-1.3, 1.3, 1], y_range=[-1.3, 1.3, 1], z_range=[-1.3, 1.3, 1],
                          x_length=2.6 * R, y_length=2.6 * R, z_length=2.6 * R, axis_config={"color": MUTED})
        sph = Sphere(radius=R, resolution=(12, 12)).set_fill(BLUE, opacity=0.06).set_stroke(GRID, width=0.5)
        xl = eq("x", size=34, color=MUTED).move_to(axes.c2p(1.45, 0, 0))
        yl = eq("y", size=34, color=MUTED).move_to(axes.c2p(0, 1.45, 0))
        zl = eq("z", size=34, color=MUTED).move_to(axes.c2p(0, 0, 1.45))
        for m in (xl, yl, zl):
            self.add_fixed_orientation_mobjects(m)
        title = label("What each operation at A does to B's Bloch vector", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Create(axes), FadeIn(sph), Write(title), run_time=1.5)

        pts = fib_sphere(48)
        cols = [BLUE if q[1] > 0.05 else (AMBER if q[1] < -0.05 else VIOLET) for q in pts]
        dots = VGroup(*[Dot3D(axes.c2p(*q), radius=0.06, color=c, resolution=(6, 6)) for q, c in zip(pts, cols)])
        cap0 = label("A's options: pure states (blue y > 0, amber y < 0)", 24, MUTED).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(cap0)
        self.play(FadeIn(dots, lag_ratio=0.02), FadeIn(cap0), run_time=1.5)
        self.begin_ambient_camera_rotation(rate=0.08)

        # replacement: ball of radius 1 - p
        f1 = eq(r"do(\sigma):\ \vec r_B = (1-p)\,\vec r_\sigma", size=36, color=RED).to_corner(UP + LEFT, buff=0.4).shift(DOWN * 0.7)
        self.add_fixed_in_frame_mobjects(f1)
        self.play(Write(f1), FadeOut(cap0))
        shrunk = VGroup(*[Dot3D(axes.c2p(*((1 - P_CC) * q)), radius=0.06, color=c, resolution=(6, 6))
                          for q, c in zip(pts, cols)])
        self.play(Transform(dots, shrunk), run_time=2)
        n1 = label("interventions see only the direct-cause branch", 24, RED).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(n1)
        self.play(FadeIn(n1))
        self.wait(1.2)
        back = VGroup(*[Dot3D(axes.c2p(*q), radius=0.06, color=c, resolution=(6, 6)) for q, c in zip(pts, cols)])
        self.play(Transform(dots, back), FadeOut(f1), FadeOut(n1), run_time=1.2)

        # conditioning on +n, swept in p
        f2 = eq(r"\text{condition on } +\vec n:\ \vec r_B = (n_x, (1-2p)n_y, n_z)", size=34, color=BLUE)
        f2.to_corner(UP + LEFT, buff=0.4).shift(DOWN * 0.7)
        self.add_fixed_in_frame_mobjects(f2)
        self.play(Write(f2))
        def cond_set(pv):
            return VGroup(*[Dot3D(axes.c2p(*cond_image(q, pv)), radius=0.06, color=c, resolution=(6, 6))
                            for q, c in zip(pts, cols)])
        ptxt = eq("p = 0", size=36, color=AMBER).to_corner(DOWN + RIGHT, buff=0.5)
        self.add_fixed_in_frame_mobjects(ptxt)
        self.play(FadeIn(ptxt))
        p_half = eq("p = 1/2", size=36, color=AMBER).to_corner(DOWN + RIGHT, buff=0.5)
        self.add_fixed_in_frame_mobjects(p_half)
        self.remove(p_half)
        self.play(Transform(dots, cond_set(0.5)), FadeOut(ptxt), FadeIn(p_half), run_time=3, rate_func=linear)
        n2 = label("p = 1/2: the y-components cancel, a flat disk", 24, BLUE).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(n2)
        self.play(FadeIn(n2))
        self.wait(0.8)
        self.play(FadeOut(n2))
        p_one = eq("p = 1", size=36, color=AMBER).to_corner(DOWN + RIGHT, buff=0.5)
        self.add_fixed_in_frame_mobjects(p_one)
        self.remove(p_one)
        self.play(Transform(dots, cond_set(1.0)), FadeOut(p_half), FadeIn(p_one), run_time=3, rate_func=linear)
        n3 = label("p = 1: pure common cause, the sphere is mirrored in y", 24, BLUE).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(n3)
        self.play(FadeIn(n3))
        self.wait(1.2)
        self.play(FadeOut(n3), FadeOut(p_one))

        # non-selective measurement: everything to the center
        f3 = eq(r"\text{measure, discard outcome}:\ \vec r_B = \vec 0", size=34, color=VIOLET)
        f3.to_corner(UP + LEFT, buff=0.4).shift(DOWN * 0.7)
        self.add_fixed_in_frame_mobjects(f3)
        self.remove(f3)
        self.play(FadeOut(f2))
        centre = VGroup(*[Dot3D(axes.c2p(0, 0, 0), radius=0.06, color=c, resolution=(6, 6)) for c in cols])
        self.play(Write(f3))
        self.play(Transform(dots, centre), run_time=2)
        n4 = label("averaging the outcomes leaves B maximally mixed", 24, VIOLET).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(n4)
        self.play(FadeIn(n4))
        self.wait(2)
        self.stop_ambient_camera_rotation()
        _ = (OUT, ORIGIN, sph)


class ReplacementCut(Scene):
    def construct(self):
        title = label("Replacement cuts the arrow: a product Choi operator", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        conv = eq(r"\mathcal E(\rho) = \operatorname{Tr}_{in}\big[(\rho^{T}\otimes I)\,J_{\mathcal E}\big]", size=34,
                  color=MUTED).next_to(title, DOWN, buff=0.3)
        self.play(Write(conv))
        d1 = eq(r"R_\sigma(\rho)", "=", r"\operatorname{Tr}_{in}\big[(\rho^{T}\otimes I)", r"(I\otimes\sigma)", r"\big]",
                size=38).move_to(UP * 1.2)
        d2 = eq(r"R_\sigma(\rho)", "=", r"\operatorname{Tr}(\rho^{T})", r"\,\sigma", size=38).move_to(d1)
        d3 = eq(r"R_\sigma(\rho)", "=", r"\operatorname{Tr}(\rho)", r"\,\sigma", size=38).move_to(d1)
        jl = eq(r"J_R = I\otimes\sigma", size=36, color=RED).move_to(UP * 0.25)
        self.play(Write(jl))
        self.play(Write(d1))
        self.play(TransformMatchingTex(d1, d2), run_time=1.4)
        self.play(TransformMatchingTex(d2, d3), run_time=1.4)
        note = label("the output never depends on the input: the incoming arrow is cut", 24, RED).move_to(DOWN * 0.5)
        self.play(FadeIn(note))
        self.wait(1.0)
        self.play(FadeOut(VGroup(d3, note, conv)), jl.animate.move_to(RIGHT * 4.2 + UP * 2.2).scale(0.85))

        # live sweep of p
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 1.05, 0.25], x_length=6.4, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(LEFT * 2.2 + DOWN * 0.9)
        xt = VGroup(*[label(f"{v:g}", 24, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.1) for v in (0, 0.5, 1)])
        yt = VGroup(*[label(f"{v:g}", 24, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.22) for v in (0, 0.5, 1)])
        xl = eq(r"p\ (\text{common-cause weight})", size=28).next_to(ax, DOWN, buff=0.45)
        yl = eq(r"p(b=0)", size=28).next_to(ax, UP, buff=0.12).align_to(ax, LEFT)
        self.play(Create(ax), FadeIn(xt), FadeIn(yt), Write(xl), Write(yl))
        p = ValueTracker(0.0)
        dc = always_redraw(lambda: Dot(ax.c2p(p.get_value(), b0_probs(p.get_value())[0]), color=BLUE, radius=0.07))
        d0 = always_redraw(lambda: Dot(ax.c2p(p.get_value(), b0_probs(p.get_value())[2]), color=RED, radius=0.07))
        d1_ = always_redraw(lambda: Dot(ax.c2p(p.get_value(), b0_probs(p.get_value())[3]), color=AMBER, radius=0.07))
        traces = [TracedPath(d.get_center, stroke_color=col, stroke_width=4) for d, col in ((dc, BLUE), (d0, RED), (d1_, AMBER))]
        leg = VGroup(eq(r"p(b=0 \mid a=0) = 1", size=28, color=BLUE),
                     eq(r"p(b=0 \mid do(|0\rangle)) = 1 - p/2", size=28, color=RED),
                     eq(r"p(b=0 \mid do(|1\rangle)) = p/2", size=28, color=AMBER)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        leg.move_to(RIGHT * 4.0 + UP * 0.4)
        self.play(Write(leg))
        self.add(*traces, dc, d0, d1_)
        self.play(p.animate.set_value(1.0), run_time=6, rate_func=linear)
        mark = DashedLine(ax.c2p(P_CC, 0), ax.c2p(P_CC, 1), color=MUTED)
        gap = eq(r"\text{at } p = 1/2:\ \ 1 \ \text{vs}\ 3/4", size=28).move_to(RIGHT * 3.9 + DOWN * 1.3)
        gap2 = VGroup(label("conditioning exceeds", 24, MUTED), label("the do value by p/2", 24, MUTED)).arrange(DOWN, buff=0.06).next_to(gap, DOWN, buff=0.15)
        self.play(Create(mark), Write(gap), FadeIn(gap2))
        self.wait(2)
        _ = (Line, Rectangle, GrowFromEdge, GRID, CYAN, linear)
