"""L2-05 Reverse a condition with Bayes' rule: 1,000 dots, a rare condition, many false alarms.

The rates come from the lesson JSON (animation.params) and go through the course's
tested qcai.science.bayes; the dot counts are those rates applied to the stored
population and rounded to whole people. Which grey dots become false positives is
shuffled with qcai.science.rng and the stored seed, so every render is the same.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Dot, FadeIn, FadeOut, LaggedStart, MathTex, Rectangle, Scene, VGroup, Write)

from qcai_style import AMBER, GRID, INK, MUTED, RED, VIOLET, label, params

LESSON = "L2-05"


def counts(p):
    from qcai import science
    r = science.bayes(p["prior"], p["sensitivity"], p["false_positive"])
    n = p["people"]
    cond = round(n * p["prior"])
    tp = round(cond * p["sensitivity"])
    fp = round((n - cond) * p["false_positive"])
    pos = tp + fp
    assert abs(pos - n * r["positive"]) < 1 and abs(tp / pos - r["posterior"]) < 0.01
    return {"n": n, "cond": cond, "tp": tp, "miss": cond - tp, "fp": fp, "pos": pos,
            "fp_exact": (n - cond) * p["false_positive"], "pct": round(100 * r["posterior"])}


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    c = counts(L["animation"]["params"])
    return [f"{c['cond']} have the allergy", f"{c['tp']} of the {c['cond']} test positive",
            f"about {c['fp']} without the allergy also test positive",
            f"{c['tp']} out of {c['pos']}", f"about {c['pct']} percent"]


class FalseAlarms(Scene):
    def construct(self):
        from qcai import science
        p = params(LESSON)
        c = counts(p)
        n, cols = c["n"], p["columns"]
        rows = n // cols
        sp = 0.215

        title = label(f"An imagined screening test for {c['n']:,} students", 36, INK, "BOLD").to_edge(UP, buff=0.3)
        sub = label("made-up numbers", 26, MUTED).next_to(title, DOWN, buff=0.12)
        self.play(Write(title), FadeIn(sub), run_time=1.2)

        gx, gy = -2.15, -0.45  # grid centre
        dots = VGroup(*[Dot([gx + (i % cols - (cols - 1) / 2) * sp, gy + ((rows - 1) / 2 - i // cols) * sp, 0],
                            radius=0.075, color=GRID) for i in range(n)])
        self.play(FadeIn(dots, lag_ratio=0.0005), run_time=1.5)

        PX = 4.75

        def panel(lines, color, y):
            return VGroup(*[label(s, 28, color) for s in lines]).arrange(DOWN, buff=0.1).move_to([PX, y, 0])

        # who has the condition: the first `cond` dots (top-left corner)
        cond_idx = list(range(c["cond"]))
        cond = VGroup(*[dots[i] for i in cond_idx])
        t1 = panel([f"{c['cond']} have the allergy"], RED, 1.9)
        self.play(*[d.animate.set_color(RED).scale(1.35) for d in cond], FadeIn(t1), run_time=1.4)
        self.wait(1.0)

        # true positives
        tp = VGroup(*[dots[i] for i in cond_idx[:c["tp"]]])
        t2 = panel([f"{c['tp']} of the {c['cond']} test positive"], VIOLET, 1.1)
        self.play(*[d.animate.set_color(VIOLET) for d in tp], FadeIn(t2), run_time=1.4)
        self.wait(1.0)

        # false positives: a seeded choice among people without the condition
        rand = science.rng(p["seed"])
        pool = list(range(c["cond"], n))
        for i in range(len(pool) - 1, 0, -1):
            j = int(rand() * (i + 1))
            pool[i], pool[j] = pool[j], pool[i]
        fp_idx = sorted(pool[:c["fp"]])
        fp = VGroup(*[dots[i] for i in fp_idx])
        t3 = panel(["about " + str(c["fp"]) + " without the", "allergy also test positive"], AMBER, 0.05)
        self.play(LaggedStart(*[d.animate.set_color(AMBER).scale(1.35) for d in fp], lag_ratio=0.02), FadeIn(t3), run_time=2.6)
        self.wait(1.4)

        # keep only the positives
        keep = set(cond_idx[:c["tp"]]) | set(fp_idx)
        others = VGroup(*[d for i, d in enumerate(dots) if i not in keep])
        t4 = panel(["Keep only the", "positive tests"], INK, -1.2)
        self.play(others.animate.set_opacity(0.12), FadeIn(t4), run_time=1.4)
        self.wait(0.6)

        bc = 14
        order = list(tp) + list(fp)
        block = [[gx + (k % bc - (bc - 1) / 2) * 0.42, 2.0 - (k // bc) * 0.42, 0] for k in range(len(order))]
        self.play(FadeOut(others), FadeOut(t4), *[d.animate.move_to(block[k]).scale(1.25) for k, d in enumerate(order)], run_time=2.0)
        brace = Rectangle(width=bc * 0.42 + 0.2, height=((len(order) - 1) // bc + 1) * 0.42 + 0.2, color=MUTED, stroke_width=2)
        brace.move_to([gx, 2.0 - ((len(order) - 1) // bc) * 0.21, 0])
        pos_lbl = label(f"{c['pos']} positive tests", 28, INK).next_to(brace, DOWN, buff=0.2)
        self.play(FadeIn(brace), FadeIn(pos_lbl), run_time=0.8)

        frac = MathTex(r"P(\text{allergy}\mid\text{positive})=", r"\frac{%d}{%d}" % (c["tp"], c["pos"]), color=INK, font_size=44)
        frac[1][:len(str(c["tp"]))].set_color(VIOLET)
        frac.move_to([gx, -1.95, 0])
        s = label(f"{c['tp']} out of {c['pos']}, about {c['pct']} percent", 30, VIOLET, "BOLD").next_to(frac, DOWN, buff=0.25)
        self.play(Write(frac), run_time=1.2)
        self.play(FadeIn(s), run_time=0.7)
        self.wait(1.0)
        note = panel(["A positive test is", "far from certain", "when the allergy", "is rare."], INK, -2.0)
        self.play(FadeIn(note), run_time=0.8)
        self.wait(3.0)
        _ = LEFT, RIGHT
