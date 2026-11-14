"""L1-06 Look for a common cause: a rising scatter splits into two flat clusters by weather.

The 10 days are a fixed, made-up table stored in the lesson JSON (animation.params.days).
No randomness is used.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Create, DashedLine, Dot, FadeIn, FadeOut, GrowArrow, Line, RoundedRectangle,
                   Scene, VGroup, Write)

from qcai_style import BLUE, INK, MUTED, label, params

LESSON = "L1-06"
HOT = "#ea580c"


def groups(p):
    days = p["days"]
    hot = [d for d in days if d["hot"]]
    cool = [d for d in days if not d["hot"]]
    return days, hot, cool


def fit(ds):
    xs = [d["ice_cream"] for d in ds]
    ys = [d["swimmers"] for d in ds]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return min(xs), max(xs), lambda x: my + b * (x - mx)


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    days, hot, cool = groups(L["animation"]["params"])
    return [f"{len(days)} made-up days", f"{len(hot)} hot days", f"{len(cool)} cool days"]


class CommonCause(Scene):
    def construct(self):
        days, hot, cool = groups(params(LESSON))

        title = label("Does ice cream make people swim?", 40, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=1.0)

        ax = Axes(x_range=[0, 60, 20], y_range=[0, 60, 20], x_length=6.0, y_length=4.5,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 32, "numbers_to_include": [0, 20, 40, 60]}
                  ).move_to(LEFT * 2.3 + DOWN * 0.3)
        for axis in (ax.x_axis, ax.y_axis):
            axis.numbers.set_color(MUTED)
            for num in axis.numbers:
                num.scale(1.25)
        xl = label("ice creams sold", 26, MUTED).next_to(ax.x_axis, DOWN, buff=0.5)
        yl = label("people swimming", 26, MUTED).rotate(1.5708).next_to(ax.y_axis, LEFT, buff=0.5)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)

        n_days = label(f"{len(days)} made-up days", 32, INK, "BOLD").move_to(RIGHT * 4.0 + UP * 2.0)
        self.play(FadeIn(n_days), run_time=0.5)
        dots = {}
        for d in days:
            dots[d["day"]] = Dot(ax.c2p(d["ice_cream"], d["swimmers"]), radius=0.11, color=MUTED)
            self.play(FadeIn(dots[d["day"]], scale=0.5), run_time=0.22)
        rise = label("They rise together.", 30, INK).next_to(n_days, DOWN, buff=0.4)
        x0, x1, f = fit(days)
        trend = DashedLine(ax.c2p(x0 - 3, f(x0 - 3)), ax.c2p(x1 + 3, f(x1 + 3)), color=MUTED, stroke_width=4)
        self.play(FadeIn(rise), Create(trend), run_time=0.9)
        self.wait(1.2)

        # color by weather
        lh = VGroup(Dot(radius=0.11, color=HOT), label(f"{len(hot)} hot days", 30, HOT, "BOLD")).arrange(RIGHT, buff=0.2)
        lc = VGroup(Dot(radius=0.11, color=BLUE), label(f"{len(cool)} cool days", 30, BLUE, "BOLD")).arrange(RIGHT, buff=0.2)
        legend = VGroup(lh, lc).arrange(DOWN, buff=0.25, aligned_edge=LEFT).next_to(rise, DOWN, buff=0.5)
        self.play(*[dots[d["day"]].animate.set_color(HOT if d["hot"] else BLUE) for d in days], FadeIn(legend), FadeOut(trend), run_time=1.2)
        self.wait(0.8)

        lines = VGroup()
        for ds, col in ((hot, HOT), (cool, BLUE)):
            x0, x1, f = fit(ds)
            lines.add(Line(ax.c2p(x0 - 3, f(x0 - 3)), ax.c2p(x1 + 3, f(x1 + 3)), color=col, stroke_width=5))
        flat = VGroup(label("Inside each color,", 30, INK), label("the line is flat.", 30, INK)).arrange(DOWN, buff=0.1)
        flat.next_to(legend, DOWN, buff=0.5)
        self.play(*[Create(m) for m in lines], FadeIn(flat), run_time=1.4)
        self.wait(2.6)

        # common-cause diagram on the right
        self.play(FadeOut(n_days), FadeOut(rise), FadeOut(legend), FadeOut(flat), run_time=0.6)

        def box(lines_, col, pos):
            t = VGroup(*[label(s, 28, col, "BOLD") for s in lines_]).arrange(DOWN, buff=0.06)
            r = RoundedRectangle(width=t.width + 0.4, height=t.height + 0.35, corner_radius=0.15, stroke_color=col, stroke_width=3)
            return VGroup(r, t).move_to(pos)

        cause = box(["hot weather"], HOT, RIGHT * 4.3 + UP * 1.6)
        ice = box(["ice cream", "sold"], INK, RIGHT * 2.95 + DOWN * 1.3)
        swim = box(["people", "swimming"], INK, RIGHT * 5.65 + DOWN * 1.3)
        a1 = Arrow(cause.get_bottom(), ice.get_top(), color=HOT, buff=0.1, stroke_width=5)
        a2 = Arrow(cause.get_bottom(), swim.get_top(), color=HOT, buff=0.1, stroke_width=5)
        self.play(FadeIn(cause), run_time=0.6)
        self.play(FadeIn(ice), FadeIn(swim), GrowArrow(a1), GrowArrow(a2), run_time=1.2)
        note = label("A common cause", 30, INK, "BOLD").next_to(VGroup(ice, swim), DOWN, buff=0.45)
        self.play(FadeIn(note), run_time=0.6)
        self.wait(3.0)
