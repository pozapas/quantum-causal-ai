"""L1-04 Count within a condition: keeping only one group changes the bottom number.

The four counts come from the lesson JSON (animation.params); the totals are worked
out here. The grid layout is shuffled with qcai.science.rng and the stored seed, so
the picture is the same on every render.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, FadeIn, FadeOut, Indicate, Line, MathTex, Rectangle, Scene, Square,
                   SurroundingRectangle, Transform, VGroup, Write)

from qcai_style import VIOLET, BLUE, INK, MUTED, RED, label, params

LESSON = "L1-04"


def table(p):
    rs, bs, rc, bc = p["red_square"], p["blue_square"], p["red_circle"], p["blue_circle"]
    return {"rs": rs, "bs": bs, "rc": rc, "bc": bc, "squares": rs + bs, "circles": rc + bc,
            "red": rs + rc, "blue": bs + bc, "all": rs + bs + rc + bc}


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    t = table(L["animation"]["params"])
    return [f"{t['rs']} out of {t['all']}", f"{t['rs']} out of {t['squares']}", f"{t['rs']} out of {t['red']}"]


def shuffled(kinds, seed):
    from qcai import science
    rand = science.rng(seed)
    out = list(kinds)
    for i in range(len(out) - 1, 0, -1):  # Fisher-Yates with the course's seeded generator
        j = int(rand() * (i + 1))
        out[i], out[j] = out[j], out[i]
    return out


def frac(a, b, color=INK):
    return MathTex(r"\frac{%d}{%d}" % (a, b), color=color, font_size=72)


class CountWithinGroup(Scene):
    def construct(self):
        p = params(LESSON)
        t = table(p)
        kinds = (["rs"] * t["rs"] + ["bs"] * t["bs"] + ["rc"] * t["rc"] + ["bc"] * t["bc"])
        kinds = shuffled(kinds, p["seed"])

        title = label(f"{t['all']} shapes: which group are we counting?", 38, INK, "BOLD").to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=1.1)

        cols, step = 6, 0.95
        rows = (len(kinds) + cols - 1) // cols
        shapes = VGroup()
        for i, k in enumerate(kinds):
            col = RED if k[0] == "r" else BLUE
            m = (Square(side_length=0.62, color=col, fill_color=col, fill_opacity=1, stroke_width=0) if k[1] == "s"
                 else Circle(radius=0.34, color=col, fill_color=col, fill_opacity=1, stroke_width=0))
            m.move_to([(i % cols - (cols - 1) / 2) * step - 3.4, ((rows - 1) / 2 - i // cols) * step - 0.35, 0])
            m.kind = k
            shapes.add(m)
        self.play(FadeIn(shapes, lag_ratio=0.04), run_time=1.5)

        RX = 3.3  # centre of the right-hand panel
        def is_(m, test):
            return test(m.kind)

        # 1. red squares out of everything
        q0 = label("Red squares,\nout of all shapes", 32, INK).move_to([RX, 1.75, 0])
        f = frac(t["rs"], t["all"]).move_to([RX, 0.3, 0])
        s0 = label(f"{t['rs']} out of {t['all']}", 32, INK).move_to([RX, -1.1, 0])
        self.play(FadeIn(q0), run_time=0.7)
        self.play(*[Indicate(m, color=RED, scale_factor=1.25) for m in shapes if m.kind == "rs"], run_time=1.0)
        self.play(Write(f), FadeIn(s0), run_time=1.0)
        self.wait(1.0)

        # 2. of the squares: everything that is not a square fades out
        q1 = label("Of the squares,\nwhat fraction is red?", 32, INK).move_to([RX, 1.75, 0])
        self.play(Transform(q0, q1), run_time=0.8)
        self.play(*[m.animate.set_opacity(0.1) for m in shapes if m.kind[1] != "s"], run_time=1.0)
        f1 = frac(t["rs"], t["squares"]).move_to(f)
        f1[0][2:].set_color(VIOLET)  # the new bottom number
        s1 = label(f"{t['rs']} out of {t['squares']} squares are red", 32, INK).move_to([RX, -1.1, 0])
        self.play(Transform(f, f1), Transform(s0, s1), run_time=1.2)
        note = label(f"The whole is now the {t['squares']} squares.", 28, VIOLET).move_to([RX, -2.0, 0])
        self.play(FadeIn(note), run_time=0.7)
        self.wait(1.6)

        # 3. of the red shapes: only red stays
        q2 = label("Of the red shapes,\nwhat fraction are squares?", 32, INK).move_to([RX, 1.75, 0])
        self.play(Transform(q0, q2), FadeOut(note), *[m.animate.set_opacity(1 if m.kind[0] == "r" else 0.1) for m in shapes],
                  run_time=1.2)
        f2 = frac(t["rs"], t["red"]).move_to(f)
        f2[0][2:].set_color(VIOLET)
        s2 = label(f"{t['rs']} out of {t['red']} red shapes are squares", 32, INK).move_to([RX, -1.1, 0])
        self.play(Transform(f, f2), Transform(s0, s2), run_time=1.2)
        note2 = label(f"The whole is now the {t['red']} red shapes.", 28, VIOLET).move_to([RX, -2.0, 0])
        self.play(FadeIn(note2), run_time=0.7)
        self.wait(1.6)

        # 4. the two-way table
        self.play(*[FadeOut(m) for m in (shapes, q0, f, s0, note2)], run_time=0.8)
        cw, ch = 2.3, 0.85
        heads = ["", "square", "circle", "total"]
        body = [["red", t["rs"], t["rc"], t["red"]], ["blue", t["bs"], t["bc"], t["blue"]],
                ["total", t["squares"], t["circles"], t["all"]]]
        x0, y0 = -2 * cw, 1.9
        cells = {}
        grid = VGroup()
        for r in range(5):
            grid.add(Line([x0, y0 - r * ch, 0], [x0 + 4 * cw, y0 - r * ch, 0], color=MUTED, stroke_width=2 if r not in (1, 3) else 3))
        for c in range(5):
            grid.add(Line([x0 + c * cw, y0, 0], [x0 + c * cw, y0 - 4 * ch, 0], color=MUTED, stroke_width=2 if c not in (1, 3) else 3))
        words = VGroup()
        for c, h in enumerate(heads):
            if h:
                m = label(h, 30, INK, "BOLD").move_to([x0 + (c + 0.5) * cw, y0 - 0.5 * ch, 0])
                words.add(m)
        for r, row in enumerate(body):
            for c, v in enumerate(row):
                col = RED if row[0] == "red" and c == 0 else BLUE if row[0] == "blue" and c == 0 else INK
                m = label(str(v), 30, col, "BOLD" if c == 0 else "NORMAL").move_to([x0 + (c + 0.5) * cw, y0 - (r + 1.5) * ch, 0])
                cells[(r, c)] = m
                words.add(m)
        self.play(Create(grid), run_time=1.0)
        self.play(FadeIn(words, lag_ratio=0.05), run_time=1.2)

        col_box = Rectangle(width=cw - 0.16, height=3 * ch - 0.16, color=VIOLET, stroke_width=6).move_to([x0 + 1.5 * cw, y0 - 2.5 * ch, 0])
        col_lbl = label(f"Of the squares: {t['rs']} out of {t['squares']}", 30, VIOLET).move_to([0, -2.15, 0])
        self.play(Create(col_box), FadeIn(col_lbl), run_time=1.0)
        self.wait(1.2)
        row_box = Rectangle(width=3 * cw - 0.3, height=ch - 0.3, color=RED, stroke_width=5).move_to([x0 + 2.5 * cw, y0 - 1.5 * ch, 0])
        row_lbl = label(f"Of the red shapes: {t['rs']} out of {t['red']}", 30, RED).move_to([0, -2.85, 0])
        self.play(Create(row_box), FadeIn(row_lbl), run_time=1.0)
        end = label("Same top number. Different whole.", 30, INK, "BOLD").move_to([0, -3.55, 0])
        self.play(FadeIn(end), run_time=0.7)
        self.wait(2.5)
        _ = DOWN, LEFT, RIGHT, UP
