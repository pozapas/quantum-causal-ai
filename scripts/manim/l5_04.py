"""L5-04 Tensor products and entanglement: three scenes.

SchmidtEllipse  a two-qubit pure state is a 2x2 coefficient matrix C; as a linear map C sends the unit circle to an
                ellipse whose semi-axes are the Schmidt coefficients.  |+>|0> collapses the circle to a segment
                (rank 1, product); cos(t)|00> + sin(t)|11> opens it to a circle of radius 1/sqrt2 at t = pi/4, with a
                live trace of the entanglement entropy.
CnotEntangles   H then CNOT on |00>: the amplitude bars, the state formula and the coefficient matrix change step by
                step; det C goes from 0 to 1/2.
BellVsMixture   400 simulated shots each of the Bell state and the coin-flip mixture of |00> and |11>, measured in the
                Z basis and the X basis: the histograms agree in Z and separate in X; then the witness <XX> + <ZZ>.
Conventions: |ab> = |a>(x)|b>, A is the left factor, C[i, j] = <ij|psi>.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from manim import (DOWN, LEFT, RIGHT, UP, Axes, Circle, Create, DashedLine, DecimalNumber, Dot, FadeIn, FadeOut,  # noqa: E402
                   Line, NumberPlane, Rectangle, ReplacementTransform, Scene, SurroundingRectangle, TracedPath,
                   Transform, TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear, ApplyMatrix,
                   ParametricFunction, Indicate)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label  # noqa: E402
from qcai.lessonfigs.l5_04 import BELL, entanglement_entropy, joint_probs, bell_rho, mixture_rho, shots  # noqa: E402

S2 = 1 / math.sqrt(2)
# product state |+>|0>: coefficient matrix and its singular values
C_PROD = np.array([[S2, 0], [S2, 0]])
SV_PROD = np.linalg.svd(C_PROD, compute_uv=False)
assert abs(SV_PROD[0] - 1) < 1e-12 and abs(SV_PROD[1]) < 1e-12 and abs(np.linalg.det(C_PROD)) < 1e-12
# Bell state: singular values 1/sqrt2, 1/sqrt2, det 1/2, entropy 1
SV_BELL = np.linalg.svd(BELL.reshape(2, 2).real, compute_uv=False)
assert np.allclose(SV_BELL, [S2, S2]) and abs(np.linalg.det(BELL.reshape(2, 2).real) - 0.5) < 1e-12
assert abs(entanglement_entropy(BELL) - 1) < 1e-12
# correlations: Bell <ZZ> = <XX> = 1, coin-flip mixture <ZZ> = 1, <XX> = 0
def _E(rho, t):
    p = joint_probs(rho, t, t)
    return p[0] - p[1] - p[2] + p[3]
assert abs(_E(bell_rho(), 0) - 1) < 1e-12 and abs(_E(bell_rho(), math.pi / 2) - 1) < 1e-12
assert abs(_E(mixture_rho(), 0) - 1) < 1e-12 and abs(_E(mixture_rho(), math.pi / 2)) < 1e-12

N_SHOTS = 400
SHOTS = shots(N_SHOTS, seed=5)

F_DET_THETA = r"\det C = \cos\theta\,\sin\theta"
F_SCHMIDT_BELL = r"s_1 = s_2 = 1/\sqrt{2}"
F_DET_HALF = r"\det C = 1/2"
F_WITNESS = r"\langle XX\rangle + \langle ZZ\rangle \le 1"


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [F_DET_THETA, F_SCHMIDT_BELL, F_DET_HALF, F_WITNESS, r"E = 1"]


class SchmidtEllipse(Scene):
    def construct(self):
        title = label("A two-qubit state is a 2 x 2 matrix", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        unit = 1.75
        p = NumberPlane(x_range=[-1.4, 1.4, 0.5], y_range=[-1.4, 1.4, 0.5], x_length=2.8 * unit, y_length=2.8 * unit,
                        background_line_style={"stroke_color": GRID, "stroke_width": 1},
                        axis_config={"color": MUTED}).shift(LEFT * 3.5 + DOWN * 0.45)
        o = p.c2p(0, 0)
        self.play(Write(title), Create(p), run_time=1.4)
        gen = eq(r"|\psi\rangle = \sum_{i,j} C_{ij}\,|ij\rangle", size=40).move_to(RIGHT * 3.3 + UP * 2.4)
        self.play(Write(gen))

        circ = Circle(radius=unit, color=MUTED, stroke_width=2).move_to(o)
        circ_lab = label("unit circle", 24, MUTED).next_to(circ, UP, buff=0.08).shift(LEFT * 1.2)
        self.play(Create(circ), FadeIn(circ_lab))

        st = eq(r"|+\rangle|0\rangle:\quad C = \tfrac{1}{\sqrt{2}}\begin{pmatrix}1 & 0\\ 1 & 0\end{pmatrix}",
                size=36, color=BLUE).move_to(RIGHT * 3.3 + UP * 1.15)
        self.play(Write(st))
        img = circ.copy().set_color(VIOLET).set_stroke(width=5)
        self.play(ApplyMatrix(C_PROD, img, about_point=o), run_time=2.2)
        r1 = VGroup(eq(r"\det C = 0", size=36), label("rank 1: the circle collapses to a segment", 26, MUTED),
                    eq(rf"s_1 = {SV_PROD[0]:.0f},\ s_2 = {abs(SV_PROD[1]):.0f}", size=36, color=VIOLET))
        r1.arrange(DOWN, buff=0.22).move_to(RIGHT * 3.3 + DOWN * 0.4)
        for m in r1:
            self.play(FadeIn(m), run_time=0.7)
        prod = label("product state: one direction for A, one for B", 26, BLUE).move_to(RIGHT * 3.3 + DOWN * 2.0)
        self.play(FadeIn(prod))
        self.wait(1.2)
        self.play(FadeOut(VGroup(st, r1, prod, img)))

        # sweep cos(t)|00> + sin(t)|11>
        th = ValueTracker(0.0)
        st2 = eq(r"\cos\theta\,|00\rangle + \sin\theta\,|11\rangle", size=38, color=BLUE).move_to(RIGHT * 3.3 + UP * 1.3)
        cm = eq(r"C = \begin{pmatrix}\cos\theta & 0\\ 0 & \sin\theta\end{pmatrix}", size=36).move_to(RIGHT * 3.3 + UP * 0.2)
        det = eq(F_DET_THETA, size=34).move_to(RIGHT * 3.3 + DOWN * 0.75)
        self.play(Write(st2), Write(cm))
        self.play(Write(det))

        def ellipse():
            t = th.get_value()
            a, b = math.cos(t), math.sin(t)
            return ParametricFunction(lambda u: p.c2p(a * math.cos(u), b * math.sin(u)), t_range=[0, 2 * math.pi],
                                      color=VIOLET, stroke_width=5)
        ell = always_redraw(ellipse)
        self.play(Create(ell))
        ax = Axes(x_range=[0, math.pi / 4, math.pi / 8], y_range=[0, 1, 0.5], x_length=3.6, y_length=1.5,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 3.0 + DOWN * 2.55)
        ylab = eq(r"E", size=30).next_to(ax.y_axis, LEFT, buff=0.15)
        xlab = eq(r"\theta", size=30).next_to(ax.x_axis, RIGHT, buff=0.12)
        one = label("1", 24, MUTED).next_to(ax.c2p(0, 1), LEFT, buff=0.28)
        self.play(Create(ax), FadeIn(ylab), FadeIn(xlab), FadeIn(one))

        def ent(t):
            c2 = math.cos(t) ** 2
            s2 = 1 - c2
            return -sum(q * math.log2(q) for q in (c2, s2) if q > 1e-12)
        dot = always_redraw(lambda: Dot(ax.c2p(th.get_value(), ent(th.get_value())), color=RED, radius=0.06))
        trace = TracedPath(dot.get_center, stroke_color=RED, stroke_width=4)
        def readout():
            t = th.get_value()
            g1 = VGroup(eq("s_1 =", size=36, color=VIOLET),
                        DecimalNumber(math.cos(t), num_decimal_places=3, font_size=36, color=VIOLET)).arrange(RIGHT, buff=0.15)
            g2 = VGroup(eq("s_2 =", size=36, color=VIOLET),
                        DecimalNumber(math.sin(t), num_decimal_places=3, font_size=36, color=VIOLET)).arrange(RIGHT, buff=0.15)
            return VGroup(g1, g2).arrange(RIGHT, buff=0.6)
        s1v = always_redraw(lambda: readout().next_to(p, DOWN, buff=0.12))
        self.add(trace, dot, s1v)
        self.play(th.animate.set_value(math.pi / 4), run_time=7, rate_func=linear)
        fin = VGroup(eq(r"\theta = \pi/4:\ |\Phi^+\rangle", size=34, color=RED), eq(F_SCHMIDT_BELL, size=34, color=RED),
                     eq(r"E = 1", size=34, color=RED)).arrange(RIGHT, buff=0.35)
        fin.to_edge(UP, buff=0.3)
        self.play(FadeOut(title), FadeIn(fin))
        self.play(Indicate(ell, color=RED))
        self.wait(1.6)


class CnotEntangles(Scene):
    def construct(self):
        title = label("H then CNOT turns a product state into a Bell state", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        yA, yB, x0, x1 = 2.2, 1.2, -6.3, -0.9
        wires = VGroup(Line([x0 + 0.9, yA, 0], [x1, yA, 0], color=INK), Line([x0 + 0.9, yB, 0], [x1, yB, 0], color=INK))
        ins = VGroup(eq(r"A\ |0\rangle", size=32).next_to([x0 + 0.9, yA, 0], LEFT, buff=0.1),
                     eq(r"B\ |0\rangle", size=32).next_to([x0 + 0.9, yB, 0], LEFT, buff=0.1))
        hbox = VGroup(Rectangle(width=0.7, height=0.7, color=BLUE, fill_color="#ffffff", fill_opacity=1).move_to([-3.9, yA, 0]))
        hbox.add(eq("H", size=34, color=BLUE).move_to(hbox))
        ctrl = Dot([-2.3, yA, 0], color=VIOLET, radius=0.1)
        targ = VGroup(Circle(radius=0.22, color=VIOLET).move_to([-2.3, yB, 0]),
                      Line([-2.3, yB - 0.22, 0], [-2.3, yB + 0.22, 0], color=VIOLET),
                      Line([-2.52, yB, 0], [-2.08, yB, 0], color=VIOLET))
        cl = Line([-2.3, yA, 0], [-2.3, yB + 0.22, 0], color=VIOLET)
        self.play(Create(wires), FadeIn(ins), FadeIn(hbox), FadeIn(VGroup(ctrl, cl, targ)))

        # amplitude bars
        base_y, hmax, bx = -3.2, 2.3, [-5.4, -4.3, -3.2, -2.1]
        names = ["00", "01", "10", "11"]
        amps = [np.array([1, 0, 0, 0.0]), np.array([S2, 0, S2, 0]), BELL.real.copy()]
        assert np.allclose(np.kron([S2, S2], [1, 0]), amps[1])
        cnot = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
        assert np.allclose(cnot @ amps[1], amps[2])
        axis = Line([-6.0, base_y, 0], [-1.5, base_y, 0], color=MUTED)
        tick = VGroup(*[label(n, 24, MUTED).move_to([x, base_y - 0.3, 0]) for x, n in zip(bx, names)])
        alab = label("amplitudes", 24, MUTED).move_to([-3.75, base_y + hmax + 0.35, 0])

        def bars(a):
            return VGroup(*[Rectangle(width=0.6, height=max(v * hmax, 0.001), color=VIOLET, fill_color=VIOLET,
                                      fill_opacity=0.75, stroke_width=1).move_to([x, base_y + v * hmax / 2, 0])
                            for x, v in zip(bx, a)])
        b = bars(amps[0])
        self.play(Create(axis), FadeIn(tick), FadeIn(alab), FadeIn(b))

        slice_ = DashedLine([-5.0, yA + 0.6, 0], [-5.0, yB - 0.6, 0], color=AMBER)
        f0 = eq(r"|00\rangle", size=38).move_to(RIGHT * 3.3 + UP * 2.0)
        c0 = eq(r"C = \begin{pmatrix}1 & 0\\ 0 & 0\end{pmatrix}", size=34).move_to(RIGHT * 3.3 + DOWN * 1.1)
        d0 = eq(r"\det C = 0", size=34).next_to(c0, DOWN, buff=0.3)
        self.play(Create(slice_), Write(f0), Write(c0), Write(d0))
        self.wait(0.4)

        # after H on A
        f1 = eq(r"\tfrac{1}{\sqrt2}(", r"|00\rangle", "+", r"|10\rangle", ")", size=38).move_to(f0)
        fac = eq(r"= |+\rangle\,|0\rangle", size=34, color=BLUE).next_to(f1, DOWN, buff=0.25)
        c1 = eq(r"C = \tfrac{1}{\sqrt2}\begin{pmatrix}1 & 0\\ 1 & 0\end{pmatrix}", size=34).move_to(c0)
        self.play(slice_.animate.move_to([-3.1, (yA + yB) / 2, 0]), Indicate(hbox, color=BLUE), run_time=1.2)
        self.play(TransformMatchingTex(f0, f1), Transform(b, bars(amps[1])), ReplacementTransform(c0, c1), run_time=1.5)
        self.play(FadeIn(fac))
        self.wait(0.6)

        # after CNOT
        rule = eq(r"\mathrm{CNOT}\,|a\,b\rangle = |a,\ b\oplus a\rangle", size=32, color=VIOLET).move_to(RIGHT * 3.3 + UP * 0.6)
        self.play(slice_.animate.move_to([-1.4, (yA + yB) / 2, 0]), Indicate(VGroup(ctrl, targ), color=VIOLET), FadeIn(rule),
                  run_time=1.2)
        f2 = eq(r"\tfrac{1}{\sqrt2}(", r"|00\rangle", "+", r"|11\rangle", ")", size=38, color=RED).move_to(f0)
        c2 = eq(r"C = \tfrac{1}{\sqrt2}\begin{pmatrix}1 & 0\\ 0 & 1\end{pmatrix}", size=34, color=RED).move_to(c0)
        d2 = eq(F_DET_HALF, size=34, color=RED).move_to(d0)
        moving = b[2].copy()
        self.play(FadeOut(fac), moving.animate.move_to([bx[3], base_y + S2 * hmax / 2, 0]),
                  b[2].animate.stretch_to_fit_height(0.001).move_to([bx[2], base_y, 0]), run_time=1.4)
        self.play(TransformMatchingTex(f1, f2), ReplacementTransform(c1, c2), ReplacementTransform(d0, d2), run_time=1.5)
        nofac = label("no way to write it as (A state)(B state)", 26, RED).next_to(f2, DOWN, buff=0.25)
        self.play(FadeIn(nofac))
        box = SurroundingRectangle(VGroup(c2, d2), color=RED, buff=0.15)
        self.play(Create(box))
        self.wait(1.8)


class BellVsMixture(Scene):
    def construct(self):
        title = label("Same Z statistics, different X statistics", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title))
        cols = {"bell": -3.6, "mix": 3.6}
        heads = VGroup(eq(r"|\Phi^+\rangle = \tfrac{1}{\sqrt2}(|00\rangle + |11\rangle)", size=32, color=VIOLET)
                       .move_to([cols["bell"], 2.85, 0]),
                       eq(r"\text{coin flip: } |00\rangle \text{ or } |11\rangle", size=32, color=AMBER)
                       .move_to([cols["mix"], 2.85, 0]))
        self.play(FadeIn(heads))
        rows = {"Z": 0.45, "X": -2.55}
        tick_names = {"Z": ["00", "01", "10", "11"], "X": ["++", "+-", "-+", "--"]}
        k = ValueTracker(0)
        scale = 3.0     # bar height per unit relative frequency
        dx = 0.95
        charts = VGroup()
        readouts = VGroup()
        for r, by in rows.items():
            charts.add(label(f"{r} basis", 28, INK, "BOLD").move_to([0, by + 0.75, 0]))
        for c, cx in cols.items():
            color = VIOLET if c == "bell" else AMBER
            for r, by in rows.items():
                data = SHOTS[f"{c}_{r}"]
                xs = [cx - 1.5 * dx + i * dx for i in range(4)]
                axis = Line([cx - 2.1, by, 0], [cx + 2.1, by, 0], color=MUTED)
                ticks = VGroup(*[label(n, 24, MUTED).move_to([x, by - 0.28, 0]) for x, n in zip(xs, tick_names[r])])

                def make(data=data, xs=xs, by=by, color=color):
                    n = int(round(k.get_value()))
                    cnt = np.bincount(data[:n], minlength=4) if n else np.zeros(4)
                    fr = cnt / max(n, 1)
                    return VGroup(*[Rectangle(width=0.62, height=max(f * scale, 0.001), color=color, fill_color=color,
                                              fill_opacity=0.75, stroke_width=1).move_to([x, by + f * scale / 2, 0])
                                    for x, f in zip(xs, fr)])

                def agree(data=data, cx=cx, by=by, color=color):
                    n = int(round(k.get_value()))
                    cnt = np.bincount(data[:n], minlength=4) if n else np.zeros(4)
                    v = (cnt[0] + cnt[3]) / max(n, 1)
                    return VGroup(label("fraction agreeing", 26, MUTED),
                                  DecimalNumber(v, num_decimal_places=2, font_size=34, color=color)).arrange(RIGHT, buff=0.15).move_to([cx, by - 0.75, 0])
                charts.add(axis, ticks, always_redraw(make))
                readouts.add(always_redraw(agree))
        self.play(FadeIn(charts), FadeIn(readouts))
        counter = always_redraw(lambda: VGroup(label("shots", 26, MUTED),
                                               DecimalNumber(k.get_value(), num_decimal_places=0, font_size=32, color=INK))
                                .arrange(RIGHT, buff=0.12).move_to([0, 2.1, 0]))
        self.add(counter)
        self.play(k.animate.set_value(N_SHOTS), run_time=9, rate_func=linear)
        ex = [("bell", "Z", "1", VIOLET), ("mix", "Z", "1", AMBER), ("bell", "X", "1", VIOLET), ("mix", "X", "1/2", AMBER)]
        exact = VGroup(*[eq(rf"P(\text{{agree}}) = {v}", size=36, color=col).move_to([cols[c], rows[r] - 0.75, 0])
                         for c, r, v, col in ex])
        self.play(FadeOut(readouts), FadeIn(exact))
        self.wait(1.8)
        self.play(FadeOut(VGroup(charts, exact, counter, heads)))
        w = VGroup(label("Any coin-flip mixture of product states obeys", 30, INK),
                   eq(F_WITNESS, size=44),
                   VGroup(eq(r"|\Phi^+\rangle:\ 1 + 1 = 2", size=40, color=VIOLET),
                          eq(r"\text{coin flip}:\ 0 + 1 = 1", size=40, color=AMBER)).arrange(RIGHT, buff=1.0),
                   label("so the Bell state is entangled; one basis alone could not show it", 28, RED))
        w.arrange(DOWN, buff=0.5).move_to(DOWN * 0.2)
        for m in w:
            self.play(FadeIn(m), run_time=0.9)
        self.wait(2.0)
        _ = (CYAN, ReplacementTransform)
