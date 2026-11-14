"""L2-10 Build an evidence record: scattered facts assemble into a card; weak links glow; scope shrinks.

The made-up two-way table (juice drinkers vs others, mostly A and B grades) is stored in the
lesson JSON (animation.params). Every percent and gap on screen is computed from it here.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, FadeIn, Indicate, Line, Rectangle, RoundedRectangle, Scene, SurroundingRectangle,
                   Transform, VGroup, Write)

from qcai_style import AMBER, BLUE, CYAN, INK, MUTED, VIOLET, label, params

LESSON = "L2-10"


def numbers(p):
    d, dg, o, og = p["drinkers"], p["drinkers_good"], p["others"], p["others_good"]
    pd, po = round(100 * dg / d), round(100 * og / o)
    assert 100 * dg % d == 0 and 100 * og % o == 0, "keep the percents whole"
    return d, dg, o, og, pd, po, pd - po, d + o


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    d, dg, o, og, pd, po, gap, n = numbers(L["animation"]["params"])
    return [f"{dg} out of {d}", f"{og} out of {o}", f"{pd} percent", f"{po} percent", f"{gap} points", f"{n} students"]


def clamp(m):
    if m.get_right()[0] > 6.8:
        m.shift(LEFT * (m.get_right()[0] - 6.8))
    if m.get_left()[0] < -6.8:
        m.shift(RIGHT * (-6.8 - m.get_left()[0]))
    return m


class EvidenceRecord(Scene):
    def construct(self):
        p = params(LESSON)
        d, dg, o, og, pd, po, gap, n = numbers(p)

        title = label("Build an evidence record", 40, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.9)

        values = [
            ("Claim", ["Juice drinkers get better grades."], INK),
            ("Source", ["A made-up survey in one imagined school"], INK),
            ("Calculation", [f"{dg} out of {d} vs {og} out of {o}", f"{pd} percent vs {po} percent: {gap} points"], INK),
            ("Assumption", ["No common cause, such as sleep"], INK),
            ("Uncertainty", [f"Only {n} students"], INK),
        ]
        starts = [(-3.6, 2.2, 0.08), (3.4, 2.4, -0.06), (-3.2, 0.9, -0.05), (3.6, -0.1, 0.07), (-4.3, -1.0, 0.06),
                  (3.6, -1.3, -0.08), (-2.6, -2.4, 0.05)]

        # scattered facts
        chips, targets, si = [], [], 0
        rows_y = [2.35, 1.6, 0.75, -0.25, -1.0]
        name_x, val_x = -5.6, -2.7
        names = VGroup()
        for (name, lines, col), y in zip(values, rows_y):
            nm = label(name, 26, VIOLET, "BOLD")
            nm.move_to([name_x, y, 0], aligned_edge=LEFT)
            names.add(nm)
            for k, s in enumerate(lines):
                tgt = label(s, 26, col)
                tgt.move_to([val_x, y - 0.42 * k + (0.2 if len(lines) > 1 else 0), 0], aligned_edge=LEFT)
                x, yy, rot = starts[si]; si += 1
                chip = label(s, 26, col).move_to([x, yy, 0]).rotate(rot)
                clamp(chip)
                chips.append(chip); targets.append(tgt)
        scope_wide = label("All students, everywhere?", 26, INK)
        x, yy, rot = starts[si]
        scope_chip = clamp(label("All students, everywhere?", 26, INK).move_to([x, yy, 0]).rotate(rot))
        self.play(*[FadeIn(c, shift=UP * 0.2) for c in chips + [scope_chip]], lag_ratio=0.15, run_time=2.0)
        self.wait(0.8)

        # the card forms and facts fly into place
        card = RoundedRectangle(width=12.6, height=5.8, corner_radius=0.2, stroke_color=BLUE, stroke_width=3).move_to([0, -0.12, 0])
        rules = VGroup(*[Line([-6.0, y, 0], [6.0, y, 0], color="#e2e8f0", stroke_width=2) for y in (1.97, 1.15, -0.0, -0.62, -1.38)])
        scope_name = label("Scope", 26, VIOLET, "BOLD").move_to([name_x, -2.25, 0], aligned_edge=LEFT)
        scope_wide.move_to([val_x, -2.25, 0], aligned_edge=LEFT)
        self.play(FadeIn(card), FadeIn(rules), FadeIn(names), FadeIn(scope_name), run_time=0.8)
        for c, t in zip(chips, targets):
            self.play(Transform(c, t), run_time=0.55)
        self.play(Transform(scope_chip, scope_wide), run_time=0.55)
        self.wait(0.6)

        # weak links glow amber
        assume_row, unc_row = chips[4], chips[5]
        tag1 = label("assumed, not tested", 24, AMBER, "BOLD").next_to(targets[4], RIGHT, buff=0.4)
        tag2 = label("small sample", 24, AMBER, "BOLD").next_to(targets[5], RIGHT, buff=0.4)
        box1 = SurroundingRectangle(assume_row, color=AMBER, buff=0.1, stroke_width=4)
        box2 = SurroundingRectangle(unc_row, color=AMBER, buff=0.1, stroke_width=4)
        self.play(FadeIn(box1), FadeIn(tag1), assume_row.animate.set_color(AMBER), run_time=0.8)
        self.play(Indicate(box1, color=AMBER), run_time=0.7)
        self.play(FadeIn(box2), FadeIn(tag2), unc_row.animate.set_color(AMBER), run_time=0.8)
        self.play(Indicate(box2, color=AMBER), run_time=0.7)
        self.wait(0.5)

        # the scope box shrinks to what the data covered
        # start wide (the poster's claim reaches everyone), then shrink to what the data covered
        left, right = val_x - 0.15, 5.85
        sbox = Rectangle(width=right - left, height=0.66, color=CYAN, stroke_width=4).move_to([(left + right) / 2, -2.25, 0])
        self.play(FadeIn(sbox), run_time=0.5)
        narrow = label(f"{n} students, one imagined school, one term", 26, CYAN, "BOLD")
        narrow.move_to([val_x, -2.25, 0], aligned_edge=LEFT)
        nbox = SurroundingRectangle(narrow, color=CYAN, buff=0.15, stroke_width=4)
        self.play(Transform(scope_chip, narrow), Transform(sbox, nbox), run_time=1.2)
        self.wait(0.6)

        end = label("Tested: a gap in made-up data.  Assumed: no common cause.", 28, INK, "BOLD").to_edge(DOWN, buff=0.25)
        self.play(FadeIn(end), run_time=0.8)
        self.wait(3.0)
        _ = MUTED
