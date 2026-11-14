import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # noqa: E401,E702
"""L2-03 Read plots without inventing causes: a scatter, its trend, a hidden common cause, and a risky extension.

The 12 made-up months (sunscreen bottles sold, sunburn cases) are stored in the lesson
JSON (animation.params). The trend line is a least-squares fit computed here; its
numbers are not shown on screen. No randomness is used.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Create, DashedLine, Dot, FadeIn, FadeOut, GrowArrow, Line,
                   RoundedRectangle, Scene, VGroup, Write)

from qcai_style import AMBER, BLUE, INK, MUTED, RED, VIOLET, label, params

LESSON = "L2-03"


def fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return lambda x: my + b * (x - mx)


def describe_words(p):
    return [f"direction: {p['direction']}", f"form: {p['form']}", f"strength: {p['strength']}"]


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    p = L["animation"]["params"]
    return [f"{len(p['sunscreen'])} made-up months"] + describe_words(p) + ["sunshine", "outside the data"]


class PlotNoCause(Scene):
    def construct(self):
        p = params(LESSON)
        xs, ys = p["sunscreen"], p["sunburn"]
        f = fit(xs, ys)
        xmax = p["x_max"]

        title = label(f"An imagined town: {len(xs)} made-up months", 36, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=1.0)

        ax = Axes(x_range=[0, xmax, 50], y_range=[0, p["y_max"], 10], x_length=6.6, y_length=5.0,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 28},
                  x_axis_config={"numbers_to_include": list(range(0, xmax + 1, 100))},
                  y_axis_config={"numbers_to_include": list(range(0, p["y_max"] + 1, 10))}).move_to(LEFT * 2.9 + DOWN * 0.35)
        for axis in (ax.x_axis, ax.y_axis):
            axis.numbers.set_color(MUTED)
            for nn in axis.numbers:
                nn.scale(1.2)
        xl = label("sunscreen bottles sold", 26, MUTED).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = label("sunburn cases", 26, MUTED).next_to(ax.y_axis, UP, buff=0.15).shift(RIGHT * 0.7)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)

        dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.08, color=BLUE) for x, y in zip(xs, ys)])
        self.play(FadeIn(dots, lag_ratio=0.25), run_time=2.4)
        x0, x1 = min(xs), max(xs)
        trend = Line(ax.c2p(x0, f(x0)), ax.c2p(x1, f(x1)), color=VIOLET, stroke_width=5)
        self.play(Create(trend), run_time=1.0)

        words = VGroup(*[label(w, 30, INK) for w in describe_words(p)]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        words.move_to(RIGHT * 3.9 + UP * 1.2)
        for w in words:
            self.play(FadeIn(w), run_time=0.5)
        self.wait(1.2)
        self.play(FadeOut(words), run_time=0.5)

        # Which way? A question mark between the variables, then a common cause.
        def box(text, col, pos):
            t = VGroup(*[label(s, 28, col, "BOLD") for s in text]).arrange(DOWN, buff=0.06)
            r = RoundedRectangle(width=t.width + 0.4, height=t.height + 0.35, corner_radius=0.15, stroke_color=col, stroke_width=3)
            return VGroup(r, t).move_to(pos)

        sc = box(["sunscreen", "sold"], INK, RIGHT * 2.3 + DOWN * 0.6)
        sb = box(["sunburn", "cases"], INK, RIGHT * 5.4 + DOWN * 0.6)
        q = label("?", 48, AMBER, "BOLD").move_to((sc.get_center() + sb.get_center()) / 2)
        self.play(FadeIn(sc), FadeIn(sb), run_time=0.6)
        self.play(FadeIn(q, scale=1.5), run_time=0.6)
        ask = label("Which causes which?", 28, INK).next_to(VGroup(sc, sb), DOWN, buff=0.4)
        self.play(FadeIn(ask), run_time=0.5)
        self.wait(1.0)

        sun = box(["sunshine"], AMBER, RIGHT * 3.85 + UP * 1.7)
        a1 = Arrow(sun.get_bottom(), sc.get_top(), color=AMBER, buff=0.1, stroke_width=5)
        a2 = Arrow(sun.get_bottom(), sb.get_top(), color=AMBER, buff=0.1, stroke_width=5)
        self.play(FadeIn(sun), run_time=0.6)
        self.play(GrowArrow(a1), GrowArrow(a2), FadeOut(ask), run_time=1.0)
        both = label("One cause can drive both.", 28, INK).next_to(VGroup(sc, sb), DOWN, buff=0.4)
        self.play(FadeIn(both), run_time=0.5)
        self.wait(2.2)
        self.play(*[FadeOut(m) for m in (sc, sb, q, sun, a1, a2, both)], run_time=0.6)

        # Extending the line far past the data
        edge = DashedLine(ax.c2p(x1, 0), ax.c2p(x1, p["y_max"]), color=MUTED, stroke_width=2, dash_length=0.1)
        ext = Line(ax.c2p(x1, f(x1)), ax.c2p(xmax, f(xmax)), color=RED, stroke_width=5)
        self.play(Create(edge), run_time=0.5)
        self.play(Create(ext), run_time=1.2)
        warn = VGroup(label("outside the data:", 30, RED, "BOLD"), label("no evidence here", 30, RED)).arrange(DOWN, buff=0.1)
        warn.move_to(RIGHT * 4.1 + UP * 0.6)
        self.play(FadeIn(warn), run_time=0.6)
        self.wait(3.0)
        _ = (UP, DOWN, LEFT, RIGHT)
