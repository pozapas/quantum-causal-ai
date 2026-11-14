"""L1-07 Track a wave: amplitude, wavelength, a dot that only bobs, and a wave half a cycle behind.

The wave is computed with numpy from the numbers in the lesson JSON (amplitude and
wavelength in grid squares), drawn on a grid of true squares, so every length on
screen can be counted.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Create, DashedLine, Dot, DoubleArrow, FadeIn,
                   FadeOut, Line, Scene, ValueTracker, VGroup, VMobject, Write, always_redraw, linear)

from qcai_style import BLUE, GRID, INK, MUTED, RED, VIOLET, label, params

LESSON = "L1-07"
HALF_COLS = 16   # grid squares on each side of the centre
HALF_ROWS = 4
Y0 = -0.45       # screen y of the middle line


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    p = L["animation"]["params"]
    return [f"{p['amplitude']} squares", f"{p['wavelength']} squares", "half a cycle behind"]


def height(x, t, p, shift=0.0):
    """Height in squares at position x (squares) and time t (s); shift in cycles (0.5 = half a cycle behind)."""
    return p["amplitude"] * np.sin(2 * np.pi * ((x - p["speed"] * t) / p["wavelength"] - shift))


class TrackAWave(Scene):
    def construct(self):
        p = params(LESSON)
        s = p["square"]
        A, lam = p["amplitude"], p["wavelength"]

        def P(x, y):  # grid squares -> screen point
            return np.array([x * s, Y0 + y * s, 0.0])

        title = label("Track a wave", 40, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=1.0)

        grid = VGroup(*[Line(P(x, -HALF_ROWS), P(x, HALF_ROWS), color=GRID, stroke_width=1.5)
                        for x in range(-HALF_COLS, HALF_COLS + 1)],
                      *[Line(P(-HALF_COLS, y), P(HALF_COLS, y), color=GRID, stroke_width=1.5)
                        for y in range(-HALF_ROWS, HALF_ROWS + 1)])
        mid = DashedLine(P(-HALF_COLS, 0), P(HALF_COLS, 0), color=MUTED, dash_length=0.12, stroke_width=2.5)
        mid_lbl = label("middle line", 26, MUTED).next_to(P(-6, 0), DOWN, buff=0.15)  # the wave is above the line here
        self.play(FadeIn(grid), Create(mid), FadeIn(mid_lbl), run_time=1.2)

        xs = np.linspace(-HALF_COLS, HALF_COLS, 641)
        t = ValueTracker(0.0)

        def wave(shift, color):
            def draw():
                ys = height(xs, t.get_value(), p, shift)
                m = VMobject(stroke_color=color, stroke_width=5)
                m.set_points_as_corners([P(x, y) for x, y in zip(xs, ys)])
                return m
            return draw

        blue = always_redraw(wave(0.0, BLUE))
        self.play(Create(blue), run_time=1.5)

        # a crest sits where the phase is a quarter cycle: x = lam/4 at t = 0
        cx = lam / 4
        crest = label("crest", 28, INK).next_to(P(cx - lam, A), UP, buff=0.12)
        trough = label("trough", 28, INK).next_to(P(cx - lam / 2, -A), DOWN, buff=0.12)
        self.play(FadeIn(crest), FadeIn(trough), run_time=0.8)

        amp_line = DoubleArrow(P(cx, 0), P(cx, A), buff=0, color=RED, stroke_width=4,
                               tip_length=0.16, max_tip_length_to_length_ratio=0.3)
        # the wave is above the middle line for a quarter wavelength each side of the crest, so the space below is free
        amp_lbl = VGroup(label("amplitude", 26, RED), label(f"{A} squares", 26, RED)).arrange(DOWN, buff=0.06)
        amp_lbl.next_to(P(cx, 0), DOWN, buff=0.15)
        self.play(Create(amp_line), FadeIn(amp_lbl), run_time=1.2)

        top = A + 1.2
        wl_line = DoubleArrow(P(cx, top), P(cx + lam, top), buff=0, color=VIOLET, stroke_width=4, tip_length=0.18)
        ticks = VGroup(DashedLine(P(cx, A), P(cx, top), color=VIOLET, dash_length=0.06, stroke_width=2),
                       DashedLine(P(cx + lam, A), P(cx + lam, top), color=VIOLET, dash_length=0.06, stroke_width=2))
        wl_lbl = label(f"wavelength: {lam} squares", 28, VIOLET).next_to(wl_line, UP, buff=0.1)
        self.play(Create(ticks), Create(wl_line), FadeIn(wl_lbl), run_time=1.2)
        self.wait(1.5)

        marks = VGroup(crest, trough, amp_line, amp_lbl, wl_line, ticks, wl_lbl, mid_lbl)
        self.play(FadeOut(marks), run_time=0.6)

        # a dot on the rope at a fixed place: its height comes from the same formula as the wave
        dx = p["dot_at"]
        track = DashedLine(P(dx, -A - 0.5), P(dx, A + 0.5), color=RED, dash_length=0.06, stroke_width=2)
        dot = always_redraw(lambda: Dot(P(dx, float(height(dx, t.get_value(), p))), color=RED, radius=0.12))
        msg1 = label("The wave moves along. The red dot only moves up and down.", 28, INK).next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(track), FadeIn(dot), FadeIn(msg1), run_time=0.8)
        arrow = Arrow(P(-6, A + 2.6), P(2, A + 2.6), buff=0, color=BLUE, stroke_width=5, tip_length=0.2)
        self.play(FadeIn(arrow), run_time=0.4)
        self.play(t.animate.set_value(p["travel_seconds"]), run_time=p["travel_seconds"], rate_func=linear)
        self.play(FadeOut(arrow), FadeOut(msg1), run_time=0.5)

        # second wave, half a cycle behind (the time is a whole number of cycles, so the picture matches t = 0)
        violet = always_redraw(wave(0.5, VIOLET))
        msg2 = label("A second wave, half a cycle behind", 28, VIOLET).next_to(title, DOWN, buff=0.3)
        self.play(FadeOut(track), FadeOut(dot), run_time=0.4)
        self.play(Create(violet), FadeIn(msg2), run_time=1.5)
        tx = cx + lam / 2  # a blue trough
        pair = DashedLine(P(tx, -A), P(tx, A), color=INK, dash_length=0.08, stroke_width=2.5)
        note = label("Its crests line up with the blue troughs.", 28, INK).to_edge(DOWN, buff=0.35)
        self.play(Create(pair), FadeIn(note), run_time=1.0)
        self.wait(1.2)
        self.play(FadeOut(pair), run_time=0.4)
        cycles = 2 * lam / p["speed"]
        self.play(t.animate.set_value(p["travel_seconds"] + cycles), run_time=cycles, rate_func=linear)
        self.wait(1.5)
        _ = (LEFT, DOWN)
