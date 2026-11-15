"""L5-01 States and the Born rule: three scenes.

BornRuleShots    amplitudes sqrt(3)/2 and 1/2 become probability bars 3/4 and 1/4; then seeded shots
                 (science.trials, seed 42) make the frequency bars and a running-frequency trace settle
                 inside the 2-sigma band; pauses at n = 400 (95 ones, expected 100) and n = 4000.
BlochSphereBorn  ThreeDScene: the polar angle sets P(0) = (1 + z)/2 as the projection onto the z axis,
                 the azimuth turns the state on a ring of equal P(0), and a global phase spins both
                 amplitude arrows while the Bloch point stays put.
BasisReveal      ThreeDScene: equator states (|0> + e^{i phi}|1>)/sqrt 2 look identical in the Z basis
                 (1/2, 1/2) but the X basis reads the relative phase: P(+) = (1 + cos phi)/2.
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, OUT, PI, RIGHT, TAU, UP, Axes, Circle, Create, DashedLine, DecimalNumber, Dot,
                   Dot3D, FadeIn, FadeOut, Line, Polygon, Rectangle, Scene, Sphere, ThreeDScene, TracedPath,
                   Transform, ValueTracker, VGroup, VMobject, Write, always_redraw, linear, smooth)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

from qcai import science  # noqa: E402  (qcai_style puts the book folder on sys.path)

# ---- the numbers the lesson text states -------------------------------------------------------
ALPHA, BETA = math.sqrt(3) / 2, 0.5
P0, P1 = ALPHA ** 2, BETA ** 2
assert abs(P0 - 0.75) < 1e-12 and abs(P1 - 0.25) < 1e-12
SEED = 42
RUN = science.trials(P1, 4000, seed=SEED)
TRACE = RUN["trace"]
HITS = {n: round(TRACE[n - 1] * n) for n in (10, 100, 400, 4000)}
assert HITS[400] == 95 and HITS[4000] == 990
SD400 = math.sqrt(400 * P1 * P0)
assert abs(SD400 - 8.66) < 0.005
THETA_EX = math.radians(60)                 # cos(30 deg) = sqrt(3)/2, so the example state has theta = 60 deg
assert abs(math.cos(THETA_EX / 2) - ALPHA) < 1e-12
Q_EX = science.qubit(THETA_EX, 0.0)
assert abs(Q_EX["p0"] - 0.75) < 1e-12 and abs(Q_EX["z"] - 0.5) < 1e-12


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["95", "990", "8.66", "0.750", "P(+) = \\frac{1 + \\cos\\varphi}{2}", "e^{i\\gamma}|\\psi\\rangle"]


# ---- shared Bloch-sphere helpers --------------------------------------------------------------
R = 2.0
CAM_PHI, CAM_THETA = 72 * DEGREES, 20 * DEGREES
SCREEN_RIGHT = np.array([-math.sin(CAM_THETA), math.cos(CAM_THETA), 0.0])
CENTER = -3.2 * SCREEN_RIGHT                # the sphere sits on the left of the frame
LIGHT = "#cbd5e1"


def bvec(theta, phi):
    return np.array([math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)])


def bpt(theta, phi):
    return CENTER + R * bvec(theta, phi)


def bloch_frame(scene):
    """Sphere, equator, prime meridian, axes and pole labels; returns the group (labels face the camera)."""
    sph = Sphere(center=CENTER, radius=R, resolution=(18, 18))
    sph.set_fill(VIOLET, opacity=0.05).set_stroke(GRID, width=0.4, opacity=0.5)
    t = np.linspace(0, TAU, 97)
    eqt = VMobject(stroke_color=LIGHT, stroke_width=2).set_points_smoothly([CENTER + R * np.array([math.cos(a), math.sin(a), 0]) for a in t])
    mer = VMobject(stroke_color=LIGHT, stroke_width=2).set_points_smoothly([CENTER + R * np.array([math.sin(a), 0, math.cos(a)]) for a in t])
    axes = VGroup(*[Line(CENTER - 1.2 * R * d, CENTER + 1.2 * R * d, color=MUTED, stroke_width=2)
                    for d in (RIGHT, UP, OUT)])
    labs = [(eq(r"|0\rangle", size=34), CENTER + 1.38 * R * OUT), (eq(r"|1\rangle", size=34), CENTER - 1.38 * R * OUT),
            (eq("x", size=32, color=MUTED), CENTER + 1.32 * R * RIGHT), (eq("y", size=32, color=MUTED), CENTER + 1.3 * R * UP)]
    group = VGroup(sph, eqt, mer, axes)
    scene.play(Create(sph), Create(eqt), Create(mer), Create(axes), run_time=1.6)
    for m, p in labs:
        m.move_to(p)
        scene.add_fixed_orientation_mobjects(m)
    return group


def fixed(scene, *mobs):
    """Pin mobjects to the screen without showing them yet (Write/FadeIn shows them)."""
    scene.add_fixed_in_frame_mobjects(*mobs)
    scene.remove(*mobs)


# ---- scene 1 ----------------------------------------------------------------------------------
class BornRuleShots(Scene):
    def construct(self):
        title = label("Amplitudes in, probabilities out, frequencies settle", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        state = eq(r"|\psi\rangle = \frac{\sqrt{3}}{2}|0\rangle + \frac{1}{2}|1\rangle", size=40).move_to(LEFT * 3.4 + UP * 2.35)
        self.play(Write(title), Write(state), run_time=1.6)

        base_y, scale = -2.5, 3.2
        xs = (-4.6, -2.3)
        base = Line(LEFT * 5.9 + UP * base_y, LEFT * 1.1 + UP * base_y, color=MUTED, stroke_width=2)
        outs = VGroup(*[eq(f"{k}", size=34, color=MUTED).move_to(RIGHT * x + UP * (base_y - 0.35)) for k, x in enumerate(xs)])

        def bar(x, h, color):
            return Rectangle(width=1.1, height=max(h * scale, 0.001), fill_color=color, fill_opacity=0.75,
                             stroke_width=0).move_to(RIGHT * x + UP * (base_y + h * scale / 2))

        amp = VGroup(bar(xs[0], ALPHA, BLUE), bar(xs[1], BETA, BLUE))
        amp_l = VGroup(eq(r"\alpha = \frac{\sqrt{3}}{2}", size=32, color=BLUE).next_to(amp[0], UP, buff=0.12),
                       eq(r"\beta = \frac{1}{2}", size=32, color=BLUE).next_to(amp[1], UP, buff=0.12))
        self.play(Create(base), FadeIn(outs), FadeIn(amp), Write(amp_l))
        self.wait(0.6)
        prob = VGroup(bar(xs[0], P0, VIOLET), bar(xs[1], P1, VIOLET))
        prob_l = VGroup(eq(r"|\alpha|^2 = \frac{3}{4}", size=32, color=VIOLET).next_to(prob[0], UP, buff=0.12),
                        eq(r"|\beta|^2 = \frac{1}{4}", size=32, color=VIOLET).next_to(prob[1], UP, buff=0.12))
        born = eq(r"P(k) = |\langle k|\psi\rangle|^2", size=34, color=INK).move_to(LEFT * 3.4 + UP * 1.4)
        self.play(Transform(amp, prob), Transform(amp_l, prob_l), Write(born), run_time=1.6)
        self.wait(0.8)

        # targets stay as dashed lines; bars now show observed frequencies
        targets = VGroup(*[DashedLine(RIGHT * (x - 0.7) + UP * (base_y + p * scale), RIGHT * (x + 0.7) + UP * (base_y + p * scale),
                                      color=INK, stroke_width=2) for x, p in zip(xs, (P0, P1))])
        self.play(Create(targets), FadeOut(amp_l))
        self.remove(amp)
        k = ValueTracker(0.0)                       # log10 of the number of shots

        def n_now():
            return max(1, min(4000, int(round(10 ** k.get_value()))))

        def freqs():
            n = n_now()
            f1 = TRACE[n - 1]
            return 1 - f1, f1

        bars = always_redraw(lambda: VGroup(bar(xs[0], freqs()[0], CYAN), bar(xs[1], freqs()[1], AMBER)))
        self.add(bars)
        self.bring_to_front(targets)

        # right: running frequency of outcome 1 against log10 n, inside the 2-sigma band
        ax = Axes(x_range=[0, 3.7, 1], y_range=[0, 0.6, 0.25], x_length=5.4, y_length=3.4,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 3.3 + DOWN * 0.95)
        ticks = VGroup(*[eq(s, size=28, color=MUTED).next_to(ax.c2p(i, 0), DOWN, buff=0.15)
                         for i, s in enumerate(("1", "10", "100", "1000"))])
        yt = VGroup(*[eq(s, size=28, color=MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.12) for s, v in (("0.25", 0.25), ("0.5", 0.5))])
        xl = label("shots n (log scale)", 24, MUTED).next_to(ticks, DOWN, buff=0.12)
        yl = label("fraction of 1s", 24, MUTED).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        grid_n = sorted({int(round(10 ** (i / 60))) for i in range(0, 217)})
        up = [ax.c2p(math.log10(n), min(0.6, P1 + 2 * math.sqrt(P1 * P0 / n))) for n in grid_n]
        lo = [ax.c2p(math.log10(n), max(0.0, P1 - 2 * math.sqrt(P1 * P0 / n))) for n in grid_n]
        band = Polygon(*up, *lo[::-1], fill_color="#cffafe", fill_opacity=0.9, stroke_width=0)
        mid = DashedLine(ax.c2p(0, P1), ax.c2p(3.7, P1), color=INK, stroke_width=2)
        self.play(Create(ax), FadeIn(band), Create(mid), FadeIn(ticks), FadeIn(yt), FadeIn(xl), FadeIn(yl), run_time=1.4)

        def trace_line():
            n = n_now()
            pts = [ax.c2p(math.log10(m), TRACE[m - 1]) for m in grid_n if m <= n]
            if len(pts) < 2:
                pts = [ax.c2p(0, TRACE[0])] * 2
            return VMobject(stroke_color=VIOLET, stroke_width=3).set_points_as_corners(pts)

        line = always_redraw(trace_line)
        counter = always_redraw(lambda: label(f"n = {n_now()}    ones = {round(TRACE[n_now() - 1] * n_now())}", 26, INK)
                                .move_to(LEFT * 3.4 + UP * 0.9))
        self.add(line, counter)
        self.play(k.animate.set_value(math.log10(400)), run_time=7, rate_func=linear)
        note = VGroup(eq(r"\text{expected } 400 \cdot \frac{1}{4} = 100,\ \text{observed } 95", size=30),
                      eq(r"\text{SD} = \sqrt{400 \cdot \frac{1}{4} \cdot \frac{3}{4}} \approx 8.66", size=30)
                      ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(RIGHT * 3.3 + UP * 2.3)
        self.play(Write(note), run_time=1.6)
        self.wait(1.4)
        self.play(k.animate.set_value(math.log10(4000)), run_time=3.5, rate_func=linear)
        end = eq(r"n = 4000:\ 990 \text{ ones, expected } 1000", size=30, color=VIOLET).move_to(note)
        self.play(Transform(note, end))
        self.wait(2.0)


# ---- scene 2 ----------------------------------------------------------------------------------
class BlochSphereBorn(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=CAM_PHI, theta=CAM_THETA)
        title = label("The Bloch sphere and the Born rule", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        form = eq(r"|\psi\rangle = \cos\frac{\theta}{2}|0\rangle + e^{i\varphi}\sin\frac{\theta}{2}|1\rangle", size=34)
        form.move_to(RIGHT * 3.4 + UP * 2.45)
        fixed(self, title, form)
        self.play(Write(title), run_time=1.0)
        bloch_frame(self)
        self.play(Write(form), run_time=1.4)

        th, ph = ValueTracker(0.0), ValueTracker(0.0)
        tip = lambda: bpt(th.get_value(), ph.get_value())  # noqa: E731
        vec = always_redraw(lambda: Line(CENTER, tip(), color=VIOLET, stroke_width=6))
        dot = always_redraw(lambda: Dot3D(tip(), radius=0.09, color=VIOLET))
        proj = always_redraw(lambda: DashedLine(tip(), CENTER + R * math.cos(th.get_value()) * OUT, color=AMBER, stroke_width=3))
        zdot = always_redraw(lambda: Dot3D(CENTER + R * math.cos(th.get_value()) * OUT, radius=0.08, color=AMBER))
        self.add(vec, dot, proj, zdot)

        def readout(tex_left, fn, y, color=INK, places=3):
            left = eq(tex_left, size=34, color=color)
            num = DecimalNumber(fn(), num_decimal_places=places, font_size=34, color=color)
            grp = VGroup(left, num).arrange(RIGHT, buff=0.15).move_to(RIGHT * 3.4 + UP * y)
            num.add_updater(lambda m: (m.set_value(fn()), self.renderer.camera.add_fixed_in_frame_mobjects(m)))
            return grp

        r_th = readout(r"\theta\ (\text{deg}) =", lambda: math.degrees(th.get_value()), 1.6, INK, 1)
        r_z = readout(r"z = \cos\theta =", lambda: math.cos(th.get_value()), 0.9, AMBER)
        r_p = readout(r"P(0) = \frac{1 + z}{2} =", lambda: (1 + math.cos(th.get_value())) / 2, 0.1, VIOLET)
        fixed(self, r_th, r_z, r_p)
        self.play(FadeIn(r_th), FadeIn(r_z), FadeIn(r_p))
        self.play(th.animate.set_value(120 * DEGREES), run_time=4)
        self.play(th.animate.set_value(THETA_EX), run_time=2)
        ex = eq(r"\theta = 60^\circ:\ P(0) = \frac{3}{4} = 0.750", size=32, color=VIOLET).move_to(RIGHT * 3.4 + DOWN * 0.9)
        fixed(self, ex)
        self.play(Write(ex))
        self.wait(0.8)

        # azimuth: a ring of states with the same P(0)
        ring = TracedPath(dot.get_center, stroke_color=CYAN, stroke_width=4)
        self.add(ring)
        say = label("turning φ keeps P(0) fixed", 28, CYAN).move_to(RIGHT * 3.4 + DOWN * 1.7)
        fixed(self, say)
        self.play(FadeIn(say))
        self.play(ph.animate.set_value(TAU), run_time=6, rate_func=linear)
        self.play(FadeOut(say), FadeOut(ex))
        ph.set_value(0)

        # global phase: both amplitude arrows turn, the Bloch point does not move
        gam = ValueTracker(0.0)
        dials = VGroup()
        for k, (amp, extra, name, col) in enumerate(((ALPHA, 0.0, r"\alpha", BLUE), (BETA, 0.0, r"\beta", AMBER))):
            c = RIGHT * (2.3 + 2.3 * k) + DOWN * 2.3
            circ = Circle(radius=0.8, color=LIGHT, stroke_width=2).move_to(c)
            arm = Line(c, c + 0.8 * amp * RIGHT, color=col, stroke_width=6)
            arm.add_updater(lambda m, c=c, amp=amp, extra=extra: m.put_start_and_end_on(
                c, c + 0.8 * amp * np.array([math.cos(gam.get_value() + extra), math.sin(gam.get_value() + extra), 0])))
            nm = eq(name, size=32, color=col).next_to(circ, LEFT, buff=0.12)
            dials.add(VGroup(circ, arm, nm))
        gl = eq(r"e^{i\gamma}|\psi\rangle", size=34, color=INK).move_to(RIGHT * 3.4 + DOWN * 1.05)
        fixed(self, dials, gl)
        self.play(FadeIn(dials), Write(gl))
        self.play(gam.animate.set_value(TAU), run_time=5, rate_func=smooth)
        same = label("same point, same probabilities", 26, MUTED).move_to(RIGHT * 3.4 + DOWN * 3.45)
        fixed(self, same)
        self.play(FadeIn(same))
        self.wait(2.0)


# ---- scene 3 ----------------------------------------------------------------------------------
class BasisReveal(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=CAM_PHI, theta=CAM_THETA)
        title = label("A relative phase hides from Z and shows in X", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        form = eq(r"|\psi_\varphi\rangle = \frac{1}{\sqrt{2}}\left(|0\rangle + e^{i\varphi}|1\rangle\right)", size=34)
        form.move_to(RIGHT * 3.4 + UP * 2.45)
        fixed(self, title, form)
        self.play(Write(title), run_time=1.0)
        bloch_frame(self)
        self.play(Write(form))

        ph = ValueTracker(0.0)
        tip = lambda: bpt(PI / 2, ph.get_value())  # noqa: E731
        vec = always_redraw(lambda: Line(CENTER, tip(), color=VIOLET, stroke_width=6))
        dot = always_redraw(lambda: Dot3D(tip(), radius=0.09, color=VIOLET))
        xproj = always_redraw(lambda: DashedLine(tip(), CENTER + R * math.cos(ph.get_value()) * RIGHT, color=BLUE, stroke_width=3))
        xdot = always_redraw(lambda: Dot3D(CENTER + R * math.cos(ph.get_value()) * RIGHT, radius=0.08, color=BLUE))
        self.add(vec, dot, xproj, xdot)

        # two bar charts pinned to the screen: Z basis (constant) and X basis (moves with phi)
        base_y, sc = -2.6, 2.2
        charts = VGroup()
        bars = []
        for j, (name, x0, col, outs) in enumerate((("Z basis", 1.6, MUTED, (r"0", r"1")), ("X basis", 4.6, BLUE, (r"+", r"-")))):
            ax = Line(RIGHT * (x0 - 1.1) + UP * base_y, RIGHT * (x0 + 1.1) + UP * base_y, color=MUTED, stroke_width=2)
            hd = label(name, 26, col).move_to(RIGHT * x0 + UP * (base_y + sc + 0.45))
            half = DashedLine(RIGHT * (x0 - 1.1) + UP * (base_y + sc / 2), RIGHT * (x0 + 1.1) + UP * (base_y + sc / 2),
                              color=LIGHT, stroke_width=2)
            ol = VGroup(*[eq(o, size=30, color=MUTED).move_to(RIGHT * (x0 + s * 0.5) + UP * (base_y - 0.3)) for o, s in zip(outs, (-1, 1))])
            charts.add(ax, hd, half, ol)
            for s in (-1, 1):
                b = Rectangle(width=0.7, height=sc / 2, fill_color=col, fill_opacity=0.75, stroke_width=0)
                b.move_to(RIGHT * (x0 + s * 0.5) + UP * (base_y + sc / 4))
                bars.append((b, j, s, x0))

        def height(j, s):
            if j == 0:
                return 0.5
            c = math.cos(ph.get_value())
            return (1 + c) / 2 if s == -1 else (1 - c) / 2

        for b, j, s, x0 in bars:
            b.add_updater(lambda m, j=j, s=s, x0=x0: m.stretch_to_fit_height(max(height(j, s) * sc, 0.001))
                          .move_to(RIGHT * (x0 + s * 0.5) + UP * (base_y + height(j, s) * sc / 2)))
        barg = VGroup(*[b for b, *_ in bars])
        rule = eq(r"P(+) = \frac{1 + \cos\varphi}{2}", size=34, color=BLUE).move_to(RIGHT * 3.4 + UP * 1.55)
        zrule = eq(r"P(0) = \frac{1}{2}\ \text{for every}\ \varphi", size=32, color=MUTED).move_to(RIGHT * 3.4 + UP * 0.8)
        fixed(self, charts, barg, rule, zrule)
        self.play(FadeIn(charts), FadeIn(barg))
        self.play(Write(zrule))
        self.play(Write(rule))
        self.play(ph.animate.set_value(TAU), run_time=9, rate_func=linear)
        last = label("same Z statistics, different states", 26, INK).move_to(RIGHT * 3.1 + DOWN * 3.45)
        fixed(self, last)
        self.play(FadeIn(last))
        self.play(ph.animate.set_value(PI), run_time=3)
        self.wait(1.5)
        _ = (Dot, RED, Transform)
