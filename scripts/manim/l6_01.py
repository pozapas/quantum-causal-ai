"""L6-01 Quantum common causes: four scenes.

BellDAGFactorization  the Bell DAG X -> A <- L -> B <- Y; the chain rule turns into the local
                      hidden-variable factorization as three graph assumptions are applied one at a time.
DeterministicCHSH     the 16 deterministic local strategies all give S = +2 or -2; convex mixtures fill
                      [-2, 2]; the quantum value 2 sqrt 2 and the algebraic maximum 4 lie outside.
QuantumCHSHSphere     ThreeDScene: Alice's directions z and x, Bob's at +phi and -phi in the x-z plane of the
                      Bloch sphere; S(phi) = 2 sqrt 2 sin(phi + pi/4) traced live, above 2 for 0 < phi < pi/2.
QuantumReichenbach    Allen et al.'s quantum conditional independence: incoherent copy and split source pass
                      (I(A:B|C) = 0), coherent copy fails (I(A:B|C) = 1), and the split source with |Phi+>
                      gives S = 2 sqrt 2.
CHSH convention: S = E(0,0) + E(0,1) + E(1,0) - E(1,1); observables cos(t) Z + sin(t) X on |Phi+>.
"""
import itertools
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (Dot3D, DOWN, LEFT, ORIGIN, PI, RIGHT, UL, UP, UR, Arrow, Arrow3D, Axes, Circle, Create, Cross, DashedLine,
                   DecimalNumber, Dot, FadeIn, FadeOut, Indicate, Line, NumberLine, Rectangle, RoundedRectangle, Scene,
                   Sphere, SurroundingRectangle, ThreeDAxes, ThreeDScene, TracedPath, TransformMatchingTex, ValueTracker,
                   VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label
from qcai import science as s

SQ2 = math.sqrt(2)
PHI = s.dm(s.bell_state("phi+"))
S_Q = s.chsh_value(PHI, 0, math.pi / 2, math.pi / 4, -math.pi / 4)
assert abs(S_Q - 2 * SQ2) < 1e-12
STRATS = list(itertools.product([1, -1], repeat=4))
S_DET = [a0 * (b0 + b1) + a1 * (b0 - b1) for a0, a1, b0, b1 in STRATS]
assert sorted(set(S_DET)) == [-2, 2] and S_DET.count(2) == 8


def s_of_phi(f):
    return 2 * math.cos(f) + 2 * math.sin(f)


for _f in np.linspace(0, math.pi / 2, 7):
    assert abs(s.chsh_value(PHI, 0, math.pi / 2, _f, -_f) - s_of_phi(_f)) < 1e-12
    assert abs(s_of_phi(_f) - 2 * SQ2 * math.sin(_f + math.pi / 4)) < 1e-12


# ---- Allen et al. checks (operators in the order input C first, then A, then B)
def choi_of(E, d):
    J = 0
    for i in range(d):
        for j in range(d):
            Eij = np.zeros((d, d), complex)
            Eij[i, j] = 1
            J = J + np.kron(Eij, E(Eij))
    return J


def ptr(J, dims, keep):
    n = len(dims)
    letters = "abcdefgh"
    L = "".join(letters[k] for k in range(n))
    R = "".join(letters[k].upper() if k in keep else letters[k] for k in range(n))
    out = "".join(letters[k] for k in keep) + "".join(letters[k].upper() for k in keep)
    d = int(np.prod([dims[k] for k in keep]))
    return np.einsum(L + R + "->" + out, J.reshape(dims + dims)).reshape(d, d)


def factor_gap(J, dc):
    """max |J - J_{A|C} J_{B|C}| with qubit outputs A, B."""
    JA = np.kron(ptr(J, [dc, 2, 2], [0, 1]), np.eye(2))
    JB = np.kron(ptr(J, [dc, 2, 2], [0, 2]), np.eye(2)).reshape(dc, 2, 2, dc, 2, 2).transpose(0, 2, 1, 3, 5, 4).reshape(J.shape)
    return float(np.abs(J - JA @ JB).max())


def cmi(J, dc):
    def S_(r):
        w = np.linalg.eigvalsh(r)
        w = w[w > 1e-12]
        return float(-(w * np.log2(w)).sum())
    r = J / dc
    return S_(ptr(r, [dc, 2, 2], [0, 1])) + S_(ptr(r, [dc, 2, 2], [0, 2])) - S_(r) - S_(ptr(r, [dc, 2, 2], [0]))


_iso = np.zeros((4, 2))
_iso[0, 0] = _iso[3, 1] = 1
J_COH = choi_of(lambda X: _iso @ X @ _iso.T, 2)
J_INC = choi_of(lambda X: X[0, 0] * np.diag([1, 0, 0, 0]) + X[1, 1] * np.diag([0, 0, 0, 1]), 2)
J_SPLIT = choi_of(lambda X: X, 4)
CMI = {"inc": cmi(J_INC, 2), "coh": cmi(J_COH, 2), "split": cmi(J_SPLIT, 4)}
assert factor_gap(J_INC, 2) < 1e-12 and factor_gap(J_SPLIT, 4) < 1e-12 and abs(factor_gap(J_COH, 2) - 1) < 1e-12
assert abs(CMI["inc"]) < 1e-9 and abs(CMI["coh"] - 1) < 1e-9 and abs(CMI["split"]) < 1e-9


def facts(L):
    """Strings shown on screen that also appear in the lesson text."""
    return ["p(a|x,\\lambda)", "2\\sqrt{2}", "S = \\pm 2", "2\\sqrt{2}\\,\\sin(\\varphi + \\pi/4)", "I(A:B|C) = 1",
            "\\rho_{AB|C} = \\rho_{A|C}\\,\\rho_{B|C}"]


def node(txt, pos, color, r=0.42, dashed=False, size=38):
    c = Circle(radius=r, color=color, stroke_width=4).set_fill(color, opacity=0.12)
    if dashed:
        c = DashedLine(ORIGIN, ORIGIN)  # placeholder replaced below
        c = Circle(radius=r, color=color, stroke_width=4).set_fill(color, opacity=0.12)
        c.set_stroke(opacity=0.9)
    t = eq(txt, size=size, color=color)
    return VGroup(c, t).move_to(pos)


def edge(a, b, color=INK):
    return Arrow(a.get_center(), b.get_center(), buff=0.48, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.18)


class BellDAGFactorization(Scene):
    def construct(self):
        title = label("Bell's scenario as a causal graph", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        X = node("X", LEFT * 6.1 + UP * 1.3, MUTED)
        A = node("A", LEFT * 5.05 + DOWN * 0.3, BLUE)
        Lm = node(r"\Lambda", LEFT * 4.0 + UP * 1.3, AMBER)
        B = node("B", LEFT * 2.95 + DOWN * 0.3, BLUE)
        Y = node("Y", LEFT * 1.9 + UP * 1.3, MUTED)
        es = VGroup(edge(X, A), edge(Lm, A, AMBER), edge(Lm, B, AMBER), edge(Y, B))
        self.play(*[FadeIn(n, scale=0.7) for n in (X, A, Lm, B, Y)], run_time=1.0)
        self.play(Create(es), run_time=1.2)
        key = VGroup(label("X, Y: settings", 24, MUTED), label("A, B: outcomes", 24, BLUE),
                     label("Lambda: hidden common cause", 24, AMBER)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        key.move_to(LEFT * 4.0 + DOWN * 2.2)
        self.play(FadeIn(key))

        parts0 = [r"p(a,b|x,y) =", r"\sum_\lambda", r"p(\lambda|x,y)", r"\,p(a|x,y,\lambda)", r"\,p(b|a,x,y,\lambda)"]
        f0 = eq(*parts0, size=32).move_to(RIGHT * 2.75 + UP * 1.6)
        chain = label("chain rule: always true", 24, MUTED).next_to(f0, DOWN, buff=0.2)
        self.play(Write(f0), FadeIn(chain))
        self.wait(0.6)

        steps = [
            ([r"p(a,b|x,y) =", r"\sum_\lambda", r"p(\lambda)", r"\,p(a|x,y,\lambda)", r"\,p(b|a,x,y,\lambda)"],
             "no arrow into Lambda from X or Y", [Lm], "measurement independence"),
            ([r"p(a,b|x,y) =", r"\sum_\lambda", r"p(\lambda)", r"\,p(a|x,\lambda)", r"\,p(b|a,y,\lambda)"],
             "no arrow X to B or Y to A", [A, B], "locality"),
            ([r"p(a,b|x,y) =", r"\sum_\lambda", r"p(\lambda)", r"\,p(a|x,\lambda)", r"\,p(b|y,\lambda)"],
             "Lambda screens off A from B", [Lm], "complete common cause"),
        ]
        cur = f0
        tags = VGroup()
        for k, (parts, why, hl, name) in enumerate(steps):
            nxt = eq(*parts, size=32).move_to(cur)
            tag = VGroup(label(f"{k + 1}. {name}", 26, VIOLET, "BOLD"), label(why, 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
            tag.move_to(RIGHT * 3.1 + DOWN * (0.15 + 0.95 * k)).align_to(RIGHT * 0.2, LEFT)
            boxes = VGroup(*[SurroundingRectangle(h, color=VIOLET, buff=0.08) for h in hl])
            if k == 0:
                self.play(FadeOut(chain))
            self.play(Create(boxes), FadeIn(tag), run_time=0.8)
            self.play(TransformMatchingTex(cur, nxt), run_time=1.4)
            self.play(FadeOut(boxes), run_time=0.4)
            tags.add(tag)
            cur = nxt
            self.wait(0.4)
        self.play(cur.animate.set_color(AMBER))
        res = eq(r"\Rightarrow\ |S| \le 2 \text{ for every such model}", size=34, color=RED).next_to(tags, DOWN, buff=0.3).align_to(tags, LEFT)
        self.play(Write(res))
        self.wait(2.0)


class DeterministicCHSH(Scene):
    def construct(self):
        title = label("Why a classical common cause cannot exceed 2", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        sdef = eq(r"S = E_{00} + E_{01} + E_{10} - E_{11}", size=36).move_to(UP * 2.35)
        self.play(Write(sdef))
        det = eq(r"S = a_0(b_0 + b_1) + a_1(b_0 - b_1)", size=36, color=VIOLET).move_to(UP * 1.55)
        self.play(Write(det))
        why = label("one bracket is 0, the other is +2 or -2", 24, MUTED).next_to(det, DOWN, buff=0.15)
        self.play(FadeIn(why))

        cells = VGroup()
        for k, (st, val) in enumerate(zip(STRATS, S_DET)):
            col = CYAN if val > 0 else AMBER
            box = RoundedRectangle(width=1.5, height=0.62, corner_radius=0.08, color=col).set_fill(col, opacity=0.12)
            txt = label("".join("+" if v > 0 else "-" for v in st), 24, INK)
            cells.add(VGroup(box, txt))
        cells.arrange_in_grid(rows=2, cols=8, buff=0.12).move_to(DOWN * 0.75)
        hdr = label("a0 a1 b0 b1 for the 16 deterministic strategies", 24, MUTED).next_to(cells, UP, buff=0.12)
        self.play(FadeIn(hdr), *[FadeIn(c, shift=DOWN * 0.1) for c in cells], run_time=1.6)
        vals = VGroup(*[eq(rf"{v:+d}", size=30, color=CYAN if v > 0 else AMBER).move_to(c) for c, v in zip(cells, S_DET)])
        self.play(*[c[1].animate.set_opacity(0) for c in cells], FadeIn(vals), run_time=1.2)
        allpm = eq(r"S = \pm 2", size=40, color=VIOLET).next_to(cells, DOWN, buff=0.25)
        self.play(Write(allpm))
        self.wait(0.8)

        self.play(FadeOut(VGroup(cells, vals, hdr, why)), allpm.animate.move_to(UP * 0.7))
        nl = NumberLine(x_range=[-4, 4, 1], length=11, color=MUTED, include_numbers=True, font_size=28,
                        decimal_number_config={"color": INK, "num_decimal_places": 0}).move_to(DOWN * 1.2)
        self.play(Create(nl))
        dots = VGroup()
        for side in (-2, 2):
            for k in range(8):
                dots.add(Dot(nl.n2p(side) + UP * (0.22 + 0.13 * k), radius=0.06, color=CYAN if side > 0 else AMBER))
        self.play(FadeIn(dots, lag_ratio=0.05), run_time=1.2)
        band = Rectangle(width=abs(nl.n2p(2)[0] - nl.n2p(-2)[0]), height=0.35).set_fill(VIOLET, 0.25).set_stroke(width=0)
        band.move_to((nl.n2p(-2) + nl.n2p(2)) / 2)
        mix = label("mixtures over lambda: every classical model lies in [-2, 2]", 26, VIOLET).move_to(DOWN * 3.05)
        self.play(FadeIn(band), FadeIn(mix))
        self.wait(0.6)
        q = Dot(nl.n2p(2 * SQ2), radius=0.1, color=RED)
        ql = eq(r"2\sqrt{2} \approx 2.83", size=34, color=RED).next_to(q, DOWN, buff=0.55)
        qn = label("shared |Phi+>", 24, RED).next_to(ql, DOWN, buff=0.08)
        self.play(FadeIn(q, scale=2), Write(ql), FadeIn(qn))
        a = Dot(nl.n2p(4), radius=0.08, color=MUTED)
        al = label("algebraic maximum 4", 24, MUTED).next_to(a, UP, buff=0.3).shift(LEFT * 0.4)
        self.play(FadeIn(a), FadeIn(al))
        self.wait(2.0)


class QuantumCHSHSphere(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=72 * DEG, theta=-90 * DEG, zoom=1.0)
        R = 1.9
        shift = np.array([-3.0, 0, 0])  # x shift in world coordinates (camera looks along y with theta=-90)
        sphere = Sphere(radius=R, resolution=(16, 16)).set_fill(BLUE, opacity=0.05).set_stroke(GRID, width=0.6).shift(shift)
        axes = ThreeDAxes(x_range=[-2.4, 2.4, 1], y_range=[-2.4, 2.4, 1], z_range=[-2.4, 2.4, 1], x_length=4.8, y_length=4.8,
                          z_length=4.8, axis_config={"color": MUTED, "include_ticks": False, "include_tip": False}).shift(shift)
        title = label("Measurement directions on a shared |Phi+>", 30, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(sphere), Create(axes), Write(title), run_time=1.4)
        zl = eq("z", size=32, color=MUTED).move_to(shift + np.array([0, 0, 2.65]))
        xl = eq("x", size=32, color=MUTED).move_to(shift + np.array([2.65, 0, 0]))
        self.add_fixed_orientation_mobjects(zl, xl)
        self.add(zl, xl)

        def d(t):  # direction cos(t) z + sin(t) x
            return shift + R * np.array([math.sin(t), 0, math.cos(t)])

        a0 = Arrow3D(shift, d(0), color=VIOLET)
        a1 = Arrow3D(shift, d(PI / 2), color=VIOLET)
        al = VGroup(eq("A_0 = Z", size=30, color=VIOLET), eq("A_1 = X", size=30, color=VIOLET)).arrange(DOWN, aligned_edge=LEFT)
        al.to_corner(UL, buff=0.35).shift(DOWN * 0.7)
        self.add_fixed_in_frame_mobjects(al)
        self.play(Create(a0), Create(a1), Write(al))
        f = ValueTracker(0.02)
        b0 = Line(shift, d(f.get_value()), color=AMBER, stroke_width=7)
        b1 = Line(shift, d(-f.get_value()), color=AMBER, stroke_width=7)
        b0.add_updater(lambda m: m.put_start_and_end_on(shift, d(f.get_value())))
        b1.add_updater(lambda m: m.put_start_and_end_on(shift, d(-f.get_value())))
        t0 = Dot3D(d(f.get_value()), radius=0.09, color=AMBER, resolution=(8, 8))
        t1 = Dot3D(d(-f.get_value()), radius=0.09, color=AMBER, resolution=(8, 8))
        t0.add_updater(lambda m: m.move_to(d(f.get_value())))
        t1.add_updater(lambda m: m.move_to(d(-f.get_value())))
        bl = eq(r"B_{0,1} = \cos\varphi\, Z \pm \sin\varphi\, X", size=30, color=AMBER).next_to(al, DOWN, buff=0.25).align_to(al, LEFT)
        self.add_fixed_in_frame_mobjects(bl)
        self.play(FadeIn(b0), FadeIn(b1), FadeIn(t0), FadeIn(t1), Write(bl))

        ax = Axes(x_range=[0, PI / 2, PI / 4], y_range=[1.6, 3.0, 0.5], x_length=4.6, y_length=3.0,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 3.6 + DOWN * 0.3)
        two = DashedLine(ax.c2p(0, 2), ax.c2p(PI / 2, 2), color=MUTED)
        tsi = DashedLine(ax.c2p(0, 2 * SQ2), ax.c2p(PI / 2, 2 * SQ2), color=RED)
        twol = label("classical bound 2", 24, MUTED).next_to(two, DOWN, buff=0.08)
        tsil = eq(r"2\sqrt{2}", size=30, color=RED).next_to(tsi, RIGHT, buff=0.1)
        yl = eq(r"S(\varphi) = 2\sqrt{2}\,\sin(\varphi + \pi/4)", size=32).next_to(ax, UP, buff=0.3)
        xlab = eq(r"\varphi", size=30).next_to(ax.x_axis, RIGHT, buff=0.3)
        ticks = VGroup(eq("0", size=26).next_to(ax.c2p(0, 1.6), DOWN, buff=0.1), eq(r"\pi/4", size=26).next_to(ax.c2p(PI / 4, 1.6), DOWN, buff=0.1),
                       eq(r"\pi/2", size=26).next_to(ax.c2p(PI / 2, 1.6), DOWN, buff=0.1))
        grp = VGroup(ax, two, tsi, twol, tsil, yl, xlab, ticks)
        self.add_fixed_in_frame_mobjects(grp)
        self.play(FadeIn(grp))
        dot = Dot(ax.c2p(0.02, s_of_phi(0.02)), radius=0.07, color=RED)
        self.add_fixed_in_frame_mobjects(dot)
        dot.add_updater(lambda m: m.move_to(ax.c2p(f.get_value(), s_of_phi(f.get_value()))))
        trace = TracedPath(dot.get_center, stroke_color=RED, stroke_width=4)
        self.add_fixed_in_frame_mobjects(trace)
        self.add(trace, dot)
        self.play(f.animate.set_value(PI / 4), run_time=4, rate_func=linear)
        best = label("phi = pi/4: S = 2.83", 26, RED).next_to(ax, DOWN, buff=0.45)
        self.add_fixed_in_frame_mobjects(best)
        self.play(FadeIn(best))
        self.wait(0.6)
        self.play(f.animate.set_value(PI / 2 - 0.02), run_time=4, rate_func=linear)
        note = label("S > 2 for every 0 < phi < pi/2", 24, MUTED).next_to(best, DOWN, buff=0.15)
        self.add_fixed_in_frame_mobjects(note)
        self.play(FadeIn(note))
        self.wait(1.5)


DEG = PI / 180


class QuantumReichenbach(Scene):
    def construct(self):
        title = label("Allen et al.: a quantum complete common cause", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        crit = eq(r"\rho_{AB|C} = \rho_{A|C}\,\rho_{B|C}", size=40, color=VIOLET).move_to(UP * 2.3)
        sub = label("quantum conditional independence of A and B given C", 24, MUTED).next_to(crit, DOWN, buff=0.12)
        self.play(Write(crit), FadeIn(sub))

        def panel(x, name, picture, verdict, ok, cmi_txt):
            hdr = label(name, 26, INK, "BOLD").move_to([x, 1.15, 0])
            pic = picture.move_to([x, -0.05, 0])
            v = eq(cmi_txt, size=32, color=CYAN if ok else RED).move_to([x, -1.45, 0])
            w = VGroup(*[label(t, 24, CYAN if ok else RED) for t in verdict]).arrange(DOWN, buff=0.08).move_to([x, -2.25, 0])
            return VGroup(hdr, pic, v, w)

        def two_out(mid, color):
            c = node("C", LEFT * 0.0, MUTED, r=0.34, size=30)
            box = RoundedRectangle(width=0.8, height=0.6, corner_radius=0.1, color=color).set_fill(color, 0.15).move_to(RIGHT * 1.15)
            a = node("A", RIGHT * 2.3 + UP * 0.55, BLUE, r=0.3, size=28)
            b = node("B", RIGHT * 2.3 + DOWN * 0.55, BLUE, r=0.3, size=28)
            bt = label(mid, 24, color).next_to(VGroup(c, box, a, b), DOWN, buff=0.12)
            return VGroup(c, box, bt, a, b, Line(c.get_right(), box.get_left(), color=INK),
                          Arrow(box.get_right(), a.get_left(), buff=0.05, color=INK, stroke_width=3),
                          Arrow(box.get_right(), b.get_left(), buff=0.05, color=INK, stroke_width=3))

        p1 = panel(-4.5, "incoherent copy", two_out("measure, copy", AMBER), ["passes", "the classical case"], True, r"I(A:B|C) = 0")
        p2 = panel(0.0, "coherent copy", two_out("|i> to |ii>", RED), ["fails", "GHZ-type Choi state"], False, r"I(A:B|C) = 1")
        p3 = panel(4.5, "split source", two_out("CL to A, CR to B", CYAN), ["passes", "a single block"], True, r"I(A:B|C) = 0")
        for p in (p1, p2, p3):
            self.play(FadeIn(p[0]), FadeIn(p[1]), run_time=0.8)
            self.play(Write(p[2]), FadeIn(p[3]), run_time=0.9)
            self.wait(0.5)
        self.wait(0.6)
        self.play(FadeOut(VGroup(p1, p2)), FadeOut(sub), p3.animate.move_to(LEFT * 3.6 + DOWN * 0.4))
        bell = VGroup(eq(r"\text{source state } |\Phi^+\rangle \text{ on } C_L C_R", size=32),
                      eq(r"p(a,b|x,y) = \operatorname{Tr}[(E_{a|x} \otimes F_{b|y})\,\rho_C]", size=32),
                      eq(r"S = 2\sqrt{2} > 2", size=38, color=RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        bell.move_to(RIGHT * 2.9 + DOWN * 0.4)
        for m in bell:
            self.play(Write(m), run_time=1.0)
        fin = label("quantum conditionally independent given C, yet Bell-violating", 26, VIOLET).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(fin))
        self.wait(2.0)
        _ = (Cross, DecimalNumber, Indicate, UR, linear, Rectangle)
