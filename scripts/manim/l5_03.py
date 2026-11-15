"""L5-03 Phase and interference: three scenes.

MachZehnderLive         an interferometer drawn as beam splitter, two arms, phase shifter, beam splitter and
                        two detectors.  As the phase phi sweeps once around, the two path amplitudes 1/2 and
                        e^{i phi}/2 add head to tail at D0, detector bars follow, and P(D0) = (1 + cos phi)/2 is
                        traced live next to P(D1) = (1 - cos phi)/2.
InterferenceDerivation  H P(phi) H |0> worked out term by term with TransformMatchingTex down to
                        P(0) = (1 + cos phi)/2 = cos^2(phi/2); then why a global phase, or a phase applied
                        before the first H, changes nothing.
PhaseOnBloch            ThreeDScene: H puts |0> on the equator, the phase turns it about z, the second H swings
                        it onto the yz great circle with height cos phi; then marking the path shrinks the
                        vector to length V and the fringe to (1 + V cos phi)/2.
"""
import cmath
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, OUT, PI, RIGHT, TAU, UP, Arrow, Axes, Circle, Create, DashedLine, DecimalNumber,
                   Dot, Dot3D, FadeIn, FadeOut, Line, Rectangle, Scene, Sphere, SurroundingRectangle, ThreeDScene,
                   TracedPath, TransformMatchingTex, ValueTracker, VGroup, VMobject, Write, always_redraw, linear,
                   smooth)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

from qcai import science  # noqa: E402

H, X, Z = science.H, science.X, science.Z


def P(phi):
    return np.diag([1, np.exp(1j * phi)])


def p0(phi, v=1.0):
    return science.interference(phi, v)["p0"]


for _phi in np.linspace(0, TAU, 13):
    _out = H @ P(_phi) @ H @ science.KET0
    assert abs(abs(_out[0]) ** 2 - p0(_phi)) < 1e-12
    assert abs(abs((1 + cmath.exp(1j * _phi)) / 2) ** 2 - p0(_phi)) < 1e-12
    assert abs(p0(_phi) - math.cos(_phi / 2) ** 2) < 1e-12
PHI_EX = 2 * PI / 3
assert abs(p0(PHI_EX) - 0.25) < 1e-12
V_MARK = 0.5
assert abs(p0(0, V_MARK) - 0.75) < 1e-12 and abs(p0(PI, V_MARK) - 0.25) < 1e-12


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["\\frac{1 + \\cos\\varphi}{2}", "\\cos^2\\frac{\\varphi}{2}", "\\frac{1 + V\\cos\\varphi}{2}",
            "e^{i\\gamma}", "0.25"]


