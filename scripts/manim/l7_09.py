"""L7-09 A research protocol from question to result: four scenes.

ProtocolPipeline  the nine stations of a preregistered protocol filled in for the depolarizing study
                  (N = 572, reject if K >= 38), then the garden of forking paths: 10 independent level-0.05
                  analyses give a false-positive chance 1 - 0.95^10 = 0.401.
OptionalStopping  40 seeded z-statistic paths under H0 monitored every 10 shots: 11 of 40 cross z = 1.645 at
                  some look, 2 of 40 are above it at n = 1000; then the exact Gaussian false-positive rate
                  as the number of looks grows (0.050, 0.130, 0.215, 0.311).
VilleBarrier      likelihood-ratio paths against the barrier 20, and Ville's inequality derived term by term.
MiniStudy         a simulated two-qubit causal study: latent bit H, intervention do(a) on A, partial swap,
                  readout of B; ACE = s derived, then running interventional and observational estimates.
All numbers come from qcai/lessonfigs/l7_09.py and are checked against the lesson text by facts().
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, DashedLine, Dot, FadeIn, FadeOut, Line,
                   Rectangle, RoundedRectangle, Scene, Transform, TransformMatchingTex, ValueTracker, VGroup,
                   VMobject, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label, tex
from qcai.lessonfigs import l7_09 as M

D = M.fixed_design()
N_PLAN, K_STAR = D["n"], D["k_star"]
assert (N_PLAN, K_STAR) == (572, 38) and abs(D["power"] - 0.901) < 5e-4
FORK = 1 - (1 - M.ALPHA) ** 10
assert abs(FORK - 0.401) < 5e-4
CZ = M.z(1 - M.ALPHA)
WALKS = M.sample_walks()
CROSS = [int(np.argmax(w > CZ)) if (w > CZ).any() else None for w in WALKS]
N_CROSS = sum(c is not None for c in CROSS)
N_FINAL = int((WALKS[:, -1] > CZ).sum())
assert (N_CROSS, N_FINAL) == (11, 2)
GK = (1, 5, 20, 100)
GFPR = [round(M.gauss_fpr(K), 3) if K > 1 else 0.05 for K in GK]
assert GFPR == [0.05, 0.13, 0.215, 0.311], GFPR
LLR = M.sample_loglr()
LOG20 = math.log(M.VILLE)
V_CROSS = [int(np.argmax(w >= LOG20)) if (w >= LOG20).any() else None for w in LLR]
N_VCROSS = sum(c is not None for c in V_CROSS)
assert N_VCROSS == 1
R = M.regime_rates()
assert abs(R["ace"] - 0.10) < 1e-12 and abs(R["obs_contrast"] - 0.37) < 1e-12
ST = M.run_study()
LB = ST["ace_hat"] - CZ * ST["se"]
assert ST["n_arm"] == 257 and (ST["k0"], ST["k1"]) == (36, 52)


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["N = 572", r"K \ge 38", "0.401", "11 of 40", "2 of 40", "0.311", "1 of 40", "s + c(1-s)",
            f"{ST['ace_hat']:.3f}", f"{ST['obs_hat']:.3f}"]


def ink_axes(ax):
    for a in (ax.x_axis, ax.y_axis):
        if hasattr(a, "numbers"):
            a.numbers.set_color(INK)
    return ax


def station(text, pos, w=2.7, h=0.62):
    box = RoundedRectangle(width=w, height=h, corner_radius=0.12, color=MUTED, stroke_width=2.5).move_to(pos)
    return VGroup(box, label(text, 24, INK).move_to(pos))


class ProtocolPipeline(Scene):
    def construct(self):
        title = label("A protocol is a commitment made before the data", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.2)
        names = ["Question", "Estimand", "Identification", "Design", "Sample size",
                 "Stopping rule", "Analysis plan", "Robustness", "Report"]
        pos = [np.array([-5.15, 2.3 - 1.0 * i, 0]) for i in range(5)] + [np.array([-2.25, -1.7 + 1.0 * i, 0]) for i in range(4)]
        st = [station(n, p) for n, p in zip(names, pos)]
        arrows = VGroup(*[Arrow(st[i][0].get_bottom(), st[i + 1][0].get_top(), buff=0.04, color=MUTED, stroke_width=3,
                                max_tip_length_to_length_ratio=0.35) for i in (0, 1, 2, 3)])
        arrows.add(*[Arrow(st[i][0].get_top(), st[i + 1][0].get_bottom(), buff=0.04, color=MUTED, stroke_width=3,
                           max_tip_length_to_length_ratio=0.35) for i in (5, 6, 7)])
        arrows.add(Arrow(st[4][0].get_right(), st[5][0].get_left(), buff=0.04, color=MUTED, stroke_width=3,
                         max_tip_length_to_length_ratio=0.3))
        self.play(*[FadeIn(s) for s in st], Create(arrows), run_time=1.6)
        panel_c = np.array([3.6, 0.6, 0])
        contents = [
            tex(r"Is the noise above the spec $p = 0.10$?", 32),
            eq(r"\mathcal{E}_p(\rho) = (1-p)\rho + p\,I/2", size=38),
            VGroup(eq(r"P(1) = p/2 \;\Rightarrow\; p = 2\,P(1)", size=38),
                   label("assumes trusted preparation and readout", 24, MUTED)).arrange(DOWN, buff=0.25),
            tex(r"input $|0\rangle$, measure $Z$, independent shots", 32),
            VGroup(eq(r"N = 572", size=44),
                   label("exact power 0.901 at p = 0.16, level 0.05", 24, MUTED)).arrange(DOWN, buff=0.25),
            tex(r"fixed $N$: no interim looks", 34),
            eq(r"\text{reject } H_0:\ p \le 0.10 \text{ if } K \ge 38", size=36),
            tex(r"readout calibration; $X$ and $Y$ probes", 32),
            tex(r"every run, every deviation, code and seeds", 32),
        ]
        cur = None
        for i, (s, ct) in enumerate(zip(st, contents)):
            ct.move_to(panel_c)
            anims = [s[0].animate.set_stroke(VIOLET, 4).set_fill(VIOLET, 0.08)]
            if cur is None:
                anims.append(FadeIn(ct))
            else:
                anims.append(FadeOut(cur))
                anims.append(FadeIn(ct))
            self.play(*anims, run_time=0.9)
            self.wait(0.9)
            cur = ct
        lock = VGroup(*[st[i][0] for i in range(8)])
        frozen = label("stations 1 to 8 are frozen before any data", 26, VIOLET).move_to(np.array([3.6, -1.0, 0]))
        self.play(lock.animate.set_fill(VIOLET, 0.18), st[8][0].animate.set_stroke(AMBER, 4), FadeIn(frozen))
        self.wait(1.2)
        self.play(FadeOut(cur), FadeOut(frozen))

        # garden of forking paths
        head = label("Without a plan: forking paths", 28, INK, "BOLD").move_to(np.array([3.4, 2.5, 0]))
        self.play(Write(head))
        root = np.array([3.4, 1.7, 0])
        levels = 4
        tree = VGroup()
        leaves = [root]
        for d in range(levels):
            new = []
            dx = 2.6 / (2 ** d)
            for p in leaves:
                for sgn in (-1, 1):
                    q = p + np.array([sgn * dx / 2, -0.55, 0])
                    tree.add(Line(p, q, color=MUTED, stroke_width=2))
                    new.append(q)
            leaves = new
        dots = VGroup(*[Dot(q, radius=0.05, color=AMBER) for q in leaves])
        self.play(Create(tree), run_time=1.8)
        self.play(FadeIn(dots))
        cap = label("4 binary choices already give 16 analyses", 24, MUTED).move_to(np.array([3.4, -0.85, 0]))
        self.play(FadeIn(cap))
        f1 = eq(r"P(\text{some } p \le 0.05) = 1 - (1 - 0.05)^{10}", size=34).move_to(np.array([3.4, -1.75, 0]))
        f2 = eq(r"P(\text{some } p \le 0.05) = 0.401", size=34).move_to(f1)
        note = label("10 independent tests, each at level 0.05, H0 true", 24, MUTED).move_to(np.array([3.4, -2.55, 0]))
        self.play(Write(f1), FadeIn(note))
        self.play(TransformMatchingTex(f1, f2), run_time=1.3)
        chosen = VGroup()
        p = root
        for d in range(levels):
            dx = 2.6 / (2 ** d)
            q = p + np.array([-dx / 2 if d % 2 == 0 else dx / 2, -0.55, 0])
            chosen.add(Line(p, q, color=VIOLET, stroke_width=7))
            p = q
        end = label("preregistration fixes one path", 26, VIOLET).move_to(np.array([3.4, -3.3, 0]))
        self.play(Create(chosen), FadeIn(end), run_time=1.4)
        self.wait(2)


class OptionalStopping(Scene):
    def construct(self):
        title = label("Peeking until significant inflates false positives", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        ax = Axes(x_range=[0, 1000, 200], y_range=[-3, 4, 1], x_length=6.6, y_length=4.8,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24},
                  y_axis_config={"numbers_to_include": [-2, 0, 2, 4]}).move_to(np.array([-2.9, -0.45, 0]))
        ink_axes(ax)
        # x tick numbers sit below the plot (at the bottom of the y range) so the paths never cover them
        xnums = VGroup(*[label(f"{x}", 22, MUTED).move_to(ax.c2p(x, -3) + DOWN * 0.25) for x in (0, 500, 1000)])
        xl = label("shots n", 24, MUTED).next_to(xnums, DOWN, buff=0.08)
        yl = eq(r"Z_n", size=32).next_to(ax.y_axis, UP, buff=0.15)
        bound = DashedLine(ax.c2p(0, CZ), ax.c2p(1000, CZ), color=RED, stroke_width=3)
        blab = eq(r"z = 1.645", size=30, color=RED).next_to(ax.c2p(1000, CZ), UP, buff=0.12).shift(LEFT * 1.0)
        h0 = label("all 40 runs have H0 true: p = 0.10", 24, MUTED).next_to(ax, UP, buff=0.05).shift(RIGHT * 0.3)
        self.play(Create(ax), FadeIn(xnums), FadeIn(xl), FadeIn(yl), Create(bound), FadeIn(blab), FadeIn(h0))
        ns = 10 * np.arange(1, 101)
        t = ValueTracker(1)

        def path(i):
            def make():
                k = int(t.get_value())
                c = CROSS[i]
                stop = k if c is None else min(k, c + 1)
                pts = [ax.c2p(ns[j], float(np.clip(WALKS[i, j], -3, 4))) for j in range(max(stop, 2))]
                col = RED if (c is not None and k > c) else BLUE
                v = VMobject(stroke_color=col, stroke_width=2.2 if col == RED else 1.4, stroke_opacity=0.95 if col == RED else 0.55)
                v.set_points_as_corners(pts)
                return v
            return always_redraw(make)

        paths = VGroup(*[path(i) for i in range(len(WALKS))])
        counter = always_redraw(lambda: label(
            f"stopped as significant: {sum(1 for c in CROSS if c is not None and int(t.get_value()) > c)} of 40",
            26, RED).move_to(np.array([3.9, 2.4, 0])))
        self.add(paths, counter)
        self.play(t.animate.set_value(100), run_time=9, rate_func=linear)
        self.wait(0.5)
        r1 = label("look after every 10 shots: 11 of 40 crossed", 24, INK).move_to(np.array([3.9, 1.75, 0]))
        endline = Line(ax.c2p(1000, -3), ax.c2p(1000, 4), color=AMBER, stroke_width=4)
        r2 = label("one look at n = 1000: 2 of 40", 24, AMBER).move_to(np.array([3.9, 1.25, 0]))
        self.play(FadeIn(r1))
        self.play(Create(endline), FadeIn(r2))
        self.wait(1)

        # exact Gaussian false-positive rate against the number of looks
        cap = label("exact rate for K equally spaced looks", 24, MUTED).move_to(np.array([3.9, 0.45, 0]))
        base_y = -2.9
        bars = VGroup()
        labs = VGroup()
        for j, (K, v) in enumerate(zip(GK, GFPR)):
            x = 2.4 + 1.05 * j
            h = v / 0.32 * 2.6
            b = Rectangle(width=0.62, height=h, color=RED if K > 1 else BLUE, fill_opacity=0.65, stroke_width=1.5)
            b.move_to(np.array([x, base_y + h / 2, 0]))
            bars.add(b)
            labs.add(VGroup(label(f"K={K}", 22, MUTED).move_to(np.array([x, base_y - 0.3, 0])),
                            label(f"{v:.3f}", 24, INK).next_to(b, UP, buff=0.08)))
        baseline = Line(np.array([1.95, base_y, 0]), np.array([6.1, base_y, 0]), color=MUTED, stroke_width=2)
        self.play(FadeIn(cap), Create(baseline))
        for b, lb in zip(bars, labs):
            b.save_state()
            b.stretch(0.01, 1, about_edge=DOWN)
            self.add(b)
            self.play(b.animate.restore(), FadeIn(lb), run_time=0.7)
        self.wait(2.5)


class VilleBarrier(Scene):
    def construct(self):
        title = label("A test you may stop at any time: Ville's inequality", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        ax = Axes(x_range=[0, 1000, 200], y_range=[-12, 5, 4], x_length=6.0, y_length=4.9,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24},
                  x_axis_config={"numbers_to_include": [0, 500, 1000]},
                  y_axis_config={"numbers_to_include": [-12, -8, -4, 0, 4]}).move_to(np.array([-3.3, -0.5, 0]))
        ink_axes(ax)
        yl = eq(r"\log L_n", size=32).next_to(ax.y_axis, UP, buff=0.12)
        xl = label("shots n", 24, MUTED).next_to(ax, DOWN, buff=0.1)
        bar = DashedLine(ax.c2p(0, LOG20), ax.c2p(1000, LOG20), color=RED, stroke_width=3)
        blab = eq(r"\log 20", size=30, color=RED).next_to(ax.c2p(1000, LOG20), UP, buff=0.1).shift(LEFT * 0.5)
        self.play(Create(ax), FadeIn(yl), FadeIn(xl), Create(bar), FadeIn(blab))
        lr = eq(r"L_n = \prod_{i \le n} \Big(\tfrac{q_1}{q_0}\Big)^{x_i}\Big(\tfrac{1-q_1}{1-q_0}\Big)^{1-x_i}", size=32)
        lr.move_to(np.array([3.5, 2.3, 0]))
        qs = eq(r"q_0 = 0.05,\quad q_1 = 0.08", size=30, color=MUTED).next_to(lr, DOWN, buff=0.2)
        self.play(Write(lr), FadeIn(qs))
        ns = 10 * np.arange(1, 101)
        t = ValueTracker(2)

        def path(i):
            def make():
                k = int(t.get_value())
                c = V_CROSS[i]
                pts = [ax.c2p(ns[j], float(np.clip(LLR[i, j], -12, 5))) for j in range(max(k, 2))]
                col = RED if (c is not None and k > c) else VIOLET
                v = VMobject(stroke_color=col, stroke_width=2.4 if col == RED else 1.3, stroke_opacity=0.95 if col == RED else 0.5)
                v.set_points_as_corners(pts)
                return v
            return always_redraw(make)

        paths = VGroup(*[path(i) for i in range(len(LLR))])
        self.add(paths)
        self.play(t.animate.set_value(100), run_time=7, rate_func=linear)
        res = label("H0 true in all 40 runs: 1 of 40 reached 20", 24, INK).move_to(np.array([3.5, 1.05, 0]))
        self.play(FadeIn(res))
        steps = [
            r"\mathbb{E}[L_{\tau \wedge N}] \le L_0 = 1",
            r"\mathbb{E}[L_{\tau \wedge N}] \ge 20\, P(\tau \le N)",
            r"P(\tau \le N) \le 1/20",
            r"P(\sup_n L_n \ge 20) \le 0.05",
        ]
        cur = eq(steps[0], size=34).move_to(np.array([3.5, 0.0, 0]))
        why = ["optional stopping, supermartingale", "L is at least 20 once it has stopped", "combine the two lines",
               "let N grow: valid at every n at once"]
        wl = label(why[0], 24, MUTED).next_to(cur, DOWN, buff=0.25)
        self.play(Write(cur), FadeIn(wl))
        self.wait(1.2)
        for s, w in zip(steps[1:], why[1:]):
            nxt = eq(s, size=34).move_to(cur)
            nw = label(w, 24, MUTED).next_to(nxt, DOWN, buff=0.25)
            self.play(TransformMatchingTex(cur, nxt), Transform(wl, nw), run_time=1.3)
            self.wait(1.3)
            cur = nxt
        box = Rectangle(width=cur.width + 0.4, height=cur.height + 0.35, color=VIOLET, stroke_width=3).move_to(cur)
        self.play(Create(box))
        self.wait(2)


def wire(y, x0, x1, dashed=False, color=INK):
    return (DashedLine if dashed else Line)(np.array([x0, y, 0]), np.array([x1, y, 0]), color=color, stroke_width=3)


def gate(text, center, w=1.1, h=0.62, color=VIOLET, size=30):
    r = Rectangle(width=w, height=h, color=color, stroke_width=3, fill_color="#ffffff", fill_opacity=1).move_to(center)
    return VGroup(r, eq(text, size=size, color=color).move_to(center))


class MiniStudy(Scene):
    def construct(self):
        title = label("A simulated two-qubit causal study, end to end", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        yH, yA, yB = 2.0, 1.1, 0.2
        x0, x1 = -6.2, -0.6
        names = VGroup(eq("H", size=32, color=MUTED).move_to(np.array([x0 - 0.3, yH, 0])),
                       eq("A", size=32).move_to(np.array([x0 - 0.3, yA, 0])),
                       eq("B", size=32).move_to(np.array([x0 - 0.3, yB, 0])))
        wires = VGroup(wire(yH, x0, -3.3, dashed=True, color=MUTED), wire(yA, x0, x1), wire(yB, x0, x1))
        lat = label("latent bit", 22, MUTED).move_to(np.array([-4.9, yH + 0.4, 0]))
        do = gate(r"do(a)", np.array([-5.0, yA, 0]), w=1.2)
        b0 = label("starts in |0>", 22, MUTED).move_to(np.array([-5.0, yB - 0.42, 0]))
        flip = gate(r"c", np.array([-3.6, yB, 0]), w=0.7, color=AMBER)
        ctrl = VGroup(Dot(np.array([-3.6, yH, 0]), color=MUTED, radius=0.08),
                      Line(np.array([-3.6, yH, 0]), flip[0].get_top(), color=MUTED, stroke_width=3))
        swap = Rectangle(width=1.0, height=yA - yB + 0.62, color=VIOLET, stroke_width=3, fill_color="#ffffff",
                         fill_opacity=1).move_to(np.array([-2.1, (yA + yB) / 2, 0]))
        swl = eq(r"\theta", size=34, color=VIOLET).move_to(swap)
        meter = VGroup(Rectangle(width=0.7, height=0.55, color=INK, stroke_width=3, fill_color="#ffffff", fill_opacity=1),
                       label("Z", 24, INK)).move_to(np.array([-0.9, yB, 0]))
        self.play(FadeIn(names), Create(wires), FadeIn(lat), run_time=1.2)
        self.play(FadeIn(do), FadeIn(b0), FadeIn(flip), Create(ctrl), FadeIn(swap), FadeIn(swl), FadeIn(meter), run_time=1.4)
        legend = VGroup(
            tex(r"latent $H$ flips $B$ with chance $c = 0.30$", 28),
            tex(r"partial swap: $\sin^2\theta = s = 0.10$", 28),
            tex(r"randomized $a$ cuts any arrow into $A$", 28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(np.array([3.6, 1.6, 0]))
        self.play(FadeIn(legend), run_time=1.2)
        self.wait(1)
        d1 = eq(r"P(B{=}1 \mid do(1)) - P(B{=}1 \mid do(0))", size=32).move_to(np.array([2.9, 0.1, 0]))
        d2 = eq(r"\Big[\tfrac{c}{2} + \big(1 - \tfrac{c}{2}\big)s\Big] - \tfrac{c}{2}(1 - s)", size=32).move_to(d1)
        d3 = eq(r"\mathrm{ACE} = s = 0.10", size=36, color=VIOLET).move_to(d1)
        self.play(Write(d1))
        self.wait(0.6)
        self.play(TransformMatchingTex(d1, d2), run_time=1.3)
        self.wait(1)
        self.play(TransformMatchingTex(d2, d3), run_time=1.3)
        o1 = eq(r"\text{if } A \text{ copies } H:\ s + c(1-s) = 0.37", size=32, color=AMBER).move_to(np.array([2.9, -0.65, 0]))
        self.play(Write(o1))
        self.wait(1.5)

        # running estimates from the preregistered simulation
        self.play(FadeOut(VGroup(legend)), d3.animate.scale(0.85).move_to(np.array([3.2, 2.55, 0])),
                  o1.animate.scale(0.85).move_to(np.array([3.2, 1.95, 0])))
        ax = Axes(x_range=[0, 257, 50], y_range=[-0.1, 0.6, 0.1], x_length=5.4, y_length=2.9,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [0, 100, 200]},
                  y_axis_config={"numbers_to_include": [0, 0.2, 0.4]}).move_to(np.array([3.5, -1.2, 0]))
        ink_axes(ax)
        xl = label("shots per arm", 22, MUTED).next_to(ax, DOWN, buff=0.1)
        t1 = DashedLine(ax.c2p(0, 0.10), ax.c2p(257, 0.10), color=VIOLET, stroke_width=2)
        t2 = DashedLine(ax.c2p(0, 0.37), ax.c2p(257, 0.37), color=AMBER, stroke_width=2)
        self.play(Create(ax), FadeIn(xl), Create(t1), Create(t2))
        y0, y1, yo, h = ST["y0"], ST["y1"], ST["yo"], ST["h"]
        ns = np.arange(10, 258)
        run_i = np.array([y1[:n].mean() - y0[:n].mean() for n in ns])
        run_o = []
        for n in ns:
            hh, oo = h[:2 * n], yo[:2 * n]
            run_o.append(oo[hh].mean() - oo[~hh].mean())
        run_o = np.array(run_o)
        t = ValueTracker(11)

        def curve(vals, col):
            def make():
                k = int(t.get_value())
                v = VMobject(stroke_color=col, stroke_width=3.5)
                v.set_points_as_corners([ax.c2p(ns[j], float(np.clip(vals[j], -0.1, 0.6))) for j in range(min(k, len(ns)))])
                return v
            return always_redraw(make)

        ci = curve(run_i, VIOLET)
        co = curve(run_o, AMBER)
        self.add(ci, co)
        self.play(t.animate.set_value(len(ns)), run_time=7, rate_func=linear)
        res = VGroup(
            tex(rf"randomized: $\widehat{{\mathrm{{ACE}}}} = {ST['ace_hat']:.3f}$", 30, VIOLET),
            tex(rf"one-sided 95\% lower bound ${LB:.3f} > 0$", 28, VIOLET),
            tex(rf"observational contrast ${ST['obs_hat']:.3f}$", 30, AMBER),
            label(f"{ST['n_arm']} shots per arm, seed {M.STUDY_SEED}, simulated", 22, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(np.array([-3.4, -2.1, 0]))
        self.play(FadeIn(res), run_time=1.2)
        self.wait(2.5)
        _ = (Circle, CYAN, GRID, RIGHT)
