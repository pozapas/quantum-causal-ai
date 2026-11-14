"""L1-10 Keep a model testable: 36 dice pairs, six sum to 7, a seeded run of 36 rolls, then the model card.

The rolls come from the course's seeded generator (qcai.science.rng) with the seed, the
number of rolls and the doubt rule stored in the lesson JSON.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, FadeIn, FadeOut, Line, MathTex, Rectangle, RoundedRectangle, Scene, Square,
                   Transform, VGroup, Write)

from qcai_style import AMBER, CYAN_LIGHT, GRID, INK, MUTED, VIOLET, label, params

LESSON = "L1-10"


def run(p):
    from qcai import science
    r = science.rng(p["seed"])
    rolls = [(int(r() * 6) + 1, int(r() * 6) + 1) for _ in range(p["rolls"])]
    sevens = sum(1 for a, b in rolls if a + b == 7)
    return rolls, sevens


def ways7():
    return sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == 7)


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    p = L["animation"]["params"]
    _, sevens = run(p)
    return [f"{ways7()} out of 36", f"{sevens} sevens in {p['rolls']} rolls",
            f"0 or {p['doubt_low']} sevens, or {p['doubt_high']} or more"]


class TestableModel(Scene):
    def construct(self):
        p = params(LESSON)
        rolls, sevens = run(p)
        N = p["rolls"]

        title = label("How often do two dice add to 7?", 40, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=1.0)

        # 6 by 6 grid of pairs
        s = 0.66
        cells, sev = VGroup(), VGroup()
        for a in range(1, 7):
            for b in range(1, 7):
                sq = Square(side_length=s, stroke_color=MUTED, stroke_width=2, fill_color="#ffffff", fill_opacity=1)
                sq.move_to([(b - 3.5) * s, (3.5 - a) * s, 0])
                t = label(str(a + b), 26, INK).move_to(sq)
                c = VGroup(sq, t)
                cells.add(c)
                if a + b == 7:
                    sev.add(c)
        top = VGroup(*[label(str(b), 26, VIOLET, "BOLD").move_to([(b - 3.5) * s, 3.5 * s - 0.05 + 0.1, 0]) for b in range(1, 7)])
        side = VGroup(*[label(str(a), 26, VIOLET, "BOLD").move_to([-3.5 * s - 0.05, (3.5 - a) * s, 0]) for a in range(1, 7)])
        grid = VGroup(cells, top, side).move_to(LEFT * 3.4 + DOWN * 0.45)
        self.play(FadeIn(cells, lag_ratio=0.02), FadeIn(top), FadeIn(side), run_time=1.6)
        info = label("36 equally likely pairs", 32, INK).move_to(RIGHT * 3.2 + UP * 1.6)
        self.play(FadeIn(info), run_time=0.6)
        self.play(*[c[0].animate.set_fill(AMBER, 1) for c in sev], run_time=1.0)
        frac = label(f"{ways7()} out of 36", 36, INK, "BOLD").next_to(info, DOWN, buff=0.5)
        eq = MathTex(r"\frac{6}{36} = \frac{1}{6}", color=INK, font_size=56).next_to(frac, DOWN, buff=0.35)
        pred = label(f"Prediction: about {N // 6} sevens in {N} rolls", 30, VIOLET).next_to(eq, DOWN, buff=0.45)
        self.play(FadeIn(frac), run_time=0.6)
        self.play(Write(eq), run_time=1.0)
        self.play(FadeIn(pred), run_time=0.7)
        self.wait(1.6)

        # run of rolls: tally chart of sums 2 to 12
        remind = label(f"Prediction: about {N // 6} sevens in {N} rolls", 30, VIOLET).move_to(UP * 1.55)
        self.play(FadeOut(info), FadeOut(frac), FadeOut(eq), FadeOut(grid), Transform(pred, remind), run_time=0.9)
        unit, w, gap = 0.6, 0.62, 0.85
        x0 = -5 * gap
        base_y = -2.35
        axis = Line([x0 - 0.4, base_y, 0], [x0 + 10 * gap + 0.4, base_y, 0], color=MUTED, stroke_width=3)
        nums = VGroup(*[label(str(k), 26, VIOLET if k == 7 else MUTED, "BOLD" if k == 7 else "NORMAL")
                        .move_to([x0 + (k - 2) * gap, base_y - 0.32, 0]) for k in range(2, 13)])
        cap = label("sum of the two dice", 26, MUTED).next_to(nums, DOWN, buff=0.15)
        self.play(FadeIn(axis), FadeIn(nums), FadeIn(cap), run_time=0.6)

        def bar(k, n):
            h = max(n * unit, 0.001)
            r = Rectangle(width=w, height=h, stroke_width=0, fill_color=AMBER if k == 7 else VIOLET, fill_opacity=1 if n else 0)
            return r.move_to([x0 + (k - 2) * gap, base_y + h / 2, 0])

        counts = {k: 0 for k in range(2, 13)}
        bars = {k: bar(k, 0) for k in range(2, 13)}
        self.add(*bars.values())

        def status(i, a, b, n7):
            return VGroup(label(f"Roll {i}: {a} + {b} = {a + b}", 30, INK),
                          label(f"{n7} {'seven' if n7 == 1 else 'sevens'} in {i} {'roll' if i == 1 else 'rolls'}", 30, AMBER if a + b == 7 else INK, "BOLD")
                          ).arrange(RIGHT, buff=0.9).move_to(UP * 2.4)

        n7 = 0
        st = status(1, *rolls[0], 0)
        for i, (a, b) in enumerate(rolls, start=1):
            counts[a + b] += 1
            n7 += a + b == 7
            new = status(i, a, b, n7)
            self.remove(st)
            self.add(new)
            st = new
            self.play(Transform(bars[a + b], bar(a + b, counts[a + b])), run_time=0.24)
        self.wait(1.4)

        # model card
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)
        rows = [("Question", "How often do two dice add to 7?"),
                ("Assumption", "The dice are fair: all 36 pairs equally likely."),
                ("Prediction", f"About {N // 6} sevens in {N} rolls."),
                ("Doubt if", f"0 or {p['doubt_low']} sevens, or {p['doubt_high']} or more."),
                ("What happened", f"{sevens} sevens in {N} rolls. No reason to doubt the dice yet.")]
        lines = VGroup()
        for k, v in rows:
            lines.add(VGroup(label(k, 28, VIOLET, "BOLD"), label(v, 28, INK)).arrange(RIGHT, buff=0.3))
        lines.arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        for ln in lines:
            ln[1].shift(RIGHT * (lines[4][0].get_right()[0] + 0.3 - ln[1].get_left()[0]))
        head = label("Model card", 38, INK, "BOLD")
        card_body = VGroup(head, lines).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        frame = RoundedRectangle(width=card_body.width + 0.9, height=card_body.height + 0.8, corner_radius=0.25,
                                 stroke_color=VIOLET, stroke_width=4, fill_color=CYAN_LIGHT, fill_opacity=0.25)
        card = VGroup(frame, card_body.move_to(frame))
        card.move_to(DOWN * 0.1)
        self.play(FadeIn(frame), FadeIn(head), run_time=0.6)
        for ln in lines:
            self.play(FadeIn(ln, shift=RIGHT * 0.2), run_time=0.55)
        self.wait(3.0)
        _ = (GRID, UP)
