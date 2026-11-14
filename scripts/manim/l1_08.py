"""L1-08 Combine waves, then square: heights add point by point, brightness is the total amplitude squared.

Waves A and B are computed with numpy from the lesson JSON; the bottom row is drawn
from a + b on the same sample points, with the same vertical scale, so the drawn sum
is exactly the pointwise sum of the two drawn waves. The brightness bar is
(largest |a + b| over whole wavelengths) squared.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, BackgroundRectangle, Create, DashedLine, Dot, FadeIn, FadeOut, Line,
                   Rectangle, Scene, ValueTracker, VGroup, VMobject, Write, always_redraw, smooth)

from qcai_style import AMBER, BLUE, INK, MUTED, VIOLET, label, params

LESSON = "L1-08"
X0 = -5.0                          # screen x of position 0
ROWS = {"A": 2.2, "B": 0.85, "S": -1.2}
U = 0.4                            # screen units per unit of amplitude, the same for all three rows
BAR_Y0, BAR_U = -2.0, 0.85         # brightness axis: screen y of 0, screen units per unit of brightness
AXIS_X, BAR_X = 3.9, 4.55


def cases(p):
    """(amplitude of the total, brightness) for one wave, two in step, two half a cycle apart."""
    A = p["amplitude"]
    return [(A, A * A), (2 * A, (2 * A) ** 2), (0, 0)]


def fmt(v):
    return f"{v:g}"


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    p = L["animation"]["params"]
    one, both, none = cases(p)
    out = [f"amplitude {fmt(a)} gives brightness {fmt(b)}" for a, b in (one, both, none)]
    out.append(f"{fmt(both[1] / one[1])} times one wave, not {fmt(both[0] / one[0])} times")
    return out


def waves(p, xs, b_scale, phase):
    """Heights of A, B and their sum at positions xs (squares); phase in cycles (0.5 = half a cycle behind)."""
    A, lam = p["amplitude"], p["wavelength"]
    a = A * np.sin(2 * np.pi * xs / lam)
    b = b_scale * A * np.sin(2 * np.pi * (xs / lam - phase))
    return a, b, a + b


class AddThenSquare(Scene):
    def construct(self):
        p = params(LESSON)
        s, lam, A = p["square"], p["wavelength"], p["amplitude"]
        xs = np.arange(0, 3 * lam + lam / 8 + 1e-9, lam / 64)   # includes every crest and trough exactly
        full = xs <= 3 * lam                                       # whole wavelengths, for the bar
        bs, ph = ValueTracker(0.0), ValueTracker(0.0)
        one, both, none = cases(p)

        # sanity: the bar must read exactly 4 in step and 0 half a cycle apart
        assert abs(np.max(np.abs(waves(p, xs, 1, 0)[2][full])) ** 2 - both[1]) < 1e-9
        assert np.max(np.abs(waves(p, xs, 1, 0.5)[2][full])) ** 2 < 1e-9

        def P(row, x, h):
            return np.array([X0 + x * s, ROWS[row] + h * U, 0.0])

        title = label("Add the heights, then square", 40, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)

        mids = VGroup(*[DashedLine(P(r, xs[0], 0), P(r, xs[-1], 0), color=MUTED, dash_length=0.1, stroke_width=2)
                        for r in ROWS])
        names = VGroup(label("wave A", 26, BLUE).move_to([-6.2, ROWS["A"], 0]),
                       label("wave B", 26, VIOLET).move_to([-6.2, ROWS["B"], 0]),
                       label("A + B", 26, INK).move_to([-6.2, ROWS["S"], 0]))

        def curve(idx, row, color):
            def draw():
                h = waves(p, xs, bs.get_value(), ph.get_value())[idx]
                m = VMobject(stroke_color=color, stroke_width=4)
                m.set_points_as_corners([P(row, x, y) for x, y in zip(xs, h)])
                return m
            return draw

        # B starts at zero size, so at first the sum row is exactly wave A
        wa = always_redraw(curve(0, "A", BLUE))
        wb = always_redraw(curve(1, "B", VIOLET))
        ws = always_redraw(curve(2, "S", INK))
        self.play(FadeIn(mids), FadeIn(names), Create(wa), Create(wb), Create(ws), run_time=1.5)

        # brightness panel
        top = both[1]
        axis = Line([AXIS_X, BAR_Y0, 0], [AXIS_X, BAR_Y0 + top * BAR_U, 0], color=MUTED, stroke_width=3)
        base = Line([AXIS_X, BAR_Y0, 0], [BAR_X + 0.6, BAR_Y0, 0], color=MUTED, stroke_width=3)
        ticks = VGroup(*[label(str(k), 26, MUTED).move_to([AXIS_X - 0.3, BAR_Y0 + k * BAR_U, 0])
                         for k in range(0, int(top) + 1)])
        head = VGroup(label("brightness", 28, INK, "BOLD"), label("amplitude × amplitude", 26, MUTED)).arrange(DOWN, buff=0.1)
        head.move_to([4.9, 2.3, 0])
        ref = DashedLine([AXIS_X, BAR_Y0 + one[1] * BAR_U, 0], [BAR_X + 0.6, BAR_Y0 + one[1] * BAR_U, 0],
                         color=AMBER, dash_length=0.08, stroke_width=3)
        ref_lbl = label("one wave", 26, AMBER).next_to(ref, RIGHT, buff=0.1)

        def bar():
            total = waves(p, xs, bs.get_value(), ph.get_value())[2][full]
            v = float(np.max(np.abs(total))) ** 2
            h = max(v * BAR_U, 0.001)
            return Rectangle(width=0.7, height=h, fill_color=AMBER, fill_opacity=0.85, stroke_width=0
                             ).move_to([BAR_X, BAR_Y0 + h / 2, 0])

        b = always_redraw(bar)
        self.play(FadeIn(head), Create(axis), Create(base), FadeIn(ticks), run_time=1.0)
        self.add(b)

        def say(*lines, color=INK):
            g = VGroup(*[label(t, 28, color) for t in lines]).arrange(DOWN, buff=0.1)
            return g.to_edge(DOWN, buff=0.3).shift(LEFT * 1.6)

        m1 = say(f"amplitude {fmt(one[0])} gives brightness {fmt(one[1])}")
        self.play(FadeIn(m1), Create(ref), FadeIn(ref_lbl), run_time=1.0)
        self.wait(1.0)

        # wave B grows in step; the sum row follows automatically
        self.play(FadeOut(m1), bs.animate.set_value(1.0), run_time=2.5, rate_func=smooth)

        mx = p["marker_at"]

        def marker():
            hs = [float(h[0]) for h in waves(p, np.array([mx]), bs.get_value(), ph.get_value())]
            g = VGroup(DashedLine(P("A", mx, 1.6), P("S", mx, -2.2), color=MUTED, dash_length=0.07, stroke_width=2))
            for row, h, col in zip("ABS", hs, (BLUE, VIOLET, INK)):
                g.add(Dot(P(row, mx, h), color=col, radius=0.08))
            return g

        def height_labels():
            hs = [float(h[0]) for h in waves(p, np.array([mx]), bs.get_value(), ph.get_value())]
            g = VGroup()
            for row, h, col in zip("ABS", hs, (BLUE, VIOLET, INK)):
                if abs(h) < 1e-9:
                    t, side = "0", UP
                else:
                    t, side = (f"{fmt(abs(h))} up", UP) if h > 0 else (f"{fmt(abs(h))} down", DOWN)
                lbl = label(t, 26, col).next_to(P(row, mx, h), side, buff=0.12)
                g.add(BackgroundRectangle(lbl, color="#ffffff", fill_opacity=0.9, buff=0.04), lbl)
            return g

        mk = always_redraw(marker)
        hl = height_labels()
        self.play(FadeIn(mk), FadeIn(hl), run_time=1.0)
        m2 = say(f"amplitude {fmt(both[0])} gives brightness {fmt(both[1])}",
                 f"{fmt(both[1] / one[1])} times one wave, not {fmt(both[0] / one[0])} times")
        self.play(FadeIn(m2), run_time=0.8)
        self.wait(2.2)

        # slide B to half a cycle behind
        m3 = say("Now slide wave B half a cycle behind ...", color=VIOLET)
        self.play(FadeOut(hl), FadeOut(m2), FadeIn(m3), run_time=0.6)
        self.play(ph.animate.set_value(0.5), run_time=p["slide_seconds"], rate_func=smooth)
        hl2 = height_labels()
        m4 = say(f"amplitude {fmt(none[0])} gives brightness {fmt(none[1])}")
        self.play(FadeIn(hl2), FadeOut(m3), FadeIn(m4), run_time=0.8)
        self.wait(2.0)
        m5 = say("Add the heights first. Then square.")
        self.play(FadeOut(m4), FadeIn(m5), run_time=0.8)
        self.wait(2.0)
        _ = RIGHT
