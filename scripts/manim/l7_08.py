"""L7-08 Reproducible quantum causal benchmarks: four scenes.

ObservationalTwins  two linear models, X -> Y and a confounded U -> X, U -> Y, X -> Y, with the same Gaussian
                    observational distribution (covariance [[2, 2], [2, 3.5]]); graph surgery for do(X) splits them:
                    slope 1.0 against 0.5.  Prediction cannot rank them; a held-out intervention can.
MetricsDisagree     a true 4-node graph and three estimates, each at structural Hamming distance 1, with very
                    different interventional errors.
QuantumHeldOut      ThreeDScene: identity and dephasing channels agree on Z-basis training data; the held-out
                    preparation |+> with an X measurement separates them, P(+) = 1 - p.
BenchmarkFailures   the harness in qcai/lessonfigs/l7_08.py: one seed against twenty, label leakage, a change of units
                    (ablation of scale information), and choosing the best of 30 null models on the test seeds.
facts() lists strings shown on screen that also appear in the lesson text.
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DEGREES, DOWN, LEFT, OUT, RIGHT, TAU, UP, Arrow, Axes, Circle, Create, Cross, Dot, Dot3D, FadeIn,
                   FadeOut, Line, Rectangle, Scene, Sphere, SurroundingRectangle, ThreeDScene, Transform, VGroup,
                   VMobject, Write)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ---- scene 1 numbers: two observationally equivalent models ---------------------------------------------------
# A: X ~ N(0, 2), Y = 1.0 X + e, Var e = 1.5.   B: U, eX, eY ~ N(0, 1), X = U + eX, Y = 0.5 X + U + eY.
COV_A = np.array([[2.0, 2.0], [2.0, 1.0 * 2.0 + 1.5]])
COV_B = np.array([[1 + 1, 0.5 * 2 + 1], [0.5 * 2 + 1, 0.25 * 2 + 1 + 2 * 0.5 * 1 + 1]])
assert np.allclose(COV_A, COV_B) and np.allclose(COV_A, [[2, 2], [2, 3.5]])
OBS_SLOPE = COV_A[0, 1] / COV_A[0, 0]
assert OBS_SLOPE == 1.0
DO_SLOPE = {"A": 1.0, "B": 0.5}


# ---- scene 2 numbers: three estimates at SHD 1 -----------------------------------------------------------------
def _scene2():
    from qcai.lessonfigs import l7_08 as h
    # nodes 0 = A, 1 = B, 2 = C, 3 = D; edges A->B 1.5, A->C 0.6, B->D 1.0, C->D 0.8
    B = np.zeros((4, 4))
    B[0, 1], B[0, 2], B[1, 3], B[2, 3] = 1.5, 0.6, 1.0, 0.8
    A = np.linalg.inv(np.eye(4) - B)
    var = np.diag(A.T @ A)
    task = dict(B=B, var=var, do_mean=np.array([h.do_mean(B, j, 2 * math.sqrt(var[j])) for j in range(4)]))
    ests = {}
    for name, (i, j, w) in {"miss A->C (0.6)": (0, 2, 0.0), "miss A->B (1.5)": (0, 1, 0.0),
                            "extra B->C (0.1)": (1, 2, 0.1)}.items():
        W = B.copy()
        W[i, j] = w
        ests[name] = (h.shd(W, B), h.int_error(task, W), W)
    return B, ests


S2_ERR = {"miss A->C (0.6)": 0.100, "miss A->B (1.5)": 0.345, "extra B->C (0.1)": 0.015}


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [r"\begin{pmatrix} 2 & 2 \\ 2 & 3.5 \end{pmatrix}", r"\mathbb{E}[Y \mid do(X = x)] = 0.5\,x",
            r"(1-p)\rho + pZ\rho Z", "P(+) = 1 - p", "0.100", "0.345", "0.015"]


def node(name, pos, color=INK):
    c = Circle(radius=0.32, color=color, stroke_width=3).move_to(pos).set_fill("#ffffff", opacity=1)
    return VGroup(c, label(name, 28, color).move_to(pos))


def edge(a, b, color=MUTED, w=None, side=UP):
    arr = Arrow(a.get_center(), b.get_center(), buff=0.36, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.18)
    if w is None:
        return arr
    return VGroup(arr, label(w, 22, color).next_to(arr.get_center(), side, buff=0.08))


# ---- scene 1 ------------------------------------------------------------------------------------------------
class ObservationalTwins(Scene):
    def construct(self):
        title = label("Same data, different interventions", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title))
        xa, ya = node("X", LEFT * 5.7 + UP * 1.9, VIOLET), node("Y", LEFT * 3.5 + UP * 1.9, VIOLET)
        ga = VGroup(xa, ya, edge(xa, ya, VIOLET, "1.0"), label("model A", 24, VIOLET).move_to(LEFT * 4.6 + UP * 2.75))
        ub = node("U", LEFT * 4.6 + DOWN * 0.95, AMBER)
        xb, yb = node("X", LEFT * 5.7 + DOWN * 2.45, AMBER), node("Y", LEFT * 3.5 + DOWN * 2.45, AMBER)
        e_ux = edge(ub, xb, AMBER)
        gb = VGroup(ub, xb, yb, e_ux, edge(ub, yb, AMBER), edge(xb, yb, AMBER, "0.5", DOWN),
                    label("model B", 24, AMBER).move_to(LEFT * 4.6 + DOWN * 0.3))
        self.play(FadeIn(ga), FadeIn(gb), run_time=1.5)
        sig = eq(r"\Sigma = \begin{pmatrix} 2 & 2 \\ 2 & 3.5 \end{pmatrix}", size=32).move_to(LEFT * 4.6 + UP * 0.65)
        self.play(Write(sig))

        ax = Axes(x_range=[-4, 4, 2], y_range=[-6, 6, 3], x_length=6.2, y_length=4.5,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 2.6 + DOWN * 0.85)
        xl = eq("X", size=30, color=MUTED).next_to(ax.x_axis, RIGHT, buff=0.1)
        yl = eq("Y", size=30, color=MUTED).next_to(ax.y_axis.get_top(), LEFT, buff=0.15)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        rng = np.random.default_rng(8)
        n = 140
        XA = rng.normal(0, math.sqrt(2), n)
        YA = XA + rng.normal(0, math.sqrt(1.5), n)
        U, eX, eY = rng.normal(size=(3, n))
        XB = U + eX
        YB = 0.5 * XB + U + eY

        def cloud(xs, ys, color):
            return VGroup(*[Dot(ax.c2p(float(np.clip(x, -3.9, 3.9)), float(np.clip(y, -5.9, 5.9))), radius=0.035,
                                color=color, fill_opacity=0.7) for x, y in zip(xs, ys)])

        ca, cb = cloud(XA, YA, VIOLET), cloud(XB, YB, AMBER)
        self.play(FadeIn(ca, lag_ratio=0.01), FadeIn(cb, lag_ratio=0.01), run_time=2)
        obs = Line(ax.c2p(-3.9, -3.9 * OBS_SLOPE), ax.c2p(3.9, 3.9 * OBS_SLOPE), color=INK, stroke_width=4)
        ol = eq(r"\mathbb{E}[Y \mid X = x] = x \ \text{(both)}", size=32).move_to(RIGHT * 2.6 + UP * 2.6)
        self.play(Create(obs), Write(ol))
        note = label("any predictor scores the same on both", 24, MUTED).next_to(ol, DOWN, buff=0.12)
        self.play(FadeIn(note))
        self.wait(1.0)

        # graph surgery on B: delete U -> X, set X by hand
        cross = Cross(e_ux, stroke_color=RED, stroke_width=6)
        dob = SurroundingRectangle(xb, color=RED, buff=0.08)
        dol = label("do(X)", 24, RED).next_to(xb, DOWN, buff=0.15)
        self.play(Create(cross), Create(dob), FadeIn(dol))
        self.play(FadeOut(e_ux), FadeOut(cross), FadeOut(note))
        Xd = rng.normal(0, math.sqrt(2), n)
        Ud, eYd = rng.normal(size=(2, n))
        cb2 = cloud(Xd, 0.5 * Xd + Ud + eYd, AMBER)
        self.play(Transform(cb, cb2), FadeOut(obs), FadeOut(ol), run_time=1.6)
        la = Line(ax.c2p(-3.9, -3.9), ax.c2p(3.9, 3.9), color=VIOLET, stroke_width=5)
        lb = Line(ax.c2p(-3.9, -3.9 * 0.5), ax.c2p(3.9, 3.9 * 0.5), color=AMBER, stroke_width=5)
        ta = eq(r"\text{A: } \mathbb{E}[Y \mid do(X = x)] = x", size=32, color=VIOLET).move_to(RIGHT * 2.6 + UP * 2.75)
        tb = eq(r"\text{B: } \mathbb{E}[Y \mid do(X = x)] = 0.5\,x", size=32, color=AMBER).move_to(RIGHT * 2.6 + UP * 2.15)
        self.play(Create(la), Write(ta))
        self.play(Create(lb), Write(tb))
        fin = label("only a held-out intervention can rank them", 26, RED).move_to(RIGHT * 2.6 + DOWN * 3.5)
        self.play(FadeIn(fin))
        self.wait(1.8)


# ---- scene 2 ------------------------------------------------------------------------------------------------
class MetricsDisagree(Scene):
    def construct(self):
        B, ests = _scene2()
        for k, (s_, e_, _) in ests.items():
            assert s_ == 1 and abs(e_ - S2_ERR[k]) < 5e-4, (k, e_)
        title = label("Three estimates, one structural Hamming distance", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title))
        names = "ABCD"

        def graph(center, W, highlight=None, extra_color=RED):
            pos = [center + UP * 1.3, center + LEFT * 1.3, center + RIGHT * 1.3, center + DOWN * 1.3]
            nodes = [node(names[i], pos[i]) for i in range(4)]
            g = VGroup(*nodes)
            for i in range(4):
                for j in range(4):
                    if W[i, j] != 0 or B[i, j] != 0:
                        if W[i, j] == 0:
                            a = Arrow(nodes[i].get_center(), nodes[j].get_center(), buff=0.36, color=RED, stroke_width=3,
                                      max_tip_length_to_length_ratio=0.15).set_opacity(0.35)
                            a = VGroup(a, label("missing", 20, RED).move_to((pos[i] + pos[j]) / 2 + LEFT * 0.35 + UP * 0.1))
                        else:
                            col = extra_color if B[i, j] == 0 else MUTED
                            a = edge(nodes[i], nodes[j], col, f"{W[i, j]:g}", UP if j != 3 else RIGHT)
                        g.add(a)
            return g

        tl = label("truth", 26, MUTED).move_to(LEFT * 4.6 + UP * 2.6)
        truth = graph(LEFT * 4.6 + DOWN * 0.4, B)
        self.play(FadeIn(tl), FadeIn(truth), run_time=1.5)
        el = label("estimate", 26, MUTED).move_to(RIGHT * 0.2 + UP * 2.6)
        self.play(FadeIn(el))
        table = VGroup()
        cur = None
        for r, (k, (s_, e_, W)) in enumerate(ests.items()):
            g = graph(RIGHT * 0.2 + DOWN * 0.4, W)
            if cur is None:
                self.play(FadeIn(g), run_time=1.2)
            else:
                self.play(Transform(cur, g), run_time=1.2)
            cur = cur or g
            row = VGroup(label(k, 24, INK), eq(rf"\mathrm{{SHD}} = {s_}", size=32),
                         eq(f"{e_:.3f}", size=34, color=RED)).arrange(RIGHT, buff=0.3)
            row.move_to(RIGHT * 4.6 + UP * (1.3 - 0.8 * r))
            table.add(row)
            self.play(FadeIn(row))
            self.wait(0.6)
        head = label("interventional error in red", 24, RED).move_to(RIGHT * 4.6 + UP * 2.05)
        self.play(FadeIn(head))
        msg = VGroup(label("SHD counts edges and ignores how strong they are.", 26, INK),
                     label("Report both: structure and interventional error.", 26, RED)).arrange(DOWN, buff=0.15)
        msg.move_to(DOWN * 3.05)
        self.play(FadeIn(msg))
        self.wait(2.0)


# ---- scene 3 ------------------------------------------------------------------------------------------------
R3 = 1.6
CAM_PHI, CAM_THETA = 70 * DEGREES, 20 * DEGREES
SCREEN_RIGHT = np.array([-math.sin(CAM_THETA), math.cos(CAM_THETA), 0.0])
CENTER = -3.0 * SCREEN_RIGHT


def fixed(scene, *mobs):
    scene.add_fixed_in_frame_mobjects(*mobs)
    scene.remove(*mobs)


class QuantumHeldOut(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=CAM_PHI, theta=CAM_THETA)
        title = label("Two channels that agree on every training setting", 30, INK, "BOLD").to_edge(UP, buff=0.25)
        fixed(self, title)
        self.play(Write(title))
        sph = Sphere(center=CENTER, radius=R3, resolution=(16, 16))
        sph.set_fill(VIOLET, opacity=0.05).set_stroke(GRID, width=0.4, opacity=0.5)
        axes = VGroup(*[Line(CENTER - 1.25 * R3 * d, CENTER + 1.25 * R3 * d, color=MUTED, stroke_width=1.6) for d in (RIGHT, UP, OUT)])
        eqt = VMobject(stroke_color="#cbd5e1", stroke_width=2).set_points_smoothly(
            [CENTER + R3 * np.array([math.cos(a), math.sin(a), 0]) for a in np.linspace(0, TAU, 73)])
        self.play(Create(sph), Create(axes), Create(eqt), run_time=1.5)
        for txt, d in ((r"|0\rangle", OUT), (r"|1\rangle", -OUT), (r"|{+}\rangle", RIGHT)):
            m = eq(txt, size=32, color=MUTED).move_to(CENTER + 1.45 * R3 * d)
            self.add_fixed_orientation_mobjects(m)

        ch = eq(r"\mathcal{E}_p(\rho) = (1-p)\rho + pZ\rho Z", size=34).move_to(RIGHT * 3.4 + UP * 2.4)
        sub = label("identity: p = 0    dephasing: p > 0", 24, MUTED).move_to(RIGHT * 3.4 + UP * 1.8)
        fixed(self, ch, sub)
        self.play(Write(ch), FadeIn(sub))

        def vec(v, color, width=6):
            return Line(CENTER, CENTER + R3 * np.asarray(v, dtype=float), color=color, stroke_width=width)

        up_id, up_dp = vec(OUT, VIOLET, 8), vec(OUT, RED, 4)
        dn_id, dn_dp = vec(-OUT, VIOLET, 8), vec(-OUT, RED, 4)
        tr = VGroup(eq(r"\text{train: } |0\rangle, |1\rangle \text{ in, } Z \text{ out}", size=32),
                    eq(r"P(\text{same}) = 1 \text{ for every } p", size=32, color=VIOLET)).arrange(DOWN, buff=0.15)
        tr.move_to(RIGHT * 3.4 + UP * 0.75)
        fixed(self, tr)
        self.play(Create(up_id), Create(up_dp), Create(dn_id), Create(dn_dp), Write(tr), run_time=1.8)
        same = label("training data cannot tell them apart", 24, RED).move_to(RIGHT * 3.4 + DOWN * 0.15)
        fixed(self, same)
        self.play(FadeIn(same))
        self.wait(0.8)

        ho = VGroup(eq(r"\text{held out: } |{+}\rangle \text{ in, } X \text{ out}", size=32),
                    eq(r"\text{Bloch } x = 1 - 2p,\quad P(+) = 1 - p", size=32, color=RED)).arrange(DOWN, buff=0.15)
        ho.move_to(RIGHT * 3.4 + DOWN * 1.15)
        fixed(self, ho)
        self.play(FadeOut(up_id), FadeOut(up_dp), FadeOut(dn_id), FadeOut(dn_dp), Write(ho))
        pid = vec(RIGHT, VIOLET, 8)
        self.play(Create(pid))
        cur = vec(RIGHT, RED, 5)
        self.play(Create(cur))
        shown = []
        for p in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
            assert abs((1 + (1 - 2 * p)) / 2 - (1 - p)) < 1e-12
            new = vec([1 - 2 * p + 1e-3, 0, 0], RED, 5)
            self.play(Transform(cur, new), run_time=0.7)
            for m in shown:
                self.remove(m)
            shown.clear()
            r = eq(rf"p = {p:.1f}:\ \ P(+) = {1 - p:.1f} \text{{ vs }} 1.0", size=32, color=RED).move_to(RIGHT * 3.4 + DOWN * 2.3)
            self.add_fixed_in_frame_mobjects(r)
            shown.append(r)
            self.wait(0.4)
        fin = label("a benchmark without this test rewards both", 24, INK).move_to(RIGHT * 3.4 + DOWN * 3.0)
        fixed(self, fin)
        self.play(FadeIn(fin))
        self.wait(1.6)


# ---- scene 4 ------------------------------------------------------------------------------------------------
class BenchmarkFailures(Scene):
    def construct(self):
        from qcai.lessonfigs import l7_08 as h
        taus = h.tune(h.VAL_SEEDS)
        main = h.run_benchmark(h.TEST_SEEDS, taus)
        leak = h.run_benchmark(h.TEST_SEEDS, h.tune(h.VAL_SEEDS, permute=False), permute=False)
        units = h.run_benchmark(h.TEST_SEEDS, taus, rescale=True)
        sel = h.selection_demo()
        learners = ["empty graph", "column order", "variance sort", "random order", "true order"]
        short = ["empty", "column", "variance\nsort", "random", "true\norder"]
        cols = [h.COLORS[L] for L in learners]
        one = {r[0]: r[2] for r in main if r[1] == 105}
        mean = {L: h.summarize(main, L, 2) for L in learners}
        assert one["random order"] < one["variance sort"] and mean["random order"][0] > mean["variance sort"][0]

        title = label("Four ways a benchmark can mislead", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title))
        base_y, x0, wbar, scale = -2.6, -6.0, 0.95, 0.42
        axis = Line(RIGHT * (x0 - 0.2) + UP * base_y, RIGHT * (x0 + 5 * 1.25) + UP * base_y, color=MUTED)
        ylab = label("SHD", 24, MUTED).move_to(RIGHT * (x0 + 0.2) + UP * 2.55)
        names = VGroup(*[label(s_, 20, MUTED).move_to(RIGHT * (x0 + 0.5 + 1.25 * i) + UP * (base_y - 0.45))
                         for i, s_ in enumerate(short)])
        self.play(Create(axis), FadeIn(names), FadeIn(ylab))

        def bars(vals, errs=None):
            g = VGroup()
            for i, v in enumerate(vals):
                hgt = max(v * scale, 0.02)
                r = Rectangle(width=wbar, height=hgt, stroke_width=0, fill_color=cols[i], fill_opacity=0.85)
                r.move_to(RIGHT * (x0 + 0.5 + 1.25 * i) + UP * (base_y + hgt / 2))
                txt = label(f"{v:.2f}" if errs is not None else f"{v:g}", 20, INK).next_to(r, UP, buff=0.06)
                parts = [r, txt]
                if errs is not None:
                    top = base_y + v * scale
                    e = Line(RIGHT * (x0 + 0.5 + 1.25 * i) + UP * max(base_y, top - errs[i] * scale),
                             RIGHT * (x0 + 0.5 + 1.25 * i) + UP * (top + errs[i] * scale), color=INK, stroke_width=2)
                    txt.next_to(e, UP, buff=0.06)
                    parts.append(e)
                g.add(VGroup(*parts))
            return g

        x_t = 3.7
        LEFT_EDGE = RIGHT * 0.9
        b = bars([one[L] for L in learners])
        t1 = VGroup(label("1. One seed (105):", 26, INK, "BOLD"),
                    label("random order beats variance sort", 24, RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        t1.move_to(RIGHT * x_t + UP * 2.2).align_to(LEFT_EDGE, LEFT)
        self.play(FadeIn(b), FadeIn(t1))
        self.wait(1.0)
        b2 = bars([mean[L][0] for L in learners], [mean[L][1] for L in learners])
        t1b = label("20 seeds, mean and sd: it does not", 24, MUTED).next_to(t1, DOWN, aligned_edge=LEFT, buff=0.1)
        self.play(Transform(b, b2), FadeIn(t1b), run_time=1.5)
        self.wait(1.0)

        lk = h.summarize(leak, "column order", 2)[0]
        t2 = VGroup(label("2. Labels left in causal order:", 26, INK, "BOLD"),
                    label(f"column order {mean['column order'][0]:.2f} -> {lk:.2f}", 24, RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        t2.move_to(RIGHT * x_t + UP * 0.75).align_to(t1, LEFT)
        hl = SurroundingRectangle(b[1], color=RED, buff=0.08)
        self.play(FadeIn(t2), Create(hl))
        vals = [mean[L][0] for L in learners]
        vals[1] = lk
        self.play(Transform(b, bars(vals, [mean[L][1] if L != "column order" else h.summarize(leak, L, 2)[1] for L in learners])))
        self.wait(0.8)
        self.play(Transform(b, b2.copy()), FadeOut(hl))

        un = h.summarize(units, "variance sort", 2)
        t3 = VGroup(label("3. Ablation: random units", 26, INK, "BOLD"),
                    label(f"variance sort {mean['variance sort'][0]:.2f} -> {un[0]:.2f}", 24, RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        t3.move_to(RIGHT * x_t + DOWN * 0.55).align_to(t1, LEFT)
        hl = SurroundingRectangle(b[2], color=RED, buff=0.08)
        self.play(FadeIn(t3), Create(hl))
        vals = [mean[L][0] for L in learners]
        vals[2] = un[0]
        errs = [mean[L][1] for L in learners]
        errs[2] = un[1]
        self.play(Transform(b, bars(vals, errs)))
        self.wait(0.8)
        self.play(FadeOut(hl))

        t4 = VGroup(label("4. Best of 30 null models,", 26, INK, "BOLD"),
                    label("   picked on the test seeds:", 26, INK, "BOLD"),
                    label(f"test {sel['test_best']:.2f} (mean of 30: {sel['test_mean']:.2f})", 24, RED),
                    label(f"fresh {sel['fresh_best']:.2f} (mean of 30: {sel['fresh_mean']:.2f})", 24, MUTED)
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        t4.move_to(RIGHT * x_t + DOWN * 2.45).align_to(t1, LEFT)
        self.play(FadeIn(t4, lag_ratio=0.3), run_time=1.5)
        self.wait(2.0)
