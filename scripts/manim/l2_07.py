"""L2-07 Read a causal graph: chain, fork and collider, then a collider made visible by selection.

The applicants' two traits come from the course's seeded generator (qcai.science.rng) with the
seed, count, score range and admission threshold stored in the lesson JSON (animation.params).
The two traits are drawn independently; the downward trend appears only among the admitted.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Create, DashedLine, Dot, FadeIn, FadeOut, GrowArrow, Line,
                   RoundedRectangle, Scene, VGroup, Write)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, VIOLET, label, params

LESSON = "L2-07"


def data(p):
    """Seeded applicants: (talent, hard work), each from low to high, rounded to 0.1."""
    from qcai import science
    r = science.rng(p["seed"])
    span = p["high"] - p["low"]
    pts = [(round(p["low"] + span * r(), 1), round(p["low"] + span * r(), 1)) for _ in range(p["n"])]
    admitted = [q for q in pts if q[0] + q[1] > p["threshold"]]
    return pts, admitted


def slope(pts):
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    b = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)
    return mx, my, b


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    p = L["animation"]["params"]
    pts, admitted = data(p)
    return [f"{len(pts)} made-up applicants", f"{len(admitted)} admitted", f"above {p['threshold']}"]


def node(text, col):
    t = label(text, 26, col, "BOLD")
    r = RoundedRectangle(width=t.width + 0.35, height=t.height + 0.3, corner_radius=0.12, stroke_color=col, stroke_width=3)
    return VGroup(r, t)


def arrow(a, b, col=MUTED):
    return Arrow(a.get_center(), b.get_center(), buff=0.42, color=col, stroke_width=5, tip_length=0.22,
                 max_tip_length_to_length_ratio=0.3)


class CausalGraphShapes(Scene):
    def flow(self, starts, ends, col):
        """Dots travel along arrows to show which way influence runs."""
        dots = [Dot(s.get_center(), radius=0.1, color=col) for s in starts]
        self.add(*dots)
        self.play(*[d.animate.move_to(e.get_center()) for d, e in zip(dots, ends)], run_time=0.9)
        self.play(*[FadeOut(d) for d in dots], run_time=0.2)

    def construct(self):
        p = params(LESSON)
        pts, admitted = data(p)
        assert len(admitted) > 10

        title = label("Three shapes of a causal graph", 40, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=1.0)

        # chain (left column, top to bottom)
        cx = -4.6
        rain, road, traffic = node("rain", BLUE), node("wet road", BLUE), node("slow traffic", BLUE)
        rain.move_to([cx, 1.6, 0]); road.move_to([cx, 0.0, 0]); traffic.move_to([cx, -1.6, 0])
        a1, a2 = arrow(rain, road, BLUE), arrow(road, traffic, BLUE)
        h1 = label("Chain", 32, BLUE, "BOLD").move_to([cx, -2.75, 0])
        self.play(FadeIn(rain), FadeIn(road), FadeIn(traffic), GrowArrow(a1), GrowArrow(a2), FadeIn(h1), run_time=1.0)
        self.flow([rain], [road], BLUE)
        self.flow([road], [traffic], BLUE)

        # fork (middle column)
        fx = 0.0
        summer, ice, burn = node("summer", VIOLET), node("ice cream", VIOLET), node("sunburn", VIOLET)
        summer.move_to([fx, 1.6, 0]); ice.move_to([fx - 1.25, -0.9, 0]); burn.move_to([fx + 1.25, -0.9, 0])
        b1, b2 = arrow(summer, ice, VIOLET), arrow(summer, burn, VIOLET)
        h2 = label("Fork", 32, VIOLET, "BOLD").move_to([fx, -2.75, 0])
        self.play(FadeIn(summer), FadeIn(ice), FadeIn(burn), GrowArrow(b1), GrowArrow(b2), FadeIn(h2), run_time=1.0)
        self.flow([summer, summer], [ice, burn], VIOLET)

        # collider (right column)
        kx = 4.6
        tal, work, adm = node("talent", AMBER), node("hard work", AMBER), node("admitted", AMBER)
        tal.move_to([kx - 1.2, 1.6, 0]); work.move_to([kx + 1.2, 1.6, 0]); adm.move_to([kx, -0.9, 0])
        c1, c2 = arrow(tal, adm, AMBER), arrow(work, adm, AMBER)
        h3 = label("Collider", 32, AMBER, "BOLD").move_to([kx, -2.75, 0])
        self.play(FadeIn(tal), FadeIn(work), FadeIn(adm), GrowArrow(c1), GrowArrow(c2), FadeIn(h3), run_time=1.0)
        self.flow([tal, work], [adm, adm], AMBER)
        self.wait(1.2)

        graphs = VGroup(rain, road, traffic, a1, a2, h1, summer, ice, burn, b1, b2, h2, tal, work, adm, c1, c2, h3)
        new_title = label("Choosing by a collider can create a pattern", 36, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(FadeOut(graphs), FadeOut(title), FadeIn(new_title), run_time=0.9)

        lo, hi = p["low"], p["high"]
        ax = Axes(x_range=[0, hi, 2], y_range=[0, hi, 2], x_length=5.4, y_length=5.0,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 28, "numbers_to_include": list(range(0, hi + 1, 2))}
                  ).move_to(LEFT * 2.9 + DOWN * 0.45)
        for axis in (ax.x_axis, ax.y_axis):
            axis.numbers.set_color(MUTED)
        xl = label("talent score", 26, MUTED).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = label("hard work score", 26, MUTED).rotate(1.5708).next_to(ax.y_axis, LEFT, buff=0.45)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)

        dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.055, color=BLUE) for x, y in pts])
        n_lbl = label(f"{len(pts)} made-up applicants", 30, INK, "BOLD").move_to([3.6, 2.0, 0])
        n_sub = label("Talent and hard work are unrelated.", 26, MUTED).next_to(n_lbl, DOWN, buff=0.2)
        self.play(FadeIn(dots, lag_ratio=0.02), FadeIn(n_lbl), run_time=2.0)
        self.play(FadeIn(n_sub), run_time=0.6)
        self.wait(1.4)

        # admission line: talent + hard work = threshold
        t = p["threshold"]
        x_a, x_b = t - hi, hi  # where the line meets the top and right edges of the plot
        cut = DashedLine(ax.c2p(x_a, hi), ax.c2p(x_b, t - x_b), color=AMBER, stroke_width=4, dash_length=0.12)
        rule = label(f"Admit if the total is above {t}.", 28, AMBER, "BOLD").next_to(n_sub, DOWN, buff=0.45)
        self.play(Create(cut), FadeIn(rule), run_time=1.2)
        keep = set(admitted)
        self.play(*[d.animate.set_color(GRID) for d, q in zip(dots, pts) if q not in keep],
                  *[d.animate.set_color(CYAN).scale(1.25) for d, q in zip(dots, pts) if q in keep], run_time=1.2)
        a_lbl = label(f"{len(admitted)} admitted", 30, CYAN, "BOLD").next_to(rule, DOWN, buff=0.45)
        self.play(FadeIn(a_lbl), run_time=0.6)
        self.wait(0.8)

        mx, my, b = slope(admitted)
        xs = [x for x, _ in admitted]
        x0, x1 = min(xs), max(xs)
        trend = Line(ax.c2p(x0, my + b * (x0 - mx)), ax.c2p(x1, my + b * (x1 - mx)), color=INK, stroke_width=5)
        msg = VGroup(label("Among the admitted,", 28, INK), label("less talent goes with", 28, INK),
                     label("more hard work.", 28, INK)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        msg.next_to(a_lbl, DOWN, buff=0.45)
        self.play(Create(trend), FadeIn(msg), run_time=1.4)
        self.wait(3.0)
        _ = lo
