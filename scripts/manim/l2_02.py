import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # noqa: E401,E702
"""L2-02 Functions map inputs to outputs: a function machine, two mapping diagrams, then residuals.

The rule h(t) = 2t + 5, the made-up measured heights and the made-up birth months are
stored in the lesson JSON (animation.params). No randomness is used.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Create, Cross, Dot, Ellipse, FadeIn, FadeOut, GrowArrow, Line,
                   RoundedRectangle, Scene, VGroup, Write)

from qcai_style import AMBER, BLUE, CYAN, INK, MUTED, RED, VIOLET, label, params

LESSON = "L2-02"


def num(v):
    return str(int(v)) if float(v).is_integer() else str(v)


def h(p, t):
    return p["rate"] * t + p["start"]


def rule(p):
    return f"h(t) = {p['rate']}t + {p['start']}"


def residual_text(p, t):
    obs = p["measured"][p["weeks"].index(t)]
    pred = h(p, t)
    return f"{num(obs)} - {num(pred)} = {num(round(obs - pred, 2))}"


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    p = L["animation"]["params"]
    t = p["machine_input"]
    return [rule(p), f"h({t}) = {num(h(p, t))}", "residual = observed - predicted"] + [residual_text(p, w) for w in p["show_residuals"]]


class FunctionResiduals(Scene):
    def construct(self):
        p = params(LESSON)

        # Part 1: the function machine
        title = label("A function: each input gives exactly one output", 34, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=1.2)
        box = RoundedRectangle(width=4.2, height=1.6, corner_radius=0.2, stroke_color=VIOLET, stroke_width=4,
                               fill_color=VIOLET, fill_opacity=0.08)
        rl = label(rule(p), 36, VIOLET, "BOLD").move_to(box)
        machine = VGroup(box, rl).move_to(UP * 0.4)
        t = p["machine_input"]
        inp = label(f"t = {t} weeks", 32, INK).move_to(LEFT * 5.0 + UP * 0.4)
        out = label(f"h = {num(h(p, t))} cm", 32, CYAN, "BOLD").move_to(RIGHT * 5.0 + UP * 0.4)
        a1 = Arrow(inp.get_right(), box.get_left(), color=MUTED, buff=0.2, stroke_width=4)
        a2 = Arrow(box.get_right(), out.get_left(), color=MUTED, buff=0.2, stroke_width=4)
        self.play(FadeIn(machine), run_time=0.8)
        self.play(FadeIn(inp), GrowArrow(a1), run_time=0.8)
        work = label(f"{p['rate']} × {t} + {p['start']} = {num(h(p, t))}", 30, INK).next_to(machine, DOWN, buff=0.5)
        self.play(FadeIn(work), run_time=0.8)
        self.play(GrowArrow(a2), FadeIn(out), run_time=0.8)
        short = label(f"h({t}) = {num(h(p, t))}", 36, CYAN, "BOLD").next_to(work, DOWN, buff=0.4)
        self.play(Write(short), run_time=0.8)
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in (machine, inp, out, a1, a2, work, short)], run_time=0.6)

        # Part 2: mapping diagrams, person -> month (a function) and month -> person (not a function)
        people = p["people"]
        months = []
        for m in people.values():
            if m not in months:
                months.append(m)

        def column(names, x, color):
            items = VGroup(*[label(n, 30, color) for n in names]).arrange(DOWN, buff=0.45)
            items.move_to([x, -0.3, 0])
            oval = Ellipse(width=max(it.width for it in items) + 1.0, height=items.height + 0.9, color=MUTED, stroke_width=3)
            oval.move_to(items)
            return items, oval

        def diagram(cx, left, right, pairs, color_l, color_r, arrow_col):
            li, lo = column(left, cx - 1.75, color_l)
            ri, ro = column(right, cx + 1.75, color_r)
            arrows = VGroup()
            for a, b in pairs:
                ia, ib = li[left.index(a)], ri[right.index(b)]
                arrows.add(Arrow(ia.get_right(), ib.get_left(), color=arrow_col, buff=0.15, stroke_width=4,
                                 max_tip_length_to_length_ratio=0.18))
            return VGroup(lo, li, ro, ri), arrows

        names = list(people.keys())
        d1, ar1 = diagram(-3.55, names, months, [(n, people[n]) for n in names], INK, BLUE, VIOLET)
        cap1 = label("person -> birth month", 28, INK, "BOLD").next_to(d1, UP, buff=0.3)
        ok1 = label("a function", 30, VIOLET, "BOLD").next_to(d1, DOWN, buff=0.3)
        self.play(FadeIn(d1), FadeIn(cap1), run_time=0.8)
        self.play(*[GrowArrow(a) for a in ar1], run_time=1.0)
        self.play(FadeIn(ok1), run_time=0.5)
        self.wait(0.8)

        d2, ar2 = diagram(3.55, months, names, [(people[n], n) for n in names], BLUE, INK, RED)
        cap2 = label("birth month -> person", 28, INK, "BOLD").next_to(d2, UP, buff=0.3)
        no2 = label("not a function", 30, RED, "BOLD").next_to(d2, DOWN, buff=0.3)
        self.play(FadeIn(d2), FadeIn(cap2), run_time=0.8)
        self.play(*[GrowArrow(a) for a in ar2], run_time=1.0)
        shared = people[names[0]]
        two = label(f"{shared} has two outputs", 26, RED).next_to(no2, DOWN, buff=0.15)
        self.play(FadeIn(no2), FadeIn(two), run_time=0.6)
        self.wait(2.0)
        self.play(*[FadeOut(m) for m in (d1, ar1, cap1, ok1, d2, ar2, cap2, no2, two)], run_time=0.6)

        # Part 3: prediction vs measurement
        title2 = label("Leo's plant: model line vs measured dots (made-up numbers)", 32, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(FadeOut(title), FadeIn(title2), run_time=0.7)
        weeks, meas = p["weeks"], p["measured"]
        ax = Axes(x_range=[0, weeks[-1] + 0.5, 1], y_range=[4, 16, 2], x_length=6.2, y_length=5.0,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 28},
                  x_axis_config={"numbers_to_include": weeks},
                  y_axis_config={"numbers_to_include": list(range(4, 17, 2))}).move_to(LEFT * 3.0 + DOWN * 0.3)
        for axis in (ax.x_axis, ax.y_axis):
            axis.numbers.set_color(MUTED)
            for nn in axis.numbers:
                nn.scale(1.2)
        xl = label("weeks, t", 26, MUTED).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = label("height, cm", 26, MUTED).next_to(ax.y_axis, UP, buff=0.15).shift(RIGHT * 0.5)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
        line = Line(ax.c2p(0, h(p, 0)), ax.c2p(weeks[-1] + 0.5, h(p, weeks[-1] + 0.5)), color=VIOLET, stroke_width=5)
        lt = label(rule(p), 30, VIOLET, "BOLD").move_to(RIGHT * 3.9 + UP * 2.2)
        lt2 = label("predicted", 26, VIOLET).next_to(lt, DOWN, buff=0.1)
        self.play(Create(line), FadeIn(lt), FadeIn(lt2), run_time=1.0)
        dots = VGroup(*[Dot(ax.c2p(w, m), radius=0.075, color=CYAN) for w, m in zip(weeks, meas)])
        dl = VGroup(Dot(radius=0.1, color=CYAN), label("measured", 26, CYAN)).arrange(RIGHT, buff=0.15).next_to(lt2, DOWN, buff=0.3)
        self.play(FadeIn(dots, lag_ratio=0.3), FadeIn(dl), run_time=1.2)
        segs = VGroup()
        for w, m in zip(weeks, meas):
            if abs(m - h(p, w)) > 1e-9:
                segs.add(Line(ax.c2p(w, h(p, w)), ax.c2p(w, m), color=AMBER if m > h(p, w) else RED, stroke_width=7).set_z_index(2))
        rule_r = label("residual = observed - predicted", 28, INK, "BOLD").next_to(dl, DOWN, buff=0.45)
        self.play(Create(segs), FadeIn(rule_r), run_time=1.2)
        notes = VGroup()
        for w in p["show_residuals"]:
            m = meas[weeks.index(w)]
            col = AMBER if m > h(p, w) else RED
            notes.add(label(f"week {w}:  " + residual_text(p, w), 28, col))
        notes.arrange(DOWN, buff=0.2, aligned_edge=LEFT).next_to(rule_r, DOWN, buff=0.35)
        for nt in notes:
            self.play(FadeIn(nt), run_time=0.7)
        self.wait(3.0)
        _ = (Cross, LEFT, RIGHT, UP, DOWN)