# ---- scene 1 --------------------------------------------------------------------------------------
class MachZehnderLive(Scene):
    def construct(self):
        title = label("A Mach-Zehnder interferometer turns phase into counts", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        phi = ValueTracker(0.0)

        # layout of the interferometer (left half of the frame)
        b1, mu, ml, b2 = np.array([-5.6, -0.6, 0]), np.array([-5.6, 1.6, 0]), np.array([-2.2, -0.6, 0]), np.array([-2.2, 1.6, 0])
        src = np.array([-6.6, -0.6, 0])
        d0, d1 = np.array([-1.0, 1.6, 0]), np.array([-2.2, 2.6, 0])
        beam = dict(color=VIOLET, stroke_width=4)
        paths = VGroup(Line(src, b1, **beam), Line(b1, mu, **beam), Line(mu, b2, **beam), Line(b1, ml, **beam), Line(ml, b2, **beam),
                       Line(b2, d0 + LEFT * 0.25, **beam), Line(b2, d1 + DOWN * 0.25, **beam))
        bs = VGroup(*[Line(p + np.array([-0.32, -0.32, 0]), p + np.array([0.32, 0.32, 0]), color=CYAN, stroke_width=8) for p in (b1, b2)])
        mirrors = VGroup(*[Line(p + np.array([-0.3, -0.3, 0]), p + np.array([0.3, 0.3, 0]), color=MUTED, stroke_width=8) for p in (mu, ml)])
        shifter = Rectangle(width=0.7, height=0.5, fill_color=AMBER, fill_opacity=0.35, stroke_color=AMBER).move_to((b1 + ml) / 2)
        sh_l = eq(r"\varphi", size=34, color=AMBER).next_to(shifter, DOWN, buff=0.12)
        bl = VGroup(eq("H", size=30, color=CYAN).move_to(b1 + np.array([-0.5, -0.45, 0])),
                    eq("H", size=30, color=CYAN).move_to(b2 + np.array([0.5, -0.45, 0])))
        dets = VGroup(Rectangle(width=0.4, height=0.6, fill_color=INK, fill_opacity=1).move_to(d0),
                      Rectangle(width=0.6, height=0.4, fill_color=INK, fill_opacity=1).move_to(d1))
        dl = VGroup(label("D0", 24, INK).next_to(dets[0], DOWN, buff=0.1), label("D1", 24, INK).next_to(dets[1], LEFT, buff=0.12))
        pl = VGroup(label("path 0", 24, MUTED).next_to((b1 + mu) / 2, LEFT, buff=0.15),
                    label("path 1", 24, MUTED).next_to((b1 + ml) / 2 + RIGHT * 0.9, DOWN, buff=0.15))
        self.play(Create(paths), FadeIn(bs), FadeIn(mirrors), run_time=1.6)
        self.play(FadeIn(shifter), Write(sh_l), FadeIn(bl), FadeIn(dets), FadeIn(dl), FadeIn(pl))

        # detector brightness bars below the interferometer
        base_y = -3.3
        bars_base = Line(np.array([-5.4, base_y, 0]), np.array([-2.4, base_y, 0]), color=MUTED, stroke_width=2)
        bar_lab = VGroup(label("D0", 24, VIOLET).move_to(np.array([-4.6, base_y - 0.25, 0])),
                         label("D1", 24, CYAN).move_to(np.array([-3.2, base_y - 0.25, 0])))
        hmax = 1.5

        def bar(x, h, col):
            return Rectangle(width=0.7, height=max(h * hmax, 0.001), fill_color=col, fill_opacity=0.8, stroke_width=0).move_to(
                np.array([x, base_y + h * hmax / 2, 0]))
        bars = always_redraw(lambda: VGroup(bar(-4.6, p0(phi.get_value()), VIOLET), bar(-3.2, 1 - p0(phi.get_value()), CYAN)))
        self.play(Create(bars_base), FadeIn(bar_lab), FadeIn(bars))

        # phasors arriving at D0 (top right)
        o = np.array([1.2, 1.55, 0])
        s = 1.6
        circ = Circle(radius=0.5 * s, color=GRID, stroke_width=2).move_to(o + RIGHT * 0.5 * s)
        a1 = Arrow(o, o + RIGHT * 0.5 * s, buff=0, color=BLUE, stroke_width=6)
        a2 = always_redraw(lambda: Arrow(o + RIGHT * 0.5 * s, o + RIGHT * 0.5 * s + 0.5 * s * np.array([math.cos(phi.get_value()), math.sin(phi.get_value()), 0]),
                                         buff=0, color=AMBER, stroke_width=6, max_tip_length_to_length_ratio=0.3))
        tot = always_redraw(lambda: Line(o, o + RIGHT * 0.5 * s + 0.5 * s * np.array([math.cos(phi.get_value()), math.sin(phi.get_value()), 0]),
                                         color=RED, stroke_width=4))
        amp = eq(r"\text{amplitude at D0} = \frac{1}{2} + \frac{1}{2}e^{i\varphi}", size=30).move_to(np.array([3.9, 2.75, 0]))
        self.play(Create(circ), Create(a1), Create(a2), Create(tot), Write(amp))

        # live fringe (bottom right)
        ax = Axes(x_range=[0, TAU, PI / 2], y_range=[0, 1, 0.5], x_length=5.0, y_length=2.2,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(np.array([3.7, -1.95, 0]))
        xt = VGroup(*[eq(t, size=26, color=MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.12)
                      for t, v in ((r"0", 0), (r"\pi", PI), (r"2\pi", TAU))])
        yt = VGroup(*[eq(t, size=26, color=MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.1) for t, v in (("1", 1), ("0.5", 0.5))])
        fl = eq(r"P(D0) = \frac{1 + \cos\varphi}{2}", size=30, color=VIOLET).next_to(ax, UP, buff=0.25).align_to(ax, LEFT)
        d1c = ax.plot(lambda x: 1 - p0(x), x_range=[0, TAU], color=CYAN, stroke_width=2)
        d1c.set_stroke(opacity=0.45)
        self.play(Create(ax), FadeIn(xt), FadeIn(yt), Write(fl), Create(d1c))
        dot = always_redraw(lambda: Dot(ax.c2p(phi.get_value(), p0(phi.get_value())), color=VIOLET, radius=0.07))
        trace = TracedPath(dot.get_center, stroke_color=VIOLET, stroke_width=4)
        self.add(trace, dot)
        self.play(phi.animate.set_value(PHI_EX), run_time=4, rate_func=linear)
        ex = eq(r"\varphi = \frac{2\pi}{3}:\ P(D0) = 0.25", size=30, color=INK).move_to(np.array([4.75, 1.55, 0]))
        self.play(Write(ex))
        self.wait(1.0)
        self.play(FadeOut(ex))
        self.play(phi.animate.set_value(TAU), run_time=6, rate_func=linear)
        notes = VGroup(label("φ = 0: every photon at D0", 24, MUTED),
                       label("φ = π: every photon at D1", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        notes.move_to(np.array([4.75, 1.55, 0]))
        self.play(FadeIn(notes))
        self.wait(2.0)


# ---- scene 2 --------------------------------------------------------------------------------------
class InterferenceDerivation(Scene):
    def construct(self):
        title = label("Where the fringe comes from", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        circ = eq(r"|0\rangle \;\to\; H \;\to\; P(\varphi) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\varphi} \end{pmatrix} \;\to\; H", size=36, color=MUTED)
        circ.move_to(UP * 2.5)
        self.play(Write(circ), run_time=1.6)
        steps = [
            eq(r"H\,P(\varphi)\,H|0\rangle", "=", r"H\,P(\varphi)", r"\frac{1}{\sqrt{2}}\left(|0\rangle + |1\rangle\right)", size=40),
            eq(r"H\,P(\varphi)\,H|0\rangle", "=", "H", r"\frac{1}{\sqrt{2}}\left(|0\rangle + e^{i\varphi}|1\rangle\right)", size=40),
            eq(r"H\,P(\varphi)\,H|0\rangle", "=", r"\frac{1 + e^{i\varphi}}{2}|0\rangle", "+", r"\frac{1 - e^{i\varphi}}{2}|1\rangle", size=40),
        ]
        for m in steps:
            m.move_to(UP * 1.2)
        self.play(Write(steps[0]), run_time=1.6)
        self.wait(0.8)
        for a, b in zip(steps, steps[1:]):
            self.play(TransformMatchingTex(a, b), run_time=1.6)
            self.wait(0.9)
        born = [
            eq("P(0)", "=", r"\frac{1}{4}\left|1 + e^{i\varphi}\right|^2", size=40),
            eq("P(0)", "=", r"\frac{1}{4}\left(2 + 2\cos\varphi\right)", size=40),
            eq("P(0)", "=", r"\frac{1 + \cos\varphi}{2}", "=", r"\cos^2\frac{\varphi}{2}", size=40, color=VIOLET),
        ]
        for m in born:
            m.move_to(DOWN * 0.15)
        self.play(Write(born[0]), run_time=1.4)
        self.wait(0.6)
        for a, b in zip(born, born[1:]):
            self.play(TransformMatchingTex(a, b), run_time=1.5)
            self.wait(0.8)
        self.play(Create(SurroundingRectangle(born[-1], color=VIOLET, buff=0.15)))
        ref = label("the same 2 + 2 cos φ as two unit arrows in L3-01", 24, MUTED).next_to(born[-1], DOWN, buff=0.35)
        self.play(FadeIn(ref))
        self.wait(0.8)

        g1 = eq(r"\text{phase on both arms: } e^{i\gamma} I \;\Rightarrow\; \text{global, no change}", size=32, color=INK)
        g2 = eq(r"\text{phase before the first } H\text{: } P(\varphi)|0\rangle = |0\rangle \;\Rightarrow\; \text{no change}", size=32, color=INK)
        g3 = eq(r"\text{only the phase between the arms, between the } H\text{s, matters}", size=32, color=RED)
        grp = VGroup(g1, g2, g3).arrange(DOWN, buff=0.22).move_to(DOWN * 2.65)
        for g in grp:
            self.play(Write(g), run_time=1.3)
        self.wait(2.0)


# ---- scene 3 --------------------------------------------------------------------------------------
CAM_PHI, CAM_THETA = 72 * DEGREES, 20 * DEGREES
SCREEN_RIGHT = np.array([-math.sin(CAM_THETA), math.cos(CAM_THETA), 0.0])
CENTER = -3.2 * SCREEN_RIGHT
R = 2.0
LIGHT = "#cbd5e1"


def fixed(scene, *mobs):
    scene.add_fixed_in_frame_mobjects(*mobs)
    scene.remove(*mobs)


class PhaseOnBloch(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=CAM_PHI, theta=CAM_THETA)
        title = label("H, phase, H on the Bloch sphere", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        fixed(self, title)
        self.play(Write(title), run_time=1.0)
        sph = Sphere(center=CENTER, radius=R, resolution=(18, 18)).set_fill(VIOLET, opacity=0.05).set_stroke(GRID, width=0.4, opacity=0.5)
        t = np.linspace(0, TAU, 97)
        eqt = VMobject(stroke_color=LIGHT, stroke_width=2).set_points_smoothly([CENTER + R * np.array([math.cos(a), math.sin(a), 0]) for a in t])
        yz = VMobject(stroke_color=LIGHT, stroke_width=2).set_points_smoothly([CENTER + R * np.array([0, math.sin(a), math.cos(a)]) for a in t])
        axes = VGroup(*[Line(CENTER - 1.2 * R * d, CENTER + 1.2 * R * d, color=MUTED, stroke_width=2) for d in (RIGHT, UP, OUT)])
        self.play(Create(sph), Create(eqt), Create(yz), Create(axes), run_time=1.4)
        for m, p in ((eq(r"|0\rangle", size=32), CENTER + 1.38 * R * OUT), (eq(r"|1\rangle", size=32), CENTER - 1.38 * R * OUT),
                     (eq("x", size=30, color=MUTED), CENTER + 1.32 * R * RIGHT), (eq("y", size=30, color=MUTED), CENTER + 1.3 * R * UP)):
            m.move_to(p)
            self.add_fixed_orientation_mobjects(m)

        # the state is held as a Bloch vector r (a 3-vector) driven by trackers
        state = {"r": np.array([0, 0, 1.0])}
        tip = lambda: CENTER + R * state["r"]  # noqa: E731
        vec = always_redraw(lambda: Line(CENTER, tip(), color=VIOLET, stroke_width=6))
        dot = always_redraw(lambda: Dot3D(tip(), radius=0.08, color=VIOLET))
        self.add(vec, dot)
        n_h = np.array([1, 0, 1]) / math.sqrt(2)

        def rot(r, n, a):
            return r * math.cos(a) + np.cross(n, r) * math.sin(a) + n * np.dot(n, r) * (1 - math.cos(a))

        info = eq(r"|0\rangle \to H \to P(\varphi) \to H", size=34).move_to(RIGHT * 3.5 + UP * 2.4)
        fixed(self, info)
        self.play(Write(info))

        # 1) first H: half turn about (x+z)/sqrt2 takes |0> to |+>
        s = ValueTracker(0.0)
        start = state["r"].copy()
        upd = lambda m: state.__setitem__("r", rot(start, n_h, PI * s.get_value()))  # noqa: E731
        vec.add_updater(upd)
        trail = TracedPath(dot.get_center, stroke_color=CYAN, stroke_width=4)
        self.add(trail)
        st1 = label("first H: |0⟩ to |+⟩ on the equator", 24, CYAN).move_to(RIGHT * 3.5 + UP * 1.6)
        fixed(self, st1)
        self.play(FadeIn(st1), s.animate.set_value(1), run_time=2.5)
        vec.remove_updater(upd)
        trail.clear_updaters()
        state["r"] = np.array([1.0, 0, 0])

        # 2) phase: quarter-turn family about z, to phi = 2pi/3
        ph = ValueTracker(0.0)
        upd2 = lambda m: state.__setitem__("r", np.array([math.cos(ph.get_value()), math.sin(ph.get_value()), 0.0]))  # noqa: E731
        vec.add_updater(upd2)
        trail2 = TracedPath(dot.get_center, stroke_color=AMBER, stroke_width=4)
        self.add(trail2)
        st2 = label("phase: turn by φ about z", 24, AMBER).move_to(RIGHT * 3.5 + UP * 1.1)
        fixed(self, st2)
        self.play(FadeIn(st2), ph.animate.set_value(PHI_EX), run_time=2.5)
        vec.remove_updater(upd2)
        trail2.clear_updaters()

        # 3) second H: (x, y, z) -> (z, -y, x)
        s3 = ValueTracker(0.0)
        start3 = state["r"].copy()
        upd3 = lambda m: state.__setitem__("r", rot(start3, n_h, PI * s3.get_value()))  # noqa: E731
        vec.add_updater(upd3)
        trail3 = TracedPath(dot.get_center, stroke_color=BLUE, stroke_width=4)
        self.add(trail3)
        st3 = label("second H: height becomes cos φ", 24, BLUE).move_to(RIGHT * 3.5 + UP * 0.6)
        fixed(self, st3)
        self.play(FadeIn(st3), s3.animate.set_value(1), run_time=2.5)
        vec.remove_updater(upd3)
        trail3.clear_updaters()
        end = np.array([0.0, -math.sin(PHI_EX), math.cos(PHI_EX)])
        assert np.allclose(state["r"], end, atol=1e-9)
        assert np.allclose(end, science.bloch(science.dm(H @ P(PHI_EX) @ H @ science.KET0)), atol=1e-9)
        res = eq(r"\varphi = \frac{2\pi}{3}:\ z = -\frac{1}{2},\ P(0) = 0.25", size=32, color=VIOLET).move_to(RIGHT * 3.5 + DOWN * 0.2)
        fixed(self, res)
        self.play(Write(res))
        self.wait(0.8)
        self.play(FadeOut(VGroup(st1, st2, st3, res)), FadeOut(trail), FadeOut(trail2), FadeOut(trail3))

        # 4) sweep the phase: the output runs round the yz circle, projection gives the fringe
        ph2 = ValueTracker(PHI_EX)
        vlen = ValueTracker(1.0)
        out = lambda: vlen.get_value() * np.array([0.0, -math.sin(ph2.get_value()), math.cos(ph2.get_value())])  # noqa: E731
        upd4 = lambda m: state.__setitem__("r", out())  # noqa: E731
        vec.add_updater(upd4)
        proj = always_redraw(lambda: DashedLine(tip(), CENTER + R * state["r"][2] * OUT, color=AMBER, stroke_width=3))
        zdot = always_redraw(lambda: Dot3D(CENTER + R * state["r"][2] * OUT, radius=0.08, color=AMBER))
        self.add(proj, zdot)
        left = eq(r"P(0) = \frac{1 + z}{2} =", size=34, color=VIOLET)
        num = DecimalNumber(p0(PHI_EX), num_decimal_places=3, font_size=34, color=VIOLET)
        ro = VGroup(left, num).arrange(RIGHT, buff=0.15).move_to(RIGHT * 3.5 + UP * 1.55)
        num.add_updater(lambda m: (m.set_value((1 + state["r"][2]) / 2), self.renderer.camera.add_fixed_in_frame_mobjects(m)))
        rule = eq(r"P(0) = \frac{1 + \cos\varphi}{2}", size=34, color=INK).move_to(RIGHT * 3.5 + UP * 0.4)
        fixed(self, ro, rule)
        self.play(FadeIn(ro), Write(rule))
        self.play(ph2.animate.set_value(PHI_EX + TAU), run_time=6, rate_func=linear)

        # 5) which-path marking shrinks the vector: fringe contrast V
        mark = label("mark the path: length shrinks to V", 24, RED).move_to(RIGHT * 3.5 + DOWN * 0.4)
        rule2 = eq(r"P(0) = \frac{1 + V\cos\varphi}{2}", size=34, color=RED).move_to(RIGHT * 3.5 + DOWN * 1.2)
        fixed(self, mark, rule2)
        self.play(FadeIn(mark), Write(rule2))
        self.play(vlen.animate.set_value(V_MARK), run_time=2, rate_func=smooth)
        rng = label("V = 0.5: P(0) only swings from 0.25 to 0.75", 24, MUTED).move_to(RIGHT * 3.5 + DOWN * 2.0)
        fixed(self, rng)
        self.play(FadeIn(rng))
        self.play(ph2.animate.set_value(PHI_EX + 2 * TAU), run_time=6, rate_func=linear)
        self.wait(1.5)
        _ = (Arrow, DashedLine, CYAN, FadeOut, smooth, linear, LEFT, DOWN)
