"""L1-09 Unknown is not the same as quantum: chances stack and never cancel; amplitudes can cancel.

The amplitude for each path comes from the lesson JSON; each one-path chance is that
amplitude squared. The two panels use separate scales (chance on the left, amplitude
on the right), so bar heights and arrow lengths are not meant to be compared.
"""
import pathlib
import sys
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Create, DashedLine, Dot, FadeIn, GrowArrow, GrowFromEdge, Indicate,
                   Line, Rectangle, Scene, VGroup, Write)

from qcai_style import AMBER, BLUE, CYAN, INK, MUTED, RED, VIOLET, label, params

LESSON = "L1-09"
CH = 5.0        # left panel: screen units per unit of chance
AU = 4.0        # right panel: screen units per unit of amplitude
BASE = -1.4     # left panel baseline (chance 0)
ZERO = -1.0     # right panel zero line (amplitude 0)


def numbers(p):
    a = Fraction(*p["amplitude"])
    c = a * a                       # chance from one path alone = amplitude squared
    return a, c, c + c, a - a, (a - a) * (a - a)


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    a, c, csum, asum, sq = numbers(L["animation"]["params"])
    return [f"{c} + {c} = {csum}", f"{a} up and {a} down add to {asum}", f"{asum} × {asum} = {sq}",
            "chances add; amplitudes can cancel"]


class ChancesAndAmplitudes(Scene):
    def construct(self):
        a, c, csum, asum, sq = numbers(params(LESSON))
        assert csum > 0 and asum == 0 and sq == 0

        title = label("Two ways to add", 40, INK, "BOLD").to_edge(UP, buff=0.3)
        divider = Line([0, 2.6, 0], [0, -2.9, 0], color=MUTED, stroke_width=2)
        lh = VGroup(label("Chances", 32, INK, "BOLD"), label("never below 0", 26, MUTED)).arrange(DOWN, buff=0.08)
        rh = VGroup(label("Amplitudes", 32, INK, "BOLD"), label("can point up or down", 26, MUTED)).arrange(DOWN, buff=0.08)
        lh.move_to([-3.6, 2.15, 0])
        rh.move_to([3.6, 2.15, 0]).align_to(lh, UP)
        self.play(Write(title), run_time=1.0)
        self.play(Create(divider), FadeIn(lh), FadeIn(rh), run_time=1.0)

        # ---- left: chance bars stack ----
        bx = -4.4
        floor = Line([bx - 1.0, BASE, 0], [bx + 1.0, BASE, 0], color=MUTED, stroke_width=3)
        zero_l = label("0", 26, MUTED).next_to(floor, LEFT, buff=0.12)
        h = float(c) * CH
        bar1 = Rectangle(width=1.0, height=h, fill_color=BLUE, fill_opacity=0.85, stroke_width=0)
        bar1.move_to([bx, BASE + h / 2, 0])
        bar2 = Rectangle(width=1.0, height=h, fill_color=CYAN, fill_opacity=0.85, stroke_width=0)
        bar2.move_to([bx, BASE + h * 1.5, 0])
        t1 = label(f"path 1: {c}", 28, BLUE).next_to(bar1, RIGHT, buff=0.25)
        t2 = label(f"path 2: {c}", 28, CYAN).next_to(bar2, RIGHT, buff=0.25)
        self.play(Create(floor), FadeIn(zero_l), run_time=0.6)
        self.play(GrowFromEdge(bar1, DOWN), FadeIn(t1), run_time=1.0)
        self.play(GrowFromEdge(bar2, DOWN), FadeIn(t2), run_time=1.0)
        lsum = label(f"{c} + {c} = {csum}", 30, INK).move_to([-3.6, -2.05, 0])
        lnot = label("never 0", 30, RED).move_to([-3.6, -2.6, 0])
        self.play(FadeIn(lsum), run_time=0.8)
        self.play(FadeIn(lnot), run_time=0.6)
        self.wait(1.8)

        # ---- right: amplitude arrows cancel ----
        zl = DashedLine([1.2, ZERO, 0], [6.4, ZERO, 0], color=MUTED, dash_length=0.1, stroke_width=2.5)
        zero_r = label("0", 26, MUTED).next_to(zl, LEFT, buff=0.12)
        L = float(a) * AU
        x1, x2 = 2.0, 2.9
        ar1 = Arrow([x1, ZERO, 0], [x1, ZERO + L, 0], buff=0, color=BLUE, stroke_width=7, tip_length=0.3,
                    max_stroke_width_to_length_ratio=10)
        ar2 = Arrow([x2, ZERO + L, 0], [x2, ZERO, 0], buff=0, color=VIOLET, stroke_width=7, tip_length=0.3,
                    max_stroke_width_to_length_ratio=10)
        join = DashedLine([x1, ZERO + L, 0], [x2, ZERO + L, 0], color=MUTED, dash_length=0.06, stroke_width=2)
        a1 = label(f"path 1: {a} up", 28, BLUE).move_to([0, ZERO + L * 0.75, 0]).align_to([3.5, 0, 0], LEFT)
        a2 = label(f"path 2: {a} down", 28, VIOLET).move_to([0, ZERO + L * 0.25, 0]).align_to([3.5, 0, 0], LEFT)
        self.play(Create(zl), FadeIn(zero_r), run_time=0.6)
        self.play(GrowArrow(ar1), FadeIn(a1), run_time=1.0)
        self.play(Create(join), GrowArrow(ar2), FadeIn(a2), run_time=1.2)
        end = Dot([x2, ZERO, 0], color=AMBER, radius=0.12)
        self.play(FadeIn(end), Indicate(end, color=AMBER), run_time=0.8)
        rsum = label(f"{a} up and {a} down add to {asum}", 30, INK).move_to([3.6, -2.05, 0])
        rsq = label(f"{asum} × {asum} = {sq}", 30, RED).move_to([3.6, -2.6, 0])
        self.play(FadeIn(rsum), run_time=0.8)
        self.wait(0.6)
        self.play(FadeIn(rsq), run_time=0.8)
        self.wait(1.2)

        bottom = label("chances add; amplitudes can cancel", 34, INK, "BOLD").to_edge(DOWN, buff=0.25)
        self.play(Write(bottom), run_time=1.4)
        self.wait(4.0)
