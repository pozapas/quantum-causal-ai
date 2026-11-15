"""L5-06 Quantum channels and complete positivity: three scenes.

NoiseDeformsBall  (3-D) the Bloch ball under three channels, driven through the exact affine Bloch maps:
                  depolarizing (uniform shrink), dephasing (squash onto the z axis), amplitude damping (shrink
                  toward |0>).  Images of |0>, |1>, |+> are tracked.
KrausDilation     amplitude damping with gamma = 0.36 as a unitary on system + environment followed by a partial
                  trace; Kraus operators K_k = <k|_E U |0>_E; the completeness sum K0^dag K0 + K1^dag K1 = I term by
                  term; the action on |1><1| and |+><+|.
TransposeNotCP    the transpose is a mirror of the Bloch ball (positive), but (id (x) T) sends |Phi+><Phi+| to SWAP/2,
                  whose eigenvalues include -1/2: positive, not completely positive.
Conventions: rho = (I + r . sigma)/2, |0> at +z; E(rho) = sum_k K_k rho K_k^dag with sum_k K_k^dag K_k = I;
extensions are (id_R (x) E) with the reference R as the left factor; T is the transpose in the computational basis.
Channel parameters follow qcai.science (dephasing with parameter p flips the phase with probability p/2).
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from manim import (DEGREES, DOWN, LEFT, PI, RIGHT, UP, Arrow, Circle, Create, DashedLine, DecimalNumber, Dot3D,  # noqa: E402
                   FadeIn, FadeOut, Indicate, Line, ParametricFunction, Rectangle, Scene, SurroundingRectangle,
                   ThreeDScene, Transform, TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, smooth)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label  # noqa: E402
from qcai.science import (KET0, KET1, X, Y, Z, I2, amplitude_damping_kraus, apply_kraus, bloch, dephasing_kraus,  # noqa: E402
                          depolarizing_kraus, dm, is_cptp)

R = 1.9
S2 = 1 / math.sqrt(2)


# --- exact Bloch maps, checked against the Kraus forms in qcai.science ------------------------------------------
def dep(v, s):
    return (1 - s) * np.asarray(v, dtype=float)


def deph(v, s):
    x, y, z = v
    return np.array([(1 - s) * x, (1 - s) * y, z])


def ad(v, s):
    x, y, z = v
    c = math.sqrt(1 - s)
    return np.array([c * x, c * y, s + (1 - s) * z])


def _check():
    rng = np.random.default_rng(3)
    for _ in range(5):
        v = rng.normal(size=3)
        v /= np.linalg.norm(v)
        rho = (I2 + v[0] * X + v[1] * Y + v[2] * Z) / 2
        for s in (0.2, 0.6, 0.9):
            assert np.allclose(bloch(apply_kraus(rho, depolarizing_kraus(s))), dep(v, s))
            assert np.allclose(bloch(apply_kraus(rho, dephasing_kraus(s))), deph(v, s))
            assert np.allclose(bloch(apply_kraus(rho, amplitude_damping_kraus(s))), ad(v, s))
            for k in (depolarizing_kraus(s), dephasing_kraus(s), amplitude_damping_kraus(s)):
                assert is_cptp(k)


_check()

# amplitude damping with gamma = 0.36: sqrt(1 - gamma) = 0.8, sqrt(gamma) = 0.6
GAMMA = 0.36
K0, K1 = amplitude_damping_kraus(GAMMA)
assert np.allclose(K0, [[1, 0], [0, 0.8]]) and np.allclose(K1, [[0, 0.6], [0, 0]])
assert np.allclose(K0.conj().T @ K0, np.diag([1, 0.64])) and np.allclose(K1.conj().T @ K1, np.diag([0, 0.36]))
OUT1 = apply_kraus(dm(KET1), [K0, K1])
assert np.allclose(OUT1, np.diag([0.36, 0.64]))
OUTP = apply_kraus(dm(np.array([S2, S2])), [K0, K1])
assert np.allclose(OUTP, [[0.68, 0.4], [0.4, 0.32]])
# the dilation unitary on S (x) E (system left): U|00> = |00>, U|10> = 0.8|10> + 0.6|01>
U_cols = {0: np.kron(KET0, KET0), 2: 0.8 * np.kron(KET1, KET0) + 0.6 * np.kron(KET0, KET1)}
for k, Kk in enumerate((K0, K1)):
    for s_in in (0, 1):
        col = U_cols[2 * s_in]                                   # U |s_in>|0>
        assert np.allclose(col.reshape(2, 2)[:, k], Kk[:, s_in])  # <k|_E U |s_in>|0>
# transpose: partial transpose of the Bell projector is SWAP/2 with eigenvalues 1/2, 1/2, 1/2, -1/2
BELL = np.array([S2, 0, 0, S2])
PB = dm(BELL)
PT = PB.reshape(2, 2, 2, 2).transpose(0, 3, 2, 1).reshape(4, 4)      # transpose on the right factor
SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
assert np.allclose(PT, SWAP / 2)
EIG = np.sort(np.linalg.eigvalsh(PT))
assert np.allclose(EIG, [-0.5, 0.5, 0.5, 0.5])

F_DEP = r"\vec r \mapsto (1-p)\,\vec r"
F_AD = r"(x, y, z) \mapsto (\sqrt{1-\gamma}\,x,\ \sqrt{1-\gamma}\,y,\ \gamma + (1-\gamma)z)"
F_KRAUS = r"K_0^\dagger K_0 + K_1^\dagger K_1"
F_U = r"U|1\rangle|0\rangle = 0.8\,|1\rangle|0\rangle + 0.6\,|0\rangle|1\rangle"
F_MIRROR = r"(x, y, z) \mapsto (x, -y, z)"
F_SWAP = r"\tfrac12\,\mathrm{SWAP}"


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [F_DEP, F_AD, F_KRAUS, F_U, F_MIRROR, F_SWAP, "0.36", "-1/2"]


def P(v):
    return np.array(v, dtype=float) * R


CURVES = [lambda u: [math.cos(u), math.sin(u), 0], lambda u: [math.cos(u), 0, math.sin(u)],
          lambda u: [0, math.cos(u), math.sin(u)],
          lambda u: [0.8 * math.cos(u), 0.8 * math.sin(u), 0.6], lambda u: [0.8 * math.cos(u), 0.8 * math.sin(u), -0.6]]


def wire(f=None, s=0.0, color=VIOLET, width=3):
    f = f or (lambda v, s: np.asarray(v, dtype=float))
    return VGroup(*[ParametricFunction(lambda u, c=c: P(f(c(u), s)), t_range=[0, 2 * PI], color=color,
                                       stroke_width=width if k < 3 else width * 0.6) for k, c in enumerate(CURVES)])


def fixed_redraw(scene, func):
    m = func()

    def upd(mob):
        mob.become(func())
        scene.renderer.camera.add_fixed_in_frame_mobjects(mob)
    m.add_updater(upd)
    scene.add_fixed_in_frame_mobjects(m)
    return m


class NoiseDeformsBall(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=20 * DEGREES)
        title = label("Noise deforms the Bloch ball", 34, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        ghost = wire(color=GRID, width=2)
        axis = DashedLine(P([0, 0, -1.15]), P([0, 0, 1.15]), color=MUTED, stroke_width=1.5)
        self.play(FadeIn(title), Create(ghost), Create(axis), run_time=1.4)
        labs = [eq(r"|0\rangle", size=32).move_to(P([0, 0, 1.3])), eq(r"|1\rangle", size=32).move_to(P([0, 0, -1.3])),
                eq(r"|+\rangle", size=32).move_to(P([1.35, 0, 0]))]
        self.add_fixed_orientation_mobjects(*labs)

        s = ValueTracker(0.0)
        chans = [
            ("Depolarizing", r"K:\ \sqrt{1-\tfrac{3p}{4}}\,I,\ \sqrt{\tfrac{p}{4}}\,X,\ \sqrt{\tfrac{p}{4}}\,Y,\ \sqrt{\tfrac{p}{4}}\,Z",
             F_DEP, dep, 0.6, "p", "uniform shrink toward I/2"),
            ("Dephasing", r"K:\ \sqrt{1-\tfrac{p}{2}}\,I,\ \sqrt{\tfrac{p}{2}}\,Z",
             r"(x, y, z) \mapsto ((1-p)\,x,\ (1-p)\,y,\ z)", deph, 0.8, "p", "squashed onto the z axis"),
            ("Amplitude damping", r"K_0 = \begin{pmatrix}1 & 0\\ 0 & \sqrt{1-\gamma}\end{pmatrix},\ "
             r"K_1 = \begin{pmatrix}0 & \sqrt{\gamma}\\ 0 & 0\end{pmatrix}", F_AD, ad, 0.7, r"\gamma",
             "shrinks toward the top"),
        ]
        for name, kraus, bmap, f, smax, sym, what in chans:
            head = VGroup(label(name, 30, VIOLET, "BOLD"), eq(kraus, size=30)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            head.to_corner(LEFT + UP, buff=0.3).shift(DOWN * 0.75)
            mp = eq(bmap, size=32, color=RED).to_edge(DOWN, buff=0.35)
            self.add_fixed_in_frame_mobjects(head, mp)
            body = always_redraw(lambda f=f: wire(f, s.get_value()))
            dots = always_redraw(lambda f=f: VGroup(Dot3D(P(f([0, 0, 1], s.get_value())), radius=0.09, color=BLUE),
                                                    Dot3D(P(f([0, 0, -1], s.get_value())), radius=0.09, color=RED),
                                                    Dot3D(P(f([1, 0, 0], s.get_value())), radius=0.09, color=AMBER)))
            self.play(FadeIn(head), FadeIn(mp), FadeIn(body), FadeIn(dots), run_time=1.0)

            def ro(sym=sym):
                g = VGroup(eq(f"{sym} =", size=34, color=INK),
                           DecimalNumber(s.get_value(), num_decimal_places=2, font_size=34, color=INK)).arrange(RIGHT, buff=0.15)
                return g.to_corner(RIGHT + UP, buff=0.3).shift(DOWN * 0.75 + LEFT * 0.4)
            r = fixed_redraw(self, ro)
            self.play(s.animate.set_value(smax), run_time=3.5, rate_func=smooth)
            r.clear_updaters()
            note = label(what, 26, MUTED).next_to(r, DOWN, buff=0.25).align_to(r, RIGHT)
            self.add_fixed_in_frame_mobjects(note)
            self.play(FadeIn(note))
            if f is ad:
                self.begin_ambient_camera_rotation(rate=0.3)
                self.wait(3.5)
                self.stop_ambient_camera_rotation()
            else:
                self.wait(1.2)
                self.play(FadeOut(VGroup(head, mp, r, note, body, dots)), run_time=0.8)
                s.set_value(0.0)
        self.wait(1.0)


class KrausDilation(Scene):
    def construct(self):
        title = label("A channel: a unitary with an environment, then forget it", 32, INK,
                      "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        yS, yE = 2.15, 1.25
        wires = VGroup(Line([-5.9, yS, 0], [-1.2, yS, 0], color=INK), Line([-5.9, yE, 0], [-2.6, yE, 0], color=INK))
        box = VGroup(Rectangle(width=1.0, height=1.5, color=VIOLET, fill_color="#ffffff", fill_opacity=1).move_to([-3.6, (yS + yE) / 2, 0]))
        box.add(eq("U", size=36, color=VIOLET).move_to(box))
        ins = VGroup(eq(r"\rho", size=34).next_to([-5.9, yS, 0], LEFT, buff=0.1),
                     eq(r"|0\rangle_E", size=32).next_to([-5.9, yE, 0], LEFT, buff=0.1))
        tr = VGroup(eq(r"\operatorname{Tr}_E", size=30, color=MUTED).next_to([-2.6, yE, 0], RIGHT, buff=0.1))
        outl = eq(r"\mathcal{E}(\rho)", size=34, color=RED).next_to([-1.2, yS, 0], RIGHT, buff=0.1)
        self.play(Create(wires), FadeIn(box), FadeIn(ins), FadeIn(tr), FadeIn(outl))

        acts = VGroup(eq(r"U|0\rangle|0\rangle = |0\rangle|0\rangle", size=32),
                      eq(F_U, size=32)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-3.2, -0.05, 0])
        gam = label("amplitude damping, \u03b3 = 0.36", 26, MUTED).next_to(acts, DOWN, buff=0.2)
        self.play(Write(acts[0]))
        self.play(Write(acts[1]), FadeIn(gam))

        kk = eq(r"K_k = \langle k|_E\, U\, |0\rangle_E", size=34, color=VIOLET).move_to([3.6, 2.4, 0])
        self.play(Write(kk))
        ks = VGroup(eq(r"K_0 = \begin{pmatrix}1 & 0\\ 0 & 0.8\end{pmatrix}", size=34),
                    eq(r"K_1 = \begin{pmatrix}0 & 0.6\\ 0 & 0\end{pmatrix}", size=34)).arrange(RIGHT, buff=0.5)
        ks.move_to([3.6, 1.2, 0])
        self.play(FadeIn(ks[0]))
        self.play(FadeIn(ks[1]))
        rule = eq(r"\mathcal{E}(\rho) = K_0\,\rho\,K_0^\dagger + K_1\,\rho\,K_1^\dagger", size=34, color=RED).move_to([3.6, 0.05, 0])
        self.play(Write(rule))

        c1 = eq(F_KRAUS, "=", r"\begin{pmatrix}1 & 0\\ 0 & 0.64\end{pmatrix}", "+", r"\begin{pmatrix}0 & 0\\ 0 & 0.36\end{pmatrix}",
                size=34).move_to([0, -1.75, 0])
        c2 = eq(F_KRAUS, "=", r"\begin{pmatrix}1 & 0\\ 0 & 1\end{pmatrix}", "=", "I", size=34).move_to(c1)
        self.play(Write(c1))
        self.play(TransformMatchingTex(c1, c2), run_time=1.4)
        tp = label("so the trace is preserved for every input", 24, MUTED).next_to(c2, DOWN, buff=0.15)
        self.play(FadeIn(tp))
        ex = VGroup(eq(r"\mathcal{E}(|1\rangle\langle 1|) = \begin{pmatrix}0.36 & 0\\ 0 & 0.64\end{pmatrix}", size=32),
                    eq(r"\mathcal{E}(|+\rangle\langle +|) = \begin{pmatrix}0.68 & 0.4\\ 0.4 & 0.32\end{pmatrix}", size=32))
        ex.arrange(RIGHT, buff=0.7).move_to([0, -3.25, 0])
        self.play(FadeIn(ex[0]))
        self.play(FadeIn(ex[1]))
        self.play(Indicate(ex, color=RED))
        self.wait(1.5)


class TransposeNotCP(Scene):
    def construct(self):
        title = label("The transpose is positive but not completely positive", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        c = np.array([-3.6, -0.3, 0])
        rad = 2.1
        disk = Circle(radius=rad, color=MUTED).move_to(c)
        xax = DashedLine(c + LEFT * (rad + 0.3), c + RIGHT * (rad + 0.3), color=AMBER)
        yax = DashedLine(c + DOWN * (rad + 0.3), c + UP * (rad + 0.3), color=GRID)
        lx = label("x", 26, MUTED).next_to(xax, RIGHT, buff=0.1)
        ly = label("y", 26, MUTED).next_to(yax, UP, buff=0.05)
        top = label("Bloch ball seen from the top (z out of the page)", 24, MUTED).next_to(disk, DOWN, buff=0.45)
        self.play(Create(disk), Create(xax), Create(yax), FadeIn(lx), FadeIn(ly), FadeIn(top))
        v = np.array([0.55, 0.65, 0])
        a1 = Arrow(c, c + rad * v, buff=0, color=VIOLET, stroke_width=6)
        self.play(Create(a1))
        a2 = a1.copy()
        self.play(a2.animate.become(Arrow(c, c + rad * np.array([0.55, -0.65, 0]), buff=0, color=AMBER, stroke_width=6)),
                  run_time=1.5)
        rt = VGroup(eq(r"T(\rho) = \rho^T", size=36), eq(r"X^T = X,\ \ Y^T = -Y,\ \ Z^T = Z", size=32),
                    eq(F_MIRROR, size=34, color=AMBER),
                    label("a mirror: the ball goes onto itself,", 26, INK), label("so T maps states to states (positive)", 26, INK))
        rt.arrange(DOWN, buff=0.28).move_to([3.2, 0.4, 0])
        for m in rt:
            self.play(FadeIn(m), run_time=0.7)
        self.wait(0.8)
        self.play(FadeOut(VGroup(disk, xax, yax, lx, ly, top, a1, a2, rt)))

        # extension to a reference qubit
        cell = 0.85
        c0 = np.array([-3.7, -0.5, 0])

        def pos(i, j):
            return c0 + np.array([(j - 1.5) * cell, (1.5 - i) * cell, 0])
        G = VGroup(*[eq("1/2" if (i, j) in ((0, 0), (0, 3), (3, 0), (3, 3)) else "0", size=34,
                        color=VIOLET if (i, j) in ((0, 3), (3, 0)) else INK).move_to(pos(i, j))
                     for i in range(4) for j in range(4)])
        names = ["00", "01", "10", "11"]
        rl = VGroup(*[label(n, 24, MUTED).move_to(pos(i, 0) + LEFT * 0.8) for i, n in enumerate(names)])
        cl = VGroup(*[label(n, 24, MUTED).move_to(pos(0, j) + UP * 0.6) for j, n in enumerate(names)])
        head = eq(r"|\Phi^+\rangle\langle\Phi^+|", size=36, color=VIOLET).move_to(c0 + UP * 2.55)
        blocks = VGroup(*[Rectangle(width=2 * cell - 0.08, height=2 * cell - 0.08, color=MUTED, stroke_width=2)
                          .move_to((pos(2 * a, 2 * b) + pos(2 * a + 1, 2 * b + 1)) / 2) for a in (0, 1) for b in (0, 1)])
        self.play(FadeIn(head), FadeIn(rl), FadeIn(cl), FadeIn(G), Create(blocks))
        step = VGroup(eq(r"(\mathrm{id}\otimes T):\ \text{transpose each block}", size=32),
                      label("(the reference qubit is left alone)", 24, MUTED)).arrange(DOWN, buff=0.12).move_to([3.3, 2.3, 0])
        self.play(FadeIn(step))
        a, b = G[3], G[12]
        ta, tb = G[6].copy(), G[9].copy()
        self.play(a.animate.move_to(pos(1, 2)), b.animate.move_to(pos(2, 1)), FadeOut(G[6]), FadeOut(G[9]), run_time=1.6)
        za, zb = eq("0", size=34).move_to(pos(0, 3)), eq("0", size=34).move_to(pos(3, 0))
        self.play(FadeIn(za), FadeIn(zb))
        res = eq(r"= " + F_SWAP, size=38, color=RED).move_to([3.3, 1.2, 0])
        self.play(Write(res))

        # eigenvalues
        base, sc = -1.4, 1.2
        xs = [2.0, 2.9, 3.8, 4.7]
        vals = [0.5, 0.5, 0.5, -0.5]
        axis = Line([1.5, base, 0], [5.2, base, 0], color=MUTED)
        bars = VGroup(*[Rectangle(width=0.6, height=abs(v) * sc * 2, color=RED if v < 0 else VIOLET,
                                  fill_color=RED if v < 0 else VIOLET, fill_opacity=0.75, stroke_width=1)
                        .move_to([x, base + v * sc, 0]) for x, v in zip(xs, vals)])
        vl = VGroup(*[eq("1/2" if v > 0 else "-1/2", size=30, color=RED if v < 0 else VIOLET)
                      .move_to([x, base + v * sc * 2 + (0.28 if v > 0 else -0.3), 0]) for x, v in zip(xs, vals)])
        el = label("eigenvalues", 26, MUTED).move_to([0.45, base + 0.6, 0])
        self.play(Create(axis), FadeIn(el), *[FadeIn(bb) for bb in bars], FadeIn(vl))
        sing = eq(r"\text{eigenvector } \tfrac{1}{\sqrt2}(|01\rangle - |10\rangle)", size=30, color=RED).move_to([-3.2, -3.05, 0])
        self.play(FadeIn(sing))
        self.play(Indicate(bars[3], color=RED), Indicate(vl[3], color=RED))
        concl = label("a negative 'probability': no physical process acts as T on half of a pair", 26, RED)
        concl.to_edge(DOWN, buff=0.12)
        self.play(FadeOut(sing), FadeIn(concl))
        self.wait(2.0)
        _ = (ta, tb, SurroundingRectangle, Transform, Dot3D)
