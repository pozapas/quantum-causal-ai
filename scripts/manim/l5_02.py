"""L5-02 Gates and circuit order: three scenes.

GatesAsRotations  ThreeDScene: |0> -H-> |+> -S-> |+i> -S-> |-> -H-> |1>.  Each gate is drawn as its true
                  rotation of the Bloch sphere (H: half turn about (x+z)/sqrt 2; S: quarter turn about z),
                  so the circuit H S S H = H Z H = X carries |0> to |1>.
CircuitOrder      a circuit drawn left to right, the same product written right to left, and the matrix
                  multiplication HZH = X transformed term by term; then SH|0> = |+i> but HS|0> = |+>.
OrderMatters      ThreeDScene: two Bloch spheres run "H, then S" and "S, then H" side by side and end at
                  different points (y axis versus x axis).
Endpoints are checked against science.bloch(science.dm(U @ psi)); facts() ties on-screen strings to the text.
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, OUT, RIGHT, TAU, UP, Arrow, Create, DashedLine, Dot3D, FadeIn, FadeOut,
                   Line, Rectangle, Scene, Sphere, SurroundingRectangle, ThreeDScene, TracedPath, TransformMatchingTex,
                   ValueTracker, VGroup, VMobject, Write, always_redraw, smooth)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

from qcai import science  # noqa: E402

# ---- gates, their Bloch rotations, and the checks ----------------------------------------------
S_GATE = np.diag([1, 1j])
T_GATE = np.diag([1, np.exp(1j * math.pi / 4)])
GATES = {"H": science.H, "S": S_GATE, "T": T_GATE, "X": science.X, "Z": science.Z}
N_H = np.array([1, 0, 1]) / math.sqrt(2)
ROT = {"H": (N_H, math.pi), "S": (np.array([0, 0, 1.0]), math.pi / 2), "T": (np.array([0, 0, 1.0]), math.pi / 4),
       "X": (np.array([1.0, 0, 0]), math.pi), "Z": (np.array([0, 0, 1.0]), math.pi)}


def rot_op(n, a):
    """exp(-i a/2 n.sigma) = cos(a/2) I - i sin(a/2) n.sigma."""
    return math.cos(a / 2) * science.I2 - 1j * math.sin(a / 2) * (n[0] * science.X + n[1] * science.Y + n[2] * science.Z)


# each gate is a global phase times its rotation operator
for g, ph in (("H", 1j), ("S", np.exp(1j * math.pi / 4)), ("T", np.exp(1j * math.pi / 8)), ("X", 1j), ("Z", 1j)):
    assert np.allclose(GATES[g], ph * rot_op(*ROT[g])), g
assert np.allclose(science.H @ science.Z @ science.H, science.X)
assert np.allclose(S_GATE @ S_GATE, science.Z)


def rotate(r, n, a):
    r, n = np.asarray(r, float), np.asarray(n, float)
    return r * math.cos(a) + np.cross(n, r) * math.sin(a) + n * np.dot(n, r) * (1 - math.cos(a))


def run(gates):
    """Bloch vectors after each gate, checked against the state vector."""
    r, psi, out = np.array([0, 0, 1.0]), science.KET0.copy(), []
    for g in gates:
        r = rotate(r, *ROT[g])
        psi = GATES[g] @ psi
        assert np.allclose(r, science.bloch(science.dm(psi)), atol=1e-9)
        out.append(r)
    return out


PATH_HSSH = run(["H", "S", "S", "H"])
assert np.allclose(PATH_HSSH[-1], [0, 0, -1])            # |1>
assert np.allclose(run(["H", "S"])[-1], [0, 1, 0])        # S H |0> = |+i>
assert np.allclose(run(["S", "H"])[-1], [1, 0, 0])        # H S |0> = |+>


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["HZH = X", "S H|0\\rangle = |{+i}\\rangle", "H S|0\\rangle = |+\\rangle", "H = i\\,R_{\\hat n}(\\pi)"]


# ---- Bloch helpers ------------------------------------------------------------------------------
CAM_PHI, CAM_THETA = 72 * DEGREES, 20 * DEGREES
SCREEN_RIGHT = np.array([-math.sin(CAM_THETA), math.cos(CAM_THETA), 0.0])
LIGHT = "#cbd5e1"


def bloch_frame(scene, center, R, label_size=32, xy=True):
    sph = Sphere(center=center, radius=R, resolution=(18, 18))
    sph.set_fill(VIOLET, opacity=0.05).set_stroke(GRID, width=0.4, opacity=0.5)
    t = np.linspace(0, TAU, 97)
    eqt = VMobject(stroke_color=LIGHT, stroke_width=2).set_points_smoothly([center + R * np.array([math.cos(a), math.sin(a), 0]) for a in t])
    mer = VMobject(stroke_color=LIGHT, stroke_width=2).set_points_smoothly([center + R * np.array([math.sin(a), 0, math.cos(a)]) for a in t])
    axes = VGroup(*[Line(center - 1.2 * R * d, center + 1.2 * R * d, color=MUTED, stroke_width=2) for d in (RIGHT, UP, OUT)])
    scene.play(Create(sph), Create(eqt), Create(mer), Create(axes), run_time=1.4)
    labs = [(eq(r"|0\rangle", size=label_size), center + 1.38 * R * OUT), (eq(r"|1\rangle", size=label_size), center - 1.38 * R * OUT)]
    if xy:
        labs += [(eq("x", size=label_size - 2, color=MUTED), center + 1.32 * R * RIGHT), (eq("y", size=label_size - 2, color=MUTED), center + 1.3 * R * UP)]
    for m, p in labs:
        m.move_to(p)
        scene.add_fixed_orientation_mobjects(m)


def fixed(scene, *mobs):
    scene.add_fixed_in_frame_mobjects(*mobs)
    scene.remove(*mobs)


class Rotor:
    """A Bloch vector that can be turned about an axis by a ValueTracker, leaving a colored trail."""

    def __init__(self, scene, center, R, color=VIOLET):
        self.scene, self.c, self.R = scene, center, R
        self.r0 = np.array([0, 0, 1.0])
        self.n, self.a = np.array([0, 0, 1.0]), 0.0
        self.t = ValueTracker(0.0)
        self.line = always_redraw(lambda: Line(self.c, self.tip(), color=color, stroke_width=6))
        self.dot = always_redraw(lambda: Dot3D(self.tip(), radius=0.08, color=color))
        scene.add(self.line, self.dot)

    def vec(self):
        return rotate(self.r0, self.n, self.a * self.t.get_value())

    def tip(self):
        return self.c + self.R * self.vec()

    def turn(self, gate, color, run_time=2.5, axis_line=True):
        """Set up gate's rotation and return (animation, trail, axis line); call done() after playing."""
        self.n, self.a = ROT[gate]
        self.t.set_value(0)
        trail = TracedPath(self.dot.get_center, stroke_color=color, stroke_width=5)
        self.scene.add(trail)
        ax = None
        if axis_line:
            ax = DashedLine(self.c - 1.25 * self.R * self.n, self.c + 1.25 * self.R * self.n, color=color, stroke_width=3)
        return self.t.animate(run_time=run_time, rate_func=smooth).set_value(1), trail, ax

    def done(self, trail):
        trail.clear_updaters()
        self.r0 = self.vec()
        self.n, self.a = np.array([0, 0, 1.0]), 0.0
        self.t.set_value(0)


