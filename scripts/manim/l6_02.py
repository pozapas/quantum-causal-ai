"""L6-02 Channels in the Choi representation: three scenes.

ChoiBuild       |Omega> = |00> + |11>, the channel on the second half, the derivation of
                J = sum_ij |i><j| (x) E(|i><j|), and the 4x4 Choi matrix of amplitude damping
                (gamma = 0.36) with its block traces (TP) and eigenvalues 1.64, 0.36, 0, 0 (CP).
TransposeTrap   Bloch ball: recovering E(rho) without the transpose sends |+i> to |-i>; the transpose
                map is the mirror y -> -y of the ball, positive but not CP, with J_T = SWAP.
ChoiSpectrum    eigenvalues of J for rho -> (1-p) rho + p I/2 as p sweeps 0 -> 1.6 (CP iff p <= 4/3),
                then for the mixture (1-t) id + t T, whose eigenvalue -t is negative for every t > 0.
Convention (course-wide): J = sum_ij |i><j| (x) E(|i><j|) on H_in (x) H_out; E(rho) = Tr_in[(rho^T (x) I) J].
Every number on screen is computed below and checked by assertions.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DecimalNumber, DOWN, LEFT, ORIGIN, OUT, PI, RIGHT, UP, Arrow, Arrow3D, Axes, Create, DashedLine, Dot3D, FadeIn,
                   FadeOut, Line, ParametricFunction, Rectangle, RoundedRectangle, Scene, Sphere, Square, SurroundingRectangle,
                   ThreeDAxes, ThreeDScene, TracedPath, Transform, TransformMatchingTex, ValueTracker, VGroup, Write,
                   always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ---------------------------------------------------------------- numbers (shared with the lesson text)
GAMMA = 0.36
SQ = math.sqrt(1 - GAMMA)          # 0.8


def choi_of(E, d=2):
    J = np.zeros((d * d, d * d), complex)
    for i in range(d):
        for j in range(d):
            Eij = np.zeros((d, d), complex)
            Eij[i, j] = 1
            J += np.kron(Eij, E(Eij))
    return J


def amp_damp(X):
    K0 = np.array([[1, 0], [0, SQ]])
    K1 = np.array([[0, math.sqrt(GAMMA)], [0, 0]])
    return K0 @ X @ K0.conj().T + K1 @ X @ K1.conj().T


J_AD = choi_of(amp_damp)
EV_AD = np.sort(np.linalg.eigvalsh(J_AD))[::-1]
assert abs(SQ - 0.8) < 1e-12
assert np.allclose(J_AD.real, [[1, 0, 0, 0.8], [0, 0, 0, 0], [0, 0, 0.36, 0], [0.8, 0, 0, 0.64]])
assert np.allclose(EV_AD, [1.64, 0.36, 0, 0])
TR_OUT = J_AD.reshape(2, 2, 2, 2).trace(axis1=1, axis2=3)
assert np.allclose(TR_OUT, np.eye(2))


def depol_eigs(p):
    return [2 - 1.5 * p, p / 2, p / 2, p / 2]


for _p in (0.0, 0.5, 4 / 3, 1.6):
    _J = choi_of(lambda X, p=_p: (1 - p) * X + p * np.trace(X) * np.eye(2) / 2)
    assert np.allclose(np.sort(np.linalg.eigvalsh(_J)), np.sort(depol_eigs(_p)))
J_T = choi_of(lambda X: X.T)
assert np.allclose(J_T, [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
assert np.allclose(np.sort(np.linalg.eigvalsh(J_T)), [-1, 1, 1, 1])
for _t in (0.0, 0.25, 1.0):
    _J = choi_of(lambda X, t=_t: (1 - t) * X + t * X.T)
    assert np.allclose(np.sort(np.linalg.eigvalsh(_J)), np.sort([2 - _t, _t, _t, -_t]))
# transpose trap: identity channel, |+i>
_pi = np.array([1, 1j]) / math.sqrt(2)
_r = np.outer(_pi, _pi.conj())
_wrong = np.einsum("aiaj->ij", (np.kron(_r, np.eye(2)) @ choi_of(lambda X: X)).reshape(2, 2, 2, 2))
assert np.allclose(_wrong, _r.T)


def facts(L):
    """Strings the animations put on screen; each also appears in the lesson text."""
    return ["|00\\rangle + |11\\rangle", "1.64", "0.36", "2 - 3p/2", "4/3", "2 - t", "\\operatorname{Tr}_{\\mathrm{out}} J = I",
            "SWAP"]


def fmt(x):
    x = float(np.real(x))
    if abs(x) < 1e-12:
        return "0"
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return s


def bracket_matrix(entries, cell_w=1.0, cell_h=0.62, size=32, color=INK):
    """A matrix drawn as a grid of eq() entries with square brackets."""
    rows, cols = len(entries), len(entries[0])
    grid = VGroup()
    for r in range(rows):
        for c in range(cols):
            m = eq(entries[r][c], size=size, color=color)
            m.move_to(RIGHT * (c - (cols - 1) / 2) * cell_w + DOWN * (r - (rows - 1) / 2) * cell_h)
            grid.add(m)
    h = rows * cell_h + 0.1
    w = cols * cell_w + 0.1
    lb = VGroup(Line(UP * h / 2, DOWN * h / 2), Line(UP * h / 2, UP * h / 2 + RIGHT * 0.15),
                Line(DOWN * h / 2, DOWN * h / 2 + RIGHT * 0.15)).set_color(INK).shift(LEFT * w / 2)
    rb = VGroup(Line(UP * h / 2, DOWN * h / 2), Line(UP * h / 2, UP * h / 2 + LEFT * 0.15),
                Line(DOWN * h / 2, DOWN * h / 2 + LEFT * 0.15)).set_color(INK).shift(RIGHT * w / 2)
    return VGroup(grid, lb, rb)


class ChoiBuild(Scene):
    def construct(self):
        title = label("Turn a channel into one operator", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))

        # the construction as a picture: two wires, the channel on the second
        omega = eq(r"|\Omega\rangle = |00\rangle + |11\rangle", size=38, color=VIOLET).move_to(LEFT * 4.3 + UP * 1.9)
        w1 = Line(LEFT * 6.0 + UP * 0.9, LEFT * 1.6 + UP * 0.9, color=INK)
        w2a = Line(LEFT * 6.0 + DOWN * 0.1, LEFT * 4.3 + DOWN * 0.1, color=INK)
        box = RoundedRectangle(width=1.1, height=0.8, corner_radius=0.12, color=BLUE).move_to(LEFT * 3.75 + DOWN * 0.1)
        bl = eq(r"\mathcal{E}", size=38, color=BLUE).move_to(box)
        w2b = Line(LEFT * 3.2 + DOWN * 0.1, LEFT * 1.6 + DOWN * 0.1, color=INK)
        tin = label("in copy", 24, MUTED).next_to(w1, UP, buff=0.08).align_to(w1, LEFT)
        tout = label("through the channel", 24, MUTED).next_to(w2a, DOWN, buff=0.5).align_to(w2a, LEFT)
        self.play(Write(omega))
        self.play(Create(w1), Create(w2a), Create(box), Write(bl), Create(w2b), FadeIn(tin), FadeIn(tout), run_time=1.6)

        d1 = eq(r"J_{\mathcal{E}} = (\mathrm{id} \otimes \mathcal{E})", r"(|\Omega\rangle\langle\Omega|)", size=36).move_to(RIGHT * 2.6 + UP * 1.9)
        d2 = eq(r"J_{\mathcal{E}} = (\mathrm{id} \otimes \mathcal{E})", r"\Big(\sum_{i,j} |i\rangle\langle j| \otimes |i\rangle\langle j|\Big)",
                size=36).move_to(RIGHT * 2.6 + UP * 1.9)
        d3 = eq(r"J_{\mathcal{E}} =", r"\sum_{i,j} |i\rangle\langle j| \otimes \mathcal{E}(|i\rangle\langle j|)", size=40,
                color=INK).move_to(RIGHT * 2.6 + UP * 1.9)
        self.play(Write(d1))
        self.wait(0.4)
        self.play(TransformMatchingTex(d1, d2), run_time=1.4)
        self.wait(0.4)
        self.play(TransformMatchingTex(d2, d3), run_time=1.4)
        conv = label("input factor first, output second", 24, MUTED).next_to(d3, DOWN, buff=0.2)
        self.play(FadeIn(conv))
        self.wait(0.8)

        # block picture
        self.play(FadeOut(VGroup(w1, w2a, box, bl, w2b, tin, tout)), omega.animate.scale(0.85).move_to(LEFT * 4.6 + UP * 2.6),
                  VGroup(d3, conv).animate.scale(0.8).move_to(RIGHT * 3.0 + UP * 2.45))
        blocks = bracket_matrix([[r"\mathcal{E}(|0\rangle\langle 0|)", r"\mathcal{E}(|0\rangle\langle 1|)"],
                                 [r"\mathcal{E}(|1\rangle\langle 0|)", r"\mathcal{E}(|1\rangle\langle 1|)"]], cell_w=2.6, cell_h=1.0, size=34)
        blocks.move_to(LEFT * 3.2 + DOWN * 0.4)
        bcap = label("2 x 2 blocks, one per |i><j|", 24, MUTED).next_to(blocks, DOWN, buff=0.3)
        self.play(FadeIn(blocks), FadeIn(bcap))
        self.wait(0.6)

        # numbers for amplitude damping
        ad = eq(r"\text{amplitude damping, } \gamma = 0.36", size=32, color=BLUE).move_to(RIGHT * 3.3 + UP * 1.35)
        ent = [[fmt(J_AD[r, c]) for c in range(4)] for r in range(4)]
        M = bracket_matrix(ent, cell_w=0.85, cell_h=0.6, size=34).move_to(RIGHT * 3.3 + DOWN * 0.45)
        self.play(Write(ad))
        self.play(FadeIn(M), run_time=1.2)
        # block outlines
        g = M[0]
        tl = SurroundingRectangle(VGroup(g[0], g[5]), color=CYAN, buff=0.08)
        br = SurroundingRectangle(VGroup(g[10], g[15]), color=CYAN, buff=0.08)
        tr = SurroundingRectangle(VGroup(g[2], g[7]), color=AMBER, buff=0.08)
        bl_ = SurroundingRectangle(VGroup(g[8], g[13]), color=AMBER, buff=0.08)
        self.play(Create(tl), Create(br), Create(tr), Create(bl_))
        tp = eq(r"\operatorname{Tr}_{\mathrm{out}} J = I", size=36, color=CYAN).move_to(RIGHT * 3.3 + DOWN * 2.15)
        tpn = VGroup(label("diagonal blocks: trace 1 and 0.36 + 0.64 = 1", 24, MUTED),
                     label("off-diagonal blocks: trace 0", 24, MUTED)).arrange(DOWN, buff=0.1).next_to(tp, DOWN, buff=0.15)
        self.play(FadeOut(bcap), Write(tp), FadeIn(tpn))
        self.wait(1.2)
        self.play(FadeOut(VGroup(tl, br, tr, bl_, tpn)))
        cp = eq(r"\text{eigenvalues of } J:\ 1.64,\ 0.36,\ 0,\ 0", size=34, color=VIOLET).move_to(LEFT * 3.2 + DOWN * 2.15)
        cpn = label("all >= 0, so the map is completely positive", 24, MUTED).next_to(cp, DOWN, buff=0.12)
        self.play(Write(cp), FadeIn(cpn))
        self.wait(2.0)


class TransposeTrap(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=68 * math.pi / 180, theta=30 * math.pi / 180, zoom=0.88)
        R = 2.0
        sphere = Sphere(radius=R, resolution=(18, 18)).set_fill(BLUE, opacity=0.06).set_stroke(GRID, width=0.6)
        axes = ThreeDAxes(x_range=[-2.6, 2.6, 1], y_range=[-2.6, 2.6, 1], z_range=[-2.6, 2.6, 1], x_length=5.2, y_length=5.2,
                          z_length=5.2, axis_config={"color": MUTED, "include_ticks": False, "include_tip": False})
        xl = eq("x", size=34, color=MUTED).move_to(np.array([2.9, 0, 0]))
        yl = eq("y", size=34, color=MUTED).move_to(np.array([0, 2.9, 0]))
        zl = eq("z", size=34, color=MUTED).move_to(np.array([0, 0, 2.9]))
        self.add_fixed_orientation_mobjects(xl, yl, zl)
        title = label("The transpose in the recovery formula is not optional", 30, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Create(axes), FadeIn(sphere), Write(title), FadeIn(xl), FadeIn(yl), FadeIn(zl), run_time=1.6)

        st = eq(r"\rho = |{+i}\rangle\langle{+i}|,\ \ \mathcal{E} = \mathrm{id}", size=32, color=VIOLET).to_corner(LEFT + UP, buff=0.4).shift(DOWN * 0.7)
        self.add_fixed_in_frame_mobjects(st)
        a = Arrow3D(ORIGIN, np.array([0, R, 0]), color=VIOLET)
        self.play(Write(st), Create(a))
        good = eq(r"\operatorname{Tr}_{\mathrm{in}}[(\rho^{T} \otimes I)J] = \rho", size=32, color=CYAN).next_to(st, DOWN, buff=0.3).align_to(st, LEFT)
        self.add_fixed_in_frame_mobjects(good)
        self.play(Write(good))
        bad = eq(r"\operatorname{Tr}_{\mathrm{in}}[(\rho \otimes I)J] = \rho^{T}", size=32, color=RED).next_to(good, DOWN, buff=0.3).align_to(st, LEFT)
        self.add_fixed_in_frame_mobjects(bad)
        b = Arrow3D(ORIGIN, np.array([0, -R, 0]), color=RED)
        self.play(Write(bad), Create(b), run_time=1.4)
        note = label("|+i> comes back as |-i>: y flips", 24, RED).next_to(bad, DOWN, buff=0.25).align_to(st, LEFT)
        self.add_fixed_in_frame_mobjects(note)
        self.play(FadeIn(note))
        self.wait(0.8)

        # the transpose map is the mirror y -> -y; show the mirror plane and a moving state with its image
        plane = Square(side_length=2 * R).set_fill(AMBER, opacity=0.10).set_stroke(AMBER, width=1)
        plane.rotate(PI / 2, axis=RIGHT)  # the x-z plane
        self.play(FadeIn(plane), FadeOut(a), FadeOut(b))
        t = ValueTracker(0.0)

        n = np.array([0.62, 0.45, 0.64])
        n = n / np.linalg.norm(n)
        u = np.cross(n, [0, 0, 1.0])
        u = u / np.linalg.norm(u)
        v = np.cross(n, u)

        def vec(tt):
            a = 0.55  # angular radius of the small circle around n
            return R * (math.cos(a) * n + math.sin(a) * (math.cos(tt) * u + math.sin(tt) * v))

        p1 = always_redraw(lambda: Dot3D(vec(t.get_value()), radius=0.07, color=VIOLET))
        p2 = always_redraw(lambda: Dot3D(vec(t.get_value()) * np.array([1, -1, 1]), radius=0.07, color=RED))
        tr1 = TracedPath(lambda: vec(t.get_value()), stroke_color=VIOLET, stroke_width=3)
        tr2 = TracedPath(lambda: vec(t.get_value()) * np.array([1, -1, 1]), stroke_color=RED, stroke_width=3)
        self.add(tr1, tr2, p1, p2)
        self.play(t.animate.set_value(2 * PI), run_time=6, rate_func=linear)
        self.play(FadeOut(VGroup(st, good, bad, note)))
        m1 = eq(r"\rho \mapsto \rho^{T}:\ (x, y, z) \mapsto (x, -y, z)", size=32).to_corner(LEFT + UP, buff=0.4).shift(DOWN * 0.7)
        m2 = label("positive: every state goes to a state", 24, MUTED).next_to(m1, DOWN, buff=0.2).align_to(m1, LEFT)
        m3 = VGroup(eq(r"J_{T} = \mathrm{SWAP}", size=32, color=RED), eq(r"\text{eigenvalues } 1, 1, 1, -1", size=32, color=RED))
        m3.arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(m2, DOWN, buff=0.3).align_to(m1, LEFT)
        m4 = label("not completely positive", 26, RED, "BOLD").next_to(m3, DOWN, buff=0.2).align_to(m1, LEFT)
        for m in (m1, m2, m3, m4):
            self.add_fixed_in_frame_mobjects(m)
        self.play(Write(m1))
        self.play(FadeIn(m2))
        self.play(Write(m3))
        self.play(FadeIn(m4))
        self.wait(2.0)
        _ = (OUT, DashedLine, ParametricFunction, Transform)


class ChoiSpectrum(Scene):
    def construct(self):
        title = label("Complete positivity is a sign test on the spectrum of J", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        fam = eq(r"\mathcal{E}_p(\rho) = (1-p)\,\rho + p\,\operatorname{Tr}(\rho)\,\tfrac{I}{2}", size=36).move_to(LEFT * 3.2 + UP * 2.3)
        self.play(Write(fam))

        ax = Axes(x_range=[0, 4.7, 1], y_range=[-1.2, 2.2, 1], x_length=5.6, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False}, x_axis_config={"include_ticks": False},
                  y_axis_config={"numbers_to_include": [-1, 0, 1, 2], "font_size": 26, "decimal_number_config": {"color": INK, "num_decimal_places": 0}})
        ax.move_to(LEFT * 3.0 + DOWN * 0.75)
        ylab = label("eigenvalues of J", 24, MUTED).next_to(ax, UP, buff=0.05).align_to(ax, LEFT).shift(RIGHT * 0.3)
        blabs = VGroup(*[eq(rf"\lambda_{k + 1}", size=30, color=MUTED).move_to(ax.c2p(1.0 + k, -1.45)) for k in range(4)])
        self.play(Create(ax), FadeIn(ylab), FadeIn(blabs))
        p = ValueTracker(0.0)
        cols = [VIOLET, CYAN, CYAN, CYAN]

        def bars(eigs):
            g = VGroup()
            for k, v in enumerate(eigs):
                x0 = ax.c2p(0.55 + k, 0)
                x1 = ax.c2p(0.55 + k + 0.9, v)
                w = abs(x1[0] - x0[0])
                h = max(abs(x1[1] - x0[1]), 0.001)
                col = RED if v < -1e-9 else cols[k]
                r = Rectangle(width=w, height=h).set_fill(col, opacity=0.75).set_stroke(col, width=1)
                r.move_to([(x0[0] + x1[0]) / 2, (x0[1] + x1[1]) / 2, 0])
                g.add(r)
            return g

        bg = always_redraw(lambda: bars(depol_eigs(p.get_value())))
        self.add(bg)
        f1 = eq(r"\lambda_1 = 2 - 3p/2", size=34, color=VIOLET).move_to(RIGHT * 3.5 + UP * 1.2)
        f2 = eq(r"\lambda_{2,3,4} = p/2", size=34, color=CYAN).next_to(f1, DOWN, buff=0.3)
        self.play(Write(f1), Write(f2))
        readout = VGroup(eq("p =", size=36), DecimalNumber(0, num_decimal_places=2, font_size=36, color=INK)).arrange(RIGHT, buff=0.15)
        readout.move_to(RIGHT * 3.5 + DOWN * 0.4)
        readout[1].add_updater(lambda m: m.set_value(p.get_value()))
        self.add(readout)
        self.play(p.animate.set_value(1.0), run_time=3.5, rate_func=linear)
        n1 = label("p = 1: fully depolarizing, still CP", 24, MUTED).move_to(RIGHT * 3.5 + DOWN * 1.2)
        self.play(FadeIn(n1))
        self.play(p.animate.set_value(4 / 3), run_time=1.6, rate_func=linear)
        n2 = eq(r"p = 4/3:\ \lambda_1 = 0", size=32, color=AMBER).move_to(RIGHT * 3.5 + DOWN * 1.9)
        self.play(Write(n2))
        self.play(p.animate.set_value(1.6), run_time=1.6, rate_func=linear)
        n3 = label("p > 4/3: a negative eigenvalue, not CP", 24, RED).move_to(RIGHT * 3.5 + DOWN * 2.6)
        self.play(FadeIn(n3))
        self.wait(1.2)

        # identity-transpose mixture
        self.remove(bg, readout)
        self.play(FadeOut(VGroup(fam, f1, f2, n1, n2, n3)))
        t = ValueTracker(0.0)
        fam2 = eq(r"\mathcal{M}_t(\rho) = (1-t)\,\rho + t\,\rho^{T}", size=36).move_to(LEFT * 3.2 + UP * 2.3)
        self.play(Write(fam2))
        bg2 = always_redraw(lambda: bars([2 - t.get_value(), t.get_value(), t.get_value(), -t.get_value()]))
        self.add(bg2)
        g1 = eq(r"2 - t,\ \ t,\ \ t,\ \ -t", size=36, color=VIOLET).move_to(RIGHT * 3.5 + UP * 1.2)
        self.play(Write(g1))
        ro2 = VGroup(eq("t =", size=36), DecimalNumber(0, num_decimal_places=2, font_size=36, color=INK)).arrange(RIGHT, buff=0.15)
        ro2.move_to(RIGHT * 3.5 + DOWN * 0.1)
        ro2[1].add_updater(lambda m: m.set_value(t.get_value()))
        self.add(ro2)
        self.play(t.animate.set_value(1.0), run_time=4, rate_func=linear)
        k1 = label("any amount of transpose breaks CP", 24, RED).move_to(RIGHT * 3.5 + DOWN * 1.0)
        k2 = label("t = 1 is the transpose: J = SWAP", 24, MUTED).move_to(RIGHT * 3.5 + DOWN * 1.6)
        self.play(FadeIn(k1), FadeIn(k2))
        self.wait(2.0)
        _ = (Arrow, Line)
