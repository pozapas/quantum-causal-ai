"""L5-10 Noise, encoding, and error correction: four scenes.

BlochContraction    3-D Bloch sphere deformed by depolarizing (p = 0.5), phase-flip (q = 0.25) and bit-flip
                    (q = 0.25) channels: an even shrink, a cigar along z, a cigar along x.
BitFlipCodeCircuit  the three-qubit code as a circuit: encode, an X error on qubit 2, parity checks onto two
                    ancillas, syndrome 11, recovery; the state line transforms term by term.
LogicalErrorRate    derivation of p_L = 3p^2 - 2p^3, then a sweep of p with the no-code line, the crossing at 1/2
                    and the gap p(1-p)(1-2p).
ShorCode            a phase flip slips past the bit-flip code; Hadamard swaps X and Z; nine qubits in three blocks
                    catch an X inside a block and a Z by comparing block signs.
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, ORIGIN, PI, RIGHT, UL, UP, UR, Axes, Circle, Create, DashedLine, DecimalNumber,
                   Dot, Dot3D, FadeIn, FadeOut, Indicate, Line, Rectangle, RoundedRectangle, Scene, SurroundingRectangle,
                   Surface, ThreeDScene, Transform, TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw,
                   linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, VIOLET_LIGHT, eq, label

P_DEP, Q_FLIP = 0.5, 0.25
assert 1 - P_DEP == 0.5 and 1 - 2 * Q_FLIP == 0.5


def p_logical(p):
    return 3 * p ** 2 - 2 * p ** 3


assert abs(p_logical(0.1) - 0.028) < 1e-12
assert abs(p_logical(0.5) - 0.5) < 1e-12

# the syndrome table on screen (BitFlipCodeCircuit) comes from simulating the circuit of the lesson figure
from qcai.lessonfigs.l5_10 import syndrome_table  # noqa: E402
SYN = syndrome_table()
assert SYN == {"none": (0, 0), "X1": (1, 0), "X2": (1, 1), "X3": (0, 1)}


def _shor_checks_after_z(q):
    """Expectations of X1...X6 and X4...X9 on |0_L> of Shor's code after Z on qubit q (0-based)."""
    g, h = np.eye(8)[0], np.eye(8)[7]
    blk = (g + h) / np.sqrt(2)
    psi = np.kron(np.kron(blk, blk), blk).reshape([2] * 9)
    psi = psi * np.where(np.arange(2) == 1, -1, 1).reshape([2 if k == q else 1 for k in range(9)])

    def x_on(v, qs):
        for k in qs:
            v = np.flip(v, axis=k)
        return v

    return [round(float(np.sum(psi * x_on(psi, qs)))) for qs in (range(0, 6), range(3, 9))]


assert _shor_checks_after_z(6) == [1, -1]          # Z on qubit 7: X1...X6 = +1, X4...X9 = -1
for _p in np.linspace(0.01, 0.99, 99):
    assert abs((_p - p_logical(_p)) - _p * (1 - _p) * (1 - 2 * _p)) < 1e-12


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["p = 0.5", "q = 0.25", "1 - 2q", "Z_1Z_2", "Z_2Z_3", "3p^2 - 2p^3", "0.028", "p(1-p)(1-2p)", "X_4\\cdots X_9"]


