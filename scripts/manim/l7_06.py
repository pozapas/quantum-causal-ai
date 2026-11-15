"""L7-06 Sample complexity and resource accounting: four scenes.

HoeffdingBand        200 independent sample means at each N (outcomes +-1, mean 0.2) against the Hoeffding and
                     Chebyshev bands for delta = 0.05; then 400 running-mean paths, of which 11 percent leave
                     the fixed-N band somewhere: the guarantee is for a fixed N, not for peeking.
HoeffdingDerivation  Markov -> independence -> Hoeffding's lemma -> optimize s -> 2 exp(-N eps^2 / 2) -> N >= 738.
LedgerVanishes       Grover on N = 2^20 items: 804 queries against 1,048,575; with a computable oracle the gap
                     survives, with an unstructured classical table the loading cost N erases it.
NoisyHeisenberg      Fisher information per query k e^{-2 gamma k} for k sequential queries per shot: the optimum
                     k = 1/(2 gamma) and the constant-factor gain 1/(2 e gamma) that replaces Heisenberg scaling.
Numbers come from qcai/lessonfigs/l7_06.py and are checked against the lesson text by facts().
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Axes, Create, DashedLine, Dot, FadeIn, FadeOut, Line, Rectangle, Scene,
                   TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label
from qcai.lessonfigs import l7_06 as M

FIXED_OUT, EVER_OUT = 0.0025, 0.1125     # band_exit_stats() with its defaults (checked in the scene)


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["738", "2000", r"2e^{-N\varepsilon^2/2}", "1,048,575", "804", r"k^\star = \frac{1}{2\gamma}",
            r"\frac{Q}{2e\gamma}", "11 percent"]


def axes_with_labels(x_range, y_range, x_length, y_length, xticks, yticks, xlab=None, ylab=None, size=22):
    ax = Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length,
              axis_config={"color": MUTED, "include_tip": False})
    labs = VGroup()
    for x in xticks:
        labs.add(label((xlab or "{:g}".format)(x), size, MUTED).next_to(ax.c2p(x, y_range[0]), DOWN, buff=0.12))
    for y in yticks:
        labs.add(label((ylab or "{:g}".format)(y), size, MUTED).next_to(ax.c2p(x_range[0], y), LEFT, buff=0.12))
    return ax, labs


def polyline(pts, color, width=4):
    return VGroup(*[Line(a, b, color=color, stroke_width=width) for a, b in zip(pts[:-1], pts[1:])])


# ---- scene 1 ----------------------------------------------------------------------------------
class HoeffdingBand(Scene):
    def construct(self):
        title = label("A fixed-N guarantee: independent means stay in the band", 30, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        # x: log10 N from 1 to 4; y: error (mean - mu) from -0.7 to 0.7, stored with offset 0.7
        ax, labs = axes_with_labels([1, 4, 1], [0, 1.4, 0.35], 9.0, 4.6, [1, 2, 3, 4], [0, 0.35, 0.7, 1.05, 1.4],
                                    xlab=lambda x: f"{10 ** x:,.0f}", ylab=lambda y: f"{y - 0.7:+.2f}".replace("+0.00", "0"))
        VGroup(ax, labs).move_to(DOWN * 0.35 + RIGHT * 0.3)

        def P(lgn, err):
            return ax.c2p(lgn, err + 0.7)

        xl = label("samples N (log scale)", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.5)
        yl = eq(r"\bar X_N - \mu", size=28).next_to(ax, LEFT, buff=0.95)
        self.play(Create(ax), FadeIn(labs), FadeIn(xl), FadeIn(yl))
        lg = np.linspace(1, 4, 120)
        hb = M.band_hoeffding(10 ** lg, M.DELTA)
        cb = M.band_chebyshev(10 ** lg, M.DELTA)
        hu = polyline([P(a, min(b, 0.7)) for a, b in zip(lg, hb)], VIOLET)
        hd = polyline([P(a, -min(b, 0.7)) for a, b in zip(lg, hb)], VIOLET)
        cu = polyline([P(a, min(b, 0.7)) for a, b in zip(lg, cb)], AMBER, 3)
        cd = polyline([P(a, -min(b, 0.7)) for a, b in zip(lg, cb)], AMBER, 3)
        k1 = eq(r"\pm\sqrt{2\ln(2/\delta)/N}", size=28, color=VIOLET)
        k2 = eq(r"\pm\sqrt{1/(\delta N)}", size=28, color=AMBER)
        keys = VGroup(k1, k2).arrange(RIGHT, buff=0.6).next_to(title, DOWN, buff=0.15)
        self.play(Create(hu), Create(hd), Create(cu), Create(cd), FadeIn(keys), run_time=1.6)

        means = M.mean_paths(200, 10000, seed=5)
        cloud = VGroup()
        self.add(cloud)
        readout = None
        for n in (30, 100, 300, 1000, 3000, 10000):
            errs = means[:, n - 1] - M.MU
            out = int(np.sum(np.abs(errs) >= M.band_hoeffding(n, M.DELTA)))
            dots = VGroup(*[Dot(P(math.log10(n) + 0.012 * ((i % 9) - 4), float(np.clip(e, -0.7, 0.7))), radius=0.025,
                                color=BLUE).set_opacity(0.6) for i, e in enumerate(errs)])
            new = eq(rf"N = {n:,}:\ {out}\ \text{{of }} 200\ \text{{outside}}", size=28, color=INK).to_corner(DOWN + RIGHT, buff=0.25)
            anims = [FadeIn(dots)]
            if readout is not None:
                anims.append(FadeOut(readout))
            self.play(*anims, FadeIn(new), run_time=0.8)
            cloud.add(dots)
            readout = new
        mark = DashedLine(P(math.log10(M.N_H), -0.7), P(math.log10(M.N_H), 0.7), color=RED)
        mt = eq(r"\varepsilon = 0.1:\ N = 738\ \ (\text{Chebyshev: } 2000)", size=28, color=RED).to_corner(DOWN + LEFT, buff=0.25)
        self.play(Create(mark), Write(mt))
        self.wait(1.2)

        # optional stopping: running means
        fixed, ever = M.band_exit_stats()
        assert abs(fixed - FIXED_OUT) < 1e-12 and abs(ever - EVER_OUT) < 1e-12
        self.play(*[FadeOut(d) for d in cloud.submobjects], FadeOut(readout), FadeOut(mark), FadeOut(mt))
        self.remove(cloud)
        paths = M.mean_paths(400, 10000, seed=11)
        idx = np.unique(np.round(np.geomspace(10, 10000, 70)).astype(int)) - 1
        exits = np.abs(paths[:, idx] - M.MU) >= M.band_hoeffding(idx + 1, M.DELTA)
        show = list(np.where(exits.any(axis=1))[0][:12]) + list(np.where(~exits.any(axis=1))[0][:12])
        lines = VGroup()
        for i in show:
            col = RED if exits[i].any() else MUTED
            lines.add(polyline([P(math.log10(j + 1), float(np.clip(paths[i, j] - M.MU, -0.7, 0.7))) for j in idx], col, 2))
        self.play(Create(lines), run_time=2.5)
        msg = VGroup(label("peeking at a running mean is not a fixed N:", 24, INK),
                     label(f"{EVER_OUT * 100:.0f} percent of 400 paths leave the band somewhere, against δ = 5 percent", 24, RED)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).next_to(title, DOWN, buff=0.12)
        self.play(FadeOut(keys), FadeIn(msg))
        self.wait(2.5)
        _ = (Rectangle, GRID, CYAN, linear, ValueTracker, always_redraw)


# ---- scene 2 ----------------------------------------------------------------------------------
class HoeffdingDerivation(Scene):
    def construct(self):
        title = label("Where the bound comes from", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        steps = [
            (eq(r"\Pr\big[S_N - N\mu \ge N\varepsilon\big]", r"\le", r"e^{-sN\varepsilon}\,\mathbb{E}\,e^{s(S_N - N\mu)}", size=36),
             "Markov's inequality applied to exp(s(S − Nμ)), for any s > 0"),
            (eq(r"\Pr\big[S_N - N\mu \ge N\varepsilon\big]", r"\le", r"e^{-sN\varepsilon}\prod_{i=1}^{N}\mathbb{E}\,e^{s(X_i - \mu)}", size=36),
             "independence"),
            (eq(r"\Pr\big[S_N - N\mu \ge N\varepsilon\big]", r"\le", r"e^{-sN\varepsilon + N s^2 (b-a)^2/8}", size=36),
             "Hoeffding's lemma, for X in [a, b]"),
            (eq(r"\Pr\big[S_N - N\mu \ge N\varepsilon\big]", r"\le", r"e^{-2N\varepsilon^2/(b-a)^2}", size=36),
             "choose s = 4ε/(b - a)²"),
        ]
        cur, note = None, None
        for m, why in steps:
            m.move_to(UP * 1.6)
            w = label(why, 24, MUTED).next_to(m, DOWN, buff=0.3)
            if cur is None:
                self.play(Write(m), FadeIn(w))
            else:
                self.play(TransformMatchingTex(cur, m), FadeOut(note), FadeIn(w), run_time=1.5)
            cur, note = m, w
            self.wait(0.7)
        two = eq(r"[a, b] = [-1, 1],\ \text{two-sided:}\quad \Pr\big[|\bar X_N - \mu| \ge \varepsilon\big] \le 2e^{-N\varepsilon^2/2}", size=34, color=VIOLET)
        two.move_to(DOWN * 0.2)
        self.play(Write(two))
        nN = eq(r"2e^{-N\varepsilon^2/2} \le \delta", r"\iff", r"N \ge \frac{2}{\varepsilon^2}\ln\frac{2}{\delta}", size=36)
        nN.move_to(DOWN * 1.5)
        self.play(Write(nN))
        num = eq(rf"\varepsilon = 0.1,\ \delta = 0.05:\quad N \ge 200\ln 40 \approx {200 * math.log(40):.1f} \;\Rightarrow\; N = 738", size=34, color=RED)
        num.move_to(DOWN * 2.7)
        self.play(Write(num))
        self.wait(2.5)


# ---- scene 3 ----------------------------------------------------------------------------------
class LedgerVanishes(Scene):
    def construct(self):
        title = label("A quadratic speedup, until the data must be loaded", 30, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        task = label("find the one marked item among N = 2^20 = 1,048,576", 24, MUTED).next_to(title, DOWN, buff=0.2)
        self.play(FadeIn(task))
        # log10 bars
        ax, labs = axes_with_labels([0, 3, 1], [0, 7, 1], 5.2, 4.0, [], [0, 2, 4, 6], ylab=lambda y: f"10^{y:g}" if y else "1")
        VGroup(ax, labs).move_to(LEFT * 3.6 + DOWN * 0.7)
        self.play(Create(ax), FadeIn(labs))

        def bar(xc, val, color):
            h = ax.c2p(0, math.log10(val))[1] - ax.c2p(0, 0)[1]
            r = Rectangle(width=1.1, height=h, fill_color=color, fill_opacity=0.75, stroke_color=INK, stroke_width=1)
            return r.move_to(ax.c2p(xc, 0), aligned_edge=DOWN)

        cl = bar(0.9, M.CLASSICAL_WORST, AMBER)
        qu = bar(2.1, M.K_GROVER, VIOLET)
        cn = label("classical", 22, AMBER).next_to(ax.c2p(0.9, 0), DOWN, buff=0.15)
        qn = label("quantum", 22, VIOLET).next_to(ax.c2p(2.1, 0), DOWN, buff=0.15)
        cv = label("1,048,575", 22, INK).next_to(cl, UP, buff=0.08)
        qv = label("804", 22, INK).next_to(qu, UP, buff=0.08)
        self.play(FadeIn(cl), FadeIn(qu), FadeIn(cn), FadeIn(qn), FadeIn(cv), FadeIn(qv))

        rows = VGroup(
            eq(r"\text{queries: } N - 1 = 1{,}048{,}575\ \text{(worst case)}", size=28, color=AMBER),
            eq(r"\text{queries: } \lfloor \tfrac{\pi}{4\theta} \rfloor = 804,\ \ \sin\theta = 2^{-10}", size=28, color=VIOLET),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 3.0 + UP * 1.3)
        self.play(Write(rows))
        self.wait(0.6)
        a = VGroup(label("Access model A: f is a circuit we can run", 24, INK),
                   eq(r"\text{cost} \approx \text{queries} \times (c_f + \text{a few gates})", size=28),
                   label("the quadratic gap survives", 24, BLUE)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        a.next_to(rows, DOWN, buff=0.45).align_to(rows, LEFT)
        self.play(FadeIn(a))
        self.wait(1.2)
        self.play(FadeOut(a))
        b = VGroup(label("Access model B: items in a classical table", 24, INK),
                   eq(r"\text{building the oracle reads all } N \text{ entries}", size=28),
                   eq(r"804 + 1{,}048{,}576 > 1{,}048{,}575", size=28, color=RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        b.next_to(rows, DOWN, buff=0.45).align_to(rows, LEFT)
        self.play(FadeIn(b))
        qu2 = bar(2.1, M.K_GROVER + M.N_ITEMS, VIOLET)
        qv2 = label("1,049,380", 22, INK).next_to(qu2, UP, buff=0.08)
        self.play(qu.animate.become(qu2), FadeOut(qv), FadeIn(qv2), run_time=1.6)
        end = label("same task, same algorithm: the access model decides the advantage", 24, RED).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(end))
        self.wait(2.5)


# ---- scene 4 ----------------------------------------------------------------------------------
class NoisyHeisenberg(Scene):
    def construct(self):
        title = label("Coherent queries beat repetition, until dephasing", 30, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        model = eq(r"P(0 \mid \varphi) = \tfrac12\big(1 + e^{-\gamma k}\cos k\varphi\big),\qquad F_{\text{shot}} \le k^2 e^{-2\gamma k}", size=30)
        model.next_to(title, DOWN, buff=0.25)
        self.play(Write(model))
        ax, labs = axes_with_labels([0, 3.7, 1], [0, 3.7, 1], 6.0, 4.0, [0, 1, 2, 3], [0, 1, 2, 3],
                                    xlab=lambda x: f"{10 ** x:,.0f}", ylab=lambda y: f"{10 ** y:,.0f}")
        VGroup(ax, labs).move_to(LEFT * 2.9 + DOWN * 1.1)
        xl = label("queries per shot k", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.5)
        yl = label("Fisher information per query", 22, MUTED).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        self.play(Create(ax), FadeIn(labs), FadeIn(xl), FadeIn(yl))
        lk = np.linspace(0, 3.7, 160)

        def P(lgk, val):
            return ax.c2p(lgk, math.log10(max(val, 1.0)))

        ideal = polyline([P(a, 10 ** a) for a in lk], MUTED, 3)
        il = label("no dephasing: k", 22, MUTED).next_to(P(2.9, 10 ** 2.9), LEFT, buff=0.2)
        self.play(Create(ideal), FadeIn(il))
        g = ValueTracker(0.1)
        curve = always_redraw(lambda: polyline([P(a, M.fisher_per_query(10 ** a, g.get_value())) for a in lk], VIOLET, 4))
        peak = always_redraw(lambda: Dot(P(math.log10(1 / (2 * g.get_value())), 1 / (2 * math.e * g.get_value())), color=RED, radius=0.08))
        rd = always_redraw(lambda: label(f"γ = {g.get_value():.4f}:  k* = {1 / (2 * g.get_value()):.0f},  F/Q = {1 / (2 * math.e * g.get_value()):.1f}",
                                         26, VIOLET).move_to(RIGHT * 3.6 + UP * 1.4))
        self.add(curve, peak, rd)
        self.play(g.animate.set_value(0.001), run_time=6, rate_func=lambda t: t)
        self.play(g.animate.set_value(M.GAMMA), run_time=2)
        self.remove(rd)
        rd2 = eq(rf"\gamma = 0.01:\ k^\star = 50,\ F/Q = {M.F_OPT:.1f}", size=28, color=VIOLET).move_to(RIGHT * 3.6 + UP * 1.4)
        self.add(rd2)
        d1 = eq(r"F_{\text{tot}} = \frac{Q}{k}\cdot k^2 e^{-2\gamma k} = Q\,k\,e^{-2\gamma k}", size=30).move_to(RIGHT * 3.5 + UP * 0.4)
        d2 = eq(r"k^\star = \frac{1}{2\gamma},\qquad F_{\max} = \frac{Q}{2e\gamma}", size=30, color=RED).move_to(RIGHT * 3.5 + DOWN * 0.7)
        d3 = eq(r"\delta\varphi \ge \sqrt{2e\gamma/Q}", size=30).move_to(RIGHT * 3.5 + DOWN * 1.8)
        self.play(Write(d1))
        self.play(Write(d2))
        self.play(Write(d3))
        msg = VGroup(label("still 1/√Q: dephasing turns Heisenberg", 22, RED),
                     label("scaling into a constant factor", 22, RED)).arrange(DOWN, buff=0.08).move_to(RIGHT * 3.5 + DOWN * 2.85)
        self.play(FadeIn(msg))
        self.wait(2.5)
        _ = (linear, CYAN, AMBER, BLUE, GRID)
