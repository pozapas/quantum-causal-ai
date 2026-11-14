"""L2-09 Use vectors for two outcomes: probability vectors on a segment, state vectors on a circle.

All numbers come from the lesson JSON (animation.params). Real amplitudes only: the arrow at
angle t has amplitudes (cos t, sin t), so the chances in the standard measurement are
cos^2 t and sin^2 t, which always add to 1. The scene checks this arithmetic with asserts.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, DashedLine, Dot, FadeIn, FadeOut, Line, Rectangle,
                   Scene, ValueTracker, VGroup, Write, always_redraw, smooth)

from qcai_style import AMBER, BLUE, CYAN, INK, MUTED, VIOLET, label, params

LESSON = "L2-09"


def fmt(x):
    return f"{round(x, 2):g}"


def numbers(p):
    a0, a1 = p["amp"]
    s0, s1 = round(a0 * a0, 4), round(a1 * a1, 4)
    assert abs(s0 + s1 - 1) < 1e-9, "squares of amplitudes must add to 1"
    for d in p["pair_deg"]:
        t = math.radians(d)
        assert abs(math.cos(t) ** 2 - 0.5) < 1e-12 and abs(math.sin(t) ** 2 - 0.5) < 1e-12
    return a0, a1, s0, s1


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    p = L["animation"]["params"]
    a0, a1, s0, s1 = numbers(p)
    pv = [f"({fmt(q)}, {fmt(1 - q)})" for q in p["prob_points"]]
    return pv + [f"{fmt(s0)} + {fmt(s1)} = 1", "(1/√2, 1/√2)", "(1/√2, -1/√2)", "same chances"]


class TwoOutcomeVectors(Scene):
    def construct(self):
        p = params(LESSON)
        a0, a1, s0, s1 = numbers(p)
        q_start, q_end = p["prob_points"]

        # ---------- part 1: probability vectors live on the segment p0 + p1 = 1 ----------
        title = label("A probability vector (p0, p1)", 40, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.9)
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=4.6, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 28, "numbers_to_include": [0, 0.5, 1],
                               "decimal_number_config": {"num_decimal_places": 1}}).move_to(LEFT * 2.6 + DOWN * 0.5)
        for axis in (ax.x_axis, ax.y_axis):
            axis.numbers.set_color(MUTED)
        xl = label("p0", 28, MUTED).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = label("p1", 28, MUTED).next_to(ax.y_axis, LEFT, buff=0.5)
        seg = Line(ax.c2p(1, 0), ax.c2p(0, 1), color=VIOLET, stroke_width=6)
        rule = label("p0 + p1 = 1", 30, VIOLET, "BOLD").move_to([3.2, 1.5, 0])
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
        self.play(Create(seg), FadeIn(rule), run_time=1.0)

        q = ValueTracker(q_start)
        dot = always_redraw(lambda: Dot(ax.c2p(q.get_value(), 1 - q.get_value()), radius=0.12, color=AMBER))
        coords = always_redraw(lambda: label(f"({q.get_value():.1f}, {1 - q.get_value():.1f})", 34, AMBER, "BOLD")
                               .move_to([3.2, 0.5, 0]))
        coin = label("fair coin", 28, MUTED).move_to([3.2, -0.3, 0])
        self.play(FadeIn(dot), FadeIn(coords), FadeIn(coin), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(coin), run_time=0.3)
        self.play(q.animate.set_value(q_end), run_time=1.6)
        both = label("Both entries from 0 to 1, adding to 1.", 28, INK).move_to([3.2, -0.3, 0])
        self.play(FadeIn(both), run_time=0.6)
        self.wait(1.2)
        dot.clear_updaters(); coords.clear_updaters()
        self.play(*[FadeOut(m) for m in (ax, xl, yl, seg, rule, dot, coords, both, title)], run_time=0.7)

        # ---------- part 2: a state vector (a0, a1) lives on the circle a0^2 + a1^2 = 1 ----------
        title2 = label("A qubit state vector (a0, a1)", 40, INK, "BOLD").to_edge(UP, buff=0.35)
        R = 2.3
        O = LEFT * 3.4 + DOWN * 0.45
        circ = Circle(radius=R, color=MUTED, stroke_width=3).move_to(O)
        xa = Line(O + LEFT * (R + 0.3), O + RIGHT * (R + 0.3), color=MUTED, stroke_width=2)
        ya = Line(O + DOWN * (R + 0.3), O + UP * (R + 0.3), color=MUTED, stroke_width=2)
        xal = label("a0", 26, MUTED).next_to(xa, RIGHT, buff=0.1)
        yal = label("a1", 26, MUTED).next_to(ya, UP, buff=0.08)
        self.play(Write(title2), Create(circ), FadeIn(xa), FadeIn(ya), FadeIn(xal), FadeIn(yal), run_time=1.2)

        t = ValueTracker(math.atan2(a1, a0))
        H = 3.0                 # bar height for chance 1
        bx, base = 2.2, -3.0    # stacked bar position (x of centre, baseline y)

        def vec():
            th = t.get_value()
            return Arrow(O, O + R * (RIGHT * math.cos(th) + UP * math.sin(th)), buff=0, color=BLUE, stroke_width=6,
                         tip_length=0.25, max_stroke_width_to_length_ratio=10)

        def bars():
            th = t.get_value()
            c0, c1 = math.cos(th) ** 2, math.sin(th) ** 2
            b0 = Rectangle(width=1.0, height=max(c0 * H, 1e-3), fill_color=CYAN, fill_opacity=0.9, stroke_width=0)
            b0.move_to([bx, base + c0 * H / 2, 0])
            b1 = Rectangle(width=1.0, height=max(c1 * H, 1e-3), fill_color=VIOLET, fill_opacity=0.9, stroke_width=0)
            b1.move_to([bx, base + c0 * H + c1 * H / 2, 0])
            l0 = label(f"chance of 0: {c0:.2f}", 26, CYAN, "BOLD").move_to([bx + 2.55, base + 0.5, 0])
            l1 = label(f"chance of 1: {c1:.2f}", 26, VIOLET, "BOLD").move_to([bx + 2.55, base + H - 0.5, 0])
            amp = label(f"a0 = {math.cos(th):.2f}    a1 = {math.sin(th):.2f}", 28, BLUE, "BOLD").move_to([bx + 1.9, 2.25, 0])
            return VGroup(b0, b1, l0, l1, amp)

        top = DashedLine([bx - 0.8, base + H, 0], [bx + 0.8, base + H, 0], color=INK, stroke_width=3)
        one = label("total 1", 24, INK).next_to(top, LEFT, buff=0.15)
        arrow_m = always_redraw(vec)
        bar_m = always_redraw(bars)
        self.play(FadeIn(arrow_m), FadeIn(bar_m), Create(top), FadeIn(one), run_time=1.0)
        sq = label("chance = amplitude squared", 26, INK).move_to([bx + 1.9, 1.7, 0])
        self.play(FadeIn(sq), run_time=0.6)
        start = t.get_value()
        self.play(t.animate.set_value(math.radians(p["sweep_deg"])), run_time=2.4, rate_func=smooth)
        neg = label("a0 can be negative", 26, MUTED).next_to(sq, DOWN, buff=0.15)
        self.play(FadeIn(neg), run_time=0.5)
        self.play(t.animate.set_value(start), run_time=2.0, rate_func=smooth)
        arrow_m.clear_updaters(); bar_m.clear_updaters()
        eq = label(f"{fmt(s0)} + {fmt(s1)} = 1", 30, INK, "BOLD").next_to(neg, DOWN, buff=0.25)
        self.play(FadeIn(eq), run_time=0.7)
        self.wait(1.4)

        # ---------- part 3: two different states, same chances ----------
        self.play(FadeOut(arrow_m), FadeOut(bar_m), FadeOut(sq), FadeOut(neg), FadeOut(eq), run_time=0.6)
        d1, d2 = [math.radians(d) for d in p["pair_deg"]]
        arr1 = Arrow(O, O + R * (RIGHT * math.cos(d1) + UP * math.sin(d1)), buff=0, color=BLUE, stroke_width=6, tip_length=0.25)
        arr2 = Arrow(O, O + R * (RIGHT * math.cos(d2) + UP * math.sin(d2)), buff=0, color=AMBER, stroke_width=6, tip_length=0.25)
        n1 = label("(1/√2, 1/√2)", 26, BLUE, "BOLD").next_to(arr1.get_end(), UP + RIGHT, buff=0.08)
        n2 = label("(1/√2, -1/√2)", 26, AMBER, "BOLD").next_to(arr2.get_end(), DOWN + RIGHT, buff=0.08)
        self.play(Create(arr1), FadeIn(n1), Create(arr2), FadeIn(n2), run_time=1.2)

        def pair_bars(x, col):
            b0 = Rectangle(width=0.9, height=0.5 * H, fill_color=CYAN, fill_opacity=0.9, stroke_width=0)
            b0.move_to([x, base + 0.25 * H, 0])
            b1 = Rectangle(width=0.9, height=0.5 * H, fill_color=VIOLET, fill_opacity=0.9, stroke_width=0)
            b1.move_to([x, base + 0.75 * H, 0])
            frame = Rectangle(width=0.9, height=H, stroke_color=col, stroke_width=5).move_to([x, base + H / 2, 0])
            return VGroup(b0, b1, frame)

        pb1, pb2 = pair_bars(1.3, BLUE), pair_bars(2.5, AMBER)
        half = label("1/2 and 1/2", 26, INK).move_to([1.9, base - 0.4, 0])
        self.play(FadeOut(top), FadeOut(one), FadeIn(pb1), FadeIn(pb2), FadeIn(half), run_time=1.0)
        msg = VGroup(label("same chances,", 30, INK, "BOLD"), label("different states", 30, INK, "BOLD"),
                     label("Another measurement", 26, MUTED), label("can tell them apart.", 26, MUTED)
                     ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).next_to(pb2, RIGHT, buff=0.4)
        self.play(FadeIn(msg), run_time=0.9)
        self.wait(3.0)
