"""L1-05 Assign a fair comparison: coin flips balance hidden strength on average; picking does not.

The strengths are a fixed made-up list in the lesson JSON; the coin flips come from the
course's seeded generator (qcai.science.rng) with the seed stored there too.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from decimal import ROUND_HALF_UP, Decimal

from manim import (DOWN, LEFT, RIGHT, UP, Circle, FadeIn, FadeOut, Line, RoundedRectangle, Scene, VGroup, Write,
                   interpolate_color, ManimColor)

from qcai_style import AMBER, GRID, INK, MUTED, VIOLET, label, params

LESSON = "L1-05"
LIGHT = "#ede9fe"
DARK = "#3b0764"


def avg(xs):
    """Average rounded half up to one decimal, as a child would round it."""
    return str((Decimal(sum(xs)) / Decimal(len(xs))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def run(p):
    from qcai import science
    s = p["strengths"]
    r = science.rng(p["seed"])
    coin = ["H" if r() < 0.5 else "T" for _ in s]
    order = sorted(range(len(s)), key=lambda i: -s[i])
    picked = ["A" if i in order[: len(s) // 2] else "B" for i in range(len(s))]
    ca = [x for x, c in zip(s, coin) if c == "H"]
    cb = [x for x, c in zip(s, coin) if c == "T"]
    pa = [x for x, g in zip(s, picked) if g == "A"]
    pb = [x for x, g in zip(s, picked) if g == "B"]
    return coin, picked, (avg(ca), avg(cb)), (avg(pa), avg(pb))


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    _, _, c, pk = run(L["animation"]["params"])
    return [f"average {c[0]}", f"average {c[1]}", f"average {pk[0]}", f"average {pk[1]}"]


def friend(v):
    col = interpolate_color(ManimColor(LIGHT), ManimColor(DARK), (v - 1) / 9)
    c = Circle(radius=0.36, fill_color=col, fill_opacity=1, stroke_color=INK, stroke_width=2)
    t = label(str(v), 28, "#ffffff" if v >= 5 else INK, "BOLD").move_to(c)
    return VGroup(c, t)


class FairAssignment(Scene):
    def construct(self):
        p = params(LESSON)
        s = p["strengths"]
        coin, picked, cavg, pavg = run(p)

        title = label("Who throws Plane A? Who throws Plane B?", 38, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=1.0)

        people = VGroup(*[friend(v) for v in s]).arrange_in_grid(2, 8, buff=0.3).move_to(UP * 0.2)
        key = label("Darker = stronger thrower (made-up strengths)", 28, MUTED).next_to(people, DOWN, buff=0.5)
        self.play(FadeIn(people, lag_ratio=0.05), FadeIn(key), run_time=1.6)
        self.wait(0.6)

        # two group boxes
        bx = VGroup()
        for x, name in ((-3.55, "Plane A"), (3.55, "Plane B")):
            b = RoundedRectangle(width=6.2, height=3.0, corner_radius=0.2, stroke_color=MUTED, stroke_width=2).move_to([x, -1.25, 0])
            h = label(name, 30, VIOLET, "BOLD").next_to(b, UP, buff=0.1)
            bx.add(VGroup(b, h))

        def slot(group_box, k):
            col, row = k % 5, k // 5
            return group_box[0].get_corner(UP + LEFT) + RIGHT * (0.7 + col * 1.2) + DOWN * (0.6 + row * 0.95)

        sub = label("Step 1: flip a coin for each friend. Heads: A. Tails: B.", 28, INK).next_to(title, DOWN, buff=0.2)
        self.play(FadeOut(key), people.animate.arrange_in_grid(1, 16, buff=0.06).next_to(sub, DOWN, buff=0.3),
                  FadeIn(sub), FadeIn(bx), run_time=1.2)
        na = nb = 0
        for i, f in enumerate(people):
            hb = label(coin[i], 30, "#b45309", "BOLD").next_to(f, DOWN, buff=0.08)
            if coin[i] == "H":
                tgt, na = slot(bx[0], na), na + 1
            else:
                tgt, nb = slot(bx[1], nb), nb + 1
            self.play(FadeIn(hb), run_time=0.12)
            self.play(f.animate.move_to(tgt), hb.animate.move_to(tgt + DOWN * 0.55), run_time=0.3)
            self.remove(hb)
        ca = label(f"average {cavg[0]}", 34, INK, "BOLD").next_to(bx[0][0], DOWN, buff=0.18)
        cb = label(f"average {cavg[1]}", 34, INK, "BOLD").next_to(bx[1][0], DOWN, buff=0.18)
        self.play(FadeIn(ca), FadeIn(cb), run_time=0.8)
        note = label("Close, but not exactly the same.", 30, VIOLET).move_to(sub)
        self.play(FadeOut(sub), FadeIn(note), run_time=0.6)
        self.wait(2.0)

        # step 2: Ryan picks
        sub2 = label("Step 2: Ryan picks. The strongest 8 go to Plane A.", 28, INK).move_to(note)
        self.play(FadeOut(note), FadeOut(ca), FadeOut(cb), FadeIn(sub2), run_time=0.6)
        na = nb = 0
        moves = []
        order = sorted(range(len(s)), key=lambda i: -s[i])
        for i in order:
            if picked[i] == "A":
                tgt, na = slot(bx[0], na), na + 1
            else:
                tgt, nb = slot(bx[1], nb), nb + 1
            moves.append(people[i].animate.move_to(tgt))
        self.play(*moves, run_time=1.8)
        pa = label(f"average {pavg[0]}", 34, INK, "BOLD").next_to(bx[0][0], DOWN, buff=0.18)
        pb = label(f"average {pavg[1]}", 34, INK, "BOLD").next_to(bx[1][0], DOWN, buff=0.18)
        self.play(FadeIn(pa), FadeIn(pb), run_time=0.8)
        note2 = label("Not fair: the strong throwers are all on Plane A.", 30, "#b91c1c").move_to(sub2)
        self.play(FadeOut(sub2), FadeIn(note2), run_time=0.6)
        self.wait(1.8)

        end = VGroup(label("A coin does not take sides.", 34, INK, "BOLD"),
                     label("It balances the groups on average, not perfectly.", 30, INK)).arrange(DOWN, buff=0.15)
        end.to_edge(UP, buff=0.4)
        self.play(FadeOut(note2), FadeOut(title), FadeIn(end), run_time=0.9)
        self.wait(2.5)
        _ = (Line, LEFT, DOWN, GRID)
