"""L1-03 Repeat and record: the fraction of heads wanders, then settles near one half.

The flips come from the course's tested simulation (qcai.science.trials) with the
seed stored in the lesson JSON, so the numbers on screen are the numbers in the text.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, UR, Axes, BackgroundRectangle, Create, DashedLine, Dot, FadeIn, FadeOut,
                   Indicate, MathTex, Scene, ValueTracker, VGroup, VMobject, Write, always_redraw, linear)

from qcai_style import AMBER, CYAN, GRID, INK, MUTED, VIOLET, label, params

LESSON = "L1-03"


def run(p):
    from qcai import science
    r = science.trials(0.5, p["flips"], p["seed"])
    trace = r["trace"]
    heads = [round(trace[k - 1] * k) for k in range(1, p["flips"] + 1)]
    return trace, heads


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    p = L["animation"]["params"]
    _, heads = run(p)
    return [f"{heads[n - 1]} out of {n}" for n in p["checkpoints"]]


class FrequencySettles(Scene):
    def construct(self):
        p = params(LESSON)
        trace, heads = run(p)
        N = p["flips"]

        title = label("Flip a fair coin, again and again", 40, INK, "BOLD").to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=1.2)

        ax = Axes(x_range=[0, N, 50], y_range=[0, 1, 0.25], x_length=10.5, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 26},
                  x_axis_config={"numbers_to_include": list(range(0, N + 1, 50))},
                  y_axis_config={"numbers_to_include": [0, 0.5, 1], "decimal_number_config": {"num_decimal_places": 1}}
                  ).shift(DOWN * 0.45)
        for axis in (ax.x_axis, ax.y_axis):
            axis.numbers.set_color(MUTED)
        xl = label("number of flips", 26, MUTED).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = label("fraction that were heads", 26, MUTED).rotate(1.5708).next_to(ax.y_axis, LEFT, buff=0.55)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.5)

        half = DashedLine(ax.c2p(0, 0.5), ax.c2p(N, 0.5), color=VIOLET, dash_length=0.12, stroke_width=3)
        half_lbl = VGroup(label("probability", 26, VIOLET), MathTex(r"=\tfrac{1}{2}", color=VIOLET, font_size=36)).arrange(RIGHT, buff=0.12)
        half_lbl.next_to(ax.c2p(N * 0.62, 0.5), UP, buff=0.5)
        self.play(Create(half), FadeIn(half_lbl), run_time=1.2)

        n = ValueTracker(1)

        def path():
            k = max(1, int(n.get_value()))
            m = VMobject(stroke_color=CYAN, stroke_width=4)
            pts = [ax.c2p(i, trace[i - 1]) for i in range(1, k + 1)]
            if len(pts) == 1:
                pts = pts * 2
            m.set_points_as_corners(pts)
            return m

        def counter():
            k = max(1, int(n.get_value()))
            return label(f"{heads[k - 1]} heads out of {k} flips", 30, INK).to_corner(UR, buff=0.5).shift(DOWN * 0.7)

        line = always_redraw(path)
        cnt = always_redraw(counter)
        self.add(line, cnt)
        self.play(n.animate.set_value(N), run_time=11, rate_func=linear)
        self.wait(0.4)

        marks = VGroup()
        for c in p["checkpoints"]:
            d = Dot(ax.c2p(c, trace[c - 1]), color=AMBER, radius=0.08)
            t = label(f"{heads[c - 1]} out of {c}", 24, INK)
            offset = {10: RIGHT * 0.9 + UP * 0.35, 20: RIGHT * 1.0 + UP * 0.55, 50: RIGHT * 0.6 + DOWN * 0.75}.get(c, DOWN * 0.8 + LEFT * 0.6)
            t.move_to(d.get_center() + offset)
            box = BackgroundRectangle(t, color="#ffffff", fill_opacity=0.92, buff=0.06)
            marks.add(VGroup(d, box, t))
        for m in marks:
            self.play(FadeIn(m, scale=0.8), Indicate(m[0], color=AMBER), run_time=0.9)

        self.play(FadeOut(cnt), run_time=0.4)
        msg = VGroup(label("Early on, the fraction jumps around.", 30, INK),
                     label("With more flips, it settles near one half, but not exactly.", 30, INK)).arrange(DOWN, buff=0.15)
        msg.set_color(INK).next_to(title, DOWN, buff=0.25)
        msg_box = BackgroundRectangle(msg, color="#ffffff", fill_opacity=0.95, buff=0.1)
        self.play(FadeIn(msg_box), FadeIn(msg), run_time=1.0)
        self.wait(2.2)
        _ = GRID
