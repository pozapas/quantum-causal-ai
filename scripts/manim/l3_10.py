"""L3-10 Estimation, intervals, and repeated tests: three 3Blue1Brown-style scenes.

IntervalsCoverage  40 simulated studies, each with n = 100 trials of an event with true probability 0.3; each
                   draws its 95% Wald interval as a bar. Bars that miss 0.3 turn red (2 of 40 in this run);
                   the exact coverage of the procedure at n = 100, p = 0.3 is 0.950.
SamplingNarrows    the exact sampling distribution of the sample proportion for n = 25, 100, 400 (p = 0.5),
                   drawn as a density histogram: each fourfold increase in n halves the standard error
                   0.1 -> 0.05 -> 0.025.
MultipleTesting    20 tests of true null hypotheses at level 0.05: two come out "significant" in this run;
                   the chance of at least one false positive, 1 - 0.95^m, is traced as m grows (0.642 at
                   m = 20); the Bonferroni threshold 0.05/20 = 0.0025 removes both.
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

import numpy as np
from scipy.stats import binom

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Axes, Create, DashedLine, DecimalNumber, Dot, FadeIn, FadeOut, Integer,
                   Line, NumberLine, Rectangle, Scene, Square, SurroundingRectangle, TracedPath, Transform,
                   ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

Z = 1.96
P_TRUE, N, M_INT, SEED_INT = 0.3, 100, 40, 1


def wald(k, n):
    ph = k / n
    se = math.sqrt(ph * (1 - ph) / n)
    return ph - Z * se, ph + Z * se


def wald_coverage(n, p):
    ks = np.arange(n + 1)
    lo_hi = [wald(int(k), n) for k in ks]
    ok = np.array([lo <= p <= hi for lo, hi in lo_hi])
    return float(binom.pmf(ks, n, p)[ok].sum())


def studies():
    rng = np.random.default_rng(SEED_INT)
    return [int(k) for k in rng.binomial(N, P_TRUE, M_INT)]


KS = studies()
INTS = [wald(k, N) for k in KS]
MISS = sum(1 for lo, hi in INTS if not lo <= P_TRUE <= hi)
COV = wald_coverage(N, P_TRUE)
assert MISS == 2 and f"{COV:.3f}" == "0.950"

NS = (25, 100, 400)
SES = [math.sqrt(0.25 / n) for n in NS]
assert [round(s, 3) for s in SES] == [0.1, 0.05, 0.025]

ALPHA, MT, SEED_T = 0.05, 20, 5
PV = [float(v) for v in np.random.default_rng(SEED_T).uniform(0, 1, MT)]
FWER20 = 1 - (1 - ALPHA) ** MT
BONF = ALPHA / MT
assert sum(v < ALPHA for v in PV) == 2 and sum(v < BONF for v in PV) == 0
assert f"{FWER20:.3f}" == "0.642" and BONF == 0.0025


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [f"{COV:.3f}", "1 - 0.95^{m}", f"{FWER20:.3f}", "0.05/20 = 0.0025",
            "\\hat p \\pm 1.96\\sqrt{\\hat p(1-\\hat p)/n}", "0.1", "0.025"]


class IntervalsCoverage(Scene):
    def construct(self):
        title = label("A 95% interval is a procedure, judged by repetition", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.0)
        nl = NumberLine(x_range=[0.1, 0.5, 0.1], length=7.6, color=MUTED, include_numbers=False).move_to([-2.2, -3.25, 0])
        nums = VGroup(*[label(f"{v:.1f}", 24, MUTED).next_to(nl.n2p(v), DOWN, buff=0.12) for v in (0.1, 0.2, 0.3, 0.4, 0.5)])
        truth = DashedLine(nl.n2p(P_TRUE) + UP * 0.1, nl.n2p(P_TRUE) + UP * 5.85, color=INK, stroke_width=3)
        tl = eq(r"p = 0.3", size=32).next_to(truth, UP, buff=0.08)
        self.play(Create(nl), FadeIn(nums), Create(truth), Write(tl))
        recipe = VGroup(eq(r"\text{each study: } n = 100 \text{ trials}", size=32),
                        eq(r"\hat p \pm 1.96\sqrt{\hat p(1-\hat p)/n}", size=32, color=BLUE)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recipe.move_to([4.25, 1.9, 0])
        self.play(Write(recipe))
        counter = VGroup(label("missed:", 26, RED), Integer(0, font_size=34, color=RED), label(f"of {M_INT}", 26, INK)) \
            .arrange(RIGHT, buff=0.15).move_to([4.6, 0.55, 0])
        self.play(FadeIn(counter))
        bars = VGroup()
        missed = 0
        for i, (k, (lo, hi)) in enumerate(zip(KS, INTS)):
            y = -2.95 + 0.14 * i
            miss = not lo <= P_TRUE <= hi
            col = RED if miss else BLUE
            bar = Line(nl.n2p(lo) + UP * (y + 3.25), nl.n2p(hi) + UP * (y + 3.25), color=col, stroke_width=5 if miss else 3.5)
            dot = Dot(nl.n2p(k / N) + UP * (y + 3.25), color=col, radius=0.035)
            g = VGroup(bar, dot)
            bars.add(g)
            if miss:
                missed += 1
                self.play(Create(g), counter[1].animate.set_value(missed), run_time=0.5)
            else:
                self.play(Create(g), run_time=0.16)
        self.wait(0.5)
        boxes = VGroup(*[SurroundingRectangle(b, color=RED, buff=0.05) for b, (lo, hi) in zip(bars, INTS)
                         if not lo <= P_TRUE <= hi])
        self.play(Create(boxes))
        cov = VGroup(label("exact coverage of the recipe", 24, VIOLET),
                     eq(rf"n = 100,\ p = 0.3:\ {COV:.3f}", size=32, color=VIOLET)).arrange(DOWN, buff=0.12).move_to([4.3, -0.4, 0])
        self.play(Write(cov))
        n1 = label("each bar either contains p or not;", 24, MUTED).move_to([4.3, -1.5, 0])
        n2 = label("95% describes the recipe over", 24, MUTED).next_to(n1, DOWN, buff=0.12)
        n3 = label("many repetitions", 24, MUTED).next_to(n2, DOWN, buff=0.12)
        self.play(FadeIn(n1), FadeIn(n2), FadeIn(n3))
        self.wait(2.5)
        _ = (DecimalNumber, CYAN, AMBER, GRID, LEFT, RIGHT)


class SamplingNarrows(Scene):
    def construct(self):
        title = label("More data, narrower spread: the 1/√n law", 34, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.0)
        ax = Axes(x_range=[0.2, 0.8, 0.1], y_range=[0, 17, 4], x_length=8.0, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False}).move_to([-1.6, -0.75, 0])
        ticks = VGroup(*[label(f"{v:.1f}", 24, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.12) for v in (0.2, 0.4, 0.5, 0.6, 0.8)])
        xl = eq(r"\hat p", size=32).next_to(ax.c2p(0.8, 0), RIGHT, buff=0.2)
        yl = label("probability density", 24, MUTED).next_to(ax.c2p(0.2, 17), RIGHT, buff=0.2)
        self.play(Create(ax), FadeIn(ticks), Write(xl), FadeIn(yl))

        def hist(n, col):
            ks = np.arange(n + 1)
            pm = binom.pmf(ks, n, 0.5)
            w = 1 / n
            g = VGroup()
            for k, pr in zip(ks, pm):
                if pr < 2e-4 or not 0.2 <= k / n <= 0.8:
                    continue
                h = pr * n
                x0, x1 = ax.c2p(k / n - w / 2, 0), ax.c2p(k / n + w / 2, h)
                g.add(Rectangle(width=x1[0] - x0[0], height=max(x1[1] - x0[1], 1e-3), fill_color=col, fill_opacity=0.8,
                                stroke_width=0.6, stroke_color="#ffffff").move_to([(x0[0] + x1[0]) / 2, (x0[1] + x1[1]) / 2, 0]))
            return g

        def bracket(se, col, n):
            y = 0.45 * float(binom.pmf(n // 2, n, 0.5)) * n
            return VGroup(Line(ax.c2p(0.5 - Z * se, y), ax.c2p(0.5 + Z * se, y), color=col, stroke_width=7),
                          Line(ax.c2p(0.5 - Z * se, y - 0.4), ax.c2p(0.5 - Z * se, y + 0.4), color=col, stroke_width=5),
                          Line(ax.c2p(0.5 + Z * se, y - 0.4), ax.c2p(0.5 + Z * se, y + 0.4), color=col, stroke_width=5))

        se_f = eq(r"\text{SE} = \sqrt{p(1-p)/n}", size=34).move_to([4.6, 2.2, 0])
        self.play(Write(se_f))
        rows = VGroup()
        cols = (BLUE, VIOLET, RED)
        cur = None
        for i, (n, se, col) in enumerate(zip(NS, SES, cols)):
            h = hist(n, col)
            br = bracket(se, AMBER, n)
            row = eq(rf"n = {n}:\ \text{{SE}} = {se:g}", size=32, color=col).move_to([4.6, 1.2 - 0.7 * i, 0])
            rows.add(row)
            if cur is None:
                cur = VGroup(h, br)
                self.play(FadeIn(h, lag_ratio=0.02), Create(br), Write(row), run_time=1.8)
            else:
                new = VGroup(h, br)
                self.play(Transform(cur, new), Write(row), run_time=1.8)
            self.wait(0.9)
        rule = eq(r"n \times 4 \ \Rightarrow\ \text{SE} \div 2", size=36, color=INK).move_to([4.6, -1.15, 0])
        self.play(Write(rule))
        note = label("amber bar: 1.96 SE each side", 24, AMBER).move_to([4.5, -1.9, 0])
        self.play(FadeIn(note))
        self.wait(2.0)
        _ = (Dot, TracedPath, ValueTracker, always_redraw, linear, Square, CYAN, GRID, MUTED, DOWN, LEFT)


class MultipleTesting(Scene):
    def construct(self):
        title = label("Run enough tests and something will look significant", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.0)
        cells = VGroup()
        for i, pv in enumerate(PV):
            sq = Square(side_length=0.8, color=MUTED, stroke_width=2, fill_color="#e0f2fe", fill_opacity=1)
            txt = label(f"{pv:.3f}", 24, INK)
            cells.add(VGroup(sq, txt))
        cells.arrange_in_grid(rows=4, cols=5, buff=0.12).move_to([-4.1, 0.2, 0])
        for c in cells:
            c[1].move_to(c[0])
        head = label("20 tests, every null hypothesis true", 24, MUTED).next_to(cells, UP, buff=0.25)
        self.play(FadeIn(head), FadeIn(cells, lag_ratio=0.05), run_time=1.6)
        rule = eq(r"\text{flag if } p\text{-value} < 0.05", size=32).next_to(cells, DOWN, buff=0.3)
        self.play(Write(rule))
        hits = [c for c, pv in zip(cells, PV) if pv < ALPHA]
        self.play(*[c[0].animate.set_fill(RED, opacity=0.85) for c in hits], run_time=1.0)
        hl = label(f"{len(hits)} false positives", 26, RED).next_to(rule, DOWN, buff=0.2)
        self.play(FadeIn(hl))
        self.wait(0.6)

        ax = Axes(x_range=[0, 60, 10], y_range=[0, 1, 0.25], x_length=5.4, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False}).move_to([3.5, -0.3, 0])
        ticks = VGroup(*[label(str(v), 24, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.12) for v in (0, 20, 40, 60)],
                       *[label(t, 24, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.12) for v, t in ((0.5, "0.5"), (1, "1"))])
        xl = label("number of tests m", 24, MUTED).next_to(ax, DOWN, buff=0.4)
        f = eq(r"P(\text{at least one false positive}) = 1 - 0.95^{m}", size=32).next_to(ax, UP, buff=0.3)
        self.play(Create(ax), FadeIn(ticks), FadeIn(xl), Write(f))
        m = ValueTracker(0)
        dot = always_redraw(lambda: Dot(ax.c2p(m.get_value(), 1 - 0.95 ** m.get_value()), color=RED, radius=0.06))
        trace = TracedPath(dot.get_center, stroke_color=RED, stroke_width=4)
        self.add(trace, dot)
        self.play(m.animate.set_value(20), run_time=2.5, rate_func=linear)
        mark = DashedLine(ax.c2p(20, 0), ax.c2p(20, FWER20), color=INK, stroke_width=2)
        ml = eq(rf"m = 20:\ {FWER20:.3f}", size=32, color=RED).next_to(ax.c2p(20, FWER20), RIGHT, buff=0.35).shift(DOWN * 0.45)
        self.play(Create(mark), Write(ml))
        self.play(m.animate.set_value(60), run_time=2.5, rate_func=linear)
        self.wait(0.6)

        bonf = eq(r"\text{Bonferroni: flag if } p < 0.05/20 = 0.0025", size=32, color=VIOLET).move_to(rule).align_to(rule, LEFT)
        bonf.move_to([0, rule.get_center()[1], 0]).align_to([-6.2, 0, 0], LEFT)
        self.play(Transform(rule, bonf))
        self.play(*[c[0].animate.set_fill("#e0f2fe", opacity=1) for c in hits], run_time=1.0)
        hl2 = label("0 flagged: family error rate at most 0.05", 24, VIOLET).move_to(hl).align_to([-6.2, 0, 0], LEFT)
        self.play(Transform(hl, hl2))
        self.wait(2.5)
        _ = (Integer, DecimalNumber, Rectangle, FadeOut, SurroundingRectangle, BLUE, AMBER, CYAN, GRID, Line, NumberLine,
             Create, DOWN, RIGHT, Transform)
