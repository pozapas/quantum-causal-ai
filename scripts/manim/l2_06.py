"""L2-06 See a reversed comparison: A wins in each group, B wins when the groups are combined.

The made-up pass counts come from the lesson JSON (animation.params). The scene
works out every rate and checks the reversal by arithmetic before drawing. Bar
width shows how many students; bar height shows the pass rate, so bar area is the
number who passed and merging two bars keeps the area. No randomness is used.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from fractions import Fraction

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, FadeIn, FadeOut, Line, Rectangle, Scene, SurroundingRectangle, Transform,
                   VGroup, Write)

from qcai_style import AMBER, BLUE, INK, MUTED, VIOLET, label, params

LESSON = "L2-06"
GROUPS = ("easy", "hard")


def data(p):
    d = {g: {k: tuple(p[g][k]) for k in ("A", "B")} for g in GROUPS}
    comb = {k: (sum(d[g][k][0] for g in GROUPS), sum(d[g][k][1] for g in GROUPS)) for k in ("A", "B")}
    rate = lambda pair: Fraction(pair[0], pair[1])  # noqa: E731
    for g in GROUPS:  # A ahead inside every group
        assert rate(d[g]["A"]) > rate(d[g]["B"]), g
    assert rate(comb["A"]) < rate(comb["B"])  # but behind when combined
    return d, comb


def pct(pair):
    x = Fraction(pair[0], pair[1]) * 100
    assert x.denominator == 1
    return int(x)


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    d, comb = data(L["animation"]["params"])
    out = [f"{d[g][k][0]} of {d[g][k][1]}" for g in GROUPS for k in ("A", "B")]
    out += [f"{comb[k][0]} of {comb[k][1]}" for k in ("A", "B")]
    out += [f"{pct(d[g][k])} percent" for g in GROUPS for k in ("A", "B")] + [f"{pct(comb[k])} percent" for k in ("A", "B")]
    return out


BASE = -2.35
H = 4.0  # height of a 100 percent bar
COL = {"A": VIOLET, "B": BLUE}


def bar(x, w, pair, key):
    h = H * pair[0] / pair[1]
    return Rectangle(width=w, height=h, color=COL[key], fill_color=COL[key], fill_opacity=0.85, stroke_width=0).move_to(
        [x, BASE + h / 2, 0])


def tags(b, pair, key):
    top = label(f"{pct(pair)} percent", 26, COL[key], "BOLD").next_to(b, UP, buff=0.12)
    bottom = label(f"{key}: {pair[0]} of {pair[1]}", 26, INK).next_to([b.get_center()[0], BASE, 0], DOWN, buff=0.18)
    return top, bottom


class ReversedComparison(Scene):
    def construct(self):
        p = params(LESSON)
        d, comb = data(p)

        title = label("Two tutoring programs, A and B (made-up numbers)", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.1)

        centre = {"easy": -3.6, "hard": 3.6}
        heads = VGroup(label("Easy courses", 30, INK, "BOLD").move_to([centre["easy"], 2.55, 0]),
                       label("Hard courses", 30, INK, "BOLD").move_to([centre["hard"], 2.55, 0]))
        heads[1].align_to(heads[0], UP)
        floor = Line([-6.8, BASE, 0], [6.8, BASE, 0], color=MUTED, stroke_width=2)
        self.play(FadeIn(heads), FadeIn(floor), run_time=0.8)

        bars, tops, bots = {}, {}, {}
        for g in GROUPS:
            for k, dx in (("A", -1.0), ("B", 1.0)):
                b = bar(centre[g] + dx, 1.2, d[g][k], k)
                t, s = tags(b, d[g][k], k)
                bars[g, k], tops[g, k], bots[g, k] = b, t, s
        self.play(*[FadeIn(bars[key], shift=UP * 0.3) for key in bars], run_time=1.2)
        self.play(*[FadeIn(tops[key]) for key in bars], *[FadeIn(bots[key]) for key in bars], run_time=0.9)
        msg = label("Pass rate: A is ahead in both groups.", 30, VIOLET).move_to([0, -3.5, 0])
        self.play(FadeIn(msg), run_time=0.7)
        self.wait(2.0)

        # width shows group size
        scale = 0.04
        msg2 = label("Now make each bar as wide as its number of students.", 30, INK).move_to(msg)
        anims = [Transform(msg, msg2)]
        for g in GROUPS:
            wa, wb = d[g]["A"][1] * scale, d[g]["B"][1] * scale
            nb = {"A": bar(centre[g] - 0.3 - wa / 2, wa, d[g]["A"], "A"), "B": bar(centre[g] + 0.3 + wb / 2, wb, d[g]["B"], "B")}
            for k in ("A", "B"):
                t, s = tags(nb[k], d[g][k], k)
                anims += [Transform(bars[g, k], nb[k]), Transform(tops[g, k], t), Transform(bots[g, k], s)]
        self.play(*anims, run_time=1.6)
        self.wait(2.2)

        # merge each program's two bars: area (students who passed) is kept
        msg3 = label("Combine the groups. Area shows students who passed.", 30, INK).move_to(msg)
        ctr = {"A": -3.0, "B": 3.0}
        moves = [Transform(msg, msg3), FadeOut(heads)]
        moves += [FadeOut(tops[key]) for key in bars] + [FadeOut(bots[key]) for key in bars]
        for k in ("A", "B"):
            w_e, w_h = d["easy"][k][1] * scale, d["hard"][k][1] * scale
            left = ctr[k] - (w_e + w_h) / 2
            moves.append(bars["easy", k].animate.move_to([left + w_e / 2, bars["easy", k].get_center()[1], 0]))
            moves.append(bars["hard", k].animate.move_to([left + w_e + w_h / 2, bars["hard", k].get_center()[1], 0]))
        self.play(*moves, run_time=1.5)
        self.wait(0.6)

        heads2 = label("All courses together", 30, INK, "BOLD").move_to([0, 2.55, 0])
        final = {}
        anims = [FadeIn(heads2)]
        for k in ("A", "B"):
            w = comb[k][1] * scale
            final[k] = bar(ctr[k], w, comb[k], k)
            anims += [Transform(bars["easy", k], final[k]), FadeOut(bars["hard", k])]
        self.play(*anims, run_time=1.6)
        ft = VGroup()
        for k in ("A", "B"):
            t, s = tags(final[k], comb[k], k)
            ft.add(t, s)
        msg4 = label("Combined: B is ahead. The comparison flipped.", 30, AMBER, "BOLD").move_to(msg)
        self.play(FadeIn(ft), Transform(msg, msg4), run_time=0.9)
        self.wait(2.4)

        # the causal story
        self.play(*[FadeOut(m) for m in (bars["easy", "A"], bars["easy", "B"], ft, floor, heads2, msg)], run_time=0.8)

        def node(text, pos):
            t = label(text, 30, INK, "BOLD").move_to(pos)
            return VGroup(SurroundingRectangle(t, color=MUTED, buff=0.22, corner_radius=0.15, stroke_width=3), t)

        diff = node("course difficulty", [0, 1.7, 0])
        prog = node("program (A or B)", [-3.4, -1.2, 0])
        pas = node("pass", [3.4, -1.2, 0])
        a1 = Arrow(diff.get_bottom(), prog.get_top(), color=AMBER, buff=0.1, stroke_width=6)
        a2 = Arrow(diff.get_bottom(), pas.get_top(), color=AMBER, buff=0.1, stroke_width=6)
        a3 = Arrow(prog.get_right(), pas.get_left(), color=INK, buff=0.1, stroke_width=6)
        q = label("?", 34, INK, "BOLD").next_to(a3, UP, buff=0.12)
        self.play(FadeIn(diff), FadeIn(prog), FadeIn(pas), run_time=0.8)
        self.play(FadeIn(a1), FadeIn(a2), run_time=0.9)
        self.play(FadeIn(a3), FadeIn(q), run_time=0.7)
        end = VGroup(label("Difficulty affects both the program and passing.", 30, INK),
                     label("So here, compare A and B within each group.", 30, VIOLET, "BOLD")).arrange(DOWN, buff=0.15)
        end.move_to([0, -2.9, 0])
        self.play(FadeIn(end), run_time=0.9)
        self.wait(3.0)
        _ = LEFT, RIGHT
