"""L1-01 Fractions describe part of a whole: one half = two fourths = four eighths, then 3/12 = 1/4.

The cuts, the number of marbles, the green count and the number of groups come from
the lesson JSON (animation.params), so the fractions on screen are the ones in the text.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, FadeIn, FadeOut, Indicate, Line, MathTex, Rectangle,
                   RoundedRectangle, Scene, Transform, VGroup, Write)

from qcai_style import BLUE, INK, MUTED, VIOLET, VIOLET_LIGHT, label, params

LESSON = "L1-01"
GREEN = "#16a34a"  # the story's green marbles


def parts(p):
    """The shaded part for each cut: the same amount (one half) each time."""
    return [(c // 2, c) for c in p["cuts"]]


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    p = L["animation"]["params"]
    out = [f"{k} out of {c}" for k, c in parts(p)]
    out += [f"{p['green']} out of {p['marbles']}", f"1 out of {p['groups']}"]
    return out


class EqualFractions(Scene):
    def construct(self):
        p = params(LESSON)

        # Part 1: one strip, the same shaded amount, more and more cuts
        title = label("The same amount, cut into more pieces", 38, INK, "BOLD").to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=1.1)

        W, H, y = 10.0, 1.2, 1.2
        x0 = -W / 2
        bar = Rectangle(width=W, height=H, color=INK, stroke_width=4).move_to([0, y, 0])
        shade = Rectangle(width=W / 2, height=H, color=VIOLET_LIGHT, fill_color=VIOLET_LIGHT, fill_opacity=0.9,
                          stroke_width=0).move_to([x0 + W / 4, y, 0])
        self.play(Create(bar), run_time=0.8)

        drawn = set()
        cut_lines = VGroup()
        steps = parts(p)
        # the whole equation is laid out once; pieces are revealed one cut at a time
        eq = MathTex(*[s for i, (k, c) in enumerate(steps) for s in ((r"=",) if i else ()) + (r"\frac{%d}{%d}" % (k, c),)],
                     color=VIOLET, font_size=64).move_to([0, -1.6, 0])
        count_lbl = None
        for i, (k, c) in enumerate(steps):
            new = VGroup()
            for j in range(1, c):
                x = x0 + W * j / c
                key = round(x, 4)
                if key not in drawn:
                    drawn.add(key)
                    new.add(Line([x, y - H / 2, 0], [x, y + H / 2, 0], color=INK, stroke_width=3))
            cut_lines.add(*new)
            lbl = label(f"{k} out of {c} parts shaded", 32, VIOLET).move_to([0, y - 1.15, 0])
            if count_lbl is None:
                self.play(Create(new), run_time=0.7)
                self.add(shade, cut_lines)
                self.play(FadeIn(shade), FadeIn(lbl), run_time=0.8)
                count_lbl = lbl
            else:
                self.play(Create(new), Transform(count_lbl, lbl), run_time=1.0)
            self.bring_to_front(cut_lines, bar)
            self.wait(0.5)
            pieces = [eq[0]] if i == 0 else [eq[2 * i - 1], eq[2 * i]]
            self.play(*[Write(m) for m in pieces], run_time=0.8)
            self.wait(0.6)
        eq_prev = eq

        same = label("The shaded part never changed.", 30, MUTED).move_to([0, -3.05, 0])
        self.play(FadeIn(same), Indicate(shade, color=VIOLET, scale_factor=1.03), run_time=1.0)
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in (title, bar, shade, cut_lines, count_lbl, eq_prev, same)], run_time=0.7)

        # Part 2: 12 marbles, 3 green, into 4 equal groups
        n, g, groups = p["marbles"], p["green"], p["groups"]
        size = n // groups
        title2 = label(f"A bag of {n} marbles", 38, INK, "BOLD").to_edge(UP, buff=0.4)
        self.play(Write(title2), run_time=0.8)
        green_at = [round((i + 0.5) * n / g) for i in range(g)]  # spread the green ones out
        marbles = VGroup(*[Circle(radius=0.3, color=GREEN if i in green_at else BLUE,
                                  fill_color=GREEN if i in green_at else BLUE, fill_opacity=1, stroke_width=0)
                           for i in range(n)]).arrange(RIGHT, buff=0.28).move_to([0, 1.7, 0])
        self.play(FadeIn(marbles, lag_ratio=0.08), run_time=1.2)
        greens = [marbles[i] for i in green_at]
        self.play(*[Indicate(m, color=GREEN, scale_factor=1.3) for m in greens], run_time=0.9)
        t1 = label(f"{g} out of {n} marbles are green", 32, GREEN).move_to([0, 0.8, 0])
        self.play(FadeIn(t1), run_time=0.7)
        self.wait(0.8)

        # target spots: group 0 holds the green marbles
        boxes, spots = VGroup(), []
        for j in range(groups):
            cx = (j - (groups - 1) / 2) * 3.0
            boxes.add(RoundedRectangle(corner_radius=0.25, width=2.7, height=1.1, color=MUTED, stroke_width=3).move_to([cx, -0.5, 0]))
            spots.append([[cx + (k - (size - 1) / 2) * 0.74, -0.5, 0] for k in range(size)])
        others = [i for i in range(n) if i not in green_at]
        order = green_at + others
        self.play(Create(boxes), run_time=0.8)
        self.play(*[marbles[i].animate.move_to(spots[pos // size][pos % size]) for pos, i in enumerate(order)], run_time=1.6)
        t2 = label(f"1 out of {groups} groups is green", 32, GREEN).move_to([0, -1.55, 0])
        self.play(Indicate(boxes[0], color=GREEN, scale_factor=1.06), FadeIn(t2), run_time=1.0)
        eq2 = MathTex(r"\frac{%d}{%d} = \frac{1}{%d}" % (g, n, groups), color=INK, font_size=60).move_to([0, -2.8, 0])
        self.play(Write(eq2), run_time=1.0)
        self.wait(2.5)
        _ = DOWN, UP, RIGHT