# ---- scene 1 ------------------------------------------------------------------------------------
class GatesAsRotations(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=CAM_PHI, theta=CAM_THETA)
        center, R = -3.3 * SCREEN_RIGHT, 2.0
        title = label("Single-qubit gates rotate the Bloch sphere", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        fixed(self, title)
        self.play(Write(title), run_time=1.0)
        bloch_frame(self, center, R)
        rotor = Rotor(self, center, R)

        # circuit row pinned at the top right; boxes appear as gates are applied
        wire = Line(RIGHT * 0.9 + UP * 2.4, RIGHT * 5.95 + UP * 2.4, color=MUTED, stroke_width=3)
        ket = eq(r"|0\rangle", size=34).next_to(wire, LEFT, buff=0.1)
        fixed(self, wire, ket)
        self.play(Create(wire), Write(ket))
        steps = [("H", VIOLET, r"H = i\,R_{\hat n}(\pi),\ \hat n = \frac{x + z}{\sqrt{2}}", r"|+\rangle"),
                 ("S", CYAN, r"S = e^{i\pi/4} R_z(\pi/2)", r"|{+i}\rangle"),
                 ("S", AMBER, r"S = e^{i\pi/4} R_z(\pi/2)", r"|-\rangle"),
                 ("H", BLUE, r"H = i\,R_{\hat n}(\pi)", r"|1\rangle")]
        info = None
        for k, (g, col, desc, reached) in enumerate(steps):
            box = VGroup(Rectangle(width=0.8, height=0.7, fill_color="#ffffff", fill_opacity=1, stroke_color=col, stroke_width=4),
                         eq(g, size=36, color=col)).move_to(RIGHT * (1.9 + 1.25 * k) + UP * 2.4)
            new_info = VGroup(eq(desc, size=32, color=col),
                              eq(rf"\text{{after gate {k + 1}: }} {reached}", size=32, color=INK)).arrange(DOWN, buff=0.25)
            new_info.move_to(RIGHT * 3.6 + UP * 1.05)
            fixed(self, box, new_info[0])
            anim, trail, ax = rotor.turn(g, col)
            if info is not None:
                self.play(FadeOut(info), run_time=0.5)
            self.play(FadeIn(box), Write(new_info[0]), Create(ax), run_time=1.0)
            self.play(anim)
            rotor.done(trail)
            assert np.allclose(rotor.r0, PATH_HSSH[k], atol=1e-9)
            fixed(self, new_info[1])
            self.play(Write(new_info[1]), FadeOut(ax), run_time=0.8)
            info = new_info
            self.wait(0.5)
        result = VGroup(eq(r"H\,S\,S\,H = H Z H = X", size=36, color=INK),
                        eq(r"X|0\rangle = |1\rangle", size=36, color=BLUE)).arrange(DOWN, buff=0.3).move_to(RIGHT * 3.6 + DOWN * 1.3)
        note = label("first gate in time = rightmost factor", 24, MUTED).move_to(RIGHT * 3.6 + DOWN * 2.8)
        fixed(self, result, note)
        self.play(Write(result), run_time=1.6)
        self.play(FadeIn(note))
        self.wait(2.0)


# ---- scene 2 ------------------------------------------------------------------------------------
M_H = r"\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}"
M_Z = r"\begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}"
M_ZH = r"\begin{pmatrix} 1 & 1 \\ -1 & 1 \end{pmatrix}"
M_2X = r"\begin{pmatrix} 0 & 2 \\ 2 & 0 \end{pmatrix}"
M_X = r"\begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}"
_h = np.array([[1, 1], [1, -1]])
assert (np.array([[1, 0], [0, -1]]) @ _h == np.array([[1, 1], [-1, 1]])).all()
assert (_h @ np.array([[1, 1], [-1, 1]]) == np.array([[0, 2], [2, 0]])).all()


class CircuitOrder(Scene):
    def construct(self):
        title = label("Circuits read left to right; matrices act right to left", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        y = 2.25
        wire = Line(LEFT * 5.2 + UP * y, LEFT * 0.4 + UP * y, color=MUTED, stroke_width=3)
        ket = eq(r"|\psi\rangle", size=36).next_to(wire, LEFT, buff=0.1)
        cols = (VIOLET, CYAN, AMBER)
        boxes = VGroup(*[VGroup(Rectangle(width=0.8, height=0.7, fill_color="#ffffff", fill_opacity=1, stroke_color=c, stroke_width=4),
                                eq(g, size=36, color=c)).move_to(RIGHT * x + UP * y)
                         for g, c, x in zip("HZH", cols, (-4.0, -2.8, -1.6))])
        time = Arrow(LEFT * 4.6 + UP * (y - 0.65), LEFT * 1.0 + UP * (y - 0.65), color=MUTED, buff=0, stroke_width=3)
        tl = label("time", 24, MUTED).next_to(time, DOWN, buff=0.08)
        self.play(Create(wire), Write(ket), run_time=0.8)
        for b in boxes:
            self.play(FadeIn(b), run_time=0.45)
        self.play(Create(time), FadeIn(tl))

        prod = eq("H", "Z", "H", r"|\psi\rangle", size=44).move_to(RIGHT * 3.4 + UP * y)
        for part, c in zip(prod[:3][::-1], cols):        # the first gate (violet) is the rightmost factor
            part.set_color(c)
        back = Arrow(RIGHT * 4.3 + UP * (y - 0.65), RIGHT * 2.5 + UP * (y - 0.65), color=MUTED, buff=0, stroke_width=3)
        bl = label("acts first", 24, MUTED).next_to(back, DOWN, buff=0.08).align_to(back, RIGHT)
        self.play(Write(prod))
        self.play(Create(back), FadeIn(bl))
        self.wait(0.8)

        lines = [eq("HZH", "=", r"\frac{1}{2}", M_H, M_Z, M_H, size=36),
                 eq("HZH", "=", r"\frac{1}{2}", M_H, M_ZH, size=36),
                 eq("HZH", "=", r"\frac{1}{2}", M_2X, size=36),
                 eq("HZH", "=", M_X, "=", "X", size=36)]
        for m in lines:
            m.move_to(UP * 0.15)
        self.play(Write(lines[0]), run_time=1.6)
        self.wait(0.6)
        for a, b in zip(lines, lines[1:]):
            self.play(TransformMatchingTex(a, b), run_time=1.5)
            self.wait(0.6)
        box = SurroundingRectangle(lines[-1], color=VIOLET, buff=0.15)
        self.play(Create(box))
        self.wait(0.6)

        a1 = eq(r"S H|0\rangle = S|+\rangle = |{+i}\rangle", size=36, color=VIOLET)
        a2 = eq(r"H S|0\rangle = H|0\rangle = |+\rangle", size=36, color=CYAN)
        pair = VGroup(a1, a2).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(LEFT * 2.6 + DOWN * 2.2)
        verdict = VGroup(eq(r"SH \neq HS", size=40, color=RED),
                         label("order changes the state", 26, MUTED)).arrange(DOWN, buff=0.15).move_to(RIGHT * 3.6 + DOWN * 2.2)
        self.play(Write(a1))
        self.play(Write(a2))
        self.play(Write(verdict))
        self.wait(2.0)


# ---- scene 3 ------------------------------------------------------------------------------------
class OrderMatters(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=CAM_PHI, theta=CAM_THETA)
        R = 1.45
        cl, cr = -3.4 * SCREEN_RIGHT - 0.45 * OUT, 3.4 * SCREEN_RIGHT - 0.45 * OUT
        title = label("Same two gates, opposite order, different state", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        hl = label("H, then S", 30, VIOLET).move_to(LEFT * 3.5 + UP * 2.75)
        hr = label("S, then H", 30, CYAN).move_to(RIGHT * 3.5 + UP * 2.75)
        fixed(self, title, hl, hr)
        self.play(Write(title), run_time=1.0)
        bloch_frame(self, cl, R, label_size=28)
        bloch_frame(self, cr, R, label_size=28)
        self.play(FadeIn(hl), FadeIn(hr))
        left, right = Rotor(self, cl, R, VIOLET), Rotor(self, cr, R, CYAN)

        # step 1: H on the left, S on the right (S only adds a phase to |0>, so the right arrow stays)
        s1l = label("step 1: H", 24, MUTED).move_to(LEFT * 3.5 + DOWN * 2.85)
        s1r = label("step 1: S leaves |0⟩ in place", 24, MUTED).move_to(RIGHT * 3.5 + DOWN * 2.85)
        fixed(self, s1l, s1r)
        a1, t1, x1 = left.turn("H", VIOLET)
        a2, t2, x2 = right.turn("S", CYAN)
        self.play(FadeIn(s1l), FadeIn(s1r), Create(x1), Create(x2), run_time=0.8)
        self.play(a1, a2)
        left.done(t1)
        right.done(t2)
        self.play(FadeOut(x1), FadeOut(x2), FadeOut(s1l), FadeOut(s1r), run_time=0.6)

        # step 2: S on the left, H on the right
        s2l = label("step 2: S", 24, MUTED).move_to(LEFT * 3.5 + DOWN * 2.85)
        s2r = label("step 2: H", 24, MUTED).move_to(RIGHT * 3.5 + DOWN * 2.85)
        fixed(self, s2l, s2r)
        a1, t1, x1 = left.turn("S", AMBER)
        a2, t2, x2 = right.turn("H", AMBER)
        self.play(FadeIn(s2l), FadeIn(s2r), Create(x1), Create(x2), run_time=0.8)
        self.play(a1, a2)
        left.done(t1)
        right.done(t2)
        assert np.allclose(left.r0, [0, 1, 0], atol=1e-9) and np.allclose(right.r0, [1, 0, 0], atol=1e-9)
        self.play(FadeOut(x1), FadeOut(x2), FadeOut(s2l), FadeOut(s2r), run_time=0.6)

        rl = eq(r"S H|0\rangle = |{+i}\rangle", size=34, color=VIOLET).move_to(LEFT * 3.5 + DOWN * 2.6)
        rr = eq(r"H S|0\rangle = |+\rangle", size=34, color=CYAN).move_to(RIGHT * 3.5 + DOWN * 2.6)
        fixed(self, rl, rr)
        self.play(Write(rl), Write(rr))
        diff = eq(r"P(+) = 0.5 \quad\text{versus}\quad P(+) = 1", size=32, color=INK).move_to(DOWN * 3.35)
        fixed(self, diff)
        self.play(Write(diff))
        self.wait(2.0)
        _ = (RED, LEFT)
