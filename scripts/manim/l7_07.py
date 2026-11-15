"""L7-07 Classical shadows and observable structure: five scenes.

SnapshotCloud     ThreeDScene: single-qubit snapshots 3U^dag|b><b|U - I have Bloch vectors 3b e_P, six points at
                  radius 3 outside the Bloch ball; their running average walks to the true Bloch vector r.
InverseChannel    the measure-and-forget channel M shrinks the Bloch disk to radius 1/3; the derivation
                  M(rho) = rho/3 + Tr(rho) I/3 term by term, the inverse 3X - Tr(X) I, and the snapshot.
BasisMatching     12 shots on 4 qubits with random bases; a weight-k Pauli string only "sees" shots whose k bases
                  all match (probability 3^-k), and then contributes +-3^k: E[o^2] = 3^k.
ErrorVsSnapshots  log-log RMSE against snapshots for weight 1, 2, 3 Paulis on 3 qubits (400 seeded repetitions),
                  slope -1/2, and the vertical gap sqrt(26.25/2.75) = 3.09.
MedianOfMeans     group means and their median; why the median fails only if half the groups fail, and the
                  binomial tail against the Hoeffding bound e^{-K/8} as K grows.
All numbers are computed here; facts() lists strings that also appear in the lesson text.
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, OUT, RIGHT, TAU, UP, Arrow, Axes, Circle, Create, DashedLine, DecimalNumber,
                   Dot, Dot3D, FadeIn, FadeOut, Indicate, Line, Rectangle, Scene, Sphere, SurroundingRectangle,
                   ThreeDScene, Transform, TransformMatchingTex, ValueTracker, VGroup, VMobject, Write, always_redraw,
                   linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ---- numbers the lesson states ---------------------------------------------------------------------------
R_VEC = np.array([0.4, 0.3, 0.6])                     # Bloch vector of the single-qubit example state
E_AXES = np.eye(3)
# exact mean of the snapshot Bloch vector 3 b e_P over P uniform and b with P(b) = (1 + b r_P)/2
MEAN = sum((1 / 3) * ((1 + b * R_VEC[p]) / 2) * 3 * b * E_AXES[p] for p in range(3) for b in (1, -1))
assert np.allclose(MEAN, R_VEC)
# snapshot for a Z-basis outcome 0: 3|0><0| - I = diag(2, -1)
assert np.allclose(3 * np.diag([1, 0]) - np.eye(2), np.diag([2, -1]))

VAR1 = 3 - 0.5 ** 2                                   # weight 1, <Z_1> = 1/2
VAR3 = 27 - 0.75                                      # weight 3, <X_1X_2X_3>^2 = 3/4
assert abs(VAR1 - 2.75) < 1e-12 and abs(VAR3 - 26.25) < 1e-12
GAP = math.sqrt(VAR3 / VAR1)
assert abs(GAP - 3.09) < 0.005 and abs(VAR3 / VAR1 - 9.55) < 0.005
assert abs(3 ** 50 - 7.18e23) / 7.18e23 < 0.001

# 12 shots on 4 qubits, basis codes 0 = X, 1 = Y, 2 = Z, state |+>|0>|+i>|0> (every target has <P> = 1)
SHOT_SEED = 1
BASES = np.random.default_rng(SHOT_SEED).integers(3, size=(12, 4))
TARGETS = {1: (0, None, None, None), 2: (0, 2, None, None), 4: (0, 2, 1, 2)}


def matches(target):
    return np.all([(BASES[:, j] == c) for j, c in enumerate(target) if c is not None], axis=0)


HITS = {k: int(matches(t).sum()) for k, t in TARGETS.items()}
EST = {k: HITS[k] * 3 ** k / 12 for k in TARGETS}
assert HITS == {1: 5, 2: 2, 4: 0} and EST == {1: 1.25, 2: 1.5, 4: 0.0}

TAIL = {K: sum(math.comb(K, j) * 0.25 ** j * 0.75 ** (K - j) for j in range(math.ceil(K / 2), K + 1))
        for K in (5, 9, 17, 25, 33)}
assert abs(TAIL[9] - 0.0489) < 5e-5 and abs(math.exp(-9 / 8) - 0.325) < 5e-4


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["3U^\\dagger|b\\rangle\\langle b|U - I", "\\operatorname{diag}(2,-1)", "3\\,b\\,\\vec e_P",
            "\\mathcal{M}^{-1}(X) = 3X - \\operatorname{Tr}(X)\\, I", "3^{-k}",
            "\\operatorname{Var}\\hat o_P = 3^k - \\langle P\\rangle^2", "26.25", "2.75", "3.09", "e^{-K/8}", "0.049"]


def fixed(scene, *mobs):
    """Pin mobjects to the screen without showing them yet."""
    scene.add_fixed_in_frame_mobjects(*mobs)
    scene.remove(*mobs)


# ---- scene 1 ------------------------------------------------------------------------------------------------
R = 0.82
CAM_PHI, CAM_THETA = 68 * DEGREES, 25 * DEGREES
SCREEN_RIGHT = np.array([-math.sin(CAM_THETA), math.cos(CAM_THETA), 0.0])
CENTER = -2.7 * SCREEN_RIGHT + 0.0 * OUT
LIGHT = "#cbd5e1"


class SnapshotCloud(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=CAM_PHI, theta=CAM_THETA)
        title = label("One random Pauli shot, one snapshot", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        fixed(self, title)
        self.play(Write(title))

        sph = Sphere(center=CENTER, radius=R, resolution=(16, 16))
        sph.set_fill(VIOLET, opacity=0.08).set_stroke(GRID, width=0.4, opacity=0.6)
        axes = VGroup(*[Line(CENTER - 3.35 * R * d, CENTER + 3.35 * R * d, color=MUTED, stroke_width=1.6)
                        for d in (RIGHT, UP, OUT)])
        ring = VMobject(stroke_color=LIGHT, stroke_width=1.5).set_points_smoothly(
            [CENTER + 3 * R * np.array([math.cos(a), math.sin(a), 0]) for a in np.linspace(0, TAU, 73)])
        self.play(Create(sph), Create(axes), Create(ring), run_time=1.6)
        for name, d in (("x", RIGHT), ("y", UP), ("z", OUT)):
            m = eq(name, size=32, color=MUTED).move_to(CENTER + 3.6 * R * d)
            self.add_fixed_orientation_mobjects(m)

        truth = Dot3D(CENTER + R * R_VEC, radius=0.08, color=VIOLET)
        tarrow = Line(CENTER, CENTER + R * R_VEC, color=VIOLET, stroke_width=5)
        self.play(Create(tarrow), FadeIn(truth))

        pts = {(p, b): CENTER + 3 * R * b * E_AXES[p] for p in range(3) for b in (1, -1)}
        six = VGroup(*[Dot3D(v, radius=0.07, color=AMBER) for v in pts.values()])
        self.play(FadeIn(six), run_time=1.0)

        f1 = eq(r"\hat\rho = 3U^\dagger|b\rangle\langle b|U - I", size=34).move_to(RIGHT * 3.7 + UP * 2.55)
        f2 = eq(r"\text{Bloch vector of }\hat\rho:\ 3\,b\,\vec e_P", size=32).move_to(RIGHT * 3.7 + UP * 1.75)
        f3 = eq(r"Z,\ b{=}{+}1:\ \hat\rho = \operatorname{diag}(2,-1)", size=32, color=AMBER).move_to(RIGHT * 3.7 + UP * 0.95)
        f4 = label("eigenvalues 2 and -1: not a state", 24, MUTED).move_to(RIGHT * 3.7 + UP * 0.4)
        for m in (f1, f2, f3, f4):
            fixed(self, m)
        self.play(Write(f1))
        self.play(Write(f2))
        self.play(Write(f3), FadeIn(f4))

        rng = np.random.default_rng(77)
        n_snap = 240
        P = rng.integers(3, size=n_snap)
        B = np.where(rng.random(n_snap) < (1 + R_VEC[P]) / 2, 1, -1)
        snaps = 3 * B[:, None] * E_AXES[P]
        run = np.cumsum(snaps, axis=0) / np.arange(1, n_snap + 1)[:, None]
        err_end = float(np.linalg.norm(run[-1] - R_VEC))
        assert err_end < 4 * math.sqrt(3 * 3 / n_snap)

        k = ValueTracker(0)

        def idx():
            return int(min(n_snap - 1, max(0, round(k.get_value()))))

        cur = always_redraw(lambda: Dot3D(CENTER + R * snaps[idx()], radius=0.12, color=RED))
        avg = always_redraw(lambda: Dot3D(CENTER + R * run[idx()], radius=0.09, color=CYAN))
        path = always_redraw(lambda: VMobject(stroke_color=CYAN, stroke_width=3).set_points_as_corners(
            [CENTER + R * v for v in run[:idx() + 1]] if idx() > 0 else [CENTER + R * run[0], CENTER + R * run[0] + 1e-4 * UP]))
        nlab = label("snapshots N =", 26, INK).move_to(RIGHT * 2.6 + DOWN * 0.55)
        elab = label("distance of average to r =", 26, CYAN).move_to(RIGHT * 3.1 + DOWN * 1.15)
        fixed(self, nlab, elab)
        self.add(cur, avg, path)
        self.play(FadeIn(nlab), FadeIn(elab))
        shown = []

        def numbers(i):
            for m in shown:
                self.remove(m)
            shown.clear()
            nv = label(f"{i + 1}", 28, INK).next_to(nlab, RIGHT, buff=0.2)
            ev = label(f"{np.linalg.norm(run[i] - R_VEC):.3f}", 28, CYAN).next_to(elab, RIGHT, buff=0.2)
            self.add_fixed_in_frame_mobjects(nv, ev)
            shown.extend([nv, ev])

        numbers(0)
        stops = list(range(1, 12)) + list(range(12, n_snap, 12)) + [n_snap - 1]
        for i in stops:
            self.play(k.animate.set_value(i), run_time=0.35 if i < 12 else 0.45, rate_func=linear)
            numbers(i)
        fin = eq(r"\mathbb{E}[\hat\rho] = \rho", size=40, color=VIOLET).move_to(RIGHT * 3.7 + DOWN * 2.1)
        note = label("only the average is a state", 24, MUTED).next_to(fin, DOWN, buff=0.15)
        fixed(self, fin, note)
        self.play(Write(fin), FadeIn(note))
        self.wait(1.5)


# ---- scene 2 ------------------------------------------------------------------------------------------------
class InverseChannel(Scene):
    def construct(self):
        title = label("Average over bases, then undo the average", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title))
        c = LEFT * 3.7 + DOWN * 0.35
        u = 0.92                                      # scene units per Bloch unit
        ax = VGroup(Line(c + LEFT * 3.1 * u, c + RIGHT * 3.1 * u, color=MUTED, stroke_width=1.5),
                    Line(c + DOWN * 3.1 * u, c + UP * 3.1 * u, color=MUTED, stroke_width=1.5))
        xl = eq("x", size=30, color=MUTED).next_to(ax[0], RIGHT, buff=0.08)
        zl = eq("z", size=30, color=MUTED).next_to(ax[1].get_end(), RIGHT, buff=0.12)
        disk = Circle(radius=u, color=VIOLET, stroke_width=3).move_to(c).set_fill(VIOLET, opacity=0.08)
        rxz = np.array([R_VEC[0], R_VEC[2], 0.0])
        st = Dot(c + u * rxz, color=VIOLET, radius=0.07)
        sl = eq(r"\rho", size=34, color=VIOLET).next_to(st, RIGHT, buff=0.14)
        self.play(Create(ax), FadeIn(xl), FadeIn(zl), Create(disk), FadeIn(st), Write(sl))

        x0 = 3.05
        l1 = eq(r"\mathcal{M}(\rho) = \mathbb{E}_U \sum_b \langle b|U\rho U^\dagger|b\rangle\,U^\dagger|b\rangle\langle b|U",
                size=32).move_to(RIGHT * x0 + UP * 2.5)
        l2 = eq(r"= \frac{1}{3}\sum_{P\in\{X,Y,Z\}} \frac{I + r_P\,P}{2}", size=32).move_to(RIGHT * x0 + UP * 1.4)
        l3 = eq(r"= \frac{I}{2} + \frac{\vec r\cdot\vec\sigma}{6}", size=32).move_to(l2)
        l4 = eq(r"= \frac{1}{3}\rho + \frac{\operatorname{Tr}\rho}{3}\, I", size=32).move_to(l2)
        self.play(Write(l1), run_time=2)
        self.play(Write(l2))
        self.wait(0.5)
        self.play(TransformMatchingTex(l2, l3))
        self.wait(0.4)
        self.play(TransformMatchingTex(l3, l4))
        shrink = label("the Bloch ball shrinks by 1/3", 26, MUTED).move_to(RIGHT * x0 + UP * 0.5)
        small = Circle(radius=u / 3, color=VIOLET, stroke_width=3).move_to(c).set_fill(VIOLET, opacity=0.18)
        st2 = Dot(c + u * rxz / 3, color=VIOLET, radius=0.07)
        self.play(Transform(disk.copy(), small), Transform(st.copy(), st2), FadeOut(sl), FadeIn(shrink), run_time=1.8)
        self.wait(0.5)

        inv = eq(r"\mathcal{M}^{-1}(X) = 3X - \operatorname{Tr}(X)\, I", size=34, color=RED).move_to(RIGHT * x0 + DOWN * 0.45)
        self.play(Write(inv))
        snap = VGroup(eq(r"\hat\rho = \mathcal{M}^{-1}\big(U^\dagger|b\rangle\langle b|U\big)", size=32, color=RED),
                      eq(r"= 3U^\dagger|b\rangle\langle b|U - I", size=32, color=RED)).arrange(DOWN, buff=0.15)
        snap.move_to(RIGHT * x0 + DOWN * 1.45)
        self.play(Write(snap))

        proj = Dot(c + u * UP, color=AMBER, radius=0.08)
        pl = eq(r"|0\rangle\langle 0|", size=30, color=AMBER).next_to(proj, LEFT, buff=0.12)
        self.play(FadeIn(proj), Write(pl))
        out = Dot(c + 3 * u * UP, color=RED, radius=0.09)
        arr = Arrow(c + u * UP, c + 3 * u * UP, buff=0.05, color=RED, stroke_width=4)
        ol = eq(r"\operatorname{diag}(2,-1)", size=32, color=RED).next_to(out, LEFT, buff=0.15)
        self.play(Create(arr), FadeIn(out), Write(ol), run_time=1.4)
        others = VGroup(*[Dot(c + 3 * u * v, color=RED, radius=0.07) for v in (DOWN, LEFT, RIGHT)])
        big = DashedLine(c + 3 * u * UP, c + 3 * u * UP, color=RED)
        self.play(FadeIn(others))
        note = label("snapshots sit at radius 3: outside the ball", 26, RED).move_to(RIGHT * x0 + DOWN * 2.75)
        note2 = label("their average is the state", 26, MUTED).next_to(note, DOWN, buff=0.15)
        self.play(FadeIn(note), FadeIn(note2))
        self.wait(1.8)
        _ = big


# ---- scene 3 ------------------------------------------------------------------------------------------------
class BasisMatching(Scene):
    def construct(self):
        title = label("A weight-k Pauli only sees shots whose k bases match", 30, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title))
        letters = "XYZ"
        x0, y0, dx, dy = -6.1, 2.5, 0.78, 0.47
        head = VGroup(*[label(f"q{j + 1}", 24, MUTED).move_to(RIGHT * (x0 + j * dx) + UP * (y0 + 0.45)) for j in range(4)])
        cells = VGroup()
        for i in range(12):
            row = VGroup(*[label(letters[BASES[i, j]], 28, INK).move_to(RIGHT * (x0 + j * dx) + UP * (y0 - i * dy))
                           for j in range(4)])
            cells.add(row)
        state = eq(r"\text{state } |{+}\rangle|0\rangle|{+}i\rangle|0\rangle", size=34).move_to(RIGHT * 2.7 + UP * 2.6)
        self.play(FadeIn(head), FadeIn(cells, lag_ratio=0.05), Write(state), run_time=2)

        def show_target(k, txt, prev=None):
            t = TARGETS[k]
            m = matches(t)
            tgt = eq(txt, size=36, color=VIOLET).move_to(RIGHT * 2.7 + UP * 1.8)
            boxes = VGroup(*[SurroundingRectangle(VGroup(*[cells[i][j] for j in range(4) if t[j] is not None]),
                                                  color=AMBER, buff=0.06, stroke_width=3) for i in range(12) if m[i]])
            vals = VGroup(*[label(f"{3 ** k if m[i] else 0}", 28, AMBER if m[i] else MUTED)
                            .move_to(RIGHT * (x0 + 4 * dx + 0.4) + UP * (y0 - i * dy)) for i in range(12)])
            est = eq(rf"\text{{mean of 12}} = {HITS[k]}\cdot {3 ** k}/12 = {EST[k]:g}", size=34, color=VIOLET)
            est.move_to(RIGHT * 2.7 + UP * 1.05)
            anims = [Write(tgt), FadeIn(vals)] + ([Create(boxes)] if len(boxes) else [])
            if prev:
                self.play(*[FadeOut(p) for p in prev])
            self.play(*anims, run_time=1.4)
            self.play(Write(est))
            self.wait(0.8)
            return [tgt, boxes, vals, est]

        g = show_target(1, r"P = X\otimes I\otimes I\otimes I\quad (k=1)")
        g = show_target(2, r"P = X\otimes Z\otimes I\otimes I\quad (k=2)", g)
        g = show_target(4, r"P = X\otimes Z\otimes Y\otimes Z\quad (k=4)", g)
        none = label("no shot matched: estimate 0, true value 1", 26, RED).move_to(RIGHT * 2.7 + UP * 0.4)
        self.play(FadeIn(none))
        self.wait(0.6)

        rules = VGroup(
            eq(r"\Pr[\text{all } k \text{ bases match}] = 3^{-k}", size=34),
            eq(r"\hat o_P \in \{0,\ \pm 3^k\}", size=34),
            eq(r"\mathbb{E}[\hat o_P^2] = 3^{-k}\cdot 9^k = 3^k", size=34),
            eq(r"\operatorname{Var}\hat o_P = 3^k - \langle P\rangle^2", size=36, color=RED),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to(RIGHT * 2.7 + DOWN * 1.3)
        for r_ in rules:
            self.play(Write(r_), run_time=1.0)
        self.wait(0.5)
        last = eq(r"k = 50:\ 3^{50} \approx 7.2\times 10^{23}", size=34, color=RED).move_to(RIGHT * 2.7 + DOWN * 3.35)
        self.play(FadeOut(none), Write(last))
        self.wait(1.8)


# ---- scene 4 ------------------------------------------------------------------------------------------------
class ErrorVsSnapshots(Scene):
    def construct(self):
        from qcai.lessonfigs import l7_07 as figs
        tab = figs.rmse_table()
        for k in (1, 2, 3):
            ratios = np.array(tab[k]["rmse"]) / np.array(tab[k]["theory"])
            assert np.all(np.abs(ratios - 1) < 0.15)
        title = label("Error falls like 1/sqrt(N); the weight sets the offset", 30, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title))
        # plot coordinates: x = log10(N) - 1, y = log10(RMSE) + 2, so the axes cross at N = 10, RMSE = 0.01
        ax = Axes(x_range=[0, 2.7, 1], y_range=[0, 2.5, 1], x_length=6.2, y_length=5.0,
                  axis_config={"color": MUTED, "include_tip": False, "include_ticks": False}).move_to(LEFT * 3.1 + DOWN * 0.45)

        def P(logn, logr):
            return ax.c2p(logn - 1, logr + 2)

        ticks = VGroup()
        for v, s_ in ((1, "10"), (2, "100"), (3, "1000")):
            ticks.add(label(s_, 22, MUTED).next_to(P(v, -2), DOWN, buff=0.15))
            if v > 1:
                ticks.add(Line(P(v, -2), P(v, 0.5), color=GRID, stroke_width=1))
        for v, s_ in ((-2, "0.01"), (-1, "0.1"), (0, "1")):
            ticks.add(label(s_, 22, MUTED).next_to(P(1, v), LEFT, buff=0.15))
            if v > -2:
                ticks.add(Line(P(1, v), P(3.7, v), color=GRID, stroke_width=1))
        xl = label("snapshots N (log scale)", 24, MUTED).next_to(ax, DOWN, buff=0.5)
        yl = label("RMSE", 24, MUTED).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        self.play(FadeIn(ticks), Create(ax), FadeIn(xl), FadeIn(yl))

        cols = {1: BLUE, 2: AMBER, 3: RED}
        var = {k: 3 ** k - tab[k]["truth"] ** 2 for k in (1, 2, 3)}
        lx = ValueTracker(1.0)

        def theory_line(k):
            def f():
                x1 = max(lx.get_value(), 1.0001)
                return Line(P(1, 0.5 * math.log10(var[k]) - 0.5), P(x1, 0.5 * math.log10(var[k]) - 0.5 * x1),
                            color=cols[k], stroke_width=3).set_opacity(0.8)
            return always_redraw(f)

        lines = [theory_line(k) for k in (1, 2, 3)]
        self.add(*lines)
        dots = VGroup()
        for k in (1, 2, 3):
            for N, r in zip(figs.NS, tab[k]["rmse"]):
                d = Dot(P(math.log10(N), math.log10(r)), color=cols[k], radius=0.065)
                d.add_updater(lambda m, x=math.log10(N): m.set_opacity(1.0 if lx.get_value() >= x - 1e-6 else 0.0))
                dots.add(d)
        self.add(dots)
        self.play(lx.animate.set_value(math.log10(4000)), run_time=6, rate_func=linear)
        for d in dots:
            d.clear_updaters()
        keys = VGroup(eq(r"Z_1:\ \operatorname{Var} = 3 - 0.25 = 2.75", size=32, color=BLUE),
                      eq(r"Z_1Z_2:\ \operatorname{Var} = 9 - 1 = 8", size=32, color=AMBER),
                      eq(r"X_1X_2X_3:\ \operatorname{Var} = 27 - 0.75 = 26.25", size=32, color=RED))
        keys.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 3.55 + UP * 1.75)
        self.play(Write(keys), run_time=2)
        xa = 3.4
        y1, y3 = 0.5 * math.log10(var[1]) - 0.5 * xa, 0.5 * math.log10(var[3]) - 0.5 * xa
        gap = Arrow(P(xa, y1), P(xa, y3), buff=0, color=INK, stroke_width=4, max_tip_length_to_length_ratio=0.25)
        gl = eq(r"\times\sqrt{26.25/2.75} \approx 3.09", size=34).move_to(RIGHT * 3.55 + DOWN * 0.05)
        self.play(Create(gap), Write(gl))
        more = label("same error: 9.5 times the snapshots", 24, MUTED).next_to(gl, DOWN, buff=0.2)
        self.play(FadeIn(more))
        slope = eq(r"\text{slope } -\tfrac12:\ \ N \approx \operatorname{Var}/\epsilon^2", size=34, color=VIOLET)
        slope.move_to(RIGHT * 3.55 + DOWN * 1.55)
        self.play(Write(slope))
        src = label("dots: 400 seeded runs; lines: theory", 24, MUTED).move_to(RIGHT * 3.55 + DOWN * 2.45)
        self.play(FadeIn(src))
        self.wait(1.8)


# ---- scene 5 ------------------------------------------------------------------------------------------------
class MedianOfMeans(Scene):
    def construct(self):
        title = label("Median of means: a bad answer needs half the groups to fail", 30, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title))
        # part 1: five group means on a line, one wild group; the mean moves out of the band, the median does not
        nl = Line(LEFT * 6.4 + UP * 1.5, LEFT * 0.5 + UP * 1.5, color=MUTED)
        mu_x, eps_u = -4.6, 0.5
        band = Rectangle(width=2 * eps_u, height=0.55, stroke_width=0, fill_color=CYAN, fill_opacity=0.2).move_to(RIGHT * mu_x + UP * 1.5)
        mu = Line(RIGHT * mu_x + UP * 1.15, RIGHT * mu_x + UP * 1.85, color=VIOLET, stroke_width=4)
        mul = eq(r"\langle O\rangle", size=32, color=VIOLET).next_to(mu.get_top(), LEFT, buff=0.15)
        epsl = eq(r"\pm\epsilon", size=30, color=CYAN).next_to(band, DOWN, buff=0.12).shift(LEFT * 0.55)
        self.play(Create(nl), FadeIn(band), Create(mu), Write(mul), Write(epsl))
        offs = [-0.4, -0.15, 0.05, 0.3, 3.3]                     # scene units; the last group failed badly
        gdots = VGroup(*[Dot(RIGHT * (mu_x + o) + UP * 1.5, color=RED if abs(o) > eps_u else BLUE, radius=0.09) for o in offs])
        self.play(FadeIn(gdots, lag_ratio=0.2), run_time=1.5)
        mean_x = mu_x + sum(offs) / len(offs)
        med_x = mu_x + sorted(offs)[len(offs) // 2]
        assert abs(mean_x - mu_x) > eps_u and abs(med_x - mu_x) < eps_u
        mean_m = VGroup(Line(RIGHT * mean_x + UP * 0.85, RIGHT * mean_x + UP * 1.2, color=AMBER, stroke_width=5),
                        label("mean", 24, AMBER).move_to(RIGHT * mean_x + UP * 0.6))
        med_m = VGroup(Line(RIGHT * med_x + UP * 1.85, RIGHT * med_x + UP * 2.2, color=BLUE, stroke_width=5),
                       label("median", 24, BLUE).move_to(RIGHT * med_x + UP * 2.45))
        self.play(FadeIn(mean_m), FadeIn(med_m))
        expl = VGroup(label("K groups of N snapshots each", 24, INK),
                      label("one wild group drags the mean", 24, AMBER),
                      label("the median needs half to move", 24, BLUE)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        expl.move_to(RIGHT * 3.4 + UP * 1.75)
        self.play(FadeIn(expl, lag_ratio=0.3), run_time=1.5)
        self.wait(0.6)

        # part 2: number of failed groups ~ Binomial(K, 1/4); tail vs e^{-K/8}
        cheb = eq(r"N \ge 4\sigma^2/\epsilon^2 \ \Rightarrow\ \Pr[\text{group fails}] \le \tfrac14", size=32).move_to(RIGHT * 3.4 + DOWN * 0.1)
        self.play(Write(cheb))
        base_y, x_left, top_h = -3.2, -6.0, 2.4
        axis = Line(RIGHT * x_left + UP * base_y, RIGHT * (x_left + 5.8) + UP * base_y, color=MUTED)
        self.play(Create(axis))
        Ks = [5, 9, 17, 25, 33]

        def bars(K):
            w = 5.6 / (K + 1)
            pm = [math.comb(K, j) * 0.25 ** j * 0.75 ** (K - j) for j in range(K + 1)]
            mx = max(pm)
            g = VGroup()
            for j, p in enumerate(pm):
                h = max(top_h * p / mx, 0.002)
                g.add(Rectangle(width=w * 0.85, height=h, stroke_width=0, fill_opacity=0.85,
                                fill_color=RED if j >= math.ceil(K / 2) else BLUE)
                      .move_to(RIGHT * (x_left + 0.1 + w * (j + 0.5)) + UP * (base_y + h / 2)))
            return g

        def readout(K):
            return VGroup(eq(rf"K = {K}", size=32),
                          eq(rf"\Pr[\ge K/2 \text{{ fail}}] = {TAIL[K]:.3f}", size=32, color=RED),
                          eq(rf"\text{{Hoeffding: }} e^{{-K/8}} = {math.exp(-K / 8):.3f}", size=32, color=MUTED)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(RIGHT * 3.4 + DOWN * 1.75)

        cap = label("failed groups out of K", 22, MUTED).next_to(axis, DOWN, buff=0.12)
        b = bars(Ks[0])
        ro = readout(Ks[0])
        self.play(FadeIn(b), Write(ro), FadeIn(cap))
        for K in Ks[1:]:
            self.play(Transform(b, bars(K)), Transform(ro, readout(K)), run_time=1.3)
            self.wait(0.5 if K != 9 else 1.0)
        fin = eq(r"K \ge 8\ln(1/\delta)\ \Rightarrow\ \Pr[\text{median fails}] \le \delta", size=32, color=VIOLET)
        fin.move_to(RIGHT * 3.4 + DOWN * 3.15)
        self.play(Write(fin))
        self.play(Indicate(fin, color=VIOLET))
        self.wait(1.5)
