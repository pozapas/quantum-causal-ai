"""L2-04 Calculate conditional probability: a row total becomes the denominator.

The four inner counts of the made-up survey come from the lesson JSON
(animation.params); every total and fraction is worked out here, so the table on
screen and the numbers in the lesson text always agree. No randomness is used.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from fractions import Fraction

from manim import (DOWN, LEFT, RIGHT, UP, Create, FadeIn, FadeOut, Line, MathTex, Rectangle, Scene, TransformFromCopy,
                   VGroup, Write)

from qcai_style import AMBER, BLUE, INK, MUTED, VIOLET, label, params

LESSON = "L2-04"


def table(p):
    im, io, nm, no = p["instrument_math"], p["instrument_not"], p["none_math"], p["none_not"]
    t = {"im": im, "io": io, "nm": nm, "no": no, "instrument": im + io, "none": nm + no,
         "math": im + nm, "not": io + no, "all": im + io + nm + no}
    assert t["instrument"] + t["none"] == t["math"] + t["not"] == t["all"]
    return t


def dec(a, b):
    """A fraction as a short decimal (exact for the lesson's numbers)."""
    x = Fraction(a, b)
    return f"{float(x):.2f}".rstrip("0").rstrip(".")


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    t = table(L["animation"]["params"])
    return [f"{t['im']} out of {t['instrument']}", f"{t['math']} out of {t['all']}",
            f"{t['im']} out of {t['instrument']} is {dec(t['im'], t['instrument'])}",
            f"{t['math']} out of {t['all']} is {dec(t['math'], t['all'])}"]


class RowBecomesWhole(Scene):
    def construct(self):
        p = params(LESSON)
        t = table(p)

        title = label(f"An imagined survey of {t['all']} students (made-up numbers)", 34, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=1.2)

        widths = [4.3, 2.4, 2.4, 1.8]
        ch = 0.72
        x0 = -sum(widths) / 2
        y0 = 2.75
        xs = [x0]
        for w in widths:
            xs.append(xs[-1] + w)
        heads = ["", "likes math", "does not", "total"]
        body = [["plays an instrument", t["im"], t["io"], t["instrument"]],
                ["no instrument", t["nm"], t["no"], t["none"]],
                ["total", t["math"], t["not"], t["all"]]]
        grid = VGroup()
        for r in range(5):
            grid.add(Line([xs[0], y0 - r * ch, 0], [xs[-1], y0 - r * ch, 0], color=MUTED, stroke_width=3 if r in (1, 3) else 2))
        for c in range(5):
            grid.add(Line([xs[c], y0, 0], [xs[c], y0 - 4 * ch, 0], color=MUTED, stroke_width=3 if c in (1, 3) else 2))

        def cx(c):
            return (xs[c] + xs[c + 1]) / 2

        cells = {}
        words = VGroup()
        for c, h in enumerate(heads):
            if h:
                m = label(h, 28, INK, "BOLD").move_to([cx(c), y0 - 0.5 * ch, 0])
                words.add(m)
        for r, row in enumerate(body):
            for c, v in enumerate(row):
                m = label(str(v), 28, INK, "BOLD" if c == 0 else "NORMAL").move_to([cx(c), y0 - (r + 1.5) * ch, 0])
                cells[(r, c)] = m
                words.add(m)
        self.play(Create(grid), run_time=1.0)
        self.play(FadeIn(words, lag_ratio=0.04), run_time=1.4)
        self.wait(0.6)

        # 1. condition on playing an instrument: that row becomes the whole
        row_box = Rectangle(width=xs[-1] - xs[0] - 0.12, height=ch - 0.12, color=VIOLET, stroke_width=6)
        row_box.move_to([(xs[0] + xs[-1]) / 2, y0 - 1.5 * ch, 0])
        q1 = label("Given: plays an instrument. Only this row counts.", 30, VIOLET).move_to([0, -0.45, 0])
        self.play(Create(row_box), FadeIn(q1), *[cells[(r, c)].animate.set_opacity(0.25) for r in (1, 2) for c in range(4)],
                  run_time=1.2)
        self.wait(0.8)

        f1 = MathTex(r"P(\text{math}\mid\text{instrument})=", r"\frac{%d}{%d}" % (t["im"], t["instrument"]),
                     r"=%s" % dec(t["im"], t["instrument"]), color=INK, font_size=48)
        f1.move_to([0, -1.55, 0])
        top, bottom = f1[1][:len(str(t["im"]))], f1[1][-len(str(t["instrument"])):]
        bottom.set_color(VIOLET)
        self.play(FadeIn(f1[0]), run_time=0.6)
        self.play(TransformFromCopy(cells[(0, 1)], top), run_time=0.9)
        self.play(FadeIn(f1[1][len(str(t["im"])):len(f1[1]) - len(str(t["instrument"]))]),
                  TransformFromCopy(cells[(0, 3)], bottom), run_time=1.0)
        self.play(FadeIn(f1[2]), run_time=0.6)
        s1 = label(f"{t['im']} out of {t['instrument']} is {dec(t['im'], t['instrument'])}", 30, VIOLET).next_to(f1, DOWN, buff=0.3)
        self.play(FadeIn(s1), run_time=0.6)
        self.wait(1.6)

        # 2. no condition: the whole survey
        self.play(FadeOut(row_box), FadeOut(q1), *[m.animate.set_opacity(1) for m in cells.values()],
                  VGroup(f1, s1).animate.scale(0.8).move_to([-3.4, -1.75, 0]), run_time=1.0)
        all_box = Rectangle(width=xs[2] - xs[1] - 0.12, height=ch - 0.12, color=BLUE, stroke_width=6).move_to([cx(1), y0 - 3.5 * ch, 0])
        all_box2 = Rectangle(width=xs[4] - xs[3] - 0.12, height=ch - 0.12, color=BLUE, stroke_width=6).move_to([cx(3), y0 - 3.5 * ch, 0])
        q2 = label("No condition: the whole survey counts.", 30, BLUE).move_to([0, -0.45, 0])
        self.play(Create(all_box), Create(all_box2), FadeIn(q2), run_time=1.0)
        f2 = MathTex(r"P(\text{math})=", r"\frac{%d}{%d}" % (t["math"], t["all"]), r"=%s" % dec(t["math"], t["all"]),
                     color=INK, font_size=48).scale(0.8).move_to([3.6, -1.55, 0])
        s2 = label(f"{t['math']} out of {t['all']} is {dec(t['math'], t['all'])}", 30, BLUE).scale(0.8).next_to(f2, DOWN, buff=0.25)
        self.play(TransformFromCopy(cells[(2, 1)], f2[1][:len(str(t["math"]))]), FadeIn(f2[0]),
                  FadeIn(f2[1][len(str(t["math"])):]), FadeIn(f2[2]), run_time=1.2)
        self.play(FadeIn(s2), run_time=0.6)
        self.wait(1.2)

        same = Fraction(t["im"], t["instrument"]) == Fraction(t["math"], t["all"])
        verdict = ("The same, so the two are independent in this survey." if same
                   else "Different, so the two are not independent in this survey.")
        end = label(verdict, 30, AMBER if not same else INK, "BOLD").move_to([0, -3.3, 0])
        self.play(FadeOut(q2), FadeIn(end), run_time=0.9)
        self.wait(2.6)
        _ = LEFT, RIGHT, UP
