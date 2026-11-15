"""L5-05 Density operators and reduced states: four scenes.

MixturesInBall         (3-D) mixing |0> and |+> moves a point along a chord inside the Bloch ball; purity is
                       (1 + |r|^2)/2.  Then two more ensembles (the eigen-ensemble and a chord along y) pass through
                       the same point: the same density operator.
PurityFromBloch        the term-by-term derivation Tr rho^2 = (1 + |r|^2)/2 and the eigenvalues (1 +- |r|)/2, with a
                       live dot on the purity curve.
PartialTraceBlocks     |Phi+><Phi+| as a 4 x 4 matrix in 2 x 2 blocks; Tr_B replaces each block by its trace and gives
                       I/2; the coin-flip mixture differs only in the coherence that Tr_B discards.
ReducedStateSteering   (3-D) the reduced state of cos(t)|00> + sin(t)|11> sinks from the pole to the center; then for
                       |Phi+>, whatever Alice measures, Bob's two conditional states are antipodal and average to I/2.
Conventions: rho = (I + r . sigma)/2 with |0> at +z; A is the left tensor factor; (Tr_B rho)_{ik} = sum_j rho_{ij,kj}.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from manim import (DEGREES, DOWN, IN, LEFT, ORIGIN, OUT, PI, RIGHT, UP, Axes, Create, DashedLine, DecimalNumber,  # noqa: E402
                   Dot, Dot3D, FadeIn, FadeOut, Indicate, Line, ParametricFunction, Rectangle, ReplacementTransform,
                   Scene, Square, SurroundingRectangle, ThreeDScene, TracedPath, Transform, TransformMatchingTex,
                   ValueTracker, VGroup, Write, always_redraw, linear, smooth)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label  # noqa: E402
from qcai.science import X, Y, Z, I2, bloch, dm, partial_trace, purity  # noqa: E402

R = 1.9          # drawn radius of the Bloch ball
S2 = 1 / math.sqrt(2)

# --- numbers shown on screen ---------------------------------------------------------------------------------
k0, kp = np.array([1, 0], dtype=complex), np.array([S2, S2], dtype=complex)
RHO_HALF = 0.5 * dm(k0) + 0.5 * dm(kp)
R_HALF = bloch(RHO_HALF)                                   # (1/2, 0, 1/2)
assert np.allclose(R_HALF, [0.5, 0, 0.5]) and abs(purity(RHO_HALF) - 0.75) < 1e-12
RN = np.linalg.norm(R_HALF)                                # 0.7071
W_PLUS, W_MINUS = (1 + RN) / 2, (1 - RN) / 2               # eigen-ensemble weights 0.854, 0.146
ev = np.linalg.eigvalsh(RHO_HALF)
assert np.allclose(sorted(ev), [W_MINUS, W_PLUS])
NHAT = R_HALF / RN
EIG_PTS = (NHAT, -NHAT)
assert np.allclose(W_PLUS * NHAT + W_MINUS * (-NHAT), R_HALF)
Y_PTS = (np.array([0.5, S2, 0.5]), np.array([0.5, -S2, 0.5]))   # chord along y through the same point
assert all(abs(np.linalg.norm(p) - 1) < 1e-12 for p in Y_PTS) and np.allclose((Y_PTS[0] + Y_PTS[1]) / 2, R_HALF)
# Bell state blocks and reduced state
BELL = np.array([S2, 0, 0, S2], dtype=complex)
RHO_BELL = dm(BELL)
assert np.allclose(partial_trace(RHO_BELL, 0), I2 / 2) and np.allclose(partial_trace(RHO_BELL, 1), I2 / 2)
RHO_MIX = np.diag([0.5, 0, 0, 0.5]).astype(complex)
assert np.allclose(partial_trace(RHO_MIX, 0), I2 / 2)

F_PURITY = r"\operatorname{Tr}\rho^2 = \tfrac12(1 + |\vec r|^2)"
F_EIG = r"\lambda_\pm = \tfrac12(1 \pm |\vec r|)"
F_WEIGHTS = f"{W_PLUS:.3f}"
F_WEIGHTS2 = f"{W_MINUS:.3f}"
F_PT = r"(\operatorname{Tr}_B\rho)_{ik} = \sum_j \rho_{ij,kj}"
F_SINK = r"\operatorname{Tr}\rho_A^2 = \tfrac12(1 + \cos^2 2\theta)"


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [F_PURITY, F_EIG, F_WEIGHTS, F_WEIGHTS2, F_PT, F_SINK]


# --- 3-D helpers -------------------------------------------------------------------------------------------------
def P(v):
    """Bloch vector -> scene point."""
    return np.array(v, dtype=float) * R


def ball():
    """Wireframe Bloch ball: equator, two meridians, three axes."""
    t = [0, 2 * PI]
    eqc = ParametricFunction(lambda u: P([math.cos(u), math.sin(u), 0]), t_range=t, color=MUTED, stroke_width=2)
    m1 = ParametricFunction(lambda u: P([math.cos(u), 0, math.sin(u)]), t_range=t, color=MUTED, stroke_width=2)
    m2 = ParametricFunction(lambda u: P([0, math.cos(u), math.sin(u)]), t_range=t, color=GRID, stroke_width=2)
    lat = VGroup(*[ParametricFunction(lambda u, h=h: P([math.sqrt(1 - h * h) * math.cos(u),
                                                       math.sqrt(1 - h * h) * math.sin(u), h]),
                                      t_range=t, color=GRID, stroke_width=1.5) for h in (-0.6, 0.6)])
    axes = VGroup(DashedLine(P([-1, 0, 0]), P([1.12, 0, 0]), color=MUTED, stroke_width=1.5),
                  DashedLine(P([0, -1, 0]), P([0, 1.12, 0]), color=MUTED, stroke_width=1.5),
                  DashedLine(P([0, 0, -1]), P([0, 0, 1.12]), color=MUTED, stroke_width=1.5))
    return VGroup(lat, m2, eqc, m1, axes)


def pole_labels(scene):
    labs = [(eq(r"|0\rangle", size=34), [0, 0, 1.25]), (eq(r"|1\rangle", size=34), [0, 0, -1.25]),
            (eq(r"|+\rangle", size=34), [1.3, 0, 0]), (eq(r"|{+i}\rangle", size=30, color=MUTED), [0, 1.3, 0])]
    out = []
    for m, v in labs:
        m.move_to(P(v))
        out.append(m)
    scene.add_fixed_orientation_mobjects(*out)
    return VGroup(*out)


def fixed_redraw(scene, func):
    """A frame-fixed mobject rebuilt every frame (re-registers new submobjects as fixed)."""
    m = func()

    def upd(mob):
        mob.become(func())
        scene.renderer.camera.add_fixed_in_frame_mobjects(mob)
    m.add_updater(upd)
    scene.add_fixed_in_frame_mobjects(m)
    return m


def readout(name_tex, value, places=3, color=INK, size=34):
    g = VGroup(eq(name_tex, size=size, color=color), DecimalNumber(value, num_decimal_places=places, font_size=size,
                                                                   color=color))
    return g.arrange(RIGHT, buff=0.15)


class MixturesInBall(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=20 * DEGREES)
        title = label("Mixtures live inside the Bloch ball", 34, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(title), Create(ball()), run_time=1.6)
        pole_labels(self)

        left = VGroup(eq(r"\rho = p\,|0\rangle\langle 0| + (1-p)\,|+\rangle\langle +|", size=30),
                      eq(r"\vec r = p\,\vec r_0 + (1-p)\,\vec r_+", size=30)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        left.to_corner(LEFT + UP, buff=0.3).shift(DOWN * 0.8)
        self.add_fixed_in_frame_mobjects(left)
        self.play(FadeIn(left))
        a, b = P([0, 0, 1]), P([1, 0, 0])
        d0, dp = Dot3D(a, radius=0.09, color=BLUE), Dot3D(b, radius=0.09, color=BLUE)
        chord = Line(a, b, color=BLUE, stroke_width=3)
        self.play(FadeIn(d0), FadeIn(dp), Create(chord))

        p = ValueTracker(1.0)
        pt = always_redraw(lambda: Dot3D(P([1 - p.get_value(), 0, p.get_value()]), radius=0.11, color=VIOLET))
        self.add(pt)

        def right_panel():
            pv = p.get_value()
            r = math.hypot(1 - pv, pv)
            g = VGroup(readout("p =", pv, 2, BLUE), readout(r"|\vec r| =", r, 3, VIOLET),
                       readout(r"\operatorname{Tr}\rho^2 =", (1 + r * r) / 2, 3, RED))
            return g.arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_corner(RIGHT + UP, buff=0.6).shift(DOWN * 0.8)
        panel = fixed_redraw(self, right_panel)
        formula = eq(F_PURITY, size=34, color=RED).to_corner(RIGHT + DOWN, buff=0.6)
        self.add_fixed_in_frame_mobjects(formula)
        self.play(FadeIn(formula))
        self.play(p.animate.set_value(0.0), run_time=3, rate_func=smooth)
        self.play(p.animate.set_value(0.5), run_time=2, rate_func=smooth)
        self.wait(0.5)
        panel.clear_updaters()

        # the eigen-ensemble: a diameter through the same point
        e1, e2 = P(EIG_PTS[0]), P(EIG_PTS[1])
        diam = Line(e1, e2, color=CYAN, stroke_width=3)
        de = VGroup(Dot3D(e1, radius=0.09, color=CYAN), Dot3D(e2, radius=0.09, color=CYAN))
        t2 = VGroup(label("same point, another ensemble:", 26, CYAN),
                    eq(r"\text{eigenstates } \pm\hat r", size=32, color=CYAN),
                    eq(rf"\text{{weights }} {W_PLUS:.3f},\ {W_MINUS:.3f}", size=32, color=CYAN)).arrange(
            DOWN, aligned_edge=LEFT, buff=0.12)
        t2.next_to(left, DOWN, buff=0.45, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(t2)
        self.play(Create(diam), FadeIn(de), FadeIn(t2), run_time=1.6)
        # a third ensemble along y
        y1, y2 = P(Y_PTS[0]), P(Y_PTS[1])
        ych = Line(y1, y2, color=AMBER, stroke_width=3)
        dy = VGroup(Dot3D(y1, radius=0.09, color=AMBER), Dot3D(y2, radius=0.09, color=AMBER))
        t3 = VGroup(eq(r"\text{or } (\tfrac12, \pm\tfrac{1}{\sqrt2}, \tfrac12)", size=32, color=AMBER),
                    eq(r"\text{weights } \tfrac12, \tfrac12", size=32, color=AMBER)).arrange(
            DOWN, aligned_edge=LEFT, buff=0.12).next_to(t2, DOWN, buff=0.3, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(t3)
        self.play(Create(ych), FadeIn(dy), FadeIn(t3), run_time=1.6)
        self.begin_ambient_camera_rotation(rate=0.35)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        end = label("same point, same density operator: no measurement tells these apart", 26, INK)
        end.to_edge(DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(end)
        self.play(FadeOut(formula), FadeIn(end))
        self.wait(2)


class PurityFromBloch(Scene):
    def construct(self):
        title = label("Purity is distance from the center", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        x0 = LEFT * 2.6
        l1 = eq(r"\rho^2", "=", r"\tfrac14", r"(I + \vec r\cdot\vec\sigma)^2", size=40).move_to(x0 + UP * 1.9)
        l2 = eq(r"\rho^2", "=", r"\tfrac14", r"\big(I + 2\,\vec r\cdot\vec\sigma + (\vec r\cdot\vec\sigma)^2\big)", size=40)
        l3 = eq(r"\rho^2", "=", r"\tfrac14", r"\big((1 + |\vec r|^2)\,I + 2\,\vec r\cdot\vec\sigma\big)", size=40)
        for m in (l2, l3):
            m.move_to(l1)
        self.play(Write(l1))
        self.play(TransformMatchingTex(l1, l2), run_time=1.4)
        side = eq(r"(\vec r\cdot\vec\sigma)^2 = |\vec r|^2 I", size=34, color=BLUE).move_to(x0 + UP * 0.85)
        why = label("because XY = -YX, and so on, and X² = Y² = Z² = I", 24, MUTED).next_to(side, DOWN, buff=0.15)
        self.play(FadeIn(side), FadeIn(why))
        self.play(TransformMatchingTex(l2, l3), run_time=1.4)
        tr = eq(F_PURITY, size=42, color=RED).move_to(x0 + DOWN * 0.75)
        trwhy = label("Tr I = 2, and every Pauli matrix has trace 0", 24, MUTED).next_to(tr, DOWN, buff=0.15)
        self.play(Write(tr), FadeIn(trwhy))
        eig = eq(F_EIG, size=40, color=VIOLET).move_to(x0 + DOWN * 2.3)
        eigwhy = label("both eigenvalues are at least 0 exactly when |r| ≤ 1", 24, MUTED).next_to(eig, DOWN, buff=0.15)
        self.play(Write(eig), FadeIn(eigwhy))

        ax = Axes(x_range=[0, 1, 0.5], y_range=[0.4, 1, 0.1], x_length=4.2, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 4.0 + DOWN * 0.3)
        xl = eq(r"|\vec r|", size=32).next_to(ax.x_axis, DOWN, buff=0.35)
        yl = eq(r"\operatorname{Tr}\rho^2", size=30).next_to(ax, UP, buff=0.15)
        ticks = VGroup(label("0", 22, MUTED).next_to(ax.c2p(0, 0.4), DOWN, buff=0.12),
                       label("1", 22, MUTED).next_to(ax.c2p(1, 0.4), DOWN, buff=0.12),
                       label("1/2", 22, MUTED).next_to(ax.c2p(0, 0.5), LEFT, buff=0.12),
                       label("1", 22, MUTED).next_to(ax.c2p(0, 1), LEFT, buff=0.12))
        curve = ax.plot(lambda r: (1 + r * r) / 2, x_range=[0, 1], color=RED, stroke_width=4)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(ticks), Create(curve))
        r = ValueTracker(0.0)
        dot = always_redraw(lambda: Dot(ax.c2p(r.get_value(), (1 + r.get_value() ** 2) / 2), color=VIOLET, radius=0.08))
        lab = always_redraw(lambda: VGroup(label("center: I/2, purity 1/2", 24, MUTED) if r.get_value() < 0.05 else
                                           label("surface: pure, purity 1", 24, MUTED) if r.get_value() > 0.95 else
                                           label("inside: mixed", 24, MUTED)).next_to(ax, DOWN, buff=0.85))
        self.add(dot, lab)
        self.wait(0.8)
        self.play(r.animate.set_value(1.0), run_time=4, rate_func=linear)
        self.wait(1.5)
        _ = (ReplacementTransform, Rectangle)


class PartialTraceBlocks(Scene):
    def construct(self):
        title = label("The partial trace keeps A's blocks and traces each one", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        cell = 0.92
        c0 = np.array([-3.5, -0.2, 0])

        def pos(i, j):
            return c0 + np.array([(j - 1.5) * cell, (1.5 - i) * cell, 0])

        def entry(v):
            return {0.5: "1/2", 0.0: "0"}[round(float(np.real(v)), 3)]

        def grid(rho, color_corner=INK):
            g = VGroup()
            for i in range(4):
                for j in range(4):
                    col = color_corner if (i, j) in ((0, 3), (3, 0)) else INK
                    g.add(eq(entry(rho[i, j]), size=36, color=col).move_to(pos(i, j)))
            return g
        names = ["00", "01", "10", "11"]
        rl = VGroup(*[label(n, 24, MUTED).move_to(pos(i, 0) + LEFT * 0.8) for i, n in enumerate(names)])
        cl = VGroup(*[label(n, 24, MUTED).move_to(pos(0, j) + UP * 0.6) for j, n in enumerate(names)])
        head = eq(r"|\Phi^+\rangle\langle\Phi^+|", size=36, color=VIOLET).move_to(c0 + UP * 2.6)
        G = grid(RHO_BELL, VIOLET)
        cols = {(0, 0): VIOLET, (0, 1): AMBER, (1, 0): AMBER, (1, 1): CYAN}
        blocks = VGroup(*[Square(side_length=2 * cell - 0.08, color=c, stroke_width=3)
                          .move_to((pos(2 * a, 2 * b) + pos(2 * a + 1, 2 * b + 1)) / 2) for (a, b), c in cols.items()])
        self.play(FadeIn(head), FadeIn(rl), FadeIn(cl), FadeIn(G))
        self.play(Create(blocks), run_time=1.2)
        bl = VGroup(*[eq(f"B_{{{a}{b}}}", size=28, color=c).next_to(blocks[k], DOWN if a else UP, buff=0.05)
                      .shift(RIGHT * (0.55 if b else -0.55)) for k, ((a, b), c) in enumerate(cols.items())])
        note = label("rows and columns of blocks: qubit A", 24, MUTED).move_to(c0 + DOWN * 2.75)
        self.play(FadeIn(note))

        d = eq(F_PT, size=36).move_to(RIGHT * 3.3 + UP * 2.1)
        self.play(Write(d))
        m1 = eq(r"\operatorname{Tr}_B\rho = ", r"\begin{pmatrix}\operatorname{Tr}B_{00} & \operatorname{Tr}B_{01}\\ "
                r"\operatorname{Tr}B_{10} & \operatorname{Tr}B_{11}\end{pmatrix}", size=34).move_to(RIGHT * 3.3 + UP * 0.6)
        self.play(Write(m1))
        m2 = eq(r"\operatorname{Tr}_B\rho = ", r"\begin{pmatrix}\tfrac12 + 0 & 0 + 0\\ 0 + 0 & 0 + \tfrac12\end{pmatrix}",
                size=34).move_to(m1)
        hl = VGroup(*[SurroundingRectangle(G[4 * (2 * a + j) + 2 * b + j], color=c, buff=0.07)
                      for (a, b), c in cols.items() for j in (0, 1)])
        self.play(Create(hl), run_time=1.0)
        self.play(TransformMatchingTex(m1, m2), run_time=1.4)
        m3 = eq(r"\operatorname{Tr}_B\rho = ", r"\begin{pmatrix}\tfrac12 & 0\\ 0 & \tfrac12\end{pmatrix} = I/2", size=34,
                color=RED).move_to(m1)
        self.play(TransformMatchingTex(m2, m3), FadeOut(hl), run_time=1.2)
        self.wait(0.6)

        # the coherence lives off the diagonal of the off-diagonal blocks
        corner = VGroup(G[3], G[12])
        circ = VGroup(*[SurroundingRectangle(m, color=RED, buff=0.08) for m in corner])
        c_txt = VGroup(label("coherence: inside B01 and B10,", 26, RED), label("off their diagonals, so Tr_B drops it", 26, RED))
        c_txt.arrange(DOWN, buff=0.08).move_to(RIGHT * 3.3 + DOWN * 0.8)
        self.play(Create(circ), FadeIn(c_txt))
        self.wait(0.6)
        G2 = grid(RHO_MIX, AMBER)
        head2 = eq(r"\text{coin flip: } |00\rangle \text{ or } |11\rangle", size=34, color=AMBER).move_to(head)
        self.play(Transform(G, G2), Transform(head, head2), FadeOut(circ), run_time=1.6)
        same = VGroup(label("same reduced state I/2,", 26, INK), label("different joint states", 26, INK))
        same.arrange(DOWN, buff=0.1).move_to(RIGHT * 3.3 + DOWN * 2.3)
        self.play(FadeIn(same))
        self.play(Indicate(m3, color=RED))
        self.wait(1.8)
        _ = bl


class ReducedStateSteering(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=20 * DEGREES)
        title = label("Half of an entangled pair is mixed", 34, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(title), Create(ball()), run_time=1.5)
        pole_labels(self)
        st = VGroup(eq(r"|\psi\rangle = \cos\theta\,|00\rangle + \sin\theta\,|11\rangle", size=30),
                    eq(r"\rho_A = \operatorname{diag}(\cos^2\theta,\ \sin^2\theta)", size=30),
                    eq(r"\vec r_A = (0,\ 0,\ \cos 2\theta)", size=30)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        st.to_corner(LEFT + UP, buff=0.3).shift(DOWN * 0.8)
        self.add_fixed_in_frame_mobjects(st)
        self.play(FadeIn(st))
        th = ValueTracker(0.0)
        pt = always_redraw(lambda: Dot3D(P([0, 0, math.cos(2 * th.get_value())]), radius=0.12, color=VIOLET))
        self.add(pt)
        f = eq(F_SINK, size=32, color=RED).to_corner(RIGHT + UP, buff=0.6).shift(DOWN * 0.8)
        self.add_fixed_in_frame_mobjects(f)
        self.play(FadeIn(f))

        def panel():
            t = th.get_value()
            return VGroup(readout(r"\theta =", t, 3, BLUE),
                          readout(r"\operatorname{Tr}\rho_A^2 =", (1 + math.cos(2 * t) ** 2) / 2, 3, RED))\
                .arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(f, DOWN, buff=0.3).align_to(f, LEFT)
        pan = fixed_redraw(self, panel)
        self.play(th.animate.set_value(PI / 4), run_time=5, rate_func=linear)
        pan.clear_updaters()
        bell = label("at θ = π/4, the Bell state: A alone is I/2, purity 1/2", 26, VIOLET).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(bell)
        self.play(FadeIn(bell))
        self.wait(1.0)
        self.play(FadeOut(VGroup(st, f, pan, bell)))

        # steering: whatever Alice measures, Bob's conditional states average to the center
        st2 = VGroup(label("Alice measures her half along n", 26, INK),
                     eq(r"\text{outcome } \pm:\ \text{Bob's half becomes } \pm\vec n", size=30),
                     eq(r"P(+) = P(-) = \tfrac12", size=30),
                     eq(r"\tfrac12\,\vec n + \tfrac12\,(-\vec n) = \vec 0", size=30, color=RED)).arrange(
            DOWN, aligned_edge=LEFT, buff=0.22)
        st2.to_corner(LEFT + UP, buff=0.3).shift(DOWN * 0.8)
        self.add_fixed_in_frame_mobjects(st2)
        self.play(FadeIn(st2))
        a = ValueTracker(0.0)

        def nvec():
            t = a.get_value()
            return np.array([math.sin(t), 0, math.cos(t)])
        plus = always_redraw(lambda: Dot3D(P(nvec()), radius=0.1, color=CYAN))
        minus = always_redraw(lambda: Dot3D(P(-nvec()), radius=0.1, color=AMBER))
        link = always_redraw(lambda: DashedLine(P(nvec()), P(-nvec()), color=MUTED, stroke_width=2))
        self.play(FadeIn(plus), FadeIn(minus), Create(link))
        self.begin_ambient_camera_rotation(rate=0.25)
        self.play(a.animate.set_value(1.5 * PI), run_time=7, rate_func=linear)
        self.stop_ambient_camera_rotation()
        end = label("Bob's average stays at the center: Alice's choice sends no signal", 26, RED).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(end)
        self.play(FadeIn(end))
        self.wait(2)
        _ = (IN, OUT, ORIGIN, TracedPath, Transform, Rectangle, X, Y, Z)
