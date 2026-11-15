"""L3-07 Expectation and variance: three 3Blue1Brown-style scenes.

SeesawMean         the distribution P(X=0, 1, 2, 4) = 0.1, 0.4, 0.3, 0.2 as weights on a beam; the fulcrum slides,
                   the beam tilts by the net turning effect sum p(x - c) = mu - c, and balances at the mean 1.8.
VarianceSquares    the squared distances (x - mu)^2 drawn as squares, weighted and added: 1.56; then the shortcut
                   E[X^2] - mu^2 derived term by term, and sigma = 1.249 marked on the line.
SampleMeansSharpen exact distributions of the mean of n fair die rolls (n = 1, 2, 4, 16, 64): the center stays at 3.5
                   while the spread shrinks like 1.708 / sqrt(n).
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, WHITE, Axes, Brace, Create, DashedLine, DecimalNumber, FadeIn, FadeOut, Line,
                   Polygon, Rectangle, ReplacementTransform, Scene, Square, TransformMatchingTex, ValueTracker, VGroup,
                   Write, always_redraw, smooth)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

XS = [0, 1, 2, 4]
PS = [Fraction(1, 10), Fraction(4, 10), Fraction(3, 10), Fraction(2, 10)]
assert sum(PS) == 1
MU = sum(x * p for x, p in zip(XS, PS))                       # 9/5
EX2 = sum(x * x * p for x, p in zip(XS, PS))                  # 24/5
VAR = sum((x - MU) ** 2 * p for x, p in zip(XS, PS))          # 39/25
assert MU == Fraction(9, 5) and EX2 == Fraction(24, 5) and VAR == EX2 - MU ** 2 == Fraction(39, 25)
SD = math.sqrt(VAR)                                           # 1.2490
TERMS = [float((x - MU) ** 2 * p) for x, p in zip(XS, PS)]    # 0.324, 0.256, 0.012, 0.968
assert np.allclose(TERMS, [0.324, 0.256, 0.012, 0.968])

# a fair die
DIE_VAR = Fraction(35, 12)
assert sum(Fraction(k * k, 6) for k in range(1, 7)) - Fraction(7, 2) ** 2 == DIE_VAR
DIE_SD = math.sqrt(DIE_VAR)                                   # 1.7078


def mean_dist(n):
    """Exact distribution of the mean of n fair die rolls: values k/n and probabilities."""
    p = np.ones(6) / 6
    d = np.array([1.0])
    for _ in range(n):
        d = np.convolve(d, p)
    vals = (np.arange(len(d)) + n) / n
    return vals, d


for _n in (1, 4, 16, 64):
    v, d = mean_dist(_n)
    assert abs(d.sum() - 1) < 1e-12 and abs(v @ d - 3.5) < 1e-9
    assert abs(math.sqrt(((v - 3.5) ** 2) @ d) - DIE_SD / math.sqrt(_n)) < 1e-9


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["1.8", "1.56", f"{SD:.3f}", "E[X^2] - \\mu^2", "0.968", f"{DIE_SD / 4:.3f}", f"{DIE_SD:.3f}"]


class SeesawMean(Scene):
    def construct(self):
        title = label("The mean is the balance point", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        s, Y = 1.3, -1.0

        def X(x):
            return (x - 2.0) * s

        c = ValueTracker(0.8)

        def torque():
            return float(sum(float(p) * (x - c.get_value()) for x, p in zip(XS, PS)))

        def scene_group():
            beam = Line([X(-0.4), Y, 0], [X(4.4), Y, 0], color=INK, stroke_width=6)
            g = VGroup(beam)
            for x, p, col in zip(XS, PS, (BLUE, VIOLET, CYAN, AMBER)):
                h = float(p) * 4.5
                g.add(Rectangle(width=0.55, height=h, stroke_color=INK, stroke_width=1.5, fill_color=col, fill_opacity=0.8)
                      .move_to([X(x), Y + h / 2 + 0.04, 0]))
                g.add(eq(f"{float(p):.1f}", size=28, color=col).move_to([X(x), Y + h + 0.3, 0]))
            ang = -max(-0.28, min(0.28, 0.22 * torque()))
            g.rotate(ang, about_point=[X(c.get_value()), Y, 0])
            return g

        def fulcrum():
            cx = X(c.get_value())
            return Polygon([cx, Y - 0.05, 0], [cx - 0.35, Y - 0.75, 0], [cx + 0.35, Y - 0.75, 0], color=INK,
                           fill_color=MUTED, fill_opacity=0.6, stroke_width=2)

        ground = VGroup(Line([X(-0.8), Y - 0.75, 0], [X(4.8), Y - 0.75, 0], color=GRID, stroke_width=3),
                        *[eq(str(k), size=30, color=MUTED).move_to([X(k), Y - 1.05, 0]) for k in range(5)])
        grp = always_redraw(scene_group)
        ful = always_redraw(fulcrum)
        self.play(Create(ground), FadeIn(grp), FadeIn(ful))
        cap = label("weights: P(X = 0, 1, 2, 4) = 0.1, 0.4, 0.3, 0.2", 26, MUTED).move_to([0, 2.55, 0])
        self.play(FadeIn(cap))

        tl = eq(r"\sum_x p(x)\,(x - c) =", size=34).move_to([-1.3, -2.9, 0])
        tv = always_redraw(lambda: DecimalNumber(torque(), num_decimal_places=2, include_sign=True, font_size=36, color=RED)
                           .next_to(tl, RIGHT, buff=0.2))
        cl = eq(r"c =", size=34).move_to([-4.6, -2.9, 0])
        cv = always_redraw(lambda: DecimalNumber(c.get_value(), num_decimal_places=2, font_size=36, color=INK)
                           .next_to(cl, RIGHT, buff=0.15))
        self.play(Write(tl), FadeIn(tv), Write(cl), FadeIn(cv))
        self.wait(0.5)
        self.play(c.animate.set_value(3.0), run_time=3.5, rate_func=smooth)
        self.wait(0.4)
        self.play(c.animate.set_value(float(MU)), run_time=3.0, rate_func=smooth)
        self.wait(0.6)
        bal = label("level: net turning effect 0", 26, RED).next_to(tv, RIGHT, buff=0.4)
        self.play(FadeIn(bal))
        self.wait(0.6)
        self.play(FadeOut(cap))
        mean = eq(r"E[X] = 0(0.1) + 1(0.4) + 2(0.3) + 4(0.2) = 1.8", size=38).move_to([0, 2.55, 0])
        self.play(Write(mean))
        why = eq(r"\sum_x p(x)(x - c) = E[X] - c \;=\; 0 \iff c = E[X]", size=32, color=MUTED).move_to([0, 1.8, 0])
        self.play(Write(why))
        note = label("no single outcome equals 1.8", 26, MUTED).move_to([0, -3.6, 0])
        self.play(FadeIn(note))
        self.wait(2.0)


class VarianceSquares(Scene):
    def construct(self):
        title = label("Variance: the average squared distance from the mean", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        s, Y, X0 = 1.12, -2.0, -5.9

        def X(x):
            return X0 + x * s

        line = Line([X(-0.3), Y, 0], [X(4.3), Y, 0], color=MUTED, stroke_width=3)
        ticks = VGroup(*[VGroup(Line([X(k), Y - 0.08, 0], [X(k), Y + 0.08, 0], color=MUTED),
                                eq(str(k), size=28, color=MUTED).move_to([X(k), Y - 0.38, 0])) for k in range(5)])
        mu = float(MU)
        mline = DashedLine([X(mu), Y - 0.15, 0], [X(mu), Y + 2.9, 0], color=RED, stroke_width=3)
        ml = eq(r"\mu = 1.8", size=30, color=RED).next_to(mline, UP, buff=0.08)
        self.play(Create(line), FadeIn(ticks), Create(mline), Write(ml))

        cols = (BLUE, VIOLET, CYAN, AMBER)
        squares = VGroup()
        rows = VGroup()
        tx = 3.0
        key = label("side = distance to μ;  darker = more probable", 22, MUTED).move_to([X(2), -3.6, 0])
        self.play(FadeIn(key))
        head = eq(r"\text{outcome}:\ p \times (x - \mu)^2", size=30, color=MUTED).move_to([tx, 2.4, 0])
        self.play(Write(head))
        for i, (x, p, col) in enumerate(zip(XS, PS, cols)):
            side = abs(x - mu) * s
            sq = Square(side_length=side, stroke_color=col, stroke_width=3, fill_color=col, fill_opacity=1.2 * float(p))
            left = min(X(x), X(mu))
            sq.move_to([left + side / 2, Y + side / 2, 0])
            d2 = float((x - MU) ** 2)
            row = eq(rf"x = {x}:\ {float(p):.1f} \times {d2:.2f} = {TERMS[i]:.3f}", size=32, color=col).move_to([tx, 1.65 - 0.62 * i, 0])
            self.play(Create(sq), Write(row), run_time=1.1)
            squares.add(sq)
            rows.add(row)
        total = eq(r"\operatorname{Var}(X) = \sum_x p(x)(x - \mu)^2 = 1.56", size=34, color=INK).move_to([tx, -1.0, 0])
        self.play(Write(total))
        self.wait(1.0)

        # the shortcut, term by term
        self.play(FadeOut(rows), FadeOut(head), total.animate.move_to([tx, 2.4, 0]))
        steps = [r"E[(X - \mu)^2] = E[X^2 - 2\mu X + \mu^2]", r"E[(X - \mu)^2] = E[X^2] - 2\mu E[X] + \mu^2",
                 r"E[(X - \mu)^2] = E[X^2] - 2\mu^2 + \mu^2", r"E[(X - \mu)^2] = E[X^2] - \mu^2"]
        cur = eq(steps[0], size=32).move_to([tx, 1.4, 0])
        self.play(Write(cur))
        for st in steps[1:]:
            nxt = eq(st, size=32).move_to([tx, 1.4, 0])
            self.play(TransformMatchingTex(cur, nxt), run_time=1.2)
            cur = nxt
            self.wait(0.3)
        num = eq(r"= 4.8 - 1.8^2 = 4.8 - 3.24 = 1.56", size=32).move_to([tx, 0.6, 0])
        self.play(Write(num))
        sdl = eq(rf"\sigma = \sqrt{{1.56}} \approx {SD:.3f}", size=36, color=VIOLET).move_to([tx, -0.4, 0])
        self.play(Write(sdl))
        band = Line([X(mu - SD), Y - 0.75, 0], [X(mu + SD), Y - 0.75, 0], color=VIOLET, stroke_width=6)
        caps = VGroup(*[Line([X(mu + e * SD), Y - 0.9, 0], [X(mu + e * SD), Y - 0.6, 0], color=VIOLET, stroke_width=4) for e in (-1, 1)])
        bl = eq(r"\mu \pm \sigma", size=28, color=VIOLET).next_to(band, DOWN, buff=0.12)
        self.play(Create(band), Create(caps), Write(bl))
        units = label("variance has squared units; σ has the units of X", 24, MUTED).move_to([tx, -1.4, 0])
        self.play(FadeIn(units))
        self.wait(2.0)
        _ = (WHITE, Brace, LEFT, RIGHT, DOWN)


class SampleMeansSharpen(Scene):
    def construct(self):
        title = label("Averages of more rolls concentrate around 3.5", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        ax = Axes(x_range=[0.5, 6.5, 0.5], y_range=[0, 2, 0.5], x_length=8.4, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24,
                               "decimal_number_config": {"num_decimal_places": 1, "color": MUTED}}).move_to([-1.6, -0.55, 0])
        ax.x_axis.add_numbers([1, 2, 3, 4, 5, 6], num_decimal_places=0, color=MUTED)
        ax.y_axis.add_numbers([0.5, 1.0, 1.5, 2.0], num_decimal_places=1, color=MUTED)
        yl = label("probability per unit", 22, MUTED).next_to(ax.y_axis, UP, buff=0.15).shift(RIGHT * 0.9)
        xl = label("mean of n rolls", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.5)
        self.play(Write(title), Create(ax), FadeIn(yl), FadeIn(xl), run_time=1.4)
        mid = DashedLine(ax.c2p(3.5, 0), ax.c2p(3.5, 2), color=RED, stroke_width=2)
        self.play(Create(mid))
        tag = VGroup(label("exact distributions,", 22, MUTED), label("computed by convolution", 22, MUTED)).arrange(
            DOWN, aligned_edge=LEFT, buff=0.08).move_to([5.0, 2.1, 0])
        self.play(FadeIn(tag))

        def bars(n):
            v, d = mean_dist(n)
            w = 1.0 / n
            g = VGroup()
            for val, pr in zip(v, d):
                h = pr / w                                   # probability per unit of the mean
                if h < 1e-4:
                    continue
                lo, hi = ax.c2p(val - w / 2, 0), ax.c2p(val + w / 2, h)
                g.add(Rectangle(width=hi[0] - lo[0], height=hi[1] - lo[1], stroke_width=0.6 if n < 16 else 0,
                                stroke_color=WHITE, fill_color=VIOLET, fill_opacity=0.75).move_to((lo + hi) / 2))
            return g

        def readout(n):
            sd = DIE_SD / math.sqrt(n)
            return VGroup(eq(rf"n = {n}", size=36),
                          eq(r"\text{mean} = 3.5", size=32, color=RED),
                          eq(rf"\sigma/\sqrt{{n}} = {sd:.3f}", size=32, color=VIOLET)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([5.0, 0.6, 0])

        def spread(n):
            sd = DIE_SD / math.sqrt(n)
            yy = 1.9
            return VGroup(Line(ax.c2p(3.5 - sd, yy), ax.c2p(3.5 + sd, yy), color=VIOLET, stroke_width=5),
                          Line(ax.c2p(3.5 - sd, yy - 0.06), ax.c2p(3.5 - sd, yy + 0.06), color=VIOLET, stroke_width=4),
                          Line(ax.c2p(3.5 + sd, yy - 0.06), ax.c2p(3.5 + sd, yy + 0.06), color=VIOLET, stroke_width=4))

        ns = [1, 2, 4, 16, 64]
        b = bars(ns[0])
        r = readout(ns[0])
        sp = spread(ns[0])
        self.play(FadeIn(b), Write(r), Create(sp))
        sig = eq(rf"\sigma = \sqrt{{35/12}} \approx {DIE_SD:.3f}", size=30, color=MUTED).move_to([5.0, -1.4, 0])
        self.play(Write(sig))
        self.wait(1.0)
        for n in ns[1:]:
            b2, r2, sp2 = bars(n), readout(n), spread(n)
            self.play(ReplacementTransform(b, b2), ReplacementTransform(r, r2), ReplacementTransform(sp, sp2), run_time=1.8)
            b, r, sp = b2, r2, sp2
            self.wait(1.0)
        law = eq(r"\operatorname{Var}(\bar X_n) = \sigma^2/n", size=32, color=INK).move_to([5.0, -2.3, 0])
        self.play(Write(law))
        cond = label("(independent rolls)", 22, MUTED).next_to(law, DOWN, buff=0.12)
        self.play(FadeIn(cond))
        self.wait(2.0)
