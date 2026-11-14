"""L1-02 Build a probability model: 8 counters become fractions on a line from 0 to 1.

The counts of red and blue counters come from the lesson JSON (animation.params),
so the fractions on screen are the fractions in the text.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, FadeIn, FadeOut, GrowFromEdge, Indicate, Line, MathTex,
                   Rectangle, Scene, TransformFromCopy, VGroup, Write)

from qcai_style import BLUE, INK, MUTED, RED, label, params

LESSON = "L1-02"


def counts(p):
    return p["red"], p["blue"], p["red"] + p["blue"]


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    r, b, n = counts(L["animation"]["params"])
    return [f"{r} out of {n}", f"{b} out of {n}"]


class ProbabilityModel(Scene):
    def construct(self):
        r, b, n = counts(params(LESSON))

        title = label(f"A bag of {n} counters, drawn without looking", 38, INK, "BOLD").to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=1.2)

        dots = VGroup(*[Circle(radius=0.36, color=RED if i < r else BLUE, fill_color=RED if i < r else BLUE,
                               fill_opacity=1, stroke_width=3) for i in range(n)]).arrange(RIGHT, buff=0.35)
        dots.move_to(UP * 2.2)
        for d in dots:
            d.set_opacity(0.25)
        self.play(FadeIn(dots, lag_ratio=0.1), run_time=1.2)
        same = label("Each counter is equally likely.", 30, MUTED).next_to(dots, DOWN, buff=0.35)
        self.play(FadeIn(same), run_time=0.8)
        self.wait(0.6)

        reds, blues = dots[:r], dots[r:]
        self.play(FadeOut(same), *[d.animate.set_opacity(1) for d in reds], run_time=0.8)
        self.play(Indicate(reds, color=RED, scale_factor=1.15), run_time=0.9)
        red_txt = label(f"{r} out of {n} are red", 32, RED).next_to(dots, DOWN, buff=0.35)
        self.play(FadeIn(red_txt), run_time=0.7)

        p_red = MathTex(r"P(\text{red}) = \frac{%d}{%d}" % (r, n), color=RED, font_size=46).move_to(LEFT * 3.8 + UP * 0.12)
        self.play(Write(p_red), run_time=1.0)
        self.wait(0.5)

        # the line from 0 to 1, built by hand so every mark has a set colour
        x0, x1, y = -5.5, 5.5, -2.2
        def X(v):
            return x0 + (x1 - x0) * v
        base = Line([x0, y, 0], [x1, y, 0], color=MUTED, stroke_width=4)
        ticks = VGroup(*[Line([X(k / n), y - 0.12, 0], [X(k / n), y + 0.12, 0], color=MUTED,
                              stroke_width=4 if k in (0, n) else 2) for k in range(n + 1)])
        zero = label("0", 30, INK).next_to([X(0), y, 0], DOWN, buff=0.25)
        one = label("1", 30, INK).next_to([X(1), y, 0], DOWN, buff=0.25)
        imp = label("impossible", 26, MUTED).next_to(zero, DOWN, buff=0.08)
        cer = label("certain", 26, MUTED).next_to(one, DOWN, buff=0.08)
        self.play(Create(base), Create(ticks), run_time=1.2)
        self.play(FadeIn(zero), FadeIn(one), FadeIn(imp), FadeIn(cer), run_time=0.8)

        h = 0.3
        red_bar = Rectangle(width=X(r / n) - x0, height=h, color=RED, fill_color=RED, fill_opacity=0.85, stroke_width=0)
        red_bar.move_to([(x0 + X(r / n)) / 2, y + h / 2 + 0.02, 0])
        red_frac = MathTex(r"\frac{%d}{%d}" % (r, n), color=RED, font_size=44).next_to(red_bar, UP, buff=0.2)
        self.play(TransformFromCopy(p_red[0][-3:], red_frac), GrowFromEdge(red_bar, LEFT), run_time=1.4)
        self.wait(0.8)

        self.play(*[d.animate.set_opacity(1) for d in blues], run_time=0.8)
        self.play(Indicate(blues, color=BLUE, scale_factor=1.15), run_time=0.9)
        blue_txt = label(f"{b} out of {n} are not red", 32, BLUE).next_to(dots, DOWN, buff=0.35)
        self.play(FadeOut(red_txt, shift=UP * 0.2), FadeIn(blue_txt), run_time=0.7)

        blue_bar = Rectangle(width=x1 - X(r / n), height=h, color=BLUE, fill_color=BLUE, fill_opacity=0.85, stroke_width=0)
        blue_bar.move_to([(X(r / n) + x1) / 2, y + h / 2 + 0.02, 0])
        blue_frac = MathTex(r"\frac{%d}{%d}" % (b, n), color=BLUE, font_size=44).next_to(blue_bar, UP, buff=0.2)
        self.play(GrowFromEdge(blue_bar, LEFT), FadeIn(blue_frac), run_time=1.4)

        p_not = MathTex(r"P(\text{not red}) = \frac{%d}{%d} = 1 - \frac{%d}{%d}" % (b, n, r, n),
                        color=BLUE, font_size=46).move_to(RIGHT * 2.6 + UP * 0.12)
        self.play(Write(p_not), run_time=1.6)
        self.wait(0.6)

        whole = label("Red and not red together fill the line: they add up to 1.", 30, INK)
        whole.move_to(DOWN * 3.62)
        self.play(FadeIn(whole), run_time=0.9)
        self.wait(3.0)
        _ = DOWN