class BlochContraction(ThreeDScene):
    def construct(self):
        R = 1.9
        self.set_camera_orientation(phi=70 * DEGREES, theta=25 * DEGREES)
        title = label("Noise channels deform the Bloch ball", 32, INK, "BOLD").to_corner(UP + LEFT, buff=0.35)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1.0)

        sphere = Surface(lambda u, v: R * np.array([math.cos(u) * math.sin(v), math.sin(u) * math.sin(v), math.cos(v)]),
                         u_range=[0, 2 * PI], v_range=[0, PI], resolution=(18, 10), fill_opacity=0.08,
                         stroke_color=VIOLET_LIGHT, stroke_width=0.6, checkerboard_colors=[VIOLET_LIGHT, VIOLET_LIGHT])
        dirs = [((0, 0, 1), BLUE), ((0, 0, -1), BLUE), ((1, 0, 0), RED), ((-1, 0, 0), RED), ((0, 1, 0), AMBER), ((0, -1, 0), AMBER)]
        arrows = VGroup()
        for d, col in dirs:
            v = R * np.array(d, dtype=float)
            arrows.add(VGroup(Line(ORIGIN, v, color=col, stroke_width=4), Dot3D(v, radius=0.08, color=col, resolution=(6, 6))))
        body = VGroup(sphere, arrows)
        labs = [eq("x", size=32, color=MUTED).move_to([R + 0.55, 0, 0]),
                eq("y", size=32, color=MUTED).move_to([0, R + 0.55, 0]),
                eq("z", size=32, color=MUTED).move_to([0, 0, R + 0.55])]
        self.play(Create(sphere), Create(arrows), run_time=2.0)
        for lb in labs:
            self.add_fixed_orientation_mobjects(lb)
        key = VGroup(eq(r"|0\rangle, |1\rangle", size=28, color=BLUE), eq(r"|{+}\rangle, |{-}\rangle", size=28, color=RED),
                     eq(r"|{+i}\rangle, |{-i}\rangle", size=28, color=AMBER)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        key.to_corner(DOWN + LEFT, buff=0.4)
        self.add_fixed_in_frame_mobjects(key)
        self.play(FadeIn(key))
        self.begin_ambient_camera_rotation(rate=0.08)

        stages = [
            ("Depolarizing", r"p = 0.5", r"\vec r \mapsto (1 - p)\,\vec r", "every direction halves",
             np.diag([1 - P_DEP] * 3)),
            ("Phase flip", r"q = 0.25", r"(r_x, r_y) \mapsto (1 - 2q)\,(r_x, r_y)", "z untouched: Z counts cannot see it",
             np.diag([1 - 2 * Q_FLIP, 1 - 2 * Q_FLIP, 1])),
            ("Bit flip", r"q = 0.25", r"(r_y, r_z) \mapsto (1 - 2q)\,(r_y, r_z)", "x untouched: |+> and |-> survive",
             np.diag([1, 1 - 2 * Q_FLIP, 1 - 2 * Q_FLIP])),
        ]
        prev = None
        for name, par, rule, note, M in stages:
            panel = VGroup(label(name, 30, INK, "BOLD"), eq(par, size=34, color=VIOLET), eq(rule, size=30),
                           label(note, 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            panel.to_edge(RIGHT, buff=0.3).to_edge(UP, buff=1.1)
            self.add_fixed_in_frame_mobjects(panel)
            self.remove(panel)
            anims = [FadeIn(panel)] + ([FadeOut(prev)] if prev is not None else [])
            self.play(*anims, run_time=0.8)
            self.play(body.animate.apply_matrix(M), run_time=2.2)
            self.wait(1.6)
            self.play(body.animate.apply_matrix(np.linalg.inv(M)), run_time=1.2)
            prev = panel
        self.stop_ambient_camera_rotation()
        end = eq(r"\text{flip channels shrink two axes by } 1 - 2q = 0.5", size=30).to_edge(DOWN, buff=0.4).shift(RIGHT * 1.6)
        self.add_fixed_in_frame_mobjects(end)
        self.play(FadeIn(end))
        self.wait(1.5)


class BitFlipCodeCircuit(Scene):
    def construct(self):
        title = label("The bit-flip code: encode, detect, correct", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)
        ys = [2.25, 1.45, 0.65, -0.35, -1.15]
        x0, x1 = -5.2, 3.0
        names = [r"q_1", r"q_2", r"q_3", r"a_1", r"a_2"]
        wires = VGroup(*[Line([x0, y, 0], [x1, y, 0], color=MUTED, stroke_width=2) for y in ys])
        wl = VGroup(*[eq(n, size=32).next_to([x0, y, 0], LEFT, buff=0.15) for n, y in zip(names, ys)])
        self.play(Create(wires), Write(wl), run_time=1.2)

        def cnot(x, c, t):
            yc, yt = ys[c], ys[t]
            return VGroup(Line([x, yc, 0], [x, yt, 0], color=INK, stroke_width=3), Dot([x, yc, 0], color=INK, radius=0.08),
                          Circle(radius=0.17, color=INK, stroke_width=3).move_to([x, yt, 0]),
                          Line([x - 0.17, yt, 0], [x + 0.17, yt, 0], color=INK, stroke_width=3),
                          Line([x, yt - 0.17, 0], [x, yt + 0.17, 0], color=INK, stroke_width=3))

        def box(x, q, txt, col=INK, fill="#ffffff"):
            r = Rectangle(width=0.55, height=0.5, color=col, stroke_width=3).set_fill(fill, opacity=1).move_to([x, ys[q], 0])
            return VGroup(r, eq(txt, size=30, color=col).move_to(r))

        def state(*parts):
            return eq(*parts, size=40).move_to([-1.1, -2.55, 0])

        st = state(r"(\alpha|0\rangle + \beta|1\rangle)", r"|00\rangle")
        self.play(Write(st))

        enc = VGroup(cnot(-4.4, 0, 1), cnot(-3.7, 0, 2))
        band = Rectangle(width=1.3, height=3.2, stroke_width=0).set_fill(VIOLET_LIGHT, opacity=0.25).move_to([-4.05, 1.45, 0])
        self.play(FadeIn(band), Create(enc), run_time=1.4)
        st2 = state(r"\alpha", r"|000\rangle", "+", r"\beta", r"|111\rangle")
        self.play(Transform(st, st2), run_time=1.2)
        self.wait(0.6)

        err = box(-2.75, 1, "X", RED, "#fee2e2")
        self.play(FadeIn(err, scale=1.4), run_time=0.8)
        st3 = state(r"\alpha", r"|010\rangle", "+", r"\beta", r"|101\rangle")
        self.remove(st)
        st = st2
        self.add(st)
        self.play(TransformMatchingTex(st, st3), run_time=1.4)
        st = st3
        self.wait(0.6)

        syn = VGroup(cnot(-1.9, 0, 3), cnot(-1.25, 1, 3), cnot(-0.6, 1, 4), cnot(0.05, 2, 4))
        band2 = Rectangle(width=2.6, height=4.0, stroke_width=0).set_fill(CYAN, opacity=0.12).move_to([-0.92, 0.55, 0])
        self.play(FadeIn(band2), Create(syn), run_time=2.0)
        meas = VGroup(box(0.9, 3, r"M"), box(0.9, 4, r"M"))
        self.play(FadeIn(meas))
        outs = VGroup(eq("1", size=34, color=RED).next_to(meas[0], UR, buff=0.05),
                      eq("1", size=34, color=RED).next_to(meas[1], UR, buff=0.05))
        checks = VGroup(eq(r"Z_1Z_2 = -1", size=30, color=RED), eq(r"Z_2Z_3 = -1", size=30, color=RED)).arrange(
            DOWN, aligned_edge=LEFT, buff=0.12).move_to([5.1, 2.3, 0])
        self.play(FadeIn(outs), Write(checks))

        rows = [("00", "none"), ("10", r"X_1"), ("11", r"X_2"), ("01", r"X_3")]
        table = VGroup(*[VGroup(eq(a, size=30), eq(r"\to", size=30), eq(b if b != "none" else r"\text{none}", size=30)).arrange(RIGHT, buff=0.2)
                         for a, b in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([5.0, 0.2, 0])
        thead = label("syndrome table", 24, MUTED).next_to(table, UP, buff=0.2)
        self.play(FadeIn(thead), FadeIn(table))
        hl = SurroundingRectangle(table[2], color=RED, buff=0.08)
        self.play(Create(hl))
        unchanged = label("data state unchanged by the checks", 24, MUTED).next_to(st, DOWN, buff=0.2)
        self.play(FadeIn(unchanged))
        self.wait(0.8)

        fix = box(2.2, 1, "X", CYAN, "#cffafe")
        self.play(FadeIn(fix, scale=1.4), FadeOut(unchanged))
        st4 = state(r"\alpha", r"|000\rangle", "+", r"\beta", r"|111\rangle")
        self.play(TransformMatchingTex(st, st4), run_time=1.4)
        st = st4
        same = label("the syndrome is the same for every alpha and beta", 24, VIOLET).next_to(st, DOWN, buff=0.2)
        self.play(FadeIn(same))
        self.wait(2.0)
        _ = (Indicate, RoundedRectangle, UL, BLUE, AMBER, GRID)


class LogicalErrorRate(Scene):
    def construct(self):
        title = label("When does the code help?", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.8)
        a = eq("p_L", "=", r"\binom{3}{2}p^2(1-p)", "+", "p^3", size=42).move_to(UP * 1.6)
        b = eq("p_L", "=", "3p^2", "-", "3p^3", "+", "p^3", size=42).move_to(UP * 1.6)
        c = eq("p_L", "=", "3p^2", "-", "2p^3", size=42).move_to(UP * 1.6)
        why = label("fails when two or three of the three qubits flip", 26, MUTED).next_to(a, DOWN, buff=0.35)
        self.play(Write(a), FadeIn(why))
        self.wait(1.0)
        self.play(TransformMatchingTex(a, b), run_time=1.6)
        self.wait(0.6)
        self.play(TransformMatchingTex(b, c), run_time=1.6)
        self.wait(0.8)
        small = eq(r"p_L = 3p^2 - 2p^3", size=34, color=VIOLET).move_to([3.9, 2.35, 0])
        self.play(FadeOut(why), Transform(c, small), run_time=1.0)

        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 1, 0.25], x_length=6.0, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False}).move_to([-2.6, -0.75, 0])
        ticks = VGroup(*[label(t, 22, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.12) for v, t in ((0, "0"), (0.5, "0.5"), (1, "1"))],
                       *[label(t, 22, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.12) for v, t in ((0.5, "0.5"), (1, "1"))])
        xl = label("physical flip probability p", 24, MUTED).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = label("logical error", 24, MUTED).next_to(ax.y_axis, UP, buff=0.15).shift(RIGHT * 0.6)
        line = DashedLine(ax.c2p(0, 0), ax.c2p(1, 1), color=MUTED, stroke_width=3)
        curve = ax.plot(p_logical, x_range=[0, 1, 0.01], color=VIOLET, stroke_width=5)
        self.play(Create(ax), FadeIn(ticks), FadeIn(xl), FadeIn(yl), run_time=1.2)
        self.play(Create(line), Create(curve), run_time=1.6)
        leg = VGroup(VGroup(DashedLine(ORIGIN, RIGHT * 0.5, color=MUTED), label("no code: p", 24, MUTED)).arrange(RIGHT, buff=0.15),
                     VGroup(Line(ORIGIN, RIGHT * 0.5, color=VIOLET, stroke_width=5), label("three-qubit code", 24, VIOLET)).arrange(RIGHT, buff=0.15)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([3.9, 1.45, 0])
        self.play(FadeIn(leg))

        p = ValueTracker(0.0)
        d1 = always_redraw(lambda: Dot(ax.c2p(p.get_value(), p.get_value()), color=MUTED, radius=0.07))
        d2 = always_redraw(lambda: Dot(ax.c2p(p.get_value(), p_logical(p.get_value())), color=RED, radius=0.08))
        gap = always_redraw(lambda: Line(ax.c2p(p.get_value(), p.get_value()), ax.c2p(p.get_value(), p_logical(p.get_value())),
                                         color=AMBER, stroke_width=5))
        ro = always_redraw(lambda: VGroup(
            VGroup(eq("p =", size=34), DecimalNumber(p.get_value(), num_decimal_places=3, font_size=34, color=INK)).arrange(RIGHT, buff=0.15),
            VGroup(eq("p_L =", size=34, color=RED), DecimalNumber(p_logical(p.get_value()), num_decimal_places=3, font_size=34, color=RED)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([3.9, 0.15, 0]))
        self.add(gap, d1, d2, ro)
        self.play(p.animate.set_value(0.1), run_time=2.0, rate_func=linear)
        at01 = eq(r"p = 0.1:\ p_L = 0.028", size=32, color=RED).move_to([3.9, -1.1, 0])
        self.play(Write(at01))
        self.wait(1.0)
        self.play(p.animate.set_value(0.5), run_time=4.0, rate_func=linear)
        cross = DashedLine(ax.c2p(0.5, 0), ax.c2p(0.5, 0.5), color=AMBER, stroke_width=3)
        cl = label("break-even at p = 1/2", 24, AMBER).next_to(ax.c2p(0.5, 0.12), RIGHT, buff=0.15)
        self.play(Create(cross), FadeIn(cl))
        self.play(p.animate.set_value(1.0), run_time=3.0, rate_func=linear)
        worse = label("above 1/2 the code hurts", 24, MUTED).move_to([3.9, -1.75, 0])
        self.play(FadeIn(worse))
        gapf = eq(r"p - p_L = p(1-p)(1-2p)", size=34, color=AMBER).move_to([3.9, -2.6, 0])
        self.play(Write(gapf))
        self.wait(2.0)
        _ = (Rectangle, CYAN, GRID, BLUE)


class ShorCode(Scene):
    def construct(self):
        title = label("Phase flips, and how Shor's code catches them", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)

        # 1. the bit-flip code misses Z
        s1 = eq(r"\alpha", r"|000\rangle", "+", r"\beta", r"|111\rangle", size=40).move_to(UP * 1.8)
        self.play(Write(s1))
        zl = label("a Z hits qubit 2", 26, RED).next_to(s1, DOWN, buff=0.3)
        self.play(FadeIn(zl))
        s2 = eq(r"\alpha", r"|000\rangle", "-", r"\beta", r"|111\rangle", size=40).move_to(s1)
        self.play(TransformMatchingTex(s1, s2), run_time=1.2)
        chk = VGroup(eq(r"Z_1Z_2 = +1", size=34), eq(r"Z_2Z_3 = +1", size=34)).arrange(RIGHT, buff=0.8).next_to(zl, DOWN, buff=0.35)
        self.play(Write(chk))
        miss = label("both checks pass: the error is missed and the logical phase is flipped", 26, RED).next_to(chk, DOWN, buff=0.3)
        self.play(FadeIn(miss))
        self.wait(1.5)
        self.play(FadeOut(VGroup(s2, zl, chk, miss)))

        # 2. Hadamard swaps the roles of X and Z
        hz = eq(r"HZH = X", r"\qquad", r"HXH = Z", size=42).move_to(UP * 1.9)
        self.play(Write(hz))
        cw = eq(r"|0_L\rangle = |{+}{+}{+}\rangle", r"\qquad", r"|1_L\rangle = |{-}{-}{-}\rangle", size=40).next_to(hz, DOWN, buff=0.4)
        self.play(Write(cw))
        sw = label("in the +/- basis a Z flips a sign, just as X flips a bit", 26, MUTED).next_to(cw, DOWN, buff=0.3)
        self.play(FadeIn(sw))
        self.wait(1.5)
        self.play(FadeOut(VGroup(hz, cw, sw)))

        # 3. nine qubits, three blocks
        xs = [-4.6, -3.8, -3.0, -0.8, 0.0, 0.8, 3.0, 3.8, 4.6]
        y = 1.3
        circles = VGroup(*[Circle(radius=0.3, color=VIOLET, stroke_width=3).set_fill(VIOLET_LIGHT, opacity=0.3).move_to([x, y, 0]) for x in xs])
        nums = VGroup(*[label(str(i + 1), 24, INK).move_to([x, y, 0]) for i, x in enumerate(xs)])
        frames = VGroup(*[RoundedRectangle(width=2.6, height=1.0, corner_radius=0.2, color=MUTED, stroke_width=2).move_to([xs[3 * k + 1], y, 0])
                          for k in range(3)])
        blab = VGroup(*[eq(r"|000\rangle \pm |111\rangle", size=30).next_to(frames[k], DOWN, buff=0.2) for k in range(3)])
        head = label("outer phase-flip code over three inner bit-flip blocks", 26, MUTED).move_to(UP * 2.55)
        self.play(FadeIn(head), Create(frames), FadeIn(circles), FadeIn(nums), run_time=1.6)
        self.play(Write(blab))

        e1 = label("X", 26, RED, "BOLD").next_to(circles[4], UP, buff=0.32)
        self.play(circles[4].animate.set_stroke(RED, width=5), FadeIn(e1))
        c1 = eq(r"Z_4Z_5 = -1,\ \ Z_5Z_6 = -1", size=32, color=RED).move_to([0, -0.9, 0])
        f1 = label("inside block 2: flip qubit 5 back", 24, MUTED).next_to(c1, DOWN, buff=0.15)
        self.play(Write(c1), FadeIn(f1))
        self.play(circles[4].animate.set_stroke(VIOLET, width=3), FadeOut(e1))
        self.wait(0.6)
        self.play(FadeOut(VGroup(c1, f1)))

        e2 = label("Z", 26, RED, "BOLD").next_to(circles[6], UP, buff=0.32)
        flipped = eq(r"|000\rangle \mp |111\rangle", size=30, color=RED).move_to(blab[2])
        self.play(FadeIn(e2), frames[2].animate.set_color(RED), Transform(blab[2], flipped))
        c2 = VGroup(eq(r"X_1\cdots X_6 = +1", size=32), eq(r"X_4\cdots X_9 = -1", size=32, color=RED)).arrange(RIGHT, buff=0.8)
        c2.move_to([0, -0.9, 0])
        f2 = label("block signs disagree at block 3: apply Z to any qubit of block 3", 24, MUTED).next_to(c2, DOWN, buff=0.15)
        self.play(Write(c2), FadeIn(f2))
        back = eq(r"|000\rangle \pm |111\rangle", size=30).move_to(blab[2])
        self.play(frames[2].animate.set_color(MUTED), Transform(blab[2], back), FadeOut(e2))
        self.wait(0.6)
        end = eq(r"\text{any one-qubit error} = c_0 I + c_1 X + c_2 Z + c_3 XZ", size=34, color=VIOLET).move_to([0, -2.85, 0])
        self.play(Write(end))
        self.wait(2.0)
        _ = (LEFT, RIGHT, DOWN, AMBER, CYAN, BLUE, GRID, Dot, Indicate, SurroundingRectangle, linear, DecimalNumber)
